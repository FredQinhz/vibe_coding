from PIL import Image, ImageDraw, ImageFont, ImageFilter
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
            ],
            "宋体": [
                "C:/Windows/Fonts/simsun.ttc",  # Windows 宋体
                "/Library/Fonts/Songti.ttc",  # macOS 宋体
                "/usr/share/fonts/windows/simsun.ttc"  # Linux 宋体
            ],
            "新宋体": [
                "C:/Windows/Fonts/nsimsun.ttc",  # Windows 新宋体
                "/Library/Fonts/Songti.ttc",  # macOS 宋体（作为备选）
                "/usr/share/fonts/windows/nsimsun.ttc"  # Linux 新宋体
            ],
            "仿宋": [
                "C:/Windows/Fonts/simfang.ttf",  # Windows 仿宋
                "C:/Windows/Fonts/STFANGSO.TTF",  # Windows 仿宋_GB2312
                "/usr/share/fonts/windows/simfang.ttf"  # Linux 仿宋
            ],
            "楷体": [
                "C:/Windows/Fonts/simkai.ttf",  # Windows 楷体
                "C:/Windows/Fonts/STKAITI.TTF",  # Windows 楷体_GB2312
                "/usr/share/fonts/windows/simkai.ttf"  # Linux 楷体
            ],
            "微软雅黑 Light": [
                "C:/Windows/Fonts/msyhl.ttc",  # Windows 微软雅黑 Light
                "/Library/Fonts/Microsoft YaHei Light.ttf",  # macOS 微软雅黑 Light
                "/usr/share/fonts/windows/msyhl.ttc"  # Linux 微软雅黑 Light
            ],
            "微软正黑": [
                "C:/Windows/Fonts/msjh.ttc",  # Windows 微软正黑
                "C:/Windows/Fonts/msjhbd.ttc",  # Windows 微软正黑加粗
                "/Library/Fonts/Microsoft JhengHei.ttf"  # macOS 微软正黑体
            ],
            "Courier New": [
                "C:/Windows/Fonts/cour.ttf",  # Windows Courier New
                "C:/Windows/Fonts/courbd.ttf",  # Windows Courier New 粗体
                "/Library/Fonts/Courier New.ttf",  # macOS Courier New
                "/usr/share/fonts/truetype/msttcorefonts/cour.ttf"  # Linux Courier New
            ],
            "Verdana": [
                "C:/Windows/Fonts/verdana.ttf",  # Windows Verdana
                "C:/Windows/Fonts/verdanab.ttf",  # Windows Verdana 粗体
                "/Library/Fonts/Verdana.ttf",  # macOS Verdana
                "/usr/share/fonts/truetype/msttcorefonts/verdana.ttf"  # Linux Verdana
            ],
            "Comic Sans MS": [
                "C:/Windows/Fonts/comic.ttf",  # Windows Comic Sans MS
                "C:/Windows/Fonts/comicbd.ttf",  # Windows Comic Sans MS 粗体
                "/Library/Fonts/Comic Sans MS.ttf",  # macOS Comic Sans MS
                "/usr/share/fonts/truetype/msttcorefonts/comic.ttf"  # Linux Comic Sans MS
            ],
            "Impact": [
                "C:/Windows/Fonts/impact.ttf",  # Windows Impact
                "/Library/Fonts/Impact.ttf",  # macOS Impact
                "/usr/share/fonts/truetype/msttcorefonts/impact.ttf"  # Linux Impact
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
        
        # 处理阴影效果
        if watermark_settings.has_shadow:
            # 获取阴影颜色、偏移和模糊值
            sh_r, sh_g, sh_b = watermark_settings.shadow_color
            shadow_fill = (sh_r, sh_g, sh_b, 255)  # 阴影始终为不透明
            shadow_offset_x, shadow_offset_y = watermark_settings.shadow_offset
            shadow_blur = watermark_settings.shadow_blur
            shadow_x = x + shadow_offset_x
            shadow_y = y + shadow_offset_y
            
            # 创建一个临时图像用于绘制阴影
            temp_img = Image.new('RGBA', (image_size[0], image_size[1]), (0, 0, 0, 0))
            temp_draw = ImageDraw.Draw(temp_img)
            
            # 在临时图像上绘制阴影
            if watermark_settings.has_stroke:
                # 阴影也需要带描边
                sr, sg, sb = watermark_settings.stroke_color
                stroke_color = (sr, sg, sb, 255)
                stroke_width = watermark_settings.stroke_width
                
                try:
                    # 使用PIL的描边功能
                    temp_draw.text((shadow_x, shadow_y), text, font=font, fill=shadow_fill,
                                  stroke_width=stroke_width, stroke_fill=stroke_color)
                except TypeError:
                    # 替代方法
                    directions = [(-1, -1), (-1, 0), (-1, 1),
                                 (0, -1),          (0, 1),
                                 (1, -1),  (1, 0), (1, 1)]
                    
                    # 绘制描边
                    for dx, dy in directions:
                        temp_draw.text((shadow_x + dx * stroke_width, shadow_y + dy * stroke_width), 
                                     text, font=font, fill=stroke_color)
                    
                    # 绘制阴影文本
                    temp_draw.text((shadow_x, shadow_y), text, font=font, fill=shadow_fill)
            else:
                # 阴影不带描边
                temp_draw.text((shadow_x, shadow_y), text, font=font, fill=shadow_fill)
            
            # 应用模糊效果
            if shadow_blur > 0:
                # 计算需要裁剪的区域，以提高模糊效率
                # 获取文本边界
                try:
                    bbox = temp_draw.textbbox((shadow_x, shadow_y), text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                except AttributeError:
                    text_width, text_height = temp_draw.textsize(text, font=font)
                
                # 添加模糊半径的缓冲区
                buffer = shadow_blur * 2
                crop_box = (
                    max(0, shadow_x - buffer),
                    max(0, shadow_y - buffer),
                    min(image_size[0], shadow_x + text_width + buffer),
                    min(image_size[1], shadow_y + text_height + buffer)
                )
                
                # 裁剪并模糊
                shadow_cropped = temp_img.crop(crop_box)
                shadow_blurred = shadow_cropped.filter(ImageFilter.GaussianBlur(radius=shadow_blur))
                
                # 将模糊后的阴影粘贴回原始图像
                draw.bitmap((crop_box[0], crop_box[1]), shadow_blurred, fill=None)
            else:
                # 没有模糊效果，直接粘贴
                draw.bitmap((0, 0), temp_img, fill=None)
        
        # 处理描边效果
        if watermark_settings.has_stroke:
            # 获取描边颜色和宽度
            sr, sg, sb = watermark_settings.stroke_color
            stroke_color = (sr, sg, sb, 255)
            stroke_width = watermark_settings.stroke_width
            
            try:
                # 使用PIL的描边功能
                draw.text((x, y), text, font=font, fill=fill_color,
                          stroke_width=stroke_width, stroke_fill=stroke_color)
            except TypeError:
                # 替代方法
                directions = [(-1, -1), (-1, 0), (-1, 1),
                             (0, -1),          (0, 1),
                             (1, -1),  (1, 0), (1, 1)]
                
                # 绘制描边
                for dx, dy in directions:
                    draw.text((x + dx * stroke_width, y + dy * stroke_width), 
                              text, font=font, fill=stroke_color)
                
                # 绘制主文本
                draw.text((x, y), text, font=font, fill=fill_color)
        else:
            # 没有描边效果，直接绘制主文本
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