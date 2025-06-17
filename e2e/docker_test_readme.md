# Docker環境でのe2eテスト実行方法

## 概要

Essentiaライブラリは特定の環境でのみ動作するため、e2eテストはDocker環境で実行する必要があります。

## テスト実行手順

1. **テストスクリプトの実行**
   ```bash
   cd /path/to/utareco-server/worktrees/mvp
   ./e2e/run_test_docker.sh
   ```

このスクリプトは以下を自動的に実行します：
- Dockerイメージのビルド
- CASE01.mdに定義されたテストの実行
- 結果の表示

## 実装内容

### 同一性判定ロジック

- **HPCP特徴抽出**: `app/core/audio/hpcp.py`
  - Essentiaを使用してm4aファイルからHPCP（Harmonic Pitch Class Profile）特徴を抽出
  - 12次元のクロマベクトルをフレーム単位で生成

- **類似度計算**: `app/core/matching/similarity.py`
  - ChromaCrossSimilarityを使用してHPCP特徴間の類似度を計算
  - CoverSongSimilarityで最終的な類似度スコアを算出
  - 閾値（デフォルト: 0.8）を超えた場合に同一と判定

### テスト内容

CASE01では、3つの楽曲の総当たり組み合わせ（6通り）で同一性判定を実行：
- 同じ楽曲同士 → 同一と判定
- 異なる楽曲同士 → 異なると判定

## トラブルシューティング

- **Dockerが起動していない場合**: Docker Desktopを起動してください
- **権限エラーの場合**: `chmod +x e2e/run_test_docker.sh`を実行してください