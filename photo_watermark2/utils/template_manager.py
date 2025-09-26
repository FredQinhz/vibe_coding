import json
import os
import shutil
from model.watermark_settings import WatermarkSettings

class TemplateManager:
    """模板管理器，负责水印模板的保存和加载"""
    
    def __init__(self):
        """初始化模板管理器"""
        # 获取当前目录
        self.current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # 模板存储目录
        self.templates_dir = os.path.join(self.current_dir, "config", "templates")
        
        # 上次设置文件
        self.last_settings_file = os.path.join(self.current_dir, "config", "last_settings.json")
        
        # 确保模板目录存在
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        # 确保配置目录存在
        config_dir = os.path.join(self.current_dir, "config")
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        # 确保模板目录存在
        if not os.path.exists(self.templates_dir):
            os.makedirs(self.templates_dir)
    
    def save_template(self, template_name, watermark_settings):
        """保存水印模板"""
        try:
            # 将设置转换为字典
            settings_dict = self._settings_to_dict(watermark_settings)
            
            # 构建模板文件路径
            template_file = os.path.join(self.templates_dir, f"{template_name}.json")
            
            # 保存为JSON文件
            with open(template_file, "w", encoding="utf-8") as f:
                json.dump(settings_dict, f, ensure_ascii=False, indent=4)
            
            return True
        except Exception as e:
            print(f"保存模板时出错：{e}")
            return False
    
    def load_template(self, template_name):
        """加载水印模板"""
        try:
            # 构建模板文件路径
            template_file = os.path.join(self.templates_dir, f"{template_name}.json")
            
            # 检查文件是否存在
            if not os.path.exists(template_file):
                print(f"模板文件不存在：{template_file}")
                return None
            
            # 读取JSON文件
            with open(template_file, "r", encoding="utf-8") as f:
                settings_dict = json.load(f)
            
            # 转换为WatermarkSettings对象
            settings = self._dict_to_settings(settings_dict)
            
            return settings
        except Exception as e:
            print(f"加载模板时出错：{e}")
            return None
    
    def get_available_templates(self):
        """获取所有可用的模板列表"""
        try:
            templates = []
            
            # 检查模板目录是否存在
            if not os.path.exists(self.templates_dir):
                return templates
            
            # 遍历模板目录中的所有JSON文件
            for file_name in os.listdir(self.templates_dir):
                if file_name.endswith(".json"):
                    # 获取模板名称（不含扩展名）
                    template_name = os.path.splitext(file_name)[0]
                    templates.append(template_name)
            
            # 按名称排序
            templates.sort()
            
            return templates
        except Exception as e:
            print(f"获取模板列表时出错：{e}")
            return []
    
    def save_last_settings(self, watermark_settings):
        """保存上次的设置"""
        try:
            # 将设置转换为字典
            settings_dict = self._settings_to_dict(watermark_settings)
            
            # 保存为JSON文件
            with open(self.last_settings_file, "w", encoding="utf-8") as f:
                json.dump(settings_dict, f, ensure_ascii=False, indent=4)
            
            return True
        except Exception as e:
            print(f"保存上次设置时出错：{e}")
            return False
    
    def load_last_settings(self):
        """加载上次的设置"""
        try:
            # 检查文件是否存在
            if not os.path.exists(self.last_settings_file):
                return None
            
            # 读取JSON文件
            with open(self.last_settings_file, "r", encoding="utf-8") as f:
                settings_dict = json.load(f)
            
            # 转换为WatermarkSettings对象
            settings = self._dict_to_settings(settings_dict)
            
            return settings
        except Exception as e:
            print(f"加载上次设置时出错：{e}")
            return None
    
    def _settings_to_dict(self, settings):
        """将WatermarkSettings对象转换为字典"""
        return {
            "text": settings.text,
            "font": settings.font,
            "font_size": settings.font_size,
            "color": settings.color,
            "opacity": settings.opacity,
            "position": settings.position,
            "custom_position": settings.custom_position,
            "last_import_dir": getattr(settings, 'last_import_dir', ''),
            "last_export_dir": getattr(settings, 'last_export_dir', '')
        }
    
    def _dict_to_settings(self, settings_dict):
        """将字典转换为WatermarkSettings对象"""
        settings = WatermarkSettings()
        
        if "text" in settings_dict:
            settings.text = settings_dict["text"]
        
        if "font" in settings_dict:
            settings.font = settings_dict["font"]
        
        if "font_size" in settings_dict:
            settings.font_size = settings_dict["font_size"]
        
        if "color" in settings_dict:
            settings.color = settings_dict["color"]
        
        if "opacity" in settings_dict:
            settings.opacity = settings_dict["opacity"]
        
        if "position" in settings_dict:
            # 确保position是元组类型（JSON中会被转换为列表）
            position = settings_dict["position"]
            if isinstance(position, list):
                settings.position = tuple(position)
            else:
                settings.position = position
        
        if "custom_position" in settings_dict:
            settings.custom_position = settings_dict["custom_position"]
            
        if "last_import_dir" in settings_dict:
            settings.last_import_dir = settings_dict["last_import_dir"]
            
        if "last_export_dir" in settings_dict:
            settings.last_export_dir = settings_dict["last_export_dir"]
        
        return settings
    
    def delete_template(self, template_name):
        """删除指定的模板"""
        try:
            # 构建模板文件路径
            template_file = os.path.join(self.templates_dir, f"{template_name}.json")
            
            # 检查文件是否存在
            if os.path.exists(template_file):
                # 删除文件
                os.remove(template_file)
                return True
            
            return False
        except Exception as e:
            print(f"删除模板时出错：{e}")
            return False