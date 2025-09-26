class WatermarkSettings:
    """水印设置类，存储水印的各种参数"""
    
    def __init__(self):
        """初始化水印设置"""
        # 文本内容
        self.text = "水印"
        
        # 字体设置
        self.font = "SimHei"
        self.font_size = 24
        
        # 颜色设置 (R, G, B)
        self.color = (255, 0, 0)  # 默认红色
        
        # 透明度 (0.0-1.0)
        self.opacity = 0.5  # 默认50%透明度
        
        # 预设位置 (row, col)，对应九宫格位置
        # row: 0(上), 1(中), 2(下)
        # col: 0(左), 1(中), 2(右)
        self.position = (2, 2)  # 默认右下角
        
        # 自定义位置 (x_ratio, y_ratio)，相对于图片尺寸的比例
        # 如果不为None，则优先使用自定义位置
        self.custom_position = None
    
    def copy(self):
        """创建当前设置的副本"""
        copy_settings = WatermarkSettings()
        copy_settings.text = self.text
        copy_settings.font = self.font
        copy_settings.font_size = self.font_size
        copy_settings.color = self.color
        copy_settings.opacity = self.opacity
        copy_settings.position = self.position
        copy_settings.custom_position = self.custom_position
        return copy_settings
    
    def __str__(self):
        """返回设置的字符串表示"""
        return (
            f"WatermarkSettings(text='{self.text}', font='{self.font}', font_size={self.font_size}, "
            f"color={self.color}, opacity={self.opacity:.2f}, position={self.position}, "
            f"custom_position={self.custom_position})"
        )
    
    def is_valid(self):
        """验证设置是否有效"""
        # 检查文本是否为空
        if not self.text or not self.text.strip():
            return False
        
        # 检查透明度是否在有效范围内
        if not (0.0 <= self.opacity <= 1.0):
            return False
        
        # 检查字体大小是否为正数
        if self.font_size <= 0:
            return False
        
        # 检查颜色值是否在有效范围内
        for c in self.color:
            if not (0 <= c <= 255):
                return False
        
        # 检查预设位置是否有效
        if self.position is not None:
            row, col = self.position
            if not (0 <= row <= 2 and 0 <= col <= 2):
                return False
        
        # 检查自定义位置是否有效
        if self.custom_position is not None:
            x_ratio, y_ratio = self.custom_position
            if not (0.0 <= x_ratio <= 1.0 and 0.0 <= y_ratio <= 1.0):
                return False
        
        return True
    
    def reset_position(self):
        """重置位置设置，清除自定义位置"""
        self.custom_position = None
        self.position = (2, 2)  # 重置为默认右下角位置