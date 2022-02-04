import logging

SERVER_LOGGER = logging.getLogger('server')


class PortValidate:
    def __set__(self, instance, value):
        try:
            ip_port = int(value)
            if ip_port < 1025 or ip_port > 65535:
                SERVER_LOGGER.critical(f'The port must be between 1024 and 65535. Trying to start with port {value}')
                exit(1)
            else:
                instance.__dict__[self.name] = value
                '''The port passed the test, add it to the list of instance attributes '''
        except:
            SERVER_LOGGER.critical(
                f'The port must be an integer between 1024 and 65535. Attempt to start with port {value}')
            exit(1)

    def __set_name__(self, owner, name):
        self.name = name


class IpValidate:
    def __set__(self, instance, value):
        tmp_str = value.split('.')
        if len(tmp_str) != 4:
            SERVER_LOGGER.critical(f'Incorrect IP address: {value}')
            exit(1)
        for el in tmp_str:
            if not el.isdigit():
                SERVER_LOGGER.critical(f'Incorrect IP address: {value}')
                exit(1)
            i = int(el)
            if i < 0 or i > 255:
                SERVER_LOGGER.critical(f'Incorrect IP address: {value}')
                exit(1)
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name
