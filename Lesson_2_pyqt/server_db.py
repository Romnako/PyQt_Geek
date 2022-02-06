from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData,ForeignKey,DateTime
from sqlalchemy.orm import mapper, sessionmaker
from Lesson_2_pyqt.lib.variables import *
import datetime
import Lesson_2_pyqt.logs.config_server_log

SERVER_LOGGER = logging.getLogger('server')


class ServerStorage:
    '''
    Class - server database
    '''
    class AllUsers:
        '''
        Class - displaying a table of all users
        An instance of this class = an entry in the AllUsers table
        '''
        def __init__(self, user_id, ip_address, ip_port, login_time):
            self.user_id = user_id
            self.ip_address = ip_address
            self.ip_port = ip_port
            self.login_time = login_time
            self.id = None


    class OnLineUsers:
        '''
        Class - displaying the table of active users:
        An instance of this class = an entry in the ActiveUsers table
        '''
        def __init__(self, user_id, ip_address, ip_port, login_time):
            self.user_id = user_id
            self.ip_address = ip_address
            self.ip_port = ip_port
            self.login_time = login_time
            self.id = None


    class LoginHistory:
        '''
        Class - displaying the login history table
        An instance of this class = an entry in the LoginHistory table
        '''
        def __init__(self, user_id, date, ip_address, ip_port):
            self.id = None
            self.user_id = user_id
            self.date = date
            self.ip_address = ip_address
            self.ip_port = ip_port

    def __init__(self):
        # Creating a database engine
        self.database_engine = create_engine(SERVER_DATABASE, echo=False, pool_recycle=3600)
        self.metadata =MetaData()

        # Create users table
        all_users_table = Table('All_Users', self.metadata,
                                Column('id', Integer, primary_key=True),
                                Column('login_name', String,unique=True),
                                Column('last_login', DateTime)
                                )

        # Create online users table
        online_users_table = Table('Online_users', self.metadata,
                                   Column('id', Integer, primary_key=True),
                                   Column('user_id', ForeignKey('All_Users.id'), unique=True),
                                   Column('ip_address', String),
                                   Column('ip_port', Integer),
                                   Column('login_time', DateTime)
                                   )

        # History login user table
        user_login_history = Table('Login_history', self.metadata,
                                   Column('id', Integer, primary_key=True),
                                   Column('user_id', ForeignKey('All_Users.id')),
                                   Column('date_time', DateTime),
                                   Column('ip_address', String),
                                   Column('ip_port', String)
                                   )

        #Create tables
        self.metadata.create_all(self.database_engine)

        mapper(self.AllUsers, all_users_table)
        mapper(self.OnLineUsers, online_users_table)
        mapper(self.LoginHistory, user_login_history)

        Session = sessionmaker(bind=self.database_engine)
        self.session = Session()

        # When we establish a connection, clear the table of active users
        self.session.query(self.OnLineUsers).delete()
        self.session.commit()

        # The function that is executed when the user logs in, writes the login fact to the database
    def user_login(self, username, ip_address, ip_port):
        SERVER_LOGGER.info(f'user_login: {username} {ip_address}:{ip_port}')
        result = self.session.query(self.AllUsers).filter_by(login_name=username)
        SERVER_LOGGER.debug(f'user_login result query:{result}')
        if result.count():
            user = result.first()
            user.last_login = datetime.datetime.now()
        else:
            '''
            We create an instance of the self.AllUsers class, through which we transfer data to the table
            A commit is needed here to assign an ID
            '''
            SERVER_LOGGER.info(f'new_user,add to DB {username} {ip_address}:{ip_port}')
            user = self.AllUsers(username)
            self.session.add(user)
            self.session.commit()

        '''
        Add the user to the active table and to the login history table
        '''
        new_active_user = self.OnLineUsers(user.id, ip_address, ip_port, datetime.datetime.now())
        self.session.add(new_active_user)
        history = self.LoginHistory(user.id, datetime.datetime.now(), ip_address, ip_port)
        self.session.add(history)
        self.session.commit()

    def user_logout(self, username):
        '''
        The function fixing the disconnection of the user
        :param username:
        :return:
        '''
        user = self.session.query(self.OnLineUsers).filter_by(login_name=username).first()
        print(f'Logout username {username} |{user}')

        self.session.query(self.OnLineUsers).filter_by(user_id=user.id).delete()
        self.session.commit()

    def users_list(self):
        '''
        The function returns a list of known users with last login time.
        :return:
        '''
        query = self.session.query(
            self.AllUsers.login_name,
            self.AllUsers.last_login,
        )
        return query.all()

    def active_users_list(self):
        '''
        The function returns a list of active users
        :return:
        '''
        query = self.session.query(
            self.AllUsers.login_name,
            self.OnLineUsers.ip_address,
            self.OnLineUsers.ip_port,
            self.OnLineUsers.login_time
        ).join(self.AllUsers)
        return query.all()

    def login_history(self, username=None):
        '''
        Function returning login history by user or all users
        :param username:
        :return:
        '''
        query = self.session.query(self.AllUsers.login_name,
                                   self.LoginHistory.date_time,
                                   self.LoginHistory.ip_address,
                                   self.LoginHistory.ip_port
                                   ).join(self.AllUsers)
        if username:
            query = query.filter(self.AllUsers.login_name == username)
        return query.all()



if __name__ == '__main__':
    test_db = ServerStorage()

    print('---start server.active_users_list---')
    print(test_db.active_users_list())

    print('---adding users client_1 client_2 client_3 client_4---')
    test_db.users_login('client_1', '192.168.1.4', '8888')
    test_db.users_login('client_2', '192.168.1.5', '7777')
    test_db.users_login('client_3', '192.168.0.0', '9999')
    test_db.users_login('client_4', '192.168.4.4', '8888')

    print('---active_users_list---')
    print(test_db.active_users_list())

    test_db.user_logout('client_1')
    print(test_db.active_users_list())

    print(test_db.login_history('client_1'))
    print(test_db.users_list())





