from socket import *
from os import listdir
from os.path import getsize 

serverPort = 11550

serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('',serverPort))

serverSocket.listen(1)

# get msg from client
def get_msg(msg):
    msg = msg.split(' ')
    seq, c, a = msg[0], msg[1], msg[2:]
    print(seq, c, a)
    return seq, c, a

# send answer back to client
def ansClient(seq, r, args=None, close=False):
    returnMsg = seq + ' ' + r
    if args:
        returnMsg += ' ' + args  
    ConnectionSocket.send(returnMsg.encode('ascii'))
    if close:
        ConnectionSocket.close()

print('server pta ok')

while 1:
    try:
        # doing connection and check if it's a valid user
        ConnectionSocket, addr = serverSocket.accept()
        msg = ConnectionSocket.recv(1024).decode()
        seq_num, command, args = get_msg(msg)

        if seq_num == '0':
            if command != 'CUMP':
                ansClient(seq_num, 'NOK', close=True)
                continue
            
            try:
            # users
                file = open('users.txt', 'r')
                users = [x[:-1] for x in file.readlines()]
                file.close()
                if args[0] not in users:
                    ansClient(seq_num, 'NOK', close=True)
                    continue
            except:
                ansClient(seq_num, 'NOK', close=True)
                continue
 
            ansClient(seq_num, 'OK')

        while 1:
            
            msg = ConnectionSocket.recv(1024).decode()
            if not msg:
                continue
            seq_num, command, args = get_msg(msg)
            
            try:
                if command == 'LIST':
                    files = [x for x in listdir('files')]
                    filesname = ','.join(files)

                    ans_args = str(len(files)) + ' ' + filesname   
                    ansClient(seq_num, 'ARQS', ans_args)            

                elif command == 'PEGA':
                    files = [x for x in listdir('files')]

                    client_filename = args[0]
                    if client_filename not in files:
                        ansClient(seq_num, 'NOK')
                        continue
                    
                    filesize = str(getsize(f'files/{client_filename}'))

                    cf = open(f'files/{client_filename}', 'rb')
                    byt = cf.read(2048)
                    ans_args = f'{filesize} {byt}'
                    ansClient(seq_num, 'ARQ', ans_args)
                    byt = cf.read(2048)
                    while byt != b'':
                        ans_args = f'{filesize} {byt}'
                        ansClient(seq_num, 'ARQ', ans_args)
                        byt = cf.read(2048)  
                    cf.close()

                elif command == 'TERM':
                    ansClient(seq_num, 'OK', close=True)
                    break

            except Exception as e:
                ansClient(seq_num, 'NOK')

    except(KeyboardInterrupt, SystemExit):
        break


serverSocket.shutdown(SHUT_RDWR)
serverSocket.close()