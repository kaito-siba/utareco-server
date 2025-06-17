"""テスト用の音声ファイルを生成"""

import numpy as np
import soundfile as sf

# サンプリングレート
sample_rate = 44100

# 1秒間の440Hz（A4）のサイン波を生成
duration = 3.0  # 3秒
t = np.linspace(0, duration, int(sample_rate * duration))
frequency = 440.0  # A4の周波数
audio_data = 0.5 * np.sin(2 * np.pi * frequency * t)

# wavファイルとして保存
sf.write("test_audio.wav", audio_data, sample_rate)
print(f"テスト音声ファイルを生成しました: test_audio.wav ({duration}秒, {frequency}Hz)")
