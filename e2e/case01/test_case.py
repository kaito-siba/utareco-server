"""CASE01のe2eテスト実行スクリプト."""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.audio.hpcp import extract_hpcp, normalize_hpcp  # noqa: E402
from app.core.matching.similarity import is_same_recording_advanced  # noqa: E402


def run_case01_test() -> bool:
    """CASE01のテストを実行する.

    Returns:
        すべてのテストがパスした場合True、それ以外はFalse
    """
    # テストデータのパス
    dataset_dir = Path(__file__).parent / "datasets"
    test_files = {
        "1": dataset_dir / "Dramaturgy.m4a",
        "2": dataset_dir / "Hanoboshi.m4a",
        "3": dataset_dir / "Heart Forecast.m4a",
    }

    # 期待される結果
    expected_results = [
        ("1", "1", True),  # 同一
        ("2", "2", True),  # 同一
        ("3", "3", True),  # 同一
        ("1", "2", False),  # 異なる
        ("2", "3", False),  # 異なる
        ("3", "1", False),  # 異なる
    ]

    # 各ファイルのHPCP特徴を抽出
    print("HPCP特徴を抽出中...")
    hpcp_features: dict[str, any] = {}
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
    results: list[tuple[str, str, bool, bool]] = []

    for file1_id, file2_id, expected in expected_results:
        print(f"\n  File{file1_id} vs File{file2_id}:")
        hpcp1 = hpcp_features[file1_id]
        hpcp2 = hpcp_features[file2_id]

        # 同一性判定（高度な特徴版）
        is_same = is_same_recording_advanced(hpcp1, hpcp2, threshold=0.95)

        # 結果を記録
        passed = is_same == expected
        results.append((file1_id, file2_id, is_same, passed))

        if not passed:
            all_passed = False

    # 結果を表示
    print("\n【テスト結果】")
    print("-" * 60)
    print(f"{'File1':^10} {'File2':^10} {'判定':^10} {'期待値':^10} {'結果':^10}")
    print("-" * 60)

    for (file1_id, file2_id, expected), (_, _, is_same, passed) in zip(
        expected_results, results, strict=False
    ):
        expected_str = "同一" if expected else "異なる"
        result_str = "同一" if is_same else "異なる"
        status = "✅ PASS" if passed else "❌ FAIL"
        print(
            f"{file1_id:^10} {file2_id:^10} {result_str:^10} "
            f"{expected_str:^10} {status:^10}"
        )

    print("-" * 60)
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
    success = run_case01_test()
    sys.exit(0 if success else 1)
