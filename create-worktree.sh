#!/bin/bash

# スクリプトの開始
echo "Git Worktree 作成スクリプト"
echo "=========================="

# worktree 名の入力を求める
read -p "Worktree 名を入力してください: " WORKTREE_NAME

# 入力値の検証
if [ -z "$WORKTREE_NAME" ]; then
    echo "エラー: Worktree 名が入力されていません"
    exit 1
fi

# worktrees ディレクトリの作成（存在しない場合）
if [ ! -d "worktrees" ]; then
    echo "worktrees ディレクトリを作成します..."
    mkdir -p worktrees
fi

# worktree のパス
WORKTREE_PATH="worktrees/$WORKTREE_NAME"

# 既存の worktree チェック
if [ -d "$WORKTREE_PATH" ]; then
    echo "エラー: $WORKTREE_PATH は既に存在します"
    exit 1
fi

# 現在のブランチ名を取得
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# worktree の作成
echo "Git worktree を作成します: $WORKTREE_PATH"
git worktree add "$WORKTREE_PATH" -b "$WORKTREE_NAME" "$CURRENT_BRANCH"

if [ $? -ne 0 ]; then
    echo "エラー: Git worktree の作成に失敗しました"
    exit 1
fi

# worktree ディレクトリに移動
cd "$WORKTREE_PATH" || exit 1

echo ""
echo "依存関係をインストールします..."
echo "=============================="

# Python の依存関係インストール
echo ""
echo "Python の依存関係をインストール中..."
uv sync

if [ $? -ne 0 ]; then
    echo "エラー: Python の依存関係インストールに失敗しました"
    exit 1
fi

# 完了メッセージ
echo ""
echo "✅ Worktree の作成と依存関係のインストールが完了しました！"
echo ""
echo "Worktree パス: $WORKTREE_PATH"
echo ""
echo "以下のコマンドで worktree に移動できます:"
echo "  cd $WORKTREE_PATH"
echo ""
echo "開発サーバーを起動する場合:"
echo "  cd $WORKTREE_PATH && uv run uvicorn app.main:app --reload"
echo ""
echo "テストを実行する場合:"
echo "  cd $WORKTREE_PATH && uv run pytest"
echo ""
echo "Worktree の一覧を確認:"
echo "  git worktree list"
echo ""
echo "Worktree を削除する場合:"
echo "  git worktree remove $WORKTREE_PATH"

# worktree ディレクトリに移動するか確認
echo ""
read -p "作成したワークツリーに移動しますか？ (y/N): " MOVE_TO_WORKTREE

if [[ $MOVE_TO_WORKTREE =~ ^[Yy]$ ]]; then
    echo ""
    echo "ワークツリーディレクトリに移動します..."
    echo "新しいシェルを起動します。exit で元のディレクトリに戻ります。"
    echo ""
    cd "$WORKTREE_PATH"
    exec $SHELL
else
    echo ""
    echo "ワークツリーの準備が完了しました。"
    echo "必要に応じて 'cd $WORKTREE_PATH' で移動してください。"
fi