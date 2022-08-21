import serial
from serial.tools import list_ports
import tkinter
import time

tk = tkinter.Tk()
global ser
global Com_No

Software_name = 'NUCLEO接続 Sample program'
wait_uart=0.01 #UART送信後の待ち時間 通信エラーおこる場合は大きくする

#シリアルポート制御サブルーチン-----------------------------
def Select_COM(event):
    Com_No = Box1_1.get()#get()でエントリーボックス値取得
    print(Com_No+' open') 
    Com_No = str(Com_No) 
    ser.open()#シリアルポートOPEN
    time.sleep(wait_uart)
    Button1_2.config(state="normal") #ボタン無効化
    Button1_1.config(state="disable") #ボタン無効化

def Close_COM(event):
    ser.send_break()    #Brake信号送信 Nucleo reset
    time.sleep(2)
    Com_No = Box1_1.get()
    print(Com_No+' close') 
    ser.close()#シリアルポートCLOSE
    Button1_1.config(state="normal") #ボタン無効化
    Button1_2.config(state="disable") #ボタン無効化


#NUCLEO COMポート検索-----------------------------------------------
ports=list_ports.comports()
device=[info for info in ports if "STLink" in info.description] #.descriptionでデバイスの名前を取得出来る

device_list=[]
for i , name in enumerate(device,0):#複数デバイスの名前表示
    device_list.append(str(name))
print(device_list)
if not len(device) == 0:
    ser=serial.Serial(device[0].device)
    Com_No = str(device[0])
    print(Com_No+' open') 
    ser.baudrate = 115200

else:
    Com_No = 'Nucleo未接続'
    print('Nucleoが接続されていません')
    #time.sleep(3)

#--------------------------------------------------------
#メインウィンドウ
tk.title(Software_name)
tk.geometry("500x200+20+20")#windowサイズ+x座標+y座標

#COMポート設定---------------------------------------
frame1 = tkinter.Frame(tk,pady=10,padx=10) 
frame1.pack(anchor=tkinter.W) #frame配置左よせ

Label1_1 = tkinter.Label(frame1, text='COMポート : ',width=12,anchor='w')

Box1_1 = tkinter.Entry(frame1,width=40)
Box1_1.insert(tkinter.END,Com_No)

Button1_1 = tkinter.Button(frame1, text=u'OPEN', width=7)
Button1_1.bind("<Button-1>",Select_COM)
Button1_2 = tkinter.Button(frame1, text=u'Close', width=7)
Button1_2.bind("<Button-1>",Close_COM)
#左クリック（<Button-1>）されると，DeleteEntryValue関数を呼び出すようにバインド

Label1_1.grid(row=0, column=0)
Box1_1.grid(row=0, column=1)
Button1_1.grid(row=0,column=2)
Button1_2.grid(row=0,column=3)

tk.mainloop()