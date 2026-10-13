import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import requests
from django.test import TestCase, override_settings
from django.utils import translation

from app.providers.mal_ja import localize_anime

ENGLISH = {
    "title": "Cowboy Bebop",
    "synopsis": "English synopsis",
    "genres": ["Action", "Sci-Fi"],
    "details": {"status": "Finished", "format": "Anime"},
}

PAYLOAD = {
    "title": "Cowboy Bebop",
    "alternative_titles": {"ja": "カウボーイビバップ"},
    "media_type": "tv",
    "start_date": "1998-04-03",
}


def _show(seasons, overview="作品概要"):
    return {
        "id": 30991,
        "name": "カウボーイビバップ",
        "overview": overview,
        "seasons": seasons,
    }


class MalJapaneseMetadataTests(TestCase):
    """Japanese titles and synopses for MAL anime."""

    def test_english_metadata_is_left_unchanged(self):
        """English UI keeps the MAL payload as stored."""
        with translation.override("en"):
            result = localize_anime("1", ENGLISH, mal_payload=PAYLOAD)

        self.assertIs(result, ENGLISH)
        self.assertEqual(result["genres"], ["Action", "Sci-Fi"])

    def test_japanese_title_season_synopsis_and_labels(self):
        """A matching cour overview replaces the English synopsis."""
        seasons = [
            {
                "season_number": 1,
                "air_date": "1998-04-03",
                "overview": "第1クールのあらすじ",
            },
        ]

        def fake_tmdb(path, **_params):
            if path == "/search/tv":
                return {
                    "results": [
                        {
                            "id": 30991,
                            "name": "カウボーイビバップ",
                            "genre_ids": [16],
                        },
                    ],
                }
            if path == "/tv/30991":
                return _show(seasons)
            message = f"unexpected path {path}"
            raise AssertionError(message)

        with (
            tempfile.TemporaryDirectory() as tmp,
            translation.override("ja"),
            override_settings(JA_META_DIR=tmp),
            patch("app.providers.mal_ja._tmdb", side_effect=fake_tmdb),
        ):
            result = localize_anime("1", ENGLISH, mal_payload=PAYLOAD)

        self.assertEqual(result["title"], "カウボーイビバップ")
        self.assertEqual(result["synopsis"], "第1クールのあらすじ")
        self.assertEqual(result["genres"], ["アクション", "SF"])
        self.assertEqual(result["details"]["status"], "放送終了")
        self.assertEqual(result["details"]["format"], "TV")
        self.assertEqual(ENGLISH["title"], "Cowboy Bebop")
        self.assertEqual(ENGLISH["genres"], ["Action", "Sci-Fi"])

    def test_related_cards_use_japanese_titles(self):
        """Related and recommendation cards prefer alternative_titles.ja."""
        data = {
            **ENGLISH,
            "related": {
                "related_anime": [{"title": "Trigun", "title_ja": "トライガン"}],
                "recommendations": [
                    {"title": "Samurai Champloo", "title_ja": ""},
                ],
            },
        }

        with (
            tempfile.TemporaryDirectory() as tmp,
            translation.override("ja"),
            override_settings(JA_META_DIR=tmp),
            patch("app.providers.mal_ja._tmdb", return_value={"results": []}),
        ):
            result = localize_anime("9", data, mal_payload=PAYLOAD)

        self.assertEqual(result["related"]["related_anime"][0]["title"], "トライガン")
        self.assertEqual(
            result["related"]["recommendations"][0]["title"],
            "Samurai Champloo",
        )
        self.assertEqual(data["related"]["related_anime"][0]["title"], "Trigun")

    def test_payload_without_japanese_title_is_refetched(self):
        """The anime details response omits alternative_titles, so look them up."""
        incomplete = {
            "title": "Cowboy Bebop",
            "media_type": "tv",
            "start_date": "1998-04-03",
        }

        def fake_tmdb(path, **_params):
            if path == "/search/tv":
                return {"results": []}
            return {}

        with (
            tempfile.TemporaryDirectory() as tmp,
            translation.override("ja"),
            override_settings(JA_META_DIR=tmp),
            patch("app.providers.mal_ja._fetch_mal", return_value=PAYLOAD) as fetch,
            patch("app.providers.mal_ja._tmdb", side_effect=fake_tmdb),
        ):
            result = localize_anime("1", dict(ENGLISH), mal_payload=incomplete)

        fetch.assert_called_once_with("1")
        self.assertEqual(result["title"], "カウボーイビバップ")

    def test_title_override_file(self):
        """ja_titles.json wins over the MAL Japanese title."""
        with (
            tempfile.TemporaryDirectory() as tmp,
            translation.override("ja"),
            override_settings(JA_META_DIR=tmp),
            patch("app.providers.mal_ja._tmdb", return_value={"results": []}),
        ):
            Path(tmp, "ja_titles.json").write_text(
                json.dumps({"mal|anime|1": " カウボーイ・ビバップ "}),
                encoding="utf-8",
            )
            result = localize_anime("1", dict(ENGLISH), mal_payload=PAYLOAD)

        self.assertEqual(result["title"], "カウボーイ・ビバップ")
        self.assertEqual(result["synopsis"], "English synopsis")

    def test_later_cour_uses_previous_season(self):
        """A cour without its own season uses the previous cour within 400 days."""
        seasons = [
            {
                "season_number": 1,
                "air_date": "1998-04-03",
                "overview": "第1クール",
            },
            {
                "season_number": 2,
                "air_date": "1999-01-01",
                "overview": "第2クール",
            },
        ]
        payload = {**PAYLOAD, "start_date": "1998-10-24"}

        def fake_tmdb(path, **_params):
            if path == "/search/tv":
                return {
                    "results": [
                        {"id": 9, "name": "カウボーイビバップ", "genre_ids": [16]},
                    ],
                }
            return _show(seasons)

        with (
            tempfile.TemporaryDirectory() as tmp,
            translation.override("ja"),
            override_settings(JA_META_DIR=tmp),
            patch("app.providers.mal_ja._tmdb", side_effect=fake_tmdb),
        ):
            result = localize_anime("1", dict(ENGLISH), mal_payload=payload)

        self.assertEqual(result["synopsis"], "第1クール")

    def test_movie_uses_movie_overview(self):
        """MAL movies take the Japanese overview from TMDB movies."""
        payload = {
            "title": "Spirited Away",
            "alternative_titles": {"ja": "千と千尋の神隠し"},
            "media_type": "movie",
            "start_date": "2001-07-20",
        }

        def fake_tmdb(path, **_params):
            self.assertEqual(path, "/search/movie")
            return {
                "results": [
                    {"id": 129, "overview": "映画のあらすじ"},
                ],
            }

        with (
            tempfile.TemporaryDirectory() as tmp,
            translation.override("ja"),
            override_settings(JA_META_DIR=tmp),
            patch("app.providers.mal_ja._tmdb", side_effect=fake_tmdb),
        ):
            result = localize_anime("1", dict(ENGLISH), mal_payload=payload)

        self.assertEqual(result["title"], "千と千尋の神隠し")
        self.assertEqual(result["synopsis"], "映画のあらすじ")

    def test_lookup_failure_keeps_english_text(self):
        """A TMDB error leaves the English title and synopsis in place."""
        with (
            tempfile.TemporaryDirectory() as tmp,
            translation.override("ja"),
            override_settings(JA_META_DIR=tmp),
            patch(
                "app.providers.mal_ja._tmdb",
                side_effect=requests.RequestException("down"),
            ),
        ):
            result = localize_anime("1", dict(ENGLISH), mal_payload=PAYLOAD)

        self.assertEqual(result["title"], "Cowboy Bebop")
        self.assertEqual(result["synopsis"], "English synopsis")
        self.assertEqual(result["genres"], ["アクション", "SF"])

    def test_unexpected_failure_returns_original_metadata(self):
        """Any unexpected error returns the original metadata unchanged."""
        with (
            translation.override("ja"),
            patch(
                "app.providers.mal_ja._copy_metadata",
                side_effect=RuntimeError("broken"),
            ),
        ):
            result = localize_anime("1", ENGLISH, mal_payload=PAYLOAD)

        self.assertIs(result, ENGLISH)

    def test_cache_without_japanese_title_is_refetched(self):
        """An older cache entry with a null title does not block a later lookup."""
        with (
            tempfile.TemporaryDirectory() as tmp,
            translation.override("ja"),
            override_settings(JA_META_DIR=tmp),
            patch("app.providers.mal_ja._tmdb", return_value={"results": []}),
        ):
            Path(tmp, "ja_meta.json").write_text(
                json.dumps(
                    {
                        "mal|anime|1": {
                            "title_ja": None,
                            "synopsis": "古いあらすじ",
                            "synopsis_source": "TMDB tv 1 season 1",
                        },
                    },
                ),
                encoding="utf-8",
            )
            result = localize_anime("1", dict(ENGLISH), mal_payload=PAYLOAD)

        self.assertEqual(result["title"], "カウボーイビバップ")
        self.assertEqual(result["synopsis"], "古いあらすじ")

    def test_manual_synopsis_is_preserved(self):
        """A manual synopsis_source entry is not replaced by TMDB."""
        with (
            tempfile.TemporaryDirectory() as tmp,
            translation.override("ja"),
            override_settings(JA_META_DIR=tmp),
            patch("app.providers.mal_ja._tmdb") as tmdb,
        ):
            Path(tmp, "ja_meta.json").write_text(
                json.dumps(
                    {
                        "mal|anime|1": {
                            "title_ja": "手入力タイトル",
                            "synopsis": "手入力のあらすじ",
                            "synopsis_source": "manual",
                        },
                    },
                ),
                encoding="utf-8",
            )
            result = localize_anime("1", dict(ENGLISH), mal_payload=PAYLOAD)

        tmdb.assert_not_called()
        self.assertEqual(result["title"], "手入力タイトル")
        self.assertEqual(result["synopsis"], "手入力のあらすじ")
