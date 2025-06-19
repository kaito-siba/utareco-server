"""データベース接続とセッション管理モジュール."""

from collections.abc import Generator
from pathlib import Path

import sqlite_vec
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

# データベースファイルのパス
DATABASE_PATH = Path("utareco.db")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# SQLAlchemy設定
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


@event.listens_for(Engine, "connect")
def load_sqlite_vec(dbapi_connection, connection_record):
    """SQLite接続時にsqlite-vec拡張を自動ロード."""
    # sqlite-vec拡張をロード
    dbapi_connection.enable_load_extension(True)
    sqlite_vec.load(dbapi_connection)
    dbapi_connection.enable_load_extension(False)
    
    # SQLiteの設定を最適化
    dbapi_connection.execute("PRAGMA foreign_keys = ON")
    dbapi_connection.execute("PRAGMA journal_mode = WAL")  # Write-Ahead Logging
    dbapi_connection.execute("PRAGMA synchronous = NORMAL")  # パフォーマンス向上
    dbapi_connection.execute("PRAGMA temp_store = MEMORY")  # 一時ファイルをメモリに


def get_db() -> Generator[Session, None, None]:
    """データベースセッションを取得するジェネレータ（FastAPI依存関数）."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """データベーステーブルを作成."""
    Base.metadata.create_all(bind=engine)


def init_database():
    """データベースを初期化（テーブル作成とベクトル拡張設定）."""
    create_tables()

    # sqlite-vecテーブルの初期化
    with SessionLocal() as db:
        # HPCP特徴量ベクトルテーブル（フレーム単位）
        db.execute(
            text("""
            CREATE VIRTUAL TABLE IF NOT EXISTS hpcp_frames USING vec0(
                recording_id INTEGER,
                frame_index INTEGER,
                hpcp_vector FLOAT[12]
            )
        """)
        )

        # 楽曲レベル統計的特徴量ベクトルテーブル
        db.execute(
            text("""
            CREATE VIRTUAL TABLE IF NOT EXISTS hpcp_summary USING vec0(
                recording_id INTEGER,
                mean_vector FLOAT[12],
                std_vector FLOAT[12],
                dominant_chord FLOAT[12]
            )
        """)
        )

        db.commit()
