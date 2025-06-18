"""CASE03のe2eテスト実行スクリプト."""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.audio.hpcp import extract_hpcp, normalize_hpcp  # noqa: E402
from app.core.matching.similarity import is_same_recording_advanced  # noqa: E402


def run_case03_test() -> bool:
    """CASE03のテストを実行する.
    
    原曲とカラオケ録音の同一性判定テスト。
    音質の違いや歌声の違い、録音環境の違いがあっても
    同じ楽曲として正しく認識されることを確認する。

    Returns:
        すべてのテストがパスした場合True、それ以外はFalse
    """
    # テストデータのパス
    dataset_dir = Path(__file__).parent / "datasets"
    test_files = {
        "original": dataset_dir / "sayonara.wav",
        "karaoke": dataset_dir / "sayonara_record.wav",
    }

    # 期待される結果
    expected_results = [
        ("original", "karaoke", True),  # 原曲 vs カラオケ録音 → 同一
    ]

    print("CASE03: 原曲とカラオケ録音の同一性判定テスト")
    print("=" * 60)

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
    print("\n原曲とカラオケ録音の同一性判定テストを実行中...")
    all_passed = True
    results: list[tuple[str, str, bool, bool]] = []

    for file1_id, file2_id, expected in expected_results:
        print(f"\n  {file1_id} vs {file2_id}:")
        hpcp1 = hpcp_features[file1_id]
        hpcp2 = hpcp_features[file2_id]

        # 同一性判定（カラオケ録音用に閾値を調整）
        is_same = is_same_recording_advanced(hpcp1, hpcp2, threshold=0.85)

        # 結果を記録
        passed = is_same == expected
        results.append((file1_id, file2_id, is_same, passed))
        
        status = "✅ PASS" if passed else "❌ FAIL"
        result_str = "同一" if is_same else "異なる"
        expected_str = "同一" if expected else "異なる"
        print(f"    判定結果: {result_str} (期待値: {expected_str}) - {status}")

        if not passed:
            all_passed = False

    # 結果を表示
    print("\n【テスト結果】")
    print("-" * 70)
    print(f"{'リファレンス':^15} {'テスト対象':^15} {'判定':^10} {'期待値':^10} {'結果':^10}")
    print("-" * 70)

    for (file1_id, file2_id, expected), (_, _, is_same, passed) in zip(
        expected_results, results, strict=False
    ):
        file1_display = "原曲" if file1_id == "original" else "カラオケ"
        file2_display = "カラオケ録音" if file2_id == "karaoke" else "原曲"
        expected_str = "同一" if expected else "異なる"
        result_str = "同一" if is_same else "異なる"
        status = "✅ PASS" if passed else "❌ FAIL"
        print(
            f"{file1_display:^15} {file2_display:^15} {result_str:^10} "
            f"{expected_str:^10} {status:^10}"
        )

    print("-" * 70)
    
    # 統計情報
    total_tests = len(results)
    passed_tests = sum(1 for _, _, _, passed in results if passed)
    
    print(f"\n総テスト数: {total_tests}")
    print(f"合格: {passed_tests}")
    print(f"不合格: {total_tests - passed_tests}")
    print(f"合格率: {passed_tests/total_tests*100:.1f}%")
    
    print(
        "\n総合結果: "
        + (
            "✅ すべてのテストがパスしました"
            if all_passed
            else "❌ 一部のテストが失敗しました"
        )
    )

    if all_passed:
        print("\n🎉 音楽マッチングシステムは以下の能力を持つことが確認されました:")
        print("  • 録音品質の違いへの堅牢性")
        print("  • 歌声の違いへの対応")
        print("  • 録音環境の違いへの対応")
        print("  • カラオケアプリでの楽曲識別への対応")

    return all_passed


if __name__ == "__main__":
    success = run_case03_test()
    sys.exit(0 if success else 1)