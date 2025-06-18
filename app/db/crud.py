"""データベースCRUD操作モジュール."""

import pickle
from pathlib import Path

import numpy as np
from sqlalchemy.orm import Session

from .models import HPCPFeature, Recording, Song


# Song関連のCRUD操作
def create_song(db: Session, title: str, artist: str | None = None) -> Song:
    """楽曲データを作成する.

    Args:
        db: データベースセッション
        title: 楽曲タイトル
        artist: アーティスト名（オプション）

    Returns:
        作成された楽曲データ
    """
    db_song = Song(title=title, artist=artist)
    db.add(db_song)
    db.commit()
    db.refresh(db_song)
    return db_song


def get_song(db: Session, song_id: int) -> Song | None:
    """楽曲データを取得する.

    Args:
        db: データベースセッション
        song_id: 楽曲ID

    Returns:
        楽曲データ、存在しない場合はNone
    """
    return db.query(Song).filter(Song.id == song_id).first()


def get_songs(db: Session, skip: int = 0, limit: int = 100) -> list[Song]:
    """楽曲データのリストを取得する.

    Args:
        db: データベースセッション
        skip: スキップするレコード数
        limit: 取得するレコード数の上限

    Returns:
        楽曲データのリスト
    """
    return db.query(Song).offset(skip).limit(limit).all()


def delete_song(db: Session, song_id: int) -> bool:
    """楽曲データを削除する（関連する録音データとHPCP特徴量も削除）.

    Args:
        db: データベースセッション
        song_id: 楽曲ID

    Returns:
        削除に成功した場合True、楽曲データが存在しない場合False
    """
    song = get_song(db, song_id)
    if not song:
        return False

    # 関連する音声ファイルも削除
    for recording in song.recordings:
        audio_path = Path(recording.audio_path)
        if audio_path.exists():
            audio_path.unlink()

    db.delete(song)
    db.commit()
    return True


# Recording関連のCRUD操作
def create_recording(
    db: Session,
    song_id: int,
    recording_name: str,
    duration: float,
    sample_rate: int,
    audio_path: str,
) -> Recording:
    """録音データを作成する.

    Args:
        db: データベースセッション
        song_id: 楽曲ID
        recording_name: 音源名（例：オリジナル、カラオケ、ピッチ+2等）
        duration: 音源の長さ（秒）
        sample_rate: サンプルレート（Hz）
        audio_path: 音声ファイルのパス

    Returns:
        作成された録音データ
    """
    db_recording = Recording(
        song_id=song_id,
        recording_name=recording_name,
        duration=duration,
        sample_rate=sample_rate,
        audio_path=audio_path,
    )
    db.add(db_recording)
    db.commit()
    db.refresh(db_recording)
    return db_recording


def get_recording(db: Session, recording_id: int) -> Recording | None:
    """録音データを取得する.

    Args:
        db: データベースセッション
        recording_id: 録音データID

    Returns:
        録音データ、存在しない場合はNone
    """
    return db.query(Recording).filter(Recording.id == recording_id).first()


def get_recordings(db: Session, skip: int = 0, limit: int = 100) -> list[Recording]:
    """録音データのリストを取得する.

    Args:
        db: データベースセッション
        skip: スキップするレコード数
        limit: 取得するレコード数の上限

    Returns:
        録音データのリスト
    """
    return db.query(Recording).offset(skip).limit(limit).all()


def delete_recording(db: Session, recording_id: int) -> bool:
    """録音データを削除する（関連するHPCP特徴量も削除）.

    Args:
        db: データベースセッション
        recording_id: 録音データID

    Returns:
        削除に成功した場合True、録音データが存在しない場合False
    """
    recording = get_recording(db, recording_id)
    if not recording:
        return False

    # 音声ファイルも削除
    audio_path = Path(recording.audio_path)
    if audio_path.exists():
        audio_path.unlink()

    db.delete(recording)
    db.commit()
    return True


def create_hpcp_feature(
    db: Session, recording_id: int, hpcp_array: np.ndarray, hop_size: int
) -> HPCPFeature:
    """HPCP特徴量を作成する.

    Args:
        db: データベースセッション
        recording_id: 録音データID
        hpcp_array: HPCP特徴量のnumpy配列（フレーム数 x 12）
        hop_size: ホップサイズ

    Returns:
        作成されたHPCP特徴量データ

    Raises:
        ValueError: HPCP配列の形状が不正な場合
    """
    if hpcp_array.ndim != 2 or hpcp_array.shape[1] != 12:
        raise ValueError(
            f"HPCP配列は(フレーム数, 12)の形状である必要があります。"
            f"実際の形状: {hpcp_array.shape}"
        )

    # numpy配列をバイナリ形式でシリアライズ
    hpcp_data = pickle.dumps(hpcp_array)

    db_hpcp = HPCPFeature(
        recording_id=recording_id,
        hpcp_data=hpcp_data,
        frame_count=hpcp_array.shape[0],
        hop_size=hop_size,
    )
    db.add(db_hpcp)
    db.commit()
    db.refresh(db_hpcp)
    return db_hpcp


def get_hpcp_feature(db: Session, recording_id: int) -> HPCPFeature | None:
    """録音データのHPCP特徴量を取得する.

    Args:
        db: データベースセッション
        recording_id: 録音データID

    Returns:
        HPCP特徴量データ、存在しない場合はNone
    """
    return (
        db.query(HPCPFeature).filter(HPCPFeature.recording_id == recording_id).first()
    )


def get_hpcp_array(db: Session, recording_id: int) -> np.ndarray | None:
    """録音データのHPCP特徴量をnumpy配列として取得する.

    Args:
        db: データベースセッション
        recording_id: 録音データID

    Returns:
        HPCP特徴量のnumpy配列、存在しない場合はNone

    Raises:
        ValueError: バイナリデータのデシリアライズに失敗した場合
    """
    hpcp_feature = get_hpcp_feature(db, recording_id)
    if not hpcp_feature:
        return None

    try:
        hpcp_array = pickle.loads(hpcp_feature.hpcp_data)
        if not isinstance(hpcp_array, np.ndarray):
            raise ValueError("デシリアライズされたデータがnumpy配列ではありません")
        return hpcp_array
    except (pickle.PickleError, ValueError) as e:
        raise ValueError(f"HPCP特徴量のデシリアライズに失敗しました: {e}") from e


def delete_hpcp_feature(db: Session, recording_id: int) -> bool:
    """録音データのHPCP特徴量を削除する.

    Args:
        db: データベースセッション
        recording_id: 録音データID

    Returns:
        削除に成功した場合True、HPCP特徴量が存在しない場合False
    """
    hpcp_feature = get_hpcp_feature(db, recording_id)
    if not hpcp_feature:
        return False

    db.delete(hpcp_feature)
    db.commit()
    return True
