from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                            QLabel, QFileDialog, QListWidget, QListWidgetItem, QScrollArea,
                            QGridLayout, QSlider, QComboBox, QLineEdit, QFrame, QColorDialog,
                            QGroupBox, QSplitter, QMessageBox, QInputDialog, QCheckBox, QSpinBox)
from PyQt5.QtGui import QPixmap, QImage, QFont, QPainter, QColor, QPen, QIcon
from PyQt5.QtCore import Qt, QPoint, QSize, QRect
import os
import sys
import subprocess
from utils.image_processor import ImageProcessor
from utils.template_manager import TemplateManager
from model.watermark_settings import WatermarkSettings

class MainWindow(QMainWindow):
    """应用程序主窗口"""
    def __init__(self):
        super().__init__()
        
        # 设置窗口标题和大小
        self.setWindowTitle("图片水印工具")
        self.resize(1200, 800)
        
        # 初始化模型
        self.image_processor = ImageProcessor()
        self.watermark_settings = WatermarkSettings()
        self.template_manager = TemplateManager()
        
        # 存储已加载的图片路径
        self.loaded_images = []
        self.current_image_index = -1
        
        # 创建UI
        self.init_ui()
        
        # 尝试加载上次的设置
        self.load_last_settings()
        
        # 启用拖放功能
        self.setAcceptDrops(True)
    
    def init_ui(self):
        """初始化用户界面"""
        # 主布局
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)
        
        # 顶部工具栏
        toolbar_widget = QWidget()
        toolbar_layout = QHBoxLayout(toolbar_widget)
        
        # 导入按钮
        self.import_single_btn = QPushButton("导入图片")
        self.import_single_btn.clicked.connect(self.import_single_image)
        
        self.import_batch_btn = QPushButton("批量导入")
        self.import_batch_btn.clicked.connect(self.import_batch_images)
        
        # 导出按钮
        self.export_btn = QPushButton("导出图片")
        self.export_btn.clicked.connect(self.export_images)
        self.export_btn.setEnabled(False)  # 初始禁用，直到有图片加载
        
        toolbar_layout.addWidget(self.import_single_btn)
        toolbar_layout.addWidget(self.import_batch_btn)
        toolbar_layout.addWidget(self.export_btn)
        toolbar_layout.addStretch()
        
        main_layout.addWidget(toolbar_widget)
        
        # 主分割器
        main_splitter = QSplitter(Qt.Horizontal)
        
        # 左侧图片列表
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        left_layout.addWidget(QLabel("图片列表："))
        
        # 图片列表控件
        self.image_list = QListWidget()
        self.image_list.setIconSize(QSize(100, 100))
        self.image_list.setViewMode(QListWidget.IconMode)
        self.image_list.setResizeMode(QListWidget.Adjust)
        self.image_list.setFlow(QListWidget.LeftToRight)
        self.image_list.setWrapping(True)
        self.image_list.itemClicked.connect(self.on_image_item_clicked)
        
        left_layout.addWidget(self.image_list)
        
        # 中间预览区域
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        
        center_layout.addWidget(QLabel("预览："))
        
        # 预览区域
        self.preview_scroll_area = QScrollArea()
        self.preview_scroll_area.setWidgetResizable(True)
        
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(400, 300)
        self.preview_label.setAcceptDrops(True)
        
        self.preview_scroll_area.setWidget(self.preview_label)
        
        # 启用预览区域的鼠标事件处理
        self.preview_label.mousePressEvent = self.on_preview_mouse_press
        self.preview_label.mouseMoveEvent = self.on_preview_mouse_move
        self.preview_label.mouseReleaseEvent = self.on_preview_mouse_release
        
        center_layout.addWidget(self.preview_scroll_area)
        
        # 右侧设置面板
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_widget.setMinimumWidth(300)
        
        # 水印内容设置
        watermark_group = QGroupBox("水印设置")
        watermark_layout = QVBoxLayout()
        
        watermark_layout.addWidget(QLabel("水印文本："))
        self.watermark_text = QLineEdit("水印")
        self.watermark_text.textChanged.connect(self.update_preview)
        watermark_layout.addWidget(self.watermark_text)
        
        # 字体设置
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("字体："))
        self.font_combo = QComboBox()
        self.font_combo.addItems(["SimHei", "Microsoft YaHei", "Arial", "Times New Roman"])
        self.font_combo.currentTextChanged.connect(self.update_preview)
        font_layout.addWidget(self.font_combo)
        watermark_layout.addLayout(font_layout)
        
        # 字号设置
        font_size_layout = QHBoxLayout()
        font_size_layout.addWidget(QLabel("字号："))
        self.font_size_combo = QComboBox()
        # 增加更多字号选项，从8到128，以4为步长增加常用字号，并添加一些较大的字号
        self.font_size_combo.addItems(["8", "10", "12", "14", "16", "18", "20", "24", "28", "32", "36", "40", "48", "64", "72", "96", "128", "160", "200"])
        self.font_size_combo.setCurrentText("24")
        self.font_size_combo.currentTextChanged.connect(self.update_preview)
        font_size_layout.addWidget(self.font_size_combo)
        watermark_layout.addLayout(font_size_layout)
        
        # 颜色设置
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("颜色："))
        self.color_button = QPushButton()
        self.color_button.setStyleSheet("background-color: rgba(255, 0, 0, 150);")
        self.color_button.clicked.connect(self.choose_color)
        color_layout.addWidget(self.color_button)
        watermark_layout.addLayout(color_layout)
        
        # 透明度设置
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("透明度："))
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(50)
        self.opacity_slider.valueChanged.connect(self.update_preview)
        opacity_layout.addWidget(self.opacity_slider)
        opacity_layout.addWidget(QLabel("50%"))
        self.opacity_slider.valueChanged.connect(lambda value: opacity_layout.itemAt(2).widget().setText(f"{value}%"))
        watermark_layout.addLayout(opacity_layout)
        
        # 样式效果分割线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        watermark_layout.addWidget(line)
        
        # 阴影效果设置
        shadow_layout = QVBoxLayout()
        shadow_header_layout = QHBoxLayout()
        self.shadow_checkbox = QCheckBox("阴影效果")
        self.shadow_checkbox.stateChanged.connect(self.update_preview)
        shadow_header_layout.addWidget(self.shadow_checkbox)
        shadow_layout.addLayout(shadow_header_layout)
        
        # 阴影设置控件组，默认隐藏
        self.shadow_settings_widget = QWidget()
        shadow_settings_layout = QVBoxLayout(self.shadow_settings_widget)
        
        # 阴影颜色
        shadow_color_layout = QHBoxLayout()
        shadow_color_layout.addWidget(QLabel("阴影颜色："))
        self.shadow_color_button = QPushButton()
        self.shadow_color_button.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.shadow_color_button.clicked.connect(self.choose_shadow_color)
        shadow_color_layout.addWidget(self.shadow_color_button)
        shadow_settings_layout.addLayout(shadow_color_layout)
        
        # 阴影偏移
        shadow_offset_layout = QHBoxLayout()
        shadow_offset_layout.addWidget(QLabel("偏移："))
        self.shadow_offset_x = QSpinBox()
        self.shadow_offset_x.setRange(-10, 10)
        self.shadow_offset_x.setValue(2)
        self.shadow_offset_x.valueChanged.connect(self.update_preview)
        shadow_offset_layout.addWidget(QLabel("X:"))
        shadow_offset_layout.addWidget(self.shadow_offset_x)
        
        self.shadow_offset_y = QSpinBox()
        self.shadow_offset_y.setRange(-10, 10)
        self.shadow_offset_y.setValue(2)
        self.shadow_offset_y.valueChanged.connect(self.update_preview)
        shadow_offset_layout.addWidget(QLabel("Y:"))
        shadow_offset_layout.addWidget(self.shadow_offset_y)
        shadow_settings_layout.addLayout(shadow_offset_layout)
        
        # 阴影模糊
        shadow_blur_layout = QHBoxLayout()
        shadow_blur_layout.addWidget(QLabel("模糊："))
        self.shadow_blur = QSpinBox()
        self.shadow_blur.setRange(0, 20)
        self.shadow_blur.setValue(2)
        self.shadow_blur.valueChanged.connect(self.update_preview)
        shadow_blur_layout.addWidget(self.shadow_blur)
        shadow_settings_layout.addLayout(shadow_blur_layout)
        
        shadow_layout.addWidget(self.shadow_settings_widget)
        self.shadow_settings_widget.setVisible(False)
        self.shadow_checkbox.stateChanged.connect(lambda state: self.shadow_settings_widget.setVisible(state == Qt.Checked))
        
        watermark_layout.addLayout(shadow_layout)
        
        # 描边效果设置
        stroke_layout = QVBoxLayout()
        stroke_header_layout = QHBoxLayout()
        self.stroke_checkbox = QCheckBox("描边效果")
        self.stroke_checkbox.stateChanged.connect(self.update_preview)
        stroke_header_layout.addWidget(self.stroke_checkbox)
        stroke_layout.addLayout(stroke_header_layout)
        
        # 描边设置控件组，默认隐藏
        self.stroke_settings_widget = QWidget()
        stroke_settings_layout = QVBoxLayout(self.stroke_settings_widget)
        
        # 描边颜色
        stroke_color_layout = QHBoxLayout()
        stroke_color_layout.addWidget(QLabel("描边颜色："))
        self.stroke_color_button = QPushButton()
        self.stroke_color_button.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.stroke_color_button.clicked.connect(self.choose_stroke_color)
        stroke_color_layout.addWidget(self.stroke_color_button)
        stroke_settings_layout.addLayout(stroke_color_layout)
        
        # 描边宽度
        stroke_width_layout = QHBoxLayout()
        stroke_width_layout.addWidget(QLabel("描边宽度："))
        self.stroke_width = QSpinBox()
        self.stroke_width.setRange(1, 10)
        self.stroke_width.setValue(1)
        self.stroke_width.valueChanged.connect(self.update_preview)
        stroke_width_layout.addWidget(self.stroke_width)
        stroke_settings_layout.addLayout(stroke_width_layout)
        
        stroke_layout.addWidget(self.stroke_settings_widget)
        self.stroke_settings_widget.setVisible(False)
        self.stroke_checkbox.stateChanged.connect(lambda state: self.stroke_settings_widget.setVisible(state == Qt.Checked))
        
        watermark_layout.addLayout(stroke_layout)
        
        watermark_group.setLayout(watermark_layout)
        right_layout.addWidget(watermark_group)
        
        # 水印位置设置
        position_group = QGroupBox("水印位置")
        position_layout = QGridLayout()
        
        positions = [
            ("左上", (0, 0)), ("上中", (0, 1)), ("右上", (0, 2)),
            ("左中", (1, 0)), ("中心", (1, 1)), ("右中", (1, 2)),
            ("左下", (2, 0)), ("下中", (2, 1)), ("右下", (2, 2))
        ]
        
        self.position_buttons = {}
        for text, pos in positions:
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, p=pos: self.set_watermark_position(p))
            position_layout.addWidget(btn, pos[0], pos[1])
            self.position_buttons[pos] = btn
        
        position_group.setLayout(position_layout)
        right_layout.addWidget(position_group)
        
        # 导出设置
        export_group = QGroupBox("导出设置")
        export_layout = QVBoxLayout()
        
        # 输出格式
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("输出格式："))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PNG", "JPEG"])
        format_layout.addWidget(self.format_combo)
        export_layout.addLayout(format_layout)
        
        # 文件命名规则
        name_layout = QVBoxLayout()
        name_layout.addWidget(QLabel("文件命名："))
        
        self.prefix_edit = QLineEdit()
        self.prefix_edit.setPlaceholderText("前缀")
        name_layout.addWidget(self.prefix_edit)
        
        self.suffix_edit = QLineEdit()
        self.suffix_edit.setPlaceholderText("后缀")
        name_layout.addWidget(self.suffix_edit)
        
        export_layout.addLayout(name_layout)
        
        export_group.setLayout(export_layout)
        right_layout.addWidget(export_group)
        
        # 模板管理
        template_group = QGroupBox("模板管理")
        template_layout = QVBoxLayout()
        
        template_btns_layout = QHBoxLayout()
        self.save_template_btn = QPushButton("保存模板")
        self.save_template_btn.clicked.connect(self.save_template)
        template_btns_layout.addWidget(self.save_template_btn)
        
        self.load_template_btn = QPushButton("加载模板")
        self.load_template_btn.clicked.connect(self.load_template)
        template_btns_layout.addWidget(self.load_template_btn)
        
        template_layout.addLayout(template_btns_layout)
        
        template_group.setLayout(template_layout)
        right_layout.addWidget(template_group)
        
        right_layout.addStretch()
        
        # 添加到分割器
        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(center_widget)
        main_splitter.addWidget(right_widget)
        
        # 设置分割器比例
        main_splitter.setSizes([200, 600, 300])
        
        main_layout.addWidget(main_splitter)
    
    def import_single_image(self):
        """导入单张图片"""
        # 使用上次的导入目录，如果有
        last_import_dir = getattr(self.watermark_settings, 'last_import_dir', '')
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", last_import_dir, "图片文件 (*.jpg *.jpeg *.png *.bmp *.tif *.tiff)"
        )
        
        if file_path:
            # 保存当前导入目录
            self.watermark_settings.last_import_dir = os.path.dirname(file_path)
            self.template_manager.save_last_settings(self.watermark_settings)
            
            self.add_image_to_list(file_path)
    
    def import_batch_images(self):
        """批量导入图片"""
        # 使用上次的导入目录，如果有
        last_import_dir = getattr(self.watermark_settings, 'last_import_dir', '')
        
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "选择图片", last_import_dir, "图片文件 (*.jpg *.jpeg *.png *.bmp *.tif *.tiff)"
        )
        
        for file_path in file_paths:
            self.add_image_to_list(file_path)
        
        # 保存当前导入目录（如果有选择文件）
        if file_paths:
            self.watermark_settings.last_import_dir = os.path.dirname(file_paths[0])
            self.template_manager.save_last_settings(self.watermark_settings)
        
        # 或者导入整个文件夹
        if not file_paths:
            folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹", last_import_dir)
            if folder_path:
                # 保存当前导入目录
                self.watermark_settings.last_import_dir = folder_path
                self.template_manager.save_last_settings(self.watermark_settings)
                
                for file_name in os.listdir(folder_path):
                    if file_name.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff")):
                        self.add_image_to_list(os.path.join(folder_path, file_name))
    
    def add_image_to_list(self, file_path):
        """将图片添加到列表"""
        if file_path in self.loaded_images:
            return
        
        self.loaded_images.append(file_path)
        
        # 创建列表项
        item = QListWidgetItem()
        item.setText(os.path.basename(file_path))
        
        # 创建缩略图
        pixmap = QPixmap(file_path)
        if not pixmap.isNull():
            thumbnail = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            item.setIcon(QIcon(thumbnail))
        
        self.image_list.addItem(item)
        
        # 启用导出按钮
        self.export_btn.setEnabled(True)
        
        # 如果是第一张图片，自动选中
        if len(self.loaded_images) == 1:
            self.image_list.setCurrentItem(item)
            self.current_image_index = 0
            self.update_preview()
    
    def on_image_item_clicked(self, item):
        """点击图片列表项时的处理"""
        self.current_image_index = self.image_list.row(item)
        self.update_preview()
    
    def update_preview(self):
        """更新预览窗口"""
        if self.current_image_index < 0 or self.current_image_index >= len(self.loaded_images):
            return
        
        file_path = self.loaded_images[self.current_image_index]
        
        # 更新水印设置
        self.update_watermark_settings()
        
        # 处理图片
        preview_image = self.image_processor.process_image(file_path, self.watermark_settings)
        
        # 显示预览
        if preview_image:
            # 根据图像模式选择正确的QImage格式
            if preview_image.mode == "RGBA":
                # RGBA模式，每像素4个字节
                qimage = QImage(
                    preview_image.tobytes(),
                    preview_image.width,
                    preview_image.height,
                    preview_image.width * 4,
                    QImage.Format_RGBA8888
                )
            else:
                # RGB模式，每像素3个字节
                qimage = QImage(
                    preview_image.tobytes(),
                    preview_image.width,
                    preview_image.height,
                    preview_image.width * 3,
                    QImage.Format_RGB888
                )
            
            pixmap = QPixmap.fromImage(qimage)
            
            # 缩放以适应预览窗口
            scaled_pixmap = pixmap.scaled(
                self.preview_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            self.preview_label.setPixmap(scaled_pixmap)
    
    def update_watermark_settings(self):
        """更新水印设置"""
        # 文本内容
        self.watermark_settings.text = self.watermark_text.text()
        
        # 字体设置
        self.watermark_settings.font = self.font_combo.currentText()
        
        # 字号设置
        try:
            self.watermark_settings.font_size = int(self.font_size_combo.currentText())
        except ValueError:
            self.watermark_settings.font_size = 24
        
        # 颜色设置
        try:
            # 尝试从样式表中提取颜色值
            style_sheet = self.color_button.styleSheet()
            rgba_part = style_sheet.split("rgba(")[-1].split(")")[0]
            color_values = rgba_part.split(",")
            
            # 提取RGB值
            if len(color_values) >= 3:
                r = int(color_values[0].strip())
                g = int(color_values[1].strip())
                b = int(color_values[2].strip())
                self.watermark_settings.color = (r, g, b)
        except Exception as e:
            print(f"Error extracting color: {e}")
            # 如果解析失败，保持当前颜色不变
        
        # 透明度设置
        self.watermark_settings.opacity = self.opacity_slider.value() / 100.0
        
        # 阴影效果设置
        self.watermark_settings.has_shadow = self.shadow_checkbox.isChecked()
        
        # 阴影颜色设置
        try:
            # 从样式表中提取颜色值
            shadow_style_sheet = self.shadow_color_button.styleSheet()
            if "rgb(" in shadow_style_sheet:
                rgb_part = shadow_style_sheet.split("rgb(")[-1].split(")")[0]
                shadow_color_values = rgb_part.split(",")
                if len(shadow_color_values) >= 3:
                    sr = int(shadow_color_values[0].strip())
                    sg = int(shadow_color_values[1].strip())
                    sb = int(shadow_color_values[2].strip())
                    self.watermark_settings.shadow_color = (sr, sg, sb)
        except Exception as e:
            print(f"Error extracting shadow color: {e}")
            # 如果解析失败，保持当前颜色不变
        
        # 阴影偏移设置
        self.watermark_settings.shadow_offset = (self.shadow_offset_x.value(), self.shadow_offset_y.value())
        
        # 阴影模糊设置
        self.watermark_settings.shadow_blur = self.shadow_blur.value()
        
        # 描边效果设置
        self.watermark_settings.has_stroke = self.stroke_checkbox.isChecked()
        
        # 描边颜色设置
        try:
            # 从样式表中提取颜色值
            stroke_style_sheet = self.stroke_color_button.styleSheet()
            if "rgb(" in stroke_style_sheet:
                rgb_part = stroke_style_sheet.split("rgb(")[-1].split(")")[0]
                stroke_color_values = rgb_part.split(",")
                if len(stroke_color_values) >= 3:
                    str_r = int(stroke_color_values[0].strip())
                    stg = int(stroke_color_values[1].strip())
                    stb = int(stroke_color_values[2].strip())
                    self.watermark_settings.stroke_color = (str_r, stg, stb)
        except Exception as e:
            print(f"Error extracting stroke color: {e}")
            # 如果解析失败，保持当前颜色不变
        
        # 描边宽度设置
        self.watermark_settings.stroke_width = self.stroke_width.value()
    
    def choose_color(self):
        """选择水印颜色"""
        color = QColorDialog.getColor()
        if color.isValid():
            # 设置按钮背景色
            opacity = int(self.opacity_slider.value() * 2.55)
            self.color_button.setStyleSheet(
                f"background-color: rgba({color.red()}, {color.green()}, {color.blue()}, {opacity});"
            )
            self.update_preview()
    
    def choose_shadow_color(self):
        """选择阴影颜色"""
        color = QColorDialog.getColor()
        if color.isValid():
            # 设置按钮背景色（阴影颜色不考虑透明度，始终为不透明）
            self.shadow_color_button.setStyleSheet(
                f"background-color: rgb({color.red()}, {color.green()}, {color.blue()});"
            )
            self.update_preview()
    
    def choose_stroke_color(self):
        """选择描边颜色"""
        color = QColorDialog.getColor()
        if color.isValid():
            # 设置按钮背景色（描边颜色不考虑透明度，始终为不透明）
            self.stroke_color_button.setStyleSheet(
                f"background-color: rgb({color.red()}, {color.green()}, {color.blue()});"
            )
            self.update_preview()
    
    def set_watermark_position(self, position):
        """设置水印位置"""
        # 取消所有按钮的选中状态
        for btn in self.position_buttons.values():
            btn.setStyleSheet("")
        
        # 设置当前按钮的选中状态
        self.position_buttons[position].setStyleSheet("background-color: lightblue;")
        
        # 更新水印位置
        self.watermark_settings.position = position
        
        # 清除手动拖拽位置
        self.watermark_settings.custom_position = None
        
        # 更新预览
        self.update_preview()
    
    def on_preview_mouse_press(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_start_pos = event.pos()
    
    def on_preview_mouse_move(self, event):
        """鼠标移动事件"""
        if self.dragging:
            # 这里可以添加拖拽的视觉反馈
            pass
    
    def on_preview_mouse_release(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton and self.dragging:
            self.dragging = False
            
            # 计算水印的相对位置
            if self.preview_label.pixmap():
                pixmap_rect = self.preview_label.pixmap().rect()
                label_rect = self.preview_label.rect()
                
                # 计算预览图在标签中的位置
                x_ratio = (event.pos().x() - (label_rect.width() - pixmap_rect.width()) / 2) / pixmap_rect.width()
                y_ratio = (event.pos().y() - (label_rect.height() - pixmap_rect.height()) / 2) / pixmap_rect.height()
                
                # 确保在有效范围内
                x_ratio = max(0, min(1, x_ratio))
                y_ratio = max(0, min(1, y_ratio))
                
                # 设置自定义位置
                self.watermark_settings.custom_position = (x_ratio, y_ratio)
                
                # 取消位置按钮的选中状态
                for btn in self.position_buttons.values():
                    btn.setStyleSheet("")
                
                # 更新预览
                self.update_preview()
    
    def export_images(self):
        """导出图片"""
        if not self.loaded_images:
            return
        
        # 使用上次的导出目录，如果有
        last_export_dir = getattr(self.watermark_settings, 'last_export_dir', '')
        
        # 选择导出文件夹
        export_dir = QFileDialog.getExistingDirectory(self, "选择导出文件夹", last_export_dir)
        if not export_dir:
            return
        
        # 检查是否是原图片所在文件夹
        original_dirs = set()
        for file_path in self.loaded_images:
            original_dirs.add(os.path.dirname(file_path))
            
        if export_dir in original_dirs:
            reply = QMessageBox.warning(
                self, "警告", "您选择的是原图片所在文件夹，可能会覆盖原文件。是否继续？",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        # 更新水印设置
        self.update_watermark_settings()
        
        # 处理并导出每张图片
        for file_path in self.loaded_images:
            # 获取文件名和扩展名
            base_name = os.path.basename(file_path)
            name_without_ext = os.path.splitext(base_name)[0]
            
            # 应用命名规则
            prefix = self.prefix_edit.text()
            suffix = self.suffix_edit.text()
            
            new_name = f"{prefix}{name_without_ext}{suffix}"
            
            # 应用输出格式
            format_str = self.format_combo.currentText().lower()
            
            # 构建输出路径
            output_path = os.path.join(export_dir, f"{new_name}.{format_str}")
            
            # 处理图片并保存
            self.image_processor.process_and_save(file_path, output_path, self.watermark_settings, format_str)
        
        # 保存当前导出目录
        self.watermark_settings.last_export_dir = export_dir
        self.template_manager.save_last_settings(self.watermark_settings)
        
        # 询问是否打开导出文件夹
        reply = QMessageBox.question(
            self, "导出完成", 
            f"已成功导出 {len(self.loaded_images)} 张图片！是否打开导出文件夹？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            # 打开导出文件夹
            if os.name == 'nt':  # Windows
                os.startfile(export_dir)
            elif os.name == 'posix':  # macOS or Linux
                subprocess.run(['open' if sys.platform == 'darwin' else 'xdg-open', export_dir])
    
    def save_template(self):
        """保存水印模板"""
        # 获取模板名称
        template_name, ok = QInputDialog.getText(self, "保存模板", "请输入模板名称：")
        if ok and template_name:
            # 更新水印设置
            self.update_watermark_settings()
            
            # 保存模板
            self.template_manager.save_template(template_name, self.watermark_settings)
            
            QMessageBox.information(self, "成功", f"模板 '{template_name}' 已保存！")
    
    def load_template(self):
        """加载水印模板"""
        # 获取可用模板列表
        templates = self.template_manager.get_available_templates()
        if not templates:
            QMessageBox.information(self, "提示", "没有可用的模板！")
            return
        
        # 显示模板选择对话框
        template_name, ok = QInputDialog.getItem(self, "加载模板", "请选择模板：", templates, 0, False)
        if ok:
            # 加载模板
            settings = self.template_manager.load_template(template_name)
            if settings:
                # 应用设置
                self.apply_template_settings(settings)
                
                QMessageBox.information(self, "成功", f"模板 '{template_name}' 已加载！")
    
    def apply_template_settings(self, settings):
        """应用模板设置"""
        # 应用文本设置
        self.watermark_text.setText(settings.text)
        
        # 应用字体设置
        font_index = self.font_combo.findText(settings.font)
        if font_index >= 0:
            self.font_combo.setCurrentIndex(font_index)
        
        # 应用字号设置
        self.font_size_combo.setCurrentText(str(settings.font_size))
        
        # 应用颜色设置
        r, g, b = settings.color
        opacity = int(settings.opacity * 100)
        self.color_button.setStyleSheet(
            f"background-color: rgba({r}, {g}, {b}, {opacity * 2.55});"
        )
        
        # 应用透明度设置
        self.opacity_slider.setValue(int(settings.opacity * 100))
        
        # 应用位置设置
        if settings.position:
            self.set_watermark_position(settings.position)
        elif settings.custom_position:
            self.watermark_settings.custom_position = settings.custom_position
            # 取消位置按钮的选中状态
            for btn in self.position_buttons.values():
                btn.setStyleSheet("")
        
        # 更新预览
        self.update_preview()
    
    def load_last_settings(self):
        """加载上次的设置"""
        settings = self.template_manager.load_last_settings()
        if settings:
            self.apply_template_settings(settings)
    
    def closeEvent(self, event):
        """关闭窗口时保存设置"""
        # 更新水印设置
        self.update_watermark_settings()
        
        # 保存当前设置
        self.template_manager.save_last_settings(self.watermark_settings)
        
        event.accept()