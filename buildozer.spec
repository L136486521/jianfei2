[app]
title = 减肥体重记录器
package.name = weighttracker
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
main = main.py
version = 1.0

# Android 配置
android.api = 30
android.minapi = 21
android.targetapi = 30
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# 应用图标
icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/presplash.png

orientation = portrait
fullscreen = 0

# 修正的依赖配置
requirements = python3,kivy==2.1.0,kivymd==1.1.1,pandas,openpyxl,numpy,android,sqlite3,datetime,json,platform,os

build_type = debug
