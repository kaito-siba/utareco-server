"""音声処理の核となる機能を提供"""

from pathlib import Path
from typing import Optional, Union

import numpy as np
import pyrubberband as pyrb
import soundfile as sf


def pitch_shift(
    audio_data: np.ndarray,
    sample_rate: int,
    semitones: float,
) -> np.ndarray:
    """音声のピッチを変更する（キー変更）

    Args:
        audio_data: 音声データ（numpy配列）
        sample_rate: サンプリングレート
        semitones: ピッチシフト量（半音単位、正で高く、負で低く）

    Returns:
        ピッチシフトされた音声データ

    Example:
        >>> audio, sr = sf.read("input.wav")
        >>> shifted = pitch_shift(audio, sr, 2.0)  # 2半音上げる
    """
    return pyrb.pitch_shift(audio_data, sample_rate, semitones)


def tempo_change(
    audio_data: np.ndarray,
    sample_rate: int,
    rate: float,
) -> np.ndarray:
    """音声のテンポを変更する（タイムストレッチ）

    Args:
        audio_data: 音声データ（numpy配列）
        sample_rate: サンプリングレート
        rate: テンポ変更率（1.0が元のテンポ、2.0で2倍速、0.5で半分）

    Returns:
        テンポ変更された音声データ

    Example:
        >>> audio, sr = sf.read("input.wav")
        >>> stretched = tempo_change(audio, sr, 1.2)  # 1.2倍速
    """
    return pyrb.time_stretch(audio_data, sample_rate, rate)


def process_audio_file(
    input_path: Union[str, Path],
    output_path: Union[str, Path],
    pitch_shift_semitones: Optional[float] = None,
    tempo_rate: Optional[float] = None,
) -> None:
    """音声ファイルを処理してキー・テンポを変更

    Args:
        input_path: 入力音声ファイルのパス
        output_path: 出力音声ファイルのパス
        pitch_shift_semitones: ピッチシフト量（半音単位）
        tempo_rate: テンポ変更率

    Raises:
        ValueError: ピッチシフトとテンポ変更の両方が指定されていない場合
        FileNotFoundError: 入力ファイルが存在しない場合

    Example:
        >>> process_audio_file("input.wav", "output.wav", pitch_shift_semitones=3)
        >>> process_audio_file("input.wav", "output.wav", tempo_rate=0.8)
        >>> process_audio_file(
        ...     "input.wav", "output.wav",
        ...     pitch_shift_semitones=-2, tempo_rate=1.1
        ... )
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        raise FileNotFoundError(f"入力ファイルが見つかりません: {input_path}")

    if pitch_shift_semitones is None and tempo_rate is None:
        raise ValueError(
            "ピッチシフトまたはテンポ変更の少なくとも一方を指定してください"
        )

    # 音声ファイルを読み込む
    audio_data, sample_rate = sf.read(str(input_path))

    # ピッチシフト処理
    if pitch_shift_semitones is not None and pitch_shift_semitones != 0:
        audio_data = pitch_shift(audio_data, sample_rate, pitch_shift_semitones)

    # テンポ変更処理
    if tempo_rate is not None and tempo_rate != 1.0:
        audio_data = tempo_change(audio_data, sample_rate, tempo_rate)

    # 出力ディレクトリが存在しない場合は作成
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 処理済み音声を書き出す
    sf.write(str(output_path), audio_data, sample_rate)
