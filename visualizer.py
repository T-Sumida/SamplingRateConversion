# -*- coding:utf-8 -*-
import argparse

import matplotlib.pyplot as plt
import numpy as np

from sr_converter import read_wav


def get_args() -> argparse.Namespace:
    """引数取得

    Returns:
        argparse.Namespace: 引数情報
    """
    parser = argparse.ArgumentParser(
        prog="visualizer.py", usage="visualize spectrogram",
        add_help=True
    )
    parser.add_argument("input", type=str, help="input wav file path")
    parser.add_argument("-o", type=str, default=None, help="output file path")
    parser.add_argument("-N", type=int, default=256, help="fft window size")
    return parser.parse_args()


def visualize(data: np.array, fs: int, output_path: str, n_fft: int):
    """指定されたデータとサンプリング周波数でスペクトログラムを作成・表示する
    Args:
        data (np.array): 信号データ
        fs (int): サンプリングレート
        output_path (str): 出力ファイルパス
        n_fft (int): FFT窓幅
    """
    pxx, freqs, bins, im = plt.specgram(
        data, NFFT=n_fft, Fs=fs,
        noverlap=n_fft//2, window=np.hamming(n_fft), cmap='jet'
    )
    plt.ylabel("Frequency [Hz]")
    plt.xlabel("Tiem [sec]")

    if output_path is not None:
        plt.savefig(output_path)

    plt.show()


if __name__ == "__main__":
    args = get_args()

    data, fs = read_wav(args.input)

    visualize(data, fs, args.o, args.N)
