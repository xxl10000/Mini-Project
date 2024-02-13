import sys
import os
import datetime
import calendar
import pandas as pd
import sqlite3
from cs50 import SQL
from sqlalchemy import create_engine


from PyQt6.QtCore import QTime, QTimer, pyqtSignal
from PyQt6.QtGui import QKeySequence
from PyQt6.QtCore import QUrl
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,

    QPushButton,
    QLabel,
    QSpinBox,
    QMessageBox,
    QComboBox,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,

    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,

    QAbstractItemView,
    
)
from SQL_data import SQLData


DATABASE = "project.db"

SPINBOX_DISPLAY_WIDTH = 50
SPINBOX_LABEL_INTERVAL = 5
WINDOW_WIDTH = 1080
WINDOW_HEIGHT = 360
# TABLE_ROW_HEIGHT = 20
# TABLE_COLUMN_WIDTH = 60
# TABLE_SIZE = WINDOW_SIZE // 3 * 2
SECTION_COUNT_OF_WEEK = 4
TABLE_COLUMN = 5

STUDY_VALUE = 45
BREAK_VALUE = 15
STUDY_DURATION = QTime(0, STUDY_VALUE, 0)
BREAK_DURATION = QTime(0, BREAK_VALUE, 0)
MINIMUM_STUDY_DURATION = 1

MUSIC_VOLUME = 50
MUSIC_DIRECTORY = "resource/music"
MUSIC_NUMBER = 16

class PyPomoView(QWidget):
    start_pressed = pyqtSignal()
    stop_pressed = pyqtSignal()
    reset_pressed = pyqtSignal()

    study_duration_change_edit = pyqtSignal()
    break_duration_change_edit = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.setWindowFilePath("PyPomo")
        self.setMinimumSize(WINDOW_WIDTH, WINDOW_HEIGHT)

        self.general_left_layout = QVBoxLayout()
        # self.general_right_layout = QVBoxLayout()
        self.general_layout = QHBoxLayout()
        self.general_layout.addLayout(self.general_left_layout)
        # self.general_layout.addLayout(self.general_right_layout)
        self.create_display_pomo(self.general_left_layout)
        # self.display_daily_data()
        self.table_daily_data = SQLData(DATABASE)
        self.general_layout.addWidget(self.table_daily_data)
        self.setLayout(self.general_layout)

    def create_display_pomo(self, layout):
        self.combo = QComboBox()
        self.combo.setEditable(True)

        layout.addWidget(self.combo)

        layout_h = QHBoxLayout()
        self.create_spinboxes(layout_h)
        self.table = QTableWidget()
        layout_h.setSpacing(20)
        layout_h.addWidget(self.table)

        layout.addLayout(layout_h)

        self.label = QLabel()

        layout.addWidget(self.label)
        self.create_buttons(layout)

        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Comment")
        layout.addWidget(self.line_edit)

    def study_duration_change(self):
        self.study_duration_change_edit.emit()

    def break_duration_change(self):
        self.break_duration_change_edit.emit()

    def start_timer(self):
        self.start_pressed.emit()
    def stop_timer(self):
        self.stop_pressed.emit()
    def reset_timer(self):
        self.reset_pressed.emit()

    def create_spinboxes(self, layout):
        layout_g = QGridLayout()
        layout_v = QVBoxLayout()
        spinboxes = {
            "study_spinbox": {"range": (1, 300), "step": 5, "value": STUDY_VALUE, "slot": self.study_duration_change, "label_text": "Study: ", "duration": "study_duration"},
            "break_spinbox": {"range": (2, 120), "step": 1, "value": BREAK_VALUE, "slot": self.break_duration_change, "label_text": "Rest: ", "duration": "break_duration"},
        }

        for index, (spinbox, details) in enumerate(spinboxes.items()):
            setattr(self, spinbox, QSpinBox())
            obj = getattr(self, spinbox)
            obj.setRange(*details["range"])
            obj.setSingleStep(details["step"])
            obj.setValue(details["value"])
            obj.valueChanged.connect(details["slot"])
            obj.setFixedWidth(SPINBOX_DISPLAY_WIDTH)
            label = QLabel(details["label_text"])
            label.setContentsMargins(0, 0, 0, 0)
            obj.setContentsMargins(0, 0, 0, 0)
            layout_g.addWidget(label, index, 0)
            layout_g.addWidget(obj, index, 1)

            # layout_v.addWidget(label)

            # layout_v.addWidget(obj)
            setattr(self, details["duration"], QTime(0, int(obj.text()), 0))
        layout_g.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(layout_g)

    def format_day(self, n: int):
        weekdays = ["Mon.", "Tue.", "Wed.", "Thu.", "Fri.", "Sat.", "Sun."]
        return weekdays[n]

    def format(self, data: dict, count_average, duration_average):
        now = datetime.datetime.now()
        
        week_number = datetime.datetime.isocalendar(now)[1]
        section_number = (week_number - 1)// SECTION_COUNT_OF_WEEK + 1

        week_day_count = now.weekday() + 1
        section_day_count = 7 * ((week_number - 1) % SECTION_COUNT_OF_WEEK ) + week_day_count
        year_day_count = now.timetuple().tm_yday
        
        year_day_total = 365 + calendar.isleap(now.year)

        time_periods = {"Day": 1, "Week": week_day_count, "Section": section_day_count, "Year": year_day_count}
        # dict of dict -> list of dict
        list_of_data = [{"Period": k, "Percent": 0, "Count": v["count"], "Duration": v["duration"]} for k, v in data.items()]

        for dict_data in list_of_data:
            period, percent, count, duration = dict_data.keys()
            time = dict_data[period].title()
            match time:
                case "Day":
                    new_period = time + " " + now.strftime("%a: %H:%M:%S")
                    new_percent = (now.hour * 60 * 60 + now.minute * 60 + now.second) / (24 * 60 * 60)
                case "Week":
                    new_period = time + " " + str(week_number) + ": " + str(week_day_count)
                    new_percent = ((week_day_count - 1) * 24 * 60 + now.hour * 60 + now.minute) / (7 * 24 * 60)
                case "Section":
                    new_period = time + " " + str(section_number) + ": " + str(section_day_count)
                    new_percent = ((section_day_count - 1) * 24 + now.hour ) / (SECTION_COUNT_OF_WEEK * 7 * 24)
                case "Year":
                    new_period = time + " " + str(now.year) + ": " + str(year_day_count)
                    new_percent = ((year_day_count - 1) * 24 + now.hour) / (year_day_total * 24)
            
            time_period = time_periods[time]


            dict_data[period] = new_period
            dict_data[percent] = str(round(new_percent * 100, 2)) + "%"
            dict_data[count_average] = round(dict_data[count] / time_period, 2)
            dict_data[duration_average] = round(dict_data[duration] / time_period, 2)

        
        # print(list_of_data)
        return list_of_data

    def display_table(self, data: dict):
        # self.table.setFixedSize(TABLE_SIZE, TABLE_SIZE)
        # print(data)
        count_average = "Count Average"
        duration_average = "Duration Average"
        # print(data)
        data = self.format(data, count_average, duration_average)
        

        self.table.setRowCount(len(data))
        # for row in range(len(data)):
        #     self.table.setRowHeight(row, TABLE_ROW_HEIGHT)

        sub_keys = ["Percent", "Count", "Duration", count_average, duration_average]
        # sub_keys = ["Count", "Duration",]

        self.table.setColumnCount(1 + len(sub_keys))
        # for col in range(1 + len(sub_keys)):
        #     self.table.setColumnWidth(col, TABLE_COLUMN_WIDTH)

        self.table.setHorizontalHeaderLabels(["Period"] + list(sub_keys))
        self.table.verticalHeader().setVisible(False)

        for row, dict_data in enumerate(data):
            for col, (key, value) in enumerate(dict_data.items()):
                self.table.setItem(row, col, QTableWidgetItem(str(value)))
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        # for the data type: dict of dict
        # for row, (period, stats) in enumerate(data.items()):
        #     self.table.setItem(row, 0, QTableWidgetItem(period))
        #     for col, stat_value in enumerate(stats.values(), 1):
        #         self.table.setItem(row, col, QTableWidgetItem(str(stat_value)))

    def create_buttons(self, layout):
        layout_h = QHBoxLayout()
        buttons = {
            "&Start": {"slot": self.start_timer, "shortcut": QKeySequence("Ctrl+S")},
            "Sto&p": {"slot": self.stop_timer, "shortcut": QKeySequence("Ctrl+P")},
            "&Reset": {"slot": self.reset_timer, "shortcut": QKeySequence("Ctrl+R")},
        }

        for button_text, details in buttons.items():
            button = QPushButton(button_text)
            button.clicked.connect(details["slot"])
            button.setShortcut(details["shortcut"])
            layout_h.addWidget(button)
        layout.addLayout(layout_h)

    def display_time(self, color = "gold", text = "No valid text"):
        # self.label.setStyleSheet(f"color: {color}; font-size: 20px;")
        self.label.setStyleSheet(f"font-size: 15px;")
        self.label.setText(text)

    def clear_comment(self):
        self.line_edit.setText("")
    
    def display_daily_data(self, query = ""):
        
        
        # query = f"SELECT activity AS 'Activity', finish_flag AS 'Finish Flag', strftime('%H:%M', start_time) AS 'Start Time', strftime('%H:%M', end_time) AS 'End Time', duration_in_minutes AS 'Duration(minutes)' FROM pomo WHERE year = {today.year} AND month = {today.month} AND day = {today.day} ORDER BY end_time DESC"
        # self.table_daily_data = SQLData(DATABASE, query)
        # self.table_daily_data.show()
        # layout.addWidget(self.table_daily_data)
        self.table_daily_data.change_query(query)
        self.table_daily_data.resizeColumnsToContents()
        self.table_daily_data.resizeRowsToContents()
        # self.general_layout.addWidget(self.table_daily_data)

class PyPomoModel:
    def __init__(self) -> None:
        # self.read_statistics()

        # it also should read from the database(from list actually, list data -> dababase, so from database), or you can edit it in the list QWidget.
        self.task = ["CS", "Leetcode", "Recite", "English Drama", "Book Notes", "Japanese", "Core Review", "Mediation", "Movie", "Focus"]

        self.pomo = {"week_number": [], "year": [], "month": [], "day":[], "day_of_week": [], "finish_flag": [], "activity": [], "comment": [], "start_time": [], "end_time": [], "duration_in_minutes": []}
        self.daily_data_query = f"""SELECT
            CASE 
                WHEN day_of_week = 0 THEN 'Mon'
                WHEN day_of_week = 1 THEN 'Tue'
                WHEN day_of_week = 2 THEN 'Wed'
                WHEN day_of_week = 3 THEN 'Thu'
                WHEN day_of_week = 4 THEN 'Fri'
                WHEN day_of_week = 5 THEN 'Sat'
                WHEN day_of_week = 6 THEN 'Sun'
            END 
            AS Weekday, activity AS 'Activity', finish_flag AS 'Finish Flag', strftime('%H:%M', start_time) AS 'Start Time', strftime('%H:%M', end_time) AS 'End Time', duration_in_minutes AS 'Duration(minutes)' FROM pomo ORDER BY end_time DESC"""
    def read_habit(self):
        self.habit = []
        db = SQL("sqlite:///" + DATABASE)
        rows = db.execute("SELECT activity FROM habit")
        for row in rows:
            self.habit.append(row["activity"])

    def get_habit(self):
        return self.habit if self.habit else self.task

    def read_statistics(self):
        db = SQL("sqlite:///" + DATABASE)
        

        time_periods = ["day", "week", "section", "year"]
        self.statistics = {period: {"count":0, "duration": 0} for period in time_periods}

        today = datetime.date.today()
        week_number = datetime.date.isocalendar(today)[1]
        section_number = (week_number - 1) // SECTION_COUNT_OF_WEEK + 1

        try:
            rows = db.execute("SELECT * FROM pomo")
        except:
            pass
        else:
            queries = {
                "day": {
                    "condition": "year = (?) AND month = (?) AND day = (?)",
                    "params": (today.year, today.month, today.day),
                },
                "week":{
                    "condition": "week_number = (?)",
                    "params": (week_number,),
                },
                "section":{
                    "condition": "week_number BETWEEN (?) AND (?)",
                    "params": (section_number* 4 - 3, section_number* 4),
                },
                "year":{
                    "condition": "year = (?)",
                    "params": (today.year,),
                },
            }
            for key, query in queries.items():
                # count how many pomos you finish in a day. It should be read from the database, if none from the table, then 1, or it should be the result by the database

                # for static query, f-string is OK.
                # use 60.0 instead of use becasue of division to integer in SQL for 2 integer number.
                rows = db.execute(f"SELECT SUM(finish_flag) AS count, ROUND(SUM(duration_in_minutes) /60.0, 2) AS duration FROM pomo WHERE {query["condition"]}", *query["params"])

                # rows = db.execute(f"SELECT * FROM pomo WHERE {query["condition"]}", *query["params"])
                # print(rows)
                self.statistics[key] = rows[0] if rows[0]["count"] else {"count": 0, "duration": 0}
        

    def seconds(self, t: QTime):
        return t.hour() * 3600 + t.minute() * 60 + t.second()

    def pomo_start(self):
        self.pomo["start_time"] = (datetime.datetime.now())

    def write_statistics(self, finish_flag, activity, comment, duration):
        engine = create_engine("sqlite:///" + DATABASE)


        current_date = datetime.datetime.now()
        pairs = {"week_number": current_date.isocalendar()[1],
                 "year": current_date.year,
                 "month": current_date.month,
                 "day": current_date.day,
                 "day_of_week": current_date.weekday(),
                 "finish_flag": finish_flag,
                 "activity": activity,
                 "comment": comment,
                 "end_time": current_date,
                 "duration_in_minutes": duration , # self.count_seconds / 60 to minute, actually!
        }

        for key, value in pairs.items():
            self.pomo[key] = (value)

        # for key, list1 in self.pomo.items():
        #     print(key, list1)
        df_new = pd.DataFrame(self.pomo, [0])
        # print(df_new)

        df_new.to_sql("pomo", engine, if_exists="append", index=False)

        # df_old = pd.read_sql("SELECT * FROM pomo", con = engine)

        # df_updated = df_new.combine_first(df_old)

        # df_updated.to_sql("pomo", engine, if_exists="replace", index=False)



    def get_statistics(self):
        return self.statistics
    # def add_pomo(self, count, duration):
    #     # it's wrong when the day or period change, which displays the wrong updated data.
    #     for period in self.statistics.keys():
    #         self.statistics[period]["count"] += count
    #         self.statistics[period]["duration"] += round(duration / 3600, 2)


class PyPomoController:
    """PyPomoController's controller class."""
    def __init__(self) :
        self._model = PyPomoModel()
        self._view = PyPomoView()

        self._view.combo.addItems(self._model.task)
        self._view.combo.activated.connect(self.study_duration_set)

        self._view.start_pressed.connect(self.start_timer)
        self._view.stop_pressed.connect(self.stop_timer)
        self._view.reset_pressed.connect(self.reset_timer)

        self._view.study_duration_change_edit.connect(self.study_duration_change)
        self._view.break_duration_change_edit.connect(self.break_duration_change)

        self.study = True
        self.count_seconds = 0
        self.timer = QTimer()

        self.study_duration = STUDY_DURATION
        self.break_duration = BREAK_DURATION
        self.remaining_time = self.study_duration

        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(MUSIC_VOLUME)
        self.music_files = os.listdir(MUSIC_DIRECTORY)
        self.music_files.sort(key = lambda x: int(x.split(".")[0]))

        self.update_view()
        
        self.timer.timeout.connect(self.update_timer)
        self.display_time()
        # self.setup_connections()

        self.table_timer = QTimer()
        self.table_timer.start(1000)
        self.table_timer.timeout.connect(self.update_view)

    def update_view(self):
        self._model.read_statistics()
        self._view.display_table(self._model.statistics)
        self._view.display_daily_data(self._model.daily_data_query)

    def update_table_timer(self):
        self._view.display_table(self._model.statistics)

    def setup_connections(self):
        self.timer.timeout.connect(self.update_timer)

    def start_timer(self):
        self.timer.start(1000)
        self.count_seconds = 0
        if self.study:
            self._model.pomo_start()

    def stop_timer(self):
        self.timer.stop()
        if self.count_seconds and round(self.count_seconds / 60, 2) >= MINIMUM_STUDY_DURATION:
            self._model.write_statistics(not self.study, self._view.combo.currentText(), self._view.line_edit.text(), round(self.count_seconds / 60, 2))
            self.count_seconds = 0

            self.update_view()
    def reset_timer(self):
        self._view.clear_comment()
        self.stop_timer()
        self.remaining_time = self.study_duration if self.study else self.break_duration
        # print(self.remaining_time, self.study_duration)
        self.display_time()

    def time_convert(self, min):
        return QTime(min // 60, min % 60, 0)
    
    def study_duration_set(self):
        if self.study:
            pass
        else:
            self.study_duration_change()

    def study_duration_change(self):
        self.study = True
        self.study_duration = self.time_convert(int(self._view.study_spinbox.text()))
        
        self.reset_timer()

    def break_duration_change(self):
        self.study = False
        self.break_duration =  self.time_convert(int(self._view.break_spinbox.text()))
        self.reset_timer()

    def display_time(self):
        self.current_duration = self.study_duration if self.study else self.break_duration
        percentage = 100 * (1 - self._model.seconds(self.remaining_time) * 1.0/ self._model.seconds(self.current_duration))

        state = "Study" if self.study else "Break"
        color = "purple" if self.study else "orange"
        format = "hh:mm:ss" if self.remaining_time >= QTime(1, 0, 0) else "mm:ss"
        self._view.display_time(color, text = f'<p>Mode: <font color={color}>{state}</font>  <br>Remaining Time: <font color="green">{self.remaining_time.toString(format)}</font> <br>Progress Percentage: <font color="blue">{percentage:.2f}%</font></p>')

    def start_music(self, n):
        self.player.setSource(QUrl.fromLocalFile(MUSIC_DIRECTORY + "/" + self.music_files[(n - 1) % len(self.music_files)]))

        self.player.play()

    def update_timer(self):


        self.remaining_time = self.remaining_time.addSecs(-1)
        if self.study:
            self.count_seconds += 1

        # print("Time remaining: ", self.remaining_time.toString())


        self.display_time()
        
        if self.remaining_time == QTime(0, 0, 0):
            if self.study:
                self.study = False
                # self._model.add_pomo(1, self.count_seconds)
                
                self.reset_timer()
                self.start_music(self._model.get_statistics()["day"]["count"])
                self.start_timer()
                # print("Study finished. Why not have a break!")
                infor = QMessageBox.information(self._view, "Information", f"Excellent, you have finished {self._model.get_statistics()["day"]["count"]} pomos, {self._model.get_statistics()["day"]["duration"]} duration in a day!")



            else:
                self.study = True
                self.reset_timer()
                # print("Break finished. Just keep studying!")

                reply = QMessageBox.question(self._view, "Question", "Continue to next pomo?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    self.start_timer()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    obj = PyPomoController()
    obj._view.show()
    sys.exit(app.exec())
