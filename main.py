import sqlite3
import os
import json
from datetime import datetime, date, timedelta
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Rectangle
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.metrics import dp
import platform

# 更可靠的Android平台检测
IS_ANDROID = False
try:
    import android
    IS_ANDROID = True
except ImportError:
    # 备选检测方法
    IS_ANDROID = platform.system() == "Linux" and "ANDROID_ARGUMENT" in os.environ

# 数据处理库的安全导入
pd = None
try:
    import pandas as pd
except ImportError:
    Logger.warning("pandas库未找到，导出/导入功能将不可用")

openpyxl_available = False
try:
    import openpyxl
    openpyxl_available = True
except ImportError:
    Logger.warning("openpyxl库未找到，Excel文件导出/导入功能将不可用")

# Android权限请求
if IS_ANDROID:
    try:
        from android.permissions import request_permissions, Permission
        request_permissions([
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.READ_EXTERNAL_STORAGE
        ])
    except Exception as e:
        Logger.warning(f"Android: 权限请求失败 - {str(e)}")

# 在Android上设置环境变量
if IS_ANDROID:
    try:
        from android import mActivity
        from android.storage import app_storage_path, primary_external_storage_path
        from android.permissions import request_permissions, Permission
        # 请求必要的权限
        request_permissions([
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.READ_EXTERNAL_STORAGE
        ])
    except Exception as e:
        Logger.warning(f"Android: 权限请求失败 - {str(e)}")

def format_date(date_obj):
    """将日期格式化为统一的YYYY/MM/DD格式
    
    Args:
        date_obj: 日期对象或日期字符串
        
    Returns:
        str: 格式化后的日期字符串 (YYYY/MM/DD)
    """
    try:
        # 如果输入已经是字符串，尝试解析为日期对象
        if isinstance(date_obj, str):
            # 去除字符串两端的空白字符
            date_str = date_obj.strip()
            # 如果字符串为空，返回今天的日期
            if not date_str:
                Logger.warning("format_date: 输入的日期字符串为空")
                return datetime.today().strftime('%Y/%m/%d')
                
            # 尝试多种常见格式解析
            formats_to_try = [
                '%Y-%m-%d',     # 2024-01-01
                '%Y/%m/%d',     # 2024/01/01
                '%Y%m%d',       # 20240101
                '%d-%m-%Y',     # 01-01-2024
                '%d/%m/%Y',     # 01/01/2024
                '%d.%m.%Y',     # 01.01.2024
                '%Y-%m-%d %H:%M:%S',  # 2024-01-01 12:00:00
                '%Y/%m/%d %H:%M:%S',  # 2024/01/01 12:00:00
                '%d-%m-%Y %H:%M:%S',  # 01-01-2024 12:00:00
                '%d/%m/%Y %H:%M:%S',  # 01/01/2024 12:00:00
            ]
            
            for fmt in formats_to_try:
                try:
                    date_obj = datetime.strptime(date_str, fmt).date()
                    break
                except ValueError:
                    continue
            else:
                # 如果所有格式都失败，尝试Excel日期格式（数字）
                try:
                    date_num = float(date_str)
                    # Excel日期从1900-01-01开始
                    if date_num > 0:
                        # 处理Excel的1900年闰年错误
                        if date_num < 60:
                            # 1900-02-29不存在，Excel错误地将其视为有效
                            delta = timedelta(days=date_num - 2)
                        else:
                            delta = timedelta(days=date_num - 1)
                        date_obj = datetime(1899, 12, 30).date() + delta
                    else:
                        Logger.error(f"format_date: 无效的Excel日期数字: {date_num}")
                        return datetime.today().strftime('%Y/%m/%d')
                except (ValueError, TypeError):
                    Logger.error(f"format_date: 无法解析日期字符串: {date_str}")
                    return datetime.today().strftime('%Y/%m/%d')
        
        # 确保是日期对象并格式化
        if hasattr(date_obj, 'strftime'):
            return date_obj.strftime('%Y/%m/%d')
        else:
            Logger.error(f"format_date: 无效的日期对象类型: {type(date_obj)}")
            return datetime.today().strftime('%Y/%m/%d')
    except Exception as e:
        Logger.error(f"format_date: 处理日期时出错: {str(e)}")
        return datetime.today().strftime('%Y/%m/%d')

def parse_date(date_str):
    """解析各种格式的日期字符串为date对象
    
    Args:
        date_str: 日期字符串
        
    Returns:
        date: 日期对象，如果无法解析则返回今天的日期
    """
    try:
        # 处理None或空字符串
        if date_str is None or (isinstance(date_str, str) and not date_str.strip()):
            Logger.warning("parse_date: 输入的日期字符串为None或空")
            return date.today()
            
        # 确保输入是字符串
        if not isinstance(date_str, str):
            date_str = str(date_str)
        
        # 去除字符串两端的空白字符
        date_str = date_str.strip()
        
        # 尝试多种常见格式解析
        formats_to_try = [
            '%Y/%m/%d',     # 2024/01/01 (首选)
            '%Y-%m-%d',     # 2024-01-01
            '%Y%m%d',       # 20240101
            '%d-%m-%Y',     # 01-01-2024
            '%d/%m/%Y',     # 01/01/2024
            '%d.%m.%Y',     # 01.01.2024
            '%Y-%m-%d %H:%M:%S',  # 2024-01-01 12:00:00
            '%Y/%m/%d %H:%M:%S',  # 2024/01/01 12:00:00
            '%d-%m-%Y %H:%M:%S',  # 01-01-2024 12:00:00
            '%d/%m/%Y %H:%M:%S',  # 01/01/2024 12:00:00
        ]
        
        for fmt in formats_to_try:
            try:
                parsed_date = datetime.strptime(date_str, fmt).date()
                # 验证日期的合理性（不允许未来日期或过旧的日期）
                if parsed_date > date.today():
                    Logger.warning(f"parse_date: 日期 {parsed_date} 是未来日期，使用今天的日期")
                    return date.today()
                if parsed_date < date(1900, 1, 1):
                    Logger.warning(f"parse_date: 日期 {parsed_date} 过于古老，使用今天的日期")
                    return date.today()
                return parsed_date
            except ValueError:
                continue
        
        # 如果所有格式都失败，尝试Excel日期格式（数字）
        try:
            date_num = float(date_str)
            # Excel日期从1900-01-01开始
            if date_num > 0:
                # 处理Excel的1900年闰年错误
                if date_num < 60:
                    delta = timedelta(days=date_num - 2)
                else:
                    delta = timedelta(days=date_num - 1)
                parsed_date = datetime(1899, 12, 30).date() + delta
                
                # 验证日期的合理性
                if parsed_date > date.today():
                    Logger.warning(f"parse_date: Excel日期转换结果 {parsed_date} 是未来日期，使用今天的日期")
                    return date.today()
                if parsed_date < date(1900, 1, 1):
                    Logger.warning(f"parse_date: Excel日期转换结果 {parsed_date} 过于古老，使用今天的日期")
                    return date.today()
                
                Logger.info(f"parse_date: 成功将Excel日期 {date_num} 转换为 {parsed_date}")
                return parsed_date
            else:
                Logger.error(f"parse_date: 无效的Excel日期数字: {date_num}")
        except (ValueError, TypeError):
            Logger.error(f"parse_date: 无法解析日期字符串: {date_str}")
            
        # 所有尝试都失败，返回今天的日期
        return date.today()
    except Exception as e:
        Logger.error(f"parse_date: 处理日期时出错: {str(e)}")
        return date.today()

class SimpleChart(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_points = []
        self.labels = []
        self.chart_title = "体重趋势图"
        self.y_axis_label = "体重(斤)"
        self.x_axis_label = "日期"
        self.min_value = 0
        self.max_value = 0
        self.background_color = (1, 1, 1, 1)
        self.line_color = (0.2, 0.6, 0.8, 1)
        self.grid_color = (0.8, 0.8, 0.8, 0.5)
        self.text_color = (0, 0, 0, 1)
        
    def set_data(self, data_points, labels=None):
        """设置图表数据"""
        # 确保data_points是列表类型
        if not isinstance(data_points, list):
            data_points = []
            
        self.data_points = data_points
        self.labels = labels if labels else [str(i+1) for i in range(len(data_points))]
        
        if data_points:
            try:
                self.min_value = min(data_points)
                self.max_value = max(data_points)
                
                value_range = self.max_value - self.min_value
                if value_range > 0:
                    self.min_value -= value_range * 0.1
                    self.max_value += value_range * 0.1
                else:
                    # 当所有值相同时，设置合理的范围
                    self.min_value -= 10
                    self.max_value += 10
            except (ValueError, TypeError):
                # 如果计算最小值或最大值出错，设置默认值
                self.min_value = 0
                self.max_value = 100
        else:
            self.min_value = 0
            self.max_value = 100
            
        self.draw_chart()
    
    def draw_chart(self):
        """绘制图表"""
        self.canvas.clear()
        
        with self.canvas:
            Color(*self.background_color)
            Rectangle(pos=self.pos, size=self.size)
            
            if not self.data_points:
                Color(*self.text_color)
                Rectangle(
                    pos=(self.center_x - 100, self.center_y - 15),
                    size=(200, 30)
                )
                return
            
            self.draw_grid_and_axes()
            self.draw_data_line()
    
    def draw_grid_and_axes(self):
        """绘制网格和坐标轴"""
        margin_left = dp(80)
        margin_bottom = dp(60)
        margin_top = dp(50)
        margin_right = dp(40)
        
        chart_width = self.width - margin_left - margin_right
        chart_height = self.height - margin_bottom - margin_top
        
        Color(*self.grid_color)
        
        num_h_lines = 5
        for i in range(num_h_lines + 1):
            y = margin_bottom + (chart_height / num_h_lines) * i
            Line(
                points=[margin_left, y, margin_left + chart_width, y],
                width=1
            )
            
        num_points = len(self.data_points)
        if num_points > 0:
            step = max(1, num_points // 5)
            
            for i in range(0, num_points, step):
                if i < len(self.labels):
                    x = margin_left + (chart_width / max(1, (num_points - 1))) * i
                    Line(
                        points=[x, margin_bottom, x, margin_bottom + chart_height],
                        width=1
                    )
        
        Color(0, 0, 0, 1)
        Line(
            points=[margin_left, margin_bottom, margin_left, margin_bottom + chart_height],
            width=2
        )
        Line(
            points=[margin_left, margin_bottom, margin_left + chart_width, margin_bottom],
            width=2
        )
    
    def draw_data_line(self):
        """绘制数据线"""
        if not self.data_points:
            return
            
        margin_left = dp(80)
        margin_bottom = dp(60)
        margin_top = dp(50)
        margin_right = dp(40)
        
        chart_width = max(1, self.width - margin_left - margin_right)
        chart_height = max(1, self.height - margin_bottom - margin_top)
        
        points = []
        num_points = len(self.data_points)
        
        for i, value in enumerate(self.data_points):
            if num_points > 1:
                # 避免除零错误
                x = margin_left + (chart_width / max(1, num_points - 1)) * i
            else:
                x = margin_left + chart_width * 0.5
            
            value_range = self.max_value - self.min_value
            # 防止除零错误，为value_range设置默认值
            if value_range > 0:
                y = margin_bottom + ((value - self.min_value) / value_range) * chart_height
            else:
                y = margin_bottom + chart_height * 0.5
            
            points.extend([x, y])
        
        Color(*self.line_color)
        Line(points=points, width=2)
        
        for i, value in enumerate(self.data_points):
            if num_points > 1:
                x = margin_left + (chart_width / (num_points - 1)) * i
            else:
                x = margin_left + chart_width * 0.5
            
            value_range = self.max_value - self.min_value
            if value_range > 0:
                y = margin_bottom + ((value - self.min_value) / value_range) * chart_height
            else:
                y = margin_bottom + chart_height * 0.5
            
            Color(0.8, 0.2, 0.2, 1)
            Rectangle(pos=(x-3, y-3), size=(6, 6))
    
    def on_size(self, *args):
        self.draw_chart()

class WeightDatabase:
    def __init__(self, app_instance=None):
        self.app = app_instance
        self.db_path = self.get_db_path()
        # 立即初始化数据库，创建必要的表
        self.init_database()
    
    def get_db_path(self):
        try:
            if IS_ANDROID:
                from android.storage import app_storage_path
                try:
                    # 使用推荐的应用存储路径
                    app_dir = app_storage_path()
                    db_path = os.path.join(app_dir, "weight_data.db")
                    Logger.info(f"Database: 使用Android存储路径 - {db_path}")
                    return db_path
                except Exception as e:
                    # 备选方案
                    Logger.warning(f"获取app_storage_path失败: {str(e)}")
                    if self.app and hasattr(self.app, 'user_data_dir'):
                        return os.path.join(self.app.user_data_dir, "weight_data.db")
                    else:
                        return ":memory:"  # 使用内存数据库作为最后备选
            else:
                return "weight_data.db"
        except Exception as e:
            Logger.error(f"获取数据库路径失败: {str(e)}")
            return ":memory:"
    
    def get_export_path(self, filename):
        """获取导出文件路径，确保路径有效且有适当的访问权限"""
        Logger.info(f"开始获取导出路径，文件名: {filename}")
        
        # 验证文件名
        if not filename or not isinstance(filename, str):
            Logger.error("无效的文件名")
            filename = "weight_data_export.xlsx"  # 默认文件名
        
        try:
            if IS_ANDROID:
                # Android环境处理
                Logger.info("Android环境：开始处理导出路径")
                
                # 尝试多种方式获取基础目录
                base_dir = None
                
                # 方法1: 优先使用应用的user_data_dir
                if self.app and hasattr(self.app, 'user_data_dir'):
                    base_dir = self.app.user_data_dir
                    Logger.info(f"Android环境：使用应用user_data_dir - {base_dir}")
                
                # 方法2: 尝试使用app_storage_path
                if not base_dir:
                    try:
                        from android.storage import app_storage_path
                        base_dir = app_storage_path()
                        Logger.info(f"Android环境：使用app_storage_path - {base_dir}")
                    except Exception as e:
                        Logger.warning(f"Android环境：无法获取app_storage_path - {str(e)}")
                
                # 方法3: 使用通用Android路径作为备选
                if not base_dir:
                    base_dir = "/data/user/0/org.example.weighttracker/files"
                    Logger.info(f"Android环境：使用通用路径 - {base_dir}")
                
                # 确保目录存在，处理可能的权限问题
                return self._ensure_directory_and_get_path(base_dir, "exports", filename, is_android=True)
            else:
                # 非Android环境（Windows、Mac、Linux等）
                Logger.info("非Android环境：开始处理导出路径")
                
                # 定义备选路径列表，按优先级排序
                alternative_paths = []
                
                # 方法1: 应用的user_data_dir（如果可用）
                if self.app and hasattr(self.app, 'user_data_dir'):
                    alternative_paths.append((self.app.user_data_dir, "应用数据目录"))
                
                # 方法2: 用户文档目录（更安全的位置）
                try:
                    import pathlib
                    # 获取用户文档目录，跨平台兼容
                    docs_dir = str(pathlib.Path.home() / "Documents")
                    alternative_paths.append((docs_dir, "用户文档目录"))
                except Exception as e:
                    Logger.warning(f"无法获取文档目录: {str(e)}")
                
                # 方法3: 用户主目录
                user_home = os.path.expanduser("~")
                alternative_paths.append((user_home, "用户主目录"))
                
                # 方法4: 当前工作目录
                try:
                    current_dir = os.getcwd()
                    alternative_paths.append((current_dir, "当前工作目录"))
                except Exception as e:
                    Logger.warning(f"无法获取当前工作目录: {str(e)}")
                
                # 尝试每个备选路径
                for base_dir, dir_type in alternative_paths:
                    Logger.info(f"尝试使用{dir_type} - {base_dir}")
                    result = self._ensure_directory_and_get_path(base_dir, "weight_data_exports", filename)
                    if result:
                        return result
                
                # 所有路径都失败了，返回相对路径作为最后手段
                Logger.warning("所有备选路径都失败，使用相对路径")
                return filename
                
        except Exception as e:
            Logger.error(f"获取导出路径失败: {str(e)}")
            # 作为最后备选，使用当前目录
            try:
                return os.path.join(os.getcwd(), filename)
            except:
                # 完全失败时，返回文件名
                return filename
    
    def _ensure_directory_and_get_path(self, base_dir, subdir_name, filename, is_android=False):
        """确保目录存在并返回完整路径"""
        try:
            # 确保base_dir有效
            if not base_dir or not isinstance(base_dir, str):
                Logger.warning("无效的基础目录")
                return None
            
            # 创建子目录
            export_dir = os.path.join(base_dir, subdir_name)
            
            # 检查目录是否存在，如果不存在则尝试创建
            if not os.path.exists(export_dir):
                try:
                    os.makedirs(export_dir, exist_ok=True)  # 使用exist_ok避免竞争条件
                    Logger.info(f"成功创建目录: {export_dir}")
                except PermissionError as e:
                    Logger.error(f"权限错误，无法创建目录 {export_dir}: {str(e)}")
                    # 直接使用基础目录
                    export_path = os.path.join(base_dir, filename)
                    if self._check_write_permission(os.path.dirname(export_path)):
                        Logger.warning(f"使用基础目录作为备选: {base_dir}")
                        return export_path
                    return None
                except Exception as e:
                    Logger.error(f"无法创建目录 {export_dir}: {str(e)}")
                    return None
            
            # 构建完整路径
            export_path = os.path.join(export_dir, filename)
            
            # 检查是否有写入权限
            if self._check_write_permission(export_dir):
                env_type = "Android" if is_android else "非Android"
                Logger.info(f"{env_type}环境：成功获取导出路径 - {export_path}")
                return export_path
            else:
                Logger.warning(f"没有写入权限: {export_dir}")
                # 尝试直接使用基础目录
                fallback_path = os.path.join(base_dir, filename)
                if self._check_write_permission(base_dir):
                    Logger.warning(f"使用基础目录作为备选: {fallback_path}")
                    return fallback_path
                return None
        except Exception as e:
            Logger.error(f"确保目录存在时出错: {str(e)}")
            return None
    
    def _check_write_permission(self, directory):
        """检查目录是否有写入权限"""
        try:
            if not directory or not os.path.exists(directory):
                # 如果目录不存在，尝试检查父目录
                parent_dir = os.path.dirname(directory)
                if parent_dir and parent_dir != directory:  # 避免无限递归
                    return self._check_write_permission(parent_dir)
                return False
            
            # 测试写入权限
            test_file = os.path.join(directory, "permission_test.tmp")
            try:
                with open(test_file, 'w') as f:
                    f.write("test")
                # 写入成功，清理测试文件
                os.remove(test_file)
                Logger.debug(f"写入权限检查通过: {directory}")
                return True
            except:
                Logger.warning(f"写入权限检查失败: {directory}")
                return False
        except Exception as e:
            Logger.error(f"检查写入权限时出错: {str(e)}")
            return False
    
    def init_database(self):
        """初始化数据库"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # 确保目录存在
                db_dir = os.path.dirname(self.db_path)
                if db_dir and not os.path.exists(db_dir):
                    os.makedirs(db_dir)
                    Logger.info(f"Database: 创建目录 - {db_dir}")
                
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS weight_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        weight_type TEXT NOT NULL,
                        weight REAL NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS diary_entries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        food TEXT,
                        thoughts TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.commit()
                conn.close()
                Logger.info("Database: 数据库初始化成功")
                return
                
            except Exception as e:
                Logger.error(f"Database: 数据库初始化失败 (尝试 {attempt + 1}/{max_retries}) - {str(e)}")
                if attempt == max_retries - 1:
                    # 最后一次尝试失败，使用内存数据库
                    try:
                        self.db_path = ":memory:"
                        conn = sqlite3.connect(self.db_path)
                        cursor = conn.cursor()
                        
                        cursor.execute('''
                            CREATE TABLE IF NOT EXISTS weight_records (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                date TEXT NOT NULL,
                                weight_type TEXT NOT NULL,
                                weight REAL NOT NULL,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )
                        ''')
                        
                        cursor.execute('''
                            CREATE TABLE IF NOT EXISTS diary_entries (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                date TEXT NOT NULL,
                                food TEXT,
                                thoughts TEXT,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )
                        ''')
                        
                        conn.commit()
                        conn.close()
                        Logger.info("Database: 使用内存数据库成功")
                    except Exception as e2:
                        Logger.error(f"Database: 内存数据库也失败 - {str(e2)}")
    
    def get_connection(self):
        """获取数据库连接，并确保表存在"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # 额外的安全检查：确保表存在
            cursor = conn.cursor()
            
            # 检查并创建weight_records表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS weight_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    weight_type TEXT NOT NULL,
                    weight REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 检查并创建diary_entries表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS diary_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    food TEXT,
                    thoughts TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            return conn
        except Exception as e:
            Logger.error(f"Database: 获取连接失败 - {str(e)}")
            return None
    
    def add_weight_record(self, date_str, weight_type, weight):
        conn = self.get_connection()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id FROM weight_records 
                WHERE date = ? AND weight_type = ?
            ''', (date_str, weight_type))
            
            existing_record = cursor.fetchone()
            
            if existing_record:
                cursor.execute('''
                    UPDATE weight_records 
                    SET weight = ?, created_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (weight, existing_record[0]))
            else:
                cursor.execute('''
                    INSERT INTO weight_records (date, weight_type, weight)
                    VALUES (?, ?, ?)
                ''', (date_str, weight_type, weight))
            
            conn.commit()
            conn.close()
            Logger.info(f"Database: 体重记录成功 - {date_str} {weight_type} {weight}斤")
            return True
        except Exception as e:
            Logger.error(f"Database: 体重记录失败 - {str(e)}")
            try:
                conn.close()
            except:
                pass
            return False
            
    def add_record(self, date_str, weight_type, weight):
        """add_weight_record的别名，用于兼容测试脚本"""
        return self.add_weight_record(date_str, weight_type, weight)
    
    def add_diary_entry(self, date_str, food, thoughts):
        conn = self.get_connection()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id FROM diary_entries WHERE date = ?
            ''', (date_str,))
            
            existing_entry = cursor.fetchone()
            
            if existing_entry:
                cursor.execute('''
                    UPDATE diary_entries 
                    SET food = ?, thoughts = ?, created_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (food, thoughts, existing_entry[0]))
            else:
                cursor.execute('''
                    INSERT INTO diary_entries (date, food, thoughts)
                    VALUES (?, ?, ?)
                ''', (date_str, food, thoughts))
            
            conn.commit()
            conn.close()
            Logger.info(f"Database: 日记记录成功 - {date_str}")
            return True
        except Exception as e:
            Logger.error(f"Database: 日记记录失败 - {str(e)}")
            try:
                conn.close()
            except:
                pass
            return False
    
    def get_today_diary_entry(self):
        """获取今天的日记记录"""
        conn = self.get_connection()
        if not conn:
            return None
            
        try:
            cursor = conn.cursor()
            current_date = format_date(date.today())
            
            cursor.execute('''
                SELECT food, thoughts FROM diary_entries WHERE date = ?
            ''', (current_date,))
            
            entry = cursor.fetchone()
            conn.close()
            
            if entry:
                return {'food': entry[0], 'thoughts': entry[1]}
            else:
                return None
        except Exception as e:
            Logger.error(f"Database: 获取今日日记失败 - {str(e)}")
            try:
                conn.close()
            except:
                pass
            return None
    
    def get_recent_records(self, days=7):
        conn = self.get_connection()
        if not conn:
            return []
            
        try:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT date, weight_type, weight 
                FROM weight_records 
                ORDER BY date DESC, weight_type ASC
                LIMIT ?
            ''', (days * 2,))
            
            records = cursor.fetchall()
            conn.close()
            
            formatted_records = []
            for record in records:
                date_str, weight_type, weight = record
                formatted_date = format_date(parse_date(date_str))
                formatted_records.append((formatted_date, weight_type, weight))
            
            return formatted_records
        except Exception as e:
            Logger.error(f"Database: 获取最近记录失败 - {str(e)}")
            try:
                conn.close()
            except:
                pass
            return []
    
    def get_all_records(self):
        conn = self.get_connection()
        if not conn:
            Logger.warning("Database: 无法获取连接，返回空记录")
            return []
            
        try:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT date, weight_type, weight 
                FROM weight_records 
                ORDER BY date ASC
            ''')
            
            records = cursor.fetchall()
            conn.close()
            
            formatted_records = []
            for record in records:
                date_str, weight_type, weight = record
                formatted_date = format_date(parse_date(date_str))
                formatted_records.append((formatted_date, weight_type, weight))
            
            return formatted_records
        except sqlite3.OperationalError as e:
            error_msg = str(e)
            if "no such table" in error_msg:
                Logger.error(f"Database: 表不存在，尝试重新创建 - {error_msg}")
                # 尝试重新初始化数据库
                try:
                    conn.close()
                except:
                    pass
                self.init_database()
                # 重新尝试获取记录
                return self.get_all_records()
            else:
                Logger.error(f"Database: 操作错误 - {error_msg}")
        except Exception as e:
            Logger.error(f"Database: 获取所有记录失败 - {str(e)}")
        finally:
            try:
                conn.close()
            except:
                pass
        return []
    
    def get_recent_diary_entries(self, count=10):
        conn = self.get_connection()
        if not conn:
            return []
            
        try:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT date, food, thoughts 
                FROM diary_entries 
                ORDER BY date DESC
                LIMIT ?
            ''', (count,))
            
            entries = cursor.fetchall()
            conn.close()
            
            formatted_entries = []
            for entry in entries:
                date_str, food, thoughts = entry
                formatted_date = format_date(parse_date(date_str))
                formatted_entries.append((formatted_date, food, thoughts))
            
            return formatted_entries
        except Exception as e:
            Logger.error(f"Database: 获取日记记录失败 - {str(e)}")
            try:
                conn.close()
            except:
                pass
            return []
    
    def get_all_diary_entries(self):
        conn = self.get_connection()
        if not conn:
            return []
            
        try:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT date, food, thoughts 
                FROM diary_entries 
                ORDER BY date ASC
            ''')
            
            entries = cursor.fetchall()
            conn.close()
            
            formatted_entries = []
            for entry in entries:
                date_str, food, thoughts = entry
                formatted_date = format_date(parse_date(date_str))
                formatted_entries.append((formatted_date, food, thoughts))
            
            return formatted_entries
        except Exception as e:
            Logger.error(f"Database: 获取所有日记失败 - {str(e)}")
            try:
                conn.close()
            except:
                pass
            return []
    
    def get_weight_statistics(self):
        conn = self.get_connection()
        if not conn:
            return None
            
        try:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT weight FROM weight_records ORDER BY date ASC LIMIT 1
            ''')
            initial_record = cursor.fetchone()
            
            cursor.execute('''
                SELECT MIN(weight) FROM weight_records
            ''')
            lightest_record = cursor.fetchone()
            
            cursor.execute('''
                SELECT MAX(weight) FROM weight_records
            ''')
            heaviest_record = cursor.fetchone()
            
            cursor.execute('''
                SELECT AVG(weight) FROM weight_records
            ''')
            average_record = cursor.fetchone()
            
            conn.close()
            
            if not initial_record:
                return None
            
            stats = {
                'initial_weight': initial_record[0],
                'lightest_weight': lightest_record[0] if lightest_record[0] else initial_record[0],
                'heaviest_weight': heaviest_record[0] if heaviest_record[0] else initial_record[0],
                'average_weight': average_record[0] if average_record[0] else initial_record[0],
                'weight_difference': (heaviest_record[0] - lightest_record[0]) if heaviest_record[0] and lightest_record[0] else 0
            }
            
            return stats
        except Exception as e:
            Logger.error(f"Database: 获取统计信息失败 - {str(e)}")
            try:
                conn.close()
            except:
                pass
            return None
    
    def get_chart_data(self, days=30):
        """获取图表数据"""
        conn = self.get_connection()
        if not conn:
            return {'morning_weights': [], 'evening_weights': [], 'labels': []}
            
        try:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT date, weight_type, weight 
                FROM weight_records 
                ORDER BY date ASC
            ''')
            
            all_records = cursor.fetchall()
            conn.close()
            
            chart_data = {}
            labels = []
            
            for record in all_records:
                date_str, weight_type, weight = record
                
                if date_str not in chart_data:
                    chart_data[date_str] = {'morning': None, 'evening': None}
                    labels.append(date_str)
                
                chart_data[date_str][weight_type] = weight
            
            morning_weights = []
            evening_weights = []
            valid_labels = []
            
            for date_str in labels[-days:]:
                morning_weight = chart_data[date_str]['morning']
                evening_weight = chart_data[date_str]['evening']
                
                if morning_weight is not None:
                    morning_weights.append(morning_weight)
                    valid_labels.append(format_date(parse_date(date_str)))
                elif evening_weight is not None:
                    morning_weights.append(evening_weight)
                    valid_labels.append(format_date(parse_date(date_str)))
                
                if evening_weight is not None:
                    evening_weights.append(evening_weight)
            
            return {
                'morning_weights': morning_weights,
                'evening_weights': evening_weights,
                'labels': valid_labels
            }
        except Exception as e:
            Logger.error(f"Database: 获取图表数据失败 - {str(e)}")
            try:
                conn.close()
            except:
                pass
            return {'morning_weights': [], 'evening_weights': [], 'labels': []}
    
    def import_data(self, data):
        """导入数据到数据库，支持体重记录和日记记录
        
        Args:
            data: 包含weight_records和diary_entries的字典
            
        Returns:
            tuple: (是否成功, 错误列表)
        """
        conn = None
        errors = []
        weight_count = 0
        diary_count = 0
        
        try:
            # 获取数据库连接
            conn = self.get_connection()
            if not conn:
                Logger.error("Database: 无法获取数据库连接")
                errors.append("无法获取数据库连接")
                return False, errors
            
            # 验证输入数据格式
            if not isinstance(data, dict):
                Logger.error("Database: 导入数据格式错误 - 必须是字典类型")
                errors.append("导入数据格式错误 - 必须是字典类型")
                return False, errors
                
            cursor = conn.cursor()
            
            # 开始事务
            conn.execute('BEGIN TRANSACTION')
            
            # 清空现有数据
            try:
                cursor.execute('DELETE FROM weight_records')
                cursor.execute('DELETE FROM diary_entries')
            except Exception as e:
                Logger.error(f"Database: 清空表数据失败: {str(e)}")
                conn.rollback()
                errors.append(f"清空表数据失败: {str(e)}")
                return False, errors
            
            # 导入体重记录 - 添加数据验证
            weight_records = data.get('weight_records', [])
            
            for record in weight_records:
                try:
                    # 验证记录长度
                    if len(record) < 3:
                        Logger.warning(f"Database: 跳过无效的体重记录 - 字段不足: {record}")
                        errors.append(f"跳过无效的体重记录 - 字段不足: {record}")
                        continue
                        
                    date_str, weight_type_cn, weight = record
                    
                    # 验证并格式化日期
                    try:
                        formatted_date = format_date(parse_date(str(date_str)))
                    except (ValueError, TypeError) as date_error:
                        Logger.warning(f"Database: 跳过无效的日期: {date_str} - {str(date_error)}")
                        errors.append(f"跳过无效的日期: {date_str}")
                        continue
                    
                    # 验证并转换体重类型
                    weight_type_en = None
                    # 支持中英文体重类型
                    if weight_type_cn in ['早晨', 'morning']:
                        weight_type_en = 'morning'
                    elif weight_type_cn in ['晚上', 'evening']:
                        weight_type_en = 'evening'
                    else:
                        Logger.warning(f"Database: 跳过无效的体重类型: {weight_type_cn}")
                        errors.append(f"跳过无效的体重类型: {weight_type_cn}")
                        continue
                        
                    # 验证并转换体重值
                    try:
                        weight_float = float(weight)
                        # 验证体重范围 (20-400斤)
                        if not (20 <= weight_float <= 400):
                            Logger.warning(f"Database: 跳过无效的体重值: {weight_float} - 超出范围20-400")
                            errors.append(f"跳过无效的体重值: {weight_float} - 超出范围20-400")
                            continue
                    except (ValueError, TypeError):
                        Logger.warning(f"Database: 跳过无效的体重值: {weight}")
                        errors.append(f"跳过无效的体重值: {weight}")
                        continue
                        
                    # 插入有效记录
                    try:
                        cursor.execute('''
                            INSERT INTO weight_records (date, weight_type, weight)
                            VALUES (?, ?, ?)
                        ''', (formatted_date, weight_type_en, weight_float))
                        weight_count += 1
                    except Exception as insert_error:
                        Logger.warning(f"Database: 插入体重记录失败: {record} - {str(insert_error)}")
                        errors.append(f"插入体重记录失败: {record}")
                        continue
                        
                except Exception as record_error:
                    Logger.warning(f"Database: 处理体重记录时出错: {record} - {str(record_error)}")
                    errors.append(f"处理体重记录时出错: {record}")
                    continue
            
            # 导入日记记录 - 添加数据验证
            diary_entries = data.get('diary_entries', [])
            
            for entry in diary_entries:
                try:
                    # 验证记录长度
                    if len(entry) < 3:
                        Logger.warning(f"Database: 跳过无效的日记记录 - 字段不足: {entry}")
                        errors.append(f"跳过无效的日记记录 - 字段不足: {entry}")
                        continue
                        
                    date_str, food, thoughts = entry
                    
                    # 验证并格式化日期
                    try:
                        formatted_date = format_date(parse_date(str(date_str)))
                    except (ValueError, TypeError) as date_error:
                        Logger.warning(f"Database: 跳过无效的日期: {date_str} - {str(date_error)}")
                        errors.append(f"跳过无效的日期: {date_str}")
                        continue
                    
                    # 处理空值
                    food_str = str(food) if food is not None else ''
                    thoughts_str = str(thoughts) if thoughts is not None else ''
                    
                    # 插入日记记录
                    try:
                        cursor.execute('''
                            INSERT INTO diary_entries (date, food, thoughts)
                            VALUES (?, ?, ?)
                        ''', (formatted_date, food_str, thoughts_str))
                        diary_count += 1
                    except Exception as insert_error:
                        Logger.warning(f"Database: 插入日记记录失败: {entry} - {str(insert_error)}")
                        errors.append(f"插入日记记录失败: {entry}")
                        continue
                    
                except Exception as entry_error:
                    Logger.warning(f"Database: 处理日记记录时出错: {entry} - {str(entry_error)}")
                    errors.append(f"处理日记记录时出错: {entry}")
                    continue
            
            # 提交事务
            try:
                conn.commit()
                Logger.info(f"Database: 成功导入 {weight_count} 条体重记录和 {diary_count} 条日记记录")
                return True, errors
            except Exception as commit_error:
                Logger.error(f"Database: 提交事务失败: {str(commit_error)}")
                conn.rollback()
                errors.append(f"提交事务失败: {str(commit_error)}")
                return False, errors
        except Exception as e:
            Logger.error(f"Database: 导入数据时发生错误: {str(e)}")
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            errors.append(f"导入数据时发生错误: {str(e)}")
            return False, errors
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass

class WeightTrackerApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = None
    
    def build(self):
        try:
            # 设置应用标题
            self.title = "减肥体重记录器"
            
            # 延迟创建数据库，确保应用完全启动
            Clock.schedule_once(self.initialize_database, 0.5)
            
            # 创建主界面
            main_layout = TabbedPanel(tab_pos='bottom_mid')
            main_layout.do_default_tab = False
            main_layout.font_size = '32sp'
            
            # 记录体重标签页
            record_tab = TabbedPanelItem(text='记录体重')
            record_tab.add_widget(self.create_record_tab())
            main_layout.add_widget(record_tab)
            
            # 体重统计标签页
            stats_tab = TabbedPanelItem(text='体重统计')
            stats_tab.add_widget(self.create_stats_tab())
            main_layout.add_widget(stats_tab)
            
            # 趋势图表标签页
            chart_tab = TabbedPanelItem(text='趋势图表')
            chart_tab.add_widget(self.create_chart_tab())
            main_layout.add_widget(chart_tab)
            
            # 减肥日记标签页
            diary_tab = TabbedPanelItem(text='减肥日记')
            diary_tab.add_widget(self.create_diary_tab())
            main_layout.add_widget(diary_tab)
            
            # 数据管理标签页
            data_tab = TabbedPanelItem(text='数据管理')
            data_tab.add_widget(self.create_data_tab())
            main_layout.add_widget(data_tab)
            
            Logger.info("App: 应用界面初始化成功")
            return main_layout
            
        except Exception as e:
            Logger.error(f"App: 应用初始化失败 - {str(e)}")
            return self.create_error_layout(str(e))
    
    def initialize_database(self, dt):
        """延迟初始化数据库"""
        try:
            self.db = WeightDatabase(self)
            Logger.info("App: 数据库初始化成功")
            
            # 初始化显示数据
            self.update_records_display()
            self.update_statistics()
            self.update_chart()
            self.load_today_diary()
            self.update_diary_display()
            
        except Exception as e:
            Logger.error(f"App: 数据库初始化失败 - {str(e)}")
            self.show_popup("错误", f"数据库初始化失败: {str(e)}")
    
    def create_error_layout(self, error_msg):
        """创建错误界面"""
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text='应用启动失败', font_size=52))
        layout.add_widget(Label(text=f'错误: {error_msg}', font_size=36))
        
        restart_btn = Button(
            text='重启应用',
            font_size=44,
            background_color=(0.8, 0.2, 0.2, 1)
        )
        restart_btn.bind(on_press=self.restart_app)
        layout.add_widget(restart_btn)
        
        return layout
    
    def restart_app(self, instance):
        """重启应用"""
        try:
            App.get_running_app().stop()
            WeightTrackerApp().run()
        except Exception as e:
            Logger.error(f"App: 重启失败 - {str(e)}")
    
    def create_record_tab(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        title = Label(text='记录体重', font_size=52, size_hint_y=0.1)
        layout.add_widget(title)
        
        time_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1, spacing=15)
        time_layout.add_widget(Label(text='选择时间:', font_size=44))
        
        self.time_spinner = Spinner(
            text='早晨',
            values=('早晨', '晚上'),
            font_size=44,
            size_hint_x=0.7
        )
        time_layout.add_widget(self.time_spinner)
        layout.add_widget(time_layout)
        
        weight_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1, spacing=15)
        weight_layout.add_widget(Label(text='体重(斤):', font_size=44))
        
        self.weight_input = TextInput(
            multiline=False,
            input_filter='float',
            font_size=44,
            hint_text='输入20-400之间的数字',
            size_hint_x=0.7
        )
        weight_layout.add_widget(self.weight_input)
        layout.add_widget(weight_layout)
        
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1, spacing=15)
        
        record_btn = Button(
            text='记录体重',
            font_size=44,
            background_color=(0.2, 0.6, 0.8, 1)
        )
        record_btn.bind(on_press=self.record_weight)
        button_layout.add_widget(record_btn)
        
        layout.add_widget(button_layout)
        
        self.records_label = Label(
            text='最近体重记录：\n\n',
            font_size=40,
            text_size=(None, None),
            size_hint_y=0.65,
            halign='left',
            valign='top'
        )
        self.records_label.bind(size=self.records_label.setter('text_size'))
        
        scroll = ScrollView()
        scroll.add_widget(self.records_label)
        layout.add_widget(scroll)
        
        Clock.schedule_once(self.update_records_display, 0.1)
        
        return layout
    
    def create_stats_tab(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        title = Label(text='体重统计', font_size=52, size_hint_y=0.1)
        layout.add_widget(title)
        
        stats_layout = BoxLayout(orientation='vertical', spacing=20, padding=20)
        
        self.initial_weight = Label(
            text='初始体重: 计算中...',
            font_size=46
        )
        stats_layout.add_widget(self.initial_weight)
        
        self.lightest_weight = Label(
            text='最轻体重: 计算中...',
            font_size=46,
            color=(0, 0.6, 0, 1)
        )
        stats_layout.add_widget(self.lightest_weight)
        
        self.heaviest_weight = Label(
            text='最重体重: 计算中...',
            font_size=46,
            color=(0.8, 0, 0, 1)
        )
        stats_layout.add_widget(self.heaviest_weight)
        
        self.average_weight = Label(
            text='平均体重: 计算中...',
            font_size=46,
            color=(0, 0, 0.8, 1)
        )
        stats_layout.add_widget(self.average_weight)
        
        self.weight_diff = Label(
            text='体重差值: 计算中...',
            font_size=46,
            color=(0.6, 0.2, 0.6, 1)
        )
        stats_layout.add_widget(self.weight_diff)
        
        layout.add_widget(stats_layout)
        
        refresh_btn = Button(
            text='刷新统计',
            font_size=44,
            background_color=(0.2, 0.7, 0.3, 1),
            size_hint_y=0.1
        )
        refresh_btn.bind(on_press=self.update_statistics)
        layout.add_widget(refresh_btn)
        
        Clock.schedule_once(self.update_statistics, 0.1)
        
        return layout
    
    def create_chart_tab(self):
        layout = BoxLayout(orientation='vertical', padding=15, spacing=15)
        
        title = Label(text='体重趋势图', font_size=52, size_hint_y=0.1)
        layout.add_widget(title)
        
        chart_type_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1, spacing=15)
        chart_type_layout.add_widget(Label(text='图表类型:', font_size=42))
        
        self.chart_type_spinner = Spinner(
            text='早晨体重',
            values=('早晨体重', '晚上体重', '全部体重'),
            font_size=42
        )
        self.chart_type_spinner.bind(text=self.on_chart_type_change)
        chart_type_layout.add_widget(self.chart_type_spinner)
        
        chart_type_layout.add_widget(Label(text='时间范围:', font_size=42))
        
        self.chart_range_spinner = Spinner(
            text='最近7天',
            values=('最近7天', '最近30天', '全部数据'),
            font_size=42
        )
        self.chart_range_spinner.bind(text=self.on_chart_range_change)
        chart_type_layout.add_widget(self.chart_range_spinner)
        
        layout.add_widget(chart_type_layout)
        
        chart_scroll = ScrollView(size_hint_y=0.7, do_scroll_x=True, do_scroll_y=True)
        chart_container = BoxLayout(orientation='vertical', size_hint=(None, None))
        chart_container.bind(minimum_height=chart_container.setter('height'))
        chart_container.bind(minimum_width=chart_container.setter('width'))
        
        self.chart = SimpleChart()
        self.chart.size_hint = (None, None)
        self.chart.size = (800, 600)
        
        chart_container.add_widget(self.chart)
        chart_scroll.add_widget(chart_container)
        layout.add_widget(chart_scroll)
        
        refresh_btn = Button(
            text='刷新图表',
            font_size=44,
            background_color=(0.2, 0.7, 0.3, 1),
            size_hint_y=0.1
        )
        refresh_btn.bind(on_press=self.update_chart)
        layout.add_widget(refresh_btn)
        
        Clock.schedule_once(self.update_chart, 0.1)
        
        return layout
    
    def create_diary_tab(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        title = Label(text='减肥日记', font_size=52, size_hint_y=0.05)
        layout.add_widget(title)
        
        layout.add_widget(Label(text='今日饮食:', font_size=44, size_hint_y=0.05))
        
        self.food_input = TextInput(
            multiline=True,
            font_size=40,
            hint_text='记录今天吃了什么...',
            size_hint_y=0.15
        )
        layout.add_widget(self.food_input)
        
        layout.add_widget(Label(text='减肥心得:', font_size=44, size_hint_y=0.05))
        
        self.thoughts_input = TextInput(
            multiline=True,
            font_size=40,
            hint_text='记录今天的感受和心得...',
            size_hint_y=0.15
        )
        layout.add_widget(self.thoughts_input)
        
        save_btn = Button(
            text='保存日记',
            font_size=44,
            background_color=(0.2, 0.6, 0.8, 1),
            size_hint_y=0.08
        )
        save_btn.bind(on_press=self.save_diary)
        layout.add_widget(save_btn)
        
        self.diary_display = Label(
            text='最近日记记录：\n\n',
            font_size=38,
            text_size=(None, None),
            size_hint_y=0.5,
            halign='left',
            valign='top'
        )
        self.diary_display.bind(size=self.diary_display.setter('text_size'))
        
        scroll = ScrollView()
        scroll.add_widget(self.diary_display)
        layout.add_widget(scroll)
        
        Clock.schedule_once(self.load_today_diary, 0.1)
        Clock.schedule_once(self.update_diary_display, 0.1)
        
        return layout
    
    def create_data_tab(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        title = Label(text='数据管理', font_size=52, size_hint_y=0.1)
        layout.add_widget(title)
        
        center_container = BoxLayout(
            orientation='vertical',
            size_hint_y=0.9
        )
        
        center_container.add_widget(Widget(size_hint_y=0.2))
        
        button_container = BoxLayout(
            orientation='vertical',
            spacing=20,
            size_hint_y=0.6
        )
        
        export_btn = Button(
            text='导出数据(Excel)',
            font_size=44,
            background_color=(0.2, 0.6, 0.8, 1),
            size_hint=(None, None),
            size=(450, 140)
        )
        export_btn.bind(on_press=self.export_data)
        
        import_btn = Button(
            text='导入数据(Excel)',
            font_size=44,
            background_color=(0.2, 0.7, 0.3, 1),
            size_hint=(None, None),
            size=(450, 140)
        )
        import_btn.bind(on_press=self.import_data)
        
        file_location_btn = Button(
            text='查看文件位置',
            font_size=44,
            background_color=(0.8, 0.6, 0.2, 1),
            size_hint=(None, None),
            size=(450, 140)
        )
        file_location_btn.bind(on_press=self.show_file_location)
        
        instructions_btn = Button(
            text='使用说明',
            font_size=44,
            background_color=(0.8, 0.4, 0.2, 1),
            size_hint=(None, None),
            size=(450, 140)
        )
        instructions_btn.bind(on_press=self.show_instructions)
        
        export_container = BoxLayout(orientation='horizontal')
        export_container.add_widget(Widget(size_hint_x=0.5))
        export_container.add_widget(export_btn)
        export_container.add_widget(Widget(size_hint_x=0.5))
        
        import_container = BoxLayout(orientation='horizontal')
        import_container.add_widget(Widget(size_hint_x=0.5))
        import_container.add_widget(import_btn)
        import_container.add_widget(Widget(size_hint_x=0.5))
        
        file_location_container = BoxLayout(orientation='horizontal')
        file_location_container.add_widget(Widget(size_hint_x=0.5))
        file_location_container.add_widget(file_location_btn)
        file_location_container.add_widget(Widget(size_hint_x=0.5))
        
        instructions_container = BoxLayout(orientation='horizontal')
        instructions_container.add_widget(Widget(size_hint_x=0.5))
        instructions_container.add_widget(instructions_btn)
        instructions_container.add_widget(Widget(size_hint_x=0.5))
        
        button_container.add_widget(export_container)
        button_container.add_widget(import_container)
        button_container.add_widget(file_location_container)
        button_container.add_widget(instructions_container)
        
        center_container.add_widget(button_container)
        center_container.add_widget(Widget(size_hint_y=0.2))
        
        layout.add_widget(center_container)
        
        return layout
    
    def record_weight(self, instance):
            if not self.db:
                self.show_popup("错误", "数据库未初始化，请重启应用")
                return
                
            weight_text = self.weight_input.text
            try:
                weight = float(weight_text)
                if 20 <= weight <= 400:
                    current_date = format_date(date.today())
                    weight_type = 'morning' if self.time_spinner.text == '早晨' else 'evening'
                    
                    if self.db.add_weight_record(current_date, weight_type, weight):
                        self.weight_input.text = ""
                        self.update_records_display()
                        self.update_statistics()
                        self.update_chart()
                        self.show_popup("成功", f"{self.time_spinner.text}体重记录成功！")
                    else:
                        self.show_popup("错误", "体重记录失败，请重试")
                else:
                    self.show_popup("错误", "体重必须在20-400斤之间")
            except ValueError:
                self.show_popup("错误", "请输入有效的数字")
    
    def update_records_display(self, dt=None):
        if not self.db:
            return
        records = self.db.get_recent_records(7)
        display_text = "最近体重记录：\n\n"
        
        for record in records:
            date_str, weight_type, weight = record
            weight_type_display = "早晨" if weight_type == "morning" else "晚上"
            display_text += f"{date_str} {weight_type_display}: {weight}斤\n"
        
        self.records_label.text = display_text
    
    def update_statistics(self, instance=None):
        if not self.db:
            return
        stats = self.db.get_weight_statistics()
        
        if stats:
            self.initial_weight.text = f"初始体重: {stats['initial_weight']}斤"
            self.lightest_weight.text = f"最轻体重: {stats['lightest_weight']}斤"
            self.heaviest_weight.text = f"最重体重: {stats['heaviest_weight']}斤"
            self.average_weight.text = f"平均体重: {stats['average_weight']:.1f}斤"
            self.weight_diff.text = f"体重差值: {stats['weight_difference']:.1f}斤"
        else:
            self.initial_weight.text = "初始体重: 暂无数据"
            self.lightest_weight.text = "最轻体重: 暂无数据"
            self.heaviest_weight.text = "最重体重: 暂无数据"
            self.average_weight.text = "平均体重: 暂无数据"
            self.weight_diff.text = "体重差值: 暂无数据"
    
    def update_chart(self, instance=None):
        range_text = self.chart_range_spinner.text
        if range_text == '最近7天':
            days = 7
        elif range_text == '最近30天':
            days = 30
        else:
            days = 365
        
        chart_data = self.db.get_chart_data(days)
        
        chart_type = self.chart_type_spinner.text
        if chart_type == '早晨体重':
            data_points = chart_data['morning_weights']
            labels = chart_data['labels']
            self.chart.chart_title = "早晨体重趋势图"
        elif chart_type == '晚上体重':
            data_points = chart_data['evening_weights']
            labels = chart_data['labels']
            self.chart.chart_title = "晚上体重趋势图"
        else:
            data_points = chart_data['morning_weights'] + chart_data['evening_weights']
            labels = chart_data['labels'] + [f"{label}(晚)" for label in chart_data['labels']]
            self.chart.chart_title = "全部体重趋势图"
        
        self.chart.set_data(data_points, labels)
    
    def on_chart_type_change(self, spinner, text):
        self.update_chart()
    
    def on_chart_range_change(self, spinner, text):
        self.update_chart()
    
    def load_today_diary(self, dt=None):
        today_entry = self.db.get_today_diary_entry()
        if today_entry:
            self.food_input.text = today_entry['food'] or ""
            self.thoughts_input.text = today_entry['thoughts'] or ""
    
    def save_diary(self, instance):
        if not self.db:
            self.show_popup("错误", "数据库未初始化，请重启应用")
            return
        food_text = self.food_input.text
        thoughts_text = self.thoughts_input.text
        current_date = format_date(date.today())
        
        if self.db.add_diary_entry(current_date, food_text, thoughts_text):
            self.update_diary_display()
            self.show_popup("成功", "日记保存成功！")
        else:
            self.show_popup("错误", "日记保存失败，请重试")
    
    def update_diary_display(self, dt=None):
        entries = self.db.get_recent_diary_entries(10)
        diary_text = "最近日记记录：\n\n"
        
        for entry in entries:
            date_str, food, thoughts = entry
            food = food or "无记录"
            thoughts = thoughts or "无记录"
            diary_text += f"日期: {date_str}\n"
            diary_text += f"饮食: {food}\n"
            diary_text += f"心得: {thoughts}\n"
            diary_text += "-" * 30 + "\n"
        
        self.diary_display.text = diary_text
    
    def export_data(self, instance):
        if not self.db:
            self.show_popup("错误", "数据库未初始化，请重启应用")
            return
        
        # 检查必要的库是否可用
        if pd is None:
            self.show_popup("导出失败", "系统缺少pandas库，无法导出数据")
            return
        
        if not openpyxl_available:
            self.show_popup("导出失败", "系统缺少openpyxl库，无法导出Excel文件")
            return
            
        try:
            # 获取数据
            weight_records = self.db.get_all_records()
            diary_entries = self.db.get_all_diary_entries()
            
            # 数据计数
            weight_count = len(weight_records) if weight_records else 0
            diary_count = len(diary_entries) if diary_entries else 0
            
            # 验证是否有数据可导出
            if weight_count == 0 and diary_count == 0:
                self.show_popup("导出失败", "没有数据可导出")
                return
            
            # 处理体重记录数据
            weight_data = []
            if weight_records:
                for record in weight_records:
                    try:
                        # 确保记录格式正确
                        if len(record) >= 3:
                            date_str = str(record[0])  # 日期是第一个字段
                            weight_type_en = str(record[1])  # 时间类型是第二个字段
                            
                            # 转换时间类型为中文
                            weight_type_cn = "早晨" if weight_type_en.lower() == "morning" else "晚上"
                            
                            # 验证体重数值
                            try:
                                weight = float(record[2])
                                # 验证体重范围
                                if 20 <= weight <= 400:
                                    weight_data.append([date_str, weight_type_cn, weight])
                                else:
                                    Logger.warning(f"跳过异常体重值: {weight} 斤")
                            except (ValueError, TypeError):
                                Logger.warning(f"跳过无效体重值: {record[2]}")
                                continue
                    except Exception as e:
                        Logger.warning(f"跳过无效的体重记录: {record}, 错误: {str(e)}")
                        continue
            
            # 处理日记数据
            diary_data = []
            if diary_entries:
                for entry in diary_entries:
                    try:
                        # 确保记录格式正确
                        if len(entry) >= 3:
                            date_str = str(entry[0])  # 日期是第一个字段
                            food = str(entry[1]) if entry[1] is not None else ''
                            thoughts = str(entry[2]) if entry[2] is not None else ''
                            diary_data.append([date_str, food, thoughts])
                    except Exception as e:
                        Logger.warning(f"跳过无效的日记记录: {entry}, 错误: {str(e)}")
                        continue
            
            # 创建DataFrame
            weight_df = pd.DataFrame(weight_data, columns=['日期', '时间类型', '体重(斤)']) if weight_data else pd.DataFrame(columns=['日期', '时间类型', '体重(斤)'])
            diary_df = pd.DataFrame(diary_data, columns=['日期', '饮食记录', '减肥心得']) if diary_data else pd.DataFrame(columns=['日期', '饮食记录', '减肥心得'])
            
            # 获取并验证导出路径
            export_path = self.db.get_export_path("weight_data_export.xlsx")
            
            # 确保目录存在并可写
            export_dir = os.path.dirname(export_path)
            if not os.path.exists(export_dir):
                try:
                    os.makedirs(export_dir, exist_ok=True)
                except Exception as e:
                    self.show_popup("导出失败", f"无法创建导出目录: {str(e)}")
                    return
            
            if not os.access(export_dir, os.W_OK):
                self.show_popup("导出失败", f"无法写入导出目录，请检查权限: {export_dir}")
                return
            
            # 写入Excel文件，使用mode='w'确保完全覆盖
            try:
                # 添加对Excel文件扩展名的验证
                if not export_path.lower().endswith('.xlsx'):
                    export_path += '.xlsx'
                    Logger.warning(f"修正了导出文件扩展名: {export_path}")
                
                with pd.ExcelWriter(export_path, engine='openpyxl', mode='w') as writer:
                    # 即使没有数据也创建空的工作表，确保结构一致性
                    # 创建体重记录表
                    weight_df.to_excel(writer, sheet_name='体重记录', index=False)
                    worksheet = writer.sheets['体重记录']
                    # 优化列宽
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        try:
                            for cell in column:
                                try:
                                    if cell.value:
                                        max_length = max(max_length, len(str(cell.value)))
                                except:
                                    pass
                            adjusted_width = min(max_length + 2, 50)
                            worksheet.column_dimensions[column_letter].width = adjusted_width
                        except Exception as col_error:
                            Logger.warning(f"优化体重记录列宽时出错: {column_letter}, 错误: {str(col_error)}")
                    
                    # 创建减肥日记表
                    diary_df.to_excel(writer, sheet_name='减肥日记', index=False)
                    worksheet = writer.sheets['减肥日记']
                    # 优化列宽
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        try:
                            for cell in column:
                                try:
                                    if cell.value:
                                        max_length = max(max_length, len(str(cell.value)))
                                except:
                                    pass
                            adjusted_width = min(max_length + 2, 80)  # 为文本内容设置更大的宽度
                            worksheet.column_dimensions[column_letter].width = adjusted_width
                        except Exception as col_error:
                            Logger.warning(f"优化日记记录列宽时出错: {column_letter}, 错误: {str(col_error)}")
            except PermissionError:
                Logger.error("没有写入权限")
                self.show_popup("导出失败", f"没有写入权限: {export_path}\n请检查文件是否被其他程序占用")
                return
            except FileNotFoundError:
                Logger.error("文件路径无效")
                self.show_popup("导出失败", f"文件路径无效或无法访问: {export_path}")
                return
            except Exception as e:
                Logger.error(f"Excel写入错误: {str(e)}")
                self.show_popup("导出失败", f"创建Excel文件时出错: {str(e)}")
                return
            
            # 验证文件是否成功创建
            if os.path.exists(export_path) and os.path.getsize(export_path) > 0:
                file_size = os.path.getsize(export_path) / 1024  # KB
                current_time = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
                
                # 尝试打开文件
                try:
                    if sys.platform == 'win32':
                        os.startfile(export_path)
                    elif sys.platform == 'darwin':
                        subprocess.call(['open', export_path])
                    elif sys.platform.startswith('linux'):
                        subprocess.call(['xdg-open', export_path])
                    
                    message = f"数据已成功导出！\n\n"
                    message += f"导出路径: {export_path}\n"
                    message += f"文件大小: {file_size:.2f} KB\n"
                    message += f"导出时间: {current_time}\n"
                    message += f"体重记录: {len(weight_data)} 条\n"
                    message += f"日记记录: {len(diary_data)} 条\n\n"
                    message += "Excel文件包含的工作表:\n"
                    if not weight_df.empty:
                        message += "1. 体重记录 - 包含所有体重数据\n"
                    if not diary_df.empty:
                        message += "2. 减肥日记 - 包含所有日记数据\n"
                    message += "\n文件正在打开..."
                    self.show_popup("导出成功", message)
                except Exception as e:
                    message = f"数据已成功导出！\n\n"
                    message += f"导出路径: {export_path}\n"
                    message += f"文件大小: {file_size:.2f} KB\n"
                    message += f"导出时间: {current_time}\n"
                    message += f"体重记录: {len(weight_data)} 条\n"
                    message += f"日记记录: {len(diary_data)} 条\n\n"
                    message += "Excel文件包含的工作表:\n"
                    if not weight_df.empty:
                        message += "1. 体重记录 - 包含所有体重数据\n"
                    if not diary_df.empty:
                        message += "2. 减肥日记 - 包含所有日记数据\n"
                    message += f"\n但无法自动打开文件: {str(e)}\n"
                    message += "请手动打开导出文件查看数据。"
                    self.show_popup("导出成功", message)
            else:
                self.show_popup("导出失败", "文件创建失败或为空文件")
                
        except Exception as e:
            Logger.error(f"导出数据异常: {str(e)}")
            self.show_popup("导出失败", f"发生意外错误: {str(e)}")
    
    def show_file_location(self, instance):
        """显示文件位置信息"""
        db_path = self.db.db_path
        export_path = self.db.get_export_path("weight_data_export.xlsx")
        
        message = "文件位置信息:\n\n"
        message += f"数据库文件: {db_path}\n"
        message += f"导出文件: {export_path}\n\n"
        
        if os.path.exists(db_path):
            db_size = os.path.getsize(db_path)
            message += f"数据库状态: 已存在 ({db_size} 字节)\n"
        else:
            message += "数据库状态: 尚未创建\n"
        
        if os.path.exists(export_path):
            export_size = os.path.getsize(export_path)
            mod_time = datetime.fromtimestamp(os.path.getmtime(export_path))
            message += f"导出文件状态: 已存在 ({export_size} 字节)\n"
            message += f"最后修改: {mod_time.strftime('%Y/%m/%d %H:%M:%S')}\n"
        else:
            message += "导出文件状态: 尚未导出\n"
        
        message += "\n在Android设备上查找文件的方法:\n"
        message += "1. 使用文件管理器应用\n"
        message += "2. 查找应用数据目录\n"
        message += "3. 或者连接电脑通过USB传输文件查看"
        
        self.show_popup("文件位置", message)
    
    def import_data(self, instance):
        Logger.info("开始导入数据操作")
        
        # 检查数据库初始化
        if not self.db:
            Logger.error("导入失败: 数据库未初始化")
            self.show_popup("错误", "数据库未初始化，请重启应用")
            return
        
        # 检查必要的库是否可用
        if pd is None:
            Logger.error("导入失败: 系统缺少pandas库")
            self.show_popup("导入失败", "系统缺少pandas库，无法导入数据")
            return
        
        if not openpyxl_available:
            Logger.error("导入失败: 系统缺少openpyxl库")
            self.show_popup("导入失败", "系统缺少openpyxl库，无法导入Excel文件")
            return
        
        try:
            # 获取导入路径
            import_path = self.db.get_export_path("weight_data_export.xlsx")
            Logger.info(f"尝试导入文件: {import_path}")
            
            if os.path.exists(import_path):
                # 添加文件存在性和可读性检查
                try:
                    # 首先验证文件是否可读
                    if os.access(import_path, os.R_OK):
                        # 获取文件信息
                        file_size = os.path.getsize(import_path) / 1024  # KB
                        Logger.info(f"文件存在且可读，大小: {file_size:.2f} KB")
                        
                        # 读取Excel文件
                        try:
                            # 首先检查Excel文件格式
                            if not import_path.lower().endswith('.xlsx'):
                                raise ValueError("不支持的文件格式，请使用.xlsx格式的Excel文件")
                            
                            # 检查文件是否真的是Excel文件（基本检查）
                            with open(import_path, 'rb') as f:
                                header = f.read(8)
                            # Excel文件的魔术数字检查
                            if header != b'PK\x03\x04' and header != b'PK\x05\x06' and header != b'PK\x07\x08':
                                raise ValueError("文件不是有效的Excel文件")
                            
                            # 读取体重记录
                            try:
                                weight_df = pd.read_excel(import_path, sheet_name='体重记录')
                                Logger.info("成功读取体重记录表")
                            except KeyError:
                                weight_df = pd.DataFrame()  # 创建空DataFrame
                                Logger.warning("Excel文件中未找到体重记录表")
                            except Exception as weight_error:
                                weight_df = pd.DataFrame()
                                Logger.error(f"读取体重记录表时出错: {str(weight_error)}")
                            
                            # 读取日记记录
                            try:
                                diary_df = pd.read_excel(import_path, sheet_name='减肥日记')
                                Logger.info("成功读取减肥日记表")
                            except KeyError:
                                diary_df = pd.DataFrame()  # 创建空DataFrame
                                Logger.warning("Excel文件中未找到减肥日记表")
                            except Exception as diary_error:
                                diary_df = pd.DataFrame()
                                Logger.error(f"读取减肥日记表时出错: {str(diary_error)}")
                        except ValueError as ve:
                            Logger.error(f"文件验证错误: {str(ve)}")
                            self.show_popup("导入失败", f"文件格式错误: {str(ve)}")
                            return
                        
                        # 清理和验证体重记录数据
                        validated_weight_records = []
                        if weight_df is not None and not weight_df.empty:
                            # 验证列是否存在
                            required_columns = ['日期', '时间类型', '体重(斤)']
                            if all(col in weight_df.columns for col in required_columns):
                                Logger.info(f"开始验证体重记录，共 {len(weight_df)} 行数据")
                                
                                for _, row in weight_df.iterrows():
                                    try:
                                        # 验证日期格式
                                        date_str = str(row['日期']).strip()
                                        # 检查时间类型
                                        weight_type = str(row['时间类型']).strip()
                                        if weight_type not in ['早晨', '晚上']:
                                            Logger.warning(f"跳过无效的时间类型: {weight_type}")
                                            continue
                                        # 验证体重是否为数字
                                        weight = float(row['体重(斤)'])
                                        # 验证体重范围
                                        if 20 <= weight <= 400:
                                            validated_weight_records.append([date_str, weight_type, weight])
                                        else:
                                            Logger.warning(f"跳过超出范围的体重值: {weight}")
                                    except (ValueError, TypeError, AttributeError) as e:
                                        Logger.warning(f"跳过无效的体重记录行: {str(e)}")
                                        continue  # 跳过无效行
                                
                                Logger.info(f"体重记录验证完成，有效记录: {len(validated_weight_records)} 条")
                            else:
                                missing_cols = [col for col in required_columns if col not in weight_df.columns]
                                Logger.error(f"Excel文件格式错误，缺少必要的列: {', '.join(missing_cols)}")
                                self.show_popup("导入失败", f"Excel文件格式错误，缺少必要的列: {', '.join(missing_cols)}")
                                return
                        else:
                            Logger.info("Excel文件中没有体重记录数据")
                        
                        # 清理日记数据
                        validated_diary_entries = []
                        if diary_df is not None and not diary_df.empty:
                            diary_required_columns = ['日期', '饮食记录', '减肥心得']
                            if all(col in diary_df.columns for col in diary_required_columns):
                                Logger.info(f"开始验证日记记录，共 {len(diary_df)} 行数据")
                                
                                for _, row in diary_df.iterrows():
                                    try:
                                        date_str = str(row['日期']).strip()
                                        food = str(row['饮食记录']) if pd.notna(row['饮食记录']) else ''
                                        thoughts = str(row['减肥心得']) if pd.notna(row['减肥心得']) else ''
                                        validated_diary_entries.append([date_str, food, thoughts])
                                    except (ValueError, TypeError, AttributeError) as e:
                                        Logger.warning(f"跳过无效的日记记录行: {str(e)}")
                                        continue  # 跳过无效行
                                
                                Logger.info(f"日记记录验证完成，有效记录: {len(validated_diary_entries)} 条")
                            else:
                                missing_cols = [col for col in diary_required_columns if col not in diary_df.columns]
                                Logger.error(f"Excel文件格式错误，缺少必要的日记列: {', '.join(missing_cols)}")
                                self.show_popup("导入失败", f"Excel文件格式错误，缺少必要的日记列: {', '.join(missing_cols)}")
                                return
                        else:
                            Logger.info("Excel文件中没有日记记录数据")
                        
                        # 验证是否有数据要导入
                        if not validated_weight_records and not validated_diary_entries:
                            Logger.warning("没有有效的数据可导入")
                            self.show_popup("导入警告", "Excel文件中没有找到有效的数据记录")
                            return
                        
                        # 构建导入数据
                        data = {
                            'weight_records': validated_weight_records,
                            'diary_entries': validated_diary_entries
                        }
                        
                        # 调用数据库导入方法并处理返回值
                        Logger.info("开始导入数据到数据库")
                        success, errors = self.db.import_data(data)
                        
                        if success:
                            # 导入成功
                            Logger.info("数据导入数据库成功")
                            # 显示导入统计信息
                            message = f"Excel数据导入成功！\n\n"
                            message += f"导入体重记录: {len(validated_weight_records)} 条\n"
                            message += f"导入日记记录: {len(validated_diary_entries)} 条\n"
                            if errors:
                                message += f"\n注意事项: {len(errors)} 条记录有警告\n"
                                for i, error in enumerate(errors[:5], 1):  # 只显示前5条警告
                                    message += f"- {error}\n"
                                if len(errors) > 5:
                                    message += f"- ...等{len(errors) - 5}条警告\n"
                            message += "\n数据已更新到系统中。"
                            self.show_popup("导入成功", message)
                            
                            # 更新显示
                            try:
                                self.update_records_display()
                                self.update_statistics()
                                self.update_chart()
                                self.update_diary_display()
                                self.load_today_diary()
                                Logger.info("成功更新UI显示")
                            except Exception as ui_error:
                                Logger.error(f"更新UI显示时出错: {str(ui_error)}")
                                self.show_popup("警告", "数据导入成功，但更新显示时出错，请手动刷新")
                        else:
                            # 导入失败
                            Logger.error("数据导入数据库失败")
                            error_message = "数据导入数据库失败\n\n"
                            if errors:
                                error_message += "错误详情:\n"
                                for i, error in enumerate(errors[:5], 1):  # 只显示前5条错误
                                    error_message += f"- {error}\n"
                                if len(errors) > 5:
                                    error_message += f"- ...等{len(errors) - 5}条错误\n"
                            else:
                                error_message += "请查看日志获取详细信息"
                            self.show_popup("导入失败", error_message)
                    else:
                        Logger.error(f"无法读取文件，请检查文件权限: {import_path}")
                        self.show_popup("导入失败", f"无法读取文件，请检查文件权限: {import_path}")
                except ValueError as ve:
                    Logger.error(f"Excel文件格式错误: {str(ve)}")
                    self.show_popup("导入失败", f"Excel文件格式错误: {str(ve)}")
                except pd.errors.EmptyDataError:
                    Logger.error("Excel文件为空或格式不正确")
                    self.show_popup("导入失败", "Excel文件为空或格式不正确")
                except pd.errors.ParserError:
                    Logger.error("Excel文件格式错误，无法解析")
                    self.show_popup("导入失败", "Excel文件格式错误，无法解析")
                except Exception as e:
                    Logger.error(f"读取Excel文件时出错: {str(e)}")
                    self.show_popup("导入失败", f"读取Excel文件时出错: {str(e)}")
            else:
                Logger.error(f"未找到导入文件: {import_path}")
                self.show_popup("导入失败", f"未找到导入文件:\n{import_path}\n\n请先导出数据再尝试导入。")
        except Exception as e:
            Logger.error(f"导入数据异常: {str(e)}")
            self.show_popup("导入失败", f"发生意外错误: {str(e)}")
    
    def show_instructions(self, instance):
        instructions = """
使用说明：

功能一：记录体重
- 早晚各记录一次体重
- 体重范围：20-400斤
- 选择时间类型后输入体重

功能二：体重统计
- 查看初始体重、最轻体重、最重体重
- 计算平均体重和体重差值
- 数据自动更新

功能三：趋势图表
- 查看体重变化趋势图
- 可选择早晨/晚上/全部体重
- 可选择最近7天/30天/全部数据
- 图表自动生成和更新

功能四：减肥日记
- 记录每日饮食内容
- 记录减肥心得和感受
- 支持查看历史记录
- 当天日记可以随时修改

功能五：数据管理
- 导出数据到Excel文件
- 从Excel文件导入数据
- 查看导出文件位置
- 数据备份和恢复

注意：请定期备份数据！

温馨提示：
1. 建议每天早晚各记录一次体重
2. 坚持记录饮食和心得有助于减肥成功
3. 定期查看趋势图了解减肥进展
4. 重要数据请及时备份到安全位置

祝您减肥成功，健康每一天！
"""
        content = BoxLayout(orientation='vertical', spacing=10)
        
        title_label = Label(
            text="使用说明", 
            font_size=48,
            size_hint_y=0.1
        )
        content.add_widget(title_label)
        
        scroll = ScrollView()
        instructions_label = Label(
            text=instructions,
            font_size=40,
            text_size=(550, None),
            size_hint_y=None,
            halign='left',
            valign='top'
        )
        instructions_label.bind(size=instructions_label.setter('text_size'))
        instructions_label.bind(texture_size=lambda instance, value: setattr(instructions_label, 'height', value[1]))
        scroll.add_widget(instructions_label)
        content.add_widget(scroll)
        
        ok_btn = Button(
            text='确定',
            font_size=44,
            size_hint_y=0.15
        )
        content.add_widget(ok_btn)
        
        popup = Popup(
            title='',
            content=content,
            size_hint=(0.9, 0.9)
        )
        
        ok_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', spacing=10)
        
        title_label = Label(
            text=title,
            font_size=46,
            size_hint_y=0.2
        )
        content.add_widget(title_label)
        
        scroll = ScrollView()
        message_label = Label(
            text=message,
            font_size=42,
            text_size=(450, None),
            size_hint_y=None,
            halign='center',
            valign='middle'
        )
        message_label.bind(size=message_label.setter('text_size'))
        message_label.bind(texture_size=lambda instance, value: setattr(message_label, 'height', value[1]))
        scroll.add_widget(message_label)
        content.add_widget(scroll)
        
        ok_btn = Button(
            text='确定',
            font_size=44,
            size_hint_y=0.2
        )
        content.add_widget(ok_btn)
        
        popup = Popup(
            title='',
            content=content,
            size_hint=(0.8, 0.7)
        )
        
        ok_btn.bind(on_press=popup.dismiss)
        popup.open()

if __name__ == '__main__':
    try:
        # 设置更详细的日志
        import logging
        from kivy.logger import Logger
        
        # 在Android上创建日志文件
        if IS_ANDROID:
            try:
                from android.storage import app_storage_path
                app_dir = app_storage_path()
                log_path = os.path.join(app_dir, "app_log.txt")
                log_dir = os.path.dirname(log_path)
                if not os.path.exists(log_dir):
                    os.makedirs(log_dir)
                
                # 添加文件处理器
                file_handler = logging.FileHandler(log_path)
                file_handler.setLevel(logging.INFO)
                Logger.addHandler(file_handler)
            except Exception as e:
                Logger.warning(f"无法创建日志文件: {str(e)}")
        
        Logger.info("App: 开始启动应用")
        # 确保WeightTrackerApp类已定义
        if 'WeightTrackerApp' in globals():
            WeightTrackerApp().run()
        else:
            raise NameError("WeightTrackerApp类未定义")
            
    except Exception as e:
        Logger.error(f"App: 应用启动失败 - {str(e)}")
        # 在Android上写入错误日志
        if IS_ANDROID:
            try:
                from android.storage import app_storage_path
                app_dir = app_storage_path()
                error_log_path = os.path.join(app_dir, "error_log.txt")
                with open(error_log_path, "w") as f:
                    f.write(f"应用启动失败: {str(e)}\n")
                    import traceback
                    f.write(traceback.format_exc())
            except:
                pass
