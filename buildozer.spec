[app]
title = 减肥体重记录器
package.name = weighttracker
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
main = main.py
version = 1.0

# Android 配置
android.api = 34  # 更新到最新API
android.minapi = 24
android.targetapi = 34
android.ndk = 25b
android.sdk = 34  # 更新SDK版本
android.ndk_api = 24
android.allow_backup = True
android.gradle_dependencies = 'com.google.android.material:material:1.12.0'  # 添加Material Design支持

# 权限配置（新增必要权限）
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE,WAKE_LOCK,QUERY_ALL_PACKAGES

# 应用图标（确保图片尺寸正确）
icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/presplash.png

orientation = portrait
fullscreen = 0

# 依赖配置（优化版本）
requirements = python3,kivy==2.1.0,sqlite3,openssl,requests,urllib3,chardet,idna,certifi,setuptools,pandas==2.2.2,numpy==1.26.4,openpyxl==3.1.2,android

# 构建配置
build_type = release  # 生产模式
p4a.branch = stable

# 日志级别
log_level = 2

[buildozer]
log_level = 2
build_dir = .buildozer
bin_dir = ./bin
