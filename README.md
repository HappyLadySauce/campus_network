# 重庆工程职业技术学院校园网自动登录

## 项目简介

这是一个专门为重庆工程职业技术学院开发的校园网自动登录工具。它提供了图形化界面，支持开机自启动，网络状态监控，详细的日志记录等功能。

## 主要功能

- 🔐 校园网账号密码配置
- 🚀 一键快速登录
- 🔄 开机自动登录
- 📊 网络状态监控
- 📝 详细的网络请求日志
- ⚡ 登录失败自动重试
- �� 配置文件持久化

## 项目结构

```
CAMPUS_NETWORK/ # 项目根目录
├── campus_network/ # 主包目录
│ ├── core/ # 核心功能模块
│ │ ├── pycache/
│ │ ├── init.py
│ │ ├── login.py # 登录逻辑实现
│ │ └── startup.py # 开机自启动实现
│ ├── gui/ # 图形界面模块
│ │ ├── pycache/
│ │ ├── init.py
│ │ ├── main_window.py # 主窗口实现
│ │ └── styles.py # UI样式定义
│ └── utils/ # 工具模块
│ ├── init.py
│ └── logger.py # 日志工具
├── resources/ # 资源文件
│ └── icon.ico # 程序图标
├── .gitignore # Git忽略文件
├── app.manifest # 应用程序清单
├── config.ini # 配置文件
├── main.py # 程序入口
├── README.md # 项目说明文档
└── requirements.txt # 依赖包列表
```

## 技术栈

- Python 3.11
- PySide6 (Qt界面库)
- requests (网络请求)
- win32api (Windows系统API)
- configparser (配置文件处理)

## 安装使用

1. 克隆项目

```bash
bash
git clone https://github.com/your-username/campus_network.git
cd campus_network
```

2. 安装依赖

```bash
bash
pip install -r requirements.txt
```

3. 运行程序

```bash
bash
python main.py
```

## 使用说明

1. 首次运行
   - 输入学号和密码
   - 点击"保存设置"
   - 点击"登录"测试连接

2. 开机自启动
   - 勾选"开机自动登录"选项
   - 点击"保存设置"
   - 程序将在系统启动时自动运行并登录

3. 查看日志
   - 网络日志：显示详细的请求和响应数据
   - 程序日志：显示程序运行状态和错误信息

## 配置文件说明

配置文件 `config.ini` 包含以下设置：

```bash
ini
[Network]
url = http://172.17.10.100/eportal/InterFace.do
user_id =
password =
service = 教学区免费上网
auto_login = false
[Debug]
enable_packet_capture = false
```

## 注意事项

- 程序需要管理员权限才能设置开机自启动
- 请确保账号密码正确
- 如遇问题请查看日志

## 开发环境

- Windows 10/11
- Python 3.11
- Visual Studio Code
- Git

## 依赖包

主要依赖包包括：
- PySide6
- requests
- pywin32
- configparser

详细依赖列表请查看 `requirements.txt`

## 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 实现基本登录功能
- 支持开机自启动
- 添加日志记录功能

## 待实现功能

- [ ] 网络状态实时监控
- [ ] 系统托盘功能
- [ ] 自动更新功能
- [ ] 多账号管理
- [ ] 登录统计报告

## 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进项目。

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 作者

HappyLadySauce

- 博客：[https://www.happyladysauce.cn](https://www.happyladysauce.cn)
- CSDN：[https://blog.csdn.net/m0_73928695](https://blog.csdn.net/m0_73928695)
- 邮箱：admin@happyladysauce.cn
- GitHub：[https://github.com/happyladysauce](https://github.com/happyladysauce)

## 赞助支持

如果这个项目对你有帮助，欢迎赞助支持作者继续开发维护！

<details>
<summary>点击展开赞助方式</summary>

| 微信赞赏 | 支付宝赞赏 |
| :---: | :---: |
| <img src="https://lsky.happyladysauce.cn/i/2024/12/22/1/1-tenx.webp" alt="微信赞赏码" width="300"/> | <img src="https://lsky.happyladysauce.cn/i/2024/12/22/1/1-ali.webp" alt="支付宝赞赏码" width="300"/> |

</details>

感谢所有赞助支持的朋友！