from socket import *
from os import listdir
from os.path import getsize 

serverPort = 11550

serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('',serverPort))

serverSocket.listen(1)

# get msg from client
def get_msg(cSocket):
    msg = cSocket.recv(1024).decode()
    msg = msg.split(' ')
    seq, c, a = msg[0], msg[1], None
    if len(msg) == 3:
        a = msg[2]
    return seq, c, a

# send answer back to client
def ansClient(seq, r, args=None, close=False):
    returnMsg = seq + ' ' + r
    if args:
        returnMsg += ' ' + args  
    ConnectionSocket.send(returnMsg.encode('ascii'))
    if close:
        ConnectionSocket.close()

# send file to client
def sendFile(seq_num, client_file):
    path = f'files/{client_file}'
    filesize = getsize(path)
    with open(path, 'rb') as cf:
        byt = cf.read()
        ans_args = f'{str(filesize)} {byt}'
        ansClient(seq_num, 'ARQ', ans_args)
        byt = cf.read(2048)
        while byt != b'':
            ans_args = f'{str(filesize)} {byt}'
            ansClient(seq_num, 'ARQ', ans_args)
            byt = cf.read(2048)
        
print('server pta ok')

while 1:
    try:
        # starting connection and check if it's a valid user
        ConnectionSocket, addr = serverSocket.accept()
        seq_num, command, args = get_msg(ConnectionSocket)
        userin = False
    
        if command != 'CUMP':
            ansClient(seq_num, 'NOK', close=True)
            continue
        
        try:
            file = open('users.txt', 'r')
            users = file.read().splitlines()
            file.close()
            if args not in users:
                ansClient(seq_num, 'NOK', close=True)
                continue
        except:
            ansClient(seq_num, 'NOK', close=True)
            continue

        ansClient(seq_num, 'OK')
        userin = True

        while 1:
            
            # handling client commands over files
            seq_num, command, args = get_msg(ConnectionSocket)
            try:
                if command == 'LIST' and userin:
                    files = [x for x in listdir('files')]
                    filesname = ','.join(files)

                    ans_args = str(len(files)) + ' ' + filesname   
                    ansClient(seq_num, 'ARQS', ans_args)            

                elif command == 'PEGA' and userin:
                    files = [x for x in listdir('files')]
                    
                    if args not in files:
                        ansClient(seq_num, 'NOK')
                        continue
                    
                    sendFile(seq_num, args)

                elif command == 'TERM' and userin:
                    ansClient(seq_num, 'OK', close=True)
                    break

                else:
                    ansClient(seq_num, 'NOK')
                    

            except Exception as e:
                ansClient(seq_num, 'NOK')

    except(KeyboardInterrupt, SystemExit):
        break


serverSocket.shutdown(SHUT_RDWR)
serverSocket.close()