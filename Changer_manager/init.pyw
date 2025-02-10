import csv
import sys
import requests

from threading import Thread
from bs4 import BeautifulSoup

from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6 import QtCore

from main_window import MovieSplashScreen
from main_window import MainWidget


def timer_loading_screen():
    QtCore.QTimer.singleShot(4000, splash.close)
    QtCore.QTimer.singleShot(4000, ex.show)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    pathToGIF = "images/loading_gif.gif"
    splash = MovieSplashScreen(pathToGIF)
    splash.show()
    ex = MainWidget()
    thread_1 = Thread(target=ex.add_to_combo_boxes)
    thread_2 = Thread(target=timer_loading_screen)

    thread_1.start()
    thread_2.start()

    sys.exit(app.exec())
