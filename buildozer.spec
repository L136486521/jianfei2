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
android.api = 31
android.minapi = 21
android.targetapi = 31
android.ndk_version = 21.4.7075529
android.sdk_version = 31
android.ndk_api = 21
android.allow_backup = True
android.gradle_dependencies = 'com.android.support:support-v4:28.0.0', 'org.apache.commons:commons-math3:3.6.1'
android.build_tools_version = 31.0.0

# 权限配置
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE,WAKE_LOCK

# 应用图标
icon.filename = icon.png
presplash.filename = presplash.png

# 应用配置
orientation = portrait
fullscreen = 0

# 依赖配置
requirements = python3,kivy==2.1.0,sqlite3,android,pyjnius,cython==0.29.33

# 优化设置
android.no_debug_bridge = True
android.archs = arm64-v8a,armeabi-v7a
android.add_libs_armeabi_v7a = libandroid.so,liblog.so,libz.so
android.add_libs_arm64_v8a = libandroid.so,liblog.so,libz.so
android.add_src = .

# 构建配置
build_type = debug
p4a.branch = stable
log_level = 2

[buildozer]
log_level = 2
build_dir = .buildozer
bin_dir = ./bin
