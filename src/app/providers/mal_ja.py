"""Japanese titles and synopses for MAL anime.

Title: optional ``ja_titles.json`` override, otherwise MAL ``alternative_titles.ja``.
Synopsis: TMDB ja-JP overview for the season/cour that matches the MAL start
date, then the show overview (movie overview for MAL movies). Cached on the
db volume. Any failure leaves the original English metadata in place.
"""

import json
import logging
import re
import threading
from datetime import date
from pathlib import Path

import requests
from django.conf import settings
from django.utils.translation import get_language

from app.models import Sources
from app.providers import services

logger = logging.getLogger(__name__)

_LOCK = threading.Lock()
_SEASON_WINDOW_DAYS = 60
_COUR_WINDOW_DAYS = 400
_ANIME_GENRE_ID = "16"
_TITLE_SPLIT = re.compile(
    # Fullwidth punctuation appears in Japanese titles and must stay as-is.
    r"[ 　]*(?:第?\d+(?:期|クール|nd|rd|th|st)|[ⅡⅢⅣ]|II+|"
    r"Season|season|2nd|3rd|4th|\(|（|～|〜)",  # noqa: RUF001
)

# MAL genre names are English even when the UI language is Japanese.
GENRE_LABELS = {
    "Action": "アクション",
    "Adventure": "アドベンチャー",
    "Comedy": "コメディ",
    "Drama": "ドラマ",
    "Fantasy": "ファンタジー",
    "Horror": "ホラー",
    "Mystery": "ミステリー",
    "Romance": "恋愛",
    "Sci-Fi": "SF",
    "Slice of Life": "日常",
    "Sports": "スポーツ",
    "Supernatural": "超常現象",
    "Suspense": "サスペンス",
    "Ecchi": "エッチ",
    "Mecha": "ロボット",
    "Music": "音楽",
    "Psychological": "心理",
    "School": "学園",
    "Military": "ミリタリー",
    "Historical": "歴史",
    "Isekai": "異世界",
    "Super Power": "超能力",
    "Martial Arts": "格闘技",
    "Space": "宇宙",
    "Vampire": "吸血鬼",
    "Harem": "ハーレム",
    "Parody": "パロディ",
    "Gore": "ゴア",
    "Detective": "探偵",
    "Time Travel": "タイムトラベル",
    "Love Polygon": "三角関係",
    "Gag Humor": "ギャグ",
    "Strategy Game": "戦略ゲーム",
    "Video Game": "ゲーム",
    "Mythology": "神話",
    "Reincarnation": "転生",
    "Survival": "サバイバル",
    "Team Sports": "チームスポーツ",
    "Workplace": "職場",
    "Award Winning": "受賞作",
    "Adult Cast": "大人キャスト",
    "Anthropomorphic": "擬人化",
    "CGDCT": "美少女日常",
    "Childcare": "子育て",
    "Combat Sports": "格闘スポーツ",
    "Delinquents": "不良",
    "Gourmet": "グルメ",
    "High Stakes Game": "デスゲーム",
    "Idols (Female)": "アイドル(女性)",
    "Idols (Male)": "アイドル(男性)",
    "Iyashikei": "癒し系",
    "Mahou Shoujo": "魔法少女",
    "Medical": "医療",
    "Organized Crime": "犯罪組織",
    "Otaku Culture": "オタク文化",
    "Performing Arts": "芸能",
    "Pets": "ペット",
    "Racing": "レース",
    "Reverse Harem": "逆ハーレム",
    "Romantic Subtext": "恋愛要素",
    "Samurai": "侍",
    "Showbiz": "芸能界",
    "Visual Arts": "美術",
    "Urban Fantasy": "現代ファンタジー",
    "Villainess": "悪役令嬢",
    "Shounen": "少年",
    "Shoujo": "少女",
    "Seinen": "青年",
    "Josei": "女性",
    "Kids": "キッズ",
    "Boys Love": "BL",
    "Girls Love": "GL",
    "Avant Garde": "アバンギャルド",
    "Erotica": "エロティカ",
    "Educational": "教育",
    "Magical Sex Shift": "性転換",
    "Crossdressing": "女装",
}

# Keys are the labels ``mal.get_readable_status`` / ``mal.get_format`` return.
STATUS_LABELS = {
    "Finished": "放送終了",
    "Finished Airing": "放送終了",
    "Airing": "放送中",
    "Currently Airing": "放送中",
    "Not Yet Aired": "未放送",
    "Upcoming": "未放送",
    "Publishing": "連載中",
    "On Hiatus": "休載",
    "Discontinued": "打ち切り",
}

FORMAT_LABELS = {
    "Anime": "TV",
    "Tv": "TV",
    "Movie": "劇場版",
    "OVA": "OVA",
    "Ova": "OVA",
    "ONA": "ONA",
    "Ona": "ONA",
    "Special": "特別編",
    "Tv Special": "TVスペシャル",
    "Music": "音楽",
}


def japanese_requested():
    """Return whether the active language should use Japanese metadata."""
    language = get_language() or settings.LANGUAGE_CODE or ""
    return language.lower().startswith("ja")


def localize_anime(media_id, data, mal_payload=None):
    """Return a Japanese copy of MAL anime metadata when the UI language is ja."""
    if not japanese_requested():
        return data

    try:
        localized = _copy_metadata(data)
        meta = _meta(media_id, mal_payload=mal_payload)
        title = _title_override(media_id) or meta.get("title_ja")
        if title:
            localized["title"] = title
        if meta.get("synopsis"):
            localized["synopsis"] = meta["synopsis"]
        _translate_labels(localized)
    except Exception:  # noqa: BLE001 - English metadata must survive any lookup failure
        logger.warning("Japanese localization failed for MAL anime %s", media_id)
        return data
    else:
        return localized


def lookup_anime(media_id, mal_payload=None):
    """Fetch Japanese title and synopsis for one MAL anime id."""
    payload = mal_payload or {}
    if "alternative_titles" not in payload:
        payload = _fetch_mal(media_id)
    result = {"title_ja": None, "synopsis": None, "synopsis_source": None}
    titles = payload.get("alternative_titles") or {}
    title_ja = (titles.get("ja") or "").strip()
    result["title_ja"] = title_ja or None

    if payload.get("media_type") == "movie":
        _fill_movie_synopsis(result, title_ja, payload.get("title"))
        return result

    _fill_tv_synopsis(result, title_ja, payload.get("title"), payload.get("start_date"))
    return result


def _copy_metadata(data):
    localized = dict(data)
    localized["details"] = dict(data.get("details") or {})
    genres = data.get("genres")
    if isinstance(genres, list):
        localized["genres"] = list(genres)
    return localized


def _translate_labels(data):
    genres = data.get("genres")
    if isinstance(genres, list):
        data["genres"] = [GENRE_LABELS.get(genre, genre) for genre in genres]

    details = data["details"]
    status = details.get("status")
    if status in STATUS_LABELS:
        details["status"] = STATUS_LABELS[status]
    media_format = details.get("format")
    if media_format in FORMAT_LABELS:
        details["format"] = FORMAT_LABELS[media_format]


def _cache_dir():
    configured = getattr(settings, "JA_META_DIR", None)
    if configured:
        return Path(configured)
    return Path(settings.BASE_DIR) / "db"


def _read_json(path):
    try:
        with path.open(encoding="utf-8") as handle:
            loaded = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return {}
    if isinstance(loaded, dict):
        return loaded
    return {}


def _write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=1)
    temporary.replace(path)


def _title_override(media_id):
    titles = _read_json(_cache_dir() / "ja_titles.json")
    override = titles.get(_meta_key(media_id))
    if isinstance(override, str) and override.strip():
        return override.strip()
    return None


def _meta_key(media_id):
    return f"mal|anime|{media_id}"


def _cache_is_complete(cached):
    """Return whether a stored entry should be reused without another lookup."""
    if not isinstance(cached, dict):
        return False
    if cached.get("synopsis_source") == "manual":
        return True
    if cached.get("title_ja"):
        return True
    return bool(cached.get("title_checked"))


def _meta(media_id, mal_payload=None):
    path = _cache_dir() / "ja_meta.json"
    key = _meta_key(media_id)
    stored = _read_json(path)
    cached = stored.get(key)
    if _cache_is_complete(cached):
        return cached

    try:
        entry = lookup_anime(media_id, mal_payload=mal_payload)
    except (requests.RequestException, services.ProviderAPIError, KeyError, TypeError):
        logger.warning("Japanese metadata lookup failed for MAL anime %s", media_id)
        return stored.get(key) or {}

    with _LOCK:
        stored = _read_json(path)
        previous = stored.get(key) or {}
        if previous.get("synopsis_source") == "manual":
            entry["synopsis"] = previous.get("synopsis")
            entry["synopsis_source"] = "manual"
        elif not entry.get("synopsis") and previous.get("synopsis"):
            entry["synopsis"] = previous.get("synopsis")
            entry["synopsis_source"] = previous.get("synopsis_source")
        entry["title_checked"] = True
        stored[key] = entry
        try:
            _write_json(path, stored)
        except OSError:
            logger.warning("Could not persist Japanese metadata cache at %s", path)
    return entry


def _fetch_mal(media_id):
    return services.api_request(
        Sources.MAL.value,
        "GET",
        f"https://api.myanimelist.net/v2/anime/{media_id}",
        params={
            "fields": "alternative_titles,start_date,media_type,title",
        },
        headers={"X-MAL-CLIENT-ID": settings.MAL_API},
    )


def _tmdb(path, **params):
    params["api_key"] = settings.TMDB_API
    params["language"] = "ja-JP"
    return services.api_request(
        Sources.TMDB.value,
        "GET",
        f"https://api.themoviedb.org/3{path}",
        params=params,
    )


def _parse_date(value):
    if not value:
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def _search_queries(title_ja, english_title):
    shortened = ""
    if title_ja:
        shortened = _TITLE_SPLIT.split(title_ja, maxsplit=1)[0].strip()
    first_token = title_ja.split()[0] if title_ja else ""
    queries = [title_ja, shortened, first_token, english_title]
    unique = []
    for query in queries:
        if query and query not in unique:
            unique.append(query)
    return unique


def _fill_movie_synopsis(result, title_ja, english_title):
    for query in _search_queries(title_ja, english_title):
        matches = _tmdb("/search/movie", query=query).get("results") or []
        matches = [match for match in matches if match.get("overview")]
        if not matches:
            continue
        chosen = matches[0]
        result["synopsis"] = chosen["overview"]
        result["synopsis_source"] = f"TMDB movie {chosen['id']}"
        return


def _fill_tv_synopsis(result, title_ja, english_title, start_date):
    start = _parse_date(start_date)
    queries = _search_queries(title_ja, english_title)
    for index, query in enumerate(queries):
        show = _match_tv_show(
            query,
            title_ja or query,
            allow_loose=index == len(queries) - 1,
        )
        if show is None:
            continue
        overview, source = _season_overview(show, start)
        if overview:
            result["synopsis"] = overview
            result["synopsis_source"] = source
            return


def _match_tv_show(query, title_ja, *, allow_loose):
    matches = _tmdb("/search/tv", query=query).get("results") or []
    matches = [
        match for match in matches if _ANIME_GENRE_ID in str(match.get("genre_ids"))
    ]
    if not matches:
        return None

    contained = [
        match
        for match in matches
        if _compact(match.get("name"))
        and _compact(match.get("name")) in _compact(title_ja)
    ]
    contained.sort(key=lambda match: len(_compact(match.get("name"))), reverse=True)
    if not contained and not allow_loose:
        return None
    chosen = (contained or matches)[0]
    return _tmdb(f"/tv/{chosen['id']}")


def _compact(value):
    # Fullwidth punctuation is stripped so Japanese titles still match.
    return re.sub(r"[\s　・:：（）()]", "", value or "")  # noqa: RUF001


def _season_overview(show, start):
    seasons = [
        season
        for season in show.get("seasons") or []
        if season.get("season_number", 0) > 0
    ]
    best = _closest_season(seasons, start) or _previous_cour(seasons, start)
    if best and (best.get("overview") or "").strip():
        source = f"TMDB tv {show['id']} season {best['season_number']}"
        return best["overview"].strip(), source

    overview = (show.get("overview") or "").strip()
    if overview:
        return overview, f"TMDB tv {show['id']} (show overview)"
    return None, None


def _closest_season(seasons, start):
    if start is None:
        return None
    best = None
    best_gap = None
    for season in seasons:
        aired = _parse_date(season.get("air_date"))
        if aired is None:
            continue
        gap = abs((aired - start).days)
        if gap <= _SEASON_WINDOW_DAYS and (best_gap is None or gap < best_gap):
            best = season
            best_gap = gap
    return best


def _previous_cour(seasons, start):
    """Use the latest season that started before a later cour of the same show."""
    if start is None:
        return None
    candidates = []
    for season in seasons:
        aired = _parse_date(season.get("air_date"))
        if aired is None or aired > start:
            continue
        if (start - aired).days <= _COUR_WINDOW_DAYS:
            candidates.append((aired, season))
    if not candidates:
        return None
    return max(candidates, key=lambda item: item[0])[1]
