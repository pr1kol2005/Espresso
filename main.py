import sqlite3
import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QDialog


class MainCoffee(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.connection = sqlite3.connect("coffee.db")
        self.pushButton.clicked.connect(self.select_data)
        self.addEditBt.clicked.connect(self.addEditData)
        self.textEdit.setPlainText("SELECT * FROM info")
        self.select_data()

    def select_data(self):
        query = self.textEdit.toPlainText()
        res = self.connection.cursor().execute(query).fetchall()
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setRowCount(0)
        for i, row in enumerate(res):
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(
                    i, j, QTableWidgetItem(str(elem)))

    def closeEvent(self, event):
        self.connection.close()

    def addEditData(self):
        prikol = AddEditCoffeeWidget(self)
        prikol.exec()


class AddEditCoffeeWidget(QDialog):
    def __init__(self, MasterWidget):
        super().__init__()
        uic.loadUi("addEditCoffeeForm.ui", self)
        self.con = MasterWidget.connection
        self.pushButton.clicked.connect(self.update_result)
        self.tableWidget.itemChanged.connect(self.item_changed)
        self.pushButton_2.clicked.connect(self.save_results)
        self.modified = {}
        self.titles = None

    def update_result(self):
        cur = self.con.cursor()
        result = cur.execute("SELECT * FROM info WHERE id=?",
                             (item_id := self.spinBox.text(),)).fetchall()
        self.tableWidget.setRowCount(len(result))
        if not result:
            return
        self.tableWidget.setColumnCount(len(result[0]))
        self.titles = [description[0] for description in cur.description]
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
        self.modified = {}

    def item_changed(self, item):
        self.modified[self.titles[item.column()]] = item.text()

    def save_results(self):
        if self.modified:
            que = "UPDATE info SET\n"
            que += ", ".join([f"{key}='{self.modified.get(key)}'"
                              for key in self.modified.keys()])
            que += "WHERE id = ?"
            print(que)
            self.con.cursor().execute(que, (self.spinBox.text(),))
            self.con.commit()
            self.modified.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainCoffee()
    ex.show()
    sys.exit(app.exec())
