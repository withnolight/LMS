import sqlite3
import sys
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *

from init import DB_PATH

root = Tk()

# Windows DPI 适配（仅在 Windows 上生效）
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
        root.tk.call('tk', "scaling", ScaleFactor / 75)
    except Exception:
        pass

def check_login(username, password):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admin WHERE name=? AND password=?",
                       (username, password))
        result = cursor.fetchone()
    return result is not None


def login():
    username = entry_user.get()
    password = entry_password.get()

    if check_login(username, password):
        messagebox.showinfo("登录成功", f"欢迎你，{username}！")
        root.destroy()
        import main
        main.create_main_window(username)
    else:
        messagebox.showerror("登录失败", "用户名或密码错误")


root.title("登录系统")
root.geometry("600x400")
root.configure(bg="#f0f0f0")

# Add a title label
label_title = Label(root, text="欢迎登录图书馆管理系统", font=("Microsoft YaHei", 16, "bold"), background="#f0f0f0")
label_title.pack(pady=10)

# Update label styles
label_user = Label(root, text="用户名:", font=("Microsoft YaHei", 12), background="#f0f0f0")
label_user.pack(pady=5)
entry_user = Entry(root, font=("Microsoft YaHei", 12), width=30)
entry_user.pack()

label_password = Label(root, text="密码:", font=("Microsoft YaHei", 12), background="#f0f0f0")
label_password.pack(pady=5)
entry_password = Entry(root, show="*", font=("Microsoft YaHei", 12), width=30)
entry_password.pack()

# Style the login button
btn_login = Button(root, text="登录", command=login, style="Custom.TButton")
btn_login.pack(pady=20)

# Add a custom style for the button
style = Style()
style.configure("Custom.TButton", font=("Microsoft YaHei", 12), padding=6)

root.mainloop()