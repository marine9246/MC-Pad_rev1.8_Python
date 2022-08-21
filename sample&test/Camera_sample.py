import cv2
import tkinter, tkinter.ttk as ttk
import datetime
import os
import time

windowsize = (800, 600)

tk=tkinter.Tk()
tk.title("camera")
tk.geometry("200x300")

cam_list = []
cam_no = 0

def find_cam():
    for camera_number in range(0, 5):
        cap = cv2.VideoCapture(camera_number, cv2.CAP_DSHOW)
        ret, frame = cap.read()

        if ret is True:
            cam_list.append(camera_number)
    cam_no = max(cam_list)
    print(cam_no)
    cap.release()
    cv2.destroyAllWindows()

def disp_cam(event):
    global capture
    cam_no = int(cbcam.get()[0])
    capture = cv2.VideoCapture(cam_no, cv2.CAP_DSHOW)
    while(True):
        ret, frame = capture.read()
        # resize the window
        frame = cv2.resize(frame, windowsize)        

        cv2.imshow('title',frame)
        key = cv2.waitKey(1) #キー入力1msec待ち
        if key == ord('q'):
            break
        elif key == ord('0'):
            cam_get_img()

    capture.release()
    cv2.destroyAllWindows()

def cam_get_img():
    #global capture
    #cam_no = int(cbcam.get()[0])
    #capture = cv2.VideoCapture(cam_no, cv2.CAP_DSHOW)
    rept = 10
    delay = 100
    now = datetime.datetime.now()
    dirpath = os.getcwd() #os.path.dirname(__file__)
    folder = '/image/'+ now.strftime('%y%m%d_%H%M%S')
    os.makedirs(dirpath+ folder)
    print('保存先 '+dirpath+ folder)

    n=0
    ret, frame = capture.read()
    cv2.imwrite(dirpath + folder+'/'+str(n).zfill(3)+'.jpg',frame)

    time_st = time.time()
    delay_result=[]
    capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)#バッファサイズを1に設定。遅延を緩和する？
    #capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
    while n < rept:
        time_rep = time.time()
        while(True):
            ret, frame = capture.read()
            key = cv2.waitKey(1) #キー入力1msec待ち
            if key == ord('q'):
                n=rept
                break
            if time.time()-time_rep > delay:
                #ret, frame = capture.read()
                delay_result.append(time.time()-time_rep)
                break
        cv2.imwrite(dirpath + folder+'/'+str(n+1).zfill(3)+'.jpg',frame)
        #frame = cv2.resize(frame, windowsize)#画面表示更新用
        #cv2.imshow('cam',frame)
        n += 1
    time_total = time.time()-time_st
    print('delay時間 Max:'+str(format(max(delay_result),'.3f')) + 's/ Min:'+str(format(min(delay_result),'.3f'))+'s')
    print('測定時間 Total' + str(format(time_total,'.2f'))+'s')
    
    capture.release()
    cv2.destroyAllWindows()


def cam_window():
    global cbcam #カメラNo
    global Boxcam_3 #step数
    global Boxcam_4 #step毎のwait時間
    global Boxcam_5 #撮影枚数

    camwindow = tkinter.Toplevel(tk)
    framecam = tkinter.Frame(camwindow,pady=10,padx=10)
    framecam.pack(anchor=tkinter.W)

    Buttoncam_1= tkinter.Button(framecam, text=u'撮影開始', width=12)
    Buttoncam_1.bind("<Button-1>",cam_get_img)

    Buttoncam_2= tkinter.Button(framecam, text=u'位置確認', width=12)
    Buttoncam_2.bind("<Button-1>",disp_cam)

    Labelcam_1 = tkinter.Label(framecam, text='Camera No',width=8, anchor='w')
    cbcam = ttk.Combobox(framecam ,width=2, state='readonly') # Combobox作成 書込み禁止設定
    cbcam["values"] = cam_list
    cbcam.current(cam_no)#初期値

    Labelcam_2= tkinter.Label(framecam, text='動作設定 ',width=10, anchor='e')
    Labelcam_3= tkinter.Label(framecam, text='Step数:',width=6, anchor='e')
    Boxcam_3 = tkinter.Entry(framecam,width=3)
    Boxcam_3.insert(tkinter.END,1)
    Labelcam_4= tkinter.Label(framecam, text='Wait[ms]:',width=8, anchor='e')
    Boxcam_4 = tkinter.Entry(framecam,width=3)
    Boxcam_4.insert(tkinter.END,50)
    Labelcam_5= tkinter.Label(framecam, text='撮影数:',width=6, anchor='e')
    Boxcam_5 = tkinter.Entry(framecam,width=3)
    Boxcam_5.insert(tkinter.END,1)

    Buttoncam_1.grid(row=0,column=0,columnspan=1)
    Buttoncam_2.grid(row=0,column=1,columnspan=1)
    Labelcam_1.grid(row=0,column=2,columnspan=1)
    cbcam.grid(row=0,column=3,columnspan=1)
    Labelcam_2.grid(row=0,column=4,columnspan=1)
    Labelcam_3.grid(row=0,column=5,columnspan=1)
    Boxcam_3.grid(row=0,column=6,columnspan=1)
    Labelcam_4.grid(row=0,column=7,columnspan=1)
    Boxcam_4.grid(row=0,column=8,columnspan=1)
    Labelcam_5.grid(row=0,column=9,columnspan=1)
    Boxcam_5.grid(row=0,column=10,columnspan=1)


find_cam()
cam_window()

tk.mainloop()