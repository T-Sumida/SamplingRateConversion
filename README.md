# SamplingRateConversion
サンプリング周波数変換処理を行うプログラム

# Overview
サンプリング周波数変換（アップサンプリングとダウンサンプリング）処理をPythonで実装したものです．

また，Wavファイルのスペクトログラムを表示するプログラムも入っています．

サンプルとして，基本周波数1000Hzの矩形波（test.wav）とその結果（test_up.wav, test_down.wav）が入っています．

コード内に問題がある可能性があるので，もしお気づきになられたら修正 or 連絡をお願い致します．

# Usage
- 環境構築
  ```
  $pip install -r requirements.txt
  ```
- サンプリング周波数変換実行
  ```
  $python sr_converter.py {input file path} {output dir path} --up {up sampling conversion} --down {down conversion rate}

  # 例
  $python sr_converter.py ./wav/test.wav ./wav --up 4 --down 4
  ```
- 可視化
  ```
  $python visualizer.py {input wav file path} -o {output file path} -N {FFT window}

  # 例
  $python visuazlier.py ./wav/test_up.wav -o ./result_png/up.png -N 512
  ```


# License
Copyright © 2020 T_Sumida Distributed under the MIT License.
