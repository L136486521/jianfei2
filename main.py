import sqlite3
import os
import json
import pandas as pd
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
from kivy.graphics import Color, Line, Rectangle, InstructionGroup
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.metrics import dp
import platform

# 检查当前平台
IS_ANDROID = platform.system() == "Linux" and "ANDROID_ARGUMENT" in os.environ

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
        self.bind(size=self._update_scroll_size)
        
    def _update_scroll_size(self, *args):
        """更新滚动区域大小"""
        if hasattr(self, 'parent_scroll') and self.parent_scroll:
            # 设置最小尺寸以确保可以滚动
            min_width = max(self.width, 800)
            min_height = max(self.height, 600)
            self.size_hint = (None, None)
            self.size = (min_width, min_height)
        
    def set_data(self, data_points, labels=None):
        """设置图表数据"""
        self.data_points = data_points
        self.labels = labels if labels else [str(i+1) for i in range(len(data_points))]
        
        if data_points:
            self.min_value = min(data_points)
            self.max_value = max(data_points)
            
            # 添加一些边距
            value_range = self.max_value - self.min_value
            if value_range > 0:
                self.min_value -= value_range * 0.1
                self.max_value += value_range * 0.1
            else:
                # 如果所有值都相同，设置一个合理的范围
                self.min_value -= 10
                self.max_value += 10
        else:
            self.min_value = 0
            self.max_value = 100
            
        self.draw_chart()
    
    def draw_chart(self):
        """绘制图表"""
        self.canvas.clear()
        
        with self.canvas:
            # 绘制背景
            Color(*self.background_color)
            Rectangle(pos=self.pos, size=self.size)
            
            if not self.data_points:
                # 没有数据时显示提示
                Color(*self.text_color)
                Rectangle(
                    pos=(self.center_x - 100, self.center_y - 15),
                    size=(200, 30)
                )
                return
            
            # 绘制网格和坐标轴
            self.draw_grid_and_axes()
            
            # 绘制数据线
            self.draw_data_line()
    
    def draw_grid_and_axes(self):
        """绘制网格和坐标轴"""
        # 计算边距
        margin_left = dp(80)
        margin_bottom = dp(60)
        margin_top = dp(50)
        margin_right = dp(40)
        
        chart_width = self.width - margin_left - margin_right
        chart_height = self.height - margin_bottom - margin_top
        
        # 绘制网格线
        Color(*self.grid_color)
        
        # 水平网格线
        num_h_lines = 5
        for i in range(num_h_lines + 1):
            y = margin_bottom + (chart_height / num_h_lines) * i
            Line(
                points=[margin_left, y, margin_left + chart_width, y],
                width=1
            )
            
            # 绘制Y轴刻度值
            value = self.max_value - (self.max_value - self.min_value) * (i / num_h_lines)
            Color(*self.text_color)
            Rectangle(
                pos=(margin_left - dp(50), y - dp(10)),
                size=(dp(45), dp(20))
            )
            # 这里应该使用Label来显示文本，但为了简化，我们使用矩形表示
            
        # 垂直网格线 (只显示部分标签避免拥挤)
        num_points = len(self.data_points)
        if num_points > 0:
            step = max(1, num_points // 5)  # 最多显示5个标签
            
            for i in range(0, num_points, step):
                if i < len(self.labels):
                    x = margin_left + (chart_width / max(1, (num_points - 1))) * i
                    Line(
                        points=[x, margin_bottom, x, margin_bottom + chart_height],
                        width=1
                    )
                    
                    # 绘制X轴标签
                    Color(*self.text_color)
                    Rectangle(
                        pos=(x - dp(20), margin_bottom - dp(30)),
                        size=(dp(40), dp(20))
                    )
                    # 这里应该使用Label来显示文本，但为了简化，我们使用矩形表示
        
        # 绘制坐标轴线
        Color(0, 0, 0, 1)
        Line(
            points=[margin_left, margin_bottom, margin_left, margin_bottom + chart_height],
            width=2
        )
        Line(
            points=[margin_left, margin_bottom, margin_left + chart_width, margin_bottom],
            width=2
        )
        
        # 绘制坐标轴标签
        Color(*self.text_color)
        # Y轴标签
        Rectangle(
            pos=(dp(10), self.center_y - dp(50)),
            size=(dp(100), dp(20))
        )
        # X轴标签
        Rectangle(
            pos=(self.center_x - dp(25), dp(10)),
            size=(dp(50), dp(20))
        )
        # 图表标题
        Rectangle(
            pos=(self.center_x - dp(50), self.height - dp(30)),
            size=(dp(100), dp(20))
        )
    
    def draw_data_line(self):
        """绘制数据线"""
        if not self.data_points:
            return
            
        # 计算边距
        margin_left = dp(80)
        margin_bottom = dp(60)
        margin_top = dp(50)
        margin_right = dp(40)
        
        chart_width = self.width - margin_left - margin_right
        chart_height = self.height - margin_bottom - margin_top
        
        # 计算数据点位置
        points = []
        num_points = len(self.data_points)
        
        for i, value in enumerate(self.data_points):
            # 修复：避免除零错误
            if num_points > 1:
                x = margin_left + (chart_width / (num_points - 1)) * i
            else:
                x = margin_left + chart_width * 0.5  # 只有一个点时放在中间
            
            # 修复：避免除零错误
            value_range = self.max_value - self.min_value
            if value_range > 0:
                y = margin_bottom + ((value - self.min_value) / value_range) * chart_height
            else:
                y = margin_bottom + chart_height * 0.5  # 如果值范围为零，放在中间
            
            points.extend([x, y])
        
        # 绘制数据线
        Color(*self.line_color)
        Line(points=points, width=2)
        
        # 绘制数据点
        for i, value in enumerate(self.data_points):
            # 修复：避免除零错误
            if num_points > 1:
                x = margin_left + (chart_width / (num_points - 1)) * i
            else:
                x = margin_left + chart_width * 0.5
            
            # 修复：避免除零错误
            value_range = self.max_value - self.min_value
            if value_range > 0:
                y = margin_bottom + ((value - self.min_value) / value_range) * chart_height
            else:
                y = margin_bottom + chart_height * 0.5
            
            Color(0.8, 0.2, 0.2, 1)
            Rectangle(pos=(x-3, y-3), size=(6, 6))
    
    def on_size(self, *args):
        """当组件大小改变时重绘图表"""
        self.draw_chart()

class WeightDatabase:
    def __init__(self, db_path=None):
        # 在Android上使用应用数据目录
        if IS_ANDROID:
            from kivy.app import App
            app = App.get_running_app()
            if app:
                self.db_path = os.path.join(app.user_data_dir, "weight_data.db")
            else:
                # 如果应用还没运行，使用默认路径
                self.db_path = "weight_data.db"
        else:
            self.db_path = db_path or "weight_data.db"
        
        Logger.info(f"Database: 数据库路径 - {self.db_path}")
        self.init_database()
    
    def init_database(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建体重记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS weight_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    weight_type TEXT NOT NULL,
                    weight REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建日记表
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
        except Exception as e:
            Logger.error(f"Database: 数据库初始化失败 - {str(e)}")
            # 尝试重新创建数据库连接
            try:
                # 如果连接失败，尝试使用内存数据库
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
        """获取数据库连接，确保表存在"""
        try:
            conn = sqlite3.connect(self.db_path)
            # 确保表存在
            cursor = conn.cursor()
            
            # 检查表是否存在，如果不存在则创建
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='weight_records'")
            if not cursor.fetchone():
                cursor.execute('''
                    CREATE TABLE weight_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        weight_type TEXT NOT NULL,
                        weight REAL NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='diary_entries'")
            if not cursor.fetchone():
                cursor.execute('''
                    CREATE TABLE diary_entries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        food TEXT,
                        thoughts TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
            
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
            
            # 检查是否已经存在当天的同类型记录
            cursor.execute('''
                SELECT id FROM weight_records 
                WHERE date = ? AND weight_type = ?
            ''', (date_str, weight_type))
            
            existing_record = cursor.fetchone()
            
            if existing_record:
                # 更新现有记录
                cursor.execute('''
                    UPDATE weight_records 
                    SET weight = ?, created_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (weight, existing_record[0]))
            else:
                # 插入新记录
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
    
    def add_diary_entry(self, date_str, food, thoughts):
        conn = self.get_connection()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            
            # 检查是否已经存在当天的日记
            cursor.execute('''
                SELECT id FROM diary_entries WHERE date = ?
            ''', (date_str,))
            
            existing_entry = cursor.fetchone()
            
            if existing_entry:
                # 更新现有日记
                cursor.execute('''
                    UPDATE diary_entries 
                    SET food = ?, thoughts = ?, created_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (food, thoughts, existing_entry[0]))
            else:
                # 插入新日记
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
            current_date = date.today().isoformat()
            
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
            return records
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
            return records
        except Exception as e:
            Logger.error(f"Database: 获取所有记录失败 - {str(e)}")
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
            return entries
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
            return entries
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
            
            # 获取最近指定天数的记录，按日期排序
            cursor.execute('''
                SELECT date, weight_type, weight 
                FROM weight_records 
                ORDER BY date ASC
            ''')
            
            all_records = cursor.fetchall()
            conn.close()
            
            # 处理数据，将同一天的早晨和晚上体重合并
            chart_data = {}
            labels = []
            
            for record in all_records:
                date_str, weight_type, weight = record
                
                if date_str not in chart_data:
                    chart_data[date_str] = {'morning': None, 'evening': None}
                    labels.append(date_str)
                
                chart_data[date_str][weight_type] = weight
            
            # 提取早晨体重数据，如果没有早晨体重则使用晚上体重
            morning_weights = []
            evening_weights = []
            valid_labels = []
            
            for date_str in labels[-days:]:  # 只取最近days天的数据
                morning_weight = chart_data[date_str]['morning']
                evening_weight = chart_data[date_str]['evening']
                
                # 优先使用早晨体重，如果没有则使用晚上体重
                if morning_weight is not None:
                    morning_weights.append(morning_weight)
                    valid_labels.append(date_str)
                elif evening_weight is not None:
                    morning_weights.append(evening_weight)
                    valid_labels.append(date_str)
                
                # 添加晚上体重
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
        conn = self.get_connection()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            
            # 清空现有数据
            cursor.execute('DELETE FROM weight_records')
            cursor.execute('DELETE FROM diary_entries')
            
            # 导入体重记录 - 将中文时间类型转换为英文
            for record in data.get('weight_records', []):
                date_str, weight_type_cn, weight = record
                # 将中文时间类型转换为英文
                weight_type_en = 'morning' if weight_type_cn == '早晨' else 'evening'
                cursor.execute('''
                    INSERT INTO weight_records (date, weight_type, weight)
                    VALUES (?, ?, ?)
                ''', (date_str, weight_type_en, weight))
            
            # 导入日记记录
            for entry in data.get('diary_entries', []):
                cursor.execute('''
                    INSERT INTO diary_entries (date, food, thoughts)
                    VALUES (?, ?, ?)
                ''', (entry[0], entry[1], entry[2]))
            
            conn.commit()
            conn.close()
            Logger.info("Database: 数据导入成功")
            return True
        except Exception as e:
            Logger.error(f"Database: 数据导入失败 - {str(e)}")
            try:
                conn.close()
            except:
                pass
            return False

class WeightTrackerApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 不在初始化时创建数据库，在build方法中创建
    
    def build(self):
        try:
            # 创建数据库实例
            self.db = WeightDatabase()
            
            # 创建主界面 - 标签放在底部，设置标签字体大小
            main_layout = TabbedPanel(tab_pos='bottom_mid')
            main_layout.do_default_tab = False
            # 设置标签页字体大小
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
            
            Logger.info("App: 应用初始化成功")
            return main_layout
        except Exception as e:
            Logger.error(f"App: 应用初始化失败 - {str(e)}")
            # 返回一个简单的错误界面
            layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
            layout.add_widget(Label(text='应用启动失败', font_size=52))
            layout.add_widget(Label(text=f'错误: {str(e)}', font_size=44))
            return layout
    
    def create_record_tab(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # 标题
        title = Label(text='记录体重', font_size=52, size_hint_y=0.1)
        layout.add_widget(title)
        
        # 选择时间 - 单独一行
        time_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1, spacing=15)
        time_layout.add_widget(Label(text='选择时间:', font_size=44))
        
        self.time_spinner = Spinner(
            text='早晨',
            values=('早晨', '晚上'),
            font_size=44,
            size_hint_x=0.7  # 设置时间选择器的宽度
        )
        time_layout.add_widget(self.time_spinner)
        layout.add_widget(time_layout)
        
        # 输入体重 - 单独一行
        weight_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1, spacing=15)
        weight_layout.add_widget(Label(text='体重(斤):', font_size=44))
        
        self.weight_input = TextInput(
            multiline=False,
            input_filter='float',
            font_size=44,
            hint_text='输入20-400之间的数字',
            size_hint_x=0.7  # 设置输入框与时间选择器相同的宽度
        )
        weight_layout.add_widget(self.weight_input)
        layout.add_widget(weight_layout)
        
        # 按钮
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1, spacing=15)
        
        record_btn = Button(
            text='记录体重',
            font_size=44,
            background_color=(0.2, 0.6, 0.8, 1)
        )
        record_btn.bind(on_press=self.record_weight)
        button_layout.add_widget(record_btn)
        
        layout.add_widget(button_layout)
        
        # 最近记录
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
        
        # 初始化显示
        Clock.schedule_once(self.update_records_display, 0.1)
        
        return layout
    
    def create_stats_tab(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # 标题
        title = Label(text='体重统计', font_size=52, size_hint_y=0.1)
        layout.add_widget(title)
        
        # 统计信息
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
        
        # 刷新按钮
        refresh_btn = Button(
            text='刷新统计',
            font_size=44,
            background_color=(0.2, 0.7, 0.3, 1),
            size_hint_y=0.1
        )
        refresh_btn.bind(on_press=self.update_statistics)
        layout.add_widget(refresh_btn)
        
        # 初始化显示
        Clock.schedule_once(self.update_statistics, 0.1)
        
        return layout
    
    def create_chart_tab(self):
        layout = BoxLayout(orientation='vertical', padding=15, spacing=15)
        
        # 标题
        title = Label(text='体重趋势图', font_size=52, size_hint_y=0.1)
        layout.add_widget(title)
        
        # 图表类型选择
        chart_type_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1, spacing=15)
        chart_type_layout.add_widget(Label(text='图表类型:', font_size=42))
        
        self.chart_type_spinner = Spinner(
            text='早晨体重',
            values=('早晨体重', '晚上体重', '全部体重'),
            font_size=42
        )
        self.chart_type_spinner.bind(text=self.on_chart_type_change)
        chart_type_layout.add_widget(self.chart_type_spinner)
        
        # 时间范围选择
        chart_type_layout.add_widget(Label(text='时间范围:', font_size=42))
        
        self.chart_range_spinner = Spinner(
            text='最近7天',
            values=('最近7天', '最近30天', '全部数据'),
            font_size=42
        )
        self.chart_range_spinner.bind(text=self.on_chart_range_change)
        chart_type_layout.add_widget(self.chart_range_spinner)
        
        layout.add_widget(chart_type_layout)
        
        # 图表容器 - 使用ScrollView包装图表
        chart_scroll = ScrollView(size_hint_y=0.7, do_scroll_x=True, do_scroll_y=True)
        chart_container = BoxLayout(orientation='vertical', size_hint=(None, None))
        chart_container.bind(minimum_height=chart_container.setter('height'))
        chart_container.bind(minimum_width=chart_container.setter('width'))
        
        self.chart = SimpleChart()
        self.chart.size_hint = (None, None)
        self.chart.size = (800, 600)  # 设置固定大小以便滚动
        self.chart.parent_scroll = chart_scroll
        
        chart_container.add_widget(self.chart)
        chart_scroll.add_widget(chart_container)
        layout.add_widget(chart_scroll)
        
        # 刷新按钮
        refresh_btn = Button(
            text='刷新图表',
            font_size=44,
            background_color=(0.2, 0.7, 0.3, 1),
            size_hint_y=0.1
        )
        refresh_btn.bind(on_press=self.update_chart)
        layout.add_widget(refresh_btn)
        
        # 初始化图表
        Clock.schedule_once(self.update_chart, 0.1)
        
        return layout
    
    def create_diary_tab(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # 标题
        title = Label(text='减肥日记', font_size=52, size_hint_y=0.05)
        layout.add_widget(title)
        
        # 今日饮食
        layout.add_widget(Label(text='今日饮食:', font_size=44, size_hint_y=0.05))
        
        self.food_input = TextInput(
            multiline=True,
            font_size=40,
            hint_text='记录今天吃了什么...',
            size_hint_y=0.15
        )
        layout.add_widget(self.food_input)
        
        # 减肥心得
        layout.add_widget(Label(text='减肥心得:', font_size=44, size_hint_y=0.05))
        
        self.thoughts_input = TextInput(
            multiline=True,
            font_size=40,
            hint_text='记录今天的感受和心得...',
            size_hint_y=0.15
        )
        layout.add_widget(self.thoughts_input)
        
        # 保存按钮
        save_btn = Button(
            text='保存日记',
            font_size=44,
            background_color=(0.2, 0.6, 0.8, 1),
            size_hint_y=0.08
        )
        save_btn.bind(on_press=self.save_diary)
        layout.add_widget(save_btn)
        
        # 日记显示
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
        
        # 初始化显示 - 加载今天的日记
        Clock.schedule_once(self.load_today_diary, 0.1)
        Clock.schedule_once(self.update_diary_display, 0.1)
        
        return layout
    
    def create_data_tab(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # 标题
        title = Label(text='数据管理', font_size=52, size_hint_y=0.1)
        layout.add_widget(title)
        
        # 创建一个容器来使按钮在页面中完全居中
        center_container = BoxLayout(
            orientation='vertical',
            size_hint_y=0.9
        )
        
        # 顶部占位空间
        center_container.add_widget(Widget(size_hint_y=0.2))
        
        # 按钮容器 - 垂直排列按钮
        button_container = BoxLayout(
            orientation='vertical',
            spacing=20,
            size_hint_y=0.6
        )
        
        # 导出按钮 - 固定大小
        export_btn = Button(
            text='导出数据(Excel)',
            font_size=44,
            background_color=(0.2, 0.6, 0.8, 1),
            size_hint=(None, None),
            size=(450, 140)
        )
        export_btn.bind(on_press=self.export_data)
        
        # 导入按钮 - 固定大小
        import_btn = Button(
            text='导入数据(Excel)',
            font_size=44,
            background_color=(0.2, 0.7, 0.3, 1),
            size_hint=(None, None),
            size=(450, 140)
        )
        import_btn.bind(on_press=self.import_data)
        
        # 查看导出文件位置按钮 - 固定大小
        file_location_btn = Button(
            text='查看导出文件位置',
            font_size=44,
            background_color=(0.8, 0.6, 0.2, 1),
            size_hint=(None, None),
            size=(450, 140)
        )
        file_location_btn.bind(on_press=self.show_file_location)
        
        # 使用说明按钮 - 固定大小
        instructions_btn = Button(
            text='使用说明',
            font_size=44,
            background_color=(0.8, 0.4, 0.2, 1),
            size_hint=(None, None),
            size=(450, 140)
        )
        instructions_btn.bind(on_press=self.show_instructions)
        
        # 创建一个水平容器来使按钮水平居中
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
        
        # 将按钮添加到按钮容器
        button_container.add_widget(export_container)
        button_container.add_widget(import_container)
        button_container.add_widget(file_location_container)
        button_container.add_widget(instructions_container)
        
        # 将按钮容器添加到居中容器
        center_container.add_widget(button_container)
        
        # 底部占位空间
        center_container.add_widget(Widget(size_hint_y=0.2))
        
        # 将居中容器添加到主布局
        layout.add_widget(center_container)
        
        return layout
    
    def record_weight(self, instance):
        weight_text = self.weight_input.text
        try:
            weight = float(weight_text)
            if 20 <= weight <= 400:
                current_date = date.today().isoformat()
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
        records = self.db.get_recent_records(7)
        display_text = "最近体重记录：\n\n"
        
        for record in records:
            date_str = record[0]
            weight_type = "早晨" if record[1] == "morning" else "晚上"
            weight = record[2]
            display_text += f"{date_str} {weight_type}: {weight}斤\n"
        
        self.records_label.text = display_text
    
    def update_statistics(self, instance=None):
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
        """更新图表数据"""
        # 根据选择的时间范围确定天数
        range_text = self.chart_range_spinner.text
        if range_text == '最近7天':
            days = 7
        elif range_text == '最近30天':
            days = 30
        else:  # 全部数据
            days = 365  # 假设一年内的数据
        
        chart_data = self.db.get_chart_data(days)
        
        # 根据选择的图表类型显示相应数据
        chart_type = self.chart_type_spinner.text
        if chart_type == '早晨体重':
            data_points = chart_data['morning_weights']
            labels = chart_data['labels']
            self.chart.chart_title = "早晨体重趋势图"
        elif chart_type == '晚上体重':
            data_points = chart_data['evening_weights']
            labels = chart_data['labels']
            self.chart.chart_title = "晚上体重趋势图"
        else:  # 全部体重
            # 合并早晨和晚上体重
            data_points = chart_data['morning_weights'] + chart_data['evening_weights']
            # 创建对应的标签
            labels = chart_data['labels'] + [f"{label}(晚)" for label in chart_data['labels']]
            self.chart.chart_title = "全部体重趋势图"
        
        self.chart.set_data(data_points, labels)
    
    def on_chart_type_change(self, spinner, text):
        """图表类型改变时更新图表"""
        self.update_chart()
    
    def on_chart_range_change(self, spinner, text):
        """时间范围改变时更新图表"""
        self.update_chart()
    
    def load_today_diary(self, dt=None):
        """加载今天的日记"""
        today_entry = self.db.get_today_diary_entry()
        if today_entry:
            self.food_input.text = today_entry['food'] or ""
            self.thoughts_input.text = today_entry['thoughts'] or ""
    
    def save_diary(self, instance):
        food_text = self.food_input.text
        thoughts_text = self.thoughts_input.text
        current_date = date.today().isoformat()
        
        if self.db.add_diary_entry(current_date, food_text, thoughts_text):
            self.update_diary_display()
            self.show_popup("成功", "日记保存成功！")
        else:
            self.show_popup("错误", "日记保存失败，请重试")
    
    def update_diary_display(self, dt=None):
        entries = self.db.get_recent_diary_entries(10)
        diary_text = "最近日记记录：\n\n"
        
        for entry in entries:
            date_str = entry[0]
            food = entry[1] or "无记录"
            thoughts = entry[2] or "无记录"
            diary_text += f"日期: {date_str}\n"
            diary_text += f"饮食: {food}\n"
            diary_text += f"心得: {thoughts}\n"
            diary_text += "-" * 30 + "\n"
        
        self.diary_display.text = diary_text
    
    def export_data(self, instance):
        try:
            # 获取所有数据
            weight_records = self.db.get_all_records()
            diary_entries = self.db.get_all_diary_entries()
            
            # 创建DataFrame - 将英文时间类型转换为中文
            weight_data = []
            for record in weight_records:
                date_str, weight_type_en, weight = record
                weight_type_cn = "早晨" if weight_type_en == "morning" else "晚上"
                weight_data.append([date_str, weight_type_cn, weight])
            
            weight_df = pd.DataFrame(weight_data, columns=['日期', '时间类型', '体重(斤)'])
            diary_df = pd.DataFrame(diary_entries, columns=['日期', '饮食记录', '减肥心得'])
            
            # 在Android上，我们可以使用应用的数据目录
            if IS_ANDROID:
                base_dir = self.user_data_dir
            else:
                base_dir = os.path.expanduser("~")
            
            export_path = os.path.join(base_dir, "weight_data_export.xlsx")
            
            # 使用ExcelWriter创建包含多个工作表的Excel文件
            with pd.ExcelWriter(export_path, engine='openpyxl') as writer:
                weight_df.to_excel(writer, sheet_name='体重记录', index=False)
                diary_df.to_excel(writer, sheet_name='减肥日记', index=False)
            
            # 显示详细的导出信息
            message = f"数据已导出到Excel文件:\n{export_path}\n\n"
            message += f"文件大小: {os.path.getsize(export_path)} 字节\n"
            message += f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            message += "Excel文件包含两个工作表:\n"
            message += "1. 体重记录 - 包含所有体重数据\n"
            message += "2. 减肥日记 - 包含所有日记数据"
            
            self.show_popup("导出成功", message)
        except Exception as e:
            self.show_popup("导出失败", f"错误: {str(e)}")
    
    def show_file_location(self, instance):
        """显示导出文件的位置信息"""
        if IS_ANDROID:
            base_dir = self.user_data_dir
        else:
            base_dir = os.path.expanduser("~")
        
        export_path = os.path.join(base_dir, "weight_data_export.xlsx")
        
        message = "导出文件位置信息:\n\n"
        message += f"文件路径: {export_path}\n\n"
        
        if os.path.exists(export_path):
            file_size = os.path.getsize(export_path)
            mod_time = datetime.fromtimestamp(os.path.getmtime(export_path))
            message += f"文件状态: 已存在\n"
            message += f"文件大小: {file_size} 字节\n"
            message += f"修改时间: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        else:
            message += f"文件状态: 尚未导出\n\n"
        
        message += "在Android设备上查找文件的方法:\n"
        message += "1. 使用文件管理器应用\n"
        message += "2. 查找应用数据目录\n"
        message += "3. 或者连接电脑通过USB传输文件查看\n\n"
        message += "在Pydroid中，你可以在侧边栏的文件浏览器中查找"
        
        self.show_popup("文件位置", message)
    
    def import_data(self, instance):
        try:
            if IS_ANDROID:
                base_dir = self.user_data_dir
            else:
                base_dir = os.path.expanduser("~")
            
            import_path = os.path.join(base_dir, "weight_data_export.xlsx")
            
            if os.path.exists(import_path):
                # 读取Excel文件
                weight_df = pd.read_excel(import_path, sheet_name='体重记录')
                diary_df = pd.read_excel(import_path, sheet_name='减肥日记')
                
                # 转换为列表格式 - 注意：时间类型已经是中文，导入时会自动转换为英文
                weight_records = weight_df.values.tolist()
                diary_entries = diary_df.values.tolist()
                
                data = {
                    'weight_records': weight_records,
                    'diary_entries': diary_entries
                }
                
                if self.db.import_data(data):
                    self.show_popup("导入成功", "Excel数据导入成功！")
                    # 更新显示
                    self.update_records_display()
                    self.update_statistics()
                    self.update_chart()
                    self.update_diary_display()
                    self.load_today_diary()  # 重新加载今天的日记
                else:
                    self.show_popup("导入失败", "数据导入失败")
            else:
                self.show_popup("导入失败", f"未找到导入文件:\n{import_path}")
        except Exception as e:
            self.show_popup("导入失败", f"错误: {str(e)}")
    
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
        # 创建可滚动的使用说明窗口
        content = BoxLayout(orientation='vertical', spacing=10)
        
        # 标题
        title_label = Label(
            text="使用说明", 
            font_size=48,
            size_hint_y=0.1
        )
        content.add_widget(title_label)
        
        # 滚动内容
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
        
        # 确定按钮
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
        # 创建可滚动的弹出窗口
        content = BoxLayout(orientation='vertical', spacing=10)
        
        # 标题
        title_label = Label(
            text=title,
            font_size=46,
            size_hint_y=0.2
        )
        content.add_widget(title_label)
        
        # 滚动内容
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
        
        # 确定按钮
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
        WeightTrackerApp().run()
    except Exception as e:
        # 如果应用崩溃，记录错误
        with open("crash_log.txt", "w") as f:
            f.write(f"应用崩溃: {str(e)}")
