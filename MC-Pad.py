"""
このファイルは、理解のためにver1.8にコメントを追記したファイルです。
プログラムは、そのままで、軽微な整形（#XXX⇒#　XXX）等も合わせて実施しています。
"""
# ------------ モジュールインポート ---------------------------------
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
# ---------------------------------------------------------
tk = tkinter.Tk()       # Tk()メソッドでルートウインドウtkを作る tk.mainloop()を最後に実行してウインドウを表示する

rev_name = 'rev1.8'  # Nucleoで表示するRevと合わせる必要あり
Software_name = 'MC-Pad ' + rev_name + ' ~Pulse Analysis & Development~'
wait_uart = 0.005  # UART送信後の待ち時間 通信エラーおこる場合は大きくする

# NUCLEO COMポート検索-----------------------------------------------
global ser
global Com_No
ports = list_ports.comports()       # 接続されているcomポートのリストを取得、2つのcomポートを使っていればリスト2つ。
# 取得できたportsリストの中から、デバイス名に"STLink"があるデバイスのみを取り出す
device = [info for info in ports if "STLink" in info.description]  # .descriptionでデバイスの名前を取得出来る
if not len(device) == 0:    # 上記条件に合う場合、device !=0なので以下の式に入る
    ser = serial.Serial(device[0].device)       # 名前に"STlink"があるcomポートの設定値を読み込む
    Com_No = str(device[0])     # リストdeviceの[0]はListPortInfo
    print(Com_No + ' open')
    ser.baudrate = 921600  # 通信速度の設定変更
    ser.timeout = None  # timeoutなし
    ser.send_break()  # Brake信号送信 Nucleo reset

else:
    Com_No = 'Nucleo未接続'
    print('Nucleoが接続されていません')
# ～2022.8.22
# ---------------------------------------------------------------------

# Tkinter関係変数------------------------------------------------------
pulse_disp_num = 6  # UIに表示するパルスの数
labewid_1 = 16  # ラベルの幅
boxwid_1 = 10
pulsemode_0 = tkinter.BooleanVar()  # チェックボックス変数
pulsemode_1 = tkinter.BooleanVar()  # チェックボックス変数
pulsemode_2 = tkinter.BooleanVar()  # チェックボックス変数
pulsemode_3 = tkinter.BooleanVar()  # チェックボックス変数
pulsemode_4 = tkinter.BooleanVar()  # チェックボックス変数
pulsemode_5 = tkinter.BooleanVar()  # チェックボックス変数
stepvm_en = tkinter.BooleanVar()  # チェックボックス変数

# Pulse設定配列
pulse_set_array = [['' for i in range(20)] for j in range(1)]  # 2次元配列定義
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
pulse_wid_name = [  # パルス幅Entry配置名前
    ['wid0_A', 'wid0_B', 'wid0_C', 'wid0_D', 'wid0_E', 'wid0_F'],
    ['wid1_A', 'wid1_B', 'wid1_C', 'wid1_D', 'wid1_E', 'wid1_F'],
    ['wid2_A', 'wid2_B', 'wid2_C', 'wid2_D', 'wid2_E', 'wid2_F'],
    ['wid3_A', 'wid3_B', 'wid3_C', 'wid3_D', 'wid3_E', 'wid3_F'],
    ['wid4_A', 'wid4_B', 'wid4_C', 'wid4_D', 'wid4_E', 'wid4_F'],
    ['wid5_A', 'wid5_B', 'wid5_C', 'wid5_D', 'wid5_E', 'wid5_F'],
    ['wid6_A', 'wid6_B', 'wid6_C', 'wid6_D', 'wid6_E', 'wid6_F'], ]

pulse_num_name = [  # パルス本数Entry配置名前
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

pulse_train_array = [['' for i in range(12)] for j in range(7)]  # 2次元配列定義
pulse_train_array_str = [['' for i in range(12)] for j in range(7)]  # 2次元配列定義

pulse_train_array_name = [['' for i in range(12)] for j in range(7)]  # 2次元配列定義
for i, row in enumerate(pulse_train_array_name, 0):  # i=行番号、row=行内容
    for n, col in enumerate(row):  # n=列番号、col=列内容
        col = 'pat' + str(i) + str(n)  #

pulse_num_array = [  # パルス本数設定配列
    [1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1],
    [1, 1, 10, 1, 1, 1]]

pulse_train_name = [0] * 7
pulse_train_labename = [0] * 7
for i, row in enumerate(pulse_train_labename, 0):  # i=行番号、row=行内容
    col = 'trname' + str(i)  #

# シーケンスEntry配置名　行(row)数=シーケンス数、列(col)数=パラメータ数
sequence_name = [['' for col in range(10)] for row in range(10)]
for i, row in enumerate(sequence_name, 0):  # i=行番号、row=行内容
    for n, col in enumerate(row):  # n=列番号、col=列内容
        col = 'se' + str(i) + str(n)  # seq00,seq01....seq(i)(n)

seq_runopt = 0
sequence_array = [[0] * 10 for row in range(10)]  # 2次元配列を0で初期化
for i, row in enumerate(sequence_array, 0):
    if i == 0:
        sequence_array[i] = [1, 40, 200, 1, 0, 0, 0, 0, 0, 3.0]  # シーケンス設定配列 初期値
    else:
        sequence_array[i] = [0, 0, 200, 0, 0, 0, 0, 0, 0, 3.0]  # シーケンス設定配列 初期値

seq_jdge_array = [0] * 7  # 判定方法選択　0 フォト判定/1 Vrs判定/2フォトNG停止3/周波数設定/4保存/5詳細保存/6評価パルス設定
for i, row in enumerate(seq_jdge_array, 0):
    seq_jdge_array[i] = tkinter.BooleanVar()

# カメラ関係変数
# cam_list = []
cam_no = 0
cam_delaylist = [100, 300, 500, 700, 1000]
cam_delay = cam_delaylist[1]

# フォト位置検出変数
# global entrypi2_3
# piseq_save = tkinter.BooleanVar() #チェックボックス変数
# piseq_save_det = tkinter.BooleanVar() #チェックボックス変数
# piseq_stop = tkinter.BooleanVar()
# piseq_freq = tkinter.BooleanVar()
piseq_section = [0] * 6
for i in range(6):
    piseq_section[i] = tkinter.BooleanVar()

piset_name = [0] * 6
piset_array = [0, 360, 200, 3.0, 0, 0]  # Photo検出時のパルス設定
piresult = ['pires0', 'pires1', 'pires2']

piset_value_name = [[0] * 3 for row in range(4)]
piset_value_array = [[2.4, 1.2, 0.1], [1.0, 1.0, 0.1], [200, 200, 20], ['1']]
# result_data =[['' for col in range(30)] for row in range(100)]

# vrsウィンドウ変数
vrswindow_flag = 0
vrsdt_name = [0] * 4
vrsdt_array = [1500, 2700, 4000, 8000]  # Dt区間
vrsjdg_name = [0] * 16
vrsjdg_array = [1, 1, 0, 1,
                0, 1, 0, 1,
                1, 1, 0, 1,
                0, 1, 0, 1]
df_vrs_res = pd.DataFrame()


# //シリアルポート制御サブルーチン-----------------------------
def Select_COM(event):
    Com_No = Box1_1.get()  # get()でエントリーボックス値取得
    print(Com_No + ' open')
    Com_No = str(Com_No)
    ser.open()  # シリアルポートOPEN
    # ser.flush()#コマンド送信完了するまで待機
    time.sleep(wait_uart)
    manual_pulse_set()
    pulse_train_set()  # パルス列設定送信
    pulse_width_set()  # パルス幅設定送信
    vm_write()
    print('init end')
    Button1_2.config(state="normal")  # ボタン無効化
    Button1_1.config(state="disable")  # ボタン無効化


def Close_COM(event):
    ser.send_break()  # Brake信号送信 Nucleo reset
    time.sleep(1)
    Com_No = Box1_1.get()
    print(Com_No + ' close')
    ser.close()  # シリアルポートCLOSE
    Button1_1.config(state="normal")  # ボタン無効化
    Button1_2.config(state="disable")  # ボタン無効化


def nucleo_revchek():
    ser.write(b'v')  # シリアル通信:送信
    ver_str = read_serial2()
    print('chk' + ver_str)
    if (rev_name in ver_str):
        time.sleep(0.001)
    else:
        tkinter.messagebox.showerror('エラー', 'Nucleoをアップデートする必要があります')


# --------------------------------------------------------
# ボタン押し実行サブルーチン-------------------------------
def manual_pulse_bot(event):
    thread_pul = threading.Thread(target=manual_pulse_set)
    Button3_1.config(state="disable")  # ボタン無効化
    thread_pul.start()  # スレッド(並列)処理


def pulse_width_bot(event):  # パルス幅/本数をBoxから読み取り
    thread_pul = threading.Thread(target=pulse_width_set)
    Button5_20.config(state="disable")  # ボタン無効化
    thread_pul.start()  # スレッド(並列)処理


def pulse_seq_bot(event):
    thread_seq = threading.Thread(target=pulse_seq_run)
    seq_run.set('実行中')
    Button6_1.config(state="disable")  # ボタン無効化
    thread_seq.start()  # スレッド(並列)処理


def pulse_seqread_bot(event):
    thread_seqread = threading.Thread(target=seq_setting)
    Button6_2.config(state="disable")  # ボタン無効化
    thread_seqread.start()  # スレッド(並列)処理


def pulse_train_bot(event):
    thread_tr = threading.Thread(target=train_setting)
    Button8_1.config(state="disable")  # ボタン無効化
    thread_tr.start()  # スレッド(並列)処理


def photo_init_bot(event):
    thread_phini = threading.Thread(target=photo_init)
    Buttonpi_1.config(state="disable")  # ボタン無効化
    thread_phini.start()  # スレッド(並列)処理


def photo_posiset_bot(event):
    thread_phset = threading.Thread(target=photo_posiset_manu)
    Buttonpi_2.config(state="disable")  # ボタン無効化
    thread_phset.start()  # スレッド(並列)処理


def photo_posicheck_bot(event):
    thread_phche = threading.Thread(target=photo_posicheck)
    Buttonpi_3.config(state="disable")  # ボタン無効化
    thread_phche.start()  # スレッド(並列)処理


def photo_seqtest_bot(event):
    thread_phche = threading.Thread(target=seqrun_repeat)
    Buttonpi2_1.config(state="disable")  # ボタン無効化
    Buttonpi2_2.config(state="normal")  # ボタン無効化
    thread_phche.start()  # スレッド(並列)処理


def photo_seqtest_stop_bot(event):
    thread_phche = threading.Thread(target=photo_seqtest_stop)
    Buttonpi2_2.config(state="disable")  # ボタン無効化
    thread_phche.start()  # スレッド(並列)処理


def vrs_winset(event):
    vrs_win.vrs_window(tk, '+' + str(xposi) + '+' + str(yposi))


# -------------------------------------------------------
# NUCLEOパルス設定書込み------------------------------------
def command_write(command, set_num):
    if command != 'x':
        ser.write(bytes(command, 'utf-8'))  # バイト型で送信
        # ser.flush()#コマンド送信完了するまで待機
        time.sleep(wait_uart)
    ser.write(bytes(pulse_set_array[0][set_num], 'utf-8'))
    ser.write(b'\r')
    read_serial()


def pulse_select_set():
    ser.write(b'1')  # シリアル通信:送信
    # ser.flush()#コマンド送信完了するまで待機
    time.sleep(wait_uart)
    ser.write(bytes(pulse_set_array[0][pulse_set_n], 'utf-8'))
    read_serial()
    read_serial()


def pmode_set():
    mode = 0b00000
    if pulsemode_4.get() == 1:
        mode = mode | 0b10000
    if pulsemode_3.get() == 1:
        mode = mode | 0b01000
    if pulsemode_2.get() == 1:
        mode = mode | 0b00100
    if pulsemode_1.get() == 1:
        mode = mode | 0b00010
    if pulsemode_0.get() == 1:
        mode = mode | 0b00001
    ser.write(b'6')  # シリアル通信:送信
    # ser.flush()#コマンド送信完了するまで待機
    time.sleep(wait_uart)
    ser.write(bytes(str(mode), 'utf-8'))
    ser.write(b'\r')
    read_serial()
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
    global pulse_set_array
    pulse_set_array[0][pulse_set_n] = Pulse_cb.get()[0]
    pulse_set_array[0][wait_set_n] = Box3_2.get()
    pulse_set_array[0][anystep_n] = Box3_3.get()
    pulse_set_array[0][pewidth_n] = Box3_4.get()
    pulse_set_array[0][pewait_n] = Box3_5.get()
    pulse_set_array[0][spkperiod_n] = Box3_7.get()
    pulse_set_array[0][spkon_n] = Box3_8.get()
    pulse_set_array[0][Vth_set_n] = Box3_9.get()
    print(pulse_set_array)
    pulse_select_set()
    command_write('2', wait_set_n)  # wait time 設定
    command_write('7', anystep_n)  # 任意step数設定
    command_write('8', pewidth_n)  # Pe設定
    command_write('x', pewait_n)
    command_write('-', spkperiod_n)  # spk設定
    command_write('x', spkon_n)
    command_write('o', Vth_set_n)  # Vth設定
    pmode_set()
    Button3_1.config(state="normal")  # ボタン有効化


def read_entry(name, array):  # entry読み出し(entry名，書込み先)
    for i, row in enumerate(name, 0):
        for n, col in enumerate(row):
            array[i][n] = col.get()


# --------------------------------------------------------
def pulse_para_write(command, data, botno):  # パルスパラメータNucleo書込み(コマンド,入力値,有効化するボタン名 xだったら何もしない)
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
    read_entry(pulse_wid_name, pulse_width_array)
    read_entry(pulse_num_name, pulse_num_array)

    pulse_para_write('3', pulse_width_array, 'x')
    pulse_para_write('4', pulse_num_array, Button5_20)


def pulse_train_set():
    pulse_para_write('p', pulse_train_array, 'x')


# --------------------------------------------------------------------
# 電圧設定関係サブルーチン----------------------------------------------
def vm_write():
    global vm_value
    vm_value = Box4_4.get()
    pulse_set_array[0][Vm_set_n] = Box4_4.get()
    command_write('^', Vm_set_n)


def insert_vm(vm_disp):  # UI表示更新
    Box4_4.delete(0, tkinter.END)
    Box4_4.insert(tkinter.END, vm_disp)


def vm_set():
    global vm_value
    vm_value = pulse_set_array[0][Vm_set_n]
    if vm_value != Box4_4.get():
        if float(Box4_4.get()) < vm_minmum:
            tkinter.messagebox.showerror('エラー', 'Vmは' + str(vm_minmum) + 'V以上としてください')
            insert_vm(vm_minmum)
        elif float(Box4_4.get()) > vm_maximum:
            tkinter.messagebox.showerror('エラー', 'Vmは' + str(vm_maximum) + 'V以上としてください')
            insert_vm(vm_maximum)
        vm_write()


def vm_up(step):
    global vm_value
    vm_value = str(round(float(vm_value) + float(step), 2))  # 小数点2桁にしてStr
    insert_vm(vm_value)
    vm_set()


# -----------------------------------------------------------------------------------
# 任意stepパルス出力
def manual_pulse_out(dire, step):
    vm_set()
    if dire == 0:
        if step == 1:
            ser.write(b'z')  # シリアル通信:送信
        elif step == 0:
            ser.write(b'b')  # シリアル通信:送信
        elif step == 360:
            ser.write(b'a')  # シリアル通信:送信
    if dire == 1:
        if step == 1:
            ser.write(b'x')  # シリアル通信:送信
        elif step == 0:
            ser.write(b'n')  # シリアル通信:送信
        elif step == 360:
            ser.write(b's')  # シリアル通信:送信
    if dire == 2:
        ser.write(b'q')  # シリアル通信:送信
    if dire == 3:  # CW→CCW往復
        ser.write(b'n')  # シリアル通信:送信
        read_serial()
        ser.write(b'b')  # シリアル通信:送信
    # read_serial()
    vrstime_print()
    if stepvm_en.get() == 1:
        vm_up(Box4_5.get())


# シーケンス動作実行---------------------------------------
def pulse_seq_run():
    wait_seq = 0.0005
    if seq_runopt == 0:
        read_entry(sequence_name, sequence_array)  # entry値読み出し
    ser.write(b'5')  # シリアル通信:送信
    # ser.flush()#コマンド送信完了するまで待機
    time.sleep(wait_uart)
    seqset_err = 0
    for i, row in enumerate(sequence_name, 0):  # 設定書き込み
        # read_serial()
        for n in range(3):
            ser.write(bytes(sequence_array[i][n], 'utf-8'))
            ser.write(b'\r')
            # read_serial()
            time.sleep(wait_seq)
            if n < 2:
                ser.write(b'0\r')  # M1設定は0
                # read_serial()
                time.sleep(wait_seq)
        mode = 0b000000
        for n in range(6):  # option書込み
            # print(sequence_array[i][n+3])
            if sequence_array[i][n + 3] == '1':
                mode = mode | (2 ** n)
                # print(mode)
        ser.write(bytes(str(mode), 'utf-8'))
        ser.write(b'\r')
        # read_serial()
        time.sleep(wait_seq)
        # 電圧設定書込み
        if float(sequence_array[i][9]) < 0.8:  # 電圧下限チェック
            sequence_array[i][9] = 0.8
            if int(sequence_array[i][1]) != 0:  # step設定が0stepならエラーにしない
                seqset_err = 2
        elif float(sequence_array[i][9]) > 4.0:  # 電圧上限チェック
            sequence_array[i][9] = 4.0
            if int(sequence_array[i][1]) != 0:  # step設定が0stepならエラーにしない
                seqset_err = 2
        # print(seqset_err)
        ser.write(bytes(str(sequence_array[i][9]), 'utf-8'))
        ser.write(b'\r')
        read_serial()
    while 1:
        resp_str = read_serial2()
        if (resp_str == 'End!'):
            break
    if seqset_err == 0:
        ser.write(b'9')  # シリアル通信　シーケンススタート
        # read_serial()
        vrstime_print()
    elif seqset_err == 2:
        tkinter.messagebox.showerror('エラー', '電圧設定は0.8~4Vにしてください')

    if seq_runopt == 0:
        manual_pulse_set()
        vm_write()
    Button6_1.config(state="normal")  # ボタン有効化
    seq_run.set('単独実行')  # ボタン表示変更


def seqrange_output(cnt, test_cnt, save):
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
                    seq_run_vm(test_cnt)  # 電圧可変テスト
                    test_cnt += 1

                    freq_test = freq_test + int(piset_value_array[2][2])
                    if seq_runopt == 2 or piset_value_array[2][2] == str(0) or seq_jdge_array[3].get() == 1:
                        freq_test = int(piset_value_array[2][1]) + 1
                wid_test = round(wid_test + float(piset_value_array[1][2]), 2)
                if seq_runopt == 2 or piset_value_array[1][2] == str(0):
                    wid_test = float(piset_value_array[1][1]) + 1

        seqrange_output(0, test_cnt, 1)  # 動作MAPファイル保存

    seqrange_output(0, test_cnt, 2)  # Vrs詳細ファイル保存(Rename)
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
    global seq_runopt
    global vm_test

    vm_test = round(piset_value_array[0][0], 2)

    cnt = 0
    posiset_flag = 1
    if seq_jdge_array[0].get() == 1:  # フォト判定が有効だったら
        posiset_flag = 0
    while 1:
        for i, col in enumerate(sequence_array, 0):
            sequence_array[i][9] = vm_test
        piseq_res.insert('end', str('{:.2f}'.format(vm_test)) + "V")  # 小数点以下3桁で表示
        insert_vm(str('{:.2f}'.format(vm_test)))

        # フォト判定　基準位置検出
        if seq_jdge_array[0].get() == 1:  # フォト判定が有効だったら
            if 'OK' in piresult[2].get():
                # if piresult[2].get() == 'OK':
                posiset_flag = 1
            else:
                posiset_flag = photo_seq_set(posiset_flag, cnt, test_cnt)  # 初期位置セット

        if posiset_flag == 1:
            pulse_seq_run()  # シーケンス動作実行

        if posiset_flag == 1:
            if seq_jdge_array[0].get() == 1:  # フォト判定が有効だったら
                posiset_flag = photo_seq_check(cnt, test_cnt)  # 位置確認
            seqrange_output(cnt, test_cnt, 0)  # 結果保存用リスト作成
            if posiset_flag == 2:
                piseq_res.insert('end', "\n")
                break
        piseq_res.insert('end', "\n")
        piseq_res.see("end")
        vm_test = round(vm_test + piset_value_array[0][2], 2)
        if piset_value_array[0][2] > 0:
            if piset_value_array[0][1] < vm_test:
                break
        if piset_value_array[0][2] < 0:
            if piset_value_array[0][1] > vm_test:
                break

        if seq_runopt == 2:
            piseq_res.insert('end', "途中終了\n")
            piseq_res.see("end")
            break
        cnt += 1


# エントリーBoxに書込み--------------------------------------------
def insert_entry(name, array):
    for i, row in enumerate(name, 0):
        for n, col in enumerate(row):
            col.delete(0, tkinter.END)
            col.insert(tkinter.END, array[i][n])


def insert_train():
    for y, row in enumerate(pulse_train_array_name, 0):
        for x, char in enumerate(row):
            # pulse_train_array_name[y][x] = pulse_train_array_str[y][x]
            char.set(pulse_train_array_str[y][x])


# チェックボックス書込み-------------------------------
def set_checkbox(name, array):
    for x, col in enumerate(array, 0):
        name[x].set(array[x])

    # ファイル書込み-------------------


def csv_write(array, folder, fname, mode):  # mode:w=新規、a=追記
    # now = datetime.datetime.now()
    with open(os.getcwd() + '/' + folder + '/' + fname + '.csv', mode, newline="") as f:
        writer = csv.writer(f)
        writer.writerows(array)


# ファイル読み込み-----------------------------------------------
def filepath_get(name, setting):  # setting 0:1ファイル、1:複数ファイル
    # global  filepath
    # 選択候補を拡張子jpgに絞る（絞らない場合は *.jpg → *）
    filetype = [("", "*" + name + "*.xlsx")]
    dirpath = os.getcwd()  # os.path.dirname(__file__)#''
    # print(dirpath)

    # 選択したファイルのパスを取得
    if setting == 1:
        filepath = tkinter.filedialog.askopenfilenames(filetypes=filetype, initialdir=dirpath)
    else:
        filepath = tkinter.filedialog.askopenfilename(filetypes=filetype, initialdir=dirpath)
    return filepath


def pulse_reading(event):
    # global  filepath
    filepath = filepath_get('width', 0)
    width_name.set(os.path.basename(filepath))
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
    global seq_path
    seq_path = filepath_get('seq', 1)  # ファイル選択ウィンドウ,複数ファイル選択可

    seq_filelist = ['表示設定']
    for i, row in enumerate(seq_path, 0):
        seq_filelist.append(os.path.splitext(os.path.basename(row))[0])
    seq_filelist.append('全て実行')

    Combopi1["values"] = seq_filelist
    Combopi1.current(0)  # 初期値
    # print(str(Combopi1.current()))
    seq_update(seq_path[0])


def seq_reading(event):  # 読み込みボタン処理
    if 'seq_path' in globals():
        if (Combopi1.current() != 0) and (Combopi1.get() != "全て実行"):
            seq_update(seq_path[Combopi1.current() - 1])


def seq_update(filepath):
    # filepath = filepath_get('seq',0)#ファイル選択ウィンドウ

    seqWindow.lift()  # シーケンスwindowをtopへ
    try:  # エラー発生した場合、except実行
        seq_filename = os.path.splitext(os.path.basename(filepath))[0]
        seq_filename = seq_filename.replace('_seq', '')
        seq_name.set(seq_filename)  # 読み込みファイル名表示
        global sequence_array

        df_seq_all = pd.read_excel(str(filepath), index_col=0, sheet_name=None)
        df_seq_raw = df_seq_all['seq']  # シート毎のデータに
        df_op_raw = df_seq_all['option']
        # シーケンス動作設定
        df_seq = df_seq_raw.loc[:, 'pulse':'1sec'].astype(str)
        df_seq['Vm'] = df_seq_raw['Vm']
        sequence_array = df_seq.values.tolist()  # Dataframeをlistに変換
        insert_entry(sequence_name, sequence_array)
        # 電圧、パルス幅、周波数設定
        df_op_vm = df_op_raw.loc['voltage':'freq', 'start':'step'].astype(str)
        piset_value_array = df_op_vm.values.tolist()  # Dataframeをlistに変換
        insert_entry(piset_value_name[:3], piset_value_array)
        # 区間のパルス幅変更有無
        df_op_sec = df_op_raw.loc['pulse', 'A':'F'].astype(int)
        sec_array = df_op_sec.values.tolist()  # Dataframeをlistに変換
        set_checkbox(piseq_section, sec_array)
        # 判定実施の有無
        df_op_jdge = df_op_raw.loc['判定', 'start':'C'].fillna(0).astype(int)
        jdge_array = df_op_jdge.values.tolist()  # Dataframeをlistに変換
        # jdge_array = jdge_array.fillna(0) #欠損値Nanを0に置換 旧seqfile対応
        set_checkbox(seq_jdge_array, jdge_array)
        # フォトインタラプタ設定
        df_op_pi = df_op_raw.loc['PI設定', 'start':'C'].astype(int)
        piset_array = df_op_pi.values.tolist()  # Dataframeをlistに変換
        print(piset_array[1:5])
        for i, col in enumerate(piset_name, 0):
            if i == 0 or i == 4:
                col.current(int(piset_array[i]))
            else:
                col.delete(0, tkinter.END)
                col.insert(tkinter.END, piset_array[i])

        Button6_2.config(state="normal")  # ボタン有効化

        # seqWindow.attributes("-topmost", True) #windowをtopに表示

    except(FileNotFoundError, TypeError):
        tkinter.messagebox.showerror('エラー', 'seq.xlsxファイルが見つかりません')
    except:
        tkinter.messagebox.showerror('エラー', 'seq.xlsxファイル読み込みに失敗しました')


def train_sort(array_name):  # パルス数が6以下の場合に配列の行を合わせる
    global pulse_disp_num
    pulse_disp_num = len(array_name) - 1
    array_num = len(array_name) - 1
    array_prov = []  # 編集用の配列
    n = 0
    row_0 = [0] * len(array_name[0])
    while n < array_num:
        array_prov.append(array_name[n])
        n += 1
    while n < 6:
        array_prov.append(row_0)
        n += 1
    array_prov.append(array_name[array_num])
    return array_prov


def train_conv():  # パルス列を記号に変換
    for y, row in enumerate(pulse_train_array, 0):
        for x, col in enumerate(row):
            aph1 = (int(str(col), 2) >> 2) & 0b11  # 文字列を2進数として読み込んでビット取り出し
            aph2 = (int(str(col), 2) >> 6) & 0b11
            bph1 = (int(str(col), 2) >> 0) & 0b11
            bph2 = (int(str(col), 2) >> 4) & 0b11

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


def train_reading(readfile):
    global pulse_train_array
    global pulse_width_array
    global pulse_num_array
    global pulse_train_name
    global vrsdt_array
    global vrsjdg_array

    try:
        df_tr_raw = pd.read_excel(str(readfile), index_col=0)
        print(df_tr_raw)
        # print('test:'+ df_tr_raw.index)
        # print( True in df_tr_raw.index.isin(['Dt区間']))

        pulse_train_array = df_tr_raw.loc['P0_tr':'Pr_tr', 'A1':'F2'].astype(int).values.tolist()  # Dataframeをlistに変換
        pulse_width_array = df_tr_raw.loc['P0_wd':'Pr_wd', 'A1':'F1'].astype(int).values.tolist()  # Dataframeをlistに変換
        pulse_num_array = df_tr_raw.loc['P0_wd':'Pr_wd', 'A2':'F2'].astype(int).values.tolist()  # Dataframeをlistに変換
        pulse_train_name = df_tr_raw.loc['P0_tr':'Pr_tr', 'type'].astype(str).values.tolist()

        pulse_train_array = train_sort(pulse_train_array)
        pulse_width_array = train_sort(pulse_width_array)
        pulse_num_array = train_sort(pulse_num_array)

        n = len(pulse_train_name) - 1
        while n < 6:
            pulse_train_name.insert(n, '設定なし')
            n += 1

        if True in df_tr_raw.index.isin(['Dt区間']):
            vrsdt_array = df_tr_raw.loc['Dt区間', 'type':'C1'].astype(int).values.tolist()
            vrsjdg_array = (df_tr_raw.loc['patA', 'type':'A2'].astype(int).values.tolist()
                            + df_tr_raw.loc['patB', 'type':'A2'].astype(int).values.tolist())
            # vrsWindow()

            if 'vrsWindow' in globals():  # vrsウィンドウが開かれたことがあるか?
                if vrsWindow.winfo_exists() == 1:  # vrsウィンドウが開かれているか？
                    vrsWindow.destroy()
                    vrs_window()

        # print(pulse_train_name)
        # print(pulse_train_array)
        # print(pulse_width_array)

    except(FileNotFoundError, TypeError):
        tkinter.messagebox.showerror('エラー', 'train.xlsxファイルが見つかりません')
    except:
        tkinter.messagebox.showerror('エラー', 'train.xlsxファイル読み込みに失敗しました')


def train_setting():
    # global  filepath
    filepath = filepath_get('train', 0)

    trainWindow.lift()  # パルス列windowをtopへ
    train_reading(filepath)

    for y, row in enumerate(pulse_train_labename, 0):
        row.set(pulse_train_name[y])

    train_conv()
    # print('check')
    insert_train()
    # print('check2')

    insert_entry(pulse_wid_name, pulse_width_array)  # entryに書込み
    insert_entry(pulse_num_name, pulse_num_array)  # entryに書込み

    pulse_width_set()  # パルス幅設定送信
    pulse_train_set()  # パルス列設定送信

    Button8_1.config(state="normal")  # ボタン有効化


# スクリーンショット#############
def screen_shot(handle1, handle2, fname):
    # 最前面のウィンドウのスクショを取得する
    # handle = win32gui.GetForegroundWindow() # 最前面のウィンドウハンドルを取得
    rect1 = win32gui.GetWindowRect(handle1)  # ウィンドウの位置を取得
    rect2 = win32gui.GetWindowRect(handle2)  # ウィンドウの位置を取得
    im1 = ImageGrab.grab().crop(rect1)
    im2 = ImageGrab.grab().crop(rect2)


def screen_shot(handle):
    # handle = win32gui.GetForegroundWindow() # 最前面のウィンドウハンドルを取得
    rect = win32gui.GetWindowRect(handle)  # ウィンドウの位置を取得
    im = ImageGrab.grab().crop(rect)
    return im


def concat_img(im1, im2, fname):  # 画像の結合
    color = (0, 0, 0)
    dst = Image.new('RGB', (im1.width + im2.width, max(im1.height, im2.height)), color)
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    dst.save('Output/' + fname + '.jpg')


def get_handle():
    handle = win32gui.GetForegroundWindow()  # 最前面のウィンドウハンドルを取得
    return handle


# カメラ関係サブルーチン##################
def find_cam():
    global cam_list
    cam_list = []
    for camera_number in range(0, 10):
        capture = cv2.VideoCapture(camera_number, cv2.CAP_DSHOW)
        ret, frame = capture.read()

        if ret is True:
            cam_list.append(camera_number)
    print(cam_list)
    cam_no = int(max(cam_list))


def disp_cam(event):
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
    print('\r' + 'focus val ', focus, end='')  # フォーカス値を重ね書き
    capture.set(cv2.CAP_PROP_AUTOFOCUS, 0)  # オートフォーカス OFF
    capture.set(cv2.CAP_PROP_FOCUS, focus)  # focus位置セット
    # https://docs.opencv.org/master/d4/d15/group__videoio__flags__base.html#ggaeb8dd9c89c10a5c63c139bf7c4f5704dad937a854bd8d1ca73edfb3570e799aa3


def cam_get_img(pulseno):
    if Com_No == 'Nucleo未接続':
        tkinter.messagebox.showerror('エラー', 'Nucleoが接続されていません')
    else:
        delay = int(Boxcam_4.get()) / 1000
        rept = int(Boxcam_5.get())
        name = str(Boxcam_6.get())

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


#################################################
####フォトインタラプタ関係サブルーチン#######

def photo_result(response, no):
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
    photo_init_w(0)
    photo_posiset()


def photo_posiset():
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
    pi_window()
    piresult[0].set('未実施')
    piresult[1].set('未実施')
    piresult[2].set('-----')
    photo_init()
    if piresult[0].get() != 'OK':
        piseq_res.insert('end', "PI初期化 失敗\n")  # 最終に追加
        Buttonpi2_1.config(state="normal")  # ボタン有効化


def photo_seq_set(flag, cnt, test_cnt):
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
    global seq_runopt
    seq_runopt = int(2)


def num_judg(readstr):
    return readstr.replace('.', '').isnumeric()


##########################
####Vrs検出関係
def vrstext_clear():
    for x, col in enumerate(vrsres_name):
        vrsres_name[x].delete('1.0', 'end')


def vrstext_save_manu():
    vrstext_save(0, 'a')


def vrstext_save(mode, write):
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
def read_serial():
    # time.sleep(wait_uart)
    # ser.flush()#コマンド送信完了するまで待機

    line = ser.readline().rstrip()  # シリアル読み込み　改行コード除去
    line = line.decode()  # bytes型からstr型に変換
    print(line)


def read_serial2():
    # time.sleep(wait_uart)
    # ser.flush()#コマンド送信完了するまで待機
    time.sleep(wait_uart)
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
    global xposi
    global yposi
    xposi = tk.winfo_rootx() + tk.winfo_width()
    yposi = tk.winfo_rooty() - 30


def read_alert(str_al):
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


# initial設定読み込み----------------------------
dirpath = os.getcwd()  # カレントディレクトリ取得
filepath = dirpath + "/" + "initial_train.xlsx"
print(filepath)
train_reading(filepath)  # 初期パルス設定読み込み
train_conv()  # パルスを記号に変換

win_tate = pulse_disp_num * 25 + 500

tk.title(Software_name)
tk.geometry("500x" + str(win_tate) + "+20+20")  # windowサイズ+x座標+y座標


# ----------------------------------------------

###############
####GUI設定#####
# シーケンス機能window作成
def sequence_window():
    global seqWindow

    # 複数開かないようにする処理
    if 'seqWindow' in globals():  # Windowが定義されているか？
        if seqWindow.winfo_exists() == 1:  # windowが存在するか？
            seqWindow.attributes('-topmost', 1)  # トップに固定表示
            seqWindow.attributes('-topmost', 0)  # 固定解除
            return
    global main_handle
    tk.attributes('-topmost', 1)  # メイン画面をトップに固定表示
    tk.attributes('-topmost', 0)  # メイン画面の固定解除
    main_handle = get_handle()  # main_windowのHandle取得

    get_winposition()  # メインwindow座標取得
    seqWindow = tkinter.Toplevel(tk)
    seqWindow.geometry('+' + str(xposi) + '+' + str(yposi))  # window座標指定

    frameseq = tkinter.Frame(seqWindow, pady=10, padx=10)
    frameseq.pack(anchor=tkinter.W)

    Labelseq_1 = tkinter.Label(frameseq, text='<シーケンス設定>', width=labewid_1, anchor='w')
    Labelseq_1.grid(row=0, column=0, columnspan=4, sticky=tkinter.W)

    # ラベル配置
    labelpi2_name = ['Start', 'Stop', 'step']
    for x, row in enumerate(labelpi2_name, 0):
        labelpi_N = tkinter.Label(frameseq, text=row, width=5, anchor='w')
        labelpi_N.grid(column=x + 1, row=2, columnspan=1, sticky=tkinter.W)

    # ラベル配置
    labelpi3_name = ['電圧範囲[V]', 'Pulse幅比率', '周波数[Hz]', '評価パルス']
    for x, row in enumerate(labelpi3_name, 0):
        labelpi_N = tkinter.Label(frameseq, text=row, width=10, anchor='w')
        if x < 3:
            labelpi_N.grid(column=0, row=4 + x, sticky=tkinter.W)

    for y, row in enumerate(piset_value_name, 0):
        for x, col in enumerate(row):
            col = 'psvname' + str(y) + str(x)

    for y, row in enumerate(piset_value_array, 0):
        for x, col in enumerate(row):
            if y == 3:
                piset_value_name[y][x] = tkinter.Entry(frameseq, width=8)
                piset_value_name[y][x].insert(tkinter.END, col)
                # piset_value_name[y][x].grid(column=x+1,row=y+4,columnspan=2,sticky=tkinter.W)
            else:
                piset_value_name[y][x] = tkinter.Entry(frameseq, width=5)
                piset_value_name[y][x].insert(tkinter.END, col)
                piset_value_name[y][x].grid(column=x + 1, row=y + 4, columnspan=1, sticky=tkinter.W)

    piseq_chk2 = tkinter.Checkbutton(frameseq, variable=seq_jdge_array[2], text='フォトNGで停止', width=12, anchor='w')
    piseq_chk2.grid(row=4, column=4, columnspan=4, sticky=tkinter.NW)
    seq_jdge_array[2].set(True)  # chekbox初期値セット

    piseq_chk3 = tkinter.Checkbutton(frameseq, variable=seq_jdge_array[3], text='設定無効', width=12, anchor='w')
    piseq_chk3.grid(row=6, column=4, columnspan=4, sticky=tkinter.NW)

    piseq_chk4 = tkinter.Checkbutton(frameseq, variable=seq_jdge_array[6], text='設定無効', width=12, anchor='w')
    # piseq_chk4.grid(row=7,column=4,columnspan=4,sticky=tkinter.NW)
    seq_jdge_array[6].set(True)  # chekbox初期値セット

    pisec_section_name = ['A', 'B', 'C', 'D', 'E', 'F']
    for x, col in enumerate(pisec_section_name):
        col = tkinter.Checkbutton(frameseq, variable=piseq_section[x], text=col)
        piseq_section[x].set(True)  # chekbox初期値セット
        ''' 
        if x <3:
            col.grid(row=5,column=4+x,columnspan=1,sticky=tkinter.W)
        else :
        '''
        col.grid(row=5, column=4 + x, columnspan=1, sticky=tkinter.W)

    # 判定方法選択
    Labelseq_2 = tkinter.Label(frameseq, text='判定実施', width=10, anchor='w')
    Labelseq_2.grid(row=8, column=0, columnspan=1, sticky=tkinter.W)
    seq_jdge_name = ['フォト検出', 'Vrs検出']
    for x, col in enumerate(seq_jdge_name):
        col = tkinter.Checkbutton(frameseq, variable=seq_jdge_array[x], text=col)
        seq_jdge_array[x].set(False)  # chekbox初期値セット
        col.grid(row=8, column=2 * x + 1, columnspan=2, sticky=tkinter.W)

    global Buttonpi2_1
    Buttonpi2_1 = tkinter.Button(frameseq, text=u'スタート', width=8)
    Buttonpi2_1.bind("<Button-1>", photo_seqtest_bot)
    Buttonpi2_1.grid(row=10, column=0, columnspan=1, sticky=tkinter.W)

    global Buttonpi2_2
    Buttonpi2_2 = tkinter.Button(frameseq, text=u'ストップ', width=8)
    Buttonpi2_2.config(state="disable")  # ボタン無効化
    Buttonpi2_2.bind("<Button-1>", photo_seqtest_stop_bot)
    Buttonpi2_2.grid(row=10, column=1, columnspan=2, sticky=tkinter.W)

    global Combopi1
    Combopi1 = ttk.Combobox(frameseq, width=18, state='readonly')  # Combobox作成 書込み禁止設定
    Combopi1["values"] = ("表示設定")
    Combopi1.current(0)  # 初期値
    Combopi1.grid(row=10, column=3, columnspan=3, sticky=tkinter.W)

    global Buttonpi2_3
    Buttonpi2_3 = tkinter.Button(frameseq, text=u'適用', width=8)
    Buttonpi2_3.bind("<Button-1>", seq_reading)
    Buttonpi2_3.grid(row=10, column=6, columnspan=2, sticky=tkinter.E)

    # scrolledtextBox
    frameseq2 = tkinter.Frame(seqWindow, pady=5, padx=10)
    frameseq2.pack(anchor=tkinter.W)

    global piseq_res
    piseq_res = tkinter.scrolledtext.ScrolledText(frameseq2, width=25, height=6)
    piseq_res.grid(row=9, column=0, rowspan=2, columnspan=4, sticky=tkinter.W)

    piseq_chk1 = tkinter.Checkbutton(frameseq2, variable=seq_jdge_array[4], text='保存', width=3, anchor='w')
    piseq_chk1.grid(row=9, column=4, columnspan=1, sticky=tkinter.NW)

    piseq_chk2 = tkinter.Checkbutton(frameseq2, variable=seq_jdge_array[5], text='Vrs詳細保存', width=9, anchor='w')
    piseq_chk2.grid(row=10, column=4, columnspan=2, sticky=tkinter.NW)

    global entrypi2_3
    entrypi2_3 = tkinter.Entry(frameseq2, width=14)
    entrypi2_3.insert(tkinter.END, 'file name')
    entrypi2_3.grid(row=9, column=5, columnspan=4, sticky=tkinter.NW)

    frameseqpi = tkinter.LabelFrame(seqWindow, pady=2, padx=10, text='フォト検出パルス設定')
    frameseqpi.pack(anchor=tkinter.W, padx=10, )

    # ラベル配置
    labelpi_name = ['使用Pulse', '1周Step数', '周波数[Hz]', '使用電圧[V]', '検出mode', 'Offset']
    for x, row in enumerate(labelpi_name, 0):
        labelpi_N = tkinter.Label(frameseqpi, text=row, width=8)
        labelpi_N.grid(column=x, row=0)

    # 入力Box配置
    for i, row in enumerate(piset_name, 0):  # i=行番号、row=行内容
        row = 'psname' + str(i)

    for i, row in enumerate(piset_array, 0):
        if i == 0:
            piset_name[i] = ttk.Combobox(frameseqpi, width=6, state='readonly')  # Combobox作成 書込み禁止設定
            piset_name[i]["values"] = ("0:CW-0", "1:CCW-1", "2:", "3:", "4:CW-4", "5:CCW-5")
            piset_name[i].current(piset_array[i])  # 初期値
        elif i == 4:
            piset_name[i] = ttk.Combobox(frameseqpi, width=6, state='readonly')  # Combobox作成 書込み禁止設定
            piset_name[i]["values"] = ("0:通常", "1:最短移動", "2:逆極性chk")  # 秒針検出はnucleo側で自動判定
            piset_name[i].current(piset_array[i])  # 初期値
        elif i == 5:
            piset_name[i] = tkinter.Entry(frameseqpi, width=12)
            piset_name[i].insert(tkinter.END, row)
            piset_name[i].grid(row=1, column=i)
        else:
            piset_name[i] = tkinter.Entry(frameseqpi, width=8)
            piset_name[i].insert(tkinter.END, row)
            piset_name[i].grid(row=1, column=i)
        piset_name[i].grid(row=1, column=i)

        Button7_4 = tkinter.Button(frameseqpi, text=u'PI 針位置単独', width=12, command=pi_window)
        # Button7_4.bind("<Button-1>",pi_window)
        Button7_4.grid(row=2, column=0, columnspan=2, sticky=tkinter.NW)

    frame6 = tkinter.Frame(seqWindow, pady=10, padx=10)
    frame6.pack(anchor=tkinter.W)

    Label6_1 = tkinter.Label(frame6, text='<動作設定>', width=labewid_1, anchor='w')
    Label6_1.grid(row=0, column=0, columnspan=3)

    # ラベル配置
    label6_name = [['Pulse', 'Step数', 'Freq', 'Trig', '逆極', 'Vrs', '補正P', 'Pe', '+50ms', 'Vm']]
    for y, row in enumerate(label6_name, 0):
        for x, col in enumerate(row):
            if x < 3 or x == 9:
                label6_N = tkinter.Label(frame6, text=col, width=6)
            else:
                label6_N = tkinter.Label(frame6, text=col, width=4)
            # if x != 6:#Pulse内 Vrs表示なし
            label6_N.grid(column=x + 1, row=y + 1)

    # 入力Box配置
    for i, row in enumerate(sequence_array, 0):
        for n, col in enumerate(row):
            if n < 3 or n == 9:
                sequence_name[i][n] = tkinter.Entry(frame6, width=6)
            else:
                sequence_name[i][n] = tkinter.Entry(frame6, width=3)
            sequence_name[i][n].insert(tkinter.END, col)
            # if n != 6:#Pulse内 Vrs表示なし
            sequence_name[i][n].grid(row=i + 2, column=n + 1)

    global seq_run  # 実行中に表記変えるため変数定義
    global Button6_1
    seq_run = tkinter.StringVar()
    seq_run.set('単独実行')
    Button6_1 = tkinter.Button(frame6, textvariable=seq_run, width=12)
    Button6_1.bind("<Button-1>", pulse_seq_bot)
    Button6_1.grid(row=i + 3, column=1, columnspan=2)
    global Button6_2
    Button6_2 = tkinter.Button(frame6, text=u'設定読込', width=12)
    Button6_2.bind("<Button-1>", pulse_seqread_bot)
    Button6_2.grid(row=i + 3, column=4, columnspan=4)

    global seq_name
    seq_name = tkinter.StringVar()
    label5_21 = tkinter.Label(frame6, textvariable=seq_name, width=15)
    label5_21.grid(row=i + 3, column=7, columnspan=5)


# パルス列設定window作成-------------------------------------------
def pulsetrain_window(event):
    global trainWindow

    # 複数開かないようにする処理
    if 'trainWindow' in globals():  # Windowが定義されているか？
        if trainWindow.winfo_exists() == 1:  # windowが存在するか？
            trainWindow.attributes('-topmost', 1)  # トップに固定表示
            trainWindow.attributes('-topmost', 0)  # 固定解除
            return

    get_winposition()  # メインwindow座標取得
    trainWindow = tkinter.Toplevel(tk)
    trainWindow.geometry('+' + str(xposi) + '+' + str(yposi))  # window座標指定
    frame8 = tkinter.Frame(trainWindow, pady=10, padx=10)
    frame8.pack(anchor=tkinter.W)

    Label8_1 = tkinter.Label(frame8, text='<パルス列設定>', width=labewid_1, anchor='w')
    Label8_1.grid(row=0, column=0, columnspan=2, sticky=tkinter.W)

    Label8_2 = tkinter.Label(frame8, text='区間', width=6, anchor='e')
    Label8_2.grid(column=1, row=1, columnspan=1, sticky=tkinter.E)

    label8_Pname = [['A', 'B', 'C', 'D', 'E', 'F']]
    for y, row in enumerate(label8_Pname, 0):
        for x, char in enumerate(row):
            label5_P = tkinter.Label(frame8, text=char, width=5)
            label5_P.grid(column=x + 2, row=y + 1)

    label8_Pnum = [['CW 　-0', 'CCW  -1', '補CW -2', '補CCW-3', 'Pulse-4', 'Pulse-5', 'Pr-6']]
    for y, row in enumerate(label8_Pnum, 0):
        for x, char in enumerate(row):
            label8_P = tkinter.Label(frame8, text=char, width=6)
            if x < pulse_disp_num or x == 6:
                label8_P.grid(column=0, row=2 * x + 2)

    for y, row in enumerate(pulse_train_labename, 0):
        pulse_train_labename[y] = tkinter.StringVar()
        char = tkinter.Label(frame8, textvariable=pulse_train_labename[y], width=12, anchor=tkinter.W)
        pulse_train_labename[y].set(pulse_train_name[y])
        if y < pulse_disp_num or y == 6:
            char.grid(column=1, row=2 * y + 2)

    for y, row in enumerate(pulse_train_array_name, 0):
        for x, char in enumerate(row):
            pulse_train_array_name[y][x] = tkinter.StringVar()
            char = tkinter.Label(frame8, textvariable=pulse_train_array_name[y][x], width=5, anchor=tkinter.W)
            pulse_train_array_name[y][x].set(pulse_train_array_str[y][x])
            if y < pulse_disp_num or y == 6:
                if x < 6:
                    char.grid(column=x + 2, row=2 * y + 2)
                elif x >= 6:
                    char.grid(column=x + 2 - 6, row=2 * y + 3)

    global Button8_1
    Button8_1 = tkinter.Button(frame8, text=u'設定読込', width=12)
    Button8_1.bind("<Button-1>", pulse_train_bot)
    Button8_1.grid(row=20, column=0, columnspan=3, sticky=tkinter.W)


# カメラウィンドウ作成---------------------------------
def cam_window(event):
    global cbcam  # カメラNo
    global Boxcam_4  # 撮影Delay
    global Boxcam_5  # 撮影枚数
    global Boxcam_6  # 保存ファイル名

    global camwindow

    # 複数開かないようにする処理
    if 'camwindow' in globals():  # Windowが定義されているか？
        if camwindow.winfo_exists() == 1:  # windowが存在するか？
            camwindow.attributes('-topmost', 1)  # トップに固定表示
            camwindow.attributes('-topmost', 0)  # 固定解除
            return

    get_winposition()  # メインwindow座標取得
    find_cam()

    camwindow = tkinter.Toplevel(tk)
    camwindow.geometry('+' + str(xposi) + '+' + str(yposi))  # window座標指定
    framecam = tkinter.Frame(camwindow, pady=10, padx=10)
    framecam.pack(anchor=tkinter.W)

    # Buttoncam_1= tkinter.Button(framecam, text=u'撮影開始', width=12)
    # Buttoncam_1.bind("<Button-1>",disp_cam)

    Buttoncam_2 = tkinter.Button(framecam, text=u'カメラ接続', width=12)
    Buttoncam_2.bind("<Button-1>", disp_cam)

    Labelcam_1 = tkinter.Label(framecam, text='Camera No', width=10, anchor='e')
    cbcam = ttk.Combobox(framecam, width=2, state='readonly')  # Combobox作成 書込み禁止設定
    cbcam["values"] = cam_list
    cbcam.current(cam_no)  # 初期値

    Labelcam_4 = tkinter.Label(framecam, text='撮影Delay[ms]:', width=12, anchor='e')
    Boxcam_4 = ttk.Combobox(framecam, width=4, state='readonly')  # Combobox作成 書込み禁止設定
    Boxcam_4["values"] = cam_delaylist
    Boxcam_4.current(1)  # 初期値

    Labelcam_5 = tkinter.Label(framecam, text='撮影step数:', width=10, anchor='e')
    Boxcam_5 = tkinter.Entry(framecam, width=3)
    Boxcam_5.insert(tkinter.END, 12)

    Labelcam_6 = tkinter.Label(framecam, text='保存名+No(Auto):', width=16, anchor='e')
    Boxcam_6 = tkinter.Entry(framecam, width=16)
    Boxcam_6.insert(tkinter.END, 'test')

    explain1 = '使い方 [0]key :撮影開始(Pulse出力 Anystep同じ)'
    explain2 = '       [q]key：停止 or Window閉じる　※設定変更はWindow閉じる'
    explain3 = '       [f]or[n]key:Fix Focus 位置変更 far or near　[A]key:Auto Focus機能有効　※対応カメラのみ'
    Expcam_1 = tkinter.Label(framecam, text=explain1, width=96, anchor='w')
    Expcam_2 = tkinter.Label(framecam, text=explain2, width=96, anchor='w')
    Expcam_3 = tkinter.Label(framecam, text=explain3, width=96, anchor='w')

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
    global piWindow

    # 複数開かないようにする処理
    if 'piWindow' in globals():  # piWindowが定義されているか？
        if piWindow.winfo_exists() == 1:  # windowが存在するか？
            piWindow.attributes('-topmost', 1)  # トップに固定表示
            piWindow.attributes('-topmost', 0)  # 固定解除
            return

    get_winposition()  # メインwindow座標取得
    piWindow = tkinter.Toplevel(tk)
    piWindow.geometry('+' + str(xposi) + '+' + str(yposi))  # window座標指定
    framepi = tkinter.Frame(piWindow, pady=10, padx=10)
    framepi.pack(anchor=tkinter.W)

    Labelpi_0 = tkinter.Label(framepi, text='<PI 初期設定>', width=labewid_1, anchor='w')
    Labelpi_0.grid(row=0, column=0, columnspan=3, sticky=tkinter.W)

    global Buttonpi_1
    Buttonpi_1 = tkinter.Button(framepi, text=u'検出初期設定', width=12)
    Buttonpi_1.bind("<Button-1>", photo_init_bot)
    Buttonpi_1.grid(row=4, column=0, columnspan=2, sticky=tkinter.W)

    piresult[0] = tkinter.StringVar()
    char = tkinter.Label(framepi, textvariable=piresult[0], width=8, anchor='w')
    piresult[0].set('未実施')
    char.grid(row=4, column=2, columnspan=1)

    Labelpi_2 = tkinter.Label(framepi, text='<PI 位置検出>', width=labewid_1, anchor='w')
    Labelpi_2.grid(row=5, column=0, columnspan=3, sticky=tkinter.W)

    global Buttonpi_2
    Buttonpi_2 = tkinter.Button(framepi, text=u'ゼロ位置セット', width=12)
    Buttonpi_2.bind("<Button-1>", photo_posiset_bot)
    Buttonpi_2.grid(row=6, column=0, columnspan=2, sticky=tkinter.W)

    piresult[1] = tkinter.StringVar()
    char = tkinter.Label(framepi, textvariable=piresult[1], width=8, anchor='w')
    piresult[1].set('未実施')
    char.grid(row=6, column=2, columnspan=1)

    global Buttonpi_3
    Buttonpi_3 = tkinter.Button(framepi, text=u'ゼロ位置確認', width=12)
    Buttonpi_3.bind("<Button-1>", photo_posicheck_bot)
    Buttonpi_3.grid(row=7, column=0, columnspan=2, sticky=tkinter.W)

    piresult[2] = tkinter.StringVar()
    char = tkinter.Label(framepi, textvariable=piresult[2], width=8, anchor='w')
    piresult[2].set('-----')
    char.grid(row=7, column=2, columnspan=1)

    global pitxt_res
    pitxt_res = tkinter.scrolledtext.ScrolledText(framepi, width=25, height=6)
    pitxt_res.grid(row=4, column=3, rowspan=4, columnspan=1, sticky=tkinter.W)


# Vrsタイミング表示機能window作成
def vrs_window():
    global vrsWindow

    # 複数開かないようにする処理
    if 'vrsWindow' in globals():  # Windowが定義されているか？
        if vrsWindow.winfo_exists() == 1:  # windowが存在するか？
            vrsWindow.attributes('-topmost', 1)  # トップに固定表示
            vrsWindow.attributes('-topmost', 0)  # 固定解除
            return

    get_winposition()  # メインwindow座標取得
    vrsWindow = tkinter.Toplevel(tk)
    vrsWindow.geometry('+' + str(xposi) + '+' + str(yposi))  # window座標指定

    framevrs = tkinter.Frame(vrsWindow, pady=10, padx=10)
    framevrs.grid(row=0, column=0, sticky=tkinter.W, columnspan=2)

    Labelvrs_0 = tkinter.Label(framevrs, text='<Vrs 検出Timing>', anchor='w')
    Labelvrs_0.grid(row=0, column=0, columnspan=3, sticky=tkinter.W)

    # ラベル配置
    labelvr1_name = ['Dt区間1 [us]', 'Dt区間2 [us]', 'Dt区間3 [us]', 'Dt区間4 [us]']
    for x, row in enumerate(labelvr1_name, 0):
        labelpi_N = tkinter.Label(framevrs, text=row, width=10, anchor='w')
        labelpi_N.grid(column=0, row=x + 1, sticky=tkinter.W)

    for x, col in enumerate(vrsdt_name, 0):
        col = 'vrsdtname' + str(x)

    for x, col in enumerate(vrsdt_array, 0):
        vrsdt_name[x] = tkinter.Entry(framevrs, width=6)
        vrsdt_name[x].insert(tkinter.END, col)
        vrsdt_name[x].grid(column=1, row=x + 1, sticky=tkinter.W)

    # 検出パターン
    framevrs1 = tkinter.LabelFrame(vrsWindow, pady=10, padx=10, text='パターン判定')
    framevrs1.grid(row=0, column=2, columnspan=5, sticky=tkinter.W)

    labelvr2_name = [0] * 16
    for x, row in enumerate(labelvr2_name, 0):
        labelpi_N = tkinter.Label(framevrs1, text=format(x, '04b'), width=4,
                                  borderwidth=2, relief="ridge", )
        if x < 4:
            labelpi_N.grid(column=3 + 2 * x, row=1, sticky=tkinter.E)
        elif x < 8:
            labelpi_N.grid(column=3 + 2 * (x - 4), row=2, sticky=tkinter.E)
        elif x < 12:
            labelpi_N.grid(column=3 + 2 * (x - 8), row=3, sticky=tkinter.E)
        else:
            labelpi_N.grid(column=3 + 2 * (x - 12), row=4, sticky=tkinter.E)

    for x, col in enumerate(vrsjdg_name, 0):
        col = 'vrsjdgname' + str(x)

    for x, row in enumerate(vrsjdg_array, 0):
        vrsjdg_name[x] = ttk.Combobox(framevrs1, width=4, state='readonly')  # Combobox作成 書込み禁止設定
        vrsjdg_name[x]["values"] = ("OK", "NG")
        vrsjdg_name[x].current(vrsjdg_array[x])  # 初期値
        if x < 4:
            vrsjdg_name[x].grid(column=4 + 2 * x, row=1, sticky=tkinter.W)
        elif x < 8:
            vrsjdg_name[x].grid(column=4 + 2 * (x - 4), row=2, sticky=tkinter.W)
        elif x < 12:
            vrsjdg_name[x].grid(column=4 + 2 * (x - 8), row=3, sticky=tkinter.W)
        else:
            vrsjdg_name[x].grid(column=4 + 2 * (x - 12), row=4, sticky=tkinter.W)

    # 結果表示テキスト
    framevrs2 = tkinter.Frame(vrsWindow, pady=10, padx=10)
    framevrs2.grid(row=2, column=0, columnspan=10, sticky=tkinter.W)
    global vrsres_name
    vrsres_name = ['Total判定', '判定| Pattern| Timing[us]', 'NG位置| 差分', '判定']
    for x, row in enumerate(vrsres_name, 0):
        if x == 0 or x == 3 or x == 2:
            labelpi_N = tkinter.Label(framevrs2, text=row, width=10, anchor='w')
        elif x == 1:
            labelpi_N = tkinter.Label(framevrs2, text=row, width=35, anchor='w')
        else:
            labelpi_N = tkinter.Label(framevrs2, text=row, width=6, anchor='w')
        if x == 0 or x == 1 or x == 2:
            labelpi_N.grid(row=0, column=3 * x, columnspan=3, sticky=tkinter.W)
    for x, row in enumerate(vrsres_name, 0):
        if x == 0:
            vrsres_name[x] = tkinter.scrolledtext.ScrolledText(framevrs2, width=25, height=15)
        elif x == 1:
            vrsres_name[x] = tkinter.scrolledtext.ScrolledText(framevrs2, width=35, height=15)
        elif x == 3:
            vrsres_name[x] = tkinter.scrolledtext.ScrolledText(framevrs2, width=6, height=15)
        else:
            vrsres_name[x] = tkinter.scrolledtext.ScrolledText(framevrs2, width=10, height=15)
        if x == 0 or x == 1 or x == 2:
            vrsres_name[x].grid(row=1, column=3 * x, columnspan=3, sticky=tkinter.W)

    Buttonvrs_1 = tkinter.Button(framevrs2, text=u'クリア', width=12, command=vrstext_clear)
    Buttonvrs_1.grid(row=6, column=0, columnspan=2, sticky=tkinter.W)

    Buttonvrs_2 = tkinter.Button(framevrs2, text=u'詳細保存', width=10, command=vrstext_save_manu)
    Buttonvrs_2.grid(row=6, column=3, columnspan=1, sticky=tkinter.E)

    global entryvrs_1
    entryvrs_1 = tkinter.Entry(framevrs2, width=14)
    entryvrs_1.insert(tkinter.END, 'file name')
    entryvrs_1.grid(row=6, column=4, columnspan=3, sticky=tkinter.W)

    Buttonvrs_3 = tkinter.Button(framevrs2, text=u'offset送信', width=8, command=vrsng_phoffset)
    Buttonvrs_3.grid(row=6, column=6, columnspan=1, sticky=tkinter.E)

    global entryvrs_2
    entryvrs_2 = tkinter.Entry(framevrs2, width=4)
    entryvrs_2.insert(tkinter.END, '-2')
    entryvrs_2.grid(row=6, column=7, columnspan=1, sticky=tkinter.W)


# COMポート設定---------------------------------------
frame1 = tkinter.Frame(tk, pady=10, padx=10)
frame1.pack(anchor=tkinter.W)  # frame配置左よせ

Label1_1 = tkinter.Label(frame1, text='COMポート : ', width=12, anchor='w')

Box1_1 = tkinter.Entry(frame1, width=40)
Box1_1.insert(tkinter.END, Com_No)

Button1_1 = tkinter.Button(frame1, text=u'OPEN', width=7)
Button1_1.bind("<Button-1>", Select_COM)
Button1_2 = tkinter.Button(frame1, text=u'Close', width=7)
Button1_2.bind("<Button-1>", Close_COM)
# 左クリック（<Button-1>）されると，DeleteEntryValue関数を呼び出すようにバインド

Label1_1.grid(row=0, column=0)
Box1_1.grid(row=0, column=1, sticky=tkinter.W)
Button1_1.grid(row=0, column=2)
Button1_2.grid(row=0, column=3)

# AD2設定-----------------
# ---------------------------
frame2 = tkinter.Frame(tk, pady=10)
frame2.pack()

# Pulse設定--------------------------------------------
frame3 = tkinter.Frame(tk, pady=10, padx=10)
frame3.pack(anchor=tkinter.W)

Label3_1 = tkinter.Label(frame3, text='<Pulse設定>', width=labewid_1, anchor='w')

# コンボボックス
Pulse_cbLabe = tkinter.Label(frame3, text='Pulse選択 : ', width=labewid_1, anchor='w')
Pulse_cb = ttk.Combobox(frame3, width=10, state='readonly')  # Combobox作成 書込み禁止設定
Pulse_cb["values"] = ("0: 2Coil-1", "1: NS", "2: 2Coil-2", "3: NS", "4: 1coil")
Pulse_cb.current(0)  # 初期値

# checkボックス
chklabe1 = tkinter.Label(frame3, text='オプション : ', width=10, anchor='w')
chk3_1 = tkinter.Checkbutton(frame3, variable=pulsemode_0, text='Triger', width=8, anchor='w')
chk3_2 = tkinter.Checkbutton(frame3, variable=pulsemode_1, text='極性反転', width=8, anchor='w')
chk3_4 = tkinter.Checkbutton(frame3, variable=pulsemode_3, text='補正あり', width=8, anchor='w')
chklabe2 = tkinter.Label(frame3, text='Vrs検出 : ', width=10, anchor='w')
chk3_3 = tkinter.Checkbutton(frame3, variable=pulsemode_2, text='Vrs enable', width=8, anchor='w')
# chk3_4 = tkinter.Label(frame3, text='',width=8,anchor='w')
# chk3_4 = tkinter.Checkbutton(frame3, variable=pulsemode_3, text='Vrs Wait',width=8,anchor='w')
chklabe3 = tkinter.Label(frame3, text='Pe設定 : ', width=10, anchor='w')
chk3_5 = tkinter.Checkbutton(frame3, variable=pulsemode_4, text='Enable', width=6, anchor='w')
Label3_4 = tkinter.Label(frame3, text='Pe幅[us]', width=8, anchor='e')
Box3_4 = tkinter.Entry(frame3, width=6)
Box3_4.insert(tkinter.END, 244)
Label3_5 = tkinter.Label(frame3, text='wait[us]', width=8, anchor='e')
Box3_5 = tkinter.Entry(frame3, width=6)
Box3_5.insert(tkinter.END, 3000)

pulsemode_0.set(True)  # chekbox初期値セット
# pulsemode_2.set(True)#chekbox初期値セット

Label3_6 = tkinter.Label(frame3, text='SPK設定 : ', width=10, anchor='w')
Label3_7 = tkinter.Label(frame3, text='周期[us]', width=8, anchor='e')
Box3_7 = tkinter.Entry(frame3, width=6)
Box3_7.insert(tkinter.END, 488)
Label3_8 = tkinter.Label(frame3, text='ON[us]', width=8, anchor='e')
Box3_8 = tkinter.Entry(frame3, width=6)
Box3_8.insert(tkinter.END, 31)

Label3_2 = tkinter.Label(frame3, text='周波数[Hz] : ', width=10, anchor='w')
Box3_2 = tkinter.Entry(frame3, width=8)
Box3_2.insert(tkinter.END, 200)
Label3_3 = tkinter.Label(frame3, text='Anysteps : ', width=10, anchor='w')
Box3_3 = tkinter.Entry(frame3, width=8)
Box3_3.insert(tkinter.END, 60)

Label3_9 = tkinter.Label(frame3, text='Vcomp[V] : ', width=10, anchor='e')
Box3_9 = tkinter.Entry(frame3, width=6, )
Box3_9.insert(tkinter.END, 3.0)
Label3_10 = tkinter.Label(frame3, text='※Jumper注意 max3V', width=14, anchor='e')

Button3_1 = tkinter.Button(frame3, text=u'設定送信', width=10)
Button3_1.bind("<Button-1>", manual_pulse_bot)

Label3_1.grid(row=0, column=0, columnspan=3, sticky=tkinter.W)
# Pulse_cbLabe.grid(row=1,column=0)
# Pulse_cb.grid(row=1,column=1,columnspan=1)
chklabe1.grid(row=2, column=0, sticky=tkinter.W)
chk3_1.grid(row=2, column=1, sticky=tkinter.W)
chk3_2.grid(row=2, column=3, sticky=tkinter.W)
chk3_4.grid(row=2, column=4)
# chk3_6.grid(row=2,column=4,sticky=tkinter.W)

# Pe設定配置
chklabe3.grid(row=4, column=0, sticky=tkinter.W)
chk3_5.grid(row=4, column=1, sticky=tkinter.W)
Label3_4.grid(row=4, column=3, sticky=tkinter.E)
Box3_4.grid(row=4, column=4, sticky=tkinter.W)
Label3_5.grid(row=4, column=5, sticky=tkinter.E)
Box3_5.grid(row=4, column=6, sticky=tkinter.W)

# SPK設定配置
Label3_6.grid(row=5, column=0, sticky=tkinter.W)
chk3_3.grid(row=5, column=1, sticky=tkinter.W)
Label3_7.grid(row=5, column=3, sticky=tkinter.E)
Box3_7.grid(row=5, column=4, sticky=tkinter.W)
Label3_8.grid(row=5, column=5, sticky=tkinter.E)
Box3_8.grid(row=5, column=6, sticky=tkinter.W)
Label3_9.grid(row=6, column=3, sticky=tkinter.E)
Box3_9.grid(row=6, column=4, sticky=tkinter.W)
Label3_10.grid(row=7, column=4, sticky=tkinter.E)

Label3_2.grid(row=6, column=0, sticky=tkinter.W)
Box3_2.grid(row=6, column=1, sticky=tkinter.W)
Label3_3.grid(row=7, column=0, sticky=tkinter.W)
Box3_3.grid(row=7, column=1, columnspan=2, sticky=tkinter.W)

Button3_1.grid(row=8, column=1, columnspan=2)

# Pulses幅/本数--------------------------------------------
frame5 = tkinter.Frame(tk, pady=10, padx=10)
frame5.pack(anchor=tkinter.W)
Label5_1 = tkinter.Label(frame5, text='<Pulse幅[us]/本数>', width=labewid_1, anchor='w')
Label5_1.grid(column=0, row=0, columnspan=3, sticky=tkinter.W)

Label5_2 = tkinter.Label(frame5, text='区間', width=6, anchor='e')
Label5_2.grid(column=0, row=1, columnspan=1, sticky=tkinter.W)

label5_Pnum = [['CW -0', 'CCW-1', '補CW -2', '補CCW-3', 'CW-4', 'CCW-5', 'Pr-6']]
for y, row in enumerate(label5_Pnum, 0):
    for x, char in enumerate(row):
        label5_P = tkinter.Label(frame5, text=char, width=7, anchor='w')
        if x < pulse_disp_num or x == 6:
            label5_P.grid(column=0, row=x + 2, sticky=tkinter.W)

label5_Pname = [['A', 'B', 'C', 'D', 'E', 'F', 'A', 'B', 'C', 'D', 'E', 'F']]
for y, row in enumerate(label5_Pname, 0):
    for x, char in enumerate(row):
        if x < 6:
            label5_P = tkinter.Label(frame5, text=char, width=5)
        else:
            label5_P = tkinter.Label(frame5, text=char, width=3)
        label5_P.grid(column=x + 1, row=y + 1)

for i in range(pulse_type):  # パルス幅設定Entry作成
    for n in range(6):
        pulse_wid_name[i][n] = tkinter.Entry(frame5, width=5)
        pulse_wid_name[i][n].insert(tkinter.END, pulse_width_array[i][n])
        if i < pulse_disp_num or i == 6:
            pulse_wid_name[i][n].grid(row=i + 2, column=n + 1)

for i in range(pulse_type):  # パルス本数設定Entry作成
    for n in range(6):
        pulse_num_name[i][n] = tkinter.Entry(frame5, width=3)
        pulse_num_name[i][n].insert(tkinter.END, pulse_num_array[i][n])
        if i < pulse_disp_num or i == 6:
            pulse_num_name[i][n].grid(row=i + 2, column=n + 7)

Button5_20 = tkinter.Button(frame5, text=u'設定送信', width=12)
Button5_20.bind("<Button-1>", pulse_width_bot)
Button5_20.grid(row=pulse_type + 2, column=1, columnspan=2)

Button5_21 = tkinter.Button(frame5, text=u'設定読込', width=12)
Button5_21.bind("<Button-1>", pulse_reading)
# Button5_21.grid(row=pulse_type+2,column=4,columnspan=2)

global width_name
width_name = tkinter.StringVar()
label5_21 = tkinter.Label(frame5, textvariable=width_name, width=15)
label5_21.grid(row=pulse_type + 2, column=6, columnspan=5)

# Pulses出力--------------------------------------------
frame4 = tkinter.Frame(tk, pady=10, padx=10)
frame4.pack(anchor=tkinter.W)

Label4_1 = tkinter.Label(frame4, text='<Pulse出力>', width=labewid_1, anchor='w')

Label4_2 = tkinter.Label(frame4, text='CW -0', width=8, anchor='w')
Label4_3 = tkinter.Label(frame4, text='CCW-1', width=8, anchor='w')

Button4_1 = tkinter.Button(frame4, text=u'1step', width=7, command=lambda: manual_pulse_out(0, 1))
Button4_2 = tkinter.Button(frame4, text=u'Any step', width=7, command=lambda: manual_pulse_out(0, 0))
Button4_3 = tkinter.Button(frame4, text=u'360step', width=7, command=lambda: manual_pulse_out(0, 360))
Button4_4 = tkinter.Button(frame4, text=u'1step', width=7, command=lambda: manual_pulse_out(1, 1))
Button4_5 = tkinter.Button(frame4, text=u'Any step', width=7, command=lambda: manual_pulse_out(1, 0))
Button4_6 = tkinter.Button(frame4, text=u'360step', width=7, command=lambda: manual_pulse_out(1, 360))
Button4_7 = tkinter.Button(frame4, text=u'Pr', width=7, command=lambda: manual_pulse_out(2, 1))
Button4_8 = tkinter.Button(frame4, text=u'Any 往復', width=7, command=lambda: manual_pulse_out(3, 0))

global Box4_4
Label4_4 = tkinter.Label(frame4, text='Vm設定[V]', width=10, anchor='e')
Box4_4 = tkinter.Entry(frame4, width=4)
Box4_4.insert(tkinter.END, 3.0)

chk4_5 = tkinter.Checkbutton(frame4, variable=stepvm_en, text='step±', width=10, anchor='e')
Box4_5 = tkinter.Entry(frame4, width=4)
Box4_5.insert(tkinter.END, 0.1)

Box4_6 = tkinter.Entry(frame4, width=7)
Box4_6.insert(tkinter.END, 1.4)
Box4_7 = tkinter.Entry(frame4, width=7)
Box4_7.insert(tkinter.END, 3.4)
Box4_8 = tkinter.Entry(frame4, width=7)
Box4_8.insert(tkinter.END, 0.2)

Label4_1.grid(row=0, column=0, columnspan=2, sticky=tkinter.W)
Label4_2.grid(row=1, column=0)
Label4_3.grid(row=2, column=0)

Button4_1.grid(row=1, column=1)
Button4_2.grid(row=1, column=2)
Button4_3.grid(row=1, column=3)
Button4_4.grid(row=2, column=1)
Button4_5.grid(row=2, column=2)
Button4_6.grid(row=2, column=3)
Button4_7.grid(row=1, column=4)
Button4_8.grid(row=2, column=4)

Label4_4.grid(row=1, column=5)
Box4_4.grid(row=1, column=6)
chk4_5.grid(row=2, column=5)
Box4_5.grid(row=2, column=6)

# オプションwindowボタン--------------------------------------------
frame7 = tkinter.Frame(tk, pady=10, padx=10)
frame7.pack(anchor=tkinter.W)

Label7_1 = tkinter.Label(frame7, text='<オプション機能>', width=labewid_1, anchor='w')
Label7_1.grid(row=0, column=0, columnspan=3)

Button7_1 = tkinter.Button(frame7, text=u'シーケンス機能', width=12,
                           command=sequence_window)
# Button7_1.bind("<Button-1>",sequence_window)
Button7_1.grid(row=1, column=3, columnspan=2)

Button7_2 = tkinter.Button(frame7, text=u'パルス列設定', width=12)
Button7_2.bind("<Button-1>", pulsetrain_window)
Button7_2.grid(row=1, column=1, columnspan=2)

Button7_3 = tkinter.Button(frame7, text=u'カメラ機能', width=10)
Button7_3.bind("<Button-1>", cam_window)
Button7_3.grid(row=1, column=5, columnspan=2)

'''
Button7_4 = tkinter.Button(frame7, text=u'PI 針位置', width=12,
                            command = pi_window)
#Button7_4.bind("<Button-1>",pi_window)
Button7_4.grid(row=1,column=7,columnspan=2)
'''

Button7_5 = tkinter.Button(frame7, text=u'Vrs 回転検出', width=12,
                           command=vrs_window)
# Button7_5.bind("<Button-1>",vrs_window)
Button7_5.grid(row=1, column=9, columnspan=2)

###############
####初期設定###
if Com_No != 'Nucleo未接続':
    Button1_1.config(state="disable")  # ボタン無効化

    read_serial()
    nucleo_revchek()
    manual_pulse_set()
    pulse_train_set()  # パルス列設定送信
    pulse_width_set()  # パルス幅設定送信
    vm_set()
    print('init end')

# vrs_windowset()

# print(tk.winfo_geometry())
# print(tk.winfo_rootx())#ディスプレイ上での位置
# print(tk.winfo_y())
# print(tk.winfo_x())
# print(tk.winfo_width())
# print(tk.winfo_exists())#windowが存在するか

tk.mainloop()