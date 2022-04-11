import os
import socket
import threading

IP = "localhost"
PORT = 4450
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
SERVER_PATH = "server"


START = "<START>"
SPLIT = "<SPLIT>"


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    welcome = START + SPLIT + "Welcome to the server."
    conn.send(welcome.encode(FORMAT))

    while True:
        data = conn.recv(SIZE).decode(FORMAT)  # wait for data from client
        data = data.split(SPLIT)
        if data[0] != START:
            print("ERROR IN RECV")
            continue
        data = data[1:]
        cmd = data[0]

        send_data = START + SPLIT  # prep response message

        if cmd == "LOGOUT":
            send_data += "DISCO"
            conn.send(send_data.encode(FORMAT))
            break
        if cmd == "ECHO":
            send_data += "ECHO BACK!!!"
            conn.send(send_data.encode(FORMAT))
            print(f"echo received from {addr}")
        if cmd == "UPLOAD":  # receives UPLOAD@<length>
            data_length = int(data[1])
            print(data_length)

    print(f"{addr} disconnected.")
    conn.close()


def main():
    print("Starting the server.")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create socket
    server.bind(ADDR)  # bind socket to address
    server.listen()  # listen for connection
    print(f"Server listening on {IP}: {PORT}")
    while True:
        conn, addr = server.accept()  # accept connections
        thread = threading.Thread(target=handle_client, args=(conn, addr))  # handle client connections
        thread.start()


if __name__ == "__main__":
    main()
