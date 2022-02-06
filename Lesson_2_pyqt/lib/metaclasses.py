import dis

'''Metaclass for server matching'''
class ServerMaker(type):
    def __init__(self, clsname, bases, clsdict):
        '''

        :param clsname: metaclass instance - Server
        :param bases: base class tuple - ()
        :param clsdict: dictionary of attributes and methods of a metaclass instance
        '''

        methods = []
        attributes = []

        for func_element in clsdict:
            try:
                res = dis.get_instructions(clsdict[func_element])
            except TypeError:
                pass
            else:
                for res_el in res:
                    #print(res_el)
                    if res_el.opname == 'LOAD_GLOBAL':
                        # opname- operation name
                        if res_el.argval not in methods:
                            methods.append(res_el.argval)
                    elif res_el.opname =='LOAD_ATTR':
                        if res_el.argval not in attributes:
                            attributes.append(res_el.argval)
        # print(f'attributes={attributes}')
        # print(f'methods={methods}')

        if connect.lower() in methods:
            raise TypeError("Server class cannot use 'connect' method")
        if not ('socket_transport'.lower() in attributes and 'create_socket'.lower() in methods):
            raise TypeError('Incorrect socket initialization.')
        super().__init__(clsname, bases, clsdict)


'''Metaclass for client validation'''
class ClientMaker(type):
    def __init__(self, clsname, base, clsdict):
        """

        :param clsname: metaclass instance - Client
        :param base: base class tuple - ()
        :param clsdict: dictionary of attributes and methods of a metaclass instance
        """
        methods = []
        for func in clsdict:
            try:
                res = dis.get_instructions(clsdict[func])
            except TypeError:
                pass
            else:
                for res_el in res:
                    if res_el.opname == 'LOAD_GLOBAL':
                        if res_el.argval not in methods:
                            methods.append(res_el.argval)

        for command in ('accept', 'listen', 'socket'):
            if command in methods:
                raise TypeError('The use of a forbidden method was detected in the class')

            if 'get_message' in methods or 'send_message' in methods:
                pass
            else:
                raise TypeError('There are no socket function calls.')
            super().__init__(clsname, bases, clsdict)
