"""CASE03のe2eテスト実行スクリプト."""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.audio.hpcp import extract_hpcp, normalize_hpcp  # noqa: E402
from app.core.matching.similarity import (  # noqa: E402
    is_same_recording_advanced,
)


def run_case03_test() -> bool:
    """CASE03のテストを実行する.

    Returns:
        すべてのテストがパスした場合True、それ以外はFalse
    """
    # テストデータのパス
    dataset_dir = Path(__file__).parent / "datasets"

    # テストファイル
    test_files = {
        "sayonara_original": dataset_dir / "sayonara.wav",
        "sayonara_karaoke": dataset_dir / "sayonara_record.wav",
        "dramaturgy": dataset_dir / "Dramaturgy.wav",
    }

    # 期待される結果
    expected_results = [
        ("sayonara_original", "sayonara_karaoke", True),  # 同一楽曲
        ("sayonara_karaoke", "dramaturgy", False),  # 異なる楽曲
        ("dramaturgy", "sayonara_karaoke", False),  # 異なる楽曲
    ]

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

    # テストを実行
    print("\n同一性判定テストを実行中...")
    all_passed = True
    results = []

    for file1_id, file2_id, expected in expected_results:
        print(f"\n  {file1_id} vs {file2_id}:")
        hpcp1 = hpcp_features[file1_id]
        hpcp2 = hpcp_features[file2_id]

        # 同一性判定（カラオケ録音用に閾値を調整）
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
        f"{'テスト対象1':^20} {'テスト対象2':^20} {'判定':^10} {'期待値':^10} {'結果':^10}"
    )
    print("-" * 80)

    for file1_id, file2_id, is_same, expected, passed in results:
        result_str = "同一" if is_same else "異なる"
        expected_str = "同一" if expected else "異なる"
        status = "✅ PASS" if passed else "❌ FAIL"
        print(
            f"{file1_id:^20} {file2_id:^20} {result_str:^10} {expected_str:^10} {status:^10}"
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
    success = run_case03_test()
    sys.exit(0 if success else 1)
