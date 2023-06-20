import os
from typing import Union, Optional
from PyQt6.QtWidgets import QGridLayout, QMainWindow, QWidget, QVBoxLayout, QScrollArea
import pandas as pd

from PyQt6.QtCore import QRegularExpression, Qt
from PyQt6.QtWidgets import (
    QLineEdit,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QWidget,
    QPushButton
)

from Heatmap2DWidget import Heatmap2DWidget


class RangeInputBox(QWidget):
    def __init__(self, axis_name="X"):
        super().__init__()
        main_layout = QGridLayout()
        self.setLayout(main_layout)

        self.title = QLabel(f"{axis_name} Range")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.start_label = QLabel("Start:")
        self.start_label.setMaximumWidth(80)
        self.start_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.stop_label = QLabel("Stop:")
        self.stop_label.setMaximumWidth(80)
        self.stop_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.range_start_box = QLineEdit("0")
        self.range_start_box.setMaximumWidth(80)
        self.range_start_box.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.range_stop_box = QLineEdit("0")
        self.range_stop_box.setMaximumWidth(80)
        self.range_stop_box.setAlignment(Qt.AlignmentFlag.AlignLeft)

        main_layout.addWidget(self.title, *(0, 0), *(1, 2))
        main_layout.addWidget(self.start_label, *(1, 0))
        main_layout.addWidget(self.range_start_box, *(1, 1))
        main_layout.addWidget(self.stop_label, *(2, 0))
        main_layout.addWidget(self.range_stop_box, *(2, 1))

    def connect_on_edit_finish(self, function):

        self.range_stop_box.editingFinished.connect(lambda: function(self.get_range()))
        self.range_stop_box.editingFinished.connect(lambda: function(self.get_range()))

    def get_range(self):
        start = self.range_start_box.text()
        stop = self.range_stop_box.text()
        if start == stop:
            return None
        else:
            return start, stop

    def set_values(self, start: float, stop: float):
        self.range_start_box.setText(start)
        self.range_stop_box.setText(stop)


class Settings(QWidget):
    def __init__(self):
        super().__init__()

        self.x_range_input = RangeInputBox(axis_name='X')
        self.y_range_input = RangeInputBox(axis_name='Y')
        self.from_zoom = QPushButton("From Zoom")
        self.load_btn = QPushButton("Load")
        self.save_btn = QPushButton("Save")

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        main_layout.addWidget(self.x_range_input)
        main_layout.addWidget(self.y_range_input)
        main_layout.addWidget(self.from_zoom)
        main_layout.addWidget(self.load_btn)
        main_layout.addWidget(self.save_btn)

    def set_x_range(self, start: float, stop: float):
        self.x_range_input.set_values(start, stop)

    def set_y_range(self, start: float, stop: float):
        self.y_range_input.set_values(start, stop)

    def connect_on_save_btn_press(self, function):
        self.save_btn.pressed.connect(function)

    def connect_on_load_btn_press(self, function):
        self.load_btn.pressed.connect(function)

    def connect_on_from_zoom(self, function):
        self.from_zoom.pressed.connect(function)

    def connect_on_edit_finish(self, function):
        self.x_range_input.connect_on_edit_finish(lambda x: function(x, (None, None)))
        self.y_range_input.connect_on_edit_finish(lambda y: function((None, None), y))


class MainWindow(QMainWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.plots = []
        self.frame_x_start = None
        self.frame_x_end = None
        self.frame_y_start = None
        self.frame_y_end = None

        self._init_ui()

        self.display_pocket_vna_plot(None)

    def _init_ui(self):
        self.setWindowTitle(f"MDMA data editor")

        self.setGeometry(100, 100, 1460, 600)

        self.main_layout = QGridLayout()
        self.settings_widget = Settings()
        self.settings_widget.connect_on_edit_finish(self.update_frame)
        self.settings_widget.connect_on_from_zoom(self.from_zoom)
        self.main_layout.addWidget(self.settings_widget, *(0, 0))

        widget = QWidget()
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)

    def clean_screen(self):
        for plot in self.plots:
            self.main_layout.removeWidget(plot["widget"])
            plot["widget"].deleteLater()
            plot["widget"] = None

    def display_hameg_plot(self, data):
        self.clean_screen()

        self.plots = [
            {
                "widget": Heatmap2DWidget(title="Signal Amplitude [dB]"),
                "position": (0, 1),
                "shape": (1, 1),
                "title": "Signal Amplitude [dB]",
            }
        ]
        for plot in self.plots:
            self.main_layout.addWidget(plot["widget"], *plot["position"], *plot["shape"])

    def display_pocket_vna_plot(self, data):
        self.clean_screen()

        self.plots = [
            {
                "widget": Heatmap2DWidget(title="Real part"),
                "position": (0, 1),
                "shape": (1, 1),
                "title": "Real part",
            },
            {
                "widget": Heatmap2DWidget(title="Imaginary part"),
                "position": (0, 2),
                "shape": (1, 1),
                "title": "Imaginary part",
            },
        ]

        for plot in self.plots:
            self.main_layout.addWidget(plot["widget"], *plot["position"], *plot["shape"])

    def update_frame(self, x_range=(None, None), y_range=(None, None)):

        if x_range[0] is not None:
            self.frame_x_start = x_range[0]
        else:
            self.frame_x_start = self.plots[0].get_x_lim()[0]

        if x_range[1] is not None:
            self.frame_x_end = x_range[1]
        else:
            self.frame_x_end = self.plots[0].get_x_lim()[1]

        if y_range[0] is not None:
            self.frame_y_start = y_range[0]
        else:
            self.frame_y_start = self.plots[0].get_y_lim()[0]

        if y_range[1] is not None:
            self.frame_y_end = y_range[1]
        else:
            self.frame_y_end = self.plots[0].get_y_lim()[1]

        print("self.frame_x_start", self.frame_x_start)
        print("self.frame_x_end", self.frame_x_end)
        print("self.frame_y_start", self.frame_y_start)
        print("self.frame_y_end", self.frame_y_end)

    def from_zoom(self):

        x_ranges = [plot["widget"].get_x_lim() for plot in self.plots]

        x_range_value = [range[1] - range[0] for range in x_ranges]

        x_range = x_ranges[x_range_value.index(min(x_range_value))]

        y_ranges = [plot["widget"].get_y_lim() for plot in self.plots]

        y_range_value = [range[1] - range[0] for range in y_ranges]
        y_range = y_ranges[y_range_value.index(min(y_range_value))]

        print(x_range, y_range)
