
import os
import sys
import pythoncom
from threading import Thread

from tkinter import ttk, Tk, Canvas, ARC, PROJECTING

from launcher_function import download_programm, check_and_create_new_app_runner, update_appliction, run_application, check_actual_version
from launcher_sitting import PATH_SRC


class PBRing:
    def __init__(self, root, canvas: Canvas, x:float, y:float, width: float, height: float, border_width: float):
        self.root = root
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.border_width = border_width

        self.start_angle = 0
        self.len_arc = 90
        self.len_arc = self.start_angle - self.len_arc
        self.sign_direction = 1

        self.arc = None
        # self.draw_arc()
        self.rotate()

    def draw_arc(self) -> None:
        if self.arc:
            self.canvas.delete(self.arc)

        self.arc = self.canvas.create_arc(self.x + self.border_width, self.y + self.border_width, self.width - self.border_width, self.height - self.border_width, 
                                          start=self.start_angle, 
                                          extent=self.len_arc,
                                          width=self.border_width, 
                                          outline="green", 
                                          style=ARC)

    def rotate(self) -> None:
        self.draw_arc()
        self.start_angle += 5
        self.len_arc += 1
        
        self.root.after(30, self.rotate)


class WaitProcessBar(Canvas):
    def __init__(self, parent, width=None, height=None):
        super().__init__(master=parent, width=width, height=height)
        self.parent = parent

        self._bg_color="#d9d9d9", 
        self._stripe_color="#b3b3b3",
        self._fill_color="#4caf50"

        self.width = self.winfo_reqwidth()
        self.height = self.winfo_reqheight()

        self._space_stript = 35
        self._width_stripe = 15

        self._bg_rect = None
        self._border_rect = None
        self._fill_rect = None
        self._offset = 0
        self._list_stripe = []
        self._x_loop = self._width_stripe * 2

        self.__draw_bg()
        self.__draw_wait_static()
        self.__draw_wait_animation()
        # self.set_value(50)
    
    def __draw_bg(self) -> None:
        self._bg_rect = self.create_rectangle(0, 0, self.width, self.height, outline="", fill=self._bg_color)
        self._border_rect = self.create_rectangle(0, 0, self.width, self.height, outline='black', width=1)
        self._fill_rect = self.create_rectangle(0, 0, 0, self.height, outline="", fill=self._fill_color, width=0)
    
    def __draw_wait_static(self) -> None:
        for it in self._list_stripe:
            try:
                self.delete(it)
            except Exception:
                pass
        self._list_stripe.clear()

        for i in range(-self._x_loop, self.width, self._space_stript):
            stripe = self.create_line(i + self._offset, 0, i + self.height + self._offset, self.height, fill=self._stripe_color, width=self._width_stripe, capstyle='projecting')
            self._list_stripe.append(stripe)
        
        for st in self._list_stripe:
            self.tag_lower(st, self._fill_rect)
        self.tag_raise(self._border_rect)

    def __draw_wait_animation(self) -> None:
        if self._offset > self._x_loop + 2:
            self._offset = 0
        self._offset += 2
        self.__draw_wait_static()
        self.after(45, self.__draw_wait_animation)

    # def __draw_load(self) -> None:
    #     self.coords(self._fill_rect, 0, 0, 50, self.height)

    def set_value(self, value: int) -> None:
        self.coords(self._fill_rect, 0, 0, int(self.width * value/100), self.height)
    
    def start(sefl) -> None:
        pass

    def stop(self) -> None:
        pass


        
class LLabel(ttk.Label):
    def __init__(self, parent):
        super().__init__(parent)
    
    def setText(self, text: str) -> None:
        self.config({'text': text})

    def setFont(self, family='Segoe UI Variable', size=16) -> None:
        self.config({'font': (family, size)})


class WindowLauncher(Tk):
    def __init__(self):
        super().__init__()

        self.initWindow()
        self.initWidgets()

    def initWindow(self) -> None:
        self.title('launcher')
        self.geometry(f'500x75+{self.winfo_screenwidth()//2}+{self.winfo_screenheight()//2}')
        # self.resizable(False, False)
        # self.overrideredirect(True)

        self.bind('<Escape>', lambda event: sys.exit())

    def initWidgets(self) -> None:
        self.pb = WaitProcessBar(self, width=500, height=25)
        self.pb.pack(padx=5, pady=5)
        # self.canvas_w = 45
        # self.canvas_h = 45
        # self.canvas = Canvas(self, width=self.canvas_w, height=self.canvas_h)
        # self.canvas.grid(row=0, column=0)
        
        # self.pb_ring = PBRing(self, self.canvas, 0, 0, self.canvas_w, self.canvas_h, 5)

        # self.label_info = LLabel(self)
        # self.label_info.setFont()
        # self.label_info.setText('Запуск приложения...')
        # self.label_info.grid(row=0, column=1)

    def __run(self) -> None:
        pythoncom.CoInitialize()
        if not os.path.exists(PATH_SRC):
            self.label_info.setText('Скачивание компонентов...')
            download_programm()

        argv = sys.argv
        print(argv)
        if len(argv) == 1:
            self.label_info.setText('Настройка приложения...')
            check_and_create_new_app_runner()
        if len(argv) == 2:
            self.label_info.setText('Проверка обновлений...')
            if not check_actual_version():
                self.label_info.setText('Обновление...')
                update_appliction()
                self.label_info.setText('Настройка приложения...')
                check_and_create_new_app_runner()
            self.label_info.setText('Запуск приложения...')
            run_application(argv[1])
        self.quit()

    def run(self) -> None:
        # Thread(target=self.__run, daemon=True).start()
        self.mainloop()


if __name__ == '__main__':
    launcher = WindowLauncher()
    launcher.run()
