from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from app.models import Item, MediaTypes, Movie, Sources, Status


class JapaneseLocaleRenderingTests(TestCase):
    """Signed-in Japanese users see translated pages."""

    def setUp(self):
        """Create a Japanese user and log in."""
        self.credentials = {"username": "test", "password": "12345"}
        self.user = get_user_model().objects.create_user(**self.credentials)
        self.user.language = "ja"
        self.user.save(update_fields=["language"])
        self.client.login(**self.credentials)

    def test_home_renders_in_japanese(self):
        """The home page uses the Japanese catalog."""
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ホーム")
        self.assertContains(response, "統計")
        self.assertContains(response, "設定")
        self.assertNotContains(response, ">Home<")

    @patch("app.providers.services.get_media_metadata")
    def test_movie_details_render_in_japanese(self, mock_get_metadata):
        """A tracked movie shows Japanese status and detail labels."""
        mock_get_metadata.return_value = {
            "media_id": "238",
            "source": Sources.TMDB.value,
            "source_url": "https://www.themoviedb.org/movie/238",
            "media_type": MediaTypes.MOVIE.value,
            "title": "ゴッドファーザー",
            "image": "http://example.com/image.jpg",
            "synopsis": "あらすじ",
            "genres": ["犯罪"],
            "score": 8.7,
            "score_count": 2,
            "max_progress": 1,
            "details": {
                "release date": "1972-03-14",
                "status": "Released",
            },
        }
        item = Item.objects.create(
            media_id="238",
            source=Sources.TMDB.value,
            media_type=MediaTypes.MOVIE.value,
            title="ゴッドファーザー",
            image="http://example.com/image.jpg",
        )
        Movie.objects.create(
            item=item,
            user=self.user,
            status=Status.COMPLETED.value,
        )

        response = self.client.get(
            reverse(
                "media_details",
                kwargs={
                    "source": Sources.TMDB.value,
                    "media_type": MediaTypes.MOVIE.value,
                    "media_id": "238",
                    "title": "godfather",
                },
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "詳細")
        self.assertContains(response, "視聴済み")
        self.assertContains(response, "公開日")
        self.assertContains(response, "公開済み")
        self.assertContains(response, "視聴済み")
        self.assertContains(response, "2件")
        self.assertContains(response, "折りたたむ")

    @patch("app.providers.services.get_media_metadata")
    def test_anime_details_render_in_japanese(self, mock_get_metadata):
        """An anime detail page uses Japanese section labels."""
        mock_get_metadata.return_value = {
            "media_id": "1",
            "source": Sources.MAL.value,
            "source_url": "https://myanimelist.net/anime/1",
            "media_type": MediaTypes.ANIME.value,
            "title": "カウボーイビバップ",
            "image": "http://example.com/image.jpg",
            "synopsis": "あらすじ",
            "genres": ["アクション"],
            "score": 8.7,
            "score_count": 1,
            "details": {
                "format": "TV",
                "status": "放送終了",
                "episodes": 26,
            },
            "related": {},
        }

        response = self.client.get(
            reverse(
                "media_details",
                kwargs={
                    "source": Sources.MAL.value,
                    "media_type": MediaTypes.ANIME.value,
                    "media_id": "1",
                    "title": "cowboy-bebop",
                },
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "カウボーイビバップ")
        self.assertContains(response, "詳細")
        self.assertContains(response, "記録に追加")
        self.assertContains(response, "形式")
        self.assertContains(response, 'lang="ja"')
