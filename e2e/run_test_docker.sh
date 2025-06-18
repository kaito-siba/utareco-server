#!/usr/bin/env bash
set -euo pipefail

# e2eテストをDocker環境で実行するスクリプト

echo "Docker環境でe2eテストを実行します..."

# Dockerイメージをビルド
echo "Dockerイメージをビルド中..."
docker build -f Dockerfile.test -t utareco-test .

# CASE01テストを実行
echo "CASE01テストを実行中..."
docker run --rm \
    -v "$(pwd)/app:/app/app:ro" \
    -v "$(pwd)/e2e:/app/e2e:ro" \
    -w /app \
    utareco-test \
    python3 e2e/case01/test_case.py

# CASE02テストを実行
echo "CASE02テストを実行中..."
docker run --rm \
    -v "$(pwd)/app:/app/app:ro" \
    -v "$(pwd)/e2e:/app/e2e:ro" \
    -w /app \
    utareco-test \
    python3 e2e/case02/test_case.py

# CASE03テストを実行
echo "CASE03テストを実行中..."
docker run --rm \
    -v "$(pwd)/app:/app/app:ro" \
    -v "$(pwd)/e2e:/app/e2e:ro" \
    -w /app \
    utareco-test \
    python3 e2e/case03/test_case.py

echo "全てのテストが完了しました。"