from PIL import Image
import io
import base64

class ImageUtils:
    """
    图像工具类，提供图像相关的辅助功能
    """
    
    @staticmethod
    def create_thumbnail(image, max_size=(100, 100)):
        """
        创建图像缩略图
        
        Args:
            image (PIL.Image): 原始图像
            max_size (tuple): 缩略图最大尺寸 (宽, 高)
            
        Returns:
            PIL.Image: 缩略图图像
        """
        # 保持原图比例创建缩略图
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        return image
    
    @staticmethod
    def image_to_base64(image, format='PNG'):
        """
        将PIL图像转换为base64字符串
        
        Args:
            image (PIL.Image): 图像对象
            format (str): 图像格式
            
        Returns:
            str: base64编码的图像字符串
        """
        buffered = io.BytesIO()
        image.save(buffered, format=format)
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        return img_str
    
    @staticmethod
    def base64_to_image(base64_str):
        """
        将base64字符串转换为PIL图像
        
        Args:
            base64_str (str): base64编码的图像字符串
            
        Returns:
            PIL.Image: 图像对象
        """
        img_data = base64.b64decode(base64_str)
        return Image.open(io.BytesIO(img_data))
    
    @staticmethod
    def ensure_rgb(image):
        """
        确保图像为RGB模式
        
        Args:
            image (PIL.Image): 图像对象
            
        Returns:
            PIL.Image: RGB模式的图像
        """
        if image.mode != 'RGB':
            return image.convert('RGB')
        return image
    
    @staticmethod
    def ensure_rgba(image):
        """
        确保图像为RGBA模式（支持透明度）
        
        Args:
            image (PIL.Image): 图像对象
            
        Returns:
            PIL.Image: RGBA模式的图像
        """
        if image.mode != 'RGBA':
            return image.convert('RGBA')
        return image