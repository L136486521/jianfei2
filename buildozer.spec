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

# (str) Android NDK version to use
android.ndk_version = 21

# (str) Android SDK version to use
android.sdk_version = 31
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
requirements = python3,kivy==2.1.0,sqlite3,android,pyjnius

# 添加pandas相关依赖，但使用更兼容Android的版本和配置
android.gradle_dependencies = org.apache.commons:commons-math3:3.6.1

# 减少应用程序大小的设置
android.no_debug_bridge = True
android.arch = arm64-v8a,armeabi-v7a

# 优化打包
android.add_libs_armeabi_v7a = libandroid.so,liblog.so,libz.so
android.add_libs_arm64_v8a = libandroid.so,liblog.so,libz.so
android.add_libs_x86 = libandroid.so,liblog.so,libz.so
android.add_libs_x86_64 = libandroid.so,liblog.so,libz.so

# 构建配置
build_type = debug
p4a.branch = stable

# 日志级别
log_level = 2

# 解决Python线程问题
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,REQUEST_INSTALL_PACKAGES
android.orientation = portrait

# 内存优化
android.add_src = .
android.add_jar = .
android.add_aars = .

[buildozer]
log_level = 2
build_dir = .buildozer
bin_dir = ./bin
