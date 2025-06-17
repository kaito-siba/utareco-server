"""HPCP特徴抽出モジュール."""

from pathlib import Path

import essentia.standard as es  # type: ignore
import numpy as np


def extract_hpcp(audio_path: Path, sample_rate: int = 44100) -> np.ndarray:
    """音声ファイルからHPCP特徴を抽出する.

    Args:
        audio_path: 音声ファイルのパス
        sample_rate: サンプルレート（デフォルト: 44100Hz）

    Returns:
        HPCP特徴行列（フレーム数 x 12）

    Raises:
        RuntimeError: Essentiaでの処理中にエラーが発生した場合
        FileNotFoundError: 音声ファイルが存在しない場合
    """
    if not audio_path.exists():
        raise FileNotFoundError(f"音声ファイルが見つかりません: {audio_path}")

    try:
        # 音声ファイルを読み込み
        loader = es.MonoLoader(filename=str(audio_path), sampleRate=sample_rate)
        audio = loader()

        # スペクトラルピークを検出
        spectral_peaks = es.SpectralPeaks()

        # HPCP抽出器を初期化
        hpcp = es.HPCP(
            size=12,
            referenceFrequency=440,
            sampleRate=sample_rate,
            harmonics=8,
            bandPreset=True,
            minFrequency=100,
            maxFrequency=5000,
            bandSplitFrequency=500,
            weightType="cosine",
            nonLinear=False,
            windowSize=1.0,
        )

        # フレーム分割
        frame_size = 4096
        hop_size = 2048
        windowing = es.Windowing(type="blackmanharris62")
        spectrum = es.Spectrum(size=frame_size)

        # HPCP特徴を計算
        hpcps = []
        for frame in es.FrameGenerator(
            audio, frameSize=frame_size, hopSize=hop_size, startFromZero=True
        ):
            windowed_frame = windowing(frame)
            spec = spectrum(windowed_frame)
            frequencies, magnitudes = spectral_peaks(spec)
            hpcp_vector = hpcp(frequencies, magnitudes)
            hpcps.append(hpcp_vector)

        # numpy配列に変換
        hpcp_array = np.array(hpcps)

        return hpcp_array

    except Exception as e:
        raise RuntimeError(f"HPCP特徴抽出中にエラーが発生しました: {e}") from e


def normalize_hpcp(hpcp_array: np.ndarray) -> np.ndarray:
    """HPCP特徴を正規化する.

    Args:
        hpcp_array: HPCP特徴行列

    Returns:
        正規化されたHPCP特徴行列
    """
    # フレーム毎に正規化（L2ノルム）
    norms = np.linalg.norm(hpcp_array, axis=1, keepdims=True)
    # ゼロ除算を防ぐ
    norms[norms == 0] = 1.0
    return hpcp_array / norms
