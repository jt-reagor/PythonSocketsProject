import os
import socket


START = "<START>"
SPLIT = "<SPLIT>"

BUFFLEN = 512

SIZE = 1024
FORMAT = "utf-8"


def receive(client):
    data_back = client.recv(SIZE).decode(FORMAT)
    data_back_split = data_back.split(SPLIT)
    if data_back_split[0] != START:
        print(data_back_split)
        print("ERROR")
        return -1
    data_back_split = data_back_split[1:]
    return data_back_split


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        line_in = input("> ")
        line_in_split = line_in.split(" ")
        cmd = line_in_split[0]

        data_to_send = START + SPLIT
        if cmd == "CONNECT":
            if len(line_in_split) != 3:
                print("ERROR")
                continue
            serv_ip = line_in_split[1]
            serv_port = int(line_in_split[2])
            client.connect((serv_ip, serv_port))
            data_back = receive(client)
            if data_back == -1:
                print("ERROR")
                continue
            print(data_back[0])

        if cmd == "LOGOUT":
            data_to_send += "LOGOUT"
            client.send(data_to_send.encode(FORMAT))
            data_back = receive(client)
            if data_back:
                print("SUCCESSFULLY DISCONNECTED")
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if cmd == "ECHO":
            data_to_send += "ECHO"
            client.send(data_to_send.encode(FORMAT))
            data_back = receive(client)
            if data_back == -1:
                print("ERROR")
                continue
            print(data_back[0])

        if cmd == "DIR":
            data_to_send += "DIR"
            client.send(data_to_send.encode(FORMAT))
            data_back = receive(client)
            print(str(data_back))

        if cmd == "DELETE":
            fname = line_in_split[1]
            data_to_send += "DELETE"+SPLIT+fname
            client.send(data_to_send.encode(FORMAT))

        if cmd == "UPLOAD":
            fname = line_in_split[1]
            f = open(fname, "rb")
            f.seek(0, 2)  # set reader at end
            length = f.tell()  # get length
            f.seek(0, 0)  # reset pointer
            data_to_send += "UPLOAD"+SPLIT+str(length)+SPLIT+str(fname)
            client.send(data_to_send.encode(FORMAT))  # send "ready to send x bytes"
            data_back = receive(client)  # wait for ack from server
            print("INITIAL READY RECIEVED")
            if data_back == -1:
                print("ERROR")
                continue
            while f.tell() < length:
                buff = f.read(BUFFLEN)
                print(f"Sending {buff}")
                client.send(buff)
                print("Buffer sent")
                print("Waiting for ready ack")
                data_back = receive(client)
                if data_back[0] != "READY":
                    print("ERROR")
                    return
                else:
                    print("Ready received")
                # print(f.tell())
            end_message = START + SPLIT + "DONE"
            client.send(end_message.encode(FORMAT))

            f.close()


if __name__ == "__main__":
    main()
