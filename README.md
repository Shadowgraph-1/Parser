
# Parser_scr_txt

## Описание
"Parser_scr_txt" — это инструмент для скачивания страниц веб-сайтов и создания скриншотов на основе списка ссылок. Программа поддерживает автоматическое извлечение всех ссылок с веб-страниц и последующую обработку. Вы можете выбрать, хотите ли скачать страницы, создать скриншоты или выполнить оба действия одновременно.

## Возможности программы
- Извлечение всех ссылок с указанного веб-сайта.
- Скачивание веб-страниц на локальный диск.
- Автоматическое создание скриншотов страниц на основе списка ссылок.
- Поддержка форматов `txt` и `html` для сохранения ссылок.
- Удобный графический интерфейс для выбора настроек программы.

## Системные требования

## Установка

### Установка через инсталлятор
1. Запустите файл `setup.exe`, который вы скачали.
2. Следуйте инструкциям установщика. Перед установкой ознакомьтесь с информацией, предоставленной в диалоговом окне.
3. Программа будет установлена по умолчанию в `C:\Program Files\<Parser_scr_txt>`.
4. После завершения установки запустите программу с рабочего стола или через меню "Пуск".

### Установка вручную из GitHub
1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/Shadowgraph-1/Parser.git
   ```
2. Убедитесь, что у вас установлены все необходимые зависимости:
   ```bash
   pip install -r requirements.txt
   ```
3. Запустите программу:
   ```bash
   Parser.exe
   ```

## Использование

### 1. Запуск программы
Запустите программу с рабочего стола или через меню "Пуск". В главном окне вам будут предложены следующие опции:

- Введите URL веб-сайта для извлечения ссылок.
- Выберите файл со списком ссылок для обработки.
- Укажите, хотите ли вы скачать страницы, создать скриншоты или выполнить оба действия.

### 2. Основные шаги работы
1. **Извлечение ссылок**:
   - Введите URL веб-сайта и нажмите "Обработать URL".
   - Программа автоматически извлечет все ссылки с указанного сайта.
   - Ссылки будут сохранены в выбранном вами формате (`txt` или `html`).

2. **Скачивание страниц**:
   - Выберите файл с ссылками.
   - Выберите "Скачать страницы" и нажмите "Начать".
   - Программа сохранит HTML-код всех указанных ссылок в выбранную директорию.

3. **Создание скриншотов**:
   - Выберите файл с ссылками.
   - Выберите "Создать скриншоты" и нажмите "Начать".
   - Скриншоты веб-страниц будут сохранены в папке `screenshots`.

### 3. Дополнительные функции
- **Редактирование файла ссылок**: Вы можете открыть файл ссылок для редактирования прямо из программы.
- **Настройки**: В разделе "Настройки" можно указать путь к `geckodriver` и браузеру, если это необходимо.

## Структура проекта

- `main.py` — основной файл для запуска программы.
- `config.json` — файл конфигурации для хранения путей к браузеру и драйверу.
- `screenshots/` — директория, где сохраняются скриншоты веб-страниц.
- `downloaded_pages/` — директория, где сохраняются скачанные веб-страницы.
- `requirements.txt` — список необходимых библиотек для работы программы.
- `parser_0.0.2.dist` - папка с файлами для работоспособности программы.

## Пример файла конфигурации (config.json)
```json
{
    "geckodriver_path": "C:/path/to/geckodriver.exe",
    "browser_path": "C:/Program Files/Mozilla Firefox/firefox.exe"
}
```

Этот файл хранит пути к `geckodriver` и браузеру, которые используются для создания скриншотов веб-страниц.

## Зависимости
Для корректной работы программы необходимы следующие библиотеки и зависимости:

- `selenium` (для автоматизации браузера и создания скриншотов)
- `requests` (для скачивания веб-страниц)
- `beautifulsoup4` (для извлечения ссылок с веб-страниц)
- `tkinter` (для создания графического интерфейса программы)

Для установки всех зависимостей выполните следующую команду:
```bash
pip install -r requirements.txt
```

## Лицензия
Программа предоставляется под следующей лицензией:

```
Лицензия Custom License by Oleg Litvinchuk

Copyright (c) 2024/ Oleg Litvinchuk

Permission is hereby granted to any person obtaining a copy of this software (the "Software") to use, modify, and distribute the Software, under the following conditions:

1. The Software may not be used for any illegal activities.
2. Modification of the Software is allowed, but any modified versions must include a reference to the original author.
3. Commercial use of the Software is allowed only with the explicit permission of the original author.
4. Redistribution of the Software is permitted, provided that the original license and copyright notice are included.

THIS SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER LIABILITY, ARISING FROM, OUT OF, OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Автор: Олег

Вы можете использовать, изменять и распространять данное программное обеспечение, при условии, что оставите эту лицензию в исходном виде. Автор не несет ответственности за любые последствия использования данной программы.
```

## Обратная связь
Если у вас возникли вопросы или предложения по улучшению программы, вы можете связаться со мной через [litvin4chuk@mail.ru] или оставить запрос (issue) в репозитории GitHub.
