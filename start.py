import sqlite3
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *
import ctypes

root = Tk()
ctypes.windll.shcore.SetProcessDpiAwareness(1)
ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
root.tk.call('tk',"scaling", ScaleFactor/75)

def check_login(username, password):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM admin WHERE name=? AND password=?", 
                   (username, password))
    result = cursor.fetchone()

    conn.close()
    return result is not None


def login():
    username = entry_user.get()
    password = entry_password.get()

    if check_login(username, password):
        messagebox.showinfo("登录成功", f"欢迎你，{username}！")
        root.destroy()
        import main
    else:
        messagebox.showerror("登录失败", "用户名或密码错误")


root.title("登录系统")
root.geometry("300x180")

label_user = Label(root, text="用户名:")
label_user.pack(pady=5)
entry_user = Entry(root)
entry_user.pack()

label_password = Label(root, text="密码:")
label_password.pack(pady=5)
entry_password = Entry(root, show="*")
entry_password.pack()

btn_login = Button(root, text="登录", command=login)
btn_login.pack(pady=15)

root.mainloop()