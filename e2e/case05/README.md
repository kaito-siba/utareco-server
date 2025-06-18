# CASE05: カラオケ音源ピッチ変化テスト

## 概要

カラオケ音源とピッチ変更されたカラオケ音源を使用し、重複無しの総当たり組み合わせで同一楽曲判定の精度をテストします。

## テストデータ

- `Eine_Kleine_karaoke.wav`: アイネクライネ（カラオケ録音）
- `Eine_Kleine_karaoke_pitch_minus_2.wav`: アイネクライネ（カラオケ録音、ピッチ-2 半音）
- `sayonara_karaoke.wav`: さよなら（カラオケ録音）

## テスト内容

### 組み合わせ

3 つのファイルから重複無しの総当たり組み合わせを生成：

1. `eine_kleine` vs `eine_kleine_pitch`（同一楽曲、ピッチ違い）
2. `eine_kleine` vs `sayonara`（異なる楽曲）
3. `eine_kleine_pitch` vs `sayonara`（異なる楽曲）

### 期待される結果

- **同一楽曲**: `eine_kleine` vs `eine_kleine_pitch` → `True`
- **異なる楽曲**: その他すべての組み合わせ → `False`

## 実行方法

```bash
cd e2e/case05
python test_case.py
```

## 判定基準

- 閾値: 0.80（ピッチ変化に対応するため少し低めに調整）
- アルゴリズム: `is_same_recording_advanced`

## 期待される成果

- ピッチが変更されたカラオケ音源でも正確な同一楽曲判定が行えること
- 同一楽曲の異なるピッチバージョンを正しく識別できること
- 異なる楽曲のカラオケ録音を正しく区別できること
