from PyQt5.QtWidgets import QMainWindow, qApp, QMessageBox, QApplication, QListView
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor
from PyQt5.QtCore import pyqtSlot, QEvent, Qt
from PyQt5 import uic
import sys
import json
import logging
import time

sys.path.append(('../'))

from Lesson_2_pyqt.client.client_gui import AddContactDialog, DelContactDialog

from Lesson_2_pyqt.client.client_db import ClientDatabase
from Lesson_2_pyqt.client.transport import ClientTransport
from Lesson_2_pyqt.lib.errors import ServerError


logger = logging.getLogger('client')



class ClientMainWindow(QMainWindow):
    def __init__(self, database, transport):
        super().__init__()
        self.database = database
        self.transport = transport

        self.ui = uic.loadUi('client/client_main_gui.ui', self)
        # self.ui = UI_MainClientWindow()
        # self.ui.setupUi(self)

        self.ui.menu_exit.triggered.connect(qApp.exit)
        self.ui.btn_send.clicked.connect(self.send_message)

        self.ui.btn_add_contact.clicked.connect(self.add_contact_window)
        self.ui.menu_del_contact.triggered.connect(self.delete_contaact_window)

        self.contacts_model = None
        self.history_model = None
        self.message = QMessageBox()
        self.current_chat = None
        self.ui.list_messages.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ui.list_messages.setWordWrap(True)

        self.ui.list_contacts.doubleClick.connect(self.select_active_user)

        self.clients_list_update()
        self.set_disabled_input()
        self.show()


    def set_disabled_input(self):
        self.ui.label_new_message.setText('To select a recipient, double-click on it in the contact window.')
        self.ui.text_message.clear()
        if self.history_model:
            self.history_model.clear()

        self.ui.btn_clear.setDisabled(True)
        self.ui.btn_send.setDisabled(True)
        self.ui.text_message.setDisabled(True)


    def History_list_update(self):
        list = sorted(self.database.get_history(self.current_chat), key=lambda item: item[3])
        if not self.history_model:
            self.history_model = QStandardItemModel()
            self.ui.list_messages.setModel(self.history_model)

            self.history_model.clear()

            length = len(list)
            start_index = 0
            if length > 20:
                start_index = length - 20

            for i in range(start_index, length):
                item = list[i]
                if item[1] == 'in':
                    mess = QStandardItem(f'Input message {item[3].replace(microsecond=0)}:\n {item[2]}')
                    #mess = setEditable(False)
                    mess.setBackground(QBrush(QColor(255, 213, 213)))
                    mess.setTextAlignment(Qt.AlignLeft)
                    self.history_model.appendRow(mess)
                else:
                    mess = QStandardItem(f'Send message {item[3].replace(microsecond=0)}:\n {item[2]}')
                    mess.setEditable(False)
                    mess.setTextAlignment(Qt.AlignRight)
                    mess.setBackground(QBrush(QColor(204, 255, 204)))
                    self.history_model.appendRow(mess)
                self.ui.list_messages.scrollToBottom()


    def select_active_user(self):
        self.current_chat = self.ui.list_contacts.currentIndex().data()
        self.set_active_user()


    def set_active_user(self):
        self.ui.label_new_message.setText(f'Input message for... {self.current_chat}:')
        self.ui.btn_clear.setDisabled(False)
        self.ui.btn_send.setDisabled(False)
        self.ui.text_message.setDisabled(False)

        self.history_list_update()


    def clients_list_update(self):
        contacts_list = self.database.get_contacts()
        self.contacts_model = QStandardItemModel()
        for i in sorted(contacts_list):
            item = QStandardItem(i)
            item.setEditable(False)
            self.contacts_model.appendRow(item)
        self.ui.list_contacts.setModel(self.contacts_model)


    def add_contact_window(self):
        global select_dialog
        select_dialog = AddContactDialog(self.transport, self.database)
        select_dialog.btn_ok.clicked.connect(lambda: self.add_contact_action(select_dialog))
        select_dialog.show()


    def add_contact_action(self, item):
        new_contact = item.selector.currentText()
        self.add_contact(new_contact)
        item.close()


    def add_contact(self, new_contact):
        try:
            self.transport.add_contact(new_contact)
        except ServerError as err:
            self.messages.critical(self, 'Server error', err.text)
        except OSError as err:
            if err.errno:
                self.messages.critical(self, 'Error', 'Lost connection to server!')
                self.close()
            self.messages.critical(self, 'Error', 'Timeout connect!')
        else:
            self.database.add_contact(new_contact)
            new_contact = QStandardItem(new_contact)
            new_contact.setEditable(False)
            self.contacts_model.appendRow(new_contact)
            logger.info(f'Successfully added contact {new_contact}')
            self.messages.information(self, 'success', 'Contact added successfully.')


    def delete_contact_window(self):
        global remove_dialog
        remove_dialog = DelContactDialog(self.database)
        remove_dialog.btn_ok.clicked.connect(lambda: self.delete_contact(remove_dialog))
        remove_dialog.show()


    def delete_contact(self, item):
        selected = item.selector.currentText()
        try:
            self.transport.remove_contact(selected)
        except ServerError as err:
            self.messages.critical(self, 'Server error', err.text)
        except OSError as err:
            if err.errno:
                self.messages.critical(self, 'success', 'Contact added successfully.')
                self.close()
            self.messages.critical(self, 'Error', 'Connection timeout')
        else:
            self.database.del_contact(selected)
            self.clients_list_update()
            logger.info(f'Successfully deleted contact {selected}')
            self.messages.information(self, 'Success', 'Successfully deleted contact')
            item.close()
            if selected == self.current_chat:
                self.current_chat = None
                self.set_disabled_input()


    def send_message(self):
        message_text = self.ui.text_message.toPlainText()
        self.ui.text_message.clear()
        if not message_text:
            return
        try:
            self.transport.send_message(self.current_chat, message_text)
            pass
        except ServerError as err:
            self.messages.critical(self, 'Error', err.text)
        except OSError as err:
            if err.errno:
                self.messages.critical(self, 'Error', 'Lost connection to server!')
                self.close()
            self.messages.critical(self, 'Error', 'Connection timeout!')
        except (ConnectionResetError, ConnectionAbortedError):
            self.messages.critical(self, 'Error', 'Lost connection to server!')
            self.close()
        else:
            self.database.save_message(self.current_chat, 'out', message_text)
            logger.debug(f'Send message for {self.current_chat}: {message_text}')
            self.history_list_update()


    @pyqtSlot(str)
    def message(self, sender):
        if sender == self.current_chat:
            self.history_list_update()
        else:
            # Проверим есть ли такой пользователь у нас в контактах:
            if self.database.check_contact(sender):
                # Если есть, спрашиваем и желании открыть с ним чат и открываем при желании
                if self.messages.question(self, 'New message', \
                                          f'New message received from {sender}, open chat with him?',
                                          QMessageBox.Yes,
                                          QMessageBox.No) == QMessageBox.Yes:
                    self.current_chat = sender
                    self.set_active_user()
            else:
                print('NO')
                if self.messages.question(self, 'New message',
                                          f'New message received from {sender}.\n '
                                          f'This user is not in your contact list.\n '
                                          f'Add to contacts and open a chat with him?',
                                          QMessageBox.Yes,
                                          QMessageBox.No) == QMessageBox.Yes:
                    self.add_contact(sender)
                    self.current_chat = sender
                    self.set_active_user()


    @pyqtSlot()
    def connection_lost(self):
        self.messages.warning(self, 'Connection failed', 'Lost connection to server.')
        self.close()

    def make_connection(self, trans_obj):
        trans_obj.new_message.connect(self.message)
        trans_obj.connection_lost.connect(self.connection_lost)



