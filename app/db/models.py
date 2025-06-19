"""SQLAlchemyデータベースモデル定義."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, LargeBinary, String
from sqlalchemy.orm import relationship

from .database import Base


class Song(Base):
    """楽曲情報モデル.

    楽曲の基本メタデータを格納するテーブル。
    複数の音源（Recording）が一つの楽曲に紐づく。
    """

    __tablename__ = "songs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, comment="楽曲タイトル")
    artist = Column(String, nullable=True, comment="アーティスト名")
    created_at = Column(DateTime, default=datetime.utcnow, comment="作成日時")
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新日時"
    )

    # リレーション
    recordings = relationship(
        "Recording", back_populates="song", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Song(id={self.id}, title='{self.title}', artist='{self.artist}')>"


class Recording(Base):
    """録音データモデル.

    音源ファイルの情報を格納するテーブル。
    一つの楽曲（Song）に対して複数の音源が存在する。
    """

    __tablename__ = "recordings"

    id = Column(Integer, primary_key=True, index=True)
    song_id = Column(
        Integer, ForeignKey("songs.id"), nullable=False, comment="楽曲ID（外部キー）"
    )
    recording_name = Column(
        String, nullable=False, comment="音源名（例：オリジナル、カラオケ、ピッチ+2等）"
    )
    duration = Column(Float, nullable=False, comment="音源の長さ（秒）")
    sample_rate = Column(Integer, nullable=False, comment="サンプルレート（Hz）")
    audio_path = Column(String, nullable=False, comment="音声ファイルのパス")
    created_at = Column(DateTime, default=datetime.utcnow, comment="作成日時")
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新日時"
    )

    # リレーション
    song = relationship("Song", back_populates="recordings")
    hpcp_features = relationship(
        "HPCPFeature", back_populates="recording", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<Recording(id={self.id}, song_id={self.song_id}, "
            f"name='{self.recording_name}')>"
        )


class HPCPFeature(Base):
    """HPCP特徴量モデル.

    RecordingテーブルのHPCP特徴量データを格納するテーブル。
    numpy配列をバイナリデータとして保存。
    """

    __tablename__ = "hpcp_features"

    id = Column(Integer, primary_key=True, index=True)
    recording_id = Column(
        Integer,
        ForeignKey("recordings.id"),
        nullable=False,
        comment="録音データID（外部キー）",
    )
    hpcp_data = Column(
        LargeBinary, nullable=False, comment="HPCP特徴量データ（numpy配列をバイナリ化）"
    )
    frame_count = Column(Integer, nullable=False, comment="フレーム数")
    hop_size = Column(Integer, nullable=False, comment="ホップサイズ")
    created_at = Column(DateTime, default=datetime.utcnow, comment="作成日時")

    # リレーション
    recording = relationship("Recording", back_populates="hpcp_features")

    def __repr__(self) -> str:
        return (
            f"<HPCPFeature(id={self.id}, recording_id={self.recording_id}, "
            f"frame_count={self.frame_count})>"
        )
