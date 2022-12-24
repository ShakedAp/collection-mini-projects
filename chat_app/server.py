import socket
import time
import traceback
from threading import Thread

# Start the server on the current computer
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
hostname = socket.gethostname()
HOST, PORT = socket.gethostbyname(hostname), 5555
server_socket.bind((HOST, PORT))
server_socket.listen()
print("[SERVER] listening on host", HOST, "and port", PORT)

# Variables and Constants
NICKNAME_LENGTH = 8
HEADER_LENGTH = 16
connections = 0
clients = {}
clients_mute_time = {}


def send_msg(sock: socket.socket, command: str, msg: str):
    """ Sending a text message with a command to the given client socket, in the correct format.

    :param sock: The socket where the message is going to be sent to.
    :type sock: socket.socket
    :param command: the command of the message.
    :type command: str
    :param msg: The content of the message.
    :type msg: str
    """
    header = f"{command} {len(msg.encode('utf-8'))}".ljust(HEADER_LENGTH)
    message = (header + msg).encode("utf-8")
    sock.send(message)


def validate_nickname(nickname: str, clients: dict, id: int):
    """ Make sure the given nickname is valid. A nickname is valid if it follows the following rules:
    a. isn't an empty string, and has a length smaller then NICKNAME_LENGTH
    b. isn't already taken by another client
    c. isn't equal to one of the system pre-used words ("global")
    d. contains only character from the ascii table, and not contains to the NUL character
    If the nickname is not valid, a unique nickname is returned, in the format of "user{id}" (ex: user0, user1...).
    If the nickname is admin, "Admin" is returned.

    :param nickname: The nickname to be checked
    :type nickname: str
    :param clients: A dictionary containing all of the current clients
    :type clients: dict
    :param id: The current id of the client
    :type id: int
    :return: The new valid nickname
    :rtype: str
    """
    if nickname.lower() == 'admin':
        return 'Admin'
    if (nickname in clients) or (len(nickname) > NICKNAME_LENGTH or len(nickname) < 1) or (nickname == 'global')\
            or (not all(0 < ord(c) < 128 for c in nickname)):
        return f'user{id}'
    return nickname


def kick_user(user: str, clients: dict):
    """Kick the given user. Notify all of the other users and close it's connection.

    :param user: The user's nickname to be kicked
    :type user: str
    :param clients: A dictionary containing all of the current clients
    :type clients: dict
    :return: None
    """
    for sock in clients.values():
        send_msg(sock, 'msg',
                 f"{'global'.ljust(NICKNAME_LENGTH)}[SERVER] {user} was kicked by the "
                 f"Admin.\n")
    clients[user].close()
    print(f"[LOG] Admin kicked {user}.")


def mute_user(user: str, mute_time: int, clients: dict, clients_mute_time: dict):
    """Mute the given user. Notify all of the other users and add to it's mute timer.

    :param user: The user's nickname to be kicked
    :type user: str
    :param mute_time: Time in minutes to mute the user
    :type mute_time: int
    :param clients: A dictionary containing all of the current clients
    :type clients: dict
    :param clients_mute_time: A dictionary containing all of the current clients' mute time
    :type clients_mute_time: dict
    :return: None
    """
    for sock in clients.values():
        send_msg(sock, 'msg',
                 f"{'global'.ljust(NICKNAME_LENGTH)}[SERVER] {user} was muted for {mute_time} minutes\n")
    clients_mute_time[user] = time.time() + mute_time * 60
    print(f"[LOG] Admin muted {user} for {mute_time} minutes.")


def handle_client(client_socket: socket.socket, _id: int):
    """Handle each client connection, running a loop to receive messages.
    This function runs in a separate thread for each client.

    :param client_socket: The client's socket
    :type client_socket: socket
    :param _id: the client's current id
    :type _id: int
    :return: None
    """
    global connections, clients, clients_mute_time
    running = True

    #  Receive the client's nickname, validate it and send it the validated nickname
    data = client_socket.recv(NICKNAME_LENGTH)
    nickname = data.decode("utf-8").strip()
    nickname = validate_nickname(nickname, clients, _id)
    client_socket.send(nickname.ljust(NICKNAME_LENGTH).encode("utf-8"))

    # Receive the password from the admin.
    if nickname == 'Admin':
        command, length = client_socket.recv(HEADER_LENGTH).decode("utf-8").strip().split(' ')
        data = client_socket.recv(int(length)).decode("utf-8")
        dest = data[:NICKNAME_LENGTH]
        message = data[NICKNAME_LENGTH:].strip()

        if message == 'password':  # Correct password
            send_msg(client_socket, 'msg', f"{dest}[SERVER] Logged in successfully!\n")
        else:  # Incorrect password.
            send_msg(client_socket, 'msg', f"{dest}[SERVER] Incorrect password.\n[SERVER] Closing in a few seconds.\n")

            print(f'[LOG] Admin tried to join, but inputted an incorrect password:  {message}')
            print("[DISCONNECT]", nickname, "disconnected")
            time.sleep(3)
            connections -= 1
            client_socket.close()
            return

    # Notify all users a new user joined. Update all the lists to include this user.
    for nick, sock in clients.items():
        send_msg(sock, 'msg', f"{'global'.ljust(NICKNAME_LENGTH)}[SERVER] {nickname} joined the server.\n")
        send_msg(sock, 'newuser', nickname)
        send_msg(client_socket, 'newuser', nick)
    clients[nickname] = client_socket
    clients_mute_time[nickname] = time.time()
    print("[LOG]", nickname, "connected to the server.")

    # User loop. Receive messages and commands.
    while running:
        try:
            command, length = client_socket.recv(HEADER_LENGTH).decode("utf-8").strip().split(' ')
            data = client_socket.recv(int(length)).decode("utf-8")

            if command == 'msg':
                dest = data[:NICKNAME_LENGTH]
                dest_stripped = dest.strip()
                message = data[NICKNAME_LENGTH:]

                if clients_mute_time[nickname] - time.time() > 0:
                    time_left = round((clients_mute_time[nickname] - time.time()) / 60, 2)
                    print(f"[LOG] {nickname} tried to send message but was muted. Still has {time_left} minutes left.")
                    send_msg(client_socket, 'msg',
                             f"{dest}[SERVER] You are still muted. Time left: {time_left} minutes.\n")

                elif dest_stripped == 'global':
                    for nick, sock in clients.items():
                        if nick != nickname:
                            send_msg(sock, 'msg', f"{dest}{nickname}: {message}")
                    print(f"[LOG] global>>   {nickname}: {message}", end='')
                else:
                    if nickname == 'Admin':
                        if message.strip() == '!kick':
                            kick_user(dest_stripped, clients)
                            continue
                        if message.startswith('!mute'):
                            try:
                                mute_time = int(message[6:-1])
                                mute_user(dest_stripped, mute_time, clients, clients_mute_time)
                            except ValueError:
                                send_msg(client_socket, 'msg', f"{dest}[SERVER] couldn't mute.\n")
                            continue

                    send_msg(clients[dest_stripped], 'msg', f"{nickname.ljust(NICKNAME_LENGTH)}{nickname}: {message}")
                    print(f"[LOG] {nickname}>>{dest_stripped}   {nickname}: {message}", end='')

        except ConnectionAbortedError:
            running = False
        except ConnectionResetError:
            running = False
        except Exception:
            traceback.print_exc()
            running = False

    # Notify all users a user has left. Update all the lists to remove this user. Close the connection.
    print("[DISCONNECT]", nickname, "disconnected.")
    clients.pop(nickname)
    clients_mute_time.pop(nickname)
    for sock in clients.values():
        send_msg(sock, 'msg', f"{'global'.ljust(NICKNAME_LENGTH)}[SERVER] {nickname} disconnected.\n")
        send_msg(sock, 'removeuser', nickname)
    connections -= 1
    client_socket.close()


def main():
    """Server main loop. Accepting each client connection and starting it's thread."""
    global connections

    while True:
        try:
            client, addr = server_socket.accept()
            print("[CONNECTION] Connected to:", addr)

            Thread(target=handle_client, args=(client, connections)).start()
            connections += 1
        except Exception as e:
            print(str(e))
            break
    print("[SERVER] Server offline")


if __name__ == '__main__':
    main()
