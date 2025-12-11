import ctypes
import sqlite3
import tkinter as tk
from tkinter import ttk
import datetime


def open_operation_window(number):
    """打开一个新的操作窗口"""
    win = tk.Toplevel()
    win.title(f"操作窗口 {number}")
    win.geometry("300x150")

    ttk.Label(win, text=f"这里是操作窗口 {number}", font=("Arial", 14)).pack(pady=30)
    ttk.Button(win, text="关闭", command=win.destroy).pack()


def update_clock(label):
    """实时更新时钟"""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    label.config(text=f"当前时间：{now}")
    label.after(1000, update_clock, label)


def create_main_window(username):
    root = tk.Tk()
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
    root.tk.call('tk',"scaling", ScaleFactor/75)
    root.title("主界面")
    root.geometry("400x600")

    # 登录用户显示
    user_label = ttk.Label(root, text=f"当前登录用户：{username}", font=("Arial", 14))
    user_label.pack(pady=10)

    # 时钟
    clock_label = ttk.Label(root, text="", font=("Arial", 12))
    clock_label.pack(pady=10)
    update_clock(clock_label)

    # 操作按钮
    button_frame = ttk.Frame(root)
    button_frame.pack(pady=40)

    ttk.Button(button_frame, text="查询书籍状态", width=20,
               command=lambda: open_operation_window(1)).pack(pady=5)
    ttk.Button(button_frame, text="查询借阅记录", width=20,
               command=lambda: open_operation_window(2)).pack(pady=5)
    ttk.Button(button_frame, text="借书", width=20,
               command=lambda: open_operation_window(3)).pack(pady=5)
    ttk.Button(button_frame, text="还书", width=20,
               command=lambda: open_operation_window(4)).pack(pady=5)
    ttk.Button(button_frame, text="新增书籍", width=20,
               command=lambda: open_operation_window(5)).pack(pady=5)
    ttk.Button(button_frame, text="读者管理", width=20,
               command=lambda: open_operation_window(6)).pack(pady=5)
    ttk.Button(button_frame, text="退出登录", width=20,
               command=lambda: open_operation_window(7)).pack(pady=5)
    root.mainloop()


# 示例：假设登录用户名是 admin
create_main_window("admin")