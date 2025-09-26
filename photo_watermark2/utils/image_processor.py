from PIL import Image, ImageDraw, ImageFont
import os

class ImageProcessor:
    """图片处理器，负责图片的加载、处理和保存"""
    
    def __init__(self):
        """初始化图片处理器"""
        # 获取当前目录
        self.current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    def process_image(self, image_path, watermark_settings):
        """处理图片，添加水印并返回处理后的图片对象"""
        try:
            # 打开图片
            image = Image.open(image_path).convert("RGBA")
            
            # 创建一个新的透明图层用于水印
            watermark_layer = Image.new("RGBA", image.size, (255, 255, 255, 0))
            
            # 获取绘图对象
            draw = ImageDraw.Draw(watermark_layer)
            
            # 添加文本水印
            self._add_text_watermark(draw, watermark_settings, image.size)
            
            # 合并图层
            result = Image.alpha_composite(image, watermark_layer)
            
            # 保留透明度信息，不转换为RGB模式
            return result
        except Exception as e:
            print(f"处理图片时出错：{e}")
            return None
    
    def _add_text_watermark(self, draw, watermark_settings, image_size):
        """添加文本水印"""
        text = watermark_settings.text
        if not text:
            return
        
        # 设置字体
        font = None
        font_name = watermark_settings.font
        
        # 为不同字体构建系统路径映射
        font_path_mapping = {
            "SimHei": [
                "C:/Windows/Fonts/simhei.ttf",  # Windows 黑体
                "/Library/Fonts/SimHei.ttf",  # macOS 黑体
                "/usr/share/fonts/windows/simhei.ttf"  # Linux 黑体
            ],
            "Microsoft YaHei": [
                "C:/Windows/Fonts/msyh.ttc",  # Windows 微软雅黑
                "C:/Windows/Fonts/msyhbd.ttc",  # Windows 微软雅黑加粗
                "/Library/Fonts/Microsoft YaHei.ttf"  # macOS 微软雅黑
            ],
            "Arial": [
                "C:/Windows/Fonts/arial.ttf",  # Windows Arial
                "C:/Windows/Fonts/arialbd.ttf",  # Windows Arial 粗体
                "/Library/Fonts/Arial.ttf",  # macOS Arial
                "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf"  # Linux Arial
            ],
            "Times New Roman": [
                "C:/Windows/Fonts/times.ttf",  # Windows Times New Roman
                "C:/Windows/Fonts/timesbd.ttf",  # Windows Times New Roman 粗体
                "/Library/Fonts/Times New Roman.ttf",  # macOS Times New Roman
                "/usr/share/fonts/truetype/msttcorefonts/times.ttf"  # Linux Times New Roman
            ]
        }
        
        # 尝试加载指定字体
        try:
            # 首先尝试直接使用字体名称（可能在某些系统上可行）
            font = ImageFont.truetype(font_name, watermark_settings.font_size)
        except (IOError, OSError):
            # 如果直接加载失败，尝试在系统字体目录中查找
            if font_name in font_path_mapping:
                for path in font_path_mapping[font_name]:
                    if os.path.exists(path):
                        try:
                            font = ImageFont.truetype(path, watermark_settings.font_size)
                            break
                        except:
                            continue
            
            # 如果找不到指定字体，尝试加载默认字体
            if font is None:
                try:
                    # 最后的备选方案 - 首先尝试黑体作为中文的后备选项
                    for path in font_path_mapping.get("SimHei", []):
                        if os.path.exists(path):
                            font = ImageFont.truetype(path, watermark_settings.font_size)
                            break
                    
                    # 如果还是不行，使用PIL默认字体
                    if font is None:
                        font = ImageFont.load_default()
                except:
                    font = ImageFont.load_default()
        
        # 获取文本尺寸
        try:
            # 尝试使用getbbox()方法（PIL 8.0+）
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except AttributeError:
            # 回退到旧的textsize()方法
            text_width, text_height = draw.textsize(text, font=font)
        
        # 计算文本位置
        x, y = self._calculate_text_position(watermark_settings, image_size, text_width, text_height)
        
        # 设置文本颜色和透明度
        r, g, b = watermark_settings.color
        fill_color = (r, g, b, int(watermark_settings.opacity * 255))
        
        # 添加文本水印
        draw.text((x, y), text, font=font, fill=fill_color)
    
    def _calculate_text_position(self, watermark_settings, image_size, text_width, text_height):
        """计算文本水印的位置"""
        img_width, img_height = image_size
        
        # 如果有自定义位置，使用自定义位置
        if watermark_settings.custom_position:
            x_ratio, y_ratio = watermark_settings.custom_position
            x = (img_width - text_width) * x_ratio
            y = (img_height - text_height) * y_ratio
            return x, y
        
        # 否则使用预设位置
        if not watermark_settings.position:
            # 默认位置：右下角
            watermark_settings.position = (2, 2)
        
        row, col = watermark_settings.position
        
        # 定义边距
        margin = 10
        
        # 计算水平位置
        if col == 0:  # 左
            x = margin
        elif col == 1:  # 中
            x = (img_width - text_width) // 2
        else:  # 右
            x = img_width - text_width - margin
        
        # 计算垂直位置
        if row == 0:  # 上
            y = margin
        elif row == 1:  # 中
            y = (img_height - text_height) // 2
        else:  # 下
            y = img_height - text_height - margin
        
        return x, y
    
    def process_and_save(self, input_path, output_path, watermark_settings, output_format="png"):
        """处理图片并保存结果"""
        try:
            # 处理图片
            processed_image = self.process_image(input_path, watermark_settings)
            
            if processed_image:
                # 保存图片
                if output_format.lower() == "jpeg":
                    # JPEG不支持透明通道，转换为RGB
                    if processed_image.mode == "RGBA":
                        processed_image = processed_image.convert("RGB")
                    processed_image.save(output_path, "JPEG", quality=95)
                else:
                    processed_image.save(output_path, "PNG")
        except Exception as e:
            print(f"保存图片时出错：{e}")
            # 可以选择在这里抛出异常，让调用者处理