[app]
title = 减肥体重记录器
package.name = weighttracker
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,txt,csv,xlsx,json

# 排除不需要的文件
source.exclude_dirs = venv,.git,__pycache__,.idea
source.exclude_exts = spec,pyc,pyo

# 确保必要的文件被包含
source.include_patterns = weighttracker.kv,*.db,*.txt
main = main.py
version = 1.0

# Android 配置
android.api = 33
android.minapi = 21
android.targetapi = 33
android.sdk_version = 33
android.ndk_api = 21
android.allow_backup = True
android.enable_androidx = True  # 只保留这一行，删除重复的
android.build_tools_version = 33.0.0

# 权限配置
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE,WAKE_LOCK

# 应用图标
icon.filename = icon.png
presplash.filename = presplash.png

# 应用配置
orientation = portrait
fullscreen = 0

# 依赖配置 - 进一步简化
requirements = python3,kivy==2.1.0,android,pyjnius,sqlite3

# 优化设置
android.no_debug_bridge = True
android.archs = arm64-v8a,armeabi-v7a
android.add_src = .

# 构建配置
build_type = debug
p4a.branch = master

# 强制使用特定的gradle和插件版本
android.gradle_plugin = 7.2.0
android.gradle_version = 7.5

# 删除重复的 android.enable_androidx 和 android.use_androidx 行

# 添加这些配置来解决gradle问题
android.accept_sdk_license = True
android.skip_update = False

log_level = 2

[buildozer]
log_level = 2
build_dir = .buildozer
bin_dir = ./bin
