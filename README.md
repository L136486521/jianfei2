# 减肥体重记录器 (Weight Tracker)

一个使用Kivy框架开发的跨平台体重记录应用，支持Windows、macOS、Linux和Android平台，专为减肥人士设计。

## 项目简介

本应用旨在帮助用户记录体重变化、管理减肥日记，并通过图表直观展示减肥进展。适合想要健康减肥并追踪自己进步的用户。

## 功能特点

### 📊 体重记录
- 早晚记录：支持早晨和晚上分别记录体重
- 自动更新：记录后自动更新统计数据和图表
- 历史查看：查看最近7天的体重记录

### 📈 数据统计
- 初始体重：记录您开始减肥时的体重
- 最轻体重：显示减肥期间的最低体重
- 最重体重：显示减肥期间的最高体重
- 平均体重：计算所有记录的平均值
- 体重差值：显示体重波动范围

### 📉 趋势图表
- 多种视图：可选择早晨体重、晚上体重或全部体重
- 时间范围：支持查看最近7天、30天或全部数据
- 交互操作：支持缩放和滚动查看详细数据
- 直观展示：通过折线图清晰展示体重变化趋势

### 📝 减肥日记
- 饮食记录：记录每日饮食内容
- 心得分享：记录减肥感受和心得
- 自动保存：当天日记可随时修改和保存
- 历史回顾：查看最近10天的日记记录

### 💾 数据管理
- 数据导出：将数据导出为Excel文件，包含体重记录和减肥日记两个工作表
- 数据导入：从Excel文件导入数据
- 文件位置：查看导出文件的具体位置
- 数据备份：支持数据备份和恢复功能

## 技术栈

- Python 3.8+
- Kivy 2.1.0
- SQLite (本地数据存储)
- Pandas 1.5.3 (数据处理)
- Openpyxl 3.0.10 (Excel文件处理)
- Buildozer (Android打包)

## 安装说明

### 开发环境设置

1. 克隆仓库：
   ```bash
   git clone <repository-url>
   cd jianfei_phone
   ```

2. 创建虚拟环境：
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate  # Windows
   ```

3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

### 运行应用

```bash
python main.py
```

### 构建Android APK

使用Buildozer构建：

```bash
# 安装Buildozer
sudo pip install buildozer

# 初始化Buildozer（如果没有buildozer.spec文件）
buildozer init

# 构建APK
buildozer android debug
```

构建完成后，APK文件将位于`bin/`目录下。

## GitHub Actions

本项目配置了GitHub Actions工作流，当代码推送到main/master分支时，会自动构建Android APK。

工作流配置位于：`.github/workflows/build.yml`

## 贡献指南

欢迎提交Issue和Pull Request！

## 许可证

MIT
