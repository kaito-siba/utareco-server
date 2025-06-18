"""録音データ管理APIエンドポイント."""

import time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.vector.sqlite_vec_manager import SQLiteVecManager
from app.db.crud import create_hpcp_feature, create_recording, create_song, get_song
from app.db.database import get_db
from app.schemas.hpcp import (
    RecordingCreateRequest,
    RecordingCreateResponse,
    RecordingInfo,
    SongInfo,
)

router = APIRouter(prefix="/recordings", tags=["Recordings"])


@router.post("/create", response_model=RecordingCreateResponse)
async def create_recording_with_hpcp(
    request: RecordingCreateRequest,
    db: Session = Depends(get_db),
) -> RecordingCreateResponse:
    """HPCP特徴量を含む録音データを作成する.

    Args:
        request: 録音データ作成リクエスト
        db: データベースセッション

    Returns:
        作成された録音データと楽曲情報

    Raises:
        HTTPException: 各種エラー
    """
    start_time = time.time()
    vec_manager = None

    try:
        # HPCP特徴量を復元
        try:
            hpcp_array = request.to_hpcp_array()
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"HPCP特徴量の復元に失敗しました: {str(e)}"
            ) from e

        # 楽曲データを作成または取得
        try:
            if request.song_id:
                # 既存楽曲への音源追加
                song = get_song(db, request.song_id)
                if not song:
                    raise HTTPException(
                        status_code=404,
                        detail=f"楽曲ID {request.song_id} が見つかりません",
                    )
            else:
                # 新規楽曲作成
                song = create_song(
                    db=db,
                    title=request.title.strip(),
                    artist=request.artist.strip() if request.artist else None,
                )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"楽曲データの処理に失敗しました: {str(e)}"
            ) from e

        # 音声ファイルの保存（実際のファイル処理は省略、ファイル名のみ保存）
        # 注意: 実際の実装では音声ファイルの永続化処理が必要
        audio_path = f"uploads/{request.audio_file_name}"

        # データベースに録音データを保存
        try:
            # 音源の長さと sample_rate を HPCP特徴量から推定
            duration = (
                hpcp_array.shape[0] * 2048 / 44100.0
            )  # フレーム数 * hop_size / sample_rate
            sample_rate = 44100  # デフォルト値

            recording = create_recording(
                db=db,
                song_id=song.id,
                recording_name=request.recording_name.strip(),
                duration=duration,
                sample_rate=sample_rate,
                audio_path=audio_path,
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"録音データの保存に失敗しました: {str(e)}"
            ) from e

        # HPCP特徴量をデータベースに保存
        try:
            hop_size = 2048  # extract_hpcp関数で使用されているホップサイズ
            create_hpcp_feature(
                db=db,
                recording_id=recording.id,
                hpcp_array=hpcp_array,
                hop_size=hop_size,
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"HPCP特徴量の保存に失敗しました: {str(e)}"
            ) from e

        # sqlite-vecにベクトルデータを格納
        vector_stored = False
        try:
            vec_manager = SQLiteVecManager()
            vec_manager.initialize_vector_tables()
            vec_manager.store_hpcp_vectors(recording.id, hpcp_array)
            vector_stored = True
        except Exception as e:
            # ベクトル格納エラーは警告レベルとし、APIは成功として扱う
            print(f"警告: ベクトルデータの格納に失敗しました: {str(e)}")
        finally:
            if vec_manager:
                vec_manager.close()

        # 処理時間計算
        processing_time = time.time() - start_time

        # レスポンス用のSongInfoとRecordingInfoを構築
        song_info = SongInfo(
            id=song.id,
            title=song.title,
            artist=song.artist,
            created_at=song.created_at,
            updated_at=song.updated_at,
        )

        recording_info = RecordingInfo(
            id=recording.id,
            song_id=recording.song_id,
            recording_name=recording.recording_name,
            duration=recording.duration,
            sample_rate=recording.sample_rate,
            created_at=recording.created_at,
            has_hpcp_features=True,  # HPCP特徴量を作成したばかりなのでTrue
            song=song_info,
        )

        return RecordingCreateResponse(
            song=song_info,
            recording=recording_info,
            vector_stored=vector_stored,
            processing_time=processing_time,
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
