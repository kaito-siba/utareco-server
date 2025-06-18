"""HPCP特徴量抽出・検索APIエンドポイント."""

import shutil
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Annotated

import essentia.standard as es  # type: ignore
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.audio.hpcp import extract_hpcp, normalize_hpcp
from app.core.vector.sqlite_vec_manager import SQLiteVecManager
from app.db.database import get_db
from app.schemas.hpcp import (
    HPCPExtractionOnlyResponse,
    HPCPSearchRequest,
    RecordingInfo,
    SimilaritySearchResponse,
    SongInfo,
)

router = APIRouter(prefix="/hpcp", tags=["HPCP"])

# サポートされる音声ファイル形式
SUPPORTED_AUDIO_FORMATS = {".wav", ".mp3", ".m4a", ".flac", ".ogg"}


@router.post("/extract-only", response_model=HPCPExtractionOnlyResponse)
async def extract_hpcp_only(
    file: Annotated[UploadFile, File(description="音声ファイル")],
) -> HPCPExtractionOnlyResponse:
    """音声ファイルからHPCP特徴量を抽出する（DB格納なし）.

    Args:
        file: アップロードされた音声ファイル

    Returns:
        HPCP特徴量と音声情報

    Raises:
        HTTPException: 各種エラー（ファイル形式、処理エラー等）
    """
    start_time = time.time()

    # ファイル形式チェック
    if not file.filename:
        raise HTTPException(status_code=400, detail="ファイル名が指定されていません")

    file_suffix = Path(file.filename).suffix.lower()
    if file_suffix not in SUPPORTED_AUDIO_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"サポートされていないファイル形式です。"
            f"サポート形式: {', '.join(SUPPORTED_AUDIO_FORMATS)}",
        )

    temp_audio_path = None

    try:
        # 一時ファイルに保存
        with tempfile.NamedTemporaryFile(suffix=file_suffix, delete=False) as temp_file:
            temp_audio_path = Path(temp_file.name)
            shutil.copyfileobj(file.file, temp_file)

        # 音声ファイルの基本情報を取得
        try:
            loader = es.MonoLoader(filename=str(temp_audio_path), sampleRate=44100)
            audio_data = loader()
            duration = len(audio_data) / 44100.0
            sample_rate = 44100
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"音声ファイルの読み込みに失敗しました: {str(e)}",
            ) from e

        # HPCP特徴量を抽出
        try:
            hpcp_array = extract_hpcp(temp_audio_path, sample_rate=sample_rate)
            hpcp_array = normalize_hpcp(hpcp_array)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"HPCP特徴量の抽出に失敗しました: {str(e)}"
            ) from e

        # 処理時間計算
        processing_time = time.time() - start_time

        # レスポンス作成
        return HPCPExtractionOnlyResponse.from_hpcp_array(
            hpcp_array=hpcp_array,
            duration=duration,
            sample_rate=sample_rate,
            processing_time=processing_time,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"処理中に内部エラーが発生しました: {str(e)}"
        ) from e
    finally:
        # クリーンアップ
        if temp_audio_path and temp_audio_path.exists():
            try:
                temp_audio_path.unlink()
            except Exception:
                pass


@router.post("/search", response_model=SimilaritySearchResponse)
async def search_similar_recordings(
    request: HPCPSearchRequest,
    db: Session = Depends(get_db),
) -> SimilaritySearchResponse:
    """HPCP特徴量による類似楽曲検索.

    Args:
        request: 検索リクエスト（HPCP特徴量、検索方法、取得件数）
        db: データベースセッション

    Returns:
        類似楽曲検索結果

    Raises:
        HTTPException: 各種エラー
    """
    start_time = time.time()

    vec_manager = None

    try:
        # HPCP特徴量を復元
        try:
            query_hpcp = request.to_hpcp_array()
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"HPCP特徴量の復元に失敗しました: {str(e)}"
            ) from e

        # sqlite-vecで類似楽曲検索
        try:
            vec_manager = SQLiteVecManager()

            if request.search_method == "frames":
                # フレーム単位検索
                search_results = vec_manager.search_similar_recordings_by_frames(
                    query_hpcp, k=request.limit
                )
            else:
                # 統計的特徴量検索
                search_results = vec_manager.search_similar_recordings_by_summary(
                    query_hpcp, k=request.limit, method=request.search_method
                )

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"類似楽曲検索に失敗しました: {str(e)}"
            ) from e

        # 検索結果を詳細情報に変換
        similar_recordings = []
        for recording_id, distance in search_results:
            from app.db.crud import get_recording

            recording = get_recording(db, recording_id)
            if recording and recording.song:
                # 距離を類似度スコアに変換（簡易的な変換）
                similarity_score = max(0.0, 1.0 - min(distance, 1.0))

                song_info = SongInfo(
                    id=recording.song.id,
                    title=recording.song.title,
                    artist=recording.song.artist,
                    created_at=recording.song.created_at,
                    updated_at=recording.song.updated_at,
                )

                recording_info = RecordingInfo(
                    id=recording.id,
                    song_id=recording.song_id,
                    recording_name=recording.recording_name,
                    duration=recording.duration,
                    sample_rate=recording.sample_rate,
                    created_at=recording.created_at,
                    has_hpcp_features=True,
                    song=song_info,
                )

                from app.schemas.hpcp import SimilarRecording

                similar_recordings.append(
                    SimilarRecording(
                        recording=recording_info,
                        similarity_score=similarity_score,
                        distance=distance,
                    )
                )

        # 処理時間計算
        search_time = time.time() - start_time

        # ダミーのクエリ録音情報（実際のクエリは録音データとして保存されていない）
        from app.schemas.hpcp import QueryRecording

        dummy_song_info = SongInfo(
            id=0,
            title="クエリ楽曲",
            artist=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        dummy_recording_info = RecordingInfo(
            id=0,
            song_id=0,
            recording_name="クエリ音源",
            duration=query_hpcp.shape[0] * 2048 / 44100.0,  # 概算時間
            sample_rate=44100,
            created_at=datetime.now(),
            has_hpcp_features=True,
            song=dummy_song_info,
        )

        query_recording = QueryRecording(recording=dummy_recording_info)

        return SimilaritySearchResponse(
            query_recording=query_recording,
            similar_recordings=similar_recordings,
            search_method=request.search_method,
            search_time=search_time,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"処理中に内部エラーが発生しました: {str(e)}"
        ) from e
    finally:
        if vec_manager:
            vec_manager.close()


@router.get("/stats")
async def get_vector_stats():
    """ベクトルデータベースの統計情報を取得する.

    Returns:
        ベクトルデータベースの統計情報
    """
    vec_manager = None
    try:
        vec_manager = SQLiteVecManager()
        stats = vec_manager.get_vector_stats()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"統計情報の取得に失敗しました: {str(e)}"
        ) from e
    finally:
        if vec_manager:
            vec_manager.close()
