## Инструменты для работы *Inventor* и *Autocad*

### Набор приложений:
#### 1. **CopyAssembly**<br> 
- <code>projcet/copy_assembly/ca_main.py</code>
- Копирование сборок Inventor с переименованием входящих файлов в сборку с сохранением всех зависимотей включая трубопроводы и генераторы рам  

#### 2. **main**<br>
- <code>projcet/main/main.py</code>
- Чтение блоков из Autocad и отображение информации по ним из БД, а также вставка соответствующи 3Д моделей в Inventor. Добавление и изменеие ссылок на 3Д моделей для заданного блока.

#### 3. **specification**<br>
- <code>projcet/specification/spec_app.py</code>
- Загрузка и подготовка спецификации из ексель или Inventor. Отображение данных для редактирвоания и формирвоания закупочной спецификации и спецификации на производство. Связь между спецификациями для автонумерации на чертежах Inventor.  

#### 4. **launcher**<br>
- <code>projcet/launcher/window_launcher.py</code>
- Лаунчер для запуска приложений. Проверяет обновление наличиие обновления на сервере.

#### 5. **to_exe**<br>
- <code>projcet/to_ext/to_exe_all_project.py</code>
- Сборка всех указанных приложений в exe. Создание для каждого проекта файл лаунчер, для запуска перед основной программой лаунчера, для проверка обновлений.

#### 6. **Record Gif From App**<br>
- <code>projects\tools\widget_record_gif_from_app.py</code>
- Запись всех экрана заданного приложении в gif.<br>

Необходимо импортировать приложение и передать в *WidgetRecordGifFromApp*

```
from ... import app

if __name__ == "__main__":<br>
    app = QtWidgets.QApplication(sys.argv) 
    player = WidgetRecordGifFromApp(app=app)
    player.show()
    sys.exit(app.exec_())
```

#### 6. **Generate Help Tour**<br>
- <code>projects\tools\generate_config_help_tour.py</code>
- Инструмент для создания интерактивной подсказки<br>
Необходимо импортировать приложение а также все зависимости для данного приложения

```
# Добавлене путей к приложению, которое необходимо запустить 
PATH_PROJCETS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH_APPLICATION = os.path.join(PATH_PROJCETS, 'specification')
PATH_APPLICATION_RESOURCES = os.path.join(PATH_PROJCETS, 'resources\\spec_resources')
PATH_SAVE_CONTENT_GIF = os.path.join(PATH_APPLICATION_RESOURCES, 'gif')
PATH_SAVE_CONTENT_IMAGE = os.path.join(PATH_APPLICATION_RESOURCES, 'image')

sys.path.append(PATH_PROJCETS)
sys.path.append(PATH_APPLICATION)

from specification.ui.main_window import WindowSpecification as child_ppplication
from projects.tools.helper_interactive import HelperInteractive

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    window = WindowCreaterConfigHelpTour(application=child_ppplication)
    window.show()
    sys.exit(app.exec_())
```