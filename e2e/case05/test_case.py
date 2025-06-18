"""CASE05のe2eテスト実行スクリプト."""

import sys
from itertools import combinations
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.audio.hpcp import extract_hpcp, normalize_hpcp  # noqa: E402
from app.core.matching.similarity import (  # noqa: E402
    is_same_recording_advanced,
)


def run_case05_test() -> bool:
    """CASE05のテストを実行する.

    カラオケ音源とピッチ変更されたカラオケ音源での重複無し総当たり組み合わせテスト

    Returns:
        すべてのテストがパスした場合True、それ以外はFalse
    """
    # テストデータのパス
    dataset_dir = Path(__file__).parent / "datasets"

    # テストファイル（カラオケ音源 + ピッチ変更）
    test_files = {
        "eine_kleine": dataset_dir / "Eine_Kleine_karaoke.wav",
        "eine_kleine_pitch": dataset_dir
        / "Eine_Kleine_karaoke_pitch_minus_2.wav",  # noqa: E501
        "sayonara": dataset_dir / "sayonara_karaoke.wav",
    }

    # 期待される結果の定義
    # 同一楽曲のペアは True、異なる楽曲のペアは False
    expected_same_pairs = {
        ("eine_kleine", "eine_kleine_pitch"),  # 同一楽曲の異なるピッチバージョン
    }

    # 各ファイルのHPCP特徴を抽出
    print("HPCP特徴を抽出中...")
    hpcp_features = {}
    for file_id, file_path in test_files.items():
        try:
            print(f"  {file_path.name} を処理中...")
            hpcp = extract_hpcp(file_path)
            hpcp_normalized = normalize_hpcp(hpcp)
            hpcp_features[file_id] = hpcp_normalized
            print(f"    完了: HPCP shape = {hpcp_normalized.shape}")
        except Exception as e:
            print(f"    エラー: {e}")
            return False

    # 重複無しの総当たり組み合わせを生成
    file_ids = list(test_files.keys())
    test_combinations = list(combinations(file_ids, 2))

    print(f"\n同一性判定テストを実行中... ({len(test_combinations)}組の組み合わせ)")
    all_passed = True
    results = []

    for file1_id, file2_id in test_combinations:
        print(f"\n  {file1_id} vs {file2_id}:")
        hpcp1 = hpcp_features[file1_id]
        hpcp2 = hpcp_features[file2_id]

        # 期待される結果を取得
        expected = (file1_id, file2_id) in expected_same_pairs or (
            file2_id,
            file1_id,
        ) in expected_same_pairs

        # 同一性判定（ピッチ変化に対応するため閾値を調整）
        is_same = is_same_recording_advanced(hpcp1, hpcp2, threshold=0.85)

        # 結果を記録
        passed = is_same == expected
        results.append((file1_id, file2_id, is_same, expected, passed))

        result_str = "同一" if is_same else "異なる"
        expected_str = "同一" if expected else "異なる"
        status = "✅ PASS" if passed else "❌ FAIL"

        print(f"    判定: {result_str} (期待値: {expected_str}) {status}")

        if not passed:
            all_passed = False

    # 結果を表示
    print("\n【テスト結果】")
    print("-" * 80)
    print(
        f"{'テスト対象1':^20} {'テスト対象2':^20} {'判定':^10} "
        f"{'期待値':^10} {'結果':^10}"
    )
    print("-" * 80)

    for file1_id, file2_id, is_same, expected, passed in results:
        result_str = "同一" if is_same else "異なる"
        expected_str = "同一" if expected else "異なる"
        status = "✅ PASS" if passed else "❌ FAIL"
        print(
            f"{file1_id:^20} {file2_id:^20} {result_str:^10} "
            f"{expected_str:^10} {status:^10}"
        )

    print("-" * 80)

    # 統計を表示
    total_tests = len(results)
    passed_tests = sum(1 for _, _, _, _, passed in results if passed)
    failed_tests = total_tests - passed_tests

    print(f"\n総テスト数: {total_tests}")
    print(f"合格: {passed_tests}")
    print(f"不合格: {failed_tests}")
    print(f"合格率: {passed_tests/total_tests*100:.1f}%")

    # 詳細分析を表示
    print("\n【詳細分析】")
    same_song_tests = [r for r in results if r[3] is True]  # 期待値がTrue（同一楽曲）
    different_song_tests = [
        r for r in results if r[3] is False  # 期待値がFalse（異なる楽曲）
    ]

    if same_song_tests:
        same_passed = sum(1 for r in same_song_tests if r[4])
        print(
            f"同一楽曲判定（ピッチ違い）: {same_passed}/{len(same_song_tests)} "
            f"({same_passed/len(same_song_tests)*100:.1f}%)"
        )

    if different_song_tests:
        diff_passed = sum(1 for r in different_song_tests if r[4])
        print(
            f"異なる楽曲判定: {diff_passed}/{len(different_song_tests)} "
            f"({diff_passed/len(different_song_tests)*100:.1f}%)"
        )

    print(
        "\n総合結果: "
        + (
            "✅ すべてのテストがパスしました"
            if all_passed
            else "❌ 一部のテストが失敗しました"
        )
    )

    return all_passed


if __name__ == "__main__":
    success = run_case05_test()
    sys.exit(0 if success else 1)
