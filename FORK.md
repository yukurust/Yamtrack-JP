# Yamtrack-JP

[FuzzyGrim/Yamtrack](https://github.com/FuzzyGrim/Yamtrack) を、日本語のまま使えるようにしたフォークです。画面の文言、日付、TMDB のメタデータ、MAL アニメのタイトルとあらすじを日本語にします。データベースのステータス値は英語のままなので、上流の Yamtrack と同じデータを引き続き使えます。

## 上流との差分

- 表示言語の初期値は `ja` です。ユーザーごとに日本語と英語を切り替えられます。
- `TMDB_LANG` の初期値は `ja-JP` です。映画とテレビ番組のタイトル、あらすじ、ジャンルは TMDB の日本語データになります。
- MAL のアニメは、言語が日本語のとき `alternative_titles.ja` をタイトルにします。あらすじは、開始日が近い TMDB のシーズン（クール）から取ります。取れないときは英語のまま残します。
- モデルの選択肢（`Completed` など）は英語のままです。画面では「視聴済み」「視聴中」「一時停止」「中断」「視聴予定」と表示します。

## 環境変数

| 変数 | 初期値 | 説明 |
| --- | --- | --- |
| `LANGUAGE_CODE` | `ja` | サイト全体の表示言語。`ja` / `en`、または `ja-JP` / `en-US` のように先頭で判定します。 |
| `TMDB_LANG` | `ja-JP` | TMDB に渡す言語。英語のメタデータに戻すときは `en`。 |
| `JA_META_DIR` | `/yamtrack/db`（`BASE_DIR/db`） | 日本語メタデータのキャッシュ置き場。 |

そのほかの環境変数は上流と同じです。データベースのボリュームも `/yamtrack/db` のままです。

設定画面の「言語」でユーザーごとに上書きできます。空欄のときは `LANGUAGE_CODE` に従います。ブラウザの `Accept-Language` では変わりません。

日付の初期値は ISO（`2026-01-18`）のままです。日本語の並びにするときは、設定の日付形式で「2026年1月18日」を選びます。言語が日本語のとき、形式を指定しない Django の日付は `2026年1月18日` になります。

## 日本語メタデータのキャッシュ

`JA_META_DIR` に次の2ファイルを置けます。キーはどちらも `mal|anime|{MALのID}` です。

- `ja_titles.json` … タイトルの上書き。値は文字列です。MAL の日本語タイトルより優先されます。
- `ja_meta.json` … タイトルとあらすじのキャッシュ。`synopsis_source` が `manual` のあらすじは、あとから取得しても上書きしません。

取得に失敗したときは、英語のタイトルとあらすじを残します。

## ビルドと起動

```bash
docker build -t ghcr.io/yukurust/yamtrack-jp:dev .
docker compose up -d
```

`docker-compose.yml` の `image` は上流の `ghcr.io/fuzzygrim/yamtrack` のままです。このフォークのイメージを使うときは、その行を `ghcr.io/yukurust/yamtrack-jp:dev` に変えるか、`docker compose build` 用にイメージ名を合わせてください。ボリューム `./db:/yamtrack/db` と、上流と同じ環境変数はそのまま使えます。

追加されるマイグレーションはユーザーの `language` 列と、日付形式の選択肢だけです。既存の行は空の言語（サイトの規定）のまま動き、ステータスの保存値は変わりません。

## コンテナイメージ

`.github/workflows/docker-image.yml` が、このリポジトリの `dev` への push とタグ `v*` で `ghcr.io/${{ github.repository }}` にイメージを公開します。このフォークでは `ghcr.io/yukurust/yamtrack-jp` です。ワークフローファイル自体は上流から変えていません。

## 上流を取り込む

GitHub の **Sync fork** で `FuzzyGrim/Yamtrack` の `dev` を取り込めます。手元から行うときは次のとおりです。

```bash
git remote add upstream https://github.com/FuzzyGrim/Yamtrack.git
git fetch upstream
git checkout dev
git merge upstream/dev
```

翻訳は `src/locale/ja/LC_MESSAGES/django.po` にまとめてあります。画面の文言を変えるときは、英語の文字列を `{% trans %}` や `gettext` で包んだままにして、このカタログに訳を足してください。ステータスやメディア種別のデータベース値は英語のままにしてください。
