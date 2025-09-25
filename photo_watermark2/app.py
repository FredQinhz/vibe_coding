import tkinter as tk
from src.ui.main_window import MainWindow
import sys
import os

# 设置中文字体支持
def set_font_for_windows():
    # 确保中文显示正常
    if sys.platform == 'win32':
        # 获取tkinter版本
        tk_version = tk.TkVersion
        if tk_version >= 8.6:
            # 对于较新版本的tkinter，设置字体配置
            from tkinter import font
            # 创建字体族
            default_font = font.nametofont("TkDefaultFont")
            default_font.configure(family="SimHei")
            text_font = font.nametofont("TkTextFont")
            text_font.configure(family="SimHei")
            fixed_font = font.nametofont("TkFixedFont")
            fixed_font.configure(family="SimHei")

# 添加src目录到Python路径
def add_src_to_path():
    # 获取当前文件所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 构建src目录路径
    src_dir = os.path.join(current_dir, "src")
    # 添加到Python路径
    if src_dir not in sys.path:
        sys.path.append(src_dir)

# 主函数
def main():
    # 添加src目录到路径
    add_src_to_path()
    
    # 创建主窗口
    root = tk.Tk()
    
    # 设置中文字体
    set_font_for_windows()
    
    # 创建应用主窗口
    app = MainWindow(root)
    
    # 启动事件循环
    root.mainloop()

if __name__ == "__main__":
    main()