import os
import socket
import threading
import time
import datetime

IP = "localhost"
# IP = "10.47.55.214"
PORT = 4450
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
SERVER_PATH = "server"
BUFFLEN = 1024
START = "<START>"
SPLIT = "<SPLIT>"
working_dir = list()
file_dict = dict()


class File:
    def __init__(self, fname):
        self.name = fname
        self.upload_date = datetime.date.today().strftime("%x")
        self.upload_time = datetime.datetime.now().strftime("%H: %M: %S")
        self.num_downloads = 0


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
            break
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
            send_data = START
            for file in os.listdir(''.join(working_dir)):  # initialize file dictionary for metadata
                file_dict[''.join(working_dir) + file] = File(file)
            for file in os.listdir(''.join(working_dir)):
                file_obj = file_dict[''.join(working_dir) + file]

                send_data += SPLIT + file_obj.name + "<SUBSPLIT>"\
                             + file_obj.upload_date + "<SUBSPLIT>"\
                             + str(file_obj.num_downloads)
            conn.send(send_data.encode(FORMAT))
            print(f"DIR returned")

        if cmd == "MKDIR":
            new_dir_name = data[1]
            os.mkdir("./sharedfolder/" + new_dir_name)
            official_new_dir_name = ''.join(working_dir) + data[1]
            new_file = File(new_dir_name)
            file_dict[official_new_dir_name] = new_file
            print(f"DIR {new_dir_name} created")

        if cmd == "CD":
            new_dir_name = data[1]
            if new_dir_name != "..":
                working_dir.append(new_dir_name + "/")
            else:
                del working_dir[-1]

        if cmd == "DELETE":
            file_name = ''.join(working_dir) + data[1]
            os.remove(file_name)
            print(f"Deleted {file_name}")

        if cmd == "DELDIR":
            dir_name = ''.join(working_dir) + data[1]
            os.rmdir(dir_name)
            print(f"Deleted {dir_name}")

        if cmd == "UPLOAD":  # receives UPLOAD<SPLIT><length>
            data_length = int(data[1])
            file_name = ''.join(working_dir) + data[2]  # change this later
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
            else:
                print("ERROR: DID NOT RECEIVE DONE")
                time.sleep(10)
            f.close()
            new_file = File(data[2])
            file_dict[file_name] = new_file

        if cmd == "DOWNLOAD":  # Receives DOWNLOAD<SPLIT><filename>
            fname = ''.join(working_dir) + data[1]
            f = open(fname, "rb")
            f.seek(0, 2)  # set reader at end
            length = f.tell()  # get length
            f.seek(0, 0)  # reset pointer
            send_data += "DOWNLOAD"+SPLIT+str(length)+SPLIT+str(fname)
            conn.send(send_data.encode(FORMAT))  # send "ready to send x bytes"
            data_back = receive(conn)  # wait for ack from server
            print("INITIAL READY RECIEVED")
            if data_back == -1:
                print("ERROR: PROBLEM IN READY ACK")
                continue
            while f.tell() < length:
                buff = f.read(BUFFLEN)
                # print(f"Sending {buff}")
                conn.send(buff)
                # print("Buffer sent")
                # print("Waiting for ready ack")
                data_back = receive(conn)
                if data_back[0] != "READY":
                    print("ERROR: DID NOT RECEIVE READY ACK")
                    return
                else:
                    # print("Ready received")
                    pass
                # print(f.tell())
            end_message = START + SPLIT + "DONE"
            conn.send(end_message.encode(FORMAT))

            f.close()

            file_dict[fname].num_downloads += 1

    print(f"{addr} disconnected.")
    conn.close()


def main():
    if not os.path.isdir("./sharedfolder"):  # if folder does not exist, create one
        os.mkdir("./sharedfolder")
    working_dir.append("./sharedfolder/")  # start working directory
    for file in os.listdir(''.join(working_dir)):  # initialize file dictionary for metadata
        file_dict[''.join(working_dir) + file] = File(file)
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
