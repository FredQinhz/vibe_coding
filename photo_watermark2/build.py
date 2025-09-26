import os
import sys
import shutil

def clean_build_folders():
    """清理之前的构建文件夹"""
    folders_to_clean = ['build', 'dist']
    for folder in folders_to_clean:
        if os.path.exists(folder):
            shutil.rmtree(folder)
    
    # 清理spec文件
    spec_file = 'photo_watermark.spec'
    if os.path.exists(spec_file):
        os.remove(spec_file)

def build_app():
    """使用PyInstaller构建应用"""
    # 确保我们在正确的目录中
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 清理之前的构建
    clean_build_folders()
    
    # 构建命令
    build_cmd = (
        f'pyinstaller --noconfirm --onefile --windowed '
        f'--add-data "config;config" '
        f'--name "照片水印工具" '
        f'--icon "config/icon.ico" '
        f'main.py'
    )
    
    # 如果没有图标文件，移除图标选项
    if not os.path.exists("config/icon.ico"):
        build_cmd = build_cmd.replace('--icon "config/icon.ico" ', '')
    
    # 执行构建
    os.system(build_cmd)
    
    print("应用打包完成！")
    print(f"可执行文件位于: {os.path.abspath('dist/照片水印工具.exe')}")

if __name__ == "__main__":
    build_app()