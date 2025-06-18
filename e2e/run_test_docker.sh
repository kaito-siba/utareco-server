#!/usr/bin/env bash
set -euo pipefail

# e2eテストをDocker環境で実行するスクリプト

echo "Docker環境でe2eテストを実行します..."

# Dockerイメージをビルド
echo "Dockerイメージをビルド中..."
docker build -f Dockerfile.test -t utareco-test .

# テストを実行
echo "CASE01テストを実行中..."
docker run --rm \
    -v "$(pwd)/app:/app/app:ro" \
    -v "$(pwd)/e2e:/app/e2e:ro" \
    -w /app \
    utareco-test \
    python3 e2e/case01/test_case01.py

echo "テストが完了しました。"