import ipaddress
import socket
import os
from platform import system
import subprocess
import chardet


def os_ping(ip_adr):
    oper = system()  #OS version, to determine the ping method

    DNULL = open(os.devnull, "w")

    if (oper == "Windows"):
        try:
            status = subprocess.call(["ping", "-n", "1", str(ip_adr)], stdout=DNULL)
            res_bytes = subprocess.check_output(f'ping -n 1 {str(ip_adr)}')
            code_dic = chardet.detect(res_bytes)
            res_str = res_bytes.decode(code_dic['encoding']).encode('utf-8')
            res = res_str.decode('utf-8')
            status = res.find('TTL=')
            if status >= 0:
                status = 0
                #print(f'Correct ping {status}')
            else:
                status = 1
        except:
            status = 1
            #print(f'Except Incorrect ping {status}')
    else:
        status = subprocess.call(["ping", "-c", "1", str(ip_adr)], stdout=DNULL)
    print(f"{ip_adr} | status={status}")
    return status

def host_ping(v_loop_ip):
    """ The function will create address availability dictionaries """
    succes_request = "Network node is accesible"
    fail_request = "Network  node is not accesible"
    fail_ip_adr = "Hostname is incorrect"

    columns = ['address', 'result']
    result = []

    print("Scanner launched...")

    i = 0
    for ip in v_loop_ip:
        request_dic = dict()
        try:
            ip_adr = ipaddress.ip_address(ip)
            status = os_ping(ip_adr)
            if status == 0:
                request_dic[columns[0]] = str(ip_adr)
                request_dic[columns[1]] = succes_request
            else:
                request_dic[columns[0]] = str(ip_adr)
                request_dic[columns[1]] = fail_request
        except:
            try:
                ip_adr = socket.gethostbyname(ip)
                status = os_ping(ip_adr)
                if status == 0:
                    request_dic[columns[0]] = str(ip)
                    request_dic[columns[1]] = succes_request
                else:
                    request_dic[columns[0]] = str(ip)
                    request_dic[columns[1]] = fail_request
            except:
                request_dic[columns[0]] = str(ip)
                request_dic[columns[1]] = fail_ip_adr
        result.append(request_dic)
        print(f"{result[i][columns[0]]} | {result[i][columns[1]]}")
        i += 1
    return result
if __name__ == '__main__':

    loop_ip = ['192.168.1.1', 'geekbrains.ru', '127.0.0.1', '192.168.0.1', '192.168.1.126', '127', 'ya.ru']
    host_ping(loop_ip)
    print("FINISH")

'''
Scanner launched...
192.168.1.1 | status=1
192.168.1.1 | Network  node is not accesible
178.248.232.209 | status=0
geekbrains.ru | Network node is accesible
127.0.0.1 | status=0
127.0.0.1 | Network node is accesible
192.168.0.1 | status=0
192.168.0.1 | Network node is accesible
192.168.1.126 | status=1
192.168.1.126 | Network  node is not accesible
127 | Hostname is incorrect
87.250.250.242 | status=0
ya.ru | Network node is accesible
FINISH
'''