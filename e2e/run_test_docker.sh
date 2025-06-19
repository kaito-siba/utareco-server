#!/usr/bin/env bash
set -euo pipefail

# e2eテストをDocker環境で実行するスクリプト

# 利用可能なテストケース
AVAILABLE_CASES=("case01" "case02" "case03" "case04" "case05")

# ヘルプメッセージを表示
show_help() {
    echo "使用方法: $0 [OPTIONS] [CASE...]"
    echo ""
    echo "OPTIONS:"
    echo "  -h, --help     このヘルプメッセージを表示"
    echo "  -a, --all      すべてのテストケースを実行（デフォルト）"
    echo ""
    echo "CASE:"
    echo "  実行するテストケースを指定（複数指定可能）"
    echo "  利用可能なテストケース: ${AVAILABLE_CASES[*]}"
    echo ""
    echo "例:"
    echo "  $0                    # すべてのテストケースを実行"
    echo "  $0 --all              # すべてのテストケースを実行"
    echo "  $0 case01             # CASE01のみ実行"
    echo "  $0 case01 case03      # CASE01とCASE03を実行"
}

# テストケースが有効かチェック
is_valid_case() {
    local case_name="$1"
    for valid_case in "${AVAILABLE_CASES[@]}"; do
        if [[ "$case_name" == "$valid_case" ]]; then
            return 0
        fi
    done
    return 1
}

# 特定のテストケースを実行
run_test_case() {
    local case_name="$1"
    local case_upper=$(echo "$case_name" | tr '[:lower:]' '[:upper:]')

    echo "${case_upper}テストを実行中..."
    docker run --rm \
        -v "$(pwd)/app:/app/app:ro" \
        -v "$(pwd)/e2e:/app/e2e:ro" \
        -w /app \
        utareco-test \
        python3 "e2e/${case_name}/test_case.py"
}

# 引数を解析
CASES_TO_RUN=()
RUN_ALL=false

if [[ $# -eq 0 ]]; then
    RUN_ALL=true
fi

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -a|--all)
            RUN_ALL=true
            shift
            ;;
        case*)
            if is_valid_case "$1"; then
                CASES_TO_RUN+=("$1")
            else
                echo "エラー: 無効なテストケース '$1'"
                echo "利用可能なテストケース: ${AVAILABLE_CASES[*]}"
                exit 1
            fi
            shift
            ;;
        *)
            echo "エラー: 無効なオプション '$1'"
            show_help
            exit 1
            ;;
    esac
done

# すべてのテストケースを実行する場合
if [[ "$RUN_ALL" == true ]]; then
    CASES_TO_RUN=("${AVAILABLE_CASES[@]}")
fi

# 実行するテストケースが指定されていない場合
if [[ ${#CASES_TO_RUN[@]} -eq 0 ]]; then
    echo "エラー: 実行するテストケースが指定されていません"
    show_help
    exit 1
fi

echo "Docker環境でe2eテストを実行します..."
echo "実行するテストケース: ${CASES_TO_RUN[*]}"

# Dockerイメージをビルド
echo "Dockerイメージをビルド中..."
docker build -f Dockerfile.test -t utareco-test .

# 指定されたテストケースを実行
for case_name in "${CASES_TO_RUN[@]}"; do
    run_test_case "$case_name"
done

echo "指定されたテストが完了しました。"