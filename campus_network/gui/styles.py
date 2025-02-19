MODERN_STYLE = """
QMainWindow {
    background-color: #f0f0f0;
}

QTabWidget::pane {
    border: 1px solid #cccccc;
    background: white;
    border-radius: 4px;
}

QTabWidget::tab-bar {
    left: 5px;
}

QTabBar::tab {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #f6f7fa, stop: 1 #dadbde);
    border: 1px solid #C4C4C3;
    border-bottom-color: #C2C7CB;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    min-width: 8ex;
    padding: 8px 12px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background: #fff;
    border-color: #9B9B9B;
    border-bottom-color: #fff;
}

QTabBar::tab:!selected {
    margin-top: 2px;
}

QPushButton {
    background-color: #0d6efd;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #0b5ed7;
}

QPushButton:pressed {
    background-color: #0a58ca;
}

QLineEdit {
    padding: 8px 12px;
    border: 1px solid #ced4da;
    border-radius: 4px;
    background-color: white;
    font-size: 14px;
    min-height: 20px;
}

QLineEdit:focus {
    border-color: #86b7fe;
    box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25);
}

QGroupBox {
    background-color: white;
    border: 1px solid #e0e0e0;
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
    font-size: 14px;
}

QTextEdit {
    background-color: #1e1e1e;
    color: #d4d4d4;
    border: 1px solid #333;
    border-radius: 4px;
    font-family: "Consolas", "Courier New", monospace;
    padding: 8px;
    selection-background-color: #264f78;
    selection-color: #ffffff;
}

QCheckBox {
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
}

QCheckBox::indicator:unchecked {
    border: 2px solid #999;
    border-radius: 3px;
    background-color: white;
}

QCheckBox::indicator:checked {
    border: 2px solid #0d6efd;
    border-radius: 3px;
    background-color: #0d6efd;
}

QStatusBar {
    background-color: #f8f9fa;
    color: #666;
}

QLabel {
    color: #333;
    font-size: 14px;
    padding: 4px;
}
"""

# 日志颜色样式
LOG_COLORS = {
    'request': {
        'timestamp': '#87CEEB',  # 天蓝色
        'method': '#98FB98',     # 浅绿色
        'url': '#DDA0DD',        # 梅红色
        'headers': '#F0E68C',    # 卡其色
        'data': '#FFB6C1'        # 浅粉色
    },
    'response': {
        'timestamp': '#87CEEB',  # 天蓝色
        'status': '#00FF00',     # 亮绿色
        'headers': '#F0E68C',    # 卡其色
        'body': '#FFA07A'        # 浅鲑鱼色
    }
} 