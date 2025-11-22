[app]
title = 减肥体重记录器
package.name = weighttracker
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
main = main.py
version = 1.0

# Android 配置
android.api = 34
android.minapi = 21
android.targetapi = 33
android.ndk = 25b
android.sdk = 33
android.ndk_api = 21
android.allow_backup = True
android.gradle_dependencies = 'com.android.support:support-v4:28.0.0'
android.build_tools_version = 34.0.0

# 权限配置
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE,WAKE_LOCK

# 应用图标
icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/presplash.png

orientation = portrait
fullscreen = 0

# 依赖配置
requirements = python3,kivy==2.1.0,openssl,requests,urllib3,certifi,setuptools,pandas==1.5.3,numpy==1.24.3,openpyxl==3.0.10,android

# 构建配置
build_type = debug
p4a.branch = stable

# 日志级别
log_level = 2

[buildozer]
log_level = 2
build_dir = .buildozer
bin_dir = ./bin
