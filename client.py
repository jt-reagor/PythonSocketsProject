import os
import socket


START = "<START>"
SPLIT = "<SPLIT>"

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


if __name__ == "__main__":
    main()
