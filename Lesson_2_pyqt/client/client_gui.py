import sys
import logging
from PyQt5.QtWidgets import QWidget, QApplication, qApp, QMainWindow, QDialog
from PyQt5 import uic

logger = logging.getLogger('client')


class UI_StartLoginDlg(QDialog):
    def __init__(self):
        super().__init__()
        self.ok_pressed = False
        uic.loadUi('client/client_start_dialog.ui', self)

        self.btn_ok.clicked.connect(self.ok_click)
        self.btn_cancel.clicked.connect(qApp.exit)
        self.show()

    def ok_click(self):
        if self.client_name.text():
            self.ok.pressed = True
            qApp.exit()


class AddContactDialog(QDialog):
    def __init__(self, transport, database):
        super().__init__()
        self.transport = transport
        self.database = database
        self.ui = uic.loadUi('client/client_add_contact_dialog.ui', self)

        self.btn_cancel.clicked.connect(self.close)
        self.btn_refresh.clicked.connect(self.update_possible_contacts)
        self.possible_contacts_update()


    def possible_contacts_update(self):
        self.selector.clear()
        contacts_list = set(self.database.get_contacts())
        user_list = set(self.database.get_users)
        user_list.remove(self.transport.username)
        self.selector.addItems(user_list - contacts_list)


    def update_possible_contacts(self):
        try:
            self.transport.user_list_update()
        except OSError:
            pass
        else:
            logger.debug('User list updated from server completed')
            self.possible_contacts_update()



class DelContactDialog(QDialog):
    def __init__(self, database):
        super().__init__()
        self.database = database
        self.ui = uic.loadUi('client/client_del_contact_dialog.ui', self)
        self.selector.addItems(sorted(self.database.get_contacts()))
        self.btn_cancel.clicked.connect(self.close)



if __name__ == '__main__':
    APP = QApplication(sys.argv)

    WINDOW_OBJ = StartLoginDlg()
    WINDOW_OBJ.show()
    a = WINDOW_OBJ.client_name.text()

    print(a)

    WINDOW_OBJ.client_name.setText(a)

    sys.exit(APP.exec_())



