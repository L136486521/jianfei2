[app]
# 应用标题和包名
title = 减肥体重记录器
package.name = weighttracker
package.domain = org.example

# 源文件配置
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,txt
source.exclude_dirs = tests, bin, venv, docs, .git, __pycache__
source.exclude_exts = spec,pyc,pyo

# 主程序入口
version = 1.0
main = main.py

# 要求配置 - 简化依赖，避免冲突
requirements = 
    python3,
    kivy==2.1.0,
    android,
    pyjnius,
    openssl,
    sqlite3,
    requests,
    pillow

# Android配置 - 使用兼容版本
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.gradle_dependencies = 'com.android.tools.build:gradle:7.2.0'
android.allow_backup = True
android.enable_androidx = True

# 权限配置
android.permissions = 
    INTERNET,
    WRITE_EXTERNAL_STORAGE,
    READ_EXTERNAL_STORAGE,
    ACCESS_NETWORK_STATE

# 构建工具版本
android.build_tools = 33.0.0

# 架构配置
android.arch = arm64-v8a,armeabi-v7a

# 应用配置
orientation = portrait
fullscreen = 0

# 图标和启动画面
icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/presplash.png

# 日志级别
log_level = 2

# 构建配置
build_type = debug
p4a.branch = master

# 优化设置
android.private_storage = True
android.accept_sdk_license = True
android.skip_compile_pyo = False

[buildozer]
# Buildozer配置
log_level = 2
warn_on_root = 1
build_dir = .buildozer
bin_dir = ./bin

# 允许覆盖默认的SDK路径
android.sdk_path = /usr/local/lib/android/sdk
android.ndk_path = /usr/local/lib/android/sdk/ndk/25b
