import requests
import time
import json
import configparser
import os
import subprocess
import platform
from typing import Dict, Optional
import socket
import uuid
import logging
from datetime import datetime
import winreg
import sys
import shutil
import ctypes

class CampusNetworkLogin:
    """
    校园网络自动登录客户端
    功能：
    1. 自动读取配置文件
    2. 自动检测网络状态
    3. 执行校园网络登录
    4. 登录失败自动重试
    """
    def __init__(self):
        self.is_windows = platform.system().lower() == 'windows'
        self.log_callback = None  # 初始化日志回调
        # 初始化配置和基本参数
        self.config = self._load_config()
        self.url = self.config.get('Network', 'url')
        self.max_retries = 3  # 最大重试次数
        # 添加自定义IP支持
        self.custom_ip = self.config.get('Network', 'custom_ip', fallback=None)
        # 添加抓包开关
        self.enable_packet_capture = self.config.getboolean('Debug', 'enable_packet_capture', fallback=False)
        self._setup_logging()
        
    def _setup_logging(self):
        """设置日志记录，使用UTF-8编码"""
        if not self.enable_packet_capture:
            self.logger = logging.getLogger('NetworkLogger')
            self.logger.setLevel(logging.DEBUG)
            return

        # 创建logs目录
        logs_dir = 'logs'
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
            
        log_filename = os.path.join(logs_dir, f'network_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        handler = logging.FileHandler(log_filename, encoding='utf-8')
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        self.logger = logging.getLogger('NetworkLogger')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(handler)

    def _log_request(self, method: str, url: str, headers: Dict, data: Optional[Dict] = None):
        """记录请求数据包"""
        try:
            log_message = [
                "\n" + "="*50,
                f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"Method: {method}",
                f"URL: {url}",
                "Headers:"
            ]
            
            for key, value in headers.items():
                log_message.append(f"  {key}: {value}")
            
            if data:
                log_message.append("Data:")
                for key, value in data.items():
                    # 对敏感信息进行脱敏
                    if key in ['password', 'userId']:
                        value = '*' * len(str(value))
                    log_message.append(f"  {key}: {value}")
            
            message = '\n'.join(log_message)
            if hasattr(self, 'log_callback'):
                self.log_callback('request', message)
        except Exception as e:
            print(f"记录请求日志失败: {str(e)}")

    def _log_response(self, response):
        """记录响应数据包"""
        try:
            log_message = [
                "\n" + "="*50,
                f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"Status Code: {response.status_code}",
                "Headers:"
            ]
            
            for key, value in response.headers.items():
                log_message.append(f"  {key}: {value}")
            
            try:
                # 尝试格式化JSON响应
                body = response.json()
                # 修复中文编码
                formatted_body = json.dumps(body, ensure_ascii=False, indent=2)
                log_message.append("Body (JSON):")
                log_message.append(formatted_body)
            except json.JSONDecodeError:
                log_message.append("Body:")
                log_message.append(response.text)
            
            message = '\n'.join(log_message)
            if hasattr(self, 'log_callback'):
                self.log_callback('response', message)
        except Exception as e:
            print(f"记录响应日志失败: {str(e)}")

    def _load_config(self) -> configparser.ConfigParser:
        """加载配置文件"""
        config = configparser.ConfigParser()
        config_path = self.get_config_path()
        
        self._log(f"尝试加载配置文件: {config_path}")
        self.is_first_run = not os.path.exists(config_path)
        
        if self.is_first_run:
            self._log("首次运行，创建默认配置...")
            # 创建默认配置
            config['Network'] = {
                'url': 'http://172.17.10.100/eportal/InterFace.do',
                'user_id': '',
                'password': '',
                'service': '教学区免费上网',
                'auto_login': 'false'
            }
            config['Debug'] = {
                'enable_packet_capture': 'false'
            }
            
            try:
                # 保存默认配置
                with open(config_path, 'w', encoding='utf-8') as f:
                    config.write(f)
                self._log(f"配置文件已创建: {config_path}")
            except Exception as e:
                self._log(f"创建配置文件失败: {str(e)}")
        else:
            try:
                # 读取现有配置
                config.read(config_path, encoding='utf-8')
                self._log("配置文件加载成功")
            except Exception as e:
                self._log(f"读取配置文件失败: {str(e)}")
                # 使用默认配置
                config['Network'] = {
                    'url': 'http://172.17.10.100/eportal/InterFace.do',
                    'user_id': '',
                    'password': '',
                    'service': '教学区免费上网',
                    'auto_login': 'false'
                }
                config['Debug'] = {
                    'enable_packet_capture': 'false'
                }
        
        return config

    def _get_login_data(self) -> Dict:
        """准备登录数据"""
        return {
            'method': 'login',
            'userId': self.config.get('Network', 'user_id'),
            'password': self.config.get('Network', 'password'),
            'service': self.config.get('Network', 'service'),
            'queryString': self._get_query_string(),
            'operatorPwd': '',
            'operatorUserId': '',
            'validcode': '',
            'passwordEncrypt': 'true'
        }

    def _get_query_string(self) -> str:
        """获取查询字符串"""
        if hasattr(self, 'custom_ip') and hasattr(self, 'custom_mac'):
            # 使用自定义设备信息
            ip = self.custom_ip
            mac = self.custom_mac
        else:
            # 使用本机信息
            try:
                ip = socket.gethostbyname(socket.gethostname())
            except:
                ip = "172.17.0.0"
            mac = self._get_real_mac()
        
        query = (
            f'wlanuserip%3D{ip}'
            '%26wlanacname%3DNAS'
            '%26ssid%3DRuijie'
            '%26nasip%3D172.17.10.10'
            f'%26mac%3D{mac}'
            '%26t%3Dwireless-v2-plain'
            '%26url%3Dhttp%3A%252F%252Fwww.baidu.com%252F'
        )
        return query

    def _get_real_mac(self) -> str:
        """获取真实的MAC地址"""
        try:
            mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
            return mac.upper()
        except:
            return "000000000000"

    def _get_headers(self) -> Dict:
        """获取请求头"""
        return {
            'Host': '172.17.10.100',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.100 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }

    def _log(self, message):
        """统一的日志处理函数"""
        print(message)  # 保留控制台输出
        if self.log_callback:
            self.log_callback('program', message)

    def login(self) -> bool:
        """执行登录操作"""
        # 检查账号密码是否已设置
        if not self.config.get('Network', 'user_id') or not self.config.get('Network', 'password'):
            self._log("错误：请先设置账号和密码")
            return False

        # 清除可能存在的自定义设备信息
        if hasattr(self, 'custom_ip'):
            delattr(self, 'custom_ip')
        if hasattr(self, 'custom_mac'):
            delattr(self, 'custom_mac')
        
        for attempt in range(self.max_retries):
            try:
                headers = self._get_headers()
                data = self._get_login_data()
                
                # 记录请求数据包
                self._log_request('POST', self.url, headers, data)
                
                # 发送登录请求
                response = requests.post(
                    self.url,
                    headers=headers,
                    data=data,
                    timeout=5
                )
                response.encoding = 'utf-8'
                
                # 记录响应数据包
                self._log_response(response)
                
                self._log(f"尝试第 {attempt + 1} 次登录: {response.text}")
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('result') == 'success':
                        self._log("登录成功！")
                        return True
                    else:
                        self._log(f"登录失败: {result.get('message', '未知错误')}")
                
            except requests.exceptions.RequestException as e:
                error_msg = f"第 {attempt + 1} 次尝试失败: {str(e)}"
                self._log(error_msg)
                self.logger.error(error_msg)
            except json.JSONDecodeError:
                error_msg = f"第 {attempt + 1} 次尝试失败: 响应格式无效"
                self._log(error_msg)
                self.logger.error(error_msg)
                
            if attempt < self.max_retries - 1:
                self._log(f"等待 {attempt + 1} 秒后重试...")
                time.sleep(attempt + 1)
        
        return False

    def _check_internet_connection(self) -> bool:
        """检查网络连接状态"""
        try:
            headers = self._get_headers()
            data = self._get_login_data()
            
            # 记录请求数据包
            self._log_request('POST', self.url, headers, data)
            
            response = requests.post(
                self.url,
                headers=headers,
                data=data,
                timeout=3
            )
            
            # 记录响应数据包
            self._log_response(response)
            
            if response.status_code == 200:
                result = response.json()
                if "已经在线" in result.get('message', ''):
                    print("检测到已经登录")
                    return True
                print(f"检测到需要登录: {result.get('message', '未知状态')}")
                return False
            
        except requests.exceptions.RequestException as e:
            error_msg = f"网络请求失败: {str(e)}"
            print(error_msg)
            self.logger.error(error_msg)
            return False
        except json.JSONDecodeError:
            error_msg = "响应格式无效"
            print(error_msg)
            self.logger.error(error_msg)
            return False

    def ensure_connection(self) -> bool:
        """确保网络连接"""
        if self._check_internet_connection():
            return True
        return self.login()

    def set_log_callback(self, callback):
        """设置日志回调函数"""
        self.log_callback = callback

    def setup_auto_start(self):
        """设置开机自动启动"""
        try:
            if self.is_windows:
                import win32api
                import win32con
                
                # 获取程序路径
                if getattr(sys, 'frozen', False):
                    app_path = sys.executable
                    # 构建启动命令
                    cmd = f'"{app_path}" --auto-login --startup'
                else:
                    current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                    python_path = os.path.join(current_dir, ".venv", "Scripts", "pythonw.exe")
                    main_py = os.path.join(current_dir, "main.py")
                    # 构建启动命令
                    cmd = f'"{python_path}" "{main_py}" --auto-login --startup'
                
                # 打开注册表
                key = win32api.RegOpenKey(
                    win32con.HKEY_LOCAL_MACHINE,
                    r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run',
                    0,
                    win32con.KEY_ALL_ACCESS
                )
                
                # 写入注册表
                win32api.RegSetValueEx(
                    key,
                    "CQEVTCampusNetwork",
                    0,
                    win32con.REG_SZ,
                    cmd
                )
                
                win32api.RegCloseKey(key)
                self._log(f"已设置开机自启动: {cmd}")
                return True
                
        except Exception as e:
            self._log(f"设置自启动失败: {str(e)}")
            return False

    def remove_auto_start(self):
        """移除开机自动启动"""
        try:
            if self.is_windows:
                import win32api
                import win32con
                
                key = win32api.RegOpenKey(
                    win32con.HKEY_LOCAL_MACHINE,
                    r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run',
                    0,
                    win32con.KEY_ALL_ACCESS
                )
                
                try:
                    win32api.RegDeleteValue(key, "CQEVTCampusNetwork")
                    self._log("已移除开机自启动")
                except:
                    pass
                finally:
                    win32api.RegCloseKey(key)
                
                return True
                
        except Exception as e:
            self._log(f"移除自启动失败: {str(e)}")
            return False

    @staticmethod
    def get_config_path():
        """获取配置文件路径"""
        if getattr(sys, 'frozen', False):
            # 打包后的路径
            base_path = os.path.dirname(sys.executable)
        else:
            # 开发环境路径
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        config_path = os.path.join(base_path, 'config.ini')
        print(f"配置文件路径: {config_path}")  # 添加日志
        return config_path 