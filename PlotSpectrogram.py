# -*- coding:utf-8 -*-
"""
実行時の引数にプロットしたいファイルのパスを与えてやる．
そのwavファイルのスペクトログラムを表示する．
（例）
python PlotSpectrogram.py [wav file path]
"""
import matplotlib.pyplot as plt
import numpy as np
import SamplingRateConversion
import sys

N = 256         # スペクトログラム生成時の窓幅
OVERLAP = 0    # スペクトログラム生成時の移動窓幅

def plot(data,fs):
    """
    指定されたデータとサンプリング周波数でスペクトログラムを作成し，表示する関数．
    """
    pxx, freqs, bins, im = plt.specgram(data, NFFT=N, Fs=fs, noverlap=OVERLAP, window=np.hamming(N),cmap='jet')
    plt.ylabel("Frequency [Hz]")
    plt.xlabel("Tiem [sec]")
    plt.show()


if __name__ == "__main__":
    args = sys.argv
    if len(args) != 2:
        print("引数にプロットするwavファイルのパスを指定してください")
        sys.exit()

    data,fs = SamplingRateConversion.readWav(args[1])
    plot(data,fs)
