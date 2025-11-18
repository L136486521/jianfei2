[app]

# 应用标题 - 显示在手机上的名称
title = 减肥体重记录器

# 应用包名 - 必须是唯一的，通常使用反域名格式
package.name = weighttracker

# 应用域名 - 同样使用反域名格式
package.domain = org.example

# 源代码目录
source.dir = .

# 应用入口文件
source.include_exts = py,png,jpg,kv,atlas

# 主程序文件
main = main.py

# 应用版本 (1.0, 1.1, 1.2...)
version = 1.0

# 应用要求的Android API级别
android.api = 30

# 应用支持的最低Android版本
android.minapi = 21

# 应用支持的目标Android版本
android.targetapi = 30

# 应用权限
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Android应用图标 (不同尺寸)
icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/presplash.png

# 预设方向 (portrait|landscape|all)
orientation = portrait

# Kivy启动器配置
fullscreen = 0

# 要求的Python模块
requirements = python3,kivy,sqlite3,datetime,json,platform,os,pandas,openpyxl

# 在构建时排除的模块
presplash.filename = %(source.dir)s/presplash.png

# 构建模式 (debug|release)
# 如果是release模式，需要设置下面的release配置
build_type = debug

# 当build_type设置为release时，需要配置以下选项
# (buildozer android release命令)
#
# package.release.name = .keystore
# package.release.password = password
# package.release.alias = alias
# package.release.alias_password = alias_password

[buildozer]

# 日志级别 (0=error, 1=warning, 2=info, 3=debug)
log_level = 2

# 构建目录
build_dir = .buildozer

# 构建输出目录
bin_dir = ./bin

# 在构建前运行的自定义命令
# pre_build_cmd = 

# 在构建后运行的自定义命令  
# post_build_cmd =

[app_source]

# 源代码排除模式
# exclude_exts = 
# exclude_dirs = 

# 包含的额外文件/目录
include_exts = 
include_dirs = 

# 在APK中包含的额外文件
include_patterns = 

# 从APK中排除的文件
exclude_patterns = 

# 在构建时解压的文件
unpack_patterns = 

# 在构建时解压的目录
unpack_dirs = 

# 在构建时运行的钩子脚本
# pre_compile_hook = 
# post_compile_hook = 

# 在构建APK时运行的钩子脚本
# pre_apk_hook = 
# post_apk_hook = 

# 在安装APK时运行的钩子脚本
# pre_install_hook = 
# post_install_hook = 