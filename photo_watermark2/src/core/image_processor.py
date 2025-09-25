from PIL import Image
import os

class ImageProcessor:
    """
    图像处理类，负责图片的加载、处理和保存
    """
    
    # 支持的输入图像格式
    SUPPORTED_INPUT_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
    
    # 支持的输出图像格式
    SUPPORTED_OUTPUT_FORMATS = {'.jpg', '.jpeg', '.png'}
    
    @staticmethod
    def load_image(file_path):
        """
        加载图片文件
        
        Args:
            file_path (str): 图片文件路径
            
        Returns:
            tuple: (PIL.Image对象, 原始图像格式)
        
        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 不支持的图像格式
            IOError: 图像加载失败
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
            
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in ImageProcessor.SUPPORTED_INPUT_FORMATS:
            raise ValueError(f"不支持的图像格式: {file_ext}")
            
        try:
            image = Image.open(file_path)
            # 确保PNG支持透明通道
            if file_ext == '.png' and image.mode != 'RGBA':
                image = image.convert('RGBA')
            return image, file_ext
        except Exception as e:
            raise IOError(f"图像加载失败: {str(e)}")
    
    @staticmethod
    def save_image(image, output_path, output_format=None, quality=95):
        """
        保存图片文件
        
        Args:
            image (PIL.Image): 图像对象
            output_path (str): 输出文件路径
            output_format (str, optional): 输出格式
            quality (int, optional): JPEG质量 (1-100)
            
        Returns:
            str: 保存的文件路径
        
        Raises:
            ValueError: 不支持的输出格式
            IOError: 图像保存失败
        """
        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # 确定输出格式
        file_ext = os.path.splitext(output_path)[1].lower()
        if not file_ext:
            if not output_format:
                raise ValueError("未指定输出格式")
            file_ext = output_format.lower()
            if not file_ext.startswith('.'):
                file_ext = '.' + file_ext
            output_path += file_ext
        elif output_format:
            # 如果指定了输出格式，覆盖文件扩展名
            output_format = output_format.lower()
            if not output_format.startswith('.'):
                output_format = '.' + output_format
            base_name = os.path.splitext(output_path)[0]
            output_path = base_name + output_format
            file_ext = output_format
        
        # 检查输出格式是否支持
        if file_ext not in ImageProcessor.SUPPORTED_OUTPUT_FORMATS:
            raise ValueError(f"不支持的输出格式: {file_ext}")
            
        try:
            # 处理透明通道
            if file_ext in ('.jpg', '.jpeg') and image.mode == 'RGBA':
                # 创建白色背景
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])  # 3是alpha通道
                image = background
            
            # 保存图片
            save_params = {}
            if file_ext in ('.jpg', '.jpeg'):
                save_params['quality'] = max(1, min(100, quality))
            
            image.save(output_path, **save_params)
            return output_path
        except Exception as e:
            raise IOError(f"图像保存失败: {str(e)}")
    
    @staticmethod
    def resize_image(image, width=None, height=None, percentage=None):
        """
        调整图片尺寸
        
        Args:
            image (PIL.Image): 图像对象
            width (int, optional): 目标宽度
            height (int, optional): 目标高度
            percentage (float, optional): 缩放百分比
            
        Returns:
            PIL.Image: 调整后的图像对象
        """
        if percentage:
            new_width = int(image.width * percentage / 100)
            new_height = int(image.height * percentage / 100)
        elif width and height:
            new_width = width
            new_height = height
        elif width:
            aspect_ratio = image.height / image.width
            new_width = width
            new_height = int(width * aspect_ratio)
        elif height:
            aspect_ratio = image.width / image.height
            new_width = int(height * aspect_ratio)
            new_height = height
        else:
            return image
            
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)