import sys
import os
import time
import platform
import ctypes
import argparse
from PySide6.QtWidgets import QApplication

from campus_network.gui import MainWindow
from campus_network.core import startup

def is_admin():
    """检查是否有管理员权限"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def main():
    print("程序启动...")
    print(f"当前工作目录: {os.getcwd()}")  # 添加工作目录日志
    print(f"程序路径: {sys.executable}")   # 添加程序路径日志
    
    if not is_admin():
        print("请求管理员权限...")
        if platform.system().lower() == 'windows':
            if getattr(sys, 'frozen', False):
                exe_path = sys.executable
                args = " ".join(sys.argv[1:])
            else:
                exe_path = sys.executable.replace("pythonw.exe", "python.exe")
                script_path = os.path.abspath(sys.argv[0])
                args = f'"{script_path}" {" ".join(sys.argv[1:])}'
            
            print(f"重启程序: {exe_path} {args}")
            try:
                result = ctypes.windll.shell32.ShellExecuteW(
                    None, 
                    "runas", 
                    exe_path,
                    args,
                    os.getcwd(),  # 设置工作目录
                    1  # 正常显示窗口
                )
                print(f"ShellExecute 结果: {result}")
                if result <= 32:  # 如果返回值小于等于32，表示发生错误
                    print(f"启动失败，错误码: {result}")
            except Exception as e:
                print(f"启动失败: {str(e)}")
            return

    print("解析命令行参数...")
    parser = argparse.ArgumentParser(description='重庆工程职业技术学院校园网自动登录')
    parser.add_argument('--auto-login', action='store_true', help='自动登录模式')
    parser.add_argument('--startup', action='store_true', help='开机自启动模式')
    args = parser.parse_args()

    try:
        print("初始化 QApplication...")
        app = QApplication(sys.argv)
        print("创建主窗口...")
        window = MainWindow()
        print("显示主窗口...")
        window.show()
        
        if args.auto_login:
            print("等待系统初始化...")
            time.sleep(2)
            print("尝试自动登录...")
            window.handle_local_login()
            
            if args.startup and window.login_successful:
                print("开机自启动模式，准备退出...")
                time.sleep(1)
                sys.exit(0)
        
        print("进入主事件循环...")
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"程序运行出错: {str(e)}")
        print("错误详情:", sys.exc_info())
        time.sleep(5)
        sys.exit(1)

if __name__ == "__main__":
    main() 