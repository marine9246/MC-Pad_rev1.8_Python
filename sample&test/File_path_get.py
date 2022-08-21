import tkinter, tkinter.filedialog, tkinter.messagebox
import os
import pandas as pd 

def filepath_get(name):
    # 選択候補を拡張子jpgに絞る（絞らない場合は *.jpg → *）
    filetype = [("", "*"+name)]
    dirpath = os.getcwd() #カレントディレクトリ取得

    # 選択したファイルのパスを取得
    filepath = tkinter.filedialog.askopenfilename(filetypes = filetype, initialdir = dirpath)
    return filepath

def file_read(filepath,sheetno):
    df_raw = pd.read_excel(str(filepath),
                            sheet_name=1, #シートNo. or Name
                            header=0,#ヘッダーにする行
                            index_col=0)#インデックスにする列
    df_raw = df_raw.loc['voltage','start':'step']
    list_raw = df_raw.values.tolist() 
    print(list_raw)
    return df_raw


filepath = filepath_get(".xlsx")#xlsxの拡張子のファイルから選択する
print(filepath)
print(file_read(filepath,1))