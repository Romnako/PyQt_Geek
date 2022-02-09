import sys
import os
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication, QLabel, QTableView, QDialog, QPushButton, \
    QLineEdit, QFileDialog, QMessageBox
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt


def gui_create_model(database):
    '''
    GUI - Create a QModel table to display in the program window
    :param database:
    :return:
    '''
    list_users = database.active_users_list()
    list_tbl = QStandardItemModel()
    list_tbl.setHorizontalHeaderLabels(['Login client', 'IP address', 'Port', 'Connection time'])
    for row in list_users:
        user, ip, port, time = row
        user = QStandardItem(user)
        user.setEditable(False)
        ip = QStandardItem(ip)
        ip.setEditable(False)
        port = QStandardItem(str(port))
        port.setEditable(False)
        time = QStandardItem(str(time.replace(microsecond=0)))
        time.setEditable(False)
        list_tbl.appendRow([user, ip, port, time])
    return list_tbl


def create_stat_model(database):
    '''
    GUI - The function that implements filling the table with the history of messages.
    :param database:
    :return:
    '''
    hist_list = database.message_history

    list_row = QStandardItemModel()
    list_row.setHorizontalHeaderLabels(['Client Login', 'Last Login', 'Messages Sent', 'Messages Received'])
    for row in hist_list:
        user, last_seen, sent, recvd = row
        user = QStandardItem(user)
        user.setEditable(False)
        last_seen = QStandardItem(str(last_seen.replace(microsecond=0)))
        last_seen.setEditable(False)
        sent = QStandardItem(str(sent))
        sent.setEditable(False)
        recvd = QStandardItem(str(recvd))
        recvd.setEditable(False)
        list_row.appendRow([user, last_seen, sent, recvd])
    return list_row


def create_stat_login_history_model(database):
    '''

    :param database:
    :return:
    '''
    hist_list = database.login_history()
    list_row = QStandardItemModel()
    list_row.setHorizontalHeaderLabels(['Login', 'Login date', 'Client ip address', 'Client port'])
    for row in hist_list:
        user, last_seen, ip, port = row
        user = QStandardItem(user)
        user.setEditable(False)
        last_seen = QStandardItem(str(last_seen.replace(microsecond=0)))
        last_seen.setEditable(False)
        ip = QStandardItem(str(ip))
        ip.setEditable(False)
        port = QStandardItem(str(port))
        port.setEditable(False)
        list_row.appendRow([user, last_seen, ip, port])
    return list_row


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Exit button
        exitAction = QAction('Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(qApp.quit)

        self.refresh_button = QAction('Update List', self)
        self.show_history_button = QAction('Clients history', self)
        self.show_login_history_button = QAction('History of client connections', self)
        self.config_btn = QAction('Server Settings', self)

        # dock widget
        self.statusBar()

        self.toolbar = self.addToolBar('MainBar')
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.refresh_button)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.show_login_history_button)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.show_history_button)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.config_btn)
        self.toolbar.addSeparator()
        self.toolbar.addAction(exitAction)

        self.setFixedWidth(800, 600)
        self.setWindowTitle('Messaging Server alpha release')
        self.label = QLabel('List of connected clients:', self)
        self.label.setFixedSize(240, 15)
        self.label.move(10, 25)

        self.active_clients_table = QTableView(self)
        self.active_clients_table.move(10, 45)
        self.active_clients_table.setFixedSize(780, 400)

        self.show()


class HistoryWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Client statistic')
        self.setFixedSize(600, 700)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.close_button = QTableView(self)
        self.close_button.move(250, 650)
        self.close_button.clicked.connect(self.close)

        self.history_table = QTableView(self)
        self.history_table.move(10, 10)
        self.history_table.setFixedSize(580, 620)

        self.show()


class LoginHistoryWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Customer login history')
        self.setFixedSize(600, 700)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.close_button = QPushButton('Close', self)
        self.close_button.move(250, 650)
        self.close_button.clicked.connect(self.close)

        self.history_table = QTableView(self)
        self.history_table.move(10, 10)
        self.history_table.setFixedSize(580, 620)

        self.show()



class ConfigWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setFixedSize(365, 260)
        self.setWindowTitle('Server Settings')

        self.db_path_label = QLabel('Path to database file: ', self)
        self.db_path_label.move(10, 10)
        self.db_path_label.setFixedSize(240, 15)

        self.db_path = QLineEdit(self)
        self.db_path.setFixedSize(250, 20)
        self.db_path.move(10, 30)
        self.db_path.setReadOnly(True)

        self.db_path_select = QPushButton('Overview...', self)
        self.db_path_select.move(275, 28)

        def open_file_dialog():
            global dialog
            dialog = QFileDialog(self)
            path = dialog.getExistingDirectory()
            path = path.replace('/', '\\')
            self.db_path.insert(path)

        self.db_path_select.clicked.connect(open_file_dialog)

        self.db_file_label = QLabel('File name of database: ', self)
        self.db_file_label.move(10, 68)
        self.db_file_label.setFixedSize(180, 15)

        self.db_file = QLineEdit(self)
        self.db_file.move(200, 66)
        self.db_file.setFixedSize(150, 20)

        self.port_label = QLabel('Port number for connections:', self)
        self.port_label.move(10, 108)
        self.port_label.setFixedSize(180, 15)

        self.port = QLineEdit(self)
        self.port.move(200, 108)
        self.port.setFixedSize(150, 20)

        self.ip_label = QLabel('Ip accept connections:', self)
        self.ip_label.move(10, 148)
        self.ip_label.setFixedSize(180, 15)

        self.ip_label_note = QLabel(' Leave this field blank to accept connections from any address.', self)
        self.ip_label_note.move(10, 168)
        self.ip_label_note.setFixedSize(500, 30)

        self.ip = QLineEdit(self)
        self.ip.move(200, 148)
        self.ip.setFixedSize(150, 20)

        self.save_btn = QPushButton('Save', self)
        self.save_btn.move(190, 220)

        self.close_button = QPushButton('Close', self)
        self.close_button.move(275, 220)
        self.close_button.clicked.connect(self.close)

        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    message = QMessageBox
    dial = MainWindow()

    app.exec_()






