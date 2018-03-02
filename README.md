# SamplingRateConversion
サンプリング周波数変換処理を行うプログラム

# Overview
サンプリング周波数変換（アップサンプリングとダウンサンプリング）処理をPythonで実装したものです．

また，Wavファイルのスペクトログラムを表示するプログラムも入っています．

サンプルとして，基本周波数1000Hzの矩形波（test.wav）とその結果（up.wav,down.wav）が入っています．

コード内に問題がある可能性があるので，もしお気づきになられたら修正 or 連絡をお願い致します．

# Usage
wavディレクトリ内に変換したいwavファイルを置いておく．

SamplingRateConversion.py内のFILENAMEを変換したいファイルのパスに置き換える．

「python SamplingRateConversion.py」を実行すると，wavディレクトリ内に結果が出力される．

PlotSpectrogram.pyの使い方は，プログラム内に記載しています．

# Requirement
Python 3.6.0

numpy 1.14.1

scipy 1.0.0

matplotlib 2.1.2


# License
Copyright © 2016 T_Sumida Distributed under the MIT License.
