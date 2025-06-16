# UtaReco

## 1. プロジェクト準備・環境構築

1. リポジトリ作成

   - GitHub/GitLab 上に新規リポジトリを作成
   - README に概要と開発手順の章立てを記載

2. 仮想環境＆依存関係管理（uv 使用）

   - `uv init` でプロジェクト初期化
   - `uv add essentia fastapi sqlalchemy[sqlite] pytest pyright ruff` などで依存登録

3. コーディング規約・CI 設定

   - `ruff.toml` で Lint＆Formatter 設定
   - Pyright 設定ファイル（`pyrightconfig.json`）作成
   - GitHub Actions で以下を自動実行

     - `ruff check`
     - `pyright`
     - `pytest --cov`

---

## 2. 音響特徴量（指紋）データベース登録機能

1. データベース設計

   - テーブル定義：

     - `recordings`（録音ファイル情報）
     - `hpcp_features`（HPCP 系列保存）

2. 録音ファイルのインポート CLI 実装（TDD で開発）

   - テスト：空ディレクトリ → ファイルなし返却
   - 実装：ディレクトリ走査 → 録音ファイル一覧取得

3. 前処理モジュール呼び出し（リサンプリング／ノイズ除去）

   - テスト：モック音声でサンプルレート変換が通ること
   - 実装：Essentia の前処理パイプライン

4. Essentia で HPCP 抽出

   - テスト：既知のサンプル音源で期待シリーズ長が得られること
   - 実装：`essentia.standard.HPCP` → ndarray → BLOB/JSON 保存

> ⚠️ Panako は一旦後回し（別 Issue で対応予定）

---

## 3. クエリ音声処理 API

1. サーバー起動・エンドポイント定義（FastAPI, TDD）

   - テスト：未実装エンドポイントへのアクセスで 404
   - Pydantic モデル：`QueryRequest`, `QueryResponse`

2. ファイル受信・保存

   - テスト：アップロードファイルのバリデーションエラー
   - 実装：一時領域への保存、WAV/MP3 チェック

3. 前処理パイプライン呼び出し

   - テスト：ダミー波形で前処理モジュールが呼ばれること
   - 実装：リサンプリング／ノイズ除去／長さ正規化

4. HPCP 抽出呼び出し

   - テスト：前処理後の信号で HPCP 計算が行われること
   - 実装：抽出 → 一時 DB またはキャッシュに保存

5. 初期レスポンス設計

   - テスト：空候補で `{candidates: [], status: "processing"}` を返す
   - 実装：FastAPI レスポンスモデル

---

## 4. マッチングロジック実装

1. 詳細類似度計算フェーズ

   - テスト：自作の小さな合成信号ペアで類似度計算が正しく動くこと
   - 実装：

     - `ChromaCrossSimilarity`／`CoverSongSimilarity` 呼び出し
     - `oti=True` で転調吸収
     - フレームスタッキング or ビート同期
     - 距離 → 類似度（例：`sim = exp(-d)`)

2. スコア評価・閾値判定

   - テスト：境界値（0.8）でマッチ/非マッチが正しく分かれること
   - 実装：上位 1 件選択＋閾値判定

3. 並列化・キャッシュ検討

   - テスト：並列処理時のスレッド安全性（モック DB）
   - 実装案検討（`concurrent.futures` or Celery ＋ Redis）

---

## 5. 結果提示＆運用機能

1. レスポンス組み立て

   - テスト：モック結果を渡して期待 JSON 構造になること
   - 実装：曲名／ID／スコア／キー差／テンポ差／処理時間

2. フロントエンドインターフェース（簡易 HTML or CLI）

   - テスト：静的 HTML でダミーデータが表示されること
   - 実装：Jinja2 テンプレート or CLI テーブル表示

3. API ドキュメント整備

   - テスト：OpenAPI スキーマに各エンドポイントが含まれること
   - 実装：FastAPI 自動ドキュメント

4. ロギング＆モニタリング

   - テスト：ログ出力モックで記録項目が揃うこと
   - 実装：

     - リクエスト／レスポンスログ
     - エラー通知（Slack Webhook）

5. Docker 化＆CI/CD

   - テスト：`docker-compose up --build` でサーバーが起動すること
   - 実装：`Dockerfile`／`docker-compose.yml` 作成
   - GitHub Actions でビルド＆プッシュ

---

**注記**

- 全フェーズとも、**TDD** を徹底し、Issue ごとにテストを書いてから実装を進めてください。
- Panako 対応は「後回しフェーズ」として Issue 化し、優先度低で管理します。
