import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QTabWidget, QPushButton, QLabel, 
                              QLineEdit, QCheckBox, QMessageBox, QGroupBox,
                              QTextEdit, QSplitter, QFrame, QMenu, QTextBrowser,
                              QDialog)
from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import QFont, QTextCharFormat, QColor, QSyntaxHighlighter, QIcon, QPixmap
from datetime import datetime

from ..core.login import CampusNetworkLogin
from .styles import MODERN_STYLE, LOG_COLORS

class LogSignals(QObject):
    request_log = Signal(str)
    response_log = Signal(str)

class LogHighlighter(QSyntaxHighlighter):
    def __init__(self, parent, log_type):
        super().__init__(parent)
        self.log_type = log_type
        self.colors = LOG_COLORS[log_type]

    def highlightBlock(self, text):
        format = QTextCharFormat()
        
        # 高亮时间戳
        if "时间:" in text:
            format.setForeground(QColor(self.colors['timestamp']))
            self.setFormat(0, len(text), format)
            
        # 高亮方法/状态
        if self.log_type == 'request':
            if "Method:" in text:
                format.setForeground(QColor(self.colors['method']))
                self.setFormat(text.index("Method:"), len(text), format)
        else:
            if "Status Code:" in text:
                format.setForeground(QColor(self.colors['status']))
                self.setFormat(text.index("Status Code:"), len(text), format)
                
        # 高亮 URL
        if "URL:" in text:
            format.setForeground(QColor(self.colors['url']))
            self.setFormat(text.index("URL:"), len(text), format)
            
        # 高亮头部
        if "Headers:" in text:
            format.setForeground(QColor(self.colors['headers']))
            self.setFormat(text.index("Headers:"), len(text), format)
            
        # 高亮数据/响应体
        if "Data:" in text or "Body:" in text:
            format.setForeground(QColor(self.colors['data' if self.log_type == 'request' else 'body']))
            self.setFormat(text.index("Data:" if "Data:" in text else "Body:"), len(text), format)

class SponsorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("赞助支持")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # 添加说明文本
        desc_label = QLabel("如果这个项目对你有帮助，欢迎赞助支持作者继续开发维护！")
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setStyleSheet("font-size: 14px; color: #666; padding: 10px;")
        layout.addWidget(desc_label)
        
        # 赞赏码布局
        sponsor_layout = QHBoxLayout()
        sponsor_layout.setSpacing(20)
        
        # 微信赞赏码
        wechat_group = QGroupBox("微信赞赏")
        wechat_layout = QVBoxLayout()
        wechat_qr = QLabel()
        wechat_qr_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                     "resources", "wechat_sponsor.png")
        if os.path.exists(wechat_qr_path):
            wechat_pixmap = QPixmap(wechat_qr_path)
            wechat_pixmap = wechat_pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, 
                                                Qt.TransformationMode.SmoothTransformation)
            wechat_qr.setPixmap(wechat_pixmap)
            wechat_qr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            wechat_qr.setText("赞赏码加载失败")
        wechat_layout.addWidget(wechat_qr)
        wechat_group.setLayout(wechat_layout)
        sponsor_layout.addWidget(wechat_group)
        
        # 支付宝赞赏码
        alipay_group = QGroupBox("支付宝赞赏")
        alipay_layout = QVBoxLayout()
        alipay_qr = QLabel()
        alipay_qr_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                     "resources", "alipay_sponsor.png")
        if os.path.exists(alipay_qr_path):
            alipay_pixmap = QPixmap(alipay_qr_path)
            alipay_pixmap = alipay_pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, 
                                                Qt.TransformationMode.SmoothTransformation)
            alipay_qr.setPixmap(alipay_pixmap)
            alipay_qr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            alipay_qr.setText("赞赏码加载失败")
        alipay_layout.addWidget(alipay_qr)
        alipay_group.setLayout(alipay_layout)
        sponsor_layout.addWidget(alipay_group)
        
        # 设置赞助码组件的样式
        for group in [wechat_group, alipay_group]:
            group.setStyleSheet("""
                QGroupBox {
                    background-color: white;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    margin-top: 16px;
                    padding: 16px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 8px;
                    padding: 0 5px;
                    color: #666;
                    font-weight: bold;
                }
            """)
        
        layout.addLayout(sponsor_layout)
        
        # 添加感谢文本
        thanks_label = QLabel("感谢所有赞助支持的朋友！")
        thanks_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        thanks_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 14px;
                padding: 10px;
            }
        """)
        layout.addWidget(thanks_label)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.login_client = CampusNetworkLogin()
        self.log_signals = LogSignals()
        self.login_successful = False
        
        # 先连接信号
        self.log_signals.request_log.connect(self.update_request_log)
        self.log_signals.response_log.connect(self.update_response_log)
        
        # 设置日志回调
        self.login_client.set_log_callback(self.handle_log)
        
        # 初始化UI
        self.init_ui()
        
        # 设置样式
        self.setStyleSheet(MODERN_STYLE) 

    def init_ui(self):
        self.setWindowTitle('重庆工程职业技术学院校园网自动登录')
        self.setMinimumSize(1000, 600)
        
        # 设置程序图标
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../resources/icon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # 左侧：配置面板
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(20, 20, 20, 20)  # 添加边距
        left_layout.setSpacing(15)  # 增加组件间距
        
        # 标题
        title_label = QLabel("校园网登录配置")
        title_label.setStyleSheet("""
            font-size: 18px; 
            font-weight: bold; 
            color: #333; 
            padding: 10px 0;
        """)
        left_layout.addWidget(title_label)
        
        # 登录设置组
        settings_group = QGroupBox("登录设置")
        settings_layout = QVBoxLayout()
        settings_layout.setSpacing(20)  # 增加间距
        settings_layout.setContentsMargins(20, 30, 20, 20)  # 增加内边距
        
        # 学号输入
        id_widget = QWidget()
        id_layout = QHBoxLayout(id_widget)
        id_layout.setContentsMargins(0, 0, 0, 0)
        id_label = QLabel("学号:")
        id_label.setFixedWidth(40)
        self.user_id_input = QLineEdit()
        self.user_id_input.setMinimumHeight(30)
        self.user_id_input.setPlaceholderText("请输入学号")
        self.user_id_input.setText(self.login_client.config.get('Network', 'user_id'))
        self.user_id_input.setStyleSheet("""
            QLineEdit {
                color: #333333;
                background-color: white;
                padding: 5px 10px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #86b7fe;
                outline: none;
            }
        """)
        id_layout.addWidget(id_label)
        id_layout.addWidget(self.user_id_input)
        settings_layout.addWidget(id_widget)
        
        # 密码输入
        pwd_widget = QWidget()
        pwd_layout = QHBoxLayout(pwd_widget)
        pwd_layout.setContentsMargins(0, 0, 0, 0)
        pwd_label = QLabel("密码:")
        pwd_label.setFixedWidth(40)
        self.password_input = QLineEdit()
        self.password_input.setMinimumHeight(30)
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setText(self.login_client.config.get('Network', 'password'))
        self.password_input.setStyleSheet("""
            QLineEdit {
                color: #333333;
                background-color: white;
                padding: 5px 10px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #86b7fe;
                outline: none;
            }
        """)
        pwd_layout.addWidget(pwd_label)
        pwd_layout.addWidget(self.password_input)
        settings_layout.addWidget(pwd_widget)
        
        # 自动登录选项
        self.auto_login_cb = QCheckBox("开机自动登录")
        self.auto_login_cb.setChecked(self.login_client.config.getboolean('Network', 'auto_login'))
        self.auto_login_cb.setMinimumHeight(30)
        self.auto_login_cb.setStyleSheet("""
            QCheckBox {
                color: #333333;
                font-size: 14px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 24px;
                height: 24px;
                border: 2px solid #999;
                border-radius: 4px;
                background-color: white;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #999;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #0d6efd;
                background-color: #0d6efd;
            }
            QCheckBox::indicator:hover {
                border-color: #0d6efd;
            }
        """)
        
        # 添加状态改变的信号连接
        self.auto_login_cb.stateChanged.connect(self.on_auto_login_changed)
        
        settings_layout.addWidget(self.auto_login_cb)
        
        # 设置组样式
        settings_group.setLayout(settings_layout)
        settings_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                margin-top: 20px;
                font-size: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #666;
                font-weight: bold;
            }
        """)
        left_layout.addWidget(settings_group)
        
        # 操作按钮组
        buttons_group = QGroupBox("操作")
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(10)  # 增加按钮间距
        buttons_layout.setContentsMargins(15, 20, 15, 15)  # 增加内部边距
        
        login_btn = QPushButton('登录')
        login_btn.setMinimumHeight(40)
        login_btn.clicked.connect(self.handle_local_login)
        buttons_layout.addWidget(login_btn)
        
        save_btn = QPushButton('保存设置')
        save_btn.setMinimumHeight(40)
        save_btn.clicked.connect(self.save_settings)
        buttons_layout.addWidget(save_btn)
        
        buttons_group.setLayout(buttons_layout)
        buttons_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                margin-top: 16px;
                padding: 16px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 5px;
                color: #666;
                font-weight: bold;
            }
        """)
        left_layout.addWidget(buttons_group)
        
        # 添加底部弹性空间
        left_layout.addStretch(1)
        
        # 设置左侧面板的最小宽度
        left_widget.setMinimumWidth(300)
        main_layout.addWidget(left_widget, 1)
        
        # 右侧：日志显示
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)  # 移除外边距
        right_layout.setSpacing(0)  # 移除间距
        
        # 日志类型选择按钮组
        log_type_group = QWidget()
        log_type_layout = QHBoxLayout(log_type_group)
        log_type_layout.setSpacing(10)
        log_type_layout.setContentsMargins(0, 0, 0, 10)
        
        # 网络日志按钮
        self.network_log_btn = QPushButton("网络日志")
        self.network_log_btn.setCheckable(True)
        self.network_log_btn.setChecked(True)
        self.network_log_btn.clicked.connect(lambda: self.switch_view("network"))
        
        # 程序日志按钮
        self.program_log_btn = QPushButton("程序日志")
        self.program_log_btn.setCheckable(True)
        self.program_log_btn.clicked.connect(lambda: self.switch_view("program"))
        
        # 关于按钮
        self.about_btn = QPushButton("关于")
        self.about_btn.setCheckable(True)
        self.about_btn.clicked.connect(lambda: self.switch_view("about"))
        
        # 设置按钮样式
        for btn in [self.network_log_btn, self.program_log_btn, self.about_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    padding: 8px 16px;
                    border-radius: 4px;
                    color: #444;
                    font-weight: normal;
                }
                QPushButton:checked {
                    background-color: #0d6efd;
                    border-color: #0d6efd;
                    color: white;
                    font-weight: bold;
                }
                QPushButton:hover:!checked {
                    background-color: #e9ecef;
                }
            """)
        
        log_type_layout.addWidget(self.network_log_btn)
        log_type_layout.addWidget(self.program_log_btn)
        log_type_layout.addWidget(self.about_btn)
        log_type_layout.addStretch()
        right_layout.addWidget(log_type_group)
        
        # 创建内容容器
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # 网络日志视图
        self.network_log_widget = QWidget()
        network_log_layout = QVBoxLayout(self.network_log_widget)
        network_log_layout.setContentsMargins(0, 0, 0, 0)
        
        # 请求和响应日志分割器
        log_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # 请求日志
        request_group = QGroupBox("请求数据包")
        request_layout = QVBoxLayout()
        self.request_log = QTextEdit()
        self.request_log.setReadOnly(True)
        self.request_log.setFont(QFont("Consolas", 10))
        self.request_log.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #333;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        self.request_highlighter = LogHighlighter(self.request_log.document(), 'request')
        request_layout.addWidget(self.request_log)
        request_group.setLayout(request_layout)
        log_splitter.addWidget(request_group)
        
        # 响应日志
        response_group = QGroupBox("响应数据包")
        response_layout = QVBoxLayout()
        self.response_log = QTextEdit()
        self.response_log.setReadOnly(True)
        self.response_log.setFont(QFont("Consolas", 10))
        self.response_log.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #333;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        self.response_highlighter = LogHighlighter(self.response_log.document(), 'response')
        response_layout.addWidget(self.response_log)
        response_group.setLayout(response_layout)
        log_splitter.addWidget(response_group)
        
        network_log_layout.addWidget(log_splitter)
        
        content_layout.addWidget(self.network_log_widget)
        
        # 程序日志视图
        self.program_log_widget = QWidget()
        program_log_layout = QVBoxLayout(self.program_log_widget)
        program_log_layout.setContentsMargins(0, 0, 0, 0)
        
        program_group = QGroupBox("程序运行日志")
        program_inner_layout = QVBoxLayout()
        program_inner_layout.setContentsMargins(10, 15, 10, 10)  # 统一内边距
        self.program_log = QTextEdit()
        self.program_log.setReadOnly(True)
        self.program_log.setFont(QFont("Consolas", 10))
        self.program_log.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #333;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        program_inner_layout.addWidget(self.program_log)
        program_group.setLayout(program_inner_layout)
        program_log_layout.addWidget(program_group)
        
        content_layout.addWidget(self.program_log_widget)
        
        # 关于视图
        self.about_widget = QWidget()
        about_layout = QVBoxLayout(self.about_widget)
        about_layout.setContentsMargins(0, 0, 0, 0)  # 移除所有边距
        about_layout.setSpacing(0)  # 移除间距

        # 创建水平分割器
        about_splitter = QSplitter(Qt.Orientation.Horizontal)

        # 左侧：程序信息卡片
        about_program_group = QGroupBox("关于程序")
        about_program_layout = QVBoxLayout()
        about_program_layout.setContentsMargins(10, 10, 10, 10)  # 减小顶部边距

        about_text = QTextBrowser()
        about_text.setOpenExternalLinks(True)
        about_text.setMinimumHeight(600)  # 增加最小高度
        about_text.setStyleSheet("""
            QTextBrowser {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #333;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
        """)

        about_info = """
        <h3>重庆工程职业技术学院校园网自动登录</h3>
        <p><b>版本：</b> 1.0.0</p>
        <p><b>功能：</b></p>
        <ul>
            <li>自动登录校园网</li>
            <li>支持开机自启动</li>
            <li>网络状态监控</li>
            <li>详细的日志记录</li>
        </ul>
        <p><b>技术支持：</b></p>
        <ul>
            <li>Python 3.11</li>
            <li>PySide6</li>
            <li>Windows API</li>
        </ul>
        <p><b>使用说明：</b></p>
        <ol>
            <li>输入学号和密码</li>
            <li>点击"保存设置"</li>
            <li>点击"登录"测试连接</li>
            <li>可选择是否开机自启动</li>
        </ol>
        <p><b>注意事项：</b></p>
        <ul>
            <li>程序需要管理员权限</li>
            <li>请确保账号密码正确</li>
            <li>如遇问题请查看日志</li>
        </ul>
        """
        about_text.setHtml(about_info)
        about_program_layout.addWidget(about_text)
        about_program_group.setLayout(about_program_layout)

        # 右侧：作者信息卡片
        author_group = QGroupBox("作者信息")
        author_layout = QVBoxLayout()
        author_layout.setContentsMargins(10, 10, 10, 10)  # 减小顶部边距

        author_text = QTextBrowser()
        author_text.setOpenExternalLinks(True)
        author_text.setMinimumHeight(600)  # 增加最小高度
        author_text.setStyleSheet("""
            QTextBrowser {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #333;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
            a {
                color: #0d6efd;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
        """)

        author_info = """
        <h3>作者信息</h3>
        <p><b>作者：</b> HappyLadySauce</p>
        <p><b>个人网站：</b> <a href="https://www.happyladysauce.cn">博客网站</a></p>
        <p><b>CSDN博客：</b> <a href="https://blog.csdn.net/m0_73928695">CSDN主页</a></p>
        
        <p><b>联系方式：</b></p>
        <ul>
            <li>邮箱：13452552349@163.com</li>
            <li>微信号：A552089234</li>
            <li>QQ号：1552089234</li>
        </ul>

        <p><b>项目相关：</b></p>
        <ul>
            <li>开源协议：MIT</li>
            <li>项目地址：<a href="https://github.com/happyladysauce/campus_network">GitHub</a></li>
        </ul>
        """
        author_text.setHtml(author_info)
        author_layout.addWidget(author_text)

        # 添加赞赏按钮
        sponsor_btn = QPushButton("赞助支持")
        sponsor_btn.setStyleSheet("""
            QPushButton {
                background-color: #0d6efd;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-height: 36px;
            }
            QPushButton:hover {
                background-color: #0b5ed7;
            }
            QPushButton:pressed {
                background-color: #0a58ca;
            }
        """)
        sponsor_btn.clicked.connect(self.show_sponsor_dialog)
        author_layout.addWidget(sponsor_btn)

        author_group.setLayout(author_layout)

        # 添加两个组到分割器
        about_splitter.addWidget(about_program_group)
        about_splitter.addWidget(author_group)

        # 设置分割器的初始大小比例（60:40）
        about_splitter.setSizes([int(self.width() * 0.6), int(self.width() * 0.4)])

        # 分割器样式
        about_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #333;
                width: 2px;
                margin: 0px;
            }
            QSplitter::handle:hover {
                background-color: #666;
            }
            QSplitter::handle:pressed {
                background-color: #0d6efd;
            }
        """)

        # 将分割器添加到布局
        about_layout.addWidget(about_splitter)

        # 初始隐藏关于视图
        self.about_widget.hide()
        content_layout.addWidget(self.about_widget)
        
        # 添加内容容器到右侧布局
        right_layout.addWidget(content_widget)
        
        # 初始显示网络日志，隐藏其他视图
        self.program_log_widget.hide()
        self.about_widget.hide()
        
        main_layout.addWidget(right_widget, 2)
        
        # 添加日志右键菜单
        for log in [self.request_log, self.response_log, self.program_log]:
            log.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            log.customContextMenuRequested.connect(self.show_log_context_menu)
        
        # 状态栏
        self.statusBar().showMessage('就绪')

    def handle_log(self, log_type, message):
        """处理日志回调"""
        try:
            if log_type == 'request':
                self.log_signals.request_log.emit(message)
            elif log_type == 'response':
                self.log_signals.response_log.emit(message)
            else:
                # 直接更新程序日志
                self.update_program_log(message)
        except Exception as e:
            print(f"处理日志失败: {str(e)}")

    def update_request_log(self, message):
        """更新请求日志"""
        try:
            current_text = self.request_log.toPlainText()
            if current_text:
                self.request_log.setText(message + "\n" + current_text)
            else:
                self.request_log.setText(message)
            self.request_log.verticalScrollBar().setValue(0)
        except Exception as e:
            print(f"更新请求日志失败: {str(e)}")

    def update_response_log(self, message):
        """更新响应日志"""
        try:
            current_text = self.response_log.toPlainText()
            if current_text:
                self.response_log.setText(message + "\n" + current_text)
            else:
                self.response_log.setText(message)
            self.response_log.verticalScrollBar().setValue(0)
        except Exception as e:
            print(f"更新响应日志失败: {str(e)}")

    def handle_local_login(self):
        """处理本地登录"""
        try:
            success = self.login_client.login()
            self.login_successful = success
            
            if success:
                self.show_message("登录成功", "本机网络连接已建立！")
                self.statusBar().showMessage('登录成功')
            else:
                self.show_message("登录失败", "网络连接失败，请检查设置。", QMessageBox.Icon.Warning)
                self.statusBar().showMessage('登录失败')
                
        except Exception as e:
            self.show_message("错误", str(e), QMessageBox.Icon.Critical)
            self.statusBar().showMessage('发生错误')

    def save_settings(self):
        """保存设置"""
        try:
            # 保存账号密码
            self.login_client.config['Network']['user_id'] = self.user_id_input.text()
            self.login_client.config['Network']['password'] = self.password_input.text()
            
            # 获取自动登录状态
            auto_login = self.auto_login_cb.isChecked()
            self.login_client.config['Network']['auto_login'] = str(auto_login).lower()
            
            # 处理开机自启动
            try:
                import win32api
                import win32con
                
                key = win32api.RegOpenKey(
                    win32con.HKEY_LOCAL_MACHINE,
                    r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run',
                    0,
                    win32con.KEY_ALL_ACCESS
                )
                
                if auto_login:
                    # 设置开机自启动
                    if getattr(sys, 'frozen', False):
                        app_path = sys.executable
                        cmd = f'"{app_path}" --auto-login --startup'
                    else:
                        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                        python_path = os.path.join(current_dir, ".venv", "Scripts", "pythonw.exe")
                        main_py = os.path.join(current_dir, "main.py")
                        cmd = f'"{python_path}" "{main_py}" --auto-login --startup'
                    
                    try:
                        win32api.RegSetValueEx(
                            key,
                            "CQEVTCampusNetwork",
                            0,
                            win32con.REG_SZ,
                            cmd
                        )
                        self.update_program_log("已设置开机自启动")
                    except Exception as e:
                        self.update_program_log(f"设置开机自启动失败: {str(e)}")
                else:
                    # 移除开机自启动
                    try:
                        win32api.RegDeleteValue(key, "CQEVTCampusNetwork")
                        self.update_program_log("已移除开机自启动")
                    except WindowsError as e:
                        if e.winerror == 2:  # 找不到注册表项
                            self.update_program_log("开机自启动项不存在，无需移除")
                        else:
                            self.update_program_log(f"移除开机自启动失败: {str(e)}")
                
                win32api.RegCloseKey(key)
                
            except Exception as e:
                self.update_program_log(f"访问注册表失败: {str(e)}")
            
            # 保存配置文件
            config_path = self.login_client.get_config_path()
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                self.login_client.config.write(f)
            
            self.show_message("成功", "设置已保存！")
            self.update_program_log("设置已保存！")
            
        except Exception as e:
            self.show_message("错误", f"保存设置失败: {str(e)}", QMessageBox.Icon.Critical)
            self.update_program_log(f"保存设置失败: {str(e)}")

    def show_message(self, title, message, icon=QMessageBox.Icon.Information):
        """显示消息对话框"""
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(icon)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def switch_view(self, view_type):
        """切换视图"""
        self.network_log_btn.setChecked(view_type == "network")
        self.program_log_btn.setChecked(view_type == "program")
        self.about_btn.setChecked(view_type == "about")
        
        self.network_log_widget.hide()
        self.program_log_widget.hide()
        self.about_widget.hide()
        
        if view_type == "network":
            self.network_log_widget.show()
        elif view_type == "program":
            self.program_log_widget.show()
        else:  # about
            self.about_widget.show()

    def update_program_log(self, message):
        """更新程序日志"""
        try:
            if not isinstance(message, str):
                message = str(message)
            
            current_text = self.program_log.toPlainText()
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            formatted_message = f"[{timestamp}] {message.strip()}"
            
            if current_text:
                self.program_log.setText(formatted_message + "\n" + current_text)
            else:
                self.program_log.setText(formatted_message)
            self.program_log.verticalScrollBar().setValue(0)
        except Exception as e:
            print(f"更新程序日志失败: {str(e)}")

    def show_log_context_menu(self, pos):
        """显示日志右键菜单"""
        menu = QMenu()
        copy_action = menu.addAction("复制")
        copy_action.triggered.connect(self.copy_log_text)
        clear_action = menu.addAction("清空")
        clear_action.triggered.connect(self.clear_log_text)
        
        # 获取触发右键菜单的文本框
        sender = self.sender()
        menu.exec(sender.mapToGlobal(pos))

    def copy_log_text(self):
        """复制日志文本"""
        sender = self.sender()
        if isinstance(sender, QMenu):
            text_edit = sender.parent()
            if text_edit.textCursor().hasSelection():
                text = text_edit.textCursor().selectedText()
            else:
                text = text_edit.toPlainText()
            QApplication.clipboard().setText(text)

    def clear_log_text(self):
        """清空日志文本"""
        sender = self.sender()
        if isinstance(sender, QMenu):
            text_edit = sender.parent()
            text_edit.clear()

    def on_auto_login_changed(self, state):
        """处理自动登录状态改变"""
        print(f"自动登录状态改变: {state == Qt.CheckState.Checked.value}")
        # 立即更新配置（可选）
        self.login_client.config['Network']['auto_login'] = str(state == Qt.CheckState.Checked.value).lower() 

    def show_sponsor_dialog(self):
        dialog = SponsorDialog(self)
        dialog.exec() 