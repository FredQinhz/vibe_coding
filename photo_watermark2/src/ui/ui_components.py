import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
from src.utils.image_utils import ImageUtils

class ImageThumbnail(tk.Frame):
    """
    图像缩略图组件，显示图片缩略图和文件名
    """
    def __init__(self, parent, image_path, on_select=None, on_remove=None, thumbnail_size=(120, 120)):
        super().__init__(parent, relief=tk.RAISED, bd=1)
        self.image_path = image_path
        self.on_select = on_select
        self.on_remove = on_remove
        self.thumbnail_size = thumbnail_size
        self.selected = False
        
        self._create_widgets()
        self._load_thumbnail()
        
        # 添加事件绑定
        self.bind('<Button-1>', self._on_click)
        for child in self.winfo_children():
            child.bind('<Button-1>', lambda e: self._on_click(e))
    
    def _create_widgets(self):
        # 缩略图容器
        self.thumbnail_frame = tk.Frame(self, width=self.thumbnail_size[0], height=self.thumbnail_size[1], bg='white')
        self.thumbnail_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.thumbnail_label = tk.Label(self.thumbnail_frame, bg='white')
        self.thumbnail_label.pack(fill=tk.BOTH, expand=True)
        
        # 文件名标签
        file_name = os.path.basename(self.image_path)
        self.filename_label = tk.Label(self, text=file_name, wraplength=self.thumbnail_size[0], justify=tk.CENTER)
        self.filename_label.pack(fill=tk.X, padx=5, pady=2)
        
        # 移除按钮
        if self.on_remove:
            self.remove_btn = tk.Button(self, text="移除", command=self._on_remove, width=8)
            self.remove_btn.pack(pady=2)
    
    def _load_thumbnail(self):
        try:
            image = Image.open(self.image_path)
            thumbnail = ImageUtils.create_thumbnail(image.copy(), self.thumbnail_size)
            self.photo = ImageTk.PhotoImage(thumbnail)
            self.thumbnail_label.config(image=self.photo)
            self.thumbnail_label.image = self.photo  # 保持引用避免被垃圾回收
        except Exception as e:
            print(f"加载缩略图失败: {e}")
            # 显示错误图标
            error_text = "无法\n加载"
            self.thumbnail_label.config(text=error_text, font=('Arial', 12))
    
    def _on_click(self, event):
        if self.on_select:
            self.on_select(self)
    
    def _on_remove(self):
        if self.on_remove:
            self.on_remove(self)
    
    def select(self):
        """选中此缩略图"""
        self.selected = True
        self.config(relief=tk.SUNKEN, bd=2, bg='#e0e0ff')
    
    def deselect(self):
        """取消选中此缩略图"""
        self.selected = False
        self.config(relief=tk.RAISED, bd=1, bg=self.master.cget('bg'))

class FileDropArea(tk.Frame):
    """
    文件拖放区域组件
    """
    def __init__(self, parent, on_files_drop=None):
        super().__init__(parent, relief=tk.RIDGE, bd=2, bg='#f0f0f0')
        self.on_files_drop = on_files_drop
        
        self._create_widgets()
        self._setup_drag_and_drop()
    
    def _create_widgets(self):
        self.label = tk.Label(self, text="拖放图片或文件夹到此处\n或点击下方按钮选择文件", 
                             bg='#f0f0f0', font=('Arial', 10))
        self.label.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    def _setup_drag_and_drop(self):
        # 绑定拖放事件
        self.bind('<Enter>', self._on_drag_enter)
        self.bind('<Leave>', self._on_drag_leave)
        self.bind('<Button-1>', self._on_click)
        self.bind('<<Drop>>', self._on_drop)
        
        # 启用拖放功能
        self.bind('<<DragOver>>', self._on_drag_over)
    
    def _on_drag_enter(self, event):
        self.config(bg='#e0e0e0')
    
    def _on_drag_leave(self, event):
        # 检查鼠标是否真的离开了组件
        x, y = event.x_root, event.y_root
        widget = self.winfo_containing(x, y)
        if widget != self and not self._is_child_widget(widget):
            self.config(bg='#f0f0f0')
    
    def _is_child_widget(self, widget):
        """检查一个组件是否是此组件的子组件"""
        while widget:
            if widget == self:
                return True
            widget = widget.master
        return False
    
    def _on_drag_over(self, event):
        # 允许拖放
        event.widget.focus_force()
        return "copy"
    
    def _on_drop(self, event):
        # 获取拖放的文件路径
        files = self.tk.splitlist(event.data)
        if files and self.on_files_drop:
            self.on_files_drop(files)
        self.config(bg='#f0f0f0')
    
    def _on_click(self, event):
        # 点击时也可以触发文件选择
        if self.on_files_drop:
            # 这里可以调用文件选择对话框
            pass
