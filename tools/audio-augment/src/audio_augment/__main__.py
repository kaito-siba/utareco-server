"""パッケージをスクリプトとして実行するためのエントリーポイント"""

from .cli import augment

if __name__ == "__main__":
    # 単一ファイル処理がデフォルト
    augment()
