import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    """程序主入口"""
    app = QApplication(sys.argv)
    
    # 设置中文显示
    font = app.font()
    font.setFamily("SimHei")
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()