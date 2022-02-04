from subprocess import Popen, CREATE_NEW_CONSOLE

P_LIST = []

while True:
    USER = input('Start clients (s) / Close clients (k) / Exit (q)')

    if USER == 'q':
        break

    elif USER == 's':
        P_LIST.append(Popen('python server.py', creationflags=CREATE_NEW_CONSOLE))
        P_LIST.append(Popen('python client.py', creationflags=CREATE_NEW_CONSOLE))
        P_LIST.append(Popen('python client.py -l', creationflags=CREATE_NEW_CONSOLE))
        P_LIST.append(Popen('python client.py -l', creationflags=CREATE_NEW_CONSOLE))

        print('Several listen clients are running')
    elif USER == 'k':
        for p in P_LIST:
            p.kill()
        P_LIST.clear()