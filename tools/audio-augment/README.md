# Audio Augment

音声ファイルのキー（ピッチ）とテンポを変更するユーティリティツールです。

## インストール

```bash
# 開発モードでインストール
uv pip install -e .
```

## 使い方

### 単一ファイルの処理

```bash
# 3半音上げる
uv run audio-augment input.wav output.wav -p 3

# テンポを0.8倍（遅く）にする
uv run audio-augment input.wav output.wav -t 0.8

# 2半音下げて、1.2倍速にする
uv run audio-augment input.wav output.wav -p -2 -t 1.2

# 詳細な出力を表示
uv run audio-augment input.wav output.wav -p 1 -v
```

### バッチ処理

ディレクトリ内のすべての音声ファイルを一括処理します。

```bash
# デフォルト設定でバッチ処理
uv run audio-augment-batch batch input_dir output_dir

# ピッチを-5から5半音、1半音刻みで変更
uv run audio-augment-batch batch input_dir output_dir -p -5 5 -s 1

# テンポを0.5から2.0倍、0.25刻みで変更
uv run audio-augment-batch batch input_dir output_dir -t 0.5 2.0 --tempo-step 0.25

# 特定の拡張子のみ処理
uv run audio-augment-batch batch input_dir output_dir -e wav -e mp3
```

## 機能

- **ピッチシフト**: 音声のキーを半音単位で変更
- **テンポ変更**: 音声の再生速度を変更（ピッチは維持）
- **バッチ処理**: 複数ファイルの一括処理
- **フォーマット対応**: WAV, MP3, FLAC など主要な音声フォーマットに対応

## 開発

```bash
# 依存関係のインストール
uv sync

# コードフォーマット
uv run ruff format .

# リント
uv run ruff check .

# 型チェック
uv run pyright

# テスト実行
uv run pytest --cov
```

## 注意事項

- M4Aファイルなど一部のフォーマットは直接サポートされていません
- 音声処理にはRubberBandライブラリを使用しています
- 処理結果の音質は元の音声ファイルとパラメータに依存します