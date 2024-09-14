import sys
import threading
import logging
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import os
import json
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QLineEdit,
    QTextEdit, QFileDialog, QMessageBox, QVBoxLayout, QHBoxLayout, QTabWidget,
    QProgressBar, QRadioButton, QButtonGroup, QGroupBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("WebDownloader")

# Класс для работы с конфигурацией
class ConfigManager:
    CONFIG_FILE = "config.json"

    @staticmethod
    def load_config():
        if os.path.exists(ConfigManager.CONFIG_FILE):
            with open(ConfigManager.CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            # Если конфигурационный файл не существует, создать его с пустыми значениями
            default_config = {
                "geckodriver_path": "",
                "browser_path": ""
            }
            ConfigManager.save_config(default_config)
            return default_config

    @staticmethod
    def get_geckodriver_path():
        config = ConfigManager.load_config()
        return config.get("geckodriver_path", "")

    @staticmethod
    def get_browser_path():
        config = ConfigManager.load_config()
        return config.get("browser_path", "")

    @staticmethod
    def set_geckodriver_path(path):
        config = ConfigManager.load_config()
        config["geckodriver_path"] = path
        ConfigManager.save_config(config)

    @staticmethod
    def set_browser_path(path):
        config = ConfigManager.load_config()
        config["browser_path"] = path
        ConfigManager.save_config(config)

    @staticmethod
    def save_config(config):
        with open(ConfigManager.CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)

# Класс для обработки веб-страниц
class Info:
    def __init__(self, site_name):
        self.site_name = site_name

    def status_site(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        logger.info(f"Отправка запроса на {self.site_name}")
        try:
            response = requests.get(self.site_name, headers=headers, timeout=50)
            response.encoding = response.apparent_encoding  # Принудительное указание кодировки
            logger.info(f"Статус-код ответа: {response.status_code}")
            if response.status_code == 200:
                return response.status_code, response
            else:
                return None, None
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при выполнении запроса: {e}")
            return None, None

    def get_info(self, filter_keyword=None):
        check_status, res = self.status_site()
        if check_status == 200:
            try:
                res.encoding = 'utf-8'
                soup = BeautifulSoup(res.text, "html.parser")
                logger.info("Операция прошла успешно")
                if filter_keyword:
                    links = soup.find_all("a", href=re.compile(filter_keyword, re.I))
                else:
                    links = soup.find_all("a")
                return links
            except Exception as e:
                logger.error(f"Ошибка при обработке контента: {e}")
                return []
        else:
            logger.error("Не удалось получить страницу, статус-код не 200.")
            return []

    def save_html(self, extension, filter_keyword=None):
        links = self.get_info(filter_keyword)
        if links:
            file_path = f"Sort_obj.{extension}"
            with open(file_path, "w", encoding="utf-8") as f:
                for num, link in enumerate(links, start=1):
                    href = link.get('href', 'Путь отсутствует')
                    if href.startswith('/'):
                        full_url = urljoin(self.site_name, href)
                    else:
                        full_url = href
                    title = link.get('title', 'Нет названия!')
                    link_info = f"№{num}, {full_url} - {title}\n"
                    f.write(link_info)
            logger.info(f"Ссылки успешно сохранены в {file_path}")
            return file_path
        return None

# Класс для загрузки страниц
class DownloaderThread(QThread):
    progress = pyqtSignal(int)
    log = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, file_with_links, base_url, extension, filter_keyword=None):
        super().__init__()
        self.file_with_links = file_with_links
        self.output_dir = "downloaded_pages"
        self.output_file = f"full_links.{extension}"
        self.base_url = base_url
        self.extension = extension
        self.filter_keyword = filter_keyword

    def sanitize_filename(self, url):
        return re.sub(r'[<>:"/\\|?*]', '_', url)

    def run(self):
        if not os.path.exists(self.file_with_links):
            self.log.emit(f"Файл {self.file_with_links} не найден.")
            return

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        skipped_links = []
        try:
            with open(self.file_with_links, "r", encoding="utf-8") as infile, open(self.output_file, "w", encoding="utf-8") as outfile:
                links = infile.readlines()
                if self.filter_keyword:
                    links = [line for line in links if re.search(self.filter_keyword, line, re.I)]

                total_links = len(links)
                for idx, line in enumerate(links):
                    match = re.search(r'(https?://[^\s]+|/[\w\-\/]+/)', line)
                    if match:
                        url = match.group(1)
                        if url.startswith('/'):
                            full_url = urljoin(self.base_url, url)
                        else:
                            full_url = url

                        outfile.write(f"Полный URL: {full_url}\n")
                        self.download_page(full_url)
                    else:
                        skipped_links.append(line)

                    progress_percent = int((idx + 1) / total_links * 100)
                    self.progress.emit(progress_percent)

            self.log.emit(f"Обработка завершена, результаты сохранены в {self.output_file}")

            if skipped_links:
                self.log.emit("Пропущенные строки:")
                for skipped in skipped_links:
                    self.log.emit(skipped.strip())

        except FileNotFoundError as e:
            self.log.emit(f"Файл не найден: {e}")
        finally:
            self.finished_signal.emit()

    def download_page(self, url):
        try:
            response = requests.get(url, timeout=110)
            if response.status_code == 200:
                sanitized_filename = self.sanitize_filename(url)
                filename = f"{sanitized_filename.replace('https://', '').replace('/', '_')}.{self.extension}"
                filepath = os.path.join(self.output_dir, filename)

                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                self.log.emit(f"Страница {url} успешно сохранена в файл {filepath}")
            else:
                self.log.emit(f"Не удалось скачать страницу {url}. Статус: {response.status_code}")
        except requests.exceptions.RequestException as e:
            self.log.emit(f"Ошибка при скачивании {url}: {e}")

# Класс для создания скриншотов
class ScreenshotThread(QThread):
    progress = pyqtSignal(int)
    log = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, file_with_links, base_url, filter_keyword=None):
        super().__init__()
        self.file_with_links = file_with_links
        self.base_url = base_url
        self.filter_keyword = filter_keyword

    def sanitize_filename(self, url):
        return re.sub(r'[<>:"/\\|?*]', '_', url)

    def run(self):
        if not os.path.exists(self.file_with_links):
            self.log.emit(f"Файл {self.file_with_links} не найден.")
            return

        screenshot_dir = 'screenshots'
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)

        skipped_links = []
        try:
            with open(self.file_with_links, "r", encoding="utf-8") as infile:
                links = infile.readlines()
                if self.filter_keyword:
                    links = [line for line in links if re.search(self.filter_keyword, line, re.I)]

                total_links = len(links)
                for idx, line in enumerate(links):
                    match = re.search(r'(https?://[^\s]+|/[\w\-\/]+/)', line)
                    if match:
                        url = match.group(1)
                        if url.startswith('/'):
                            full_url = urljoin(self.base_url, url)
                        else:
                            full_url = url

                        file_name = os.path.join(screenshot_dir, f"screenshot_{idx + 1}.png")
                        self.screenshot(full_url, file_name)
                    else:
                        skipped_links.append(line)

                    progress_percent = int((idx + 1) / total_links * 100)
                    self.progress.emit(progress_percent)

            self.log.emit(f"Обработка завершена. Скриншоты сохранены в {screenshot_dir}")

            if skipped_links:
                self.log.emit("Пропущенные строки:")
                for skipped in skipped_links:
                    self.log.emit(skipped.strip())

        except FileNotFoundError as e:
            self.log.emit(f"Файл не найден: {e}")
        finally:
            self.finished_signal.emit()

    def screenshot(self, url, file_name):
        geckodriver_path = ConfigManager.get_geckodriver_path()

        if not geckodriver_path or not os.path.exists(geckodriver_path):
            self.log.emit(f"Некорректный путь к geckodriver: {geckodriver_path}")
            return

        firefox_binary_path = ConfigManager.get_browser_path()
        if not firefox_binary_path or not os.path.exists(firefox_binary_path):
            self.log.emit(f"Некорректный путь к браузеру: {firefox_binary_path}")
            return

        options = Options()
        options.binary_location = firefox_binary_path
        options.headless = True

        service = Service(executable_path=geckodriver_path)
        driver = webdriver.Firefox(service=service, options=options)

        try:
            self.log.emit(f"Открытие страницы {url} для создания скриншота.")
            driver.get(url)

            # Дождаться полной загрузки страницы
            time.sleep(2)

            # Получить размер страницы
            total_height = driver.execute_script("return document.body.scrollHeight")
            driver.set_window_size(1920, total_height)
            time.sleep(2)

            screenshot = driver.save_screenshot(file_name)
            if screenshot:
                self.log.emit(f"Скриншот сохранен как {file_name}")
            else:
                self.log.emit(f"Ошибка при создании скриншота для {url}")
        except Exception as e:
            self.log.emit(f"Ошибка при создании скриншота для {url}: {e}")
        finally:
            driver.quit()

# Диалог для редактирования файла ссылок
class EditFileDialog(QtWidgets.QDialog):
    def __init__(self, file_path):
        super().__init__()
        self.setWindowTitle("Редактирование файла ссылок")
        self.setGeometry(150, 150, 600, 400)
        self.file_path = file_path
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.text_editor = QTextEdit()
        with open(self.file_path, "r", encoding="utf-8") as file:
            content = file.read()
        self.text_editor.setText(content)
        layout.addWidget(self.text_editor)

        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.save_file)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def save_file(self):
        new_content = self.text_editor.toPlainText().strip()
        with open(self.file_path, "w", encoding="utf-8") as file:
            file.write(new_content)
        QMessageBox.information(self, "Успех", "Файл успешно сохранен.")
        self.accept()

# Основное приложение с интерфейсом PyQt5
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Web Downloader & Screenshot Tool")
        self.setGeometry(100, 100, 800, 700)
        self.init_ui()

    def init_ui(self):
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Основной таб
        self.main_tab = QWidget()
        self.tab_widget.addTab(self.main_tab, "Основное")

        # Настройки таб
        self.settings_tab = QWidget()
        self.tab_widget.addTab(self.settings_tab, "Настройки")

        self.init_main_tab()
        self.init_settings_tab()

    def init_main_tab(self):
        layout = QVBoxLayout()

        # Ввод URL
        url_layout = QHBoxLayout()
        url_label = QLabel("Введите URL сайта:")
        self.url_input = QLineEdit()
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)

        # Кнопка обработки URL
        self.process_url_button = QPushButton("Обработать URL")
        self.process_url_button.clicked.connect(self.process_url)
        layout.addWidget(self.process_url_button)

        # Выбор файла ссылок
        file_layout = QHBoxLayout()
        self.file_button = QPushButton("Выбрать файл ссылок")
        self.file_button.clicked.connect(self.choose_file)
        self.file_label = QLabel("Файл не выбран")
        file_layout.addWidget(self.file_button)
        file_layout.addWidget(self.file_label)
        layout.addLayout(file_layout)

        # Редактирование файла ссылок
        self.edit_file_button = QPushButton("Просмотреть и редактировать ссылки")
        self.edit_file_button.clicked.connect(self.edit_file)
        layout.addWidget(self.edit_file_button)

        # Фильтр ссылок
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Фильтр ссылок (по href или title):")
        self.filter_input = QLineEdit()
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_input)
        layout.addLayout(filter_layout)

        # Выбор формата файла
        format_group = QGroupBox("Выберите формат файла для текста:")
        format_layout = QHBoxLayout()
        self.txt_radio = QRadioButton("TXT")
        self.txt_radio.setChecked(True)
        self.html_radio = QRadioButton("HTML")
        format_layout.addWidget(self.txt_radio)
        format_layout.addWidget(self.html_radio)
        format_group.setLayout(format_layout)
        layout.addWidget(format_group)

        # Выбор типа загрузки
        download_group = QGroupBox("Выберите тип загрузки:")
        download_layout = QHBoxLayout()
        self.pages_radio = QRadioButton("Скачать страницы")
        self.screenshots_radio = QRadioButton("Создать скриншоты")
        self.both_radio = QRadioButton("Скачать и страницы, и скриншоты")
        self.both_radio.setChecked(True)
        download_layout.addWidget(self.pages_radio)
        download_layout.addWidget(self.screenshots_radio)
        download_layout.addWidget(self.both_radio)
        download_group.setLayout(download_layout)
        layout.addWidget(download_group)

        # Кнопка начала обработки
        self.download_button = QPushButton("Начать")
        self.download_button.clicked.connect(self.start_processing)
        layout.addWidget(self.download_button)

        # Прогрессбар
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Лог вывода
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

        self.main_tab.setLayout(layout)

    def init_settings_tab(self):
        layout = QVBoxLayout()

        # Настройки путей
        settings_layout = QVBoxLayout()

        # Путь к geckodriver
        geckodriver_layout = QHBoxLayout()
        geckodriver_label = QLabel("Путь к geckodriver:")
        self.geckodriver_input = QLineEdit()
        self.geckodriver_browse_btn = QPushButton("Обзор...")
        self.geckodriver_browse_btn.clicked.connect(self.browse_geckodriver)
        geckodriver_layout.addWidget(geckodriver_label)
        geckodriver_layout.addWidget(self.geckodriver_input)
        geckodriver_layout.addWidget(self.geckodriver_browse_btn)
        settings_layout.addLayout(geckodriver_layout)

        # Путь к браузеру
        browser_layout = QHBoxLayout()
        browser_label = QLabel("Путь к браузеру:")
        self.browser_input = QLineEdit()
        self.browser_browse_btn = QPushButton("Обзор...")
        self.browser_browse_btn.clicked.connect(self.browse_browser)
        browser_layout.addWidget(browser_label)
        browser_layout.addWidget(self.browser_input)
        browser_layout.addWidget(self.browser_browse_btn)
        settings_layout.addLayout(browser_layout)

        # Кнопка сохранения настроек
        self.save_settings_btn = QPushButton("Сохранить настройки")
        self.save_settings_btn.clicked.connect(self.save_settings)
        settings_layout.addWidget(self.save_settings_btn)

        # Подсказка по путям
        self.path_hint = QLabel("Пример пути: C:/path/to/file.exe")
        self.path_hint.setStyleSheet("color: grey;")
        settings_layout.addWidget(self.path_hint)

        layout.addLayout(settings_layout)
        self.settings_tab.setLayout(layout)

        # Загрузка существующих настроек
        self.load_settings()

    def load_settings(self):
        config = ConfigManager.load_config()
        self.geckodriver_input.setText(config.get("geckodriver_path", ""))
        self.browser_input.setText(config.get("browser_path", ""))

    def save_settings(self):
        geckodriver_path = self.geckodriver_input.text()
        browser_path = self.browser_input.text()

        # Проверка существования путей
        if geckodriver_path and not os.path.exists(geckodriver_path):
            QMessageBox.warning(self, "Предупреждение", "Путь к geckodriver некорректен.")
            return
        if browser_path and not os.path.exists(browser_path):
            QMessageBox.warning(self, "Предупреждение", "Путь к браузеру некорректен.")
            return

        ConfigManager.set_geckodriver_path(geckodriver_path)
        ConfigManager.set_browser_path(browser_path)

        QMessageBox.information(self, "Успех", "Настройки сохранены успешно!")

    def browse_geckodriver(self):
        geckodriver_path, _ = QFileDialog.getOpenFileName(self, "Выбрать geckodriver", "", "Executable Files (*.exe)")
        if geckodriver_path:
            self.geckodriver_input.setText(geckodriver_path)

    def browse_browser(self):
        browser_path, _ = QFileDialog.getOpenFileName(self, "Выбрать браузер", "", "Executable Files (*.exe)")
        if browser_path:
            self.browser_input.setText(browser_path)

    def process_url(self):
        url = self.url_input.text()
        extension = "txt" if self.txt_radio.isChecked() else "html"
        filter_keyword = self.filter_input.text().strip()

        if not url:
            QMessageBox.warning(self, "Предупреждение", "Пожалуйста, введите URL.")
            return

        self.info = Info(url)
        file_with_links = self.info.save_html(extension, filter_keyword)

        if not file_with_links:
            QMessageBox.critical(self, "Ошибка", "Не удалось получить ссылки с сайта.")
            return

        self.file_path = file_with_links
        QMessageBox.information(self, "Успех", f"Ссылки успешно извлечены и сохранены в формате {extension}.")
        self.log(f"Ссылки с {url} были успешно извлечены в файл {file_with_links}")

    def choose_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выбрать файл ссылок", "", "Text Files (*.txt);;HTML Files (*.html)")
        if file_path:
            self.file_path = file_path
            self.file_label.setText(os.path.basename(file_path))
            self.log(f"Файл ссылок выбран: {file_path}")

    def edit_file(self):
        if not hasattr(self, 'file_path') or not self.file_path:
            QMessageBox.warning(self, "Предупреждение", "Сначала выберите файл ссылок.")
            return

        dialog = EditFileDialog(self.file_path)
        dialog.exec_()
        self.log(f"Файл ссылок {self.file_path} был отредактирован.")

    def start_processing(self):
        if not hasattr(self, 'file_path') or not self.file_path:
            QMessageBox.warning(self, "Предупреждение", "Пожалуйста, выберите или создайте файл ссылок.")
            return

        choice = ""
        if self.pages_radio.isChecked():
            choice = "pages"
        elif self.screenshots_radio.isChecked():
            choice = "screenshots"
        elif self.both_radio.isChecked():
            choice = "both"

        extension = "txt" if self.txt_radio.isChecked() else "html"
        filter_keyword = self.filter_input.text().strip()

        self.download_button.setEnabled(False)

        if choice in ["pages", "both"]:
            self.downloader_thread = DownloaderThread(
                self.file_path,
                self.url_input.text(),
                extension,
                filter_keyword
            )
            self.downloader_thread.progress.connect(self.update_progress)
            self.downloader_thread.log.connect(self.log)
            self.downloader_thread.finished_signal.connect(self.download_finished)
            self.downloader_thread.start()

        if choice in ["screenshots", "both"]:
            self.screenshot_thread = ScreenshotThread(
                self.file_path,
                self.url_input.text(),
                filter_keyword
            )
            self.screenshot_thread.progress.connect(self.update_progress)
            self.screenshot_thread.log.connect(self.log)
            self.screenshot_thread.finished_signal.connect(self.download_finished)
            self.screenshot_thread.start()

    def download_finished(self):
        self.download_button.setEnabled(True)
        QMessageBox.information(self, "Успех", "Задача выполнена!")
        self.log("Задача выполнена.")

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def log(self, message):
        self.log_output.append(message)

# Диалог для редактирования файла ссылок
class EditFileDialog(QtWidgets.QDialog):
    def __init__(self, file_path):
        super().__init__()
        self.setWindowTitle("Редактирование файла ссылок")
        self.setGeometry(150, 150, 600, 400)
        self.file_path = file_path
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.text_editor = QTextEdit()
        with open(self.file_path, "r", encoding="utf-8") as file:
            content = file.read()
        self.text_editor.setText(content)
        layout.addWidget(self.text_editor)

        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.save_file)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def save_file(self):
        new_content = self.text_editor.toPlainText().strip()
        with open(self.file_path, "w", encoding="utf-8") as file:
            file.write(new_content)
        QMessageBox.information(self, "Успех", "Файл успешно сохранен.")
        self.accept()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
