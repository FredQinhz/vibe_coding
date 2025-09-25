import os
import glob
from pathlib import Path
from src.core.image_processor import ImageProcessor

class FileHandler:
    """
    文件处理类，负责文件选择、批量导入和文件名处理
    """
    
    @staticmethod
    def get_supported_files(folder_path):
        """
        获取指定文件夹下所有支持的图像文件
        
        Args:
            folder_path (str): 文件夹路径
            
        Returns:
            list: 支持的图像文件路径列表
        """
        supported_files = []
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            for ext in ImageProcessor.SUPPORTED_INPUT_FORMATS:
                pattern = os.path.join(folder_path, f"*{ext}")
                supported_files.extend(glob.glob(pattern, recursive=False))
                # 处理大写扩展名
                pattern_upper = os.path.join(folder_path, f"*{ext.upper()}")
                supported_files.extend(glob.glob(pattern_upper, recursive=False))
        return supported_files
    
    @staticmethod
    def generate_output_filename(input_path, output_folder, prefix=None, suffix=None, output_format=None):
        """
        根据规则生成输出文件名
        
        Args:
            input_path (str): 输入文件路径
            output_folder (str): 输出文件夹
            prefix (str, optional): 自定义前缀
            suffix (str, optional): 自定义后缀
            output_format (str, optional): 输出格式
            
        Returns:
            str: 生成的输出文件路径
        """
        # 获取原文件名和扩展名
        file_name = os.path.basename(input_path)
        base_name, ext = os.path.splitext(file_name)
        
        # 构建新文件名
        new_base_name = base_name
        if prefix:
            new_base_name = prefix + new_base_name
        if suffix:
            new_base_name = new_base_name + suffix
        
        # 确定输出扩展名
        if output_format:
            if not output_format.startswith('.'):
                output_format = '.' + output_format
            new_ext = output_format
        else:
            new_ext = ext.lower()
            # 确保输出格式支持
            if new_ext not in ImageProcessor.SUPPORTED_OUTPUT_FORMATS:
                new_ext = '.png'  # 默认使用PNG
        
        # 构建完整输出路径
        output_filename = new_base_name + new_ext
        output_path = os.path.join(output_folder, output_filename)
        
        # 确保文件名唯一
        counter = 1
        base_output_path = output_path
        while os.path.exists(output_path):
            output_path = f"{os.path.splitext(base_output_path)[0]}_{counter}{new_ext}"
            counter += 1
        
        return output_path
    
    @staticmethod
    def validate_output_folder(input_folder, output_folder):
        """
        验证输出文件夹是否合法（不能与输入文件夹相同）
        
        Args:
            input_folder (str): 输入文件夹路径
            output_folder (str): 输出文件夹路径
            
        Returns:
            bool: 是否合法
        """
        if not input_folder or not output_folder:
            return True
            
        # 标准化路径
        input_folder = os.path.normpath(os.path.abspath(input_folder))
        output_folder = os.path.normpath(os.path.abspath(output_folder))
        
        return input_folder != output_folder
    
    @staticmethod
    def is_supported_image(file_path):
        """
        检查文件是否为支持的图像格式
        
        Args:
            file_path (str): 文件路径
            
        Returns:
            bool: 是否为支持的图像格式
        """
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return False
            
        file_ext = os.path.splitext(file_path)[1].lower()
        return file_ext in ImageProcessor.SUPPORTED_INPUT_FORMATS