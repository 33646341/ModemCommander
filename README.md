# ModemCommander - 光猫配置自动化工具

[![License: MIT](https://img.shields.io/github/license/33646341/ModemCommander)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)

适用于移动某些型号光猫的配置工具，可自动获取超级管理员密码，并支持启用DMZ等功能，方便进行网络调试或穿透操作。

⚠️ 请注意：使用此工具应遵守当地法律法规，仅用于合法授权的设备测试和管理。

---

## 🛠️ 功能特性

- 自动获取超级管理员账户密码（`aucTeleAccountPassword`）
- 自动开启 DMZ 并设置目标 IP 地址

## 🚀 使用方法

1. 克隆仓库：
   ```bash
   git clone https://github.com/33646341/ModemCommander.git
   cd ModemCommander
   ```

2. 安装依赖：
   ```bash
   # 使用uv（推荐）
   uv sync

   # 或传统方式
   pip install aiohttp telnetlib3 pyyaml pycryptodome loguru
   ```

3. 配置文件：修改 `config.yaml` 文件，把 `password` 填写为光猫背面的管理密码。

4. 执行脚本：
   ```bash
   # 使用uv（推荐）
   uv run main.py

   # 或传统方式
   python main.py
   ```

---

## 📌 支持的光猫型号

目前支持以下光猫型号：
- UNG433H-S

> 其他光猫型号可根据实际情况自行修改代码。

---

## ⚠️ 法律声明

本工具仅供学习交流和合法授权用途。未经授权不得对他人设备进行任何操作。使用本工具造成的后果由使用者自行承担。

---

## 📜 许可证

该项目采用 MIT License，请参阅 [LICENSE](LICENSE) 文件了解更多。
