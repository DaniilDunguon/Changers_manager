import csv
import os
import webbrowser

from bs4 import BeautifulSoup
import requests

from table_results_dialog import DialogResult, ParsingResults

from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6 import QtCore
from PyQt6.QtWidgets import QMainWindow, QSplashScreen, QWidget, QLabel
from PyQt6.QtGui import QFont, QColor, QMovie, QPixmap, QPainter


class MovieSplashScreen(QSplashScreen):

    def __init__(self, pathToGIF: str):
        self.movie = QMovie(pathToGIF)
        self.movie.jumpToFrame(0)
        pixmap = QPixmap(self.movie.frameRect().size())
        QSplashScreen.__init__(self, pixmap)
        self.movie.frameChanged.connect(self.repaint)

    def showEvent(self, event):
        self.movie.start()

    def hideEvent(self, event):
        self.movie.stop()

    def paintEvent(self, event):
        painter = QPainter(self)
        pixmap = self.movie.currentPixmap()
        self.setMask(pixmap.mask())
        painter.drawPixmap(1, 1, pixmap)


class MainWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/yandex_project.ui', self)
        self.setWindowTitle("Обменники")
        self.build()

    def build(self):
        self.set_fonts()
        self.set_styles_main()
        self.buttons_connect()

    def buttons_connect(self):
        self.accept_top_courses.clicked.connect(self.show_result_root)
        self.show_saved_courses.clicked.connect(self.load_courses_to_downloading_folder)
        self.source_site.clicked.connect(self.open_link_site)
        self.github.clicked.connect(self.open_link_github)

    def show_result_root(self):
        try:
            self.status_parsing.setText("Ожидание")
            Parser = ParsingResults(self.return_combobox_from(),
                                    self.return_combobox_to(),
                                    self.return_count_currency(),
                                    self.return_status_parsing(),
                                    self.return_state_check_marks())
            Parser.parsing_site()
            self.dialog_win = DialogResult(Parser.return_name_file())
            self.dialog_win.show()
            self.status_parsing.setText("Успех")
        except Exception:
            self.status_parsing.setText("Не успех")

    def open_link_github(self):
        webbrowser.open("https://github.com/DaniilDunguon/Changers_manager")

    def open_link_site(self):
        webbrowser.open("https://www.okchanger.ru/")


    def load_courses_to_downloading_folder(self):
        current_dir = os.getcwd()
        os.startfile(f"{current_dir}/csv_files")

    """ CONSTANT DATA SET """

    def set_fonts(self):
        self.FONT_FOR_BUTTONS = QFont("Roboto", 12)

    def set_styles_main(self):
        self.get_combobox.setFont(self.FONT_FOR_BUTTONS)
        self.post_combobox.setFont(self.FONT_FOR_BUTTONS)

    """ CONSTANT DATA RETURN """

    def return_currencies(self):
        header = {"User-Agent":
                      "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0"}
        url = requests.get("https://www.okchanger.ru/", headers=header)
        page = BeautifulSoup(url.text, "lxml")

        list_currencies = page.find(id="left-panel").find_all("li", class_="")
        self.array_currencies_from = [i.text.strip() for i in list_currencies]

        list_currencies = page.find(id="right-panel").find_all("li", class_="")
        self.array_currencies_to = [i.text.strip() for i in list_currencies]

    def add_to_combo_boxes(self):
        self.return_currencies()
        for i in range(len(self.array_currencies_from)):
            self.add_combo_box_item(self.post_combobox, self.array_currencies_from[i])

        for i in range(len(self.array_currencies_to)):
            self.add_combo_box_item(self.get_combobox, self.array_currencies_to[i])

    def add_combo_box_item(self, combobox, item):
        combobox.addItem(item)

    """ DYMANIC DATA RETURN """

    def return_combobox_from(self):
        return self.post_combobox.currentText()

    def return_combobox_to(self):
        return self.get_combobox.currentText()

    def return_count_currency(self):
        return self.count_valute.value()

    def return_status_parsing(self):
        return self.status_parsing.text

    def return_state_check_marks(self):
        return self.check_marks.isChecked()