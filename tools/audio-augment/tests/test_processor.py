"""音声処理機能のテスト"""

import numpy as np

from audio_augment.processor import pitch_shift, tempo_change


def test_pitch_shift():
    """ピッチシフト機能のテスト"""
    # サンプル音声データの生成（1秒間の440Hzサイン波）
    sample_rate = 44100
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio_data = np.sin(2 * np.pi * 440 * t)

    # ピッチシフト実行
    shifted = pitch_shift(audio_data, sample_rate, 2.0)

    # 結果の検証
    assert isinstance(shifted, np.ndarray)
    assert shifted.shape == audio_data.shape


def test_tempo_change():
    """テンポ変更機能のテスト"""
    # サンプル音声データの生成
    sample_rate = 44100
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio_data = np.sin(2 * np.pi * 440 * t)

    # テンポ変更実行（2倍速）
    stretched = tempo_change(audio_data, sample_rate, 2.0)

    # 結果の検証
    assert isinstance(stretched, np.ndarray)
    # 2倍速にしたので長さは約半分になるはず
    assert len(stretched) < len(audio_data)
