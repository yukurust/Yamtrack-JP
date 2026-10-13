"""User-facing labels translated for the Japanese fork.

Model choice values stay in English so existing databases and upstream code
keep working. These maps only change what is displayed.
"""

from django.utils.translation import gettext_lazy as _

from app.models import MediaTypes

STATUS_LABELS = {
    "Completed": _("Completed"),
    "In Progress": _("In Progress"),
    "In progress": _("In Progress"),
    "Planning": _("Planning"),
    "Paused": _("Paused"),
    "Dropped": _("Dropped"),
    "All": _("All"),
}

MEDIA_TYPE_LABELS = {
    MediaTypes.TV.value: _("TV Show"),
    MediaTypes.SEASON.value: _("TV Season"),
    MediaTypes.EPISODE.value: _("Episode"),
    MediaTypes.MOVIE.value: _("Movie"),
    MediaTypes.ANIME.value: _("Anime"),
    MediaTypes.MANGA.value: _("Manga"),
    MediaTypes.GAME.value: _("Game"),
    MediaTypes.BOOK.value: _("Book"),
    MediaTypes.COMIC.value: _("Comic"),
    MediaTypes.BOARDGAME.value: _("Boardgame"),
}

MEDIA_TYPE_PLURALS = {
    MediaTypes.TV.value: _("TV Shows"),
    MediaTypes.SEASON.value: _("TV Seasons"),
    MediaTypes.EPISODE.value: _("Episodes"),
    MediaTypes.MOVIE.value: _("Movies"),
    MediaTypes.ANIME.value: _("Anime"),
    MediaTypes.MANGA.value: _("Manga"),
    MediaTypes.GAME.value: _("Games"),
    MediaTypes.BOOK.value: _("Books"),
    MediaTypes.COMIC.value: _("Comics"),
    MediaTypes.BOARDGAME.value: _("Boardgames"),
}

UNITS = {
    "Episode": _("Episode"),
    "Chapter": _("Chapter"),
    "Page": _("Page"),
    "Issue": _("Issue"),
    "Play": _("Play"),
    "episode": _("episode"),
    "episodes": _("episodes"),
    "chapter": _("chapter"),
    "chapters": _("chapters"),
    "page": _("page"),
    "pages": _("pages"),
    "issue": _("issue"),
    "issues": _("issues"),
    "play": _("play"),
    "plays": _("plays"),
    "hour": _("hour"),
    "hours": _("hours"),
    "E": _("E"),
}

DETAIL_LABELS = {
    "format": _("format"),
    "start date": _("start date"),
    "end date": _("end date"),
    "status": _("status"),
    "episodes": _("episodes"),
    "runtime": _("runtime"),
    "studios": _("studios"),
    "season": _("season"),
    "broadcast": _("broadcast"),
    "source": _("source"),
    "number of chapters": _("number of chapters"),
    "release date": _("release date"),
    "country": _("country"),
    "languages": _("languages"),
    "first air date": _("first air date"),
    "last air date": _("last air date"),
    "seasons": _("seasons"),
    "themes": _("themes"),
    "platforms": _("platforms"),
    "companies": _("companies"),
    "physical format": _("physical format"),
    "number of pages": _("number of pages"),
    "publish date": _("publish date"),
    "author": _("author"),
    "publishers": _("publishers"),
    "isbn": _("isbn"),
    "authors": _("authors"),
    "year": _("year"),
    "status in country of origin": _("status in country of origin"),
    "latest chapter translated": _("latest chapter translated"),
    "publisher": _("publisher"),
    "issues count": _("issues count"),
    "last issue name": _("last issue name"),
    "last issue number": _("last issue number"),
    "people": _("people"),
    "last updated": _("last updated"),
    "players": _("players"),
    "playtime": _("playtime"),
    "min age": _("min age"),
    "designers": _("designers"),
}

DETAIL_VALUES = {
    "Finished": _("Finished"),
    "Airing": _("Airing"),
    "Upcoming": _("Upcoming"),
    "Publishing": _("Publishing"),
    "On Hiatus": _("On Hiatus"),
    "Discontinued": _("Discontinued"),
    "Released": _("Released"),
    "Ended": _("Ended"),
    "Returning Series": _("Returning Series"),
    "In Production": _("In Production"),
    "Post Production": _("Post Production"),
    "Planned": _("Planned"),
    "Rumored": _("Rumored"),
    "Canceled": _("Canceled"),
    "Pilot": _("Pilot"),
    "Movie": _("Movie"),
    "TV": _("TV"),
    "Unknown": _("Unknown"),
    "Unknown air date": _("Unknown air date"),
    "No synopsis available.": _("No synopsis available."),
}

RELATED_LABELS = {
    "Related Anime": _("Related Anime"),
    "Related Manga": _("Related Manga"),
    "Recommendations": _("Recommendations"),
    "Seasons": _("Seasons"),
    "Collection": _("Collection"),
    "DLCs": _("DLCs"),
    "Parent Game": _("Parent Game"),
    "Remasters": _("Remasters"),
    "Remakes": _("Remakes"),
    "Expansions": _("Expansions"),
    "Standalone Expansions": _("Standalone Expansions"),
    "Expanded Games": _("Expanded Games"),
    "Other Editions": _("Other Editions"),
}

CHOICE_LABELS = {
    "Upcoming": _("Upcoming"),
    "Recent": _("Recent"),
    "Completion": _("Completion"),
    "Episodes Left": _("Episodes Left"),
    "Title": _("Title"),
    "Rating": _("Rating"),
    "Progress": _("Progress"),
    "Start Date": _("Start Date"),
    "End Date": _("End Date"),
    "Last Item Added": _("Last Item Added"),
    "Name": _("Name"),
    "Items Count": _("Items Count"),
    "Newest First": _("Newest First"),
    "Date Added": _("Date Added"),
    "Media Type": _("Media Type"),
    "Current Date": _("Current Date"),
    "Release Date": _("Release Date"),
    "No Date": _("No Date"),
    "Monday": _("Monday"),
    "Sunday": _("Sunday"),
    "Grid": _("Grid"),
    "Table": _("Table"),
    "List": _("List"),
    "Score": _("Score"),
    "Status": _("Status"),
    "Notes": _("Notes"),
    "Start date": _("Start date"),
    "End date": _("End date"),
    "Select": _("Select"),
    "Parent TV Show": _("Parent TV Show"),
    "Parent Season": _("Parent Season"),
    "Progress (Time Played)": _("Progress (Time Played)"),
    "Progress (Chapters)": _("Progress (Chapters)"),
    "Progress (Pages)": _("Progress (Pages)"),
    "Progress (Issues)": _("Progress (Issues)"),
    "Progress (Plays)": _("Progress (Plays)"),
    "2026-01-18 (ISO)": _("2026-01-18 (ISO)"),
    "18/01/2026 (EU)": _("18/01/2026 (EU)"),
    "01/18/2026 (US)": _("01/18/2026 (US)"),
    "Jan 18, 2026": _("Jan 18, 2026"),
    "18 Jan, 2026": _("18 Jan, 2026"),
    "2026年1月18日": _("2026年1月18日"),
    "14:30 (24-hour)": _("14:30 (24-hour)"),
    "2:30 PM (12-hour)": _("2:30 PM (12-hour)"),
}

CONSUMPTION = {
    "Movies watched": _("Movies watched"),
    "Movie watched": _("Movie watched"),
    "Anime episodes watched": _("Anime episodes watched"),
    "Anime episode watched": _("Anime episode watched"),
    "TV episodes watched": _("TV episodes watched"),
    "TV episode watched": _("TV episode watched"),
    "Manga chapters read": _("Manga chapters read"),
    "Manga chapter read": _("Manga chapter read"),
    "Book pages read": _("Book pages read"),
    "Book page read": _("Book page read"),
    "Comic issues read": _("Comic issues read"),
    "Comic issue read": _("Comic issue read"),
    "Boardgame plays": _("Boardgame plays"),
    "Boardgame play": _("Boardgame play"),
    "Game hours played": _("Game hours played"),
    "Game hour played": _("Game hour played"),
}


def status_label(value):
    """Return the translated tracker status label."""
    return STATUS_LABELS.get(value, value)


def choice_label(value):
    """Return a translated label for a known settings choice."""
    return CHOICE_LABELS.get(value, value)


def detail_value(value):
    """Translate a known metadata value, leaving everything else unchanged."""
    if not isinstance(value, str):
        return value
    return DETAIL_VALUES.get(value, value)


def unit_label(value):
    """Translate a progress unit noun."""
    return UNITS.get(value, value)


def consumption_label(phrase):
    """Translate a statistics consumption descriptor."""
    return CONSUMPTION.get(phrase, phrase)
