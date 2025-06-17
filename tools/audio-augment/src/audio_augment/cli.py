"""コマンドラインインターフェース"""

from pathlib import Path
from typing import List, Optional, Tuple

import click

from .processor import process_audio_file


@click.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.argument("output_file", type=click.Path(path_type=Path))
@click.option(
    "-p",
    "--pitch",
    type=float,
    help="ピッチシフト量（半音単位）。正の値で高く、負の値で低くなる",
)
@click.option(
    "-t",
    "--tempo",
    type=float,
    help="テンポ変更率。1.0が元のテンポ、2.0で2倍速、0.5で半分",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="詳細な出力を表示",
)
def augment(
    input_file: Path,
    output_file: Path,
    pitch: Optional[float],
    tempo: Optional[float],
    verbose: bool,
) -> None:
    """音声ファイルのキー・テンポを変更する

    INPUT_FILE: 入力音声ファイル（WAV, FLAC, MP3など）
    OUTPUT_FILE: 出力音声ファイル

    Examples:
        # 3半音上げる
        audio-augment input.wav output.wav -p 3

        # テンポを0.8倍（遅く）にする
        audio-augment input.wav output.wav -t 0.8

        # 2半音下げて、1.2倍速にする
        audio-augment input.wav output.wav -p -2 -t 1.2
    """
    if pitch is None and tempo is None:
        click.echo(
            "エラー: ピッチまたはテンポの少なくとも一方を指定してください", err=True
        )
        click.echo("使用方法: audio-augment --help", err=True)
        raise click.Abort()

    if verbose:
        click.echo(f"入力ファイル: {input_file}")
        click.echo(f"出力ファイル: {output_file}")
        if pitch is not None:
            click.echo(f"ピッチシフト: {pitch:+.1f} 半音")
        if tempo is not None:
            click.echo(f"テンポ変更率: {tempo:.2f}x")

    try:
        process_audio_file(
            input_file,
            output_file,
            pitch_shift_semitones=pitch,
            tempo_rate=tempo,
        )
        click.echo(f"✅ 処理完了: {output_file}")
    except Exception as e:
        click.echo(f"❌ エラー: {e}", err=True)
        raise click.Abort()


@click.group()
def cli():
    """音声ファイル増強ツール"""
    pass


@cli.command()
@click.argument(
    "input_dir", type=click.Path(exists=True, file_okay=False, path_type=Path)
)
@click.argument("output_dir", type=click.Path(file_okay=False, path_type=Path))
@click.option(
    "-p",
    "--pitch-range",
    nargs=2,
    type=float,
    default=(-3, 3),
    help="ピッチシフトの範囲（最小, 最大）デフォルト: -3 3",
)
@click.option(
    "-t",
    "--tempo-range",
    nargs=2,
    type=float,
    default=(0.8, 1.2),
    help="テンポ変更率の範囲（最小, 最大）デフォルト: 0.8 1.2",
)
@click.option(
    "-s",
    "--step",
    type=float,
    default=1.0,
    help="ピッチシフトのステップ（半音単位）デフォルト: 1.0",
)
@click.option(
    "--tempo-step",
    type=float,
    default=0.1,
    help="テンポ変更率のステップ デフォルト: 0.1",
)
@click.option(
    "-e",
    "--extensions",
    multiple=True,
    default=["wav", "mp3", "flac"],
    help="処理する音声ファイルの拡張子",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="詳細な出力を表示",
)
def batch(
    input_dir: Path,
    output_dir: Path,
    pitch_range: Tuple[float, float],
    tempo_range: Tuple[float, float],
    step: float,
    tempo_step: float,
    extensions: Tuple[str, ...],
    verbose: bool,
) -> None:
    """ディレクトリ内の音声ファイルをバッチ処理

    INPUT_DIR: 入力ディレクトリ
    OUTPUT_DIR: 出力ディレクトリ

    Examples:
        # デフォルト設定でバッチ処理
        audio-augment batch input_dir output_dir

        # ピッチを-5から5半音、1半音刻みで変更
        audio-augment batch input_dir output_dir -p -5 5 -s 1

        # テンポを0.5から2.0倍、0.25刻みで変更
        audio-augment batch input_dir output_dir -t 0.5 2.0 --tempo-step 0.25
    """
    # 入力ファイルを収集
    input_files: List[Path] = []
    for ext in extensions:
        input_files.extend(input_dir.glob(f"**/*.{ext}"))

    if not input_files:
        click.echo(f"警告: {input_dir} に音声ファイルが見つかりません", err=True)
        return

    click.echo(f"見つかったファイル数: {len(input_files)}")

    # 出力ディレクトリを作成
    output_dir.mkdir(parents=True, exist_ok=True)

    # ピッチシフトの値を生成
    pitch_min, pitch_max = pitch_range
    pitch_values = []
    current_pitch = pitch_min
    while current_pitch <= pitch_max:
        if current_pitch != 0:  # 0は変更なしなのでスキップ
            pitch_values.append(current_pitch)
        current_pitch += step

    # テンポ変更率の値を生成
    tempo_min, tempo_max = tempo_range
    tempo_values = []
    current_tempo = tempo_min
    while current_tempo <= tempo_max:
        if abs(current_tempo - 1.0) > 0.01:  # 1.0は変更なしなのでスキップ
            tempo_values.append(current_tempo)
        current_tempo += tempo_step

    total_variations = len(pitch_values) + len(tempo_values)
    click.echo(
        f"生成される変種数: {total_variations} "
        f"(ピッチ: {len(pitch_values)}, テンポ: {len(tempo_values)})"
    )

    processed = 0
    errors = 0

    with click.progressbar(input_files, label="処理中") as files:
        for input_file in files:
            # 相対パスを保持
            relative_path = input_file.relative_to(input_dir)
            base_name = relative_path.stem
            suffix = relative_path.suffix

            # ピッチシフトのバリエーション
            for pitch in pitch_values:
                output_name = f"{base_name}_pitch{pitch:+.1f}{suffix}"
                output_path = output_dir / relative_path.parent / output_name

                try:
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    process_audio_file(
                        input_file,
                        output_path,
                        pitch_shift_semitones=pitch,
                    )
                    processed += 1
                    if verbose:
                        click.echo(f"\n✅ {input_file.name} → {output_name}")
                except Exception as e:
                    errors += 1
                    if verbose:
                        click.echo(f"\n❌ {input_file.name}: {e}")

            # テンポ変更のバリエーション
            for tempo in tempo_values:
                output_name = f"{base_name}_tempo{tempo:.2f}x{suffix}"
                output_path = output_dir / relative_path.parent / output_name

                try:
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    process_audio_file(
                        input_file,
                        output_path,
                        tempo_rate=tempo,
                    )
                    processed += 1
                    if verbose:
                        click.echo(f"\n✅ {input_file.name} → {output_name}")
                except Exception as e:
                    errors += 1
                    if verbose:
                        click.echo(f"\n❌ {input_file.name}: {e}")

    click.echo(f"\n処理完了: 成功 {processed} / エラー {errors}")


if __name__ == "__main__":
    cli()
