import socket
import _thread

port = 5555
host = socket.gethostname()
server = (host, port)
buff = 1024

listened = 3

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


try:
    sock.bind(server)
except socket.error as error:
    print(error)

sock.listen(listened)
print('Server opened! Waiting for a connection...')

replies = []

for cont in range(listened):
    replies.append(' ')


def handler(conn, player):
    global buff

    conn.send(b'Connected to server!')

    while True:
        try:
            data = conn.recv(buff)
            reply = data.decode()

            for players in range(listened):
                replies[player - 1] = reply

            reply = replies[:]
            reply.remove(reply[player - 1])
            reply = ' '.join(reply)

            if not data:
                print('Disconnected!')
                break
            else:
                print(f'Received: {reply}')
                print(f'Sending: {reply}')

            conn.sendall(str(reply).encode())

        except Exception as e:
            print(e)
            break

    print('Lost connection.')
    conn.close()


player_id = 1
while True:
    connection, address = sock.accept()
    print(f'Connected to: {address}')

    _thread.start_new_thread(handler, (connection, player_id))
    player_id += 1
