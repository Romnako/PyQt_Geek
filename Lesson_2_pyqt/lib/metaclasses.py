import dis


class ServerMaker(type):
    '''
    ���������, ����������� ��� � �������������� ������ ��� ����������
    ������� ����� ���: connect. ����� �����������, ��� ���������
    ����� �������� TCP � �������� �� IPv4 ���������.
    '''

    def __init__(cls, clsname, bases, clsdict):
        methods = []
        attributes = []
        for func in clsdict:
            try:
                ret = dis.get_instructions(clsdict[func])
            except TypeError:
                pass
            else:
                for i in ret:
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            methods.append(i.argval)
                    elif i.opname == 'LOAD_ATTR':
                        if i.argval not in attributes:
                            attributes.append(i.argval)
        if 'connect' in methods:
            raise TypeError('������������� ������ connect ����������� � ��������� ������')
        if not ('SOCK_STREAM' in attributes and 'AF_INET' in attributes):
            raise TypeError('������������ ������������� ������.')
        super().__init__(clsname, bases, clsdict)


class ClientMaker(type):
    '''
     ���������, ����������� ��� � �������������� ������ ��� ���������
    ������� ����� ���: accept, listen. ����� �����������, ��� ����� ��
    �������� ������ ������������ ������.
    '''

    def __init__(cls, clsname, bases, clsdict):
        methods = []
        for func in clsdict:
            try:
                ret = dis.get_instructions(clsdict[func])
            except TypeError:
                pass
            else:
                for i in ret:
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            methods.append(i.argval)
        for command in ('accept', 'listen', 'socket'):
            if command in methods:
                raise TypeError('� ������ ���������� ������������� ������������ ������')
        if 'get_message' in methods or 'send_message' in methods:
            pass
        else:
            raise TypeError('����������� ������ �������, ���������� � ��������.')
        super().__init__(clsname, bases, clsdict)