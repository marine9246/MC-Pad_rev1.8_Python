import tkinter

root = tkinter.Tk()

def entry_set(name,array,frame):
    for x, col in enumerate(name,0):
        col = tkinter.Entry(frame,width=6)
        col.insert(tkinter.END,array[x])
        col.grid(column=0,row=x,sticky=tkinter.W)    

frame0 = tkinter.Frame(root,pady=10,padx=10)
#frame0.pack(pady=5,padx=5)
frame0.grid(column=0,row=0,pady=5,padx=5)

entryname0 = ['ent1a','ent2a','ent3a']
entryarray0 = ['100','1000','2000']
entry_set(entryname0,entryarray0,frame0)

frame1 = tkinter.LabelFrame(root,pady=10,padx=10,text='menu2')
#frame1.pack(pady=5,padx=5)
frame1.grid(column=1,row=0,pady=5,padx=5)

entryname1 = ['ent1b','ent2b','ent3b']
entryarray1 = ['200','2000','3000']
entry_set(entryname1,entryarray1,frame1)

frame2 = tkinter.LabelFrame(root,pady=10,padx=10,text='menu3',relief='sunken')
#frame2.pack(pady=5,padx=5)
frame2.grid(column=0,row=1,pady=5,padx=5)

entryname2 = ['ent1c','ent2c','ent3c']
entryarray2 = ['300','3000','4000']
entry_set(entryname2,entryarray2,frame2)

frame3 = tkinter.LabelFrame(root,pady=10,padx=10,text='menu4',relief='raised')
#frame2.pack(pady=5,padx=5)
frame3.grid(column=0,row=2,pady=5,padx=5)

entryname3 = ['ent1c','ent2c','ent3c']
entryarray3 = ['300','3000','4000']
entry_set(entryname3,entryarray3,frame3)

root.mainloop()