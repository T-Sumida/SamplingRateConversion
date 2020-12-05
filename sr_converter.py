# -*- coding:utf-8 -*-
import os
import wave
import struct
import argparse
from typing import Tuple

import numpy as np
import scipy.signal


def get_args() -> argparse.Namespace:
    """引数取得

    Returns:
        argparse.Namespace: 引数情報
    """
    parser = argparse.ArgumentParser(
        prog="sr_converter.py", usage="convert samplingrate",
        add_help=True
    )
    parser.add_argument("input", type=str, help="input wav file path")
    parser.add_argument("output_dir", type=str, help="output dir path")
    parser.add_argument(
        "--up", type=int, default=None, help="up conversion rate: int"
    )
    parser.add_argument(
        "--down", type=int, default=None, help="down conversion rate: int"
    )
    return parser.parse_args()


def read_wav(filename: str) -> Tuple[np.array, int]:
    """wavファイルを読み込んで，データ・サンプリングレートを返す関数

    Args:
        filename (str): wavファイルパス

    Returns:
        Tuple[np.array, int]: (信号データ, サンプリングレート)
    """
    try:
        wf = wave.open(filename)
        fs = wf.getframerate()
        # -1 ~ 1までに正規化した信号データを読み込む
        data = np.frombuffer(wf.readframes(wf.getnframes()), dtype="int16") / 32768.0
        return (data, fs)
    except Exception as e:
        print(e)
        exit()


def write_wav(filename: str, data: np.array, fs: int) -> None:
    """入力されたファイル名でwavファイルを書き出す．

    Args:
        filename (str): 出力ファイルパス
        data (np.array): 信号データ
        fs (int): サンプリングレート
    """
    # データを-32768から32767の整数値に変換
    data = [int(x * 32767.0) for x in data]
    # バイナリ化
    binwave = struct.pack("h" * len(data), *data)
    wf = wave.Wave_write(filename)
    params = (
        1,                          # channel
        2,                          # byte width
        fs,                         # sampling rate
        len(data),                  # number of frames
        "NONE", "not compressed"    # no compression
    )
    wf.setparams(params)
    wf.writeframes(binwave)
    wf.close()


def upsampling(conversion_rate: int, data: np.array, fs: int) -> Tuple[np.array, int]:
    """アップサンプリングを行う．
       入力として，変換レートとデータとサンプリング周波数．
       アップサンプリング後のデータとサンプリング周波数を返す．

    Args:
        conversion_rate (int): 変換レート
        data (np.array): 信号データ
        fs (int): サンプリングレート

    Returns:
        Tuple[np.array, int]: 変換後の信号データとサンプリングレート
    """
    # 補間するサンプル数を決める
    interpolation_sample_num = conversion_rate-1

    # FIRフィルタの用意をする
    nyqF = (fs*conversion_rate)/2.0     # 変換後のナイキスト周波数
    cF = (fs/2.0-500.)/nyqF             # カットオフ周波数を設定（変換前のナイキスト周波数より少し下を設定）
    taps = 511                          # フィルタ係数（奇数じゃないとだめ）
    b = scipy.signal.firwin(taps, cF)   # LPFを用意

    # 補間処理
    up_data = []
    for d in data:
        up_data.append(d)
        # 1サンプルの後に，interpolation_sample_num分だけ0を追加する
        for i in range(interpolation_sample_num):
            up_data.append(0.0)

    # フィルタリング
    result_data = scipy.signal.lfilter(b, 1, up_data)
    return (result_data, int(fs*conversion_rate))


def downsampling(conversion_rate: int, data: np.array, fs: int) -> Tuple[np.array, int]:
    """ダウンサンプリングを行う．
    入力として，変換レートとデータとサンプリング周波数．
    アップサンプリング後のデータとサンプリング周波数を返す．

    Args:
        conversion_rate (int): 変換レート
        data (np.array): 信号データ
        fs (int): サンプリングレート

    Returns:
        Tuple[np.array, int]: 変換後の信号データとサンプリングレート
    """
    # 間引くサンプル数を決める
    decimation_sampleNum = conversion_rate-1

    # FIRフィルタの用意をする
    nyqF = (fs/conversion_rate)/2.0             # 変換後のナイキスト周波数
    cF = (fs/conversion_rate/2.0-500.)/nyqF     # カットオフ周波数を設定（変換前のナイキスト周波数より少し下を設定）
    taps = 511                                  # フィルタ係数（奇数じゃないとだめ）
    b = scipy.signal.firwin(taps, cF)           # LPFを用意

    # フィルタリング
    data = scipy.signal.lfilter(b, 1, data)

    # 間引き処理
    down_data = []
    for i in range(0, len(data), decimation_sampleNum+1):
        down_data.append(data[i])

    return (down_data, int(fs/conversion_rate))


if __name__ == "__main__":
    args = get_args()

    # テストwavファイルを読み込む
    data, fs = read_wav(args.input)

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    base_file_name = os.path.splitext(os.path.basename(args.input))[0]

    if args.up is not None:
        up_data, up_fs = upsampling(args.up, data, fs)
        write_wav(
            os.path.join(args.output_dir, base_file_name + "_up.wav"),
            up_data, up_fs
        )

    if args.down is not None:
        down_data, down_fs = downsampling(args.down, data, fs)
        write_wav(
            os.path.join(args.output_dir, base_file_name + "_down.wav"),
            down_data, down_fs
        )
