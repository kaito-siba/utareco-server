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
    # 1. グローバル特徴（平均HPCP）- より厳密な比較
    mean_query = np.mean(hpcp_query, axis=0)
    mean_reference = np.mean(hpcp_reference, axis=0)

    # 正規化
    mean_query = mean_query / (np.linalg.norm(mean_query) + 1e-6)
    mean_reference = mean_reference / (np.linalg.norm(mean_reference) + 1e-6)

    # 最適な転調を見つける（より厳密）
    global_similarities = []
    for shift in range(12):
        shifted_query = np.roll(mean_query, shift)
        # コサイン類似度に加えてユークリッド距離も考慮
        cosine_sim = np.dot(shifted_query, mean_reference)
        euclidean_dist = np.linalg.norm(shifted_query - mean_reference)
        # 距離を類似度に変換（0-1範囲）
        distance_sim = 1.0 / (1.0 + euclidean_dist)
        # 調和平均で組み合わせ
        combined_sim = 2 * cosine_sim * distance_sim / (cosine_sim + distance_sim + 1e-6)
        global_similarities.append(combined_sim)

    best_shift = np.argmax(global_similarities)
    global_similarity = global_similarities[best_shift]

    # 2. ヒストグラム特徴（より識別力の高い計算）
    hist_query = calculate_hpcp_histogram(hpcp_query, bins=32)  # ビン数を増やして精度向上
    hist_reference = calculate_hpcp_histogram(hpcp_reference, bins=32)

    # Earth Mover's Distance（EMD）風の計算
    hist_similarity = 1.0 - np.sum(np.abs(hist_query - hist_reference)) / 2
    
    # カイ二乗距離も計算
    chi2_distance = np.sum((hist_query - hist_reference) ** 2 / (hist_query + hist_reference + 1e-6))
    chi2_similarity = 1.0 / (1.0 + chi2_distance)
    
    # ヒストグラム類似度を改善
    hist_similarity = (hist_similarity + chi2_similarity) / 2

    # 3. 時系列特徴（最適転調でシフト）
    shifted_hpcp_query = np.roll(hpcp_query, best_shift, axis=1)
    temporal_query = calculate_temporal_features(shifted_hpcp_query)
    temporal_reference = calculate_temporal_features(hpcp_reference)

    # 正規化
    temporal_query = temporal_query / (np.linalg.norm(temporal_query) + 1e-6)
    temporal_reference = temporal_reference / (
        np.linalg.norm(temporal_reference) + 1e-6
    )

    # より厳密な時系列類似度計算
    temporal_cosine = np.dot(temporal_query, temporal_reference)
    temporal_euclidean_dist = np.linalg.norm(temporal_query - temporal_reference)
    temporal_distance_sim = 1.0 / (1.0 + temporal_euclidean_dist)
    temporal_similarity = (temporal_cosine + temporal_distance_sim) / 2

    # 4. 長さ比率による補正（テンポ変化対応）
    length_ratio = min(len(hpcp_query), len(hpcp_reference)) / max(len(hpcp_query), len(hpcp_reference))
    # テンポ変化が0.8倍～1.25倍の範囲内なら補正を適用
    if length_ratio > 0.64:  # 0.8^2 = 0.64 (テンポ変化による長さ変化の二乗)
        length_penalty = 1.0
    else:
        length_penalty = 0.95  # 長さ差が大きい場合は少し減点

    # 重み付け平均（時系列特徴の重みを上げる）
    weights = [0.25, 0.25, 0.5]  # global, histogram, temporal
    final_similarity = (
        weights[0] * global_similarity
        + weights[1] * hist_similarity
        + weights[2] * temporal_similarity
    ) * length_penalty

    return float(final_similarity)


def is_same_recording_advanced(
    hpcp_query: np.ndarray,
    hpcp_reference: np.ndarray,
    threshold: float = 0.89,
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
