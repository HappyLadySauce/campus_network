import os
import sys
import time
import subprocess
import win32api
import win32con

def add_to_startup():
    """添加到注册表启动项"""
    try:
        # 获取当前脚本的完整路径
        startup_script = os.path.abspath(sys.argv[0])
        startup_path = os.path.dirname(startup_script)
        
        # 打开注册表键
        key = win32api.RegOpenKey(
            win32con.HKEY_LOCAL_MACHINE,
            r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run',
            0,
            win32con.KEY_ALL_ACCESS
        )
        
        # 设置启动命令，添加工作目录
        if getattr(sys, 'frozen', False):
            # 打包后的命令
            cmd = f'cmd /c "cd /d "{startup_path}" && "{startup_script}"'
        else:
            # 开发环境的命令
            python_path = os.path.join(startup_path, ".venv", "Scripts", "pythonw.exe")
            cmd = f'cmd /c "cd /d "{startup_path}" && "{python_path}" "{startup_script}"'
        
        # 写入注册表
        win32api.RegSetValueEx(
            key,
            "CQEVTCampusNetwork",
            0,
            win32con.REG_SZ,
            cmd
        )
        
        win32api.RegCloseKey(key)
        print(f"已添加到开机启动项: {cmd}")
        return True
        
    except Exception as e:
        print(f"添加启动项失败: {str(e)}")
        return False

def startup():
    print("启动中...")
    try:
        # 获取真实路径
        startup_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        # 切换工作目录
        os.chdir(startup_path)
        print(f"工作目录已设置为: {startup_path}")
        
        # 确保程序在启动项中
        add_to_startup()
        
        if getattr(sys, 'frozen', False):
            # 打包后的路径
            main_exe = os.path.join(startup_path, "重庆工程职业技术学院校园网自动登录.exe")
            cmd = [main_exe, "--auto-login", "--startup"]
        else:
            # 开发环境路径
            venv_path = os.path.join(startup_path, ".venv", "Scripts", "pythonw.exe")
            main_py = os.path.join(startup_path, "main.py")
            cmd = [venv_path, main_py, "--auto-login", "--startup"]
        
        print(f"启动命令: {' '.join(cmd)}")
        
        # 等待系统初始化
        time.sleep(5)
        
        # 启动主程序（设置工作目录）
        subprocess.Popen(cmd, cwd=startup_path)
        print("启动完成...")
        
    except Exception as e:
        print(f"自启动失败: {str(e)}")
        print("请手动启动程序...")
        time.sleep(3)
    
    time.sleep(1)

if __name__ == "__main__":
    startup() 