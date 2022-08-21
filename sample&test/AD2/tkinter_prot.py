import time

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk

from dwfwrapper import *
from dwfwrapper.trigger import *

# 最初に見つけたデバイスに接続（接続されているのが一つの場合は多用する）
device = DeviceManager().get_first_device()
device.open()

# デバイス接続時に安定化のため待機
time.sleep(2)

def get_analog():
    # #### 任意波形生成器の設定
    device.aout.sine(0, freq=100, amp=1.5)  # 0 = W1
    device.aout.sine(1, freq=500, amp=0.5)  # 1 = W2

    # PCトリガ（後のdevice.trigger()）をトリガとして待機
    device.aout.output(PCTrigger())

    # #### オシロスコープの設定
    sampling_freq = 10000

    # AnalogOutと同期したトリガ。引数の0 = W1
    # 今回はAnalogOutがPCTriggerで起動するので、PCTriggerと指定しても結果は同じ
    trig = AnalogOutTrigger(0)

    # ストリーミングでのオシロスコープ観察
    with device.ain.stream(sampling_freq, n_samples=500, trigger=trig) as s:
        # PCトリガをかける = AnalogOutが起動
        device.trigger()

        # データの受信開始
        # データを落とす可能性があるので前行との間にはできるだけ処理をいれないこと
        wave = s.get_data()    

    return wave.ch1,wave.ch2

def culc_data(array):
    for x,col in enumerate(meas_name):
        col.delete(0,tk.END)

    meas_name[0].insert(tk.END,format(max(array),'.3f'))
    meas_name[1].insert(tk.END,format(min(array),'.3f'))
    meas_name[2].insert(tk.END,format(sum(array)/len((array)),'.3f'))

def plotdata():
    fig.clear()#前の描画データの消去
    wave1,wave2 = get_analog()
    culc_data(wave1)

    # ax1
    ax1 = fig.add_subplot(111)#1x1の1番目
    #ax1.plot(x1, y1)
    ax1.plot(wave1)
    #ax1.plot(wave2)
    ax1.set_title('Analog')
    ax1.set_ylabel('Voltage[V]')

    canvas.draw()


# When windows is closed.
def _destroyWindow():
    device.close()
    root.quit()
    root.destroy()


# Tkinter Class

root = tk.Tk()
root.title('analog discovery test')
root.withdraw()
root.protocol('WM_DELETE_WINDOW', _destroyWindow)  # When you close the tkinter window.

frame1 = tk.Frame(root,pady=10,padx=10)
frame1.grid(row=0,column=0,sticky=tk.W)

font_size = 20

global meas_name
meas_labe=['Max[V]','Min[V]','Avg[V]']
meas_name=[0]*len(meas_labe)

for x,col in enumerate(meas_labe):
    col = tk.Label(frame1, text=col+':',width=6,anchor='w', font=("",font_size))
    col.grid(row=x,column=0,columnspan=1,sticky=tk.W)
    
    meas_name[x] = 'meas'+str(x)
    meas_name[x] = tk.Entry(frame1,width=6, font=("",font_size))
    meas_name[x].insert(tk.END,'---')
    meas_name[x].grid(row=x,column=1,columnspan=1,sticky=tk.W)

Button1 = tk.Button(frame1, text=u'測定開始', width=12,command = plotdata, font=("",font_size))
Button1.grid()

explain = 'w1：1.5V 100Hz　正弦波、ch1：波形取得表示 Max/Min/Avg計算'
Label1= tk.Label(frame1, text=explain , anchor='w', font=("",10))
Label1.grid(row=len(meas_labe)+1,column=0,columnspan=2,sticky=tk.W)

frame2 = tk.Frame(root,pady=10,padx=10)
frame2.grid(row=len(meas_labe),column=0,columnspan=1)

# Figure instance
fig = plt.Figure()
fig.gca().set_aspect('equal', adjustable='box')#グラフ領域の調整

# Canvas
canvas = FigureCanvasTkAgg(fig, master=frame2)  # Generate canvas instance, Embedding fig in root
#canvas.draw()
canvas.get_tk_widget().pack()
#canvas._tkcanvas.pack()


# root
root.update()
root.deiconify()
root.mainloop()