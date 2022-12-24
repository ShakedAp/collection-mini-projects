import socket
import tkinter
import tkinter as tk
import traceback
from threading import Thread
from tkinter import messagebox
from tkinter import scrolledtext

# Constants
NICKNAME_LENGTH = 8
HEADER_LENGTH = 16


class LoginWindow:

    def __init__(self):
        """Creates the login window, and runs it's main loop."""
        self.nickname = ''
        self.waiting_for_connection, self.connected = False, False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # --- Create login gui ---
        self.window = tk.Tk()
        # Position window in the middle of the screen
        screen_width, screen_height = self.window.winfo_screenwidth(), self.window.winfo_screenheight()
        width, height = 400, 300
        addx, addy = (screen_width - width) / 2, (screen_height - height) / 2
        self.window.title("Login window")
        self.window.geometry(f'{width}x{height}+{int(addx)}+{int(addy)}')
        self.window.resizable(False, False)

        # Create canvas, and add a background
        back_img = tk.PhotoImage(file='login_background.png')
        canvas = tk.Canvas(self.window, width=width, height=height)
        canvas.pack(fill='both', expand=True)
        canvas.create_image(0, 0, image=back_img, anchor='nw')

        # Add fields labels
        x_pos = 140
        canvas.create_text(width / 2, 20, text='Login', font=("Arial", 12, 'bold'), fill='white')
        canvas.create_text(x_pos, 100, text='nickname:', font=("Arial", 12), fill='white')
        canvas.create_text(x_pos, 150, text='IP:', font=("Arial", 12), fill='white')
        canvas.create_text(x_pos, 200, text='port:', font=("Arial", 12), fill='white')

        # Add fields entries, with default values
        self.nick_entry = tk.Entry(self.window)
        canvas.create_window(x_pos + 150, 100, window=self.nick_entry)
        self.ip_entry = tk.Entry(self.window)
        canvas.create_window(x_pos + 150, 150, window=self.ip_entry)
        self.ip_entry.insert(tk.END, socket.gethostbyname(socket.gethostname()))
        self.port_entry = tk.Entry(self.window)
        self.port_entry.insert(tk.END, '5555')
        canvas.create_window(x_pos + 150, 200, window=self.port_entry)

        # Add a login button
        self.login_button = tk.Button(self.window, text="login", font=("Arial", 12), command=self.login)
        canvas.create_window(width / 2, 250, window=self.login_button)

        self.window.mainloop()

    def connect(self, ip: str, port: int, nickname: str):
        """Tries connecting to the server with the given ip and port. If a successful connection was made,
        the nickname is sent and receives the validated nickname. Then, closes the window.
        If the connection failed an appropriate error message appears.

        :param ip: The server's ip
        :type ip: str
        :param port: The server's port
        :type port: int
        :param nickname: The user's nickname
        :type nickname: str
        :return: None
        """
        display_message = ''
        try:
            # Connect to the server and send given nickname, Then close window
            self.sock.connect((ip, port))
            self.sock.send(nickname.ljust(NICKNAME_LENGTH).encode('utf-8'))
            self.nickname = self.sock.recv(NICKNAME_LENGTH).decode('utf-8').strip()
            self.connected = True
            self.window.withdraw()
            self.window.quit()
        except TimeoutError:
            display_message = 'Timeout Error.'
        except WindowsError:
            display_message = "Couldn't connect to server"
        except Exception as e:
            display_message = str(e)

        # Display an error message
        if display_message:
            messagebox.showerror("Error", display_message)
            self.waiting_for_connection = False

    def login(self):
        """ Gets the inputted nickname, ip and port from the fields and tries to connect to the server with them.
        If those values are not valid or an error occurred, an error message window will be popped up.
        This method in mainly called from the login button.

        :return: None
        """
        if not self.waiting_for_connection:
            display_message = ''
            entered_nickname = self.nick_entry.get()
            entered_ip = self.ip_entry.get().strip()
            entered_port = self.port_entry.get()

            # Check if the nickname, IP and port are valid
            if not entered_nickname or not entered_ip or not entered_port:
                display_message = 'Must enter all fields'
            elif len(entered_nickname) > NICKNAME_LENGTH:
                display_message = 'Nickname too long'
            elif not all(0 < ord(c) < 128 for c in entered_nickname):
                display_message = 'Invalid nickname'
            else:
                try:
                    # Check if Ip is legal
                    socket.inet_aton(entered_ip)
                    if entered_ip.count('.') != 3:
                        display_message = 'Ip must be legal.'
                    # Check if port is legal
                    entered_port = int(entered_port)
                except socket.error:
                    display_message = 'Ip must be legal.'
                except ValueError:
                    display_message = 'Port must be a number.'

            # Display an error message if some of the values aren't valid. Try connecting to the server otherwise
            if display_message:
                messagebox.showerror("Error", display_message)
            else:
                login_thread = Thread(target=self.connect, args=(entered_ip, entered_port, entered_nickname))
                login_thread.setDaemon(True)
                login_thread.start()
                self.waiting_for_connection = True


class Client:

    def __init__(self, sock: socket.socket, nickname: str):
        self.sock = sock
        self.nickname = nickname

        self.currently_messaging = ''
        self.running, self.gui_done = True, False
        # unread_messages -> [messages, index]
        self.messages, self.unread_messages = {}, {}
        self.users_count = 0

    def receive(self):
        """A method that receives the server's messages, and handles them accordingly. Runs on a separate thread.
        If an error occurs or the server closed the connection, the window and connection are closed.

        :return: None
        """
        while self.running:
            if not self.gui_done:
                continue

            try:
                data = self.sock.recv(HEADER_LENGTH).decode("utf-8")
                if not data:
                    self.close()
                    break
                command, length = data.strip().split(' ')
                data = self.sock.recv(int(length)).decode("utf-8")

                if command == 'msg':
                    dest = data[:NICKNAME_LENGTH].strip()
                    message = data[NICKNAME_LENGTH:]

                    self.messages[dest].append(message)
                    if dest == self.currently_messaging:  # Output message to the current chat
                        self.text_area.config(state='normal')
                        self.text_area.insert('end', message)
                        self.text_area.config(state='disabled')
                    else:  # Add notification
                        self.unread_messages[dest][0] += 1
                        self.menu_area.delete(self.unread_messages[dest][1])
                        self.menu_area.insert(self.unread_messages[dest][1],
                                              f"{dest}\0({self.unread_messages[dest][0]})")
                if command == 'newuser':
                    self.add_user(data)
                if command == 'removeuser':
                    self.remove_user(data)

            except ConnectionAbortedError:
                self.close()
            except ConnectionResetError:
                self.close()

    def gui_loop(self):
        """Instantiate the window, create all of the gui, and run the gui loop. This method runs on a separate thread.

        :return: None
        """

        #  -- Create chat gui --
        menu_bg, chat_bg = '#638773', '#638387'
        self.window = tk.Tk()
        self.chat_frame = tk.Frame(self.window)
        self.menu_frame = tk.Frame(self.window)
        self.chat_frame.configure(background=chat_bg)
        self.menu_frame.configure(background=menu_bg)

        self.window.title(f"Chat Application - {self.nickname}")
        self.window.resizable(False, False)
        # Position window in the middle of the screen
        screen_width, screen_height = self.window.winfo_screenwidth(), self.window.winfo_screenheight()
        width, height = 665, 565
        addx, addy = (screen_width - width) / 2, (screen_height - height) / 2
        self.window.geometry(f'{width}x{height}+{int(addx)}+{int(addy)}')

        # Configure chat frame
        back_button = tk.Button(self.chat_frame, text="Back", font=("Arial", 10), command=self.goto_menu)
        back_button.place(x=0, y=0)

        self.chat_label = tk.Label(self.chat_frame, text=f"Chat {self.currently_messaging}:", bg=chat_bg,
                                   font=("Arial", 12))
        self.chat_label.pack(padx=20, pady=5)

        self.text_area = tk.scrolledtext.ScrolledText(self.chat_frame)
        self.text_area.pack(padx=20, pady=5)
        self.text_area.config(state='disabled')

        message_label = tk.Label(self.chat_frame, text="Message:", bg=chat_bg, font=("Arial", 12))
        message_label.pack(padx=20, pady=5)

        self.input_area = tk.Text(self.chat_frame, height=3)
        self.input_area.pack(padx=20, pady=5)

        send_button = tk.Button(self.chat_frame, text="Send", font=("Arial", 12), command=self.send_current_msg)
        send_button.pack(padx=0, pady=0)

        # Configure menu frame
        menu_label = tk.Label(self.menu_frame, text="Choose a person to message:", bg=menu_bg, font=("Arial", 12))
        menu_label.pack(padx=20, pady=5)

        self.menu_area = tk.Listbox(self.menu_frame, height=25, width=65, font=("Arial", 12), selectmode=tkinter.SINGLE)
        self.menu_area.pack(padx=20, pady=5)
        self.add_user('global')

        chat_button = tk.Button(self.menu_frame, text="Message!", font=("Arial", 12),
                                command=self.select_person_message)
        chat_button.pack(padx=0, pady=5)

        # Update window settings
        def validate(event):
            # Don't allow the user to input more that 128 characters
            content = self.input_area.get(1.0, "end")
            len_ = 128
            if len(content) > len_ + 1:
                self.input_area.delete(1.0, 'end')
                self.input_area.insert('insert', content[:len_])

        self.window.bind('<KeyPress>', validate)
        self.window.bind('<Return>', self.send_current_msg)
        self.window.bind('<Shift-Key-Return>', lambda x: None)  # Allow the user to add a \n character

        self.menu_frame.pack(fill='both', expand=1)
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        self.gui_done = True
        self.window.mainloop()

    def close(self):
        """Closes the application. Destroys the window and closes the connection.

        :return: None
        """
        self.window.quit()
        self.sock.close()
        self.running = False

    def send_current_msg(self, event=None):
        """Sends the current text in the input area as a message. Send the text to the server, and add it to the
        current chat's gui.

        :param event: tkinter event
        :return: None
        """
        message = self.input_area.get(1.0, "end").strip() + '\n'

        if self.currently_messaging != '' and message != '\n':
            # Send message to all users
            self.send_msg('msg', self.currently_messaging.ljust(NICKNAME_LENGTH) + message)
            # Add text to display
            message = 'You: ' + message
            self.text_area.config(state='normal')
            self.messages[self.currently_messaging].append(message)
            self.text_area.insert('end', message)
            self.input_area.delete('1.0', 'end')
            self.text_area.config(state='disabled')

    def send_msg(self, command, msg):
        """Sending a text message with a command to the server, in the correct format.

        :param command: the command of the message.
        :type command: str
        :param msg: The content of the message.
        :type msg: str
        """
        header = f"{command} {len(msg.encode('utf-8'))}".ljust(HEADER_LENGTH)
        message = (header + msg).encode("utf-8")
        self.sock.send(message)

    def goto_menu(self):
        """Switching the gui to show the menu frame.

        :return: None
        """
        self.menu_frame.pack(fill='both', expand=1)
        self.chat_frame.forget()
        self.currently_messaging = ''

    def select_person_message(self):
        """Switching the gui 1to show the selected person's chat. Removes the notifications and opens the chat gui.

        :return: None
        """
        try:
            self.currently_messaging = self.menu_frame.selection_get().split('\0')[0]
            self.chat_label.configure(text=f"Chat {self.currently_messaging}:")
            # Removing notification
            self.unread_messages[self.currently_messaging][0] = 0
            self.menu_area.delete(self.unread_messages[self.currently_messaging][1])
            self.menu_area.insert(self.unread_messages[self.currently_messaging][1],
                                  self.currently_messaging + '\0')
            # Going to chat frame
            self.chat_frame.pack(fill='both', expand=1)
            self.menu_frame.forget()

            # Loading current chat text
            self.text_area.config(state='normal')
            self.text_area.delete('1.0', 'end')
            for message in self.messages[self.currently_messaging]:
                self.text_area.insert('end', message)
            self.text_area.config(state='disabled')
        except tk.TclError:
            # Trying to go to a selected chat without selecting any
            pass

    def add_user(self, nickname: str):
        """Add a new user.

        :param nickname: The user's nickname to be added.
        ":type nickname: str
        :return: None
        """
        self.menu_area.insert('end', nickname + "\0")
        self.messages[nickname] = []
        self.unread_messages[nickname] = [0, self.users_count]
        self.users_count += 1

    def remove_user(self, nickname: str):
        """Remove a user. If the current user chat is open, go to the menu.

        :param nickname: The user's nickname to be removed.
        ":type nickname: str
        :return: None
        """
        self.menu_area.delete(self.unread_messages[nickname][1])
        del self.unread_messages[nickname]
        del self.messages[nickname]
        self.users_count -= 1
        if self.currently_messaging == nickname:
            self.goto_menu()



def main():
    """ The main method.
    Creates a client object and a Login Window.
    After the client has been connected, starts the gui loop and the receive loop.
    """

    login_window = LoginWindow()
    client = Client(login_window.sock, login_window.nickname)

    if login_window.connected:
        Thread(target=client.gui_loop, args=()).start()
        client.receive()


if __name__ == '__main__':
    main()
