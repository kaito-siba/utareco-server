"""高度な音声の同一性判定モジュール."""

import numpy as np


def calculate_hpcp_histogram(hpcp: np.ndarray, bins: int = 24) -> np.ndarray:
    """HPCP特徴のヒストグラムを計算する.

    Args:
        hpcp: HPCP特徴行列
        bins: ヒストグラムのビン数

    Returns:
        正規化されたヒストグラム
    """
    # 各ピッチクラスの強度分布を計算
    histograms = []
    for i in range(12):
        hist, _ = np.histogram(hpcp[:, i], bins=bins, range=(0, 1))
        histograms.append(hist)

    # 結合して正規化
    histogram = np.concatenate(histograms)
    return histogram / (np.sum(histogram) + 1e-6)


def calculate_temporal_features(hpcp: np.ndarray) -> np.ndarray:
    """時系列特徴を計算する.

    Args:
        hpcp: HPCP特徴行列

    Returns:
        時系列特徴ベクトル
    """
    # セグメント分割（10分割）
    n_segments = 10
    segment_size = len(hpcp) // n_segments

    segment_features = []
    for i in range(n_segments):
        start = i * segment_size
        end = (i + 1) * segment_size if i < n_segments - 1 else len(hpcp)
        segment = hpcp[start:end]

        # セグメントの平均と標準偏差
        mean = np.mean(segment, axis=0)
        std = np.std(segment, axis=0)
        segment_features.extend(mean)
        segment_features.extend(std)

    return np.array(segment_features)


def calculate_similarity_advanced(
    hpcp_query: np.ndarray, hpcp_reference: np.ndarray
) -> float:
    """高度な特徴を使用して類似度を計算する.

    Args:
        hpcp_query: クエリ音声のHPCP特徴行列
        hpcp_reference: 参照音声のHPCP特徴行列

    Returns:
        similarity_score: 類似度スコア（0.0-1.0）
    """
    # 1. グローバル特徴（平均HPCP）
    mean_query = np.mean(hpcp_query, axis=0)
    mean_reference = np.mean(hpcp_reference, axis=0)

    # 正規化
    mean_query = mean_query / (np.linalg.norm(mean_query) + 1e-6)
    mean_reference = mean_reference / (np.linalg.norm(mean_reference) + 1e-6)

    # 最適な転調を見つける
    global_similarities = []
    for shift in range(12):
        shifted_query = np.roll(mean_query, shift)
        sim = np.dot(shifted_query, mean_reference)
        global_similarities.append(sim)

    best_shift = np.argmax(global_similarities)
    global_similarity = global_similarities[best_shift]

    # 2. ヒストグラム特徴
    hist_query = calculate_hpcp_histogram(hpcp_query)
    hist_reference = calculate_hpcp_histogram(hpcp_reference)

    # ヒストグラムの類似度（転調不変）
    hist_similarity = 1.0 - np.sum(np.abs(hist_query - hist_reference)) / 2

    # 3. 時系列特徴（最適転調でシフト）
    shifted_hpcp_query = np.roll(hpcp_query, best_shift, axis=1)
    temporal_query = calculate_temporal_features(shifted_hpcp_query)
    temporal_reference = calculate_temporal_features(hpcp_reference)

    # 正規化
    temporal_query = temporal_query / (np.linalg.norm(temporal_query) + 1e-6)
    temporal_reference = temporal_reference / (
        np.linalg.norm(temporal_reference) + 1e-6
    )

    temporal_similarity = np.dot(temporal_query, temporal_reference)

    # 重み付け平均
    weights = [0.3, 0.3, 0.4]  # global, histogram, temporal
    final_similarity = (
        weights[0] * global_similarity
        + weights[1] * hist_similarity
        + weights[2] * temporal_similarity
    )

    return float(final_similarity)


def is_same_recording_advanced(
    hpcp_query: np.ndarray,
    hpcp_reference: np.ndarray,
    threshold: float = 0.85,
) -> bool:
    """高度な特徴で2つの音声が同一録音かどうかを判定する.

    Args:
        hpcp_query: クエリ音声のHPCP特徴行列
        hpcp_reference: 参照音声のHPCP特徴行列
        threshold: 同一判定のための閾値

    Returns:
        同一録音の場合True、異なる場合False
    """
    similarity_score = calculate_similarity_advanced(hpcp_query, hpcp_reference)
    print(f"    高度な類似度: {similarity_score:.4f}")
    return similarity_score >= threshold
