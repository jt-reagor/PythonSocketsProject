import os
import socket
import threading

IP = "localhost"
PORT = 4450
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
SERVER_PATH = "server"
BUFFLEN = 512
START = "<START>"
SPLIT = "<SPLIT>"
working_dir = list()

def receive(client, size=SIZE):
    data_back = client.recv(size).decode(FORMAT)
    data_back_split = data_back.split(SPLIT)
    if data_back_split[0] != START:
        print(data_back_split)
        print("ERROR")
        return -1
    data_back_split = data_back_split[1:]
    return data_back_split


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

        if cmd == "DIR":
            for file in os.listdir(''.join(working_dir)):
                send_data += file + SPLIT  # add more information about files here
            conn.send(send_data.encode(FORMAT))
            print(f"DIR returned")

        if cmd == "DELETE":
            file_name = ''.join(working_dir) + data[1]
            os.remove(file_name)
            print(f"Deleted {file_name}")

        if cmd == "UPLOAD":  # receives UPLOAD<SPLIT><length>
            data_length = int(data[1])
            file_name = ''.join(working_dir) + "new" +data[2]  # change this later
            f = open(file_name, "wb")
            print(f"Ready for file of length {data_length}")
            send_data += "READY"
            conn.send(send_data.encode(FORMAT))
            buff = bytes()
            while len(buff) < data_length:
                data_in = conn.recv(BUFFLEN)
                buff += data_in
                # print(buff)
                send_data = START+SPLIT+"READY"  # send ready ack
                conn.send(send_data.encode(FORMAT))
            f.write(buff)  # write bytes from buffer to file
            data_in = receive(conn)  # get acknowledgement that client has finished
            if data_in[0] == "DONE":
                print("Done receiving")
            f.close()

    print(f"{addr} disconnected.")
    conn.close()


def main():
    if not os.path.isdir("./sharedfolder"):
        os.mkdir("./sharedfolder")
    working_dir.append("./sharedfolder/")
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
