
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime, Text
from sqlalchemy.orm import mapper, sessionmaker
from Lesson_2_pyqt.lib.variables import *
import datetime


class ServerStorage:
    # Класс - отображение таблицы всех пользователей
    class AllUsers:
        def __init__(self, username):
            self.name = username
            self.last_login = datetime.datetime.now()
            self.id = None

    # Класс - отображение таблицы активных пользователей:
    class ActiveUsers:
        def __init__(self, user_id, ip_address, port, login_time):
            self.user = user_id
            self.ip_address = ip_address
            self.port = port
            self.login_time = login_time
            self.id = None

    # Класс - отображение таблицы истории входов
    class LoginHistory:
        def __init__(self, name, date, ip, port):
            self.id = None
            self.name = name
            self.date_time = date
            self.ip = ip
            self.port = port

    # Класс - отображение таблицы контактов пользователей
    class UsersContacts:
        def __init__(self, user, contact):
            self.id = None
            self.user = user
            self.contact = contact

    # Класс отображение таблицы истории действий
    class UsersHistory:
        def __init__(self, user):
            self.id = None
            self.user = user
            self.sent = 0
            self.accepted = 0

    def __init__(self, path):
        # Создаём движок базы данных
        print(path)
        self.database_engine = create_engine(f'sqlite:///{path}', echo=False, pool_recycle=POOL_RECYCLE,
                                             connect_args={'check_same_thread': False})

        # Создаём объект MetaData
        self.metadata = MetaData()

        # Создаём таблицу пользователей
        users_table = Table('Users', self.metadata,
                            Column('id', Integer, primary_key=True),
                            Column('name', String, unique=True),
                            Column('last_login', DateTime)
                            )

        # Создаём таблицу активных пользователей
        active_users_table = Table('Active_users', self.metadata,
                                   Column('id', Integer, primary_key=True),
                                   Column('user', ForeignKey('Users.id'), unique=True),
                                   Column('ip_address', String),
                                   Column('port', Integer),
                                   Column('login_time', DateTime)
                                   )

        # Создаём таблицу истории входов
        user_login_history = Table('Login_history', self.metadata,
                                   Column('id', Integer, primary_key=True),
                                   Column('name', ForeignKey('Users.id')),
                                   Column('date_time', DateTime),
                                   Column('ip', String),
                                   Column('port', String)
                                   )

        # Создаём таблицу контактов пользователей
        contacts = Table('Contacts', self.metadata,
                         Column('id', Integer, primary_key=True),
                         Column('user', ForeignKey('Users.id')),
                         Column('contact', ForeignKey('Users.id'))
                         )

        # Создаём таблицу истории пользователей
        users_history_table = Table('History', self.metadata,
                                    Column('id', Integer, primary_key=True),
                                    Column('user', ForeignKey('Users.id')),
                                    Column('sent', Integer),
                                    Column('accepted', Integer)
                                    )

        # Создаём таблицы
        self.metadata.create_all(self.database_engine)

        # Создаём отображения
        mapper(self.AllUsers, users_table)
        mapper(self.ActiveUsers, active_users_table)
        mapper(self.LoginHistory, user_login_history)
        mapper(self.UsersContacts, contacts)
        mapper(self.UsersHistory, users_history_table)

        # Создаём сессию
        Session = sessionmaker(bind=self.database_engine)
        self.session = Session()

        # Если в таблице активных пользователей есть записи, то их необходимо удалить
        self.session.query(self.ActiveUsers).delete()
        self.session.commit()

    # Функция выполняющяяся при входе пользователя, записывает в базу факт входа /  ключ
    def user_login(self, username, ip_address, port, key):
        rez = self.session.query(self.AllUsers).filter_by(name=username)
        # Если имя пользователя уже присутствует в таблице, обновляем время последнего входа
        if rez.count():
            user = rez.first()
            user.last_login = datetime.datetime.now()
            if user.pubkey != key:
                user.pubkey = key
        # Если нет - незареганным нельзя
        else:
            raise ValueError('Пользователь не зарегистрирован.')

        # Теперь можно создать запись в таблицу активных пользователей о факте входа.
        new_active_user = self.ActiveUsers(user.id, ip_address, port, datetime.datetime.now())
        self.session.add(new_active_user)
        # и сохранить в историю входов
        history = self.LoginHistory(user.id, datetime.datetime.now(), ip_address, port)
        self.session.add(history)
        # Сохраняем изменения
        self.session.commit()

    def add_user(self, name, passwd_hash):
        user_row = self.AllUsers(name, passwd_hash)
        self.session.add(user_row)
        self.session.commit()
        history_row = self.UsersHistory(user_row.id)
        self.session.add(history_row)
        self.session.commit()

    def remove_user(self, name):
        user = self.session.query(self.AllUsers).filter_by(name=name).first()
        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()
        self.session.query(self.LoginHistory).filter_by(name=user.id).delete()
        self.session.query(self.UsersContacts).filter_by(user=user.id).delete()
        self.session.query(self.UsersContacts).filter_by(contact=user.id).delete()
        self.session.query(self.UsersHistory).filter_by(user=user.id).delete()
        self.session.query(self.AllUsers).filter_by(name=name).delete()
        self.session.commit()

    def get_hash(self, name):
        user = self.session.query(self.AllUsers).filter_by(name=name).first()
        return user.passwd_hash

    def get_pubkey(self, name):
        user = self.session.query(self.AllUsers).filter_by(name=name).first()
        return user.pubkey

    def check_user(self, name):
        if self.session.query(self.AllUsers).filter_by(name=name).count():
            return True
        else:
            return False

    def user_logout(self, username):
        user = self.session.query(self.AllUsers).filter_by(name=username).first()
        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()
        self.session.commit()

    def process_message(self, sender, recipient):
        sender = self.session.query(self.AllUsers).filter_by(name=sender).first().id
        recipient = self.session.query(self.AllUsers).filter_by(name=recipient).first().id
        sender_row = self.session.query(self.UsersHistory).filter_by(user=sender).first()
        sender_row.sent += 1
        recipient_row = self.session.query(self.UsersHistory).filter_by(user=recipient).first()
        recipient_row.accepted += 1
        self.session.commit()

    def add_contact(self, user, contact):
        user = self.session.query(self.AllUsers).filter_by(name=user).first()
        contact = self.session.query(self.AllUsers).filter_by(name=contact).first()
        # Проверяем что не дубль и что контакт может существовать (полю пользователь мы доверяем)
        if not contact or self.session.query(self.UsersContacts).filter_by(user=user.id,
                                                                           contact=contact.id).count():
            return
        # Создаём объект и заносим его в базу
        contact_row = self.UsersContacts(user.id, contact.id)
        self.session.add(contact_row)
        self.session.commit()

    def remove_contact(self, user, contact):
        user = self.session.query(self.AllUsers).filter_by(name=user).first()
        contact = self.session.query(self.AllUsers).filter_by(name=contact).first()
        # Проверяем что контакт может существовать (полю пользователь мы доверяем)
        if not contact:
            return
        self.session.query(self.UsersContacts).filter(self.UsersContacts.user == user.id,
                                                      self.UsersContacts.contact == contact.id).delete()
        self.session.commit()

    def users_list(self):
        query = self.session.query(self.AllUsers.name, self.AllUsers.last_login)
        return query.all()

    def active_users_list(self):
        # Запрашиваем соединение таблиц и собираем кортежи имя, адрес, порт, время.
        query = self.session.query(
            self.AllUsers.name,
            self.ActiveUsers.ip_address,
            self.ActiveUsers.port,
            self.ActiveUsers.login_time
        ).join(self.AllUsers)
        return query.all()

    def login_history(self, username=None):
        # Запрашиваем историю входа
        query = self.session.query(self.AllUsers.name,
                                   self.LoginHistory.date_time,
                                   self.LoginHistory.ip,
                                   self.LoginHistory.port
                                   ).join(self.AllUsers)
        # Если было указано имя пользователя, то фильтруем по нему
        if username:
            query = query.filter(self.AllUsers.name == username)
        # Возвращаем список кортежей
        return query.all()

    # Функция возвращает список контактов пользователя.
    def get_contacts(self, username):
        user = self.session.query(self.AllUsers).filter_by(name=username).one()
        query = self.session.query(self.UsersContacts, self.AllUsers.name). \
            filter_by(user=user.id). \
            join(self.AllUsers, self.UsersContacts.contact == self.AllUsers.id)
        # выбираем только имена пользователей и возвращаем их.
        return [contact[1] for contact in query.all()]

    # Функция возвращает количество переданных и полученных сообщений
    def message_history(self):
        query = self.session.query(
            self.AllUsers.name,
            self.AllUsers.last_login,
            self.UsersHistory.sent,
            self.UsersHistory.accepted
        ).join(self.AllUsers)
        return query.all()

# Отладка
if __name__ == '__main__':
    test_db = ServerStorage()
    test_db.user_login('1111', '192.168.1.113', 8080)
    test_db.user_login('McG2', '192.168.1.113', 8081)
    print(test_db.users_list())
    # print(test_db.active_users_list())
    # test_db.user_logout('McG')
    # print(test_db.login_history('re'))
    # test_db.add_contact('test2', 'test1')
    # test_db.add_contact('test1', 'test3')
    # test_db.add_contact('test1', 'test6')
    # test_db.remove_contact('test1', 'test3')
    test_db.process_message('McG2', '1111')
    print(test_db.message_history())

# class ServerStorage:
#     '''
#     Class - server database
#     '''
#     class AllUsers:
#         '''
#         Class - displaying a table of all users
#         An instance of this class = an entry in the AllUsers table
#         '''
#         def __init__(self, user_id, ip_address, ip_port, login_time):
#             self.user_id = user_id
#             self.ip_address = ip_address
#             self.ip_port = ip_port
#             self.login_time = login_time
#             # self.users_login = users_login
#             self.id = None
#
#
#     class OnLineUsers:
#         '''
#         Class - displaying the table of active users:
#         An instance of this class = an entry in the ActiveUsers table
#         '''
#         def __init__(self, user_id, ip_address, ip_port, login_time):
#             self.user_id = user_id
#             self.ip_address = ip_address
#             self.ip_port = ip_port
#             self.login_time = login_time
#             self.id = None
#
#
#     class LoginHistory:
#         '''
#         Class - displaying the login history table
#         An instance of this class = an entry in the LoginHistory table
#         '''
#         def __init__(self, user_id, date, ip_address, ip_port):
#             self.id = None
#             self.user_id = user_id
#             self.date = date
#             self.ip_address = ip_address
#             self.ip_port = ip_port
#
#     def __init__(self):
#         # Creating a database engine
#         self.database_engine = create_engine(f'sqlite:///{path}', echo=False, pool_recycle=7200,
#                                              connect_args={'check_same_thread': False})
#         self.metadata =MetaData()
#
#         # Create users table
#         all_users_table = Table('All_Users', self.metadata,
#                                 Column('id', Integer, primary_key=True),
#                                 Column('login_name', String,unique=True),
#                                 Column('last_login', DateTime)
#                                 )
#
#         # Create online users table
#         online_users_table = Table('Online_users', self.metadata,
#                                    Column('id', Integer, primary_key=True),
#                                    Column('user_id', ForeignKey('All_Users.id'), unique=True),
#                                    Column('ip_address', String),
#                                    Column('ip_port', Integer),
#                                    Column('login_time', DateTime)
#                                    )
#
#         # History login user table
#         user_login_history = Table('Login_history', self.metadata,
#                                    Column('id', Integer, primary_key=True),
#                                    Column('user_id', ForeignKey('All_Users.id')),
#                                    Column('date_time', DateTime),
#                                    Column('ip_address', String),
#                                    Column('ip_port', String)
#                                    )
#
#         # Create table contact user
#         contacts = Table('Contacts', self.metadata,
#                          Column('id', Integer, primary_key=True),
#                          Column('user', ForeignKey('Users.id')),
#                          Column('contact', ForeignKey('Users.id'))
#                          )
#
#         # Create table history users
#         users_history_table = Table('History', self.metadata,
#                                     Column('id', Integer, primary_key=True),
#                                     Column('user', ForeignKey('Users.id')),
#                                     Column('sent', Integer),
#                                     Column('accepted', Integer)
#                                     )
#
#         #Create tables
#         self.metadata.create_all(self.database_engine)
#
#         mapper(self.AllUsers, all_users_table)
#         mapper(self.OnLineUsers, online_users_table)
#         mapper(self.LoginHistory, user_login_history)
#         mapper(self.UsersContacts, contacts)
#         mapper(self.UsersHistory, users_history_table)
#
#         Session = sessionmaker(bind=self.database_engine)
#         self.session = Session()
#
#         # When we establish a connection, clear the table of active users
#         self.session.query(self.OnLineUsers).delete()
#         self.session.commit()
#
#         # The function that is executed when the user logs in, writes the login fact to the database
#     def user_login(self, username, ip_address, ip_port):
#         server_logger.info(f'user_login: {username} {ip_address}:{ip_port}')
#         result = self.session.query(self.AllUsers).filter_by(login_name=username)
#         server_logger.debug(f'user_login result query:{result}')
#         if result.count():
#             user = result.first()
#             user.last_login = datetime.datetime.now()
#         else:
#             '''
#             We create an instance of the self.AllUsers class, through which we transfer data to the table
#             A commit is needed here to assign an ID
#             '''
#             server_logger.info(f'new_user,add to DB {username} {ip_address}:{ip_port}')
#             user = self.AllUsers(username)
#             self.session.add(user)
#             self.session.commit()
#
#         '''
#         Add the user to the active table and to the login history table
#         '''
#         new_active_user = self.OnLineUsers(user.id, ip_address, ip_port, datetime.datetime.now())
#         self.session.add(new_active_user)
#         history = self.LoginHistory(user.id, datetime.datetime.now(), ip_address, ip_port)
#         self.session.add(history)
#         self.session.commit()
#
#     def user_logout(self, username):
#         '''
#         The function fixing the disconnection of the user
#         :param username:
#         :return:
#         '''
#         user = self.session.query(self.OnLineUsers).filter_by(login_name=username).first()
#         print(f'Logout username {username} |{user}')
#
#         self.session.query(self.OnLineUsers).filter_by(user_id=user.id).delete()
#         self.session.commit()
#
#     def users_list(self):
#         '''
#         The function returns a list of known users with last login time.
#         :return:
#         '''
#         query = self.session.query(
#             self.AllUsers.login_name,
#             self.AllUsers.last_login,
#         )
#         return query.all()
#
#     def active_users_list(self):
#         '''
#         The function returns a list of active users
#         :return:
#         '''
#         query = self.session.query(
#             self.AllUsers.login_name,
#             self.OnLineUsers.ip_address,
#             self.OnLineUsers.ip_port,
#             self.OnLineUsers.login_time
#         ).join(self.AllUsers)
#         return query.all()
#
#     def login_history(self, username=None):
#         '''
#         Function returning login history by user or all users
#         :param username:
#         :return:
#         '''
#         query = self.session.query(self.AllUsers.login_name,
#                                    self.LoginHistory.date_time,
#                                    self.LoginHistory.ip_address,
#                                    self.LoginHistory.ip_port
#                                    ).join(self.AllUsers)
#         if username:
#             query = query.filter(self.AllUsers.login_name == username)
#         return query.all()
#
#     def get_contacts(self, username):
#
#         user = self.session.query(self.AllUsers).filter_by(name=username).one()
#         query = self.session.query(self.UsersContacts, self.AllUsers.name). \
#             filter_by(user=user.id). \
#             join(self.AllUsers, self.UsersContacts.contact == self.AllUsers.id)
#
#         return [contact[1] for contact in query.all()]
#
#
#     def message_history(self):
#         query = self.session.query(
#             self.AllUsers.name,
#             self.AllUsers.last_login,
#             self.UsersHistory.sent,
#             self.UsersHistory.accepted
#         ).join(self.AllUsers)
#         return query.all()
#
#
# if __name__ == '__main__':
#     test_db = ServerStorage()
#
#     print('---start server.active_users_list---')
#     print(test_db.active_users_list())
#
#     print('---adding users client_1 client_2 client_3 client_4---')
#     test_db.user_login('client_1', '192.168.1.4', '8888')
#     test_db.user_login('client_2', '192.168.1.5', '7777')
#     test_db.user_login('client_3', '192.168.0.0', '9999')
#     test_db.user_login('client_4', '192.168.4.4', '8888')
#
#     print('---active_users_list---')
#     print(test_db.active_users_list())
#
#     test_db.user_logout('client_1')
#     print(test_db.active_users_list())
#
#     print(test_db.login_history('client_1'))
#     print(test_db.users_list())





