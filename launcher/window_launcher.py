
import os
import sys
import pythoncom
from threading import Thread
from time import sleep
from tkinter import ttk, Tk, Canvas, ARC, PhotoImage

from launcher_sitting import ROOT
from launcher_function import download_programm, check_and_create_new_app_runner, update_appliction, run_application, check_actual_version
from launcher_sitting import PATH_SRC


class WaitProcessBar(Canvas):
    def __init__(self, parent, width=None, height=None):
        super().__init__(master=parent, width=width, height=height)
        self.parent = parent

        self._bg_color="#d9d9d9", 
        self._stripe_color="#b3b3b3",
        self._fill_color="#4caf50"
        self.current_value = 0

        self.width = self.winfo_reqwidth()
        self.height = self.winfo_reqheight()

        self._space_stripe = 35
        self._width_stripe = 15

        self._bg_rect = None
        self._border_rect = None
        self._fill_rect = None
        self._offset = -2 * self._space_stripe
        self._list_stripe = []

        self.__draw_bg()
        self.__draw_wait_animation()
    
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

        for i in range(0, 2 * self.width, self._space_stripe):
            stripe = self.create_line(i + self._offset, 0, i + self.height + self._offset, self.height, fill=self._stripe_color, width=self._width_stripe, capstyle='projecting')
            self._list_stripe.append(stripe)
        
        for st in self._list_stripe:
            self.tag_lower(st, self._fill_rect)
        self.tag_raise(self._border_rect)

    def __draw_wait_animation(self) -> None:
        if self._offset > -1:
            self._offset = -2 * self._space_stripe
        self._offset += 2
        self.__draw_wait_static()
        self.after(45, self.__draw_wait_animation)

    def set_value(self, value: float) -> None:
        self.current_value = value
        self.coords(self._fill_rect, 0, 0, int(self.width * value), self.height)
    
    def plus_value(self, value: float) -> None:
        self.set_value(self.current_value + value)


class MyLabel(ttk.Label):
    def __init__(self, parent, text=''):
        super().__init__(parent)

        self.text = text
        self.color = 'black'
        self.backgorund = '#fff'
        self.border = None

        self.setBackground(self.backgorund)
        self.setText(text)

    def setText(self, text: str) -> None:
        self.text = text
        self.config(text=text)
    
    def setFont(self, family='Segoe UI Variable', size=10) -> None:
        self.config({'font': (family, size)})

    def setColor(self, color: str) -> None:
        self.color = color
        self.config(color=color)

    def setBackground(self, color: str) -> None:
        self.backgorund = color
        self.config(background=color)
    
    def setWidth(self, value:float=3) -> None:
        self.width = value
        self.config(width=value)

    def setHeight(self, value: float):
        self.height = value
        self.config(height=value)

    def setAlignText(self, align='center') -> None:
        self.config(anchor=align)

    def setJustify(self, justify: str) -> None:
        self.config(justify=justify)


class CustomButton(MyLabel):
    def __init__(self, parent, text=''):
        super().__init__(parent, text)

        self.backgorund_leave = '#999'
        self.setWidth()
        self.setAlignText()

        self.__command_clicked = None
        self.__initEvent()

    def __initEvent(self) -> None:
        self.bind('<Enter>', self.eventEnter)
        self.bind('<Leave>', self.eventLeave)
        self.bind('<ButtonPress>', self.__clicked)

    def eventEnter(self, event) -> None:
        self.config(background=self.backgorund_leave, cursor='hand2')

    def eventLeave(self, event) -> None:
        self.config(background=self.backgorund)
    
    def setBackgroundLeave(self, color):
        self.backgorund_leave = color

    def setClicked(self, command) -> None:
        self.__command_clicked = command
    
    def __clicked(self, event) -> None:
        if self.__command_clicked is not None:
            self.__command_clicked()

class WindowLauncher(Tk):
    def __init__(self):
        super().__init__()

        self.width, self.height = 350, 70
    
        self.initWindow()
        self.initWidgets()

        self.bind("<Configure>", self.on_state_change)

    def initWindow(self) -> None:
        self.title('Constructor launcher')
        self.geometry(f'{self.width}x{self.height}+{self.winfo_screenwidth()//2}+{self.winfo_screenheight()//2}')
        self.resizable(False, False)
        # self.overrideredirect(True)
        
        photo = PhotoImage(file=os.path.join(ROOT, r'resources\icon', 'icon_launcher.png'))
        self.iconbitmap(os.path.join(ROOT, r'resources\icon', 'icon_launcher.ico'))
        self.iconphoto(True, photo)

        self.config(background='#fff')

        self.bind('<Escape>', lambda event: sys.exit())

    def initWidgets(self) -> None:
        main_style = ttk.Style()
        main_style.configure('TFrame', background='#fff')
        self.main_frame = ttk.Frame(self, style='TMain.TFrame', borderwidth=2, relief='solid')
        self.main_frame.pack(fill='both')

        self.ico_title = ttk.Label(self.main_frame, image=PhotoImage(file=os.path.join(ROOT, r'resources\icon', 'icon_launcher.png')))
        self.ico_title.grid(row=0, sticky='w')
    
        self.label_title = MyLabel(self.main_frame )
        self.label_title.setText('Constructor launcher')
        self.label_title.grid(row=0, sticky='w')

        self.frame_hide_close = ttk.Frame(self.main_frame )
        self.frame_hide_close.grid(row=0, sticky='e', ipadx=5)

        self.btn_hide = CustomButton(self.frame_hide_close)
        self.btn_hide.setText('_')
        self.btn_hide.setClicked(self.minimize)
        self.btn_hide.grid(row=0, column=0, ipady=1)

        self.btn_close = CustomButton(self.frame_hide_close)
        self.btn_close.setBackgroundLeave('red')
        self.btn_close.setText('x')
        self.btn_close.setClicked(lambda: sys.exit())
        self.btn_close.grid(row=0, column=1, ipady=1)

        self.pb = WaitProcessBar(self.main_frame , width=self.width, height=20)
        self.pb.grid(row=1, column=0)
        
        self.label_info = MyLabel(self.main_frame )
        self.label_info.setText('Запуск приложения...')
        # self.label_info.setFont()
        self.label_info.setJustify(justify='left')
        self.label_info.grid(row=2, column=0, sticky='w')

    def on_state_change(self, event) -> None:
        state = self.state()
        if state == 'normal':
            self.overrideredirect(True)
        elif state == 'iconic':
            self.overrideredirect(False)

    def minimize(self) -> None:
        self.overrideredirect(False)
        self.iconify() 

    def __run2(self) -> None:
        sleep(1)
        self.pb.set_value(0.2)
        sleep(1)
        self.pb.plus_value(0.2)
        sleep(1)
        self.pb.plus_value(0.2)
        sleep(1)
        self.pb.plus_value(0.2)

    def __run(self) -> None:
        pythoncom.CoInitialize()
        if not os.path.exists(PATH_SRC):
            self.label_info.setText('Скачивание компонентов...')
            download_programm()

        argv = sys.argv
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
        Thread(target=self.__run2, daemon=True).start()
        self.mainloop()


if __name__ == '__main__':
    launcher = WindowLauncher()
    launcher.run()
