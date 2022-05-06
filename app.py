import os
import wave
import shutil
import struct
from typing import Tuple

import librosa
import scipy.signal
import numpy as np
import streamlit as st
import plotly.express as px

GRAPH_WIDTH = 720
GRAPH_HEIGHT = 400
TMP_DIR = "./tmp"

if os.path.exists(TMP_DIR):
    shutil.rmtree(TMP_DIR)
os.makedirs(TMP_DIR)


@st.cache
def calc_spectrogram(wav: np.ndarray, sr: int, hop_len: int = 128, win_len: int = 256) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """スペクトログラムを計算する.

    Args:
        wav (np.ndarray): 信号データ
        sr (int): サンプリングレート
        hop_len (int, optional): FFT時のホップレングス. Defaults to 128.
        win_len (int, optional): FFT時の窓幅. Defaults to 256.

    Returns:
        Tuple[np.ndarray, np.ndarray, np.ndarray]: _description_
    """
    sample_freq_fs_fc, segment_time_fs_fc, spec_data_fs_fc = scipy.signal.spectrogram(wav, sr, nperseg=win_len, noverlap=hop_len)
    return sample_freq_fs_fc, segment_time_fs_fc, spec_data_fs_fc


def output_tmp_audio(data, sr, file_path) -> None:
    """入力されたファイル名でwavファイルを書き出す.

    Args:
        filename (str): 出力ファイルパス
        data (np.array): 信号データ
        fs (int): サンプリングレート
    """
    # データを-32768から32767の整数値に変換
    data = [int(x * 32767.0) for x in data]
    # バイナリ化
    binwave = struct.pack("h" * len(data), *data)
    wf = wave.Wave_write(file_path)
    params = (
        1,                          # channel
        2,                          # byte width
        sr,                         # sampling rate
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

    return (np.array(down_data), int(fs/conversion_rate))


def main():
    st.title("Sampling Rate Conversion")
    uploaded_file = st.sidebar.file_uploader("Audio file upload")

    if uploaded_file is not None:
        wav, sr = librosa.load(uploaded_file, sr=None, mono=True)
        upsampling_file = os.path.join(TMP_DIR, "up.wav")
        downsampling_file = os.path.join(TMP_DIR, "down.wav")

        st.subheader('Original Audio')

        st.write('sampling rate = ', sr, 'Hz')
        st.audio(uploaded_file)

        # SideBar
        st.sidebar.title('spectrogram')
        hop_len = st.sidebar.slider('hop len',  min_value=128, max_value=2048, step=128, value=128)
        win_len = st.sidebar.slider('win len',  min_value=512, max_value=4096, step=256, value=512)
        st.sidebar.title("sampling conversion")
        up_rate = st.sidebar.slider('up sampling rate',  min_value=2, max_value=20, step=2, value=2)
        down_rate = st.sidebar.slider('down sampling rate',  min_value=2, max_value=20, step=2, value=2)

        # Original Audio Visualize
        freq, _, spec = calc_spectrogram(wav, sr, hop_len, win_len)
        fig = px.imshow(np.flipud(spec), aspect='auto')
        fig.update_layout(title="Up Sampling Spectrogram", width=GRAPH_WIDTH, height=GRAPH_HEIGHT,
                            xaxis = dict(showticklabels=False),
                            yaxis = dict(
                            tickmode = 'array',
                            tickvals = [1, int(spec.shape[0]/4), int(spec.shape[0]/2), int(spec.shape[0]-1)],
                            ticktext = [str(int(freq[int(spec.shape[0]-1)])), str(int(freq[int(3*spec.shape[0]/4)])), str(int(freq[int(spec.shape[0]/2)])), str(0)],
                            title = "frequency(Hz)"))
        st.write(fig)

        # Up Sampling Audio Visualize
        st.subheader('Up Sampling Audio')
        up_wav, up_sr = upsampling(up_rate, wav, sr)
        st.write('sampling rate = ', up_sr, 'Hz')
        output_tmp_audio(up_wav, up_sr, upsampling_file)
        st.audio(upsampling_file)

        freq, _, spec = calc_spectrogram(up_wav, up_sr, hop_len, win_len)
        fig = px.imshow(np.flipud(spec), aspect='auto')
        fig.update_layout(title="Down Sampling Spectrogram", width=GRAPH_WIDTH, height=GRAPH_HEIGHT,
                            xaxis = dict(showticklabels=False),
                            yaxis = dict(
                            tickmode = 'array',
                            tickvals = [1, int(spec.shape[0]/4), int(spec.shape[0]/2), int(spec.shape[0]-1)],
                            ticktext = [str(int(freq[int(spec.shape[0]-1)])), str(int(freq[int(3*spec.shape[0]/4)])), str(int(freq[int(spec.shape[0]/2)])), str(0)],
                            title = "frequency(Hz)"))
        st.write(fig)

        # Down Sampling Audio Visualize
        st.subheader('Down Sampling Audio')
        down_wav, down_sr = downsampling(down_rate, wav, sr)

        st.write('sampling rate = ', down_sr, 'Hz')
        output_tmp_audio(down_wav, down_sr, downsampling_file)
        st.audio(downsampling_file)

        freq, _, spec = calc_spectrogram(down_wav, down_sr, hop_len, win_len)
        fig = px.imshow(np.flipud(spec), aspect='auto')
        fig.update_layout(title="Original Spectrogram", width=GRAPH_WIDTH, height=GRAPH_HEIGHT,
                            xaxis = dict(showticklabels=False),
                            yaxis = dict(
                            tickmode = 'array',
                            tickvals = [1, int(spec.shape[0]/4), int(spec.shape[0]/2), int(spec.shape[0]-1)],
                            ticktext = [str(int(freq[int(spec.shape[0]-1)])), str(int(freq[int(3*spec.shape[0]/4)])), str(int(freq[int(spec.shape[0]/2)])), str(0)],
                            title = "frequency(Hz)"))
        st.write(fig)


if __name__ == "__main__":
    main()
