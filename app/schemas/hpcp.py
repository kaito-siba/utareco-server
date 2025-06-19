"""HPCP特徴量API用Pydanticスキーマ定義."""

import base64
from datetime import datetime

import numpy as np
from pydantic import BaseModel, Field, validator


class SongInfo(BaseModel):
    """楽曲情報."""

    id: int = Field(..., description="楽曲ID")
    title: str = Field(..., description="楽曲タイトル")
    artist: str | None = Field(None, description="アーティスト名")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")


class RecordingInfo(BaseModel):
    """録音データ情報."""

    id: int = Field(..., description="録音データID")
    song_id: int = Field(..., description="楽曲ID")
    recording_name: str = Field(..., description="音源名")
    duration: float = Field(..., description="音源の長さ（秒）")
    sample_rate: int = Field(..., description="サンプルレート（Hz）")
    created_at: datetime = Field(..., description="作成日時")
    has_hpcp_features: bool = Field(..., description="HPCP特徴量存在フラグ")
    song: SongInfo = Field(..., description="楽曲情報")


class HPCPExtractionRequest(BaseModel):
    """HPCP特徴量抽出リクエスト.

    Note:
        音声ファイルは multipart/form-data で送信されるため、
        このスキーマには含まれない。

        新規楽曲作成または既存楽曲への音源追加の両方に対応。
    """

    # 既存楽曲への音源追加の場合
    song_id: int | None = Field(
        None, description="既存楽曲ID（既存楽曲に音源を追加する場合）"
    )

    # 新規楽曲作成の場合
    title: str | None = Field(
        None, description="楽曲タイトル（新規楽曲作成の場合）", max_length=200
    )
    artist: str | None = Field(
        None, description="アーティスト名（新規楽曲作成の場合）", max_length=200
    )

    # 共通
    recording_name: str = Field(..., description="音源名", min_length=1, max_length=100)

    @validator("title")
    def validate_title_or_song_id(cls, v, values):
        """song_idまたはtitleのいずれかが必須."""
        song_id = values.get("song_id")
        if not song_id and not v:
            raise ValueError("song_idまたはtitleのいずれかが必須です")
        if song_id and v:
            raise ValueError("song_idとtitleは同時に指定できません")
        return v


# 新しい分離されたAPIのスキーマ
class HPCPExtractionOnlyResponse(BaseModel):
    """HPCP特徴量抽出のみレスポンス."""

    hpcp_data: str = Field(..., description="HPCP特徴量（Base64エンコード）")
    audio_info: dict = Field(..., description="音声ファイル基本情報")
    hpcp_stats: "HPCPStats" = Field(..., description="HPCP特徴量統計情報")
    processing_time: float = Field(..., description="処理時間（秒）")

    @classmethod
    def from_hpcp_array(
        cls,
        hpcp_array: np.ndarray,
        duration: float,
        sample_rate: int,
        processing_time: float,
    ) -> "HPCPExtractionOnlyResponse":
        """numpy配列からレスポンスを作成."""
        import pickle

        # HPCP配列をBase64エンコード
        hpcp_bytes = pickle.dumps(hpcp_array)
        hpcp_data = base64.b64encode(hpcp_bytes).decode("utf-8")

        # 音声情報
        audio_info = {
            "duration": duration,
            "sample_rate": sample_rate,
            "channels": 1,  # モノラル
            "format": "processed",
        }

        # HPCP統計情報
        hpcp_stats = HPCPStats(
            frame_count=hpcp_array.shape[0],
            feature_dimension=hpcp_array.shape[1],
            duration=duration,
            hop_size=2048,  # extract_hpcp関数のデフォルト
            sample_rate=sample_rate,
        )

        return cls(
            hpcp_data=hpcp_data,
            audio_info=audio_info,
            hpcp_stats=hpcp_stats,
            processing_time=processing_time,
        )


class HPCPSearchRequest(BaseModel):
    """類似楽曲検索リクエスト."""

    hpcp_data: str = Field(..., description="HPCP特徴量（Base64エンコード）")
    search_method: str = Field(
        "frames",
        description="検索方法",
        pattern="^(frames|mean|dominant|std)$",
    )
    limit: int = Field(5, description="取得する類似楽曲数", ge=1, le=50)

    def to_hpcp_array(self) -> np.ndarray:
        """Base64エンコードされたHPCP特徴量をnumpy配列に変換."""
        import pickle

        hpcp_bytes = base64.b64decode(self.hpcp_data.encode("utf-8"))
        hpcp_array = pickle.loads(hpcp_bytes)

        if not isinstance(hpcp_array, np.ndarray):
            raise ValueError("HPCP特徴量の形式が不正です")

        if hpcp_array.ndim != 2 or hpcp_array.shape[1] != 12:
            raise ValueError(
                f"HPCP配列は(フレーム数, 12)の形状である必要があります。"
                f"実際の形状: {hpcp_array.shape}"
            )

        return hpcp_array


class RecordingCreateRequest(BaseModel):
    """録音データ作成リクエスト."""

    # HPCP特徴量
    hpcp_data: str = Field(..., description="HPCP特徴量（Base64エンコード）")

    # 音源情報
    recording_name: str = Field(..., description="音源名", min_length=1, max_length=100)
    audio_file_name: str = Field(..., description="元の音声ファイル名")

    # 楽曲情報（既存楽曲への追加 or 新規楽曲作成）
    song_id: int | None = Field(
        None, description="既存楽曲ID（既存楽曲に音源を追加する場合）"
    )
    title: str | None = Field(
        None, description="楽曲タイトル（新規楽曲作成の場合）", max_length=200
    )
    artist: str | None = Field(
        None, description="アーティスト名（新規楽曲作成の場合）", max_length=200
    )

    @validator("title")
    def validate_title_or_song_id(cls, v, values):
        """song_idまたはtitleのいずれかが必須."""
        song_id = values.get("song_id")
        if not song_id and not v:
            raise ValueError("song_idまたはtitleのいずれかが必須です")
        if song_id and v:
            raise ValueError("song_idとtitleは同時に指定できません")
        return v

    def to_hpcp_array(self) -> np.ndarray:
        """Base64エンコードされたHPCP特徴量をnumpy配列に変換."""
        import pickle

        hpcp_bytes = base64.b64decode(self.hpcp_data.encode("utf-8"))
        hpcp_array = pickle.loads(hpcp_bytes)

        if not isinstance(hpcp_array, np.ndarray):
            raise ValueError("HPCP特徴量の形式が不正です")

        return hpcp_array


class RecordingCreateResponse(BaseModel):
    """録音データ作成レスポンス."""

    song: SongInfo = Field(..., description="楽曲情報")
    recording: RecordingInfo = Field(..., description="録音データ情報")
    vector_stored: bool = Field(..., description="ベクトルDB格納完了フラグ")
    processing_time: float = Field(..., description="処理時間（秒）")


class HPCPStats(BaseModel):
    """HPCP特徴量統計情報."""

    frame_count: int = Field(..., description="フレーム数")
    feature_dimension: int = Field(..., description="特徴量次元数（12）")
    duration: float = Field(..., description="楽曲の長さ（秒）")
    hop_size: int = Field(..., description="ホップサイズ")
    sample_rate: int = Field(..., description="サンプルレート（Hz）")


class HPCPExtractionResponse(BaseModel):
    """HPCP特徴量抽出レスポンス."""

    song: SongInfo = Field(..., description="楽曲情報")
    recording: RecordingInfo = Field(..., description="録音データ情報")
    hpcp_stats: HPCPStats = Field(..., description="HPCP特徴量統計情報")
    processing_time: float = Field(..., description="処理時間（秒）")
    vector_stored: bool = Field(..., description="ベクトルDB格納完了フラグ")


class SimilarRecording(BaseModel):
    """類似音源情報."""

    recording: RecordingInfo = Field(..., description="録音データ情報")
    similarity_score: float = Field(..., description="類似度スコア（0-1）")
    distance: float = Field(..., description="ベクトル距離")


class QueryRecording(BaseModel):
    """クエリ音源情報."""

    recording: RecordingInfo = Field(..., description="録音データ情報")


class SimilaritySearchResponse(BaseModel):
    """類似楽曲検索レスポンス."""

    query_recording: QueryRecording = Field(..., description="クエリ楽曲情報")
    similar_recordings: list[SimilarRecording] = Field(
        ..., description="類似楽曲リスト"
    )
    search_method: str = Field(..., description="検索方法")
    search_time: float = Field(..., description="検索時間（秒）")


class SongListResponse(BaseModel):
    """楽曲リストレスポンス."""

    songs: list[SongInfo] = Field(..., description="楽曲リスト")
    total_count: int = Field(..., description="総件数")
    page: int = Field(..., description="ページ番号")
    per_page: int = Field(..., description="1ページあたりの件数")


class RecordingListResponse(BaseModel):
    """録音データリストレスポンス."""

    recordings: list[RecordingInfo] = Field(..., description="録音データリスト")
    total_count: int = Field(..., description="総件数")
    page: int = Field(..., description="ページ番号")
    per_page: int = Field(..., description="1ページあたりの件数")


class VectorStats(BaseModel):
    """ベクトルデータベース統計情報."""

    total_frames: int = Field(..., description="総フレーム数")
    total_recordings: int = Field(..., description="総録音データ数")
    summary_records: int = Field(..., description="サマリーレコード数")


class ErrorResponse(BaseModel):
    """エラーレスポンス."""

    error: str = Field(..., description="エラーメッセージ")
    detail: str | None = Field(None, description="エラー詳細")
    error_code: str | None = Field(None, description="エラーコード")
