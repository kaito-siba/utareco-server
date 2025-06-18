# E2E テスト

このテストは開発におけるマイルストーンとして使用します。
この E2E テストをクリアすることを目標に開発を進めてください。

各テストケースは CASE_xx.md というファイル名で配置されています。
xx の部分は連番になっているので、順にクリアしていってください。

また、使用する音源データは e2e/datasets に配置しています。

# Docker 環境での e2e テスト実行方法

## 概要

Essentia ライブラリは特定の環境でのみ動作するため、e2e テストは Docker 環境で実行する必要があります。

## テスト実行手順

1. **テストスクリプトの実行**
   ```bash
   cd /path/to/utareco-server/worktrees/mvp
   ./e2e/run_test_docker.sh
   ```

このスクリプトは以下を自動的に実行します：

- Docker イメージのビルド
- CASE01.md に定義されたテストの実行
- 結果の表示

## 実装内容

### 同一性判定ロジック

- **HPCP 特徴抽出**: `app/core/audio/hpcp.py`

  - Essentia を使用して m4a ファイルから HPCP（Harmonic Pitch Class Profile）特徴を抽出
  - 12 次元のクロマベクトルをフレーム単位で生成

- **類似度計算**: `app/core/matching/similarity.py`
  - ChromaCrossSimilarity を使用して HPCP 特徴間の類似度を計算
  - CoverSongSimilarity で最終的な類似度スコアを算出
  - 閾値（デフォルト: 0.8）を超えた場合に同一と判定

### テスト内容

CASE01 では、3 つの楽曲の総当たり組み合わせ（6 通り）で同一性判定を実行：

- 同じ楽曲同士 → 同一と判定
- 異なる楽曲同士 → 異なると判定

## トラブルシューティング

- **Docker が起動していない場合**: Docker Desktop を起動してください
- **権限エラーの場合**: `chmod +x e2e/run_test_docker.sh`を実行してください
