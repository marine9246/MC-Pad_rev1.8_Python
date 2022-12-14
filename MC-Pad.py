"""
このファイルは、理解のためにver1.8にコメントを追記したファイルです。
プログラムは、そのままで、軽微な整形（#XXX⇒#　XXX）等も合わせて実施しています。
"""
# ------------ 1. モジュールインポート ---------------------------------
import time
import copy
# import numpy as np
import csv
import shutil  # ファイル移動
from numpy.lib import stride_tricks
# from numpy.core.numeric import tensor dot
import pandas as pd
# import matplotlib.pyplot as plt
import serial
from serial.tools import list_ports
# import seaborn as sns
import time
import sys
import os, tkinter, tkinter.filedialog, tkinter.messagebox
import tkinter.ttk as ttk
import tkinter.scrolledtext
import threading  # 並列処理
import cv2  # カメラ取得
import datetime
import itertools  # 2次元配列を1次元に平坦化
import re  # 文字列置換
import glob

from PIL import ImageGrab, Image  # 画像処理関係
# from pynput import keyboard #マウスやキーボード操作
import win32gui  # スクリーンショット関係

# import xlrd     #excel読み込み
# import pprint   #配列print時に改行で見やすく
# ------------------- ~ 1. モジュールインポート ------------------------
# ------------------- 2. データ変数　GUI変数定義 -----------------------
tk = tkinter.Tk()  # メインウインドウの作成 tk.mainloop()を最後に実行してウインドウを表示する

rev_name = 'rev1.8'  # Nucleoで表示するRevと合わせる必要あり
Software_name = 'MC-Pad ' + rev_name + ' ~Pulse Analysis & Development~'
wait_uart = 0.005  # UART送信後の待ち時間 通信エラーおこる場合は大きくする
# ------------------- ~ 2. データ変数　GUI変数定義 ----------------------
# ------------------- 3. NUCLEO COMポート検索 -------------------------
global ser
global Com_No
ports = list_ports.comports()  # 接続されているcomポートのリストを取得、2つのcomポートを使っていればリスト2つ。
# 取得できたportsリストの中から、デバイス名に"STLink"があるデバイスのみを取り出す
device = [info for info in ports if "STLink" in info.description]  # .descriptionでデバイスの名前を取得出来る
if not len(device) == 0:  # 上記条件に合う場合、device !=0なので以下の式に入る
    ser = serial.Serial(device[0].device)  # 名前に"STlink"があるcomポートの設定値を読み込む device[0].deviceはSTlinkがあるcomポート番号
    Com_No = str(device[0])  # リストdeviceの[0]はListPortInfo: COM*-STMicroelectronicsSTLink Virtual COM Port(COM*)
    print(Com_No + ' open')
    ser.baudrate = 921600  # 通信速度の設定変更
    ser.timeout = None  # timeoutなし
    ser.send_break()  # Brake信号送信 Nucleo reset

else:
    Com_No = 'Nucleo未接続'
    print('Nucleoが接続されていません')
# -------------------- ~ 3. NUCLEO COMポート検索 ----------------------

# -------------------- 4. Tkinter関係変数 -----------------------------
pulse_disp_num = 6  # UIに表示するパルスの数
labewid_1 = 16  # ラベルの幅
boxwid_1 = 10
pulsemode_0 = tkinter.BooleanVar()  # チェックボックス変数　pulsemode_0.set(True)でON .set(False)でOFF　Triger
pulsemode_1 = tkinter.BooleanVar()  # チェックボックス変数　極性反転
pulsemode_2 = tkinter.BooleanVar()  # チェックボックス変数　Vrs enable
pulsemode_3 = tkinter.BooleanVar()  # チェックボックス変数　補正有り
pulsemode_4 = tkinter.BooleanVar()  # チェックボックス変数　Pe設定 Enable
pulsemode_5 = tkinter.BooleanVar()  # チェックボックス変数　※使用箇所無し
stepvm_en = tkinter.BooleanVar()  # チェックボックス変数 Vm設定　±step
# -------------------- ~ 4. Tkinter関係変数 ---------------------------
# -------------------- 5. Pulse設定配列、GUI表示データ定義 ---------------
pulse_set_array = [['' for i in range(20)] for j in range(1)]  # 2次元配列定義 jのrange(1)なので["","","",....,""]
pulse_set_n = 0  # パルス種設定
wait_set_n = 1  # Wait時間
anystep_n = 2  # 任意パルスステップ数
pewidth_n = 3  # Peパルス幅
pewait_n = 4  # Peパルス後のWait時間
spkperiod_n = 5  # SPK周期
spkon_n = 6  # SPKON時間
Vm_set_n = 7
Vm_min_n = 8
Vm_max_n = 9
Vm_step_n = 10
Vth_set_n = 11

vm_minmum = 1.0  # 電圧設定下限
vm_maximum = 4.0  # 電圧設定上限

focus = 500

pulse_type = 7  # パルス種
pulse_wid_name = [  # パルス幅Entry配置名前 この要素がEntryボックス
    ['wid0_A', 'wid0_B', 'wid0_C', 'wid0_D', 'wid0_E', 'wid0_F'],
    ['wid1_A', 'wid1_B', 'wid1_C', 'wid1_D', 'wid1_E', 'wid1_F'],
    ['wid2_A', 'wid2_B', 'wid2_C', 'wid2_D', 'wid2_E', 'wid2_F'],
    ['wid3_A', 'wid3_B', 'wid3_C', 'wid3_D', 'wid3_E', 'wid3_F'],
    ['wid4_A', 'wid4_B', 'wid4_C', 'wid4_D', 'wid4_E', 'wid4_F'],
    ['wid5_A', 'wid5_B', 'wid5_C', 'wid5_D', 'wid5_E', 'wid5_F'],
    ['wid6_A', 'wid6_B', 'wid6_C', 'wid6_D', 'wid6_E', 'wid6_F'], ]

pulse_num_name = [  # パルス本数Entry配置名前　この要素がEntryボックス
    ['num0_A', 'num0_B', 'num0_C', 'num0_D', 'num0_E', 'num0_F'],
    ['num1_A', 'num1_B', 'num1_C', 'num1_D', 'num1_E', 'num1_F'],
    ['num2_A', 'num2_B', 'num2_C', 'num2_D', 'num2_E', 'num2_F'],
    ['num3_A', 'num3_B', 'num3_C', 'num3_D', 'num3_E', 'num3_F'],
    ['num4_A', 'num4_B', 'num4_C', 'num4_D', 'num4_E', 'num4_F'],
    ['num5_A', 'num5_B', 'num5_C', 'num5_D', 'num5_E', 'num5_F'],
    ['num6_A', 'num6_B', 'num6_C', 'num6_D', 'num6_E', 'num6_F'], ]

pulse_width_array = [  # パルス幅設定配列
    [732, 0, 1960, 0, 0, 0],
    [732, 0, 1960, 0, 0, 0],
    [0, 1000, 1000, 1000, 0, 0],
    [0, 1000, 1000, 1000, 0, 0],
    [1500, 0, 0, 0, 0, 0],
    [630, 630, 1260, 0, 0, 0],
    [0, 0, 244, 0, 0, 0]]

pulse_train_array = [['' for i in range(12)] for j in range(7)]  # 2次元配列定義　空のリスト作成
pulse_train_array_str = [['' for i in range(12)] for j in range(7)]  # 2次元配列定義

pulse_train_array_name = [['' for i in range(12)] for j in range(7)]  # 2次元配列定義
"""
pulse_train_array_name = [["","","","","","","","","","","",""], 行番号0
                          ["","","","","","","","","","","",""], 行番号1
                          .-------- row 行内容 ----------------
                          .
                          ["","","","","","","","","","","",""]] 行番号6
"""
for i, row in enumerate(pulse_train_array_name, 0):  # i=行番号、row=行内容 上記リストのインデックスがi、値がrow
    for n, col in enumerate(row):  # n=列番号、col=列内容 上記rowのインデックスがn、値がcol
        col = 'pat' + str(i) + str(n)  # 最終的にcol='pat611'だが、下の代入により書き換わる

pulse_num_array = [  # パルス本数設定配列
    [1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1],
    [1, 1, 10, 1, 1, 1]]

pulse_train_name = [0] * 7  # [0,0,0,0,0,0,0]
pulse_train_labename = [0] * 7  # [0,0,0,0,0,0,0]
for i, row in enumerate(pulse_train_labename, 0):  # 上記のインデックスがi、値がrow
    col = 'trname' + str(i)  # col = 'trname6'

# シーケンスEntry配置名　行(row)数=シーケンス数、列(col)数=パラメータ数
"""
sequence_name　= [["","","","","","","","","",""], 行番号0
                  ["","","","","","","","","",""], 行番号1 
                   .-------- row 行内容 -------
                   .
                  ["","","","","","","","","",""]] 行番号9                  
"""
sequence_name = [['' for col in range(10)] for row in range(10)]
for i, row in enumerate(sequence_name, 0):  # i=行番号、row=行内容 上記リストのインデックスがi、値がrow
    for n, col in enumerate(row):  # n=列番号、col=列内容 上記rowのインデックスがn、値がcol
        col = 'se' + str(i) + str(n)  # seq00,seq01....seq(i)(n),最終的にseq99

seq_runopt = 0
sequence_array = [[0] * 10 for row in range(10)]  # 2次元配列を0で初期化
"""
sequence_array = [[0,0,0,0,0,0,0,0,0,0], 行番号0
                  [0,0,0,0,0,0,0,0,0,0], 行番号1
                  .----- row 行内容 ----
                  .
                  [0,0,0,0,0,0,0,0,0,0]]　行番号9
"""
for i, row in enumerate(sequence_array, 0):  # i=行番号、row=行内容 上記リストのインデックスがi、値がrow
    if i == 0:
        sequence_array[i] = [1, 40, 200, 1, 0, 0, 0, 0, 0, 3.0]  # シーケンス設定配列 初期値
    else:  # i=1~9
        sequence_array[i] = [0, 0, 200, 0, 0, 0, 0, 0, 0, 3.0]  # シーケンス設定配列 初期値

seq_jdge_array = [0] * 7  # 判定方法選択　0 フォト判定/1 Vrs判定/2フォトNG停止3/周波数設定/4保存/5詳細保存/6評価パルス設定　3周波数設定⇒設定無効
for i, row in enumerate(seq_jdge_array, 0):  # seq_jdge_array = [0,0,0,0,0,0,0] インデックスがi、値がrow
    seq_jdge_array[i] = tkinter.BooleanVar()  # チェックボックス変数　7個のチェックボックスを用意しているが、6個しかGUI上に無い。評価パルス設定が無い

# カメラ関係変数
# cam_list = []
cam_no = 0
cam_delaylist = [100, 300, 500, 700, 1000]
cam_delay = cam_delaylist[1]  # cam_delayListからdelay値を選択

# フォト位置検出変数
# global entrypi2_3
# piseq_save = tkinter.BooleanVar() #チェックボックス変数
# piseq_save_det = tkinter.BooleanVar() #チェックボックス変数
# piseq_stop = tkinter.BooleanVar()
# piseq_freq = tkinter.BooleanVar()
piseq_section = [0] * 6  # [0,0,0,0,0,0]
for i in range(6):
    piseq_section[i] = tkinter.BooleanVar()  # 6個のチェックボックスを用意

piset_name = [0] * 6  # [0,0,0,0,0,0]
piset_array = [0, 360, 200, 3.0, 0, 0]  # Photo検出時のパルス条件設定　使用パルス/1周step数/周波数/電圧/検出mode/offset
piresult = ['pires0', 'pires1', 'pires2']

piset_value_name = [[0] * 3 for row in range(4)]  # [[0,0,0],[0,0,0],[0,0,0],[0,0,0]]
piset_value_array = [[2.4, 1.2, 0.1], [1.0, 1.0, 0.1], [200, 200, 20], ['1']]  # シーケンス設定GUI部
# result_data =[['' for col in range(30)] for row in range(100)]

# vrsウィンドウ変数
vrswindow_flag = 0  # 使用していない
vrsdt_name = [0] * 4  # [0,0,0,0]
vrsdt_array = [1500, 2700, 4000, 8000]  # Dt区間 GUI上は1400/3000/4000/5000 これはinitial_trainで読み込まれ書き換えられる
vrsjdg_name = [0] * 16  # [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
vrsjdg_array = [1, 1, 0, 1,  # 1:NG, 0:OK
                0, 1, 0, 1,
                1, 1, 0, 1,
                0, 1, 0, 1]  # initial.trainで書き換えられる　patA、patB
df_vrs_res = pd.DataFrame()  # df_vrs_resオブジェクトをデータフレームオブジェクトとして扱う


# -------------------- ~ 5. Pulse設定配列、GUI表示変数定義 -----------
# 6. initial設定読み込み に処理が移る
#
# ----------------- 関数定義 ----------------------------------
# -------------- Select_COM() -----------------------------
# //シリアルポート制御サブルーチン-----------------------------
def Select_COM(event):
    """
    メインウインドのCOMポートOPENボタンの左クリック入力により、コールされる。
    COMポートEntryのCOMポート番号を取得し、シリアルポートOPEN
    パルス設定、パルス列、幅、本数をNucleoに送信する

    :param event:
    :return:
    """
    Com_No = Box1_1.get()  # get()でエントリーボックス値取得　この時点でstr型のため、下でのstr型変換不要
    print(Com_No + ' open')
    Com_No = str(Com_No)
    ser.open()  # シリアルポートOPEN
    # ser.flush()#コマンド送信完了するまで待機
    time.sleep(wait_uart)  # wait_UART 5msec sleep
    manual_pulse_set()  # パルス設定の取得とNucleoへの送信
    pulse_train_set()  # パルス列設定をNucleoへ送信
    pulse_width_set()  # パルス幅設定と本数をNucleoへ送信
    vm_write()  # Vm設定値を読み込みNucleoへ送信
    print('init end')
    Button1_2.config(state="normal")  # Closeボタン有効化
    Button1_1.config(state="disabled")  # Openボタン無効化 disableをdisabledに変更


# -------------- ~ Select_COM() ---------------------------

# ------------- Close_COM() -------------------------------
def Close_COM(event):
    """
    メインウインドのCOMポートCloseボタンの左クリック入力により、コールされる。
    COMポートEntryのCOMポート番号を取得しコンソールにClose表示とNucleoにブレーク信号送信

    :param event:
    :return:
    """
    ser.send_break()  # Brake信号送信 Nucleo reset
    time.sleep(1)
    Com_No = Box1_1.get()  # get()でエントリーボックス値取得
    print(Com_No + ' close')
    ser.close()  # シリアルポートCLOSE
    Button1_1.config(state="normal")  # OPENボタン有効化
    Button1_2.config(state="disabled")  # Closeボタン無効化 disableをdisabledに変更


# ------------- ~ Close_COM() -----------------------------

# -------------- nucleo_revcheck() ------------------------
def nucleo_revchek():
    """
    Nucleoのソフトver.チェック
    シリアル通信で、'v'を送信し、Nucleoからver.のchar型配列データを得る。
    :return:
    """
    ser.write(b'v')  # シリアル通信:送信 'v':ver.チェックコマンド送信
    ver_str = read_serial2()  # シリアル通信受信により、ver.取得
    print('chk' + ver_str)
    if (rev_name in ver_str):  # python側のrev_nameとNucleo側のverが同じかチェックする。
        time.sleep(0.001)  # 1msecのsleep
    else:  # ver.が異なっていてもその後の動作は継続する。
        tkinter.messagebox.showerror('エラー', 'Nucleoをアップデートする必要があります')


# --------------　~ nucleo_revcheck() -----------------------

# ------------- manual_pulse_bot() -------------------------
# ボタン押し実行サブルーチン-------------------------------------
def manual_pulse_bot(event):
    """
    <pulse設定>項目内の'設定送信'ボタンが左クリックされた際に実行される。
    平行処理として、manual_pulse_set(項目内のパラメータを読み込み、Nucleoに送信する。)
    を開始する。
    :param event:
    :return:
    """
    thread_pul = threading.Thread(target=manual_pulse_set)  # 平行処理のインスタンス作成
    Button3_1.config(state="disabled")  # ボタン無効化 disable⇒disabledに変更
    thread_pul.start()  # 平行処理開始


# ------------- ~ manual_pulse_bot() ----------------------

# ------------ pulse_width_bot() --------------------------
def pulse_width_bot(event):  # パルス幅/本数をBoxから読み取り
    """
    <Pulse幅/本数>項目内の'設定送信'ボタンが左クリックされた際に実行される。
    平行処理として、pulse_width_set(項目内のパラメータを読み込み、Nucleoに送信する。)
    を開始する。

    :param event:
    :return:
    """
    thread_pul = threading.Thread(target=pulse_width_set)  # 平行処理のインスタンス作成
    Button5_20.config(state="disabled")  # ボタン無効化 disable⇒disabledに変更
    thread_pul.start()  # 平行処理開始


# ------------ ~ pulse_width_bot() ------------------------

# ---------------- pulse_seq_bot() ------------------------
def pulse_seq_bot(event):
    """
    mainウインドウのシーケンス機能ボタン押下で表示されるシーケンス設定ウインドウの単独実行ボタンを押下で実行される。
    <単独実行>を<実行中>の表示に変更し、ボタンを無効化する
    この関数は、スレッド処理するオブジェクト（=thread_seq、実行処理はpulse_seq_run）を生成し、startさせる
    :param event:
    :return:
    """
    thread_seq = threading.Thread(target=pulse_seq_run)
    seq_run.set('実行中')
    Button6_1.config(state="disable")  # ボタン無効化
    thread_seq.start()  # スレッド(並列)処理


def pulse_seqread_bot(event):
    """
    mainウインドウのシーケンス機能ボタン押下で表示されるシーケンス設定ウインドウの設定読込ボタンを押下で実行される。
    ボタンを無効化する
    この関数は、スレッド処理するオブジェクト（=thread_seqread、実行処理はseq_setting）を生成し、startさせる
    :param event:
    :return:
    """
    thread_seqread = threading.Thread(target=seq_setting)
    Button6_2.config(state="disable")  # ボタン無効化
    thread_seqread.start()  # スレッド(並列)処理


def pulse_train_bot(event):
    """
    mainウインドウのパルス列設定ボタン押下で表示されるパルス列設定ウインドウの設定読込ボタンを押下で実行される。
    ボタンを無効化する
    この関数は、スレッド処理するオブジェクト（=thread_tr、実行処理はtrain_setting）を生成し、startさせる
    :param event:
    :return:
    """
    thread_tr = threading.Thread(target=train_setting)
    Button8_1.config(state="disable")  # ボタン無効化
    thread_tr.start()  # スレッド(並列)処理


def photo_init_bot(event):
    """
    mainウインドウのシーケンス機能ボタン押下で表示されるシーケンス設定ウインドウのPI針位置単独ボタンを押下で表示される<PI初期設定>ウインドウの
    検出初期設定ボタンの押下で実行される。
    ボタンを無効化する
    この関数は、スレッド処理するオブジェクト（=thread_phini、実行処理はphoto_init）を生成し、startさせる
    :param event:
    :return:
    """
    thread_phini = threading.Thread(target=photo_init)
    Buttonpi_1.config(state="disable")  # ボタン無効化
    thread_phini.start()  # スレッド(並列)処理


def photo_posiset_bot(event):
    """
    mainウインドウのシーケンス機能ボタン押下で表示されるシーケンス設定ウインドウのPI針位置単独ボタンを押下で表示される<PI初期設定>ウインドウの
    ゼロ位置セットボタンの押下で実行される。
    ボタンを無効化する
    この関数は、スレッド処理するオブジェクト（=thread_phset、実行処理はphoto_posiset_manu）を生成し、startさせる
    :param event:
    :return:
    """
    thread_phset = threading.Thread(target=photo_posiset_manu)
    Buttonpi_2.config(state="disable")  # ボタン無効化
    thread_phset.start()  # スレッド(並列)処理


def photo_posicheck_bot(event):
    """
    mainウインドウのシーケンス機能ボタン押下で表示されるシーケンス設定ウインドウのPI針位置単独ボタンを押下で表示される<PI初期設定>ウインドウの
    ゼロ位置確認ボタンの押下で実行される。
    ボタンを無効化する
    この関数は、スレッド処理するオブジェクト（=thread_phche、実行処理はphoto_posicheck）を生成し、startさせる
    :param event:
    :return:
    """
    thread_phche = threading.Thread(target=photo_posicheck)
    Buttonpi_3.config(state="disable")  # ボタン無効化
    thread_phche.start()  # スレッド(並列)処理


def photo_seqtest_bot(event):
    """
    mainウインドウのシーケンス機能ボタン押下で表示されるシーケンス設定ウインドウのスタートボタンの押下で実行される。
    ボタンを無効化し、ストップボタンを有効化する
    この関数は、スレッド処理するオブジェクト（=thread_phche、実行処理はseqrun_repeat）を生成し、startさせる
    :param event:
    :return:
    """
    thread_phche = threading.Thread(target=seqrun_repeat)
    Buttonpi2_1.config(state="disable")  # ボタン無効化
    Buttonpi2_2.config(state="normal")  # ボタン有効化
    thread_phche.start()  # スレッド(並列)処理


def photo_seqtest_stop_bot(event):
    """
    mainウインドウのシーケンス機能ボタン押下で表示されるシーケンス設定ウインドウのストップボタンの押下で実行される。
    ボタンを無効化する
    この関数は、スレッド処理するオブジェクト（=thread_phche、実行処理はphoto_seqtest_stop）を生成し、startさせる
    :param event:
    :return:
    """
    thread_phche = threading.Thread(target=photo_seqtest_stop)
    Buttonpi2_2.config(state="disable")  # ボタン無効化
    thread_phche.start()  # スレッド(並列)処理


# この関数は使用していない
def vrs_winset(event):
    """

    :param event:
    :return:
    """
    vrs_win.vrs_window(tk, '+' + str(xposi) + '+' + str(yposi))


# -------------------------------------------------------
# NUCLEOパルス設定書込み------------------------------------
def command_write(command, set_num):
    """
    Nucleoに対し、UARTでコマンドを送信し、設定値データを送信する
    コマンド'x'の場合は、その前のコマンド＆データ送信に続いて、データ送信のみである。
    例)　pe waitとspk onはデータのみでその前のコマンド&データに引き続きデータを送信する
    :param command:Nucleoへの送信制御コマンド
    :param set_num:Nucleoへの送信データ
    :return:
    """
    if command != 'x':
        ser.write(bytes(command, 'utf-8'))  # バイト型で送信
        # ser.flush()#コマンド送信完了するまで待機
        time.sleep(wait_uart)
    ser.write(bytes(pulse_set_array[0][set_num], 'utf-8'))  # Nucleoへの送信するデータをリストから選択する
    ser.write(b'\r')  # Nucleoへ上記データを送信後、終了としてリターン送信
    read_serial()  # Nucleoからのシリアルデータ受信しょり


def pulse_select_set():
    """
    Nucleoへのコマンド'1'　pulse_setを送信し、受付メッセージを受信する
    :return:
    """
    ser.write(b'1')  # シリアル通信:送信　pulse_set
    # ser.flush()#コマンド送信完了するまで待機
    time.sleep(wait_uart)
    ser.write(bytes(pulse_set_array[0][pulse_set_n], 'utf-8'))  # pulse_set_nは0でcw-0を選択している
    read_serial()  # Pulse set 0 or 2,4　がNucleoから送信される
    read_serial()  # Pulse_set(1)=0 select　がNucleoから送信される


def pmode_set():
    """
    GUIの各チェックボックス変数が1なら各モードを’１’にしてNucleoにmode_setコマンド＆データを送信する
    :return:
    """
    mode = 0b00000
    if pulsemode_4.get() == 1:  # Pe設定 Enable
        mode = mode | 0b10000
    if pulsemode_3.get() == 1:  # 補正有り
        mode = mode | 0b01000
    if pulsemode_2.get() == 1:  # Vrs enable
        mode = mode | 0b00100
    if pulsemode_1.get() == 1:  # 極性反転
        mode = mode | 0b00010
    if pulsemode_0.get() == 1:  # Triger
        mode = mode | 0b00001
    ser.write(b'6')  # シリアル通信:コマンド　mode_set送信
    # ser.flush()#コマンド送信完了するまで待機
    time.sleep(wait_uart)
    ser.write(bytes(str(mode), 'utf-8'))  # 上記で設定したmode送信
    ser.write(b'\r')  # 送信終了リターン送信
    read_serial()  # Nucleoからの'mode = *set\n'を受信しコンソールに表示 *は送信したモード
    '''
    if pulsemode_5.get() == True:
        ser.write(bytes('1','utf-8'))
    else:
        ser.write(bytes('0','utf-8'))
    ser.write(b'\r')
    
    while 1:
        resp_str = read_serial2()
        if(resp_str == 'End!'):
            break
    '''


def manual_pulse_set():  # パルス設定の取得と送信
    """
    GUIの<Pulse設定>欄の各ウィジェットの値をリスト変数pulse_set_arrayに読み込み、Nucleoに送信する
    :return:
    """
    global pulse_set_array  # 2次元リスト [["","","","",...."",""]]だが値は1次元しかない
    pulse_set_array[0][pulse_set_n] = Pulse_cb.get()[0]  # 初期値　pulse_set_array[0][0]=0
    pulse_set_array[0][wait_set_n] = Box3_2.get()  # 初期値　pulse_set_array[0][1]=200
    pulse_set_array[0][anystep_n] = Box3_3.get()  # 初期値　pulse_set_array[0][2]=60
    pulse_set_array[0][pewidth_n] = Box3_4.get()  # 初期値　pulse_set_array[0][3]=244
    pulse_set_array[0][pewait_n] = Box3_5.get()  # 初期値　pulse_set_array[0][4]=3000
    pulse_set_array[0][spkperiod_n] = Box3_7.get()  # 初期値　pulse_set_array[0][5]=488
    pulse_set_array[0][spkon_n] = Box3_8.get()  # 初期値　pulse_set_array[0][6]=31
    pulse_set_array[0][Vth_set_n] = Box3_9.get()  # 初期値　pulse_set_array[0][11]=3.0
    print(
        pulse_set_array)  # [['0', '200', '60', '244', '3000', '488', '31', '', '', '', '', '3.0', '', '', '', '', '', '', '', '']]
    pulse_select_set()  # Nucleoへコマンド'1'　pulse_set送信
    command_write('2', wait_set_n)  # wait time 設定 パルス周期
    command_write('7', anystep_n)  # 任意step数設定
    command_write('8', pewidth_n)  # Pe設定
    command_write('x', pewait_n)  # 上のPe設定コマンド処理内でpewaitデータを送信する
    command_write('-', spkperiod_n)  # spk設定
    command_write('x', spkon_n)  # 上のspk設定処理内でspkonデータを送信する
    command_write('o', Vth_set_n)  # Vth設定
    pmode_set()  # mode設定
    Button3_1.config(state="normal")  # ボタン有効化　<Pulse設定>の設定送信ボタン


def read_entry(name, array):  # entry読み出し(entry名，書込み先)
    """
    パルス列設定、シーケンス設定のGUI上のEntryウィジェットに設定されている値を読み込み、リストに保存する。

    :param name:GUI上のEntryウィジェットのentry名
    :param array:entryに入力された値を保存するリスト変数
    :return:
    """
    for i, row in enumerate(name, 0):  # 例 CW-0行~Pr行まで1行づつ取り出す i=0のときrow=CW-0行
        for n, col in enumerate(row):  # 例 A列~F列まで取り出す i=0,n=0の時、CW-0行のA列
            array[i][n] = col.get()  # 例 書き込み先のリストに書き出す


# --------------------------------------------------------
def pulse_para_write(command, data, botno):  # パルスパラメータNucleo書込み(コマンド,入力値,有効化するボタン名 xだったら何もしない)
    """
    パルスパラメータ（設定値）をNucleoに書き込む
    :param command:Nucleo送信コマンド　p:pulse_train_set, 3:pulse_width_set, 4:pulse_num_set
    :param data:initial_train.xlsx、あるいはtrainファイルで読み込んだパラメータ
    :param botno:'x'以外なら、ボタン有化する　対象ボタン不明？
    :return:
    """
    for i, row in enumerate(data, 0):
        ser.write(bytes(command, 'utf-8'))  # バイト型で送信
        # ser.flush()                       #コマンド送信完了するまで待機
        time.sleep(wait_uart)
        ser.write(bytes(str(i), 'utf-8'))  # シリアル通信:送信
        # ser.flush()                      #コマンド送信完了するまで待機
        time.sleep(wait_uart)
        # read_serial()
        for n, col in enumerate(row):
            ser.write(bytes(str(data[i][n]), 'utf-8'))
            ser.write(b'\r')
        read_serial()
    if botno != 'x':
        botno.config(state="normal")  # ボタン有効化


def pulse_width_set():  # パルス幅本数を送信
    """
    GUI上の<Pulse幅/本数>のEntry欄に設定された値を読み込み、リストに保存して、Nucleoに送信セットする。

    :return:
    """
    read_entry(pulse_wid_name, pulse_width_array)  # GUI上の<Pulse幅/本数>のパルス幅を読み込み、pulse_width_arrayリストに保存
    read_entry(pulse_num_name, pulse_num_array)  # GUI上の<Pulse幅/本数>のパルス本数を読み込み、pulse_num_arrayリストに保存

    pulse_para_write('3', pulse_width_array, 'x')  # Nucleo送信コマンド'3':pulse_width_setでパルス幅送信セット
    pulse_para_write('4', pulse_num_array, Button5_20)  # Nucleo送信コマンド'4':pulse_num_setでパルス数送信セット


def pulse_train_set():
    """
    Nucleo　送信コマンド'p':pulse_train_setでpulse_train_arrayリストデータを送信する
    :return:
    """
    pulse_para_write('p', pulse_train_array, 'x')


# --------------------------------------------------------------------
# 電圧設定関係サブルーチン----------------------------------------------
def vm_write():
    """
    Vm設定Boxの値を読み込み、pulse_set_arrayリストに記憶し、Nucleoにコマンド:Voltage_setで送信する
    :return:
    """
    global vm_value
    vm_value = Box4_4.get()  # Vm設定Box値の読み込み
    pulse_set_array[0][Vm_set_n] = Box4_4.get()  # Vm設定Box値をリストに保存
    command_write('^', Vm_set_n)  # Voltage_setコマンドでデータpulse_set_array[0][Vm_set_n]を送信


def insert_vm(vm_disp):  # UI表示更新
    """
    mainウインドウの<Pulse出力>のVm設定[V]にvm_dispで渡される値を表示する
    :param vm_disp:
    :return:
    """
    Box4_4.delete(0, tkinter.END)  # 入力欄の表示すべてクリア
    Box4_4.insert(tkinter.END, vm_disp)  # vm_dispで渡される値を入力欄の最後に追加


def vm_set():
    """
    pulse_set_array[0][Vm_set_n=7]からVmの値をvm_valueに読み込み
    GUI上のVm設定Entryボックスの値と違えば、Vm設定Entryボックスを書き換える。（min,max制限有り）
    :return:
    """
    global vm_value
    vm_value = pulse_set_array[0][Vm_set_n]  # pulse_set_arrayに書き込まれたvm値を読み込む Vm_set_n=7は変？ vm_value=""となっている
    if vm_value != Box4_4.get():  # Vm設定Boxに入力されたVm値と保存されているVm値が異なる場合に処理する。
        if float(Box4_4.get()) < vm_minmum:  # vm最小値未満の場合の処理
            tkinter.messagebox.showerror('エラー', 'Vmは' + str(vm_minmum) + 'V以上としてください')
            insert_vm(vm_minmum)  # vm最小値で書き換える
        elif float(Box4_4.get()) > vm_maximum:  # vm最大値より大きい場合の処理
            tkinter.messagebox.showerror('エラー', 'Vmは' + str(vm_maximum) + 'V以上としてください')  # ここは'以下’の間違い
            insert_vm(vm_maximum)  # vm最大値で書き換える
        vm_write()  # Vm設定Entryボックスの値を読み込み、pulse_set_arrayリストに保存して、Nucleoに送信する


def vm_up(step):
    """
    mainウインドウのVm設定stepのEntryボックス内に表示されたステップをVm設定のEntryボックスに表示されているvm_value値に加算し
    小数点2桁にまるめ、新たにEntyrボックスに表示し、値を更新する
    :param step:
    :return:
    """
    global vm_value
    vm_value = str(round(float(vm_value) + float(step), 2))  # 小数点2桁にしてStr
    insert_vm(vm_value)  # 新たにVm設定のEntryボックスに入力する
    vm_set()  # 新たなvm値に更新


# -----------------------------------------------------------------------------------
# 任意stepパルス出力
def manual_pulse_out(dire, step):
    """
    mainウインドウ内で<Pulse出力>欄でマニュアルでパルス出力する。
    関数の引数により、正逆、ステップ数を判断し、nucleoにコマンドとしてシリアル通信する。
    :param dire:    駆動方向
    :param step:    駆動ステップ
    :return:
    """
    vm_set()
    if dire == 0:  # CW-0 正転
        if step == 1:  # 1step駆動
            ser.write(b'z')  # シリアル通信:送信 文字の場合はバイト型に変換して送信する　b'文字'
        elif step == 0:  # 0であるが、anystepで示されたstep数を実行
            ser.write(b'b')  # シリアル通信:送信
        elif step == 360:  # 360step駆動
            ser.write(b'a')  # シリアル通信:送信
    if dire == 1:  # CCW-1 逆転
        if step == 1:  # 1step駆動
            ser.write(b'x')  # シリアル通信:送信
        elif step == 0:  # 0であるが、anystepで示されたstep数を実行
            ser.write(b'n')  # シリアル通信:送信
        elif step == 360:  # 360step駆動
            ser.write(b's')  # シリアル通信:送信
    if dire == 2:  # Pr駆動
        ser.write(b'q')  # シリアル通信:送信
    if dire == 3:  # CCW→CW往復
        ser.write(b'n')  # シリアル通信:送信 CCW
        read_serial()  # End!受信
        ser.write(b'b')  # シリアル通信:送信 CW
    # read_serial()
    vrstime_print()  # vrstimeのprint
    if stepvm_en.get() == 1:  # mainウインドウのVm設定のstepチェックボックスがONなら
        vm_up(Box4_5.get())  # Vm step　Entry欄のstep値を読み込みVmに増加減する


# シーケンス動作実行---------------------------------------
def pulse_seq_run():
    """
    シーケンス設定ウインドウの<単独実行>ボタンを押下でスレッド処理される
    :return:
    """
    wait_seq = 0.0005
    if seq_runopt == 0:  # ???????????????????? 0,1,2があるが内容は不明 ???????????????????????????????????????
        # sequence_arrayリストの値は、プログラム開始初期に初期値設定されている
        # sequence_name（入力Entryボックス）はシーケンス設定ウインドウを作成した際に、sequence_arrayから読み込み入力されている
        read_entry(sequence_name,
                   sequence_array)  # entry値読み出し 　シーケンス設定ウインドウの<動作設定>の各Entryボックス内の値を読込む(sequence_nameボックスの値をsequence_arrayに書き出す)
    ser.write(b'5')  # シリアル通信:送信 シーケンスセットコマンドをnucleoに送信
    # ser.flush()#コマンド送信完了するまで待機
    time.sleep(wait_uart)  # 5msecウエイト
    seqset_err = 0  # 0/2 0:OK、2:エラー
    for i, row in enumerate(sequence_name,
                            0):  # 設定書き込み i:リストの行番号、row:リストの行の内容 ここまでで、sequence_nameの値とsequence_arrayの値は同じ
        # read_serial()
        for n in range(3):
            ser.write(bytes(sequence_array[i][n], 'utf-8'))  # ST_Linkのシリアル通信でn=0～2（pulse、step数、Freq)までを送信
            ser.write(b'\r')  # return送信
            # read_serial()
            time.sleep(wait_seq)  # 0.5msecウエイト
            if n < 2:  # Nucleo側は、パルス（M0,M1）、step数（M0,M1）、Freq（これはwait[us]とし定義されている）、パルスオプションの順で受け付ける
                ser.write(b'0\r')  # MC_PadはM0のみなので、Nucleoにpulseとstep数のM1分を0として送信する
                # read_serial()
                time.sleep(wait_seq)
        mode = 0b000000
        for n in range(6):  # option書込み
            # print(sequence_array[i][n+3])
            if sequence_array[i][n + 3] == '1':  # n+3=3～8 Trig,逆極,Vrs,補正P,Pe,50msのモードビットに'1'セット
                mode = mode | (2 ** n)  # 2^nでLSBからモードビットを立てる この場合、上記と各モードビットの並びは逆LSBがTrig
                # print(mode)
        ser.write(bytes(str(mode), 'utf-8'))  # 上記までで、pulse,step数,Freq,を送っているので続けてmode(6bit分)を送る
        ser.write(b'\r')  # return送信
        # read_serial()
        time.sleep(wait_seq)
        # 電圧設定書込み
        if float(sequence_array[i][9]) < 0.8:  # sequence_array[i][9]=Vm：電圧下限チェック
            sequence_array[i][9] = 0.8  # 強制的に0.8設定
            if int(sequence_array[i][1]) != 0:  # step設定が0stepならエラーにしない
                seqset_err = 2  # step設定が0step以外なら、エラーにする
        elif float(sequence_array[i][9]) > 4.0:  # 電圧上限チェック
            sequence_array[i][9] = 4.0  # 強制的に4.0にする
            if int(sequence_array[i][1]) != 0:  # step設定が0stepならエラーにしない
                seqset_err = 2  # step設定が0step以外なら、エラーにする
        # print(seqset_err)
        ser.write(
            bytes(str(sequence_array[i][9]), 'utf-8'))  # 上記までで、modeまで送っているから続けて電圧Vmを送る（Nucleoのsequence_set関数ではVmまで入力する）
        ser.write(b'\r')  # return送信
        read_serial()  # 送信したデータをNucleoから読込む
    while 1:
        resp_str = read_serial2()  # 警告処理付きの読み込み処理を行って
        if (resp_str == 'End!'):  # 'End!'が帰れば正常なので処理を抜ける
            break
    if seqset_err == 0:  # エラー無しの処理
        ser.write(b'9')  # シリアル通信　シーケンススタート
        # read_serial()
        vrstime_print()
    elif seqset_err == 2:  # 電圧設定でエラーのある場合の処理
        tkinter.messagebox.showerror('エラー', '電圧設定は0.8~4Vにしてください')

    if seq_runopt == 0:  # この変数の内容は不明、シーケンスrunオプション 0:通常？,1:Photo位置検出用シーケンス,2：？
        manual_pulse_set()  # mainウインドウ内の<Pulse設定>の値をNucleoに送信
        vm_write()  # mainウインドウ内のVm設定値をNucleoに送信
    Button6_1.config(state="normal")  # ボタン有効化
    seq_run.set('単独実行')  # ボタン表示変更


def seqrange_output(cnt, test_cnt, save):
    """

    :param cnt:
    :param test_cnt:
    :param save: 0：結果保存用リスト作成,1：動作MAPファイル保存,2：Vrs詳細ファイル保存,3：同じ時の実行結果を保存
    :return:
    """
    global result_data
    global result_data_vrs
    global result_data_vrs2
    global cnt_save
    global now_fname
    # global wid_test
    # global freq_test
    if save == 0:
        if test_cnt == 0 and cnt == 0:  # 初期化
            # now_fname = datetime.datetime.now()#保存ファイル名に使用
            cnt_save = 0
            result_data = [['' for col in range(50)] for row in range(100)]
            result_data_vrs = [['' for col in range(50)] for row in range(100)]
            result_data_vrs2 = [['' for col in range(50)] for row in range(100)]
            result_data[0][0] = seq_name.get()
            result_data[1][0] = 'Offset'  # ファイル書込み用
            # result_data[1][0]='Pulse種'#ファイル書込み用
            result_data[2][0] = 'Pulse幅比率'  # ファイル書込み用
            result_data[3][0] = '周波数設定'
        if cnt == 0:
            result_data[1][test_cnt + 1] = pioffset_test  # ファイル書込み用
            # result_data[1][test_cnt+1]=pulse_test#ファイル書込み用
            result_data[2][test_cnt + 1] = wid_test  # ファイル書込み用
            result_data[3][test_cnt + 1] = freq_test  # ファイル書込み用
        if seq_jdge_array[0].get() == 1:  # フォト判定が有効だったら
            result_data[4][0] = 'フォト判定'  # ファイル書込み用
            result_data[cnt + 5][0] = str('{:.2f}'.format(vm_test))  # ファイル書込み用
            result_data[cnt + 5][test_cnt + 1] = piresult[2].get()  # ファイル書込み用
        if seq_jdge_array[1].get() == 1:  # vrs判定が有効だったら
            result_data_vrs[0][0] = 'Vrs判定'  # ファイル書込み用
            result_data_vrs2[0][0] = 'Vrs平均本数'  # ファイル書込み用
            result_data_vrs[cnt + 1][0] = str('{:.2f}'.format(vm_test))  # ファイル書込み用
            result_data_vrs2[cnt + 1][0] = str('{:.2f}'.format(vm_test))  # ファイル書込み用
            vrs_result_read = vrsres_name[0].get('insert -1lines', 'insert -1lines lineend')
            if len(vrs_result_read) == 0:  # 空白だったら
                vrs_result_read = ['NULL', 'NULL', 'NULL']
            else:
                vrs_result_read = vrs_result_read.split()
            result_data_vrs[cnt + 1][test_cnt + 1] = vrs_result_read[1]  # 0:電圧、1:結果、2:平均本数
            result_data_vrs2[cnt + 1][test_cnt + 1] = vrs_result_read[2]  # 0:電圧、1:結果、2:平均本数
        if seq_runopt < 2 and seq_jdge_array[5].get() == 1 and seq_jdge_array[1].get() == 1:
            if test_cnt == 0 and cnt == 0:
                vrstext_save(1, 'w')
            else:
                vrstext_save(1, 'a')
        if cnt + 5 > cnt_save:
            cnt_save = cnt + 5
    elif save == 1:
        if seq_jdge_array[4].get() == 1:  # and seq_runopt < 2
            fname = now_fname.strftime('%y%m%d_%H%M%S_') + entrypi2_3.get().replace('file name',
                                                                                    '') + seq_name.get() + '_op'
            fname = re.sub(r'[\\|/|:|?|.|"|<|>|\|]', '_', fname)  # ファイル名に使えない文字列を置換
            csv_write(result_data[0:cnt_save + 2], 'Output', fname, 'w')  # 結果をcsvに保存
            if seq_jdge_array[1].get() == 1:  # vrs判定が有効だったら
                '''
                vrs_result_pat = vrsres_name[0].get('1.0', 'end -1c')
                print(vrs_result_pat.splitlines())
                vrs_result_list = vrs_result_pat.split()
                print(vrs_result_list)
                '''
                csv_write(result_data_vrs[0:cnt_save - 2], 'Output', fname, 'a')  # 結果をcsvに保存
                csv_write(result_data_vrs2[0:cnt_save - 2], 'Output', fname, 'a')  # 結果をcsvに保存
            concat_img(main_im, seqwin_im, fname)  # 試験設定画面を画像保存

    elif save == 2:
        if seq_jdge_array[5].get() == 1:  # 詳細保存が有効だったら
            # now = datetime.datetime.now()
            fname = entrypi2_3.get().replace('file name', '')
            fname = re.sub(r'[\\|/|:|?|.|"|<|>|\|]', '_', fname)  # ファイル名に使えない文字列を置換
            fname_vrs = entryvrs_1.get().replace('file name', '')
            fname_vrs = re.sub(r'[\\|/|:|?|.|"|<|>|\|]', '_', fname_vrs)  # ファイル名に使えない文字列を置換

            path = os.getcwd() + '/' + 'Output' + '/'
            fname_det = (now_fname.strftime('%y%m%d_')
                         + 'detail_' + fname_vrs
                         + fname + 'temp'
                         + '.csv')

            fname_det_new = (now_fname.strftime('%y%m%d_%H%M%S_')
                             + fname + seq_name.get() + '-detail_'
                             + '.csv')

            os.rename(path + fname_det, path + fname_det_new)

    elif save == 3:  # 同じ時の実行結果を結合
        target = now_fname.strftime('%y%m%d_%H%M%S_') + '*' + 'op.csv'  # 同じ時刻にスタートしたファイルを抽出
        fld_list = glob.glob(os.getcwd() + '/Output/' + target)  # ファイル名をlistに取得
        # print(fld_list)
        if len(fld_list) > 1:
            for i, row in enumerate(fld_list, 0):  # 一つのファイルに結合
                if i == 0:
                    df_all = pd.read_csv(fld_list[i], encoding="shift-jis", header=None)  # 日本語含むcsv、ヘッダーなし
                    df_all = df_all.dropna(how='all', axis=1)
                else:
                    df = pd.read_csv(fld_list[i], encoding="shift-jis", header=None)  # 日本語含むcsv、ヘッダーなし
                    df = df.dropna(how='all', axis=1)
                    df_all = pd.concat([df_all, df], axis=1)
                shutil.move(row, os.getcwd() + '/Output/origin/')
            path = os.getcwd() + '/Output/'
            df_all_file = now_fname.strftime('%y%m%d_%H%M%S_') + entrypi2_3.get().replace('file name',
                                                                                          '') + '_OutputAll'
            df_all_file = re.sub(r'[\\|/|:|?|.|"|<|>|\|]', '_', df_all_file)  # ファイル名に使えない文字列を置換
            df_all.to_csv(path + df_all_file + '.csv', encoding="utf-8-sig", index=False, header=False)


def seqrun_repeat():
    """

    :return:
    """
    global seq_runopt
    global now_fname
    now_fname = datetime.datetime.now()  # 保存ファイル名に使用

    if 'seq_path' in globals():
        if (Combopi1.current() != 0) and (Combopi1.get() != "全て実行"):
            seq_update(seq_path[Combopi1.current() - 1])
    if (Combopi1.get() != "全て実行"):
        seqrange_run()
    else:
        for i, row in enumerate(seq_path, 0):
            seq_update(row)
            seqrange_run()
            if seq_runopt == 2:
                break
        seqrange_output(0, 0, 3)


def seqrange_run():
    """

    :return:
    """
    global seq_runopt
    global wid_test
    global freq_test
    global pulse_test
    global vm_test
    global pioffset_test
    piseq_res.delete('1.0', 'end')  # テキストの最初から最後まで消去
    seq_runopt = 0

    pulse_width_set()  # パルス幅設定送信

    global seqwin_im, main_im
    seqwin_handle = get_handle()  # seqence_windowのHandle取得
    seqwin_im = screen_shot(seqwin_handle)  # シーケンスwindowイメージ読み取り

    # tk.attributes('-topmost', 1)#メイン画面をトップに固定表示
    # tk.attributes('-topmost', 0)#メイン画面の固定解除
    # main_handle = get_handle()  #main_windowのHandle取得
    main_im = screen_shot(main_handle)  # メインwindowイメージ読み取り

    # 電圧&周波数&パルス幅&使用パルス 設定読み込み
    for i, row in enumerate(piset_value_name, 0):
        for n, col in enumerate(row):
            if i == 3:
                if n == 0:
                    piset_value_array[i] = col.get().split(',')
            else:
                piset_value_array[i][n] = float(col.get())

    if piset_value_array[0][0] > piset_value_array[0][1]:
        piset_value_array[0][2] = -1 * piset_value_array[0][2]

    if float(piset_value_array[1][0]) > float(piset_value_array[1][1]):
        tkinter.messagebox.showerror('エラー', 'Pulse幅設定 StartよりStopの値を大きくしてください')
        return

    if int(piset_value_array[2][0]) > int(piset_value_array[2][1]):
        tkinter.messagebox.showerror('エラー', '周波数設定 StartよりStopの値を大きくしてください')
        return

    if float(piset_value_array[0][2]) == 0 or float(piset_value_array[1][2]) == 0 or float(
            piset_value_array[2][2]) == 0:
        tkinter.messagebox.showerror('エラー', 'stepは0より大きく値を設定してください')
        return

    print(piset_value_array)
    read_entry(sequence_name, sequence_array)  # seq設定読み出し
    seq_runopt = 1  # photo位置検出用シーケンス動作

    pioffset_array = [0]  # オフセット変更テストカウンタ
    # フォト判定初期設定
    if seq_jdge_array[0].get() == 1:  # フォト判定が有効だったら
        photo_seq_init()  # PI初期化
        pioffset_array = piset_name[5].get().strip().split(',')
        if piresult[0].get() != 'OK':
            seq_runopt = 2

    if seq_jdge_array[1].get() == 1:  # vrs判定が有効だったら
        vrs_window()  # vrsウィンドウ
        vrstext_clear()  # vrsウィンドウ結果クリア

    test_cnt = 0
    # フォトオフセット変更ループ
    for offset_num in range(len(pioffset_array)):
        photo_init_w(offset_num)
        pioffset_test = pioffset_array[offset_num]
        piseq_res.insert('end', 'Offset設定 :' + str(pioffset_test) + '\n')
        # パルス種変更ループ
        for pulse_n, pulse_test in enumerate(piset_value_array[3], 0):
            if seq_jdge_array[6].get() == 0:  # checkされていたらパルス変更しない
                for i, col in enumerate(sequence_array, 0):
                    sequence_array[i][0] = str(pulse_test)
            else:
                pulse_test = sequence_array[0][0]
            piseq_res.insert('end', 'pulse設定 :No' + str(pulse_test) + '\n')

            # パルス幅変更ループ
            wid_test = float(piset_value_array[1][0])  # パルス幅比率初期値
            while wid_test <= float(piset_value_array[1][1]) and seq_runopt < 2:
                pulse_width_array_sub = copy.deepcopy(pulse_width_array)
                for y, row in enumerate(pulse_width_array_sub, 0):  # パルス比率変更
                    for x, col in enumerate(row):
                        if piseq_section[x].get() == 1:  # checkされていたら幅変更
                            pulse_width_array_sub[y][x] = str(int(float(col) * wid_test))

                piseq_res.insert('end', 'Pulse幅比率:' + str(wid_test) + '\n')
                pulse_para_write('3', pulse_width_array_sub, 'x')

                # 周波数変更ループ
                freq_test = int(piset_value_array[2][0])  # 周波数初期値
                while freq_test <= int(piset_value_array[2][1]) and seq_runopt < 2:
                    if seq_jdge_array[3].get() == 0:  # checkされていたら周波数変更しない
                        for i, col in enumerate(sequence_array, 0):
                            # if int(sequence_array[i][2]) < 1000: #1000Hzより大きい設定だったら
                            sequence_array[i][2] = str(freq_test)
                    else:
                        freq_test = int(sequence_array[0][2])
                    piseq_res.insert('end', 'Freq設定  :' + str(freq_test) + 'Hz\n')
                    '''
                    result_data[0][test_cnt+1]=wid_test#ファイル書込み用
                    result_data[1][test_cnt+1]=freq_test#ファイル書込み用          
                    '''
                    seq_run_vm(test_cnt)  # 電圧可変テスト　test_cnt=0でコール
                    test_cnt += 1  # test_cnt=1

                    freq_test = freq_test + int(piset_value_array[2][2])
                    if seq_runopt == 2 or piset_value_array[2][2] == str(0) or seq_jdge_array[3].get() == 1:
                        freq_test = int(piset_value_array[2][1]) + 1
                wid_test = round(wid_test + float(piset_value_array[1][2]), 2)
                if seq_runopt == 2 or piset_value_array[1][2] == str(0):
                    wid_test = float(piset_value_array[1][1]) + 1

        seqrange_output(0, test_cnt, 1)  # 動作MAPファイル保存 test_cnt=1

    seqrange_output(0, test_cnt, 2)  # Vrs詳細ファイル保存(Rename) test_cnt=1
    for i, col in enumerate(sequence_array, 0):  # 電圧を初期値に
        sequence_array[i][9] = round(piset_value_array[0][0], 2)
    insert_entry(sequence_name, sequence_array)
    manual_pulse_set()
    pulse_para_write('3', pulse_width_array, 'x')
    insert_vm(str(pulse_set_array[0][Vm_set_n]))
    vm_write()
    piseq_res.insert('end', "テスト終了\n")
    piseq_res.see("end")
    Buttonpi2_1.config(state="normal")  # ボタン有効化
    Buttonpi2_2.config(state="disable")  # ボタン無効化


def seq_run_vm(test_cnt):
    """
    電圧可変テスト？ seqrange_run関数からのみコールされる
    ・mainウインドウからシーケンス機能ボタン押下で表示されるシーケンスウインドウの<シーケンス設定>欄の電圧範囲Start電圧値を読みとり、
    スクロールドtextBoxの表示
    ・

    :param test_cnt: 0のみでコール
    :return:
    """
    global seq_runopt
    global vm_test
    # piset_value_array [[2.4, 1.2, 0.1], [1.0, 1.0, 0.1], [200, 200, 20], ['1']]
    vm_test = round(piset_value_array[0][0], 2)  # 電圧範囲のStart電圧 小数点2桁以下を四捨五入

    cnt = 0
    posiset_flag = 1  # 位置セットフラグON
    if seq_jdge_array[0].get() == 1:  # チェックボタン"フォト検出"の値を取得、フォト検出判定が有効だったら
        posiset_flag = 0  # フォト検出判定有効なら、位置セットフラグOFFする(フォト検出でOKが出たら、位置セットフラグをONする)

    while 1:
        for i, col in enumerate(sequence_array, 0):  # シーケンス設定ウインドウの<動作設定>欄のシーケンス設定配列データの読み込み
            sequence_array[i][9] = vm_test  # [i][9]は、Vm　これに上記のStart電圧を代入
        piseq_res.insert('end', str('{:.2f}'.format(vm_test)) + "V")  # <シーケンス設定>のスクロールテキストBox（piseq_res)に挿入、小数点以下2桁で表示　
        insert_vm(str('{:.2f}'.format(vm_test)))  # mainウインドウ<Pulse出力>のVm入力欄にvm_test値を小数点以下2桁で入力表示させる

        # フォト判定　基準位置検出
        if seq_jdge_array[0].get() == 1:  # チェックボタン"フォト検出"の値を取得、フォト判定が有効だったら
            if 'OK' in piresult[2].get():  # piresult[2](ゼロ位置確認）に'OK'が有れば
                # if piresult[2].get() == 'OK':
                posiset_flag = 1  # 位置セットフラグをONする。
            else:  # piresult[2](ゼロ位置確認）に'OK'が無ければ
                posiset_flag = photo_seq_set(posiset_flag, cnt, test_cnt)  # 初期位置セット position_flag=0,cnt=0~,test_cnt=0

        if posiset_flag == 1:  # 位置セットフラグON（多分、検出初期設定、ゼロ位置セット、ゼロ位置確認までOKならこのフラグがONする？）
            pulse_seq_run()  # フォトインタプラ準備OKならシーケンス動作実行

        if posiset_flag == 1:  # 位置セットフラグON（多分、検出初期設定、ゼロ位置セット、ゼロ位置確認までOKならこのフラグがONする？）
            if seq_jdge_array[0].get() == 1:  # チェックボタン"フォト検出"の値を取得、フォト判定が有効だったら
                posiset_flag = photo_seq_check(cnt, test_cnt)  # 位置確認
            seqrange_output(cnt, test_cnt, 0)  # 結果保存用リスト作成 cnt=0~, test_cnt=0
            if posiset_flag == 2:  # このフラグは0～2まであるが、不明 (2:フォトNGで停止のチェックボックスが有効で、フォト検出NGの場合セット？)
                piseq_res.insert('end', "\n")  # <シーケンス設定>のスクロールテキストBoxに'end'を挿入
                break
        piseq_res.insert('end', "\n")  # <シーケンス設定>のスクロールテキストBoxに'end'を挿入
        piseq_res.see("end")  # <シーケンス設定>のスクロールテキストBoxを末尾までスクロールして表示させる
        vm_test = round(vm_test + piset_value_array[0][2], 2)  # 読込んだ初期電圧+Step電圧 小数点2桁以下を四捨五入
        if piset_value_array[0][2] > 0:  # Step電圧が正なら
            if piset_value_array[0][1] < vm_test:  # Stop電圧が新たなvm_testより小なら
                break
        if piset_value_array[0][2] < 0:  # step電圧が負なら
            if piset_value_array[0][1] > vm_test:  # Stop電圧が新たなvm_testより大なら
                break

        if seq_runopt == 2:  # この変数は0～2だが内容不明　
            piseq_res.insert('end', "途中終了\n")  # <シーケンス設定>のスクロールテキストBoxに'end'を挿入
            piseq_res.see("end")  # <シーケンス設定>のスクロールテキストBoxを末尾までスクロールして表示させる
            break
        cnt += 1


# エントリーBoxに書込み--------------------------------------------
def insert_entry(name, array):
    """
    ・mainウインドウの<Pulse幅[us]/本数>欄のEntryボックスに値を書き込む
    ・シーケンス設定ウインドウの<シーケンス設定>欄および<動作設定>欄のEntryボックスに値を書き込む
    :param name:　書き込むEntryボックスの指定 pulse_wid_name/pulse_num_name/sequence_name/piset_value_name[:3]
    :param array:　書き込むデータの指定 pulse_width_array/pulse_num_array/sequence_array/piset_value_array
    :return:
    """
    for i, row in enumerate(name, 0):  # i=0～、row：各Entryボックスの配列の行データ（Entry1、Entry2、・・・Entryn)
        for n, col in enumerate(row):  # n=0～、col:各EntryボックスEntry1、Entry2
            col.delete(0, tkinter.END)  # 各Entryボックス内の表示されているデータのクリア
            col.insert(tkinter.END, array[i][n])  # i,nで示す書き込みデータをEntryボックスに挿入する


def insert_train():
    """
    関数train_setting()より唯一呼ばれる。
    パルス列設定ウインドウのラベル表示　NP/--　NP/NP・・・等を動的に変えるためにラベルのtextvaliable＝pulse_train_array_name[y][x]としてある。
    pulse_train_array_nameはtkinter.StringVar()であるので、charもtkinter.StringVar()でそれにpulse_train_array_str[y][x]で読み込んだラベルをセットすることで、ラベル表示を動的に変更する

    :return:
    """
    for y, row in enumerate(pulse_train_array_name, 0):
        for x, char in enumerate(row):
            # pulse_train_array_name[y][x] = pulse_train_array_str[y][x]
            char.set(pulse_train_array_str[y][x])


# チェックボックス書込み-------------------------------
def set_checkbox(name, array):
    """
    シーケンス設定ウインドウのチェックボックスにtrue/falseの書き込み

    :param name:　BooleanVar()型の変数でシーケンス設定ウインドウのA:Fのチェックボックスとフォト検出/Vrs検出/保存・・等のチェックボックス変数
    :param array:　チェックボックスに設定する値true/false
    :return:
    """
    for x, col in enumerate(array, 0):
        name[x].set(array[x])       # colにarrayの要素を読み込むが、直接name[x]=チェックボックスのBooleanVar()にセットする

    # ファイル書込み-------------------


def csv_write(array, folder, fname, mode):  # mode:w=新規、a=追記
    """
    folder、fnameで指定されたファイルへarray（listデータ）の値を書き込んで保存する

    :param array: ファイルへ書き込むlistデータ
    :param folder:  ファイルのあるフォルダ
    :param fname: ファイルname
    :param mode: 書き込みモード　新規/追記
    :return:
    """
    # now = datetime.datetime.now()
    with open(os.getcwd() + '/' + folder + '/' + fname + '.csv', mode, newline="") as f:    # カレントDIRの指定フォルダにcsvファイルをOPEN　windowsではnewline=""必要
        writer = csv.writer(f)  # 上記OPENしたファイルオブジェクトを作成
        writer.writerows(array)     # ファイルオブジェクトにarrayで示されるデータlistを1行毎に書き込む


# ファイル読み込み-----------------------------------------------
def filepath_get(name, setting):  # setting 0:1ファイル、1:複数ファイル
    """
    nameを含むファイル（複数も含む）のパスを取得する

    :param name:    ファイルネームに含まれる名前
    :param setting: 複数ファイルか単数か指定
    :return:    ファイル（複数含む）のパス
    """
    # global  filepath
    # 選択候補を拡張子jpgに絞る（絞らない場合は *.jpg → *）
    filetype = [("", "*" + name + "*.xlsx")]    # ファイル拡張子およびファイルのフィルタリング指定
    dirpath = os.getcwd()  # os.path.dirname(__file__)#''   # カレントDIRの取得
    # print(dirpath)

    # 選択したファイルのパスを取得
    if setting == 1:    # 複数ファイルの場合
        filepath = tkinter.filedialog.askopenfilenames(filetypes=filetype, initialdir=dirpath)
    else:               # 単一ファイルの場合
        filepath = tkinter.filedialog.askopenfilename(filetypes=filetype, initialdir=dirpath)
    return filepath     # ファイルパスをreturn


def pulse_reading(event):
    """
    mainウインドウの<Pulse幅[us]/本数>欄の設定送信ボタンの横の設定読み込みボタン（表示されていない）をマウスクリックした際にコールされ、
    エクセルファイルから、パルス幅、本数を読み込み<Pulse幅/本数>のEntryボックスに表示し、内容をNucleoに送信する
    ただし、ボタンがそもそも表示されていないため、この関数は機能しない

    :param event:
    :return:
    """
    # global  filepath
    filepath = filepath_get('width', 0)     # 'ファイルネームに'width'を含むエクセルファイルのパスを取得
    width_name.set(os.path.basename(filepath))  # mainウインドウの<設定送信>の横にlabel5_21のテキスト表示でファイルパスを表示する仕組みだが機能しない
    global pulse_width_array
    global pulse_num_array

    df_pulse = pd.read_excel(str(filepath))
    df_pulse = df_pulse.astype(int)  # int型変換

    pulse_width_array = df_pulse.loc[:, 'Aw':'Fw'].values.tolist()  # Dataframeをlistに変換
    pulse_num_array = df_pulse.loc[:, 'An':'Fn'].values.tolist()  # Dataframeをlistに変換
    print(pulse_width_array)

    insert_entry(pulse_wid_name, pulse_width_array)  # entryに書込み
    insert_entry(pulse_num_name, pulse_num_array)  # entryに書込み
    pulse_width_set()  # 設定送信


######シーケンス設定読み込み
def seq_setting():
    """
    mainウインドウのシーケンス機能ボタン押下で表示されるシーケンス設定ウインドウの設定読込ボタンを押下で実行されるpulse_seqread_bot()
    の中でスレッド処理設定されるスレッド実行部分

    :return:
    """
    global seq_path
    seq_path = filepath_get('seq', 1)  # ファイル選択ウィンドウで、'seq'を含む複数のファイルのパスを得る

    seq_filelist = ['表示設定']
    for i, row in enumerate(seq_path, 0):   # row:上記で得たファイルパス
        # os.path.splitext(file_path)でタプルで（'拡張子以外',’.拡張子')を得る。[0]は拡張子以外、[1]は.拡張子
        # os.path.basename(file_path)で拡張子付きファイルネームのみ取得
        seq_filelist.append(os.path.splitext(os.path.basename(row))[0])     # ファイルネームのみ（拡張子無し）を取得
    seq_filelist.append('全て実行')     # seq_filelist = ['表示設定', file1, file2, file3,・・・, '全て実行']

    Combopi1["values"] = seq_filelist   # シーケンス設定ウインドウの<シーケンス設定>欄のコンボBoxのvaluesオプションに上記filelistを渡す
    Combopi1.current(0)  # 初期値  '表示設定'
    # print(str(Combopi1.current()))
    seq_update(seq_path[0])     # 上記でファイル選択したファイルパスの1番目の値を引数にseq_update関数をコール


def seq_reading(event):  # 読み込みボタン処理
    """
    シーケンスウインドウの<シーケンス設定>欄にある適用ボタンをマウス左クリックした際にコールされ、適用ボタンの左にあるコンボBoxにシーケンスファイルがある場合にseq_updateを実行
    :param event:
    :return:
    """
    if 'seq_path' in globals():
        if (Combopi1.current() != 0) and (Combopi1.get() != "全て実行"):    # current()でインデクス、get()で値の取得をする
            seq_update(seq_path[Combopi1.current() - 1])        # 現在のインデックス-1のファイルを指定してシーケンスupdate実行


def seq_update(filepath):
    """
    filepathで指定されたシーケンスファイルを実行
    :param filepath:
    :return:
    """
    # filepath = filepath_get('seq',0)#ファイル選択ウィンドウ

    seqWindow.lift()  # シーケンスwindowを最前面に移動させる
    try:  # エラー発生した場合、except実行
        seq_filename = os.path.splitext(os.path.basename(filepath))[0]      # filepathで渡されたファイル名（拡張子無し）を取得
        seq_filename = seq_filename.replace('_seq', '')     # 上記で取得したファイル名の_seqを削除
        seq_name.set(seq_filename)  # 読み込みファイル名表示をlabel5_21のラベル文字としてシーケンスウィンドウの設定読み込みボタンの横に表示
        global sequence_array
        # pandas.DataFrameとして読み込む
        df_seq_all = pd.read_excel(str(filepath), index_col=0, sheet_name=None)     # filepathで渡されたExcelファイルを先頭列をインデックスに全てのシートを読込む
        df_seq_raw = df_seq_all['seq']  # シートは、[seq]と[option]シートの2つがあるのでシート毎のデータに分ける
        df_op_raw = df_seq_all['option']
        # シーケンス動作設定
        df_seq = df_seq_raw.loc[:, 'pulse':'1sec'].astype(str)      # 全部の行と'pulse'～'1sec'までの列で示される2次元データを文字列データとして読込む
        df_seq['Vm'] = df_seq_raw['Vm']     # 'Vm'列のデータを読み込む
        sequence_array = df_seq.values.tolist()  # 上記のDataframeデータをlistに変換 ex:[[0,8,50,...3],[0,1,1000,...3],...[0,1,50...3]]
        insert_entry(sequence_name, sequence_array)     # シーケンス設定ウインドウの<動作設定>欄のEntryボックスに書き込む
        # 電圧、パルス幅、周波数設定
        df_op_vm = df_op_raw.loc['voltage':'freq', 'start':'step'].astype(str)  # optionシートの行：（voltage~freq）、列：（start~step）の値をstrにして読み込む
        piset_value_array = df_op_vm.values.tolist()  # Dataframeをlistに変換 ex:[[3.4,2.6,0.4],[1,1,0.2],[50,200,50]]
        insert_entry(piset_value_name[:3], piset_value_array)   # シーケンス設定ウインドウの<シーケンス設定>欄のEntryボックスに書き込む
        # 区間のパルス幅変更有無
        df_op_sec = df_op_raw.loc['pulse', 'A':'F'].astype(int)     # 'option'シートのデータの内、行：'pulse'、列：'A~F'のデータをint型に変換する。
        sec_array = df_op_sec.values.tolist()  # Dataframeをlistに変換　ex：[1,1,1,1,1,1]
        set_checkbox(piseq_section, sec_array)  # シーケンスウインドウの<シーケンス設定>欄のチェックボタン'A'~'F'を上記のsec_arrayのリストの値を書き込む
        # 判定実施の有無
        df_op_jdge = df_op_raw.loc['判定', 'start':'C'].fillna(0).astype(int)     # 'option'シートのデータの内、行:’判定'、列:'start'~'c'のデータをint型に変換する。欠損値は0で置き換え
        jdge_array = df_op_jdge.values.tolist()  # Dataframeをlistに変換 ex:[1,0,1,1,1,0]
        # jdge_array = jdge_array.fillna(0) #欠損値Nanを0に置換 旧seqfile対応
        set_checkbox(seq_jdge_array, jdge_array)    # シーケンスウインドウの<シーケンス設定>欄の判定チェックボタンに値を設定
        # フォトインタラプタ設定
        df_op_pi = df_op_raw.loc['PI設定', 'start':'C'].astype(int)   # 'option'シートのデータの内、行:’PI設定'、列:'start'~'c'のデータをint型に変換する。
        piset_array = df_op_pi.values.tolist()  # Dataframeをlistに変換 ex:[1,360,200,3,2,0]
        print(piset_array[1:5])     # コンソールに上記piset_arrayのデータの内、インデックス1~4までをprint出力
        for i, col in enumerate(piset_name, 0):     # i:0~5、col：リストpiset_nameの値（中身はウィジェットでコンボボックス、Entry,Entry,Entry,コンボボックス,Entry）
            if i == 0 or i == 4:    # piset_arrayの内容は、Pulse,Fullstep,Freq,電圧,mode,offset
                col.current(int(piset_array[i]))    # i=0:Pulse, i=4:modeの場合は、値をint型でcol(コンボbox）にセット
            else:
                col.delete(0, tkinter.END)      # col(Entry)の内容を削除し、Fullstep,Freq,電圧,offsetのいずれかの値をセットする
                col.insert(tkinter.END, piset_array[i])

        Button6_2.config(state="normal")  # ボタン有効化 シーケンスウインドウの設定読み込みボタン

        # seqWindow.attributes("-topmost", True) #windowをtopに表示

    except(FileNotFoundError, TypeError):
        tkinter.messagebox.showerror('エラー', 'seq.xlsxファイルが見つかりません')
    except:
        tkinter.messagebox.showerror('エラー', 'seq.xlsxファイル読み込みに失敗しました')  # 上記2つのエラー以外の処理


# ----------------- train_sort() --------------------------
def train_sort(array_name):  # パルス種類数が6以下の場合に配列の行を合わせる
    """
    GUI上はパルス種類が7種類表示できるが、パルス種類が6種類以下の場合にリストデータを0で補い、リストの行を7行に合わせる。
    その際、変換後の最後の行（7行目）に変換前の最後の行データを設定する。
    （例） パルス種類がデフォルト7だが、2種類しか指定されない場合
    変換前
                A1   B1  C1  ..  F1       A2  B2  C2  ..  F2
    パルス1      P1    P2   P3 .. P6       P7  P8  P9   .. P12
    パルス2      P21   P22  P23 ..P26      P27 P28 P29  .. P212

    変換後
                A1   B1  C1  ..  F1       A2  B2  C2  ..  F2
    パルス1      P1    P2   P3 .. P6       P7  P8  P9   .. P12
    パルス2      0     0    0  ..  0       0   0   0    .. 0
    パルス3      0     0    0  ..  0       0   0   0    .. 0
    パルス4      0     0    0  ..  0       0   0   0    .. 0
    パルス5      0     0    0  ..  0       0   0   0    .. 0
    パルス6      0     0    0  ..  0       0   0   0    .. 0
    パルス7      P21   P22  P23 ..P26      P27 P28 P29  .. P212

    :param: array_name   リスト pulse_train_array,pulse_width_array,pulse_name_array
    :return:    リスト　変換後のpulse_train_array,pulse_width_array,pulse_name_array
    """
    global pulse_disp_num
    pulse_disp_num = len(array_name) - 1
    array_num = len(array_name) - 1
    array_prov = []  # 編集用の配列
    n = 0
    row_0 = [0] * len(array_name[0])  # 7種類に足りないリストを0で埋める　*_trainは12個、*_width、*_numは6個の0データ
    while n < array_num:  # n<パルス種類数-1なので、パルス種類の最後のパルデータの1つ前までリストに追加していく
        array_prov.append(array_name[n])
        n += 1
    while n < 6:  # パルス種類　最大7種類の1種類手前まで、つまり6種類目までを0データのリストで埋める
        array_prov.append(row_0)
        n += 1
    array_prov.append(array_name[array_num])  # パルス種類7番目のデータは、もともとの最後のパルス種類データを追加する。
    return array_prov


# ---------------- ~ train_sort() -------------------------

# --------------- train_conv() ----------------------------
def train_conv():  # パルス列を記号に変換
    """
    initial_train.xlsxを読込んだリストの値を、パルス列設定windowに表示する記号に変換する
    NP/--,NP/NP,...とか

    :return:
    """
    for y, row in enumerate(pulse_train_array, 0):  # リストpulse_train_arrayから、インデックス初期値を0としyに、値をrowに取り込む
        for x, col in enumerate(row):  # b7_b6_b5_b4_b3_b2_b1_b0(b7-b6:A相検出、b5-b4:B相検出、b3-b2:A相OUT、b1-b0:B相OUT)
            aph1 = (int(str(col), 2) >> 2) & 0b11  # ①　文字列を2進数として読み込んでビット取り出し A相OUT
            aph2 = (int(str(col), 2) >> 6) & 0b11  # ②　A相検出
            bph1 = (int(str(col), 2) >> 0) & 0b11  # ③　B相OUT
            bph2 = (int(str(col), 2) >> 4) & 0b11  # ④　B相検出
            """
            (例) initial_train.xls 
                            A1        B1          C1          D1          E1          F1          A2 B2 C2 D2 E2 F2                
            y=0の時のrowの値 00001000  00001010    01000010    00000110    01000000    00000000    .................         
                            ↓           ↓           ↓           ↓           ↓          ...........................                         
                           x=0のcol  x=1のcol     x=2のcol     x=3のcol     x=4のcol     ...........................
            ①　2進数として数値化すると、0b1000　2bit右シフトで&0b11するとaph1=0b10
            ②　2進数として数値化すると、0b1000　6bit右シフトで&0b11するとaph2=0b00
            ③　2進数として数値化すると、0b1000　0bit右シフトで&0b11するとbph1=0b00
            ④　2進数として数値化すると、0b1000　4bit右シフトで&0b11するとbph2=0b00
            下の条件式を処理すると、
            aph="NP"
            bph="--"            
            """
            if aph1 == 0b01:
                aph = "RP"
            elif aph1 == 0b10:
                aph = "NP"
            else:
                aph = "--"
            if aph2 == 0b01:
                aph = "rd"
            elif aph2 == 0b10:
                aph = "nd"
            elif aph2 == 0b11:
                aph = "wd"

            if bph1 == 0b01:
                bph = "RP"
            elif bph1 == 0b10:
                bph = "NP"
            else:
                bph = "--"
            if bph2 == 0b01:
                bph = "rd"
            elif bph2 == 0b10:
                bph = "nd"
            elif bph2 == 0b11:
                bph = "wd"

            pulse_train_array_str[y][x] = aph + "/" + bph
    # print(pulse_train_array_str)


# ---------------- ~ train_conv() -------------------------

# ----------------- train_reading() -----------------------
def train_reading(readfile):
    """
    Excel file('***train')のsenddataシートの値を読み込み、各項目をリスト化する。
    例外処理（ファイル無し、読み込みエラー）有り

    :param readfile: initial_train.xlsxファイルのフルパス
    :return:
    """
    global pulse_train_array  # Excel　P0_Tr～Pr_trをrow、A1～F2をcolデータとする
    global pulse_width_array  # Excel　P0_wd～Pr_wdをrow、A1～F1をcolデータとする
    global pulse_num_array  # Excel　P0_wd～Pr_wdをrow、A2～F2をcolデータとする
    global pulse_train_name  # Excel　P0_wd～Pr_wdをrow、typeをcolデータとする
    global vrsdt_array
    global vrsjdg_array

    try:
        df_tr_raw = pd.read_excel(str(readfile), index_col=0)  # 第1引数：ファイルパスreadfileで可、第2引数:インデックスにする列
        print(df_tr_raw)
        # print('test:'+ df_tr_raw.index)
        # print( True in df_tr_raw.index.isin(['Dt区間']))
        """
        例
                type    A1      B1  ...F1   A2      B2  ...F2
        P0_tr   name1   d1      d2  ...d6   d7      d8  ...d12
        P1_tr   name2   d11     d22 ...d66  d77     d88 ...d122
        .
        .
        .
        pr_tr   name7   d111    d222...d666 d777    d888...d1222
        である場合、
        
        以下の処理で上記Dataframeをlistに変換する
        pulse_train_array = [[d1,d2,...d6,d7,d8,...d12],[d11,d22,...d66,d77,d88,...d122],...,[d111,d222...d666,d777,d888,...d1222]]
        
        """

        pulse_train_array = df_tr_raw.loc['P0_tr':'Pr_tr', 'A1':'F2'].astype(
            int).values.tolist()  # Dataframeをlistに変換 すべてintに型変換
        pulse_width_array = df_tr_raw.loc['P0_wd':'Pr_wd', 'A1':'F1'].astype(
            int).values.tolist()  # Dataframeをlistに変換 すべてintに型変換
        pulse_num_array = df_tr_raw.loc['P0_wd':'Pr_wd', 'A2':'F2'].astype(
            int).values.tolist()  # Dataframeをlistに変換 すべてintに型変換
        pulse_train_name = df_tr_raw.loc['P0_tr':'Pr_tr', 'type'].astype(
            str).values.tolist()  # Dataframeをlistに変換　すべてstrに型変換

        # GUI上は7種類のパルスを設定出来るが、6種類以下の場合は、リストデータを0で補い、パルス種類7種類となるように補正する。
        pulse_train_array = train_sort(pulse_train_array)
        pulse_width_array = train_sort(pulse_width_array)
        pulse_num_array = train_sort(pulse_num_array)

        n = len(pulse_train_name) - 1
        while n < 6:
            pulse_train_name.insert(n, '設定なし')  # GUI上7種類のパルス種別を設定できるが、6種類以下の場合、train_nameに'設定なし'を挿入していく
            n += 1  # 例えば、3種類のパルス種の場合、2番目と3番目の間に'設定なし'を挿入し、3番目のパルス種類名を7番目にする

        if True in df_tr_raw.index.isin(['Dt区間']):  # index_col=0で指定された列に'Dt区間'があればTrueを返す
            vrsdt_array = df_tr_raw.loc['Dt区間', 'type':'C1'].astype(
                int).values.tolist()  # 行：'Dt区間'、列：'type'～'C1'までの値をintでcastし、リストに追加
            vrsjdg_array = (df_tr_raw.loc['patA', 'type':'A2'].astype(
                int).values.tolist()  # 行：'patA'、列：’type’～’A2’までの値をintでcastし、リストに追加
                            + df_tr_raw.loc['patB', 'type':'A2'].astype(
                        int).values.tolist())  # 行：'patB'、列：’type’～’A2’までの値をintでcastし、リストに追加
            # vrsWindow()

            if 'vrsWindow' in globals():  # vrsウィンドウが開かれたことがあるか? あればglobal名前空間に変数'vrsWindow'がある。
                if vrsWindow.winfo_exists() == 1:  # vrsウィンドウが開かれているか？
                    vrsWindow.destroy()  # vrwWidowを閉じる
                    vrs_window()  # 新たにwindowを開く

        # print(pulse_train_name)
        # print(pulse_train_array)
        # print(pulse_width_array)

    except(FileNotFoundError, TypeError):
        tkinter.messagebox.showerror('エラー', 'train.xlsxファイルが見つかりません')
    except:
        tkinter.messagebox.showerror('エラー', 'train.xlsxファイル読み込みに失敗しました')


# ----------------- ~ train_reading ------------------------
def train_setting():
    """
    mainウインドウのパルス列設定ボタン押下で表示されるパルス列設定ウインドウの設定読込ボタンを押下で実行されるpulse_train_bot()内で
    生成されるスレッド処理
    :return:
    """
    # global  filepath
    filepath = filepath_get('train', 0)     # 'tarin'を含む、1ファイルのパスを取得する

    trainWindow.lift()  # パルス列設定windowをtopへ
    train_reading(filepath)     # 上記で取得したfilepathのエクセルファイルを読込む

    for y, row in enumerate(pulse_train_labename, 0):   # pulse_train_lebname:パルス設定ウインドウのラベルウィジェット
        row.set(pulse_train_name[y])        # ラベルウィジェットにpulse_train_name[y]の値をセットする

    train_conv()        # 読込んだtrainデータをパルス設定ウインドウにラベルとして（NP/--,NP/NP,...とか）表示する値に変換する
    # print('check')
    insert_train()      #　パルス列設定ウインドウのラベル表示　NP/--　NP/NP・・・等を動的に変える
    # print('check2')

    insert_entry(pulse_wid_name, pulse_width_array)  # メインウインドウの<pulse幅[us]/本数>のpulse幅Entryに書き込み
    insert_entry(pulse_num_name, pulse_num_array)  # メインウインドウの<pulse幅[us]/本数>の本数Entryに書き込み

    pulse_width_set()  # パルス幅設定送信   Nucleoへ
    pulse_train_set()  # パルス列設定送信   Nucleoへ

    Button8_1.config(state="normal")  # ボタン有効化

# スクリーンショット#############
def screen_shot(handle1, handle2, fname):
    """
    パラメータにより、同じ名称の関数を選択
    seqウインドウかmainウインドウのイメージ（スクリーンショット)読み取り処理
    :param handle1:
    :param handle2:
    :param fname:
    :return:
    """
    # 最前面のウィンドウのスクショを取得する
    # handle = win32gui.GetForegroundWindow() # 最前面のウィンドウハンドルを取得
    rect1 = win32gui.GetWindowRect(handle1)  # ウィンドウの位置を取得
    rect2 = win32gui.GetWindowRect(handle2)  # ウィンドウの位置を取得
    im1 = ImageGrab.grab().crop(rect1)
    im2 = ImageGrab.grab().crop(rect2)


def screen_shot(handle):
    """
    seqウインドウかmainウインドウのイメージ（スクリーンショット)読み取り処理
    :param handle:
    :return:
    """
    # handle = win32gui.GetForegroundWindow() # 最前面のウィンドウハンドルを取得
    rect = win32gui.GetWindowRect(handle)  # ウィンドウの位置を取得
    im = ImageGrab.grab().crop(rect)        # イメージの取得
    return im


def concat_img(im1, im2, fname):  # 画像の結合
    """
    イメージファイルの結合を実施し、ファイル名を指定して保存する
    :param im1:
    :param im2:
    :param fname:
    :return:
    """
    color = (0, 0, 0)
    dst = Image.new('RGB', (im1.width + im2.width, max(im1.height, im2.height)), color)
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    dst.save('Output/' + fname + '.jpg')


def get_handle():
    """
    ウインドウハンドル（識別情報）を取得する
    :return:
    """
    handle = win32gui.GetForegroundWindow()  # 最前面のウィンドウハンドルを取得
    return handle


# カメラ関係サブルーチン##################
def find_cam():
    """
    システムに接続されているカメラを検出し、そのデバイスIDを決める
    :return:
    """
    global cam_list
    cam_list = []
    for camera_number in range(0, 10):  # 1台のみだとカメラのデバイスIDは'0'
        capture = cv2.VideoCapture(camera_number, cv2.CAP_DSHOW)  # Direct Showでカメラの設定変更を簡単にできるようになる
        ret, frame = capture.read()  # 画像取り込み、retには成功か失敗かが入り、frameに画像データが取り込まれる。

        if ret is True:
            cam_list.append(camera_number)  # 画像取り込みが成功したcamera_numberをリストに追加
    print(cam_list)
    cam_no = int(max(cam_list))  # リストの最大値のカメラデバイスIDをcam_noとする


def disp_cam(event):
    """
    カメラウインドウ内のカメラ接続ボタン左クリック操作でコールされるカメラ操作処理
    撮影、オートフォーカス、フォーカス設定等
    :param event:
    :return:
    """
    global capture
    global cap_size
    global windowsize
    global focus
    cam_no = int(cbcam.get()[0])
    capture = cv2.VideoCapture(cam_no, cv2.CAP_DSHOW)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, 10000)  # カメラの最大解像度に設定
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 10000)  # カメラの最大解像度に設定
    ret, frame = capture.read()

    cap_size = []
    cap_size.append(capture.get(cv2.CAP_PROP_FRAME_WIDTH))  # 設定された解像度取得
    cap_size.append(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))  # 設定された解像度取得
    cap_size.append(cap_size[1] / cap_size[0])

    windowsize = (700, int(700 * cap_size[2]))  # 画像の縦横比は維持して幅を800に
    frame = cv2.resize(frame, windowsize)
    cv2.imshow('cam', frame)
    cv2.moveWindow('cam', int(xposi), int(yposi) + 100)

    # focus = 500#固定フォーカスの初期値
    # capture.set(cv2.CAP_PROP_AUTOFOCUS,1)#オートフォーカス ON
    if focus != 500:
        cam_focus_set(focus)

    while (True):
        ret, frame = capture.read()
        # resize the window
        # windowsize = (800, int(800*cap_size[2]))
        frame = cv2.resize(frame, windowsize)
        cv2.imshow('cam', frame)

        key = cv2.waitKey(1)  # キー入力1msec待ち
        if key == ord('q'):
            break
        elif key == ord('0'):
            cam_get_img(0)
        elif key == ord('1'):
            cam_get_img(1)
        elif key == ord('m'):
            manual_pulse_out(0, 0)
        elif key == ord('f'):
            focus = focus - 10
            if focus < 1:
                focus = 0
            cam_focus_set(focus)
        elif key == ord('n'):
            focus = focus + 10
            if focus > 1000:
                focus = 1000
            cam_focus_set(focus)
        elif key == ord('a'):
            capture.set(cv2.CAP_PROP_AUTOFOCUS, 1)  # オートフォーカス ON

    capture.release()
    cv2.destroyAllWindows()


def cam_focus_set(focus):
    """
    フォーカス値によるフォーカス設定
    :param focus:
    :return:
    """
    print('\r' + 'focus val ', focus, end='')  # フォーカス値を重ね書き
    capture.set(cv2.CAP_PROP_AUTOFOCUS, 0)  # オートフォーカス OFF
    capture.set(cv2.CAP_PROP_FOCUS, focus)  # focus位置セット
    # https://docs.opencv.org/master/d4/d15/group__videoio__flags__base.html#ggaeb8dd9c89c10a5c63c139bf7c4f5704dad937a854bd8d1ca73edfb3570e799aa3


def cam_get_img(pulseno):
    """
    pulseno: 0=正転、1=逆転を指定して撮影開始
    :param pulseno:
    :return:
    """
    if Com_No == 'Nucleo未接続':
        tkinter.messagebox.showerror('エラー', 'Nucleoが接続されていません')
    else:
        delay = int(Boxcam_4.get()) / 1000      # 撮影ディレイ
        rept = int(Boxcam_5.get())              # 撮影ステップ数
        name = str(Boxcam_6.get())              # ファイル名

        now = datetime.datetime.now()
        dirpath = os.getcwd()  # os.path.dirname(__file__)
        folder = '/image/' + name + '_' + now.strftime('%y%m%d_%H%M%S')
        os.makedirs(dirpath + folder)
        print('保存先 ' + dirpath + folder)

        n = 0
        ret, frame = capture.read()
        cv2.imwrite(dirpath + folder + '/' + name + '-P' + str(pulseno) + '_' + str(n).zfill(3) + '.jpg', frame)

        time_st = time.time()
        delay_result = []
        capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # バッファサイズを1に設定。遅延を緩和する？
        # capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        while n < rept:
            manual_pulse_out(pulseno, 0)
            time_rep = time.time()
            while (True):
                ret, frame = capture.read()
                key = cv2.waitKey(1)  # キー入力1msec待ち
                if key == ord('q'):
                    n = rept
                    break
                if time.time() - time_rep > delay:
                    ret, frame = capture.read()
                    delay_result.append(time.time() - time_rep)
                    break
            cv2.imwrite(dirpath + folder + '/' + name + '-P' + str(pulseno) + '_' + str(n + 1).zfill(3) + '.jpg', frame)
            frame = cv2.resize(frame, windowsize)  # 画面表示更新用
            cv2.imshow('cam', frame)
            n += 1
        time_total = time.time() - time_st
        print('delay時間 Max:' + str(format(max(delay_result), '.3f')) + 's/ Min:' + str(
            format(min(delay_result), '.3f')) + 's')
        print('測定時間 Total' + str(format(time_total, '.2f')) + 's')

# 2023.1.11
#################################################
####　フォトインタラプタ関係サブルーチン　#######

def photo_result(response, no):
    """

    :param response:
    :param no:
    :return:
    """
    if ('result OK' in response):
        # if(alf_flag == 1):
        #    piresult[no].set('alf OK')
        if ('Posi=' in response):
            piresult[no].set(response.replace(' result ', '').replace('Posi=', ''))
        elif ('result OK' in response):
            piresult[no].set('OK')
    elif ('result NG' in response):
        # piresult[no].set(response.replace('result ',''))
        piresult[no].set('NG')


def photo_init_w(offset_num):  # フォト設定書込み
    """

    :param offset_num:
    :return:
    """
    ser.write(b't')  # シリアル通信:送信
    # ser.flush()#コマンド送信完了するまで待機
    time.sleep(wait_uart)
    ser.write(bytes(piset_name[0].get()[0], 'utf-8'))
    read_serial()
    read_serial()
    ser.write(bytes(piset_name[2].get(), 'utf-8'))
    ser.write(b'\r')
    read_serial()
    ser.write(bytes(piset_name[3].get(), 'utf-8'))
    ser.write(b'\r')
    read_serial()
    ser.write(bytes(piset_name[1].get(), 'utf-8'))
    ser.write(b'\r')
    read_serial()
    ser.write(bytes(piset_name[4].get()[0], 'utf-8'))
    ser.write(b'\r')
    read_serial()
    # ser.write(bytes(piset_name[5].get(),'utf-8'))
    pioffset_array = piset_name[5].get().strip().split(',')
    if int(pioffset_array[offset_num]) < 0:
        pioffset_array[offset_num] = str(int(piset_name[1].get()) + int(pioffset_array[offset_num]))
    ser.write(bytes(pioffset_array[offset_num], 'utf-8'))
    ser.write(b'\r')
    read_serial()


def photo_init():  # フォトインタラプタ初期設定
    """

    :return:
    """
    piresult[0].set('実施中')
    piresult[1].set('-----')
    piresult[2].set('-----')

    photo_init_w(0)
    pitxt_res.delete('1.0', 'end')
    ser.write(b'w')  # シリアル通信:送信
    while 1:
        resp_str = read_serial2()
        pitxt_res.insert('end', resp_str + '\n')
        pitxt_res.see("end")
        if ('result' in resp_str):
            break
    photo_result(resp_str, 0)
    while 1:
        resp_str = read_serial2()
        pitxt_res.insert('end', resp_str + '\n')
        pitxt_res.see("end")
        if ('End!' in resp_str):
            break
    Buttonpi_1.config(state="normal")  # ボタン有効化


def photo_posiset_manu():
    """

    :return:
    """
    photo_init_w(0)
    photo_posiset()


def photo_posiset():
    """

    :return:
    """
    piresult[1].set('実施中')
    piresult[2].set('-----')
    ser.write(b'e')  # シリアル通信:送信
    # ser.flush()#コマンド送信完了するまで待機
    time.sleep(wait_uart)
    while 1:
        resp_str = read_serial2()
        if ('result' in resp_str):
            break
    photo_result(resp_str, 1)
    while 1:
        resp_str = read_serial2()
        if ('End!' in resp_str):
            break
    Buttonpi_2.config(state="normal")  # ボタン有効化


def photo_posicheck():
    """

    :return:
    """
    piresult[2].set('実施中')
    ser.write(b'r')  # シリアル通信:送信
    # ser.flush()#コマンド送信完了するまで待機
    time.sleep(wait_uart)
    while 1:
        resp_str = read_serial2()
        if ('result' in resp_str):
            break
    photo_result(resp_str, 2)
    while 1:
        resp_str = read_serial2()
        pitxt_res.insert('end', resp_str + '\n')
        pitxt_res.see("end")
        if ('End!' in resp_str):
            break
    Buttonpi_3.config(state="normal")  # ボタン有効化


def photo_seq_init():
    """

    :return:
    """
    pi_window()
    piresult[0].set('未実施')
    piresult[1].set('未実施')
    piresult[2].set('-----')
    photo_init()
    if piresult[0].get() != 'OK':
        piseq_res.insert('end', "PI初期化 失敗\n")  # 最終に追加
        Buttonpi2_1.config(state="normal")  # ボタン有効化


def photo_seq_set(flag, cnt, test_cnt):
    """

    :param flag:
    :param cnt:
    :param test_cnt:
    :return:
    """
    if flag == 0:
        photo_posiset()
        if piresult[1].get() != 'OK':
            piseq_res.insert('end', " 位置セット")
            Buttonpi2_1.config(state="normal")  # ボタン有効化
            result_data[cnt + 4][0] = str('{:.2f}'.format(vm_test))  # ファイル書込み用
            result_data[cnt + 4][test_cnt + 1] = " 位置セットNG"  # ファイル書込み用
        else:
            flag = 1
    return flag


def photo_seq_check(cnt, test_cnt):
    """

    :param cnt:
    :param test_cnt:
    :return:
    """
    flag = 1
    photo_posicheck()

    if 'OK' in piresult[2].get():
        piseq_res.insert('end', ' ' + piresult[2].get())
    else:
        piseq_res.insert('end', " NG")
        if seq_jdge_array[2].get() == 1:
            flag = 2
        else:
            flag = 0
    return flag

    '''
    if piresult[2].get() != 'OK':
        piseq_res.insert('end', " NG")
        if seq_jdge_array[2].get() == 1:
            flag = 2
        else:
            flag = 0
    elif piresult[2].get() == 'OK':
        piseq_res.insert('end', " OK")
    return flag
    '''


def photo_seqtest_stop():
    """

    :return:
    """
    global seq_runopt
    seq_runopt = int(2)


def num_judg(readstr):
    """

    :param readstr:
    :return:
    """
    return readstr.replace('.', '').isnumeric()


##########################
####Vrs検出関係
def vrstext_clear():
    """

    :return:
    """
    for x, col in enumerate(vrsres_name):
        vrsres_name[x].delete('1.0', 'end')


def vrstext_save_manu():
    """

    :return:
    """
    vrstext_save(0, 'a')


def vrstext_save(mode, write):
    """

    :param mode:
    :param write:
    :return:
    """
    read_vrs = []
    max_time = []
    for i in range(3):
        read_raw0 = (vrsres_name[3 - i].get('1.0', 'end-1c').replace(',', '/')).splitlines()  # カンマをスラッシュに変更して読み取り
    read_raw0 = [read_raw0[i].split(' | ') for i in range(len(read_raw0))]  # |で区切って2次元配列
    for i in range(3):
        # read_raw = (vrsres_name[3-i].get('1.0', 'end-1c').replace(',','/')).splitlines()#カンマをスラッシュに変更して読み取り
        read_raw = [row[i] for row in read_raw0]
        read_raw[0:0] = ['', '', '']  # 3個の空白追加
        read_vrs.append(read_raw)
    print(read_vrs)
    for y, row in enumerate(read_vrs):
        if y == 2:
            for x, col in enumerate(row):
                if x > 2:  # 3列は空白
                    if '/' in col:
                        max_time.append(max(map(int, col.split('/'))))
                    else:
                        max_time.append('')
            max_time[0:0] = ['', '', '']  # 3個の空白追加
            read_vrs.append(max_time)

    folder = 'Output'
    fname = 'detail_' + entryvrs_1.get().replace('file name', '')
    fname = re.sub(r'[\\|/|:|?|.|"|<|>|\|]', '_', fname)  # ファイル名に使えない文字列を置換
    if 'entrypi2_3' in globals():
        if entrypi2_3.winfo_exists() == 1:  # wedgetが存在するか？
            fname = fname + entrypi2_3.get().replace('file name', '')
            fname = re.sub(r'[\\|/|:|?|.|"|<|>|\|]', '_', fname)  # ファイル名に使えない文字列を置換
            if mode > 0:  # シーケンスでの詳細保存の場合
                fname = fname + 'temp'
    now = datetime.datetime.now()
    path_name = os.getcwd() + '/' + folder + '/' + now.strftime('%y%m%d_') + fname + '.csv'
    # if mode < 2:
    with open(path_name, write, newline="") as f:
        writer = csv.writer(f)
        writer.writerows(read_vrs)
        # elif mode == 2:#シーケンス途中終了の場合
    #    os.remove(path_name)


def vrs_jdge_res(time_array, vrs_steps):
    """

    :param time_array:
    :param vrs_steps:
    :return:
    """
    vrs_pat = 0
    vrs_pat_cnt = [0, 0, 0, 0]
    for x, col in enumerate(time_array):
        if num_judg(col):  # 値が全て数字だったら
            for n in range(1, 5):
                if int(col) < int(vrsdt_name[n - 1].get()):
                    vrs_pat = vrs_pat | (0b1000 >> n - 1)
                    vrs_pat_cnt[n - 1] += 1
                    break
    vrs_print(time_array, vrs_pat, vrs_pat_cnt, vrs_steps)
    if vrsjdg_name[vrs_pat].get() == 'OK':
        return 0, vrs_pat_cnt
    else:
        return 1, vrs_pat_cnt


def vrsng_phoffset():  # vrsNG位置をフォトオフセットへコピーする
    """

    :return:
    """
    sequence_window()
    send_posi = []
    for i in range(len(vrsng_posi)):  # vrsNG位置から、既定ステップを引く
        if i == 0:
            send_posi.append(vrsng_posi[i] + int(entryvrs_2.get()))
        elif (vrsng_posi[i] - vrsng_posi[i - 1]) > 2:  # ステップ差が2より大きい場合に位置を送る
            send_posi.append(vrsng_posi[i] + int(entryvrs_2.get()))
    piset_name[5].delete(0, tkinter.END)
    piset_name[5].insert('end', ",".join(map(str, send_posi)))  # listをカンマを追加して書込み


def vrs_print(time, pat, pat_cnt, vrs_steps):
    """

    :param time:
    :param pat:
    :param pat_cnt:
    :param vrs_steps:
    :return:
    """
    global df_vrs_res  # Vrs判定結果保存用df
    global vrs_step_bf
    global vrsng_posi
    timing_str = ','.join(time)  # 配列を結合
    patcnt_str = ''.join(map(str, pat_cnt))  # 文字列に変換してから結合
    vrsres_name[1].insert('end', str(vrs_steps).zfill(3) + ' ')
    vrsres_name[1].insert('end', vrsjdg_name[pat].get() + ' | ')  # パターン判定と合致する文字を入力
    vrsres_name[1].insert('end', patcnt_str + ' | ')
    vrsres_name[1].insert('end', timing_str + '\n')
    if vrs_steps == 1:  # 1step目に前回NG位置をゼロクリア
        vrs_step_bf = 0
        vrsng_posi = []
    if 'NG' in vrsjdg_name[pat].get():
        if vrs_step_bf == 0:  # 最初のNG位置だった場合
            vrs_step_def = 0
        else:
            vrs_step_def = vrs_steps - vrs_step_bf
        vrsng_posi.append(vrs_steps)
        vrsres_name[2].insert('end', str(vrs_steps).zfill(3) + ' | ')  # step数記載
        vrsres_name[2].insert('end', str(vrs_step_def).zfill(3) + '\n')
        vrs_step_bf = vrs_steps
        # vrsres_name[2].insert('end', vrsjdg_name[pat].get()+'\n')
    # vrsres_name[2].insert('end', format(pat,'03b')+'\n')
    # vrsres_name[2].insert('end', patcnt_str+'\n')
    # vrsres_name[3].insert('end', str(vrs_steps).zfill(3)+' ')#step数記載
    # vrsres_name[3].insert('end', vrsjdg_name[pat].get()+'\n')
    df_vrs_res[vrs_steps] = vrsjdg_name[pat].get()
    for x, col in enumerate(vrsres_name):  # 最終行を表示
        vrsres_name[x].see("end")


def vrstime_print():
    """

    :return:
    """
    while 1:  # 測定中フリーズ対策　測定中に他アプリ操作などで停止することがあったため修正
        vrs_res = read_serial2()
        if ('End!' in vrs_res):
            break
    vrs_steps = 1
    vrs_ng = 0
    pat_sum = [0, 0, 0, 0]
    if 'vrsWindow' in globals():  # vrsウィンドウが開かれたことがあるか?
        if vrsWindow.winfo_exists() == 1:  # vrsウィンドウが開かれているか？#Vrs有効になっているか
            if vrs_res.find(',' + str(1) + ',') != -1:
                for x in range(1, 4):  # テキストクリア
                    vrsres_name[x].delete('1.0', 'end')
                    df_vrs_res[:0]  # dfを空にする
                while 1:
                    n = 0
                    vrs_list = []
                    vrs_list_1d = []
                    while n < 4:  # (,1,)の文字列を探す
                        start_no = vrs_res.find(',' + str(n + 1) + ',')  # 文字列に含まれる任意の文字の位置を探す
                        if n < 3:
                            stop_no = vrs_res.find(',' + str(n + 2) + ',')
                        elif n == 3:
                            stop_no = vrs_res.find(',' + str(1) + ',')
                            if stop_no == -1:
                                stop_no = vrs_res.find('End')
                        ins_str = vrs_res[start_no + 1:stop_no]
                        # vrsres_name[n].insert('end', ins_str+'\n')
                        # vrsres_name[n].see("end")
                        vrs_res = vrs_res[stop_no:]  # stop no以降の文字列のみ取り出す
                        n += 1
                        vrs_list.append(ins_str[2:].split(','))  # カンマ区切りでリスト化
                    vrs_list_1d = list(itertools.chain.from_iterable(vrs_list))  # 2次元配列を1次元に
                    vrs_list_1d = [a for a in vrs_list_1d if a != '']  # 空の要素を削除

                    # print(vrs_list_1d)
                    # vrsres_name[3].insert('end', str(vrs_steps).zfill(3)+' ')#step数記載

                    pat_res, pat_cnt = vrs_jdge_res(vrs_list_1d, vrs_steps)
                    pat_sum = list(map(sum, zip(pat_sum, pat_cnt)))

                    if pat_res == 1:
                        vrs_ng += 1

                    if vrs_res.find(',' + str(1) + ',') == -1:
                        pat_avg = [round(x / vrs_steps, 1) for x in pat_sum]  # 平均計算
                        pat_avg_str = '/'.join(map(str, pat_avg))  # 文字列に変換してから結合
                        vrsres_name[0].insert('end', Box4_4.get() + ' ')  # 電圧書込み
                        if vrs_ng == 0:  # 全ての判定結果を左のBoxに書込み
                            vrsres_name[0].insert('end', 'OK ')
                        else:
                            vrsres_name[0].insert('end', 'NG' + str(vrs_ng))
                        vrsres_name[0].insert('end', ' ' + pat_avg_str + '\n')
                        # print(item for item in df_vrs_res.columns if item.find('NG') != -1)
                        break

                    vrs_steps += 1


# ---------------------------------------------------------------------
# ------------------- read_serial() -----------------------
def read_serial():
    """
    Nucleoとのシリアル通信読み込み処理 1

    :return:
    """
    # time.sleep(wait_uart)
    # ser.flush()#コマンド送信完了するまで待機

    line = ser.readline().rstrip()  # シリアル1行読み込み　空白、タブ、改行コード除去
    line = line.decode()  # bytes型からstr型に変換
    print(line)  # 読み込んだ文字列を表示


# ------------------- ~ read_serial() ----------------------

def read_serial2():
    """
    Nucleoとのシリアル通信読み込み処理 2
    読み込み時の警告があった場合の処理機能付き
    :return:
    """
    # time.sleep(wait_uart)
    # ser.flush()#コマンド送信完了するまで待機
    time.sleep(wait_uart)  # wait_uart(sec)のsleepで通信時の動作ウエイト
    '''
    while 1:    #シリアル通信の受信待ちループ
        line = ser.read(1)#シリアル読み込み1文字
        if len(line) == 1:
            line = line + ser.readline().rstrip()#シリアル読み込み　改行コード除去
            line = line.decode()#bytes型からstr型に変換
            break
        else:
            if stop_en.get() ==1:
                break
    '''
    line = ser.readline().rstrip()  # シリアル読み込み　改行コード除去
    line = line.decode()  # bytes型からstr型に変換

    if 'al-' in line:
        read_alert(line)

    print(line)
    return line


def get_winposition():
    """
    メインウインドウの座標を取得し,ｘ座標：メインウィンドウの右横、ｙ座標：メインウインドウより上に30
    の座標を返す
    :return:
    """
    global xposi
    global yposi
    xposi = tk.winfo_rootx() + tk.winfo_width()  # メインウインドウのディスプレー左上原点のx座標+メインウィンドウの幅
    yposi = tk.winfo_rooty() - 30  # メインウインドウのディスプレー左上原点のy座標-30 30:ウインドウのタイトル部のyサイズ


def read_alert(str_al):
    """

    :param str_al:
    :return:
    """
    global alertwindow
    if 'mV' in str_al:
        return
    # 複数開かないようにする処理
    if 'alertwindow' in globals():  # piWindowが定義されているか？
        if alertwindow.winfo_exists() == 1:  # windowが存在するか？
            # alertwindow.attributes('-topmost', 1)#トップに固定表示
            # alertwindow.attributes('-topmost', 0)#固定解除
            alertwindow.destroy()
    alertwindow = tkinter.Toplevel(tk)
    alertwindow.title('注意！')
    alertwindow.geometry('300x40+20+20')
    if 'al-f' in str_al:
        freq_max = str_al.replace('al-f', '').replace('sequence', '').replace('End', '')
        freq_max = freq_max.split(',')  # 周波数値だけ取り出し
        alert_lab = tkinter.Label(alertwindow, text=('周波数' + freq_max[0] + '駆動しています'), font=('', 12))

    alert_lab.pack(anchor='center', expand=1)
    alertwindow.after(2000, lambda: alertwindow.destroy())


# 5. Pulse設定配列、GUI表示変数定義より、処理がこの場所へ移る。
# --------------- 6. initial設定読み込み ----------------------------
dirpath = os.getcwd()  # カレントディレクトリ取得
filepath = dirpath + "/" + "initial_train.xlsx"
print(filepath)
train_reading(filepath)  # 初期パルス設定読み込み initial_train.xlsxの読み込み
train_conv()  # パルスを記号に変換 （NP/--,NP/NPとか）

# メインウインドウのサイズ設定
win_tate = pulse_disp_num * 25 + 500  # windowの縦サイズを設定

tk.title(Software_name)  # windowのタイトル設定
tk.geometry("500x" + str(win_tate) + "+20+20")  # windowサイズ横500×win_tate+xオフセット座標+yオフセット座標(左上原点の横に20px、縦に20px)


# ------------ ~ 6. initial設定読み込み -------------------------------
# 7. COMポート設定に処理が移る
###############
####GUI設定#####
# シーケンス機能window作成
def sequence_window():
    """
    mainウインドウでシーケンス機能ボタンを押下した際に開くウィンドウの設定＆表示処理
    :return:
    """
    global seqWindow

    # 複数開かないようにする処理
    if 'seqWindow' in globals():  # Windowが定義されているか？  global名前空間にあるシンボルの中にseqWindowが有れば、開かれている。
        if seqWindow.winfo_exists() == 1:  # windowが存在するか？　ここでもseqWindowが存在するか否か確認している 存在しているならreturn
            seqWindow.attributes('-topmost', 1)  # seqWindowをトップに固定表示 次の行で解除しないと常に最前面に固定表示される
            seqWindow.attributes('-topmost', 0)  # 固定解除
            return
    global main_handle
    tk.attributes('-topmost', 1)  # メイン画面をトップに固定表示
    tk.attributes('-topmost', 0)  # メイン画面の固定解除
    main_handle = get_handle()  # 最前面のウィンドウ(main_window)のHandle取得

    get_winposition()  # メインwindowの右横位置の座標取得（y座標は30だけ上　ウインドウのタイトル部分のyサイズを引いてある）
    seqWindow = tkinter.Toplevel(tk)  # seqWindowをメインウインドウのサブウインドウとして作成（メインウインドウを閉じるとサブも閉じる)
    seqWindow.geometry('+' + str(xposi) + '+' + str(yposi))  # seqWindowの座標指定 メインウインドウの右横に表示する

    frameseq = tkinter.Frame(seqWindow, pady=10, padx=10)  # <シーケンス設定>の項目用にframeをseqWindowに作成
    frameseq.pack(anchor=tkinter.W)  # フレームを配置表示 左寄せ指示

    Labelseq_1 = tkinter.Label(frameseq, text='<シーケンス設定>', width=labewid_1, anchor='w')  # <シーケンス設定>ラベルの作成
    Labelseq_1.grid(row=0, column=0, columnspan=4, sticky=tkinter.W)  # <シーケンス設定>ラベルの配置、左寄せ、column４つを結合

    # ラベル配置
    labelpi2_name = ['Start', 'Stop', 'step']  # ラベルnameをリストで作成
    for x, row in enumerate(labelpi2_name, 0):  # 0番目(x=0)からリストの要素を取り出す
        labelpi_N = tkinter.Label(frameseq, text=row, width=5, anchor='w')  # ラベル作成
        labelpi_N.grid(column=x + 1, row=2, columnspan=1, sticky=tkinter.W)  # ラベルの配置 インデックスを使い、columnを移動

    # ラベル配置
    labelpi3_name = ['電圧範囲[V]', 'Pulse幅比率', '周波数[Hz]', '評価パルス']  # ラベルnameをリストで作成
    for x, row in enumerate(labelpi3_name, 0):  # 0番目（x=0)からリストの要素を取り出す
        labelpi_N = tkinter.Label(frameseq, text=row, width=10, anchor='w')  # ラベル作成 左に配置
        if x < 3:
            labelpi_N.grid(column=0, row=4 + x, sticky=tkinter.W)  # '電圧範囲'～'周波数'まで、4,5,6行に配置

    for y, row in enumerate(piset_value_name, 0):  # 0番目（x=0)からpiset_value_nameリストの要素を取り出す
        for x, col in enumerate(row):  # 上記で取り出した要素（これもリスト）からcolに要素を取り出す
            col = 'psvname' + str(y) + str(
                x)  # しかし、上記colに要素を取り出してもここで、'psyname'+str(y)+str(x)で書き換えられる。ここはリストに追加したかったのか？

    for y, row in enumerate(piset_value_array, 0):  # 0番目（x=0)からpiset_value_arrayリストの要素を取り出す
        for x, col in enumerate(row):  # 上記で取り出した要素（これもリスト）からcolに要素を取り出す
            if y == 3:  # piset_value_aaray: [[2.4, 1.2, 0.1], [1.0, 1.0, 0.1], [200, 200, 20], ['1']]
                piset_value_name[y][x] = tkinter.Entry(frameseq, width=8)  # 下でgridがコメントアプトなので使用しない
                piset_value_name[y][x].insert(tkinter.END, col)
                # piset_value_name[y][x].grid(column=x+1,row=y+4,columnspan=2,sticky=tkinter.W)
            else:  # y=0~2
                piset_value_name[y][x] = tkinter.Entry(frameseq, width=5)  # Entry作成　5文字分
                piset_value_name[y][x].insert(tkinter.END, col)  # Entryに上記でcolに読み込んだpiset_value_arrayの要素を入力
                piset_value_name[y][x].grid(column=x + 1, row=y + 4, columnspan=1, sticky=tkinter.W)  # Entryの表示設定

    piseq_chk2 = tkinter.Checkbutton(frameseq, variable=seq_jdge_array[2], text='フォトNGで停止', width=12, anchor='w')
    piseq_chk2.grid(row=4, column=4, columnspan=4, sticky=tkinter.NW)
    seq_jdge_array[2].set(True)  # chekbox初期値セット 'フォトNGで停止'のチェックをONする

    piseq_chk3 = tkinter.Checkbutton(frameseq, variable=seq_jdge_array[3], text='設定無効', width=12, anchor='w')
    piseq_chk3.grid(row=6, column=4, columnspan=4, sticky=tkinter.NW)

    piseq_chk4 = tkinter.Checkbutton(frameseq, variable=seq_jdge_array[6], text='設定無効', width=12,
                                     anchor='w')  # 使用無し
    # piseq_chk4.grid(row=7,column=4,columnspan=4,sticky=tkinter.NW)
    seq_jdge_array[6].set(True)  # chekbox初期値セット 評価パルス設定のチェックボタンONする。しかし、表示していないので使用無し

    pisec_section_name = ['A', 'B', 'C', 'D', 'E', 'F']  # チェックボタンのtext表示をリストで作成
    for x, col in enumerate(pisec_section_name):  # colに上記リストの要素’A’～’F’を取り出す　xは0～5
        col = tkinter.Checkbutton(frameseq, variable=piseq_section[x], text=col)  # 上記読み込んだcolをtext表示し、さらにチェックボタンを作成
        piseq_section[x].set(True)  # chekbox初期値セット ’A'～'F'の各チェックボタンをすべてON
        ''' 
        if x <3:
            col.grid(row=5,column=4+x,columnspan=1,sticky=tkinter.W)
        else :
        '''
        col.grid(row=5, column=4 + x, columnspan=1, sticky=tkinter.W)  # チェックボタンの表示

    # 判定方法選択
    Labelseq_2 = tkinter.Label(frameseq, text='判定実施', width=10,
                               anchor='w')  # フォト検出、Vrs検出のチェックボタンのグループ名称'判定実施'の設定 左寄せ
    Labelseq_2.grid(row=8, column=0, columnspan=1, sticky=tkinter.W)  # 上記ラベルの表示　stickyオプションで左寄せ指定

    seq_jdge_name = ['フォト検出', 'Vrs検出']  # 回転判定の方法のテキストをリストで用意
    for x, col in enumerate(seq_jdge_name):  # colに上記テキストを読みだす。xは0～1
        col = tkinter.Checkbutton(frameseq, variable=seq_jdge_array[x], text=col)  # 上記読み込んだcolをテキスト表示し、チェックボタンを作成
        seq_jdge_array[x].set(False)  # chekbox初期値セット　オール0で無選択
        col.grid(row=8, column=2 * x + 1, columnspan=2, sticky=tkinter.W)  # 上記チェックボタンの表示　stickyオプションで左寄せ指定

    global Buttonpi2_1
    Buttonpi2_1 = tkinter.Button(frameseq, text=u'スタート', width=8)  # 'スタート'ボタンの作成
    Buttonpi2_1.bind("<Button-1>", photo_seqtest_bot)  # <Button-1>:マウスの左クリックによりコールバック関数実施
    Buttonpi2_1.grid(row=10, column=0, columnspan=1, sticky=tkinter.W)  # ボタンの表示　stickyオプションで左寄せ指定

    global Buttonpi2_2
    Buttonpi2_2 = tkinter.Button(frameseq, text=u'ストップ', width=8)  # 'ストップ'ボタンの作成
    Buttonpi2_2.config(state="disable")  # ボタン無効化
    Buttonpi2_2.bind("<Button-1>", photo_seqtest_stop_bot)  # <Button-1>:マウスの左クリックによりコールバック関数実施
    Buttonpi2_2.grid(row=10, column=1, columnspan=2, sticky=tkinter.W)  # ボタンの表示　stickyオプションで左寄せ指定

    global Combopi1
    Combopi1 = ttk.Combobox(frameseq, width=18, state='readonly')  # Combobox作成 書込み禁止設定
    Combopi1["values"] = ("表示設定")  # コンボボックス内の表示を'表示設定'とタプルで指定
    Combopi1.current(0)  # 初期値
    Combopi1.grid(row=10, column=3, columnspan=3, sticky=tkinter.W)  # コンボボックスの表示　stickyオプションで左寄せ指定

    global Buttonpi2_3
    Buttonpi2_3 = tkinter.Button(frameseq, text=u'適用', width=8)  # '適用'ボタンの作成
    Buttonpi2_3.bind("<Button-1>", seq_reading)  # <Button-1>:マウスの左クリックによりコールバック関数実施
    Buttonpi2_3.grid(row=10, column=6, columnspan=2, sticky=tkinter.E)  # ボタンの表示　stickyオプションで右寄せ指定

    # scrolledtextBox
    frameseq2 = tkinter.Frame(seqWindow, pady=5, padx=10)  # スクロールテキストを配置するフレームの作成
    frameseq2.pack(anchor=tkinter.W)  # 左寄せに表示

    global piseq_res
    piseq_res = tkinter.scrolledtext.ScrolledText(frameseq2, width=25, height=6)  # フレームframeseq2にスクロールtextボックスを設定
    piseq_res.grid(row=9, column=0, rowspan=2, columnspan=4, sticky=tkinter.W)  # stickyで左側配置指定

    piseq_chk1 = tkinter.Checkbutton(frameseq2, variable=seq_jdge_array[4], text='保存', width=3,
                                     anchor='w')  # チェックボタン'保存'を左寄りに配置設定
    piseq_chk1.grid(row=9, column=4, columnspan=1, sticky=tkinter.NW)  # gridで上記チェックボタンを配置

    piseq_chk2 = tkinter.Checkbutton(frameseq2, variable=seq_jdge_array[5], text='Vrs詳細保存', width=9,
                                     anchor='w')  # チェックボタン'Vrs詳細保存'を左寄りに配置設定
    piseq_chk2.grid(row=10, column=4, columnspan=2, sticky=tkinter.NW)  # gridで上記チェックボタン配置

    global entrypi2_3
    entrypi2_3 = tkinter.Entry(frameseq2, width=14)  # Entry'filename'をフレームframeseq2に作成
    entrypi2_3.insert(tkinter.END, 'file name')  # Entryに'filename'とEntryの最後に追加入力
    entrypi2_3.grid(row=9, column=5, columnspan=4, sticky=tkinter.NW)  # gridでEntryを上左側に配置

    frameseqpi = tkinter.LabelFrame(seqWindow, pady=2, padx=10, text='フォト検出パルス設定')  # ラベルフレームの作成
    frameseqpi.pack(anchor=tkinter.W, padx=10, )  # ラベルフレームの配置

    # ラベル配置
    labelpi_name = ['使用Pulse', '1周Step数', '周波数[Hz]', '使用電圧[V]', '検出mode', 'Offset']  # ラベルをリストで用意
    for x, row in enumerate(labelpi_name, 0):  # 上記リストからxにインデックスをrowに要素を代入
        labelpi_N = tkinter.Label(frameseqpi, text=row, width=8)  # 上記のラベルフレームにrowの値（ラベル名）でラベルを作成
        labelpi_N.grid(column=x, row=0)  # ラベルフレーム内のrow=0行、columnに上記リストのインデックスを渡して配置

    # 入力Box配置
    for i, row in enumerate(piset_name, 0):  # i=行番号、row=行内容 リストpiset_nameからインデックスをiに、要素をrowに代入
        row = 'psname' + str(i)  # 'psname0','psname1',・・・

    for i, row in enumerate(piset_array, 0):  # piset_array:photo検出のパルス条件設定値
        if i == 0:  # 使用パルス　リストpiset_nameのインデックス0のウィジェットにcomboboxを設定
            piset_name[i] = ttk.Combobox(frameseqpi, width=6, state='readonly')  # Combobox作成 書込み禁止設定
            piset_name[i]["values"] = (
            "0:CW-0", "1:CCW-1", "2:", "3:", "4:CW-4", "5:CCW-5")  # comboboxのvaluesオプションにタプルで渡す
            piset_name[i].current(piset_array[i])  # 初期値 piset_array[0]=0⇒"0:CW-0"設定
        elif i == 4:  # 検出モード リストpiset_nameのインデックス4のウィジェットにcomboboxを設定
            piset_name[i] = ttk.Combobox(frameseqpi, width=6, state='readonly')  # Combobox作成 書込み禁止設定
            piset_name[i]["values"] = ("0:通常", "1:最短移動", "2:逆極性chk")  # 秒針検出はnucleo側で自動判定、valuesオプションにタプルで渡す
            piset_name[i].current(piset_array[i])  # 初期値 piset_array[4]=0⇒"0:通常"設定
        elif i == 5:  # offset リストpiset_nameのインデックス5のウィジェットにEntryを設定
            piset_name[i] = tkinter.Entry(frameseqpi, width=12)  # 入力Entry作成
            piset_name[i].insert(tkinter.END, row)  # インデックスi=5：row=0 挿入する文字rowで示される値を入力欄の最後から入力
            piset_name[i].grid(row=1, column=i)  # 上記Entryをgridで配置
        else:  # 1周step数/周波数/電圧 リストpiset_nameのインデックス1,2,3のウィジェットにEntryを設定
            piset_name[i] = tkinter.Entry(frameseqpi, width=8)  # 入力Entry作成
            piset_name[i].insert(tkinter.END, row)  # i=1:row=360,i=2:row=200,i=3:row=3.0 挿入する文字rowで示される値を入力欄の最後から入力
            piset_name[i].grid(row=1, column=i)  # リストpiset_nameのインデックスで示される要素（ウィジェット）をインデックスiで示されるcolumnに配置
        piset_name[i].grid(row=1, column=i)  # リストpiset_nameのインデックスで示される要素（ウィジェット）をインデックスiで示されるcolumnに配置

        Button7_4 = tkinter.Button(frameseqpi, text=u'PI 針位置単独', width=12, command=pi_window)  # ボタン'PI 針位置単独'の設定
        # Button7_4.bind("<Button-1>",pi_window)
        Button7_4.grid(row=2, column=0, columnspan=2, sticky=tkinter.NW)  # 上記ボタンをフレームframeseqpiのrow=2に上左側に配置

    frame6 = tkinter.Frame(seqWindow, pady=10, padx=10)  # フレームframe6の作成 下記の<動作設定>のウィジェット配置用フレーム
    frame6.pack(anchor=tkinter.W)  # frame6を左寄りに配置

    Label6_1 = tkinter.Label(frame6, text='<動作設定>', width=labewid_1, anchor='w')  # ラベル<動作設定>をframe6に作成 左寄りに作成
    Label6_1.grid(row=0, column=0, columnspan=3)  # 上記ラベルを配置

    # ラベル配置
    label6_name = [['Pulse', 'Step数', 'Freq', 'Trig', '逆極', 'Vrs', '補正P', 'Pe', '+50ms', 'Vm']]  # ラベル名をリストのリストで設定
    for y, row in enumerate(label6_name, 0):  # 上記リストのインデックス0から要素を取り出す。この場合インデックスは0のみで要素は['Pulse', 'Step数', ・・・, 'Vm']
        for x, col in enumerate(
                row):  # 上記row=['Pulse', 'Step数', 'Freq', 'Trig', '逆極', 'Vrs', '補正P', 'Pe', '+50ms', 'Vm']から各要素をcolに取り出す
            if x < 3 or x == 9:  # 下記の入力box欄の大きさに応じてwidthを変えるためインデックス値で分ける
                label6_N = tkinter.Label(frame6, text=col, width=6)  # 'Pulse', 'Step数', 'Freq', 'Vm'
            else:
                label6_N = tkinter.Label(frame6, text=col, width=4)  # 'Trig', '逆極', 'Vrs', '補正P', 'Pe', '+50ms'
            # if x != 6:#Pulse内 Vrs表示なし
            label6_N.grid(column=x + 1, row=y + 1)  # インデックスx,y=0　column=1~10,row=1に配置

    # 入力Box配置
    for i, row in enumerate(sequence_array, 0):  # sequence_array[10×10]のリスト rowに各行を読込む
        for n, col in enumerate(
                row):  # n:sequence_arrayの行rowの各要素をcolに読込む。各行の要素は、'Pulse', 'Step数', 'Freq', 'Trig', '逆極', 'Vrs', '補正P', 'Pe', '+50ms', 'Vm'の値
            if n < 3 or n == 9:  # Entry入力欄の大きさに応じてwidthを変えるためインデックス値で分ける
                sequence_name[i][n] = tkinter.Entry(frame6, width=6)  # 'Pulse', 'Step数', 'Freq', 'Vm'の入力欄
            else:
                sequence_name[i][n] = tkinter.Entry(frame6, width=3)  # 'Trig', '逆極', 'Vrs', '補正P', 'Pe', '+50ms'の入力欄
            sequence_name[i][n].insert(tkinter.END, col)  # 各入力欄にcolに読込まれた値を入力欄の最後に追加
            # if n != 6:#Pulse内 Vrs表示なし
            sequence_name[i][n].grid(row=i + 2, column=n + 1)  # row=2~11,column=1~10に配置

    global seq_run  # ボタン押下時の関数実行中に表記変えるため変数定義
    global Button6_1
    seq_run = tkinter.StringVar()  # widget変数を文字列変数とする
    seq_run.set('単独実行')  # widget変数seq_runに初期文字列をセット
    Button6_1 = tkinter.Button(frame6, textvariable=seq_run, width=12)  # ボタンをそのtextに変数seq_runを渡して表示する
    Button6_1.bind("<Button-1>", pulse_seq_bot)  # マウスの左クリック操作で実行関数を呼ぶ。その中で、ボタンの表示変更
    Button6_1.grid(row=i + 3, column=1, columnspan=2)  # このiは上記のfor文の最後のi=9を引き継いでいる　row=12、column=1に配置
    global Button6_2
    Button6_2 = tkinter.Button(frame6, text=u'設定読込', width=12)  # ボタン'設定読込'の作成
    Button6_2.bind("<Button-1>", pulse_seqread_bot)  # マウスの左クリック操作で実行関数を呼ぶ
    Button6_2.grid(row=i + 3, column=4, columnspan=4)  # このiは9なので、row=12,column=4に配置

    global seq_name
    seq_name = tkinter.StringVar()  # widget変数を文字列変数とする
    label5_21 = tkinter.Label(frame6, textvariable=seq_name, width=15)  # フレームframe6にラベル（テキスト変数seq_name）を作成
    label5_21.grid(row=i + 3, column=7, columnspan=5)  # i=9なのでrow=12,column=7に上記ラベルを配置


# パルス列設定window作成-------------------------------------------
def pulsetrain_window(event):
    """
    mainウインドウでパルス列設定ボタンを押下した際に開くウィンドウの設定＆表示処理

    :param event:
    :return:
    """
    global trainWindow

    # 複数開かないようにする処理
    if 'trainWindow' in globals():  # Windowが定義されているか？ global名前空間にあるシンボルの中にtrainWindowが有れば、開かれている。
        if trainWindow.winfo_exists() == 1:  # windowが存在するか？ ここでも開かれているか確認。開かれていればreturn
            trainWindow.attributes('-topmost', 1)  # トップに固定表示 trainWindowを最前面に表示、次のコマンドで解除しないと常に最前面表示となる
            trainWindow.attributes('-topmost', 0)  # 固定解除
            return

    get_winposition()  # メインwindow座標取得（y座標は30だけ上　ウインドウのタイトル部分のyサイズを引いてある）
    trainWindow = tkinter.Toplevel(tk)  # trainWindowをメインウインドウのサブウインドウとして作成（メインウインドウを閉じるとサブも閉じる)
    trainWindow.geometry('+' + str(xposi) + '+' + str(yposi))  # window座標指定 メインウインドウの右横に表示する
    frame8 = tkinter.Frame(trainWindow, pady=10, padx=10)  # <パルス列設定>の項目用にframe8を作成
    frame8.pack(anchor=tkinter.W)  # フレームを配置表示 空きスペースの左寄せ指示

    Label8_1 = tkinter.Label(frame8, text='<パルス列設定>', width=labewid_1, anchor='w')  # frame8にラベル<パルス列設定>を作成
    Label8_1.grid(row=0, column=0, columnspan=2, sticky=tkinter.W)  # <パルス列設定>ラベルの配置、左寄せ、column2つを結合

    Label8_2 = tkinter.Label(frame8, text='区間', width=6, anchor='e')  # frame8にラベル'区間'を作成
    Label8_2.grid(column=1, row=1, columnspan=1, sticky=tkinter.E)  # 上記ラベルの作成

    label8_Pname = [['A', 'B', 'C', 'D', 'E', 'F']]  # ラベルのテキストをリストで作成
    for y, row in enumerate(label8_Pname, 0):  # 上記リストの値とインデクスを取り込む　y=0のみ、row=['A','B',...'F']
        for x, char in enumerate(row):  # 上記で読み込んだrowからインデクスと、値を読み込む　x=0～5　char='A'～'F'
            label5_P = tkinter.Label(frame8, text=char, width=5)  # frame8にラベルをテキストにcharを渡して作成
            label5_P.grid(column=x + 2, row=y + 1)  # row= 1, column=2～7にラベルを配置

    label8_Pnum = [['CW 　-0', 'CCW  -1', '補CW -2', '補CCW-3', 'Pulse-4', 'Pulse-5', 'Pr-6']]  # ラベルのテキストをリストで作成
    for y, row in enumerate(label8_Pnum, 0):  # 上記リストの値とインデクスを取り込む　y=0のみ、row=['CW 　-0', 'CCW  -1', ..., 'Pr-6']
        for x, char in enumerate(row):  # 上記で読み込んだrowからインデクスと、値を読み込む　x=0～6　char='CW 　-0'～ 'Pr-6'
            label8_P = tkinter.Label(frame8, text=char, width=6)  # frame8にラベルをテキストにcharを渡して作成
            if x < pulse_disp_num or x == 6:  # x=0~6
                label8_P.grid(column=0, row=2 * x + 2)  # row=2,4,6,...,14 2つおきにラベルを配置する

    for y, row in enumerate(pulse_train_labename, 0):  # リストpulse_train_labenameからインデックスをyに値をrowに読み込む
        pulse_train_labename[y] = tkinter.StringVar()  # リストpulse_train_labenameの各要素を文字列として扱うことの設定
        char = tkinter.Label(frame8, textvariable=pulse_train_labename[y], width=12,
                             anchor=tkinter.W)  # frame8にラベルを作成、表示テキストにpulse_train_labenameの各要素を渡して作成
        pulse_train_labename[y].set(
            pulse_train_name[y])  # pulse_train_labenameの要素にpulse_train_name(関数train_readingで読み込んだ)の各要素を代入
        if y < pulse_disp_num or y == 6:  # y=0～6
            char.grid(column=1, row=2 * y + 2)  # 上記ラベルをcolumn=1, row=2,4,6...,14まで2つ置きに配置

    for y, row in enumerate(pulse_train_array_name, 0):  # リストpulse_train_array_name(7行×12列)からインデックスをyに値をrowに読み込むy=0～6
        for x, char in enumerate(row):  # 上記のrowからインデックスをx、値をcharに読み込む x=0～11
            pulse_train_array_name[y][x] = tkinter.StringVar()  # リストpulse_train_array_nameの各要素を文字列として扱うことの設定
            char = tkinter.Label(frame8, textvariable=pulse_train_array_name[y][x], width=5,
                                 anchor=tkinter.W)  # frame8にラベルを作成、表示テキストにpulse_train_array_nameの各要素を渡して作成
            pulse_train_array_name[y][x].set(pulse_train_array_str[y][
                                                 x])  # pulse_train_array_nameの要素にpulse_train_array_str(関数train_readingで読み込んだ)の各要素を代入
            if y < pulse_disp_num or y == 6:  # y=0～6
                if x < 6:  # X=0～5
                    char.grid(column=x + 2, row=2 * y + 2)  # row=2,4,6,...14 column=2,3,4,...,7 A1,B1,C1,D1,E1,F1
                elif x >= 6:  # x=6~11
                    char.grid(column=x + 2 - 6, row=2 * y + 3)  # row=3,5,7,...15 column=2,3,4,...,7　A2,B2,C2,D2,E2,F2

    global Button8_1
    Button8_1 = tkinter.Button(frame8, text=u'設定読込', width=12)  # frame8にボタン’設定読込'をグローバルで作成
    Button8_1.bind("<Button-1>", pulse_train_bot)  # マウスの左クリックによりpulse_train_bot実行
    Button8_1.grid(row=20, column=0, columnspan=3, sticky=tkinter.W)  # 上記のボタンの配置


# カメラウィンドウ作成---------------------------------
def cam_window(event):
    """
    メインウインドウで'カメラ機能'ボタンを押したときに表示されるカメラ機能用ウインドウの作成
    :param event:
    :return:
    """
    global cbcam  # カメラNo
    global Boxcam_4  # 撮影Delay
    global Boxcam_5  # 撮影枚数
    global Boxcam_6  # 保存ファイル名

    global camwindow

    # 複数開かないようにする処理
    if 'camwindow' in globals():  # Windowが定義されているか？ global名前空間にあるシンボルの中にcamWindowが有れば、開かれている。
        if camwindow.winfo_exists() == 1:  # windowが存在するか？ ここで、存在すれば以下を実行してreturn
            camwindow.attributes('-topmost', 1)  # トップに固定表示　camwindowをTOPに表示。つぎで解除しないと常に最前面表示となる
            camwindow.attributes('-topmost', 0)  # 固定解除
            return

    get_winposition()  # メインwindow座標取得（y座標は30だけ上　ウインドウのタイトル部分のyサイズを引いてある）
    find_cam()  # システムに接続されているカメラのデバイスIDを検出

    camwindow = tkinter.Toplevel(tk)  # mainウィンドウに紐づくサブウインドウとして作成
    camwindow.geometry('+' + str(xposi) + '+' + str(yposi))  # 上部get_winposition()で取得した座標を指定 ディスプレー左上原点
    framecam = tkinter.Frame(camwindow, pady=10, padx=10)  # 上記camwindowにフレーム作成
    framecam.pack(anchor=tkinter.W)  # フレームの配置 空きスペース左寄りに配置指定

    # Buttoncam_1= tkinter.Button(framecam, text=u'撮影開始', width=12)
    # Buttoncam_1.bind("<Button-1>",disp_cam)

    Buttoncam_2 = tkinter.Button(framecam, text=u'カメラ接続', width=12)  # ’カメラ接続'のボタン作成
    Buttoncam_2.bind("<Button-1>", disp_cam)  # マウスの左クリックでdisp_com関数実行指定

    Labelcam_1 = tkinter.Label(framecam, text='Camera No', width=10, anchor='e')  # 上記フレームに'Camera No'のラベル作成
    cbcam = ttk.Combobox(framecam, width=2, state='readonly')  # Combobox作成 書込み禁止設定
    cbcam["values"] = cam_list  # 上記のコンボボックスの'values'にfind_cam()で検出したカメラリストを渡す。
    cbcam.current(cam_no)  # 初期値にcam_noを渡す

    Labelcam_4 = tkinter.Label(framecam, text='撮影Delay[ms]:', width=12, anchor='e')  # 上記フレームにラベル'撮影Delay[ms]:'作成
    Boxcam_4 = ttk.Combobox(framecam, width=4, state='readonly')  # Combobox作成 書込み禁止設定
    Boxcam_4["values"] = cam_delaylist  # 上記のコンボボックスの'values'に[100, 300, 500, 700, 1000]を渡す
    Boxcam_4.current(1)  # 初期値　300を初期値として設定

    Labelcam_5 = tkinter.Label(framecam, text='撮影step数:', width=10, anchor='e')  # 上記フレームに'撮影step数:'ラベル作成
    Boxcam_5 = tkinter.Entry(framecam, width=3)  # Entryを作成
    Boxcam_5.insert(tkinter.END, 12)  # 上記Entryに12を入力欄の最後に追加

    Labelcam_6 = tkinter.Label(framecam, text='保存名+No(Auto):', width=16, anchor='e')  # 上記フレームに'保存名+No(Auto):'ラベル作成
    Boxcam_6 = tkinter.Entry(framecam, width=16)  # Entryを作成
    Boxcam_6.insert(tkinter.END, 'test')  # 'test'を入力欄の最後に追加

    # 説明を文字列変数で設定し、ラベルのtextに渡すことで表示
    explain1 = '使い方 [0]key :撮影開始(Pulse出力 Anystep同じ)'
    explain2 = '       [q]key：停止 or Window閉じる　※設定変更はWindow閉じる'
    explain3 = '       [f]or[n]key:Fix Focus 位置変更 far or near　[A]key:Auto Focus機能有効　※対応カメラのみ'
    Expcam_1 = tkinter.Label(framecam, text=explain1, width=96, anchor='w')
    Expcam_2 = tkinter.Label(framecam, text=explain2, width=96, anchor='w')
    Expcam_3 = tkinter.Label(framecam, text=explain3, width=96, anchor='w')

    # 上記で作成した各ウィジェットの配置指定
    Buttoncam_2.grid(row=0, column=0, columnspan=1)
    Labelcam_1.grid(row=0, column=1, columnspan=1)
    cbcam.grid(row=0, column=2, columnspan=1)
    Labelcam_4.grid(row=0, column=3, columnspan=1)
    Boxcam_4.grid(row=0, column=4, columnspan=1)
    Labelcam_5.grid(row=0, column=5, columnspan=1)
    Boxcam_5.grid(row=0, column=6, columnspan=1)
    Labelcam_6.grid(row=0, column=7, columnspan=1)
    Boxcam_6.grid(row=0, column=8, columnspan=1)
    Expcam_1.grid(row=1, column=0, columnspan=9)
    Expcam_2.grid(row=2, column=0, columnspan=9)
    Expcam_3.grid(row=3, column=0, columnspan=9)
    # Labelcam_8.grid(row=2,column=0,columnspan=8)


# フォトインタラプタ機能window作成
def pi_window():
    """
    シーケンス機能ウィンドウ　フォト検出パルス設定欄の'PI針位置単独'ボタンが押された際のウィンドウ設定処理
    :return:
    """
    global piWindow

    # 複数開かないようにする処理
    if 'piWindow' in globals():  # piWindowが定義されているか？ global名前空間にあるシンボルの中にpiwindowが有れば、開かれている。
        if piWindow.winfo_exists() == 1:  # windowが存在するか？
            piWindow.attributes('-topmost', 1)  # トップに固定表示
            piWindow.attributes('-topmost', 0)  # 固定解除
            return

    get_winposition()  # メインwindow座標取得
    piWindow = tkinter.Toplevel(tk)  # mainウィンドウに紐づくサブウインドウとして作成
    piWindow.geometry('+' + str(xposi) + '+' + str(yposi))  # window座標指定　上記get_winposition()で取得した座標を指定 ディスプレー左上原点
    framepi = tkinter.Frame(piWindow, pady=10, padx=10)  # piwindowにフレーム作成
    framepi.pack(anchor=tkinter.W)  # フレームの配置

    Labelpi_0 = tkinter.Label(framepi, text='<PI 初期設定>', width=labewid_1, anchor='w')  # 上記フレームにラベル'<PI 初期設定>'作成
    Labelpi_0.grid(row=0, column=0, columnspan=3, sticky=tkinter.W)  # ラベルの配置

    global Buttonpi_1
    Buttonpi_1 = tkinter.Button(framepi, text=u'検出初期設定', width=12)  # フレームにボタン'検出初期設定'作成
    Buttonpi_1.bind("<Button-1>", photo_init_bot)  # マウスの左クリックで　photo_init_bot関数実行
    Buttonpi_1.grid(row=4, column=0, columnspan=2, sticky=tkinter.W)  # ボタンの配置

    piresult[0] = tkinter.StringVar()  # リストのインデックス[0]に文字列変数設定
    char = tkinter.Label(framepi, textvariable=piresult[0], width=8, anchor='w')  # テキスト変数に上記変数を渡してラベルの作成
    piresult[0].set('未実施')  # リストの値に'未実施’指定
    char.grid(row=4, column=2, columnspan=1)  # 上記ラベルの配置

    Labelpi_2 = tkinter.Label(framepi, text='<PI 位置検出>', width=labewid_1, anchor='w')  # 上記フレームにラベル'<PI 位置検出>'作成
    Labelpi_2.grid(row=5, column=0, columnspan=3, sticky=tkinter.W)  # ラベルの配置

    global Buttonpi_2
    Buttonpi_2 = tkinter.Button(framepi, text=u'ゼロ位置セット', width=12)  # 上記フレームにボタン'ゼロ位置セット'作成
    Buttonpi_2.bind("<Button-1>", photo_posiset_bot)  # マウスの左クリックで　photo?position_bot関数実行
    Buttonpi_2.grid(row=6, column=0, columnspan=2, sticky=tkinter.W)  # ボタンの配置

    piresult[1] = tkinter.StringVar()  # リストのインデックス[1]に文字列変数設定
    char = tkinter.Label(framepi, textvariable=piresult[1], width=8, anchor='w')  # テキスト変数に上記変数を渡してラベルの作成
    piresult[1].set('未実施')  # リストの値に'未実施’指定
    char.grid(row=6, column=2, columnspan=1)  # ラベルの配置

    global Buttonpi_3
    Buttonpi_3 = tkinter.Button(framepi, text=u'ゼロ位置確認', width=12)  # 上記framepiにボタン'ゼロ位置確認'作成
    Buttonpi_3.bind("<Button-1>", photo_posicheck_bot)  # マウスの左クリックで photo_posicheck_bot実行
    Buttonpi_3.grid(row=7, column=0, columnspan=2, sticky=tkinter.W)  # ボタンの配置

    piresult[2] = tkinter.StringVar()  # リストのインデックス[2]に文字列変数設定
    char = tkinter.Label(framepi, textvariable=piresult[2], width=8, anchor='w')  # テキスト変数に上記変数を渡してラベルの作成
    piresult[2].set('-----')  # リストの値に'-----’指定
    char.grid(row=7, column=2, columnspan=1)  # ラベルの配置

    global pitxt_res
    pitxt_res = tkinter.scrolledtext.ScrolledText(framepi, width=25, height=6)  # 上記framepiにスクロールドテキストボックス作成
    pitxt_res.grid(row=4, column=3, rowspan=4, columnspan=1, sticky=tkinter.W)  # スクロールドテキストボックス配置


# Vrsタイミング表示機能window作成
def vrs_window():
    """
    メインウインドウでVrs回転検出ボタンが押下されたときに開くウインドウの処理
    :return:
    """
    global vrsWindow

    # 複数開かないようにする処理
    if 'vrsWindow' in globals():  # Windowが定義されているか？ global名前空間にあるシンボルの中にvrswindowが有れば、開かれている。
        if vrsWindow.winfo_exists() == 1:  # windowが存在するか？ 開かれていればreturn
            vrsWindow.attributes('-topmost', 1)  # トップに固定表示
            vrsWindow.attributes('-topmost', 0)  # 固定解除
            return

    get_winposition()  # メインwindow座標取得
    vrsWindow = tkinter.Toplevel(tk)  # mainウインドウに紐づくサブウインドウとして作成
    vrsWindow.geometry('+' + str(xposi) + '+' + str(yposi))  # window座標指定 上記get_winposition()で取得した座標を指定 ディスプレー左上原点

    framevrs = tkinter.Frame(vrsWindow, pady=10, padx=10)  # 上記で作成したウインドウにフレームを作成
    framevrs.grid(row=0, column=0, sticky=tkinter.W, columnspan=2)  # フレームの配置

    Labelvrs_0 = tkinter.Label(framevrs, text='<Vrs 検出Timing>', anchor='w')  # フレームframevrsにラベル'<Vrs 検出Timing>'作成
    Labelvrs_0.grid(row=0, column=0, columnspan=3, sticky=tkinter.W)  # ラベルの配置

    # ラベル配置
    labelvr1_name = ['Dt区間1 [us]', 'Dt区間2 [us]', 'Dt区間3 [us]', 'Dt区間4 [us]']  # ラベルに記載する内容をリストで作成
    for x, row in enumerate(labelvr1_name, 0):  # 上記リストの各インデックスと各値を読み出す
        labelpi_N = tkinter.Label(framevrs, text=row, width=10, anchor='w')  # 読込んだrow値をテキストに渡しラベルの作成
        labelpi_N.grid(column=0, row=x + 1, sticky=tkinter.W)  # row(行番号)=1～4までラベルの配置

    for x, col in enumerate(vrsdt_name, 0):  # リストvrsdt_nameのインデックス0から値をcolに読込む
        col = 'vrsdtname' + str(x)  # せっかく読込んだcolにインデクスを文字列化し'vrsdtname'に加える
        # 上記で設定したcolなのに以下でまた変更している
    for x, col in enumerate(vrsdt_array, 0):  # initial_trainで書き換えられたvrsdt_arrayリストをcolに読込む
        vrsdt_name[x] = tkinter.Entry(framevrs, width=6)  # インデックスx=0~3のEntryをframevrsに作成
        vrsdt_name[x].insert(tkinter.END, col)  # 上記で作成したEntryにvrsdt_arrayの値を入力する
        vrsdt_name[x].grid(column=1, row=x + 1, sticky=tkinter.W)  # 各Entry（4つ）を配置する

    # 検出パターン
    framevrs1 = tkinter.LabelFrame(vrsWindow, pady=10, padx=10, text='パターン判定')  # vrsWindowにラベルフレーム'パターン判定'作成
    framevrs1.grid(row=0, column=2, columnspan=5, sticky=tkinter.W)  # ラベルフレームの配置

    labelvr2_name = [0] * 16  # 16個の値を持つリストを作成
    for x, row in enumerate(labelvr2_name, 0):  # インデックス0～15まで、値をrowに読込む（この段階で値はオール0）
        labelpi_N = tkinter.Label(framevrs1, text=format(x, '04b'), width=4,
                                  borderwidth=2, relief="ridge", )  # フレームframevrs1にラベルのフォーマットを4桁のバイナリとして作成
        if x < 4:  # インデックスx=0～3
            labelpi_N.grid(column=3 + 2 * x, row=1, sticky=tkinter.E)  # row=1 column=3,5,7,9に上記のラベルを配置
        elif x < 8:  # インデックスx=4～7
            labelpi_N.grid(column=3 + 2 * (x - 4), row=2, sticky=tkinter.E)  # row=2 column=3,5,7,9に上記のラベルを配置
        elif x < 12:  # インデックスx=7～11
            labelpi_N.grid(column=3 + 2 * (x - 8), row=3, sticky=tkinter.E)  # row=3 column=3,5,7,9に上記のラベルを配置
        else:  # インデックスx=8～15
            labelpi_N.grid(column=3 + 2 * (x - 12), row=4, sticky=tkinter.E)  # row=4 column=3,5,7,9に上記のラベルを配置

    for x, col in enumerate(vrsjdg_name, 0):  # 16個の値を持つリストからインデックスと値を読込む
        col = 'vrsjdgname' + str(x)  # 上記で読込んだcolだが、ここでインデクス番号を文字列化し'vrsjdgname'に追加して設定される。

    for x, row in enumerate(vrsjdg_array, 0):  # OK/NGを0/1で表したリストからインデックスと値を読込む
        vrsjdg_name[x] = ttk.Combobox(framevrs1, width=4,
                                      state='readonly')  # Combobox作成 書込み禁止設定 vrsjdg_nameリストの各要素をコンボボックスとする
        vrsjdg_name[x]["values"] = ("OK", "NG")  # コンボボックスのvaluesオプションにタプル("OK", "NG")を渡す
        vrsjdg_name[x].current(vrsjdg_array[x])  # 初期値　コンボボックスの初期値としてvrsjdg_arrayの各インデクスに対応する値が設定される
        if x < 4:  # インデックスx=0～3
            vrsjdg_name[x].grid(column=4 + 2 * x, row=1, sticky=tkinter.W)  # row=1 column=4,6,8,10に上記のコンボボックスを配置
        elif x < 8:  # インデックスx=4～7
            vrsjdg_name[x].grid(column=4 + 2 * (x - 4), row=2, sticky=tkinter.W)  # row=2 column=4,6,8,10に上記のコンボボックスを配置
        elif x < 12:  # インデックスx=8～11
            vrsjdg_name[x].grid(column=4 + 2 * (x - 8), row=3, sticky=tkinter.W)  # row=3 column=4,6,8,10に上記のコンボボックスを配置
        else:  # インデックスx=12～16
            vrsjdg_name[x].grid(column=4 + 2 * (x - 12), row=4, sticky=tkinter.W)  # row=4 column=4,6,8,10に上記のコンボボックスを配置

    # 結果表示テキスト
    framevrs2 = tkinter.Frame(vrsWindow, pady=10, padx=10)  # vrsWindowにフレームframevrs2を作成
    framevrs2.grid(row=2, column=0, columnspan=10, sticky=tkinter.W)  # 上記フレームを配置
    global vrsres_name
    vrsres_name = ['Total判定', '判定| Pattern| Timing[us]', 'NG位置| 差分', '判定']  # リストでラベル名を作成
    for x, row in enumerate(vrsres_name, 0):  # インデクスx=0～3、rowは上記リストの各要素
        if x == 0 or x == 3 or x == 2:  # 文字数違いでラベルを作成
            labelpi_N = tkinter.Label(framevrs2, text=row, width=10, anchor='w')
        elif x == 1:
            labelpi_N = tkinter.Label(framevrs2, text=row, width=35, anchor='w')
        else:  # この条件はない
            labelpi_N = tkinter.Label(framevrs2, text=row, width=6, anchor='w')
        if x == 0 or x == 1 or x == 2:  # 'Total判定', '判定| Pattern| Timing[us]', 'NG位置| 差分'のみ配置
            labelpi_N.grid(row=0, column=3 * x, columnspan=3, sticky=tkinter.W)

    for x, row in enumerate(vrsres_name,
                            0):  # インデクスx=0～3、rowはリスト['Total判定', '判定| Pattern| Timing[us]', 'NG位置| 差分', '判定']の各要素
        if x == 0:  # 'Total判定'
            vrsres_name[x] = tkinter.scrolledtext.ScrolledText(framevrs2, width=25,
                                                               height=15)  # 上記リストの各要素をスクロールドテキストに変更
        elif x == 1:  # '判定| Pattern| Timing[us]'
            vrsres_name[x] = tkinter.scrolledtext.ScrolledText(framevrs2, width=35, height=15)
        elif x == 3:  # '判定' これは作成されるが、配置されない
            vrsres_name[x] = tkinter.scrolledtext.ScrolledText(framevrs2, width=6, height=15)
        else:  # , 'NG位置| 差分',
            vrsres_name[x] = tkinter.scrolledtext.ScrolledText(framevrs2, width=10, height=15)
        if x == 0 or x == 1 or x == 2:  # 'Total判定', '判定| Pattern| Timing[us]', 'NG位置| 差分'のみ配置する
            vrsres_name[x].grid(row=1, column=3 * x, columnspan=3, sticky=tkinter.W)

    Buttonvrs_1 = tkinter.Button(framevrs2, text=u'クリア', width=12, command=vrstext_clear)  # フレームframevrs2にボタン'クリア'作成
    Buttonvrs_1.grid(row=6, column=0, columnspan=2, sticky=tkinter.W)  # 上記ボタンの配置

    Buttonvrs_2 = tkinter.Button(framevrs2, text=u'詳細保存', width=10,
                                 command=vrstext_save_manu)  # フレームframevrs2にボタン'詳細保存'作成
    Buttonvrs_2.grid(row=6, column=3, columnspan=1, sticky=tkinter.E)  # 上記ボタンの配置

    global entryvrs_1
    entryvrs_1 = tkinter.Entry(framevrs2, width=14)  # フレームframevrs2にEntry作成
    entryvrs_1.insert(tkinter.END, 'file name')  # Entryの最後に'file name'追記
    entryvrs_1.grid(row=6, column=4, columnspan=3, sticky=tkinter.W)  # Entryの配置

    Buttonvrs_3 = tkinter.Button(framevrs2, text=u'offset送信', width=8,
                                 command=vrsng_phoffset)  # フレームramevrs2にボタン'offset送信'作成
    Buttonvrs_3.grid(row=6, column=6, columnspan=1, sticky=tkinter.E)  # ボタンの配置

    global entryvrs_2
    entryvrs_2 = tkinter.Entry(framevrs2, width=4)  # フレームframevrs2にEntry作成
    entryvrs_2.insert(tkinter.END, '-2')  # Entryの最後に-2を追記
    entryvrs_2.grid(row=6, column=7, columnspan=1, sticky=tkinter.W)  # 上記Entryの配置


# ---------------- ~ 関数定義 ---------------------------------
#
# ---------------- main window作成 ----------------------------
#
"""
mainウインドウの作成
mainウインドウの中に配置するウィジェットのサイズ、配置を指定し、初期状態を設定する。

COMポート
<Pulse設定>
<Pulse幅／本数>
<Pulse出力>
<オプション機能>
"""
# ---------------- COMポート設定GUI ----------------------------
frame1 = tkinter.Frame(tk, pady=10, padx=10)  # Frame(複数のウィジェットを配置出来るコンテナ)　pady、padx枠とテキストの間の空白
frame1.pack(anchor=tkinter.W)  # frame配置左よせ

Label1_1 = tkinter.Label(frame1, text='COMポート : ', width=12, anchor='w')  # ラベル'COMポート:'配置frame1の左端

Box1_1 = tkinter.Entry(frame1, width=40)  # COMポート入力欄　半角40文字
Box1_1.insert(tkinter.END, Com_No)  # 入力欄の最後に追加

Button1_1 = tkinter.Button(frame1, text=u'OPEN', width=7)  # u:unicode文字列が作成される
Button1_1.bind("<Button-1>", Select_COM)  # "<Button-1>"=マウスの左クリックにより、Select_COM関数を実施する
Button1_2 = tkinter.Button(frame1, text=u'Close', width=7)
Button1_2.bind("<Button-1>", Close_COM)  # "<Button-1>"=マウスの左クリックにより、Close_COM関数を実施する

Label1_1.grid(row=0, column=0)  # Label1_1、BOX1_1、Button1_1、Button1_2をgridでrow=0行に一列に配置する
Box1_1.grid(row=0, column=1, sticky=tkinter.W)  # COMポートEntryBox　stickyで配置方向指定W:左寄せ
Button1_1.grid(row=0, column=2)  # 'OPEN'ボタン
Button1_2.grid(row=0, column=3)  # 'Close'ボタン

# ---------------- ~ COMポート設定GUI --------------------------
# --------------- AD2設定GUI -----------------
# 本スクリプトでframe2を使用する箇所はない。
frame2 = tkinter.Frame(tk, pady=10)
frame2.pack()  # frame1の下に配置されているが、サイズ小さくて見えない。⇒使用していない
# --------------- ~ AD2設定GUI ---------------

# ---------------- Pulse設定GUI ----------------------------
frame3 = tkinter.Frame(tk, pady=10, padx=10)  # frame3に<Pulse設定>部分のウィジェットを配置する
frame3.pack(anchor=tkinter.W)  # 左端に配置

Label3_1 = tkinter.Label(frame3, text='<Pulse設定>', width=labewid_1, anchor='w')  # Label3_1をframe3の左端に配置

# コンボボックス
# ----------- このコンボボックスはメインウインドウに表示していない。⇒使用していない ----------------------
Pulse_cbLabe = tkinter.Label(frame3, text='Pulse選択 : ', width=labewid_1, anchor='w')
Pulse_cb = ttk.Combobox(frame3, width=10, state='readonly')  # Combobox作成 書込み禁止設定
Pulse_cb["values"] = ("0: 2Coil-1", "1: NS", "2: 2Coil-2", "3: NS", "4: 1coil")
Pulse_cb.current(0)  # 初期値
# --------------------------------------------------------------------------------------------

# checkボックス
chklabe1 = tkinter.Label(frame3, text='オプション : ', width=10, anchor='w')  # frame3の左端にラベル'オプション:'を配置
chk3_1 = tkinter.Checkbutton(frame3, variable=pulsemode_0, text='Triger', width=8,
                             anchor='w')  # frame3にチェックボタンを作成し、'Triger'テキストを左配置、チェック状態はvariableによる
chk3_2 = tkinter.Checkbutton(frame3, variable=pulsemode_1, text='極性反転', width=8,
                             anchor='w')  # frame3にチェックボタンを作成し、'極性反転'テキストを左配置、チェック状態はvariableによる
chk3_4 = tkinter.Checkbutton(frame3, variable=pulsemode_3, text='補正あり', width=8,
                             anchor='w')  # frame3にチェックボタンを作成し、'補正あり'テキストを左配置、チェック状態はvariableによる
chklabe2 = tkinter.Label(frame3, text='Vrs検出 : ', width=10, anchor='w')  # メインウインドウ上に表示していない。⇒使用していない
chk3_3 = tkinter.Checkbutton(frame3, variable=pulsemode_2, text='Vrs enable', width=8,
                             anchor='w')  # frame3にチェックボタンを作成し、'Vrs enable'テキストを左配置、チェック状態はvariableによる
# chk3_4 = tkinter.Label(frame3, text='',width=8,anchor='w')
# chk3_4 = tkinter.Checkbutton(frame3, variable=pulsemode_3, text='Vrs Wait',width=8,anchor='w')
chklabe3 = tkinter.Label(frame3, text='Pe設定 : ', width=10, anchor='w')  # frame3にラベル'Pe設定'を左配置
chk3_5 = tkinter.Checkbutton(frame3, variable=pulsemode_4, text='Enable', width=6,
                             anchor='w')  # frame3にチェックボタンを作成し、'Enable'テキストを左配置、チェック状態はvariableによる
Label3_4 = tkinter.Label(frame3, text='Pe幅[us]', width=8, anchor='e')  # frame3にラベル'Pe幅[us]'右配置
Box3_4 = tkinter.Entry(frame3, width=6)
Box3_4.insert(tkinter.END, 244)  # frame3に入力欄を作成し、入力欄の最後に244を挿入
Label3_5 = tkinter.Label(frame3, text='wait[us]', width=8, anchor='e')  # frame3にラベル'wait[us]'右配置
Box3_5 = tkinter.Entry(frame3, width=6)
Box3_5.insert(tkinter.END, 3000)  # frame3に入力欄を作成し、入力欄の最後に3000を挿入

pulsemode_0.set(True)  # chekbox初期値セット 'Triger'チェックBOXの初期値
# pulsemode_2.set(True)#chekbox初期値セット

Label3_6 = tkinter.Label(frame3, text='SPK設定 : ', width=10, anchor='w')  # anchor:Labelウイジェットに表示するtextの配置指定左
Label3_7 = tkinter.Label(frame3, text='周期[us]', width=8, anchor='e')  # anchor:Labelウイジェットに表示するtextの配置指定右
Box3_7 = tkinter.Entry(frame3, width=6)  # Entryウィジェット作成
Box3_7.insert(tkinter.END, 488)  # Entry欄の最後に488挿入
Label3_8 = tkinter.Label(frame3, text='ON[us]', width=8, anchor='e')  # anchor:Labelウイジェットに表示するtextの配置指定右
Box3_8 = tkinter.Entry(frame3, width=6)  # Entryウィジェット作成
Box3_8.insert(tkinter.END, 31)  # Entry欄の最後に31挿入

Label3_2 = tkinter.Label(frame3, text='周波数[Hz] : ', width=10, anchor='w')  # anchor:Labelウイジェットに表示するtextの配置指定左
Box3_2 = tkinter.Entry(frame3, width=8)  # 周波数入力欄 半角8文字
Box3_2.insert(tkinter.END, 200)  # 初期値として入力欄の最後に追加
Label3_3 = tkinter.Label(frame3, text='Anysteps : ', width=10, anchor='w')  # anchor:Labelウイジェットに表示するtextの配置指定左
Box3_3 = tkinter.Entry(frame3, width=8)  # Anysteps入力欄 半角8文字
Box3_3.insert(tkinter.END, 60)  # 初期値として入力欄の最後に追加

Label3_9 = tkinter.Label(frame3, text='Vcomp[V] : ', width=10, anchor='e')  # anchor:Labelウイジェットに表示するtextの配置指定右 左と右で大差ない
Box3_9 = tkinter.Entry(frame3, width=6)  # Vcomp入力欄　半角6文字
Box3_9.insert(tkinter.END, 3.0)  # 初期値として入力欄の最後に追加
Label3_10 = tkinter.Label(frame3, text='※Jumper注意 max3V', width=14,
                          anchor='e')  # anchor:Labelウイジェットに表示するtextの配置指定 16文字無いと※表示されない
Button3_1 = tkinter.Button(frame3, text=u'設定送信', width=10)  # ’設定送信'ボタン作成 u:unicode文字列が作成される
Button3_1.bind("<Button-1>", manual_pulse_bot)  # <Button-1>"=マウスの左クリックにより、manual_pulse_bot関数処理する

Label3_1.grid(row=0, column=0, columnspan=3, sticky=tkinter.W)  # <Pulse設定>のラベルの配置位置指定
# Pulse_cbLabe.grid(row=1,column=0)
# Pulse_cb.grid(row=1,column=1,columnspan=1)
chklabe1.grid(row=2, column=0, sticky=tkinter.W)  # ラベル'オプション'配置指定 stickyで左に配置
chk3_1.grid(row=2, column=1, sticky=tkinter.W)  # チェックボタン'Triger'を’オプション'の右のcolumnに配置
chk3_2.grid(row=2, column=3, sticky=tkinter.W)  # チェックボタン'極性反転'を'Triger'の右のcolumnに配置
chk3_4.grid(row=2, column=4)  # チェックボタン'補正あり'を'極性反転'の右のcolumnに配置
# chk3_6.grid(row=2,column=4,sticky=tkinter.W)

# Pe設定配置
chklabe3.grid(row=4, column=0, sticky=tkinter.W)  # ラベル'Pe設定'配置指定
chk3_5.grid(row=4, column=1, sticky=tkinter.W)  # チェックボタン'Enable'をPe設定の右のcolumnに配置
Label3_4.grid(row=4, column=3, sticky=tkinter.E)  # ラベル'Pe幅'を'Enable'の右のcolumnに配置
Box3_4.grid(row=4, column=4, sticky=tkinter.W)  # 入力欄を'Pe幅'の右のcolumnに配置
Label3_5.grid(row=4, column=5, sticky=tkinter.E)  # ラベル'wait'をPe幅の入力欄の右のcolumnに配置
Box3_5.grid(row=4, column=6, sticky=tkinter.W)  # 入力欄を'wait'の右のcolumnに配置

# SPK設定配置
Label3_6.grid(row=5, column=0, sticky=tkinter.W)  # ラベル'SPK設定'配置指定
chk3_3.grid(row=5, column=1, sticky=tkinter.W)  # チェックボタン'Vrs enable'をSPK設定の右のcolumnに配置
Label3_7.grid(row=5, column=3, sticky=tkinter.E)  # ラベル'周期'を'Vrs enable'の右のcolumnに配置
Box3_7.grid(row=5, column=4, sticky=tkinter.W)  # 入力欄を'周期'の右のcolumnに配置
Label3_8.grid(row=5, column=5, sticky=tkinter.E)  # ラベル'ON'を周期の入力欄の右のcolumnに配置
Box3_8.grid(row=5, column=6, sticky=tkinter.W)  # 入力欄を'ON'の右のcolumnに配置
Label3_9.grid(row=6, column=3, sticky=tkinter.E)  # ラベル'Vcomp[V]'を'周波数'の入力欄の右のcolumnに配置
Box3_9.grid(row=6, column=4, sticky=tkinter.W)  # 入力欄を'Vcomp[V]'の右のcolumnに配置
Label3_10.grid(row=7, column=4, sticky=tkinter.E)  # ラベル'Jumper注意...'を'Vcomp'の入力欄の下のrowに配置

Label3_2.grid(row=6, column=0, sticky=tkinter.W)  # ラベル'周波数'配置指定
Box3_2.grid(row=6, column=1, sticky=tkinter.W)  # 入力欄を'周波数'の右のcolumnに配置
Label3_3.grid(row=7, column=0, sticky=tkinter.W)  # ラベル'Anysteps'配置指定
Box3_3.grid(row=7, column=1, columnspan=2, sticky=tkinter.W)  # 入力欄を'Anysteps'の右のcolumnに配置

Button3_1.grid(row=8, column=1, columnspan=2)  # '設定送信'ボタン配置指定
# ---------------- ~ Pulse設定GUI --------------------------

# ---------------- Pulses幅/本数設定GUI ----------------------
frame5 = tkinter.Frame(tk, pady=10, padx=10)  # <Pulse幅/本数>ウィジェット用のフレーム作成
frame5.pack(anchor=tkinter.W)  # frame5を左端に配置　ただし、実際はメインウィンドウの横サイズに合わせられる
Label5_1 = tkinter.Label(frame5, text='<Pulse幅[us]/本数>', width=labewid_1, anchor='w')  # ラベル'<Pulse幅/本数>'をframe5に配置指示
Label5_1.grid(column=0, row=0, columnspan=3, sticky=tkinter.W)  # ラベル'<Pulse幅/本数>'を左配置で表示

Label5_2 = tkinter.Label(frame5, text='区間', width=6, anchor='e')  # ラベル'区間'を右配置指示
Label5_2.grid(column=0, row=1, columnspan=1, sticky=tkinter.W)  # ラベル'区間'を表示　左配置

label5_Pnum = [['CW -0', 'CCW-1', '補CW -2', '補CCW-3', 'CW-4', 'CCW-5', 'Pr-6']]  # ラベルデータをリストで用意
for y, row in enumerate(label5_Pnum, 0):  # y=0のみ, row='CW -0' row='CCW-1'........
    for x, char in enumerate(row):  # x=0, char=CW -0 x=1, char=CCW-1 ........x=6, char=Pr-6
        label5_P = tkinter.Label(frame5, text=char, width=7, anchor='w')  # ラベルの作成
        if x < pulse_disp_num or x == 6:  # pulse_disp_num = 6 なので結局x<=6で判定
            label5_P.grid(column=0, row=x + 2, sticky=tkinter.W)  # ’区間'の下からrow=1置きにラベルを配置表示する

label5_Pname = [['A', 'B', 'C', 'D', 'E', 'F', 'A', 'B', 'C', 'D', 'E', 'F']]  # ラベルデータをリストで用意
for y, row in enumerate(label5_Pname, 0):  # y=0のみ, row='A' row='B'........
    for x, char in enumerate(row):  # x=0, char=A x=1, char=B ........x=11, char=F
        if x < 6:  # X=0～5まではパルス幅入力欄
            label5_P = tkinter.Label(frame5, text=char, width=5)
        else:  # X=6～11まではパルス本数入力欄
            label5_P = tkinter.Label(frame5, text=char, width=3)
        label5_P.grid(column=x + 1, row=y + 1)  # '区間'と同じ行(row=1)で右にcolumn=1置きに移動させて表示する

for i in range(pulse_type):  # パルス幅設定Entry作成 pulse_type=7なので、0～6まで繰り返す （パルス種別数7）
    for n in range(6):  # 0～5まで繰り返す　区間（A～Fの6）
        pulse_wid_name[i][n] = tkinter.Entry(frame5, width=5)  # Entryボックスをframe5に作成 i:パルス種別、n:区間
        pulse_wid_name[i][n].insert(tkinter.END,
                                    pulse_width_array[i][n])  # 上で作成したEntryボックスにpulse_width_array[i][n]の値を挿入
        if i < pulse_disp_num or i == 6:  # pulse_disp_num = 6 なので結局x<=6で判定
            pulse_wid_name[i][n].grid(row=i + 2, column=n + 1)  # 上で作成したEntryボックスを配置表示  row=2,column=1から1行づつ配置

for i in range(pulse_type):  # パルス本数設定Entry作成 pulse_type=7なので、0～6まで繰り返す （パルス種別数7）
    for n in range(6):  # 0～5まで繰り返す　区間（A～Fの6）
        pulse_num_name[i][n] = tkinter.Entry(frame5, width=3)  # Entryボックスをframe5に作成 i:パルス種別、n:区間 本数なので、上の幅よりはwidth少ない
        pulse_num_name[i][n].insert(tkinter.END, pulse_num_array[i][n])  # 上で作成したEntryボックスにpulse_num_array[i][n]の値を挿入
        if i < pulse_disp_num or i == 6:  # pulse_disp_num = 6 なので結局x<=6で判定
            pulse_num_name[i][n].grid(row=i + 2, column=n + 7)  # 上で作成したEntryボックスを配置表示  row=2,column=7から1行づつ配置

Button5_20 = tkinter.Button(frame5, text=u'設定送信', width=12)  # ’設定送信'ボタン作成 u:unicode文字列が作成される
Button5_20.bind("<Button-1>", pulse_width_bot)  # <Button-1>"=マウスの左クリックにより、pulse_width_bot関数処理する
Button5_20.grid(row=pulse_type + 2, column=1,
                columnspan=2)  # '設定送信'ボタンを表示 row=9, column=1,Pr-6の欄の'A','B'column2つ分を1つとして表示する

Button5_21 = tkinter.Button(frame5, text=u'設定読込', width=12)  # '設定読込'ボタン作成
Button5_21.bind("<Button-1>", pulse_reading)  # <Button-1>"=マウスの左クリックにより、pulse_reading関数処理する
# Button5_21.grid(row=pulse_type+2,column=4,columnspan=2)       # ただし、'設定読込'ボタンは表示されていない

global width_name  # 上記の’設定読込'ボタンが無効化されているために、width_nameを表示するラベルは機能しない
width_name = tkinter.StringVar()  # StringVar()で読み込まれたテキスト変数でlabel5_21のテキスト表示を可変する仕組みだが機能しない
label5_21 = tkinter.Label(frame5, textvariable=width_name, width=15)
label5_21.grid(row=pulse_type + 2, column=6, columnspan=5)  # '設定送信'の横、F～Dの範囲にラベルが用意されるが、機能しないので何も表示されない
# ---------------- ~ Pulses幅/本数設定GUI ---------------------

# ---------------- Pulses出力設定GUI --------------------------
frame4 = tkinter.Frame(tk, pady=10, padx=10)  # <Pulse出力>ウィジェット用のフレーム作成
frame4.pack(anchor=tkinter.W)  # frame4を左端に配置　ただし、実際はメインウィンドウの横サイズに合わせられる

Label4_1 = tkinter.Label(frame4, text='<Pulse出力>', width=labewid_1, anchor='w')  # ラベル'<Pulse出力>'をframe4に配置指示　文字数半角16

Label4_2 = tkinter.Label(frame4, text='CW -0', width=8, anchor='w')  # ラベル'CW -0'をframe4に配置指示左　文字数半角8
Label4_3 = tkinter.Label(frame4, text='CCW-1', width=8, anchor='w')  # ラベル'CCW-1'をframe4に配置指示左　文字数半角8

Button4_1 = tkinter.Button(frame4, text=u'1step', width=7,
                           command=lambda: manual_pulse_out(0, 1))  # '1step'ボタン作成し、クリック時は、Nucleoにコマンド'z'送信
Button4_2 = tkinter.Button(frame4, text=u'Any step', width=7,
                           command=lambda: manual_pulse_out(0, 0))  # 'Any step'ボタン作成し、クリック時は、Nucleoにコマンド'b'送信
Button4_3 = tkinter.Button(frame4, text=u'360step', width=7,
                           command=lambda: manual_pulse_out(0, 360))  # '360step'ボタン作成し、クリック時は、Nucleoにコマンド'a'送信
Button4_4 = tkinter.Button(frame4, text=u'1step', width=7,
                           command=lambda: manual_pulse_out(1, 1))  # '1step'ボタン作成し、クリック時は、Nucleoにコマンド'x'送信
Button4_5 = tkinter.Button(frame4, text=u'Any step', width=7,
                           command=lambda: manual_pulse_out(1, 0))  # 'Any step'ボタン作成し、クリック時は、Nucleoにコマンド'n'送信
Button4_6 = tkinter.Button(frame4, text=u'360step', width=7,
                           command=lambda: manual_pulse_out(1, 360))  # '360step'ボタン作成し、クリック時は、Nucleoにコマンド's'送信
Button4_7 = tkinter.Button(frame4, text=u'Pr', width=7,
                           command=lambda: manual_pulse_out(2, 1))  # 'Pr'ボタン作成し、クリック時は、Nucleoにコマンド'q'送信
Button4_8 = tkinter.Button(frame4, text=u'Any 往復', width=7,
                           command=lambda: manual_pulse_out(3, 0))  # 'Any往復'ボタン作成し、クリック時は、Nucleoにコマンド'n'送信,コマンド'b'送信

global Box4_4
Label4_4 = tkinter.Label(frame4, text='Vm設定[V]', width=10, anchor='e')  # ラベル'Vm設定[V]'の作成、配置は右
Box4_4 = tkinter.Entry(frame4, width=4)  # Entry入力欄作成
Box4_4.insert(tkinter.END, 3.0)  # Entryに3.0を挿入

chk4_5 = tkinter.Checkbutton(frame4, variable=stepvm_en, text='step±', width=10,
                             anchor='e')  # チェックボタン'step±'作成、テキストの配置は右
Box4_5 = tkinter.Entry(frame4, width=4)  # Entry入力欄作成
Box4_5.insert(tkinter.END, 0.1)  # Entryに0.1挿入

# ****** Box4_6 ~ Box4_8は作成されるが、メインウインドウ上に表示していない **********
Box4_6 = tkinter.Entry(frame4, width=7)  # Entryの作成
Box4_6.insert(tkinter.END, 1.4)  # 作成したEntryに1.4挿入
Box4_7 = tkinter.Entry(frame4, width=7)  # Entryの作成
Box4_7.insert(tkinter.END, 3.4)  # 作成したEntryに3.4挿入
Box4_8 = tkinter.Entry(frame4, width=7)  # Entryの作成
Box4_8.insert(tkinter.END, 0.2)  # 作成したEntryに0.2挿入
# *************************************************************************

# <Pulse出力>欄のウィジェットの表示指定
Label4_1.grid(row=0, column=0, columnspan=2, sticky=tkinter.W)  # ラベル'<Pulse出力>'の表示指示　左
Label4_2.grid(row=1, column=0)  # ラベル'CW -0'の表示指示
Label4_3.grid(row=2, column=0)  # ラベル'CCW-1'の表示指示

Button4_1.grid(row=1, column=1)  # ボタン'1step'の表示指示 CW -0
Button4_2.grid(row=1, column=2)  # ボタン'Anystep'の表示指示 CW -0
Button4_3.grid(row=1, column=3)  # ボタン'360step'の表示指示 CW -0
Button4_4.grid(row=2, column=1)  # ボタン'1step'の表示指示 CCW-1
Button4_5.grid(row=2, column=2)  # ボタン'Anystep'の表示指示 CCW-1
Button4_6.grid(row=2, column=3)  # ボタン'360step'の表示指示 CCW-1
Button4_7.grid(row=1, column=4)  # ボタン'Pr'の表示指示 CW -0
Button4_8.grid(row=2, column=4)  # ボタン'Any往復'の表示指示 CCW-1

Label4_4.grid(row=1, column=5)  # ラベル'Vm設定[V]'の表示指示
Box4_4.grid(row=1, column=6)  # Entryの表示指示
chk4_5.grid(row=2, column=5)  # チェックボタン'step±'の表示指示
Box4_5.grid(row=2, column=6)  # Entryの表示指示
# ---------------- ~ Pulses出力設定GUI ------------------------

# ---------------- オプション機能設定GUI --------------------
frame7 = tkinter.Frame(tk, pady=10, padx=10)  # <オプション機能>のウィジェット用のフレーム作成
frame7.pack(anchor=tkinter.W)  # フレームの表示指示　左

Label7_1 = tkinter.Label(frame7, text='<オプション機能>', width=labewid_1, anchor='w')  # ラベル'<オプション機能>の作成　左
Label7_1.grid(row=0, column=0, columnspan=3)  # ラベルの表示指示 column 3個結合

Button7_1 = tkinter.Button(frame7, text=u'シーケンス機能', width=12,
                           command=sequence_window)  # ボタン'シーケンス機能'を作成、選択時sequence_window関数を実行　関数名のみ
# Button7_1.bind("<Button-1>",sequence_window)
Button7_1.grid(row=1, column=3, columnspan=2)  # ボタンの表示指示、column　2個結合

Button7_2 = tkinter.Button(frame7, text=u'パルス列設定', width=12)  # ボタン'パルス列設定'を作成
Button7_2.bind("<Button-1>", pulsetrain_window)  # ボタンが左クリックされたら、pulsetrain_window関数を実行 関数名のみ
Button7_2.grid(row=1, column=1, columnspan=2)  # ボタンの表示指示、column　2個結合

Button7_3 = tkinter.Button(frame7, text=u'カメラ機能', width=10)  # ボタン'カメラ機能'を作成
Button7_3.bind("<Button-1>", cam_window)  # ボタンが左クリックされたら、cam_window関数を実行 関数名のみ
Button7_3.grid(row=1, column=5, columnspan=2)  # ボタンの表示指示、column　2個結合

'''
Button7_4 = tkinter.Button(frame7, text=u'PI 針位置', width=12,
                            command = pi_window)                # ボタン'PI 針位置'を作成　入力が有ったら、pi_window関数実行　関数名のみ
#Button7_4.bind("<Button-1>",pi_window)                 # 上記でボタンが押された時の処理を実行するのでコメントアウト
Button7_4.grid(row=1,column=7,columnspan=2)             # ボタンの表示指示、column　2個結合
'''

Button7_5 = tkinter.Button(frame7, text=u'Vrs 回転検出', width=12,
                           command=vrs_window)  # ボタン'vrs 回転検出'を作成 入力されたら、vrs_window関数実行 関数名のみ
# Button7_5.bind("<Button-1>",vrs_window)               # 上記でボタンが押された時の処理を実行するので、コメントアウト
Button7_5.grid(row=1, column=9, columnspan=2)  # ボタンの表示指示、column　2個結合
# ---------------- ~ オプション機能設定GUI ---------------------
# ---------------- ~ main window作成 -------------------------
###############
####初期設定###
if Com_No != 'Nucleo未接続':
    Button1_1.config(state="disable")  # ボタン無効化

    read_serial()  # Nucleoのver読み込み
    nucleo_revchek()  # Python側とNucleo側のver.比較
    manual_pulse_set()  # GUIのPulse設定欄の値を読み込み、Nucleoに送信設定する
    pulse_train_set()  # パルス列設定送信
    pulse_width_set()  # パルス幅、本数設定送信
    vm_set()  # Vm設定値をGUI上のBoxから読み込み、送信設定する
    print('init end')

# vrs_windowset()

# print(tk.winfo_geometry())
# print(tk.winfo_rootx())#ディスプレイ上での位置
# print(tk.winfo_y())
# print(tk.winfo_x())
# print(tk.winfo_width())
# print(tk.winfo_exists())#windowが存在するか

# メインウインドウのループ処理
tk.mainloop()
