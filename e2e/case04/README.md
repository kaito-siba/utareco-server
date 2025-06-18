# CASE04: カラオケ音源総当たりテスト

## 概要

すべてカラオケ音源を使用し、重複無しの総当たり組み合わせで同一楽曲判定の精度をテストします。

## テストデータ

- `Eine_Kleine_karaoke_1.wav`: アイネクライネ（カラオケ録音 1）
- `Eine_Kleine_karaoke_2.wav`: アイネクライネ（カラオケ録音 2）
- `sayonara_karaoke.wav`: さよなら（カラオケ録音）

## テスト内容

### 組み合わせ

3 つのファイルから重複無しの総当たり組み合わせを生成：

1. `eine_kleine_1` vs `eine_kleine_2`（同一楽曲）
2. `eine_kleine_1` vs `sayonara`（異なる楽曲）
3. `eine_kleine_2` vs `sayonara`（異なる楽曲）

### 期待される結果

- **同一楽曲**: `eine_kleine_1` vs `eine_kleine_2` → `True`
- **異なる楽曲**: その他すべての組み合わせ → `False`

## 実行方法

```bash
cd e2e/case04
python test_case.py
```

## 判定基準

- 閾値: 0.85（カラオケ録音用に調整）
- アルゴリズム: `is_same_recording_advanced`

## 期待される成果

- すべてのカラオケ音源で正確な同一楽曲判定が行えること
- 同一楽曲の異なるカラオケ録音を正しく識別できること
- 異なる楽曲のカラオケ録音を正しく区別できること
