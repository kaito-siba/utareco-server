## テストケース 02

## 概要

同一楽曲のテンポ・ピッチ変更版を用いた同一性判定のテストです。
原曲をリファレンスとして、変更版との比較で楽曲の同一性を判定します。
楽曲の演奏速度やピッチが変更されても同じ楽曲として正しく認識され、
かつ異なる楽曲の変更版とは区別されることを確認します。

## 使用するデータ

### リファレンス楽曲（原曲）

1. Dramaturgy.wav
2. Hanoboshi.wav
3. Heart Forecast.wav

### テンポ変更版

- Dramaturgy_tempo0.80x.wav (80%速度)
- Dramaturgy_tempo0.90x.wav (90%速度)
- Dramaturgy_tempo1.10x.wav (110%速度)
- Hanoboshi_tempo0.80x.wav (80%速度)
- Hanoboshi_tempo0.90x.wav (90%速度)
- Hanoboshi_tempo1.10x.wav (110%速度)
- Heart Forecast_tempo0.80x.wav (80%速度)
- Heart Forecast_tempo0.90x.wav (90%速度)
- Heart Forecast_tempo1.10x.wav (110%速度)

### ピッチ変更版

- Dramaturgy_pitch+1.0.wav (+1 半音)
- Dramaturgy_pitch+2.0.wav (+2 半音)
- Dramaturgy_pitch+3.0.wav (+3 半音)
- Hanoboshi_pitch+1.0.wav (+1 半音)
- Hanoboshi_pitch+2.0.wav (+2 半音)
- Hanoboshi_pitch+3.0.wav (+3 半音)
- Heart Forecast_pitch+1.0.wav (+1 半音)
- Heart Forecast_pitch+2.0.wav (+2 半音)
- Heart Forecast_pitch+3.0.wav (+3 半音)

## テスト内容

リファレンス楽曲と変更版の比較による同一性判定テスト (全 54 通り) を実行します。

### 同一楽曲の判定テスト (18 通り)

各リファレンス楽曲と、その楽曲の変更版が「同一」と判定されることを確認：

**Dramaturgy.wav vs Dramaturgy 変更版 (6 通り)**

- Dramaturgy.wav vs Dramaturgy_tempo0.80x.wav → 同一
- Dramaturgy.wav vs Dramaturgy_tempo0.90x.wav → 同一
- Dramaturgy.wav vs Dramaturgy_tempo1.10x.wav → 同一
- Dramaturgy.wav vs Dramaturgy_pitch+1.0.wav → 同一
- Dramaturgy.wav vs Dramaturgy_pitch+2.0.wav → 同一
- Dramaturgy.wav vs Dramaturgy_pitch+3.0.wav → 同一

**Hanoboshi.wav vs Hanoboshi 変更版 (6 通り)**

- Hanoboshi.wav vs Hanoboshi_tempo0.80x.wav → 同一
- Hanoboshi.wav vs Hanoboshi_tempo0.90x.wav → 同一
- Hanoboshi.wav vs Hanoboshi_tempo1.10x.wav → 同一
- Hanoboshi.wav vs Hanoboshi_pitch+1.0.wav → 同一
- Hanoboshi.wav vs Hanoboshi_pitch+2.0.wav → 同一
- Hanoboshi.wav vs Hanoboshi_pitch+3.0.wav → 同一

**Heart Forecast.wav vs Heart Forecast 変更版 (6 通り)**

- Heart Forecast.wav vs Heart Forecast_tempo0.80x.wav → 同一
- Heart Forecast.wav vs Heart Forecast_tempo0.90x.wav → 同一
- Heart Forecast.wav vs Heart Forecast_tempo1.10x.wav → 同一
- Heart Forecast.wav vs Heart Forecast_pitch+1.0.wav → 同一
- Heart Forecast.wav vs Heart Forecast_pitch+2.0.wav → 同一
- Heart Forecast.wav vs Heart Forecast_pitch+3.0.wav → 同一

### 異なる楽曲の判定テスト (36 通り)

リファレンス楽曲と、異なる楽曲の変更版が「異なる」と判定されることを確認：

**Dramaturgy.wav vs 他楽曲の変更版 (12 通り)**

- Dramaturgy.wav vs Hanoboshi の 6 つの変更版 → 全て異なる
- Dramaturgy.wav vs Heart Forecast の 6 つの変更版 → 全て異なる

**Hanoboshi.wav vs 他楽曲の変更版 (12 通り)**

- Hanoboshi.wav vs Dramaturgy の 6 つの変更版 → 全て異なる
- Hanoboshi.wav vs Heart Forecast の 6 つの変更版 → 全て異なる

**Heart Forecast.wav vs 他楽曲の変更版 (12 通り)**

- Heart Forecast.wav vs Dramaturgy の 6 つの変更版 → 全て異なる
- Heart Forecast.wav vs Hanoboshi の 6 つの変更版 → 全て異なる
