import sys
import cv2
import imageio
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QFileDialog, QLabel, QSlider, QStyleOptionSlider, QStyle, QFrame,
)
from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor, QBrush, QPen


def frame_to_time_str(frame, fps):
    """Перевод кадра в формат времени ММ:СС"""
    if fps == 0:
        return "00:00"
    total_seconds = int(frame / fps)
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes:02}:{seconds:02}"


class MarkedSlider(QSlider):
    """Кастомный слайдер, рисующий отметки начала и конца"""
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.start_mark = None
        self.end_mark = None

    def set_marks(self, start, end):
        self.start_mark = start
        self.end_mark = end
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)

        # Рисуем отметки
        painter = QPainter(self)
        option = QStyleOptionSlider()
        self.initStyleOption(option)
        groove_rect = self.style().subControlRect(QStyle.CC_Slider, option, QStyle.SC_SliderGroove, self)
        slider_min = groove_rect.x()
        slider_max = groove_rect.right()

        def frame_to_pos(frame):
            if self.maximum() == 0:
                return slider_min
            return slider_min + (slider_max - slider_min) * (frame / self.maximum())

        if self.start_mark is not None:
            x = int(frame_to_pos(self.start_mark))
            pen = QPen(10)
            painter.setPen(pen)
            painter.setPen(QColor(0, 255, 0))
            painter.drawLine(x, groove_rect.top(), x, groove_rect.bottom())

        if self.end_mark is not None:
            x = int(frame_to_pos(self.end_mark))
            pen = QPen(10)
            painter.setPen(pen)
            painter.setPen(QColor(255, 0, 0))
            painter.drawLine(x, groove_rect.top(), x, groove_rect.bottom())


class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GIF Creator from Video (v2)")
        self.resize(850, 600)

        # --- UI elements ---
        self.video_label = QLabel("Загрузите видео", self)
        self.video_label.setAlignment(Qt.AlignCenter)

        self.slider = MarkedSlider(Qt.Horizontal)
        self.slider.setEnabled(False)

        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setAlignment(Qt.AlignRight)

        self.load_btn = QPushButton("Открыть видео")
        self.play_btn = QPushButton("▶️ / ⏸️")
        self.mark_start_btn = QPushButton("Отметить начало")
        self.mark_end_btn = QPushButton("Отметить конец")
        self.make_gif_btn = QPushButton("Создать GIF")

        self.play_btn.setEnabled(False)
        self.make_gif_btn.setEnabled(False)

        # Layout
        hbox = QHBoxLayout()
        hbox.addWidget(self.load_btn)
        hbox.addWidget(self.play_btn)
        hbox.addWidget(self.mark_start_btn)
        hbox.addWidget(self.mark_end_btn)
        hbox.addWidget(self.make_gif_btn)

        vbox = QVBoxLayout()
        vbox.addWidget(self.video_label)
        vbox.addWidget(self.slider)
        vbox.addWidget(self.time_label)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

        # --- Video variables ---
        self.cap = None
        self.timer = QTimer()
        self.frame_rate = 30
        self.total_frames = 0
        self.current_frame = 0
        self.start_mark = None
        self.end_mark = None
        self.playing = False

        # --- Signals ---
        self.load_btn.clicked.connect(self.load_video)
        self.play_btn.clicked.connect(self.toggle_play)
        self.slider.sliderMoved.connect(self.seek_video)
        self.timer.timeout.connect(self.next_frame)
        self.mark_start_btn.clicked.connect(self.mark_start)
        self.mark_end_btn.clicked.connect(self.mark_end)
        self.make_gif_btn.clicked.connect(self.make_gif)

    def load_video(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Выберите видео", "", "Video Files (*.mp4 *.avi *.mkv)")
        if not filename:
            return
        self.cap = cv2.VideoCapture(filename)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frame_rate = self.cap.get(cv2.CAP_PROP_FPS)
        self.slider.setMaximum(self.total_frames)
        self.slider.setEnabled(True)
        self.play_btn.setEnabled(True)
        self.make_gif_btn.setEnabled(True)
        self.video_path = filename
        self.current_frame = 0
        self.start_mark = None
        self.end_mark = None
        self.slider.set_marks(None, None)
        self.show_frame(0)
        self.update_time_label()

    def show_frame(self, frame_number):
        if not self.cap:
            return
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = self.cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w
            q_img = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(q_img).scaled(
                self.video_label.width(), self.video_label.height(), Qt.KeepAspectRatio))
        self.slider.setValue(frame_number)
        self.update_time_label()

    def toggle_play(self):
        if not self.cap:
            return
        if self.playing:
            self.timer.stop()
        else:
            interval = int(1000 / self.frame_rate)
            self.timer.start(interval)
        self.playing = not self.playing

    def next_frame(self):
        if self.current_frame >= self.total_frames - 1:
            self.timer.stop()
            self.playing = False
            return
        self.current_frame += 1
        self.show_frame(self.current_frame)

    def seek_video(self, position):
        self.current_frame = position
        self.show_frame(position)

    def mark_start(self):
        self.start_mark = self.slider.value()
        self.slider.set_marks(self.start_mark, self.end_mark)
        print(f"Start mark set at frame {self.start_mark}")

    def mark_end(self):
        self.end_mark = self.slider.value()
        self.slider.set_marks(self.start_mark, self.end_mark)
        print(f"End mark set at frame {self.end_mark}")

    def update_time_label(self):
        current_time = frame_to_time_str(self.slider.value(), self.frame_rate)
        total_time = frame_to_time_str(self.total_frames, self.frame_rate)
        self.time_label.setText(f"{current_time} / {total_time}")

    def make_gif(self):
        if not self.start_mark or not self.end_mark or self.start_mark >= self.end_mark:
            print("Некорректные метки.")
            return

        save_path, _ = QFileDialog.getSaveFileName(self, "Сохранить GIF", "", "GIF Files (*.gif)")
        if not save_path:
            return

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.start_mark)
        frames = []
        for i in range(self.start_mark, self.end_mark):
            ret, frame = self.cap.read()
            if not ret:
                break
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(frame_rgb)

        imageio.mimsave(save_path, frames, loop=0, fps=self.frame_rate)
        print(f"GIF сохранён в {save_path}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec_())
