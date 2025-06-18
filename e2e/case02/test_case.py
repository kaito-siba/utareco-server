"""CASE02のe2eテスト実行スクリプト."""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.audio.hpcp import extract_hpcp, normalize_hpcp  # noqa: E402
from app.core.matching.similarity import is_same_recording_advanced  # noqa: E402


def run_case02_test() -> bool:
    """CASE02のテストを実行する.

    Returns:
        すべてのテストがパスした場合True、それ以外はFalse
    """
    # テストデータのパス
    dataset_dir = Path(__file__).parent / "datasets"
    
    # リファレンス楽曲
    reference_files = {
        "Dramaturgy": dataset_dir / "Dramaturgy.wav",
        "Hanoboshi": dataset_dir / "Hanoboshi.wav", 
        "Heart Forecast": dataset_dir / "Heart Forecast.wav",
    }
    
    # 変更版楽曲
    modified_files = {
        "Dramaturgy": [
            dataset_dir / "Dramaturgy_tempo0.80x.wav",
            dataset_dir / "Dramaturgy_tempo0.90x.wav", 
            dataset_dir / "Dramaturgy_tempo1.10x.wav",
            dataset_dir / "Dramaturgy_pitch+1.0.wav",
            dataset_dir / "Dramaturgy_pitch+2.0.wav",
            dataset_dir / "Dramaturgy_pitch+3.0.wav",
        ],
        "Hanoboshi": [
            dataset_dir / "Hanoboshi_tempo0.80x.wav",
            dataset_dir / "Hanoboshi_tempo0.90x.wav",
            dataset_dir / "Hanoboshi_tempo1.10x.wav", 
            dataset_dir / "Hanoboshi_pitch+1.0.wav",
            dataset_dir / "Hanoboshi_pitch+2.0.wav",
            dataset_dir / "Hanoboshi_pitch+3.0.wav",
        ],
        "Heart Forecast": [
            dataset_dir / "Heart Forecast_tempo0.80x.wav",
            dataset_dir / "Heart Forecast_tempo0.90x.wav",
            dataset_dir / "Heart Forecast_tempo1.10x.wav",
            dataset_dir / "Heart Forecast_pitch+1.0.wav", 
            dataset_dir / "Heart Forecast_pitch+2.0.wav",
            dataset_dir / "Heart Forecast_pitch+3.0.wav",
        ],
    }

    # リファレンス楽曲のHPCP特徴を抽出
    print("リファレンス楽曲のHPCP特徴を抽出中...")
    reference_hpcp = {}
    for song_name, file_path in reference_files.items():
        try:
            print(f"  {file_path.name} を処理中...")
            hpcp = extract_hpcp(file_path)
            hpcp_normalized = normalize_hpcp(hpcp)
            reference_hpcp[song_name] = hpcp_normalized
            print(f"    完了: HPCP shape = {hpcp_normalized.shape}")
        except Exception as e:
            print(f"    エラー: {e}")
            return False

    # 変更版楽曲のHPCP特徴を抽出
    print("\n変更版楽曲のHPCP特徴を抽出中...")
    modified_hpcp = {}
    for song_name, file_paths in modified_files.items():
        modified_hpcp[song_name] = []
        for file_path in file_paths:
            try:
                print(f"  {file_path.name} を処理中...")
                hpcp = extract_hpcp(file_path)
                hpcp_normalized = normalize_hpcp(hpcp)
                modified_hpcp[song_name].append((file_path.name, hpcp_normalized))
                print(f"    完了: HPCP shape = {hpcp_normalized.shape}")
            except Exception as e:
                print(f"    エラー: {e}")
                return False

    # テストを実行
    print("\n同一性判定テストを実行中...")
    all_passed = True
    results = []

    # 1. 同一楽曲の判定テスト (18通り)
    print("\n=== 同一楽曲の判定テスト ===")
    for song_name in reference_files.keys():
        print(f"\n{song_name}の変更版テスト:")
        ref_hpcp = reference_hpcp[song_name]
        
        for mod_name, mod_hpcp in modified_hpcp[song_name]:
            print(f"  {song_name} vs {mod_name}:")
            
            # 同一性判定（閾値を調整）
            is_same = is_same_recording_advanced(ref_hpcp, mod_hpcp, threshold=0.89)
            expected = True  # 同一楽曲なので期待値はTrue
            passed = is_same == expected
            
            results.append((song_name, mod_name, is_same, expected, passed))
            
            if not passed:
                all_passed = False

    # 2. 異なる楽曲の判定テスト (36通り)
    print("\n=== 異なる楽曲の判定テスト ===")
    song_names = list(reference_files.keys())
    
    for i, song1 in enumerate(song_names):
        for j, song2 in enumerate(song_names):
            if i != j:  # 異なる楽曲の組み合わせ
                print(f"\n{song1} vs {song2}の変更版テスト:")
                ref_hpcp = reference_hpcp[song1]
                
                for mod_name, mod_hpcp in modified_hpcp[song2]:
                    print(f"  {song1} vs {mod_name}:")
                    
                    # 同一性判定
                    is_same = is_same_recording_advanced(ref_hpcp, mod_hpcp, threshold=0.89)
                    expected = False  # 異なる楽曲なので期待値はFalse
                    passed = is_same == expected
                    
                    results.append((song1, mod_name, is_same, expected, passed))
                    
                    if not passed:
                        all_passed = False

    # 結果を表示
    print("\n【テスト結果】")
    print("-" * 80)
    print(f"{'リファレンス':^15} {'テスト対象':^25} {'判定':^10} {'期待値':^10} {'結果':^10}")
    print("-" * 80)

    for ref_name, test_name, is_same, expected, passed in results:
        result_str = "同一" if is_same else "異なる"
        expected_str = "同一" if expected else "異なる"
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{ref_name:^15} {test_name:^25} {result_str:^10} {expected_str:^10} {status:^10}")

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
    success = run_case02_test()
    sys.exit(0 if success else 1)