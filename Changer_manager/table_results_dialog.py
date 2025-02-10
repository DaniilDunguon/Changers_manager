import os
import sqlite3
import csv
from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QTableWidgetItem, QHeaderView
from undetected_chromedriver import Chrome
from undetected_chromedriver.options import ChromeOptions
from undetected_chromedriver.webelement import By


class ParsingResults:
    def __init__(self, combobox_from, combobox_to, count_currency, status_parsing, marks_check):
        self.combobox_to = combobox_to
        self.combobox_from = combobox_from
        self.count_currency = count_currency
        self.status_parsing = status_parsing
        self.marks_check = marks_check

        driver_options = ChromeOptions()
        driver_options.add_argument("--headless=new")
        self.driver = Chrome(options=driver_options)

    def parsing_site(self):
        self.driver.get("https://www.okchanger.ru/")
        list_currencies = self.driver.find_element(By.ID, "left-panel").find_elements(By.TAG_NAME, 'li')
        array_currencies_from = [i.click() for i in list_currencies if i.text.strip() == self.combobox_from]

        list_currencies = self.driver.find_element(By.ID, "right-panel").find_elements(By.TAG_NAME, 'li')
        array_currencies_to = [i.click() for i in list_currencies if i.text.strip() == self.combobox_to]
        table_changers = self.driver.find_element(By.ID, "ExchangeDirectionsTableSelected")

        for i, block in enumerate(table_changers.find_elements(By.CLASS_NAME, "rates-table")):
            name = block.find_element(By.CLASS_NAME, "hidden-sm.hidden-xs.text-sm.cut-text").text
            post_currencies = block.find_element(By.NAME, "GiveAmount").text
            get_currencies = block.find_element(By.NAME, "TakeAmount").text
            negative_marks = block.find_element(By.CLASS_NAME, "negative.noclick").text
            positive_marks = block.find_element(By.CLASS_NAME, "positive.noclick").text
            if self.marks_check is True:
                all_changers_data = {
                    "имя": name,
                    "отношение оценок": f"{positive_marks} хор./{negative_marks} плох.",
                    "валюта": f"{self.combobox_from}/{self.combobox_to}",
                    "отношение": f"{post_currencies}/{get_currencies}",
                }
            else:
                all_changers_data = {
                    "имя": name,
                    "отношение оценок": "",
                    "валюта": f"{self.combobox_from}/{self.combobox_to}",
                    "отношение": f"{post_currencies}/{get_currencies}",
                }
            if i < 1:
                self.set_header_to_csv([all_changers_data], self.combobox_from, self.combobox_to)
            self.save_data_to_csv([all_changers_data], self.combobox_from, self.combobox_to)

        self.driver.close()

    def return_name_file(self):
        return f'csv_files/{self.combobox_from}-{self.combobox_to}.csv'

    def set_header_to_csv(self, data, from_val, to_val):
        with open(f'csv_files/{from_val}-{to_val}.csv', 'w', newline='', encoding="utf8") as f:
            writer = csv.DictWriter(
                f, fieldnames=list(data[0].keys()),
                delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
            writer.writeheader()

    def save_data_to_csv(self, data, from_val, to_val):
        with open(f'csv_files/{from_val}-{to_val}.csv', 'a', newline='', encoding="utf8") as f:
            writer = csv.DictWriter(
                f, fieldnames=list(data[0].keys()),
                delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
            for d in data:
                writer.writerow(d)


class DialogResult(QMainWindow):
    def __init__(self, name_file_csv):
        super().__init__()
        uic.loadUi('ui/yandex_project_dialog.ui', self)
        self.setWindowTitle("Лучшие обменники")
        self.name_file_csv = name_file_csv
        self.load_table()
        self.add_button_binds()

    def add_button_binds(self):
        self.save_table_account.clicked.connect(self.save_table_to_sql)
        self.load_csv.clicked.connect(self.open_csv_file)
        self.clear_db.clicked.connect(self.clear_table_from_sql)

    def open_csv_file(self):
        current_dir = os.getcwd()
        os.startfile(f"{current_dir}/{self.name_file_csv}")

    def clear_table_from_sql(self):
        connect = sqlite3.connect("sqlite/db.sqlite")
        curson = connect.cursor()
        request = """DELETE FROM Table_courses;
        """

        curson.execute(request)
        connect.commit()
        curson.close()

    def save_table_to_sql(self):
        connect = sqlite3.connect("sqlite/db.sqlite")
        curson = connect.cursor()
        request = """INSERT INTO Table_courses
                          (name, marks, valute, proportion) 
                           VALUES (?,?,?,?);"""

        with open(self.name_file_csv, encoding="utf8") as file:
            reader = csv.reader(file, delimiter=';', quotechar='"')
            for i, row in enumerate(reader):
                if i == 0:
                    continue

                curson.execute(request, tuple(row))
            connect.commit()
            curson.close()

    def load_table(self):
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_widget.resizeColumnsToContents()
        self.table_widget.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table_widget.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table_widget.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        for i in range(5):
            self.table_widget.setRowHeight(i, 51)

        with open(self.name_file_csv, encoding="utf8") as file:
            reader = csv.reader(file, delimiter=';', quotechar='"')
            for i, row in enumerate(reader):
                if i == 0:
                    continue
                self.table_widget.setRowCount(
                    self.table_widget.rowCount() + 1)
                for j, elem in enumerate(row):
                    self.table_widget.setItem(
                        i - 1, j, QTableWidgetItem(elem))
            self.table_widget.resizeColumnsToContents()
