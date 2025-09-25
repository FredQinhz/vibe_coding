import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
from src.core.image_processor import ImageProcessor
from src.core.file_handler import FileHandler
from src.ui.ui_components import ImageThumbnail, FileDropArea

class MainWindow:
    """
    应用主窗口类
    """
    def __init__(self, root):
        self.root = root
        self.root.title("照片水印工具")
        self.root.geometry("900x600")
        self.root.minsize(800, 500)
        
        # 存储导入的图片路径
        self.imported_images = []
        
        # 当前选中的缩略图
        self.selected_thumbnail = None
        
        # 输出设置
        self.output_folder = ""
        self.output_prefix = ""
        self.output_suffix = "_watermarked"
        self.output_format = "png"
        self.image_quality = 95
        self.resize_percentage = 100
        
        # 创建UI
        self._create_ui()
        
        # 绑定事件
        self._bind_events()
    
    def _create_ui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建左侧面板（图片列表）
        left_panel = ttk.LabelFrame(main_frame, text="导入的图片")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10), pady=5)
        
        # 创建拖放区域
        self.drop_area = FileDropArea(left_panel, on_files_drop=self._on_files_drop)
        self.drop_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建按钮区域
        button_frame = ttk.Frame(left_panel)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.import_btn = ttk.Button(button_frame, text="导入图片", command=self._import_images)
        self.import_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.import_folder_btn = ttk.Button(button_frame, text="导入文件夹", command=self._import_folder)
        self.import_folder_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.clear_btn = ttk.Button(button_frame, text="清空列表", command=self._clear_images)
        self.clear_btn.pack(side=tk.RIGHT)
        
        # 创建图片网格视图
        self.scrollable_frame = ttk.Frame(left_panel)
        self.scrollable_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.canvas = tk.Canvas(self.scrollable_frame)
        self.scrollbar = ttk.Scrollbar(self.scrollable_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_content = ttk.Frame(self.canvas)
        
        self.scrollable_content.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_content, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # 绑定鼠标滚轮事件
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # 创建右侧面板（输出设置）
        right_panel = ttk.LabelFrame(main_frame, text="输出设置")
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0), pady=5, ipady=5)
        
        # 输出文件夹选择
        folder_frame = ttk.Frame(right_panel)
        folder_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        ttk.Label(folder_frame, text="输出文件夹:").pack(side=tk.TOP, anchor=tk.W, pady=(0, 5))
        
        folder_input_frame = ttk.Frame(folder_frame)
        folder_input_frame.pack(fill=tk.X)
        
        self.output_folder_var = tk.StringVar()
        ttk.Entry(folder_input_frame, textvariable=self.output_folder_var, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(folder_input_frame, text="浏览...", command=self._select_output_folder).pack(side=tk.RIGHT)
        
        # 输出格式选择
        format_frame = ttk.Frame(right_panel)
        format_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(format_frame, text="输出格式:").pack(side=tk.TOP, anchor=tk.W, pady=(0, 5))
        
        self.output_format_var = tk.StringVar(value="png")
        format_options = ttk.Frame(format_frame)
        format_options.pack(fill=tk.X)
        
        ttk.Radiobutton(format_options, text="JPEG", variable=self.output_format_var, value="jpg").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(format_options, text="PNG", variable=self.output_format_var, value="png").pack(side=tk.LEFT)
        
        # 文件名设置
        filename_frame = ttk.Frame(right_panel)
        filename_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(filename_frame, text="文件名前缀:").pack(side=tk.TOP, anchor=tk.W, pady=(0, 5))
        self.prefix_var = tk.StringVar(value="")
        ttk.Entry(filename_frame, textvariable=self.prefix_var).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(filename_frame, text="文件名后缀:").pack(side=tk.TOP, anchor=tk.W, pady=(0, 5))
        self.suffix_var = tk.StringVar(value="_watermarked")
        ttk.Entry(filename_frame, textvariable=self.suffix_var).pack(fill=tk.X)
        
        # JPEG质量设置
        quality_frame = ttk.LabelFrame(right_panel, text="JPEG质量")
        quality_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.quality_var = tk.IntVar(value=95)
        ttk.Scale(quality_frame, from_=1, to=100, orient="horizontal", variable=self.quality_var).pack(fill=tk.X, padx=10, pady=10)
        self.quality_label = ttk.Label(quality_frame, text=f"质量: {self.quality_var.get()}%")
        self.quality_label.pack()
        
        # 缩放设置
        resize_frame = ttk.LabelFrame(right_panel, text="图片缩放")
        resize_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.resize_var = tk.IntVar(value=100)
        ttk.Scale(resize_frame, from_=10, to=200, orient="horizontal", variable=self.resize_var).pack(fill=tk.X, padx=10, pady=10)
        self.resize_label = ttk.Label(resize_frame, text=f"缩放: {self.resize_var.get()}%")
        self.resize_label.pack()
        
        # 导出按钮
        self.export_btn = ttk.Button(right_panel, text="导出图片", command=self._export_images, style="Accent.TButton")
        self.export_btn.pack(fill=tk.X, padx=10, pady=(20, 10))
        
        # 创建自定义样式
        style = ttk.Style()
        style.configure("Accent.TButton", font=('Arial', 10, 'bold'))
    
    def _bind_events(self):
        # 绑定滑块事件
        self.quality_var.trace_add("write", self._update_quality_label)
        self.resize_var.trace_add("write", self._update_resize_label)
        
        # 绑定窗口调整事件
        self.root.bind("<Configure>", self._on_window_resize)
    
    def _on_window_resize(self, event):
        # 当窗口大小改变时，更新画布大小
        self.canvas.itemconfig(self.canvas_frame, width=self.canvas.winfo_width())
    
    def _on_mousewheel(self, event):
        # 处理鼠标滚轮滚动
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def _update_quality_label(self, *args):
        # 更新质量标签
        self.quality_label.config(text=f"质量: {self.quality_var.get()}%")
    
    def _update_resize_label(self, *args):
        # 更新缩放标签
        self.resize_label.config(text=f"缩放: {self.resize_var.get()}%")
    
    def _import_images(self):
        # 导入单个或多个图片
        file_types = [("图像文件", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif *.JPG *.JPEG *.PNG *.BMP *.TIFF *.TIF")]
        file_paths = filedialog.askopenfilenames(title="选择图片文件", filetypes=file_types)
        
        if file_paths:
            self._add_images(file_paths)
    
    def _import_folder(self):
        # 导入整个文件夹
        folder_path = filedialog.askdirectory(title="选择图片文件夹")
        
        if folder_path:
            # 获取文件夹中所有支持的图像文件
            image_files = FileHandler.get_supported_files(folder_path)
            if image_files:
                self._add_images(image_files)
            else:
                messagebox.showinfo("提示", "所选文件夹中没有支持的图像文件")
    
    def _on_files_drop(self, files):
        # 处理拖放的文件
        image_files = []
        
        for file_path in files:
            # 处理文件路径中的转义字符
            file_path = file_path.strip('"')
            
            if os.path.isdir(file_path):
                # 如果是文件夹，获取其中的所有图像文件
                image_files.extend(FileHandler.get_supported_files(file_path))
            elif FileHandler.is_supported_image(file_path):
                # 如果是支持的图像文件，直接添加
                image_files.append(file_path)
        
        if image_files:
            self._add_images(image_files)
    
    def _add_images(self, file_paths):
        # 添加图片到列表
        new_images = []
        for file_path in file_paths:
            if file_path not in self.imported_images:
                self.imported_images.append(file_path)
                new_images.append(file_path)
        
        if new_images:
            self._display_images(new_images)
            # 自动选择输出文件夹（如果还未设置）
            if not self.output_folder and len(new_images) > 0:
                first_image_folder = os.path.dirname(new_images[0])
                # 尝试创建输出文件夹
                output_folder = os.path.join(first_image_folder, "output")
                self.output_folder = output_folder
                self.output_folder_var.set(output_folder)
    
    def _display_images(self, file_paths):
        # 显示图片缩略图
        for file_path in file_paths:
            # 创建缩略图组件
            thumbnail = ImageThumbnail(
                self.scrollable_content, 
                file_path, 
                on_select=self._on_thumbnail_select, 
                on_remove=self._on_thumbnail_remove
            )
            
            # 计算网格布局
            cols = max(1, self.scrollable_content.winfo_width() // 140)  # 每个缩略图大约140宽度
            idx = len(self.scrollable_content.winfo_children()) - 1
            row = idx // cols
            col = idx % cols
            
            thumbnail.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        
        # 更新画布滚动区域
        self.scrollable_content.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _on_thumbnail_select(self, thumbnail):
        # 选中缩略图
        if self.selected_thumbnail:
            self.selected_thumbnail.deselect()
        self.selected_thumbnail = thumbnail
        thumbnail.select()
    
    def _on_thumbnail_remove(self, thumbnail):
        # 移除缩略图
        file_path = thumbnail.image_path
        if file_path in self.imported_images:
            self.imported_images.remove(file_path)
        
        # 销毁组件
        thumbnail.destroy()
        
        # 如果删除的是选中的缩略图，重置选中状态
        if self.selected_thumbnail == thumbnail:
            self.selected_thumbnail = None
        
        # 重新布局剩余的缩略图
        self._rearrange_thumbnails()
    
    def _rearrange_thumbnails(self):
        # 重新排列缩略图
        children = self.scrollable_content.winfo_children()
        cols = max(1, self.scrollable_content.winfo_width() // 140)
        
        for i, child in enumerate(children):
            row = i // cols
            col = i % cols
            child.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
    
    def _clear_images(self):
        # 清空图片列表
        if messagebox.askyesno("确认", "确定要清空所有图片吗？"):
            # 移除所有缩略图组件
            for child in self.scrollable_content.winfo_children():
                child.destroy()
            
            # 清空图片列表
            self.imported_images.clear()
            self.selected_thumbnail = None
    
    def _select_output_folder(self):
        # 选择输出文件夹
        folder_path = filedialog.askdirectory(title="选择输出文件夹")
        
        if folder_path:
            # 检查是否与原文件夹相同
            if self.imported_images:
                # 获取第一个图片的文件夹
                first_image_folder = os.path.dirname(self.imported_images[0])
                if not FileHandler.validate_output_folder(first_image_folder, folder_path):
                    if not messagebox.askyesno("警告", "输出文件夹与输入文件夹相同，可能会覆盖原图。是否继续？"):
                        return
            
            self.output_folder = folder_path
            self.output_folder_var.set(folder_path)
    
    def _export_images(self):
        # 导出图片
        if not self.imported_images:
            messagebox.showinfo("提示", "没有要导出的图片")
            return
        
        # 检查输出文件夹
        if not self.output_folder:
            messagebox.showinfo("提示", "请先选择输出文件夹")
            return
        
        # 确保输出文件夹存在
        if not os.path.exists(self.output_folder):
            try:
                os.makedirs(self.output_folder)
            except Exception as e:
                messagebox.showerror("错误", f"创建输出文件夹失败: {str(e)}")
                return
        
        # 获取输出设置
        prefix = self.prefix_var.get()
        suffix = self.suffix_var.get()
        output_format = self.output_format_var.get()
        quality = self.quality_var.get()
        resize_percentage = self.resize_var.get()
        
        # 创建进度窗口
        progress_window = tk.Toplevel(self.root)
        progress_window.title("导出中")
        progress_window.geometry("300x100")
        progress_window.resizable(False, False)
        
        # 居中显示
        progress_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (progress_window.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (progress_window.winfo_height() // 2)
        progress_window.geometry("+%d+%d" % (x, y))
        
        # 添加进度条
        ttk.Label(progress_window, text="正在导出图片...").pack(pady=10)
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress_window, variable=progress_var, length=280)
        progress_bar.pack(pady=10)
        
        # 确保进度窗口在最前面
        progress_window.grab_set()
        progress_window.update()
        
        # 导出图片
        success_count = 0
        error_count = 0
        errors = []
        
        try:
            for i, image_path in enumerate(self.imported_images):
                try:
                    # 加载图片
                    image, _ = ImageProcessor.load_image(image_path)
                    
                    # 调整尺寸
                    if resize_percentage != 100:
                        image = ImageProcessor.resize_image(image, percentage=resize_percentage)
                    
                    # 生成输出文件名
                    output_path = FileHandler.generate_output_filename(
                        image_path, 
                        self.output_folder, 
                        prefix=prefix, 
                        suffix=suffix, 
                        output_format=output_format
                    )
                    
                    # 保存图片
                    ImageProcessor.save_image(image, output_path, quality=quality)
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    errors.append(f"{os.path.basename(image_path)}: {str(e)}")
                
                # 更新进度条
                progress_var.set((i + 1) / len(self.imported_images) * 100)
                progress_window.update()
        finally:
            # 关闭进度窗口
            progress_window.destroy()
        
        # 显示导出结果
        if error_count > 0:
            error_msg = "\n".join(errors)
            messagebox.showerror("导出结果", f"成功导出 {success_count} 张图片\n导出失败 {error_count} 张图片\n\n错误详情:\n{error_msg}")
        else:
            messagebox.showinfo("导出结果", f"成功导出 {success_count} 张图片")
            # 打开输出文件夹
            if messagebox.askyesno("完成", "是否打开输出文件夹？"):
                import subprocess
                subprocess.Popen(f'explorer "{self.output_folder}"')