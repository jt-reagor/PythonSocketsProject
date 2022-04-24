import os
import socket
import time


START = "<START>"
SPLIT = "<SPLIT>"

BUFFLEN = 1024

SIZE = 1024
FORMAT = "utf-8"


# recv and parse data from connection
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
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create socket
    while True:
        line_in = input("> ")
        line_in_split = line_in.split(" ")
        cmd = line_in_split[0]

        data_to_send = START + SPLIT

        if cmd == "CONNECT":  # takes two arguments: ip and port
            if len(line_in_split) != 3:
                print("ERROR")
                continue
            serv_ip = line_in_split[1]
            serv_port = int(line_in_split[2])
            client.connect((serv_ip, serv_port))  # connect
            data_back = receive(client)  # get welcome message
            if data_back == -1:
                print("ERROR")
                continue
            print(data_back[0])
            
            username, password = map(str,input().split())
            data_to_send += "VERIFY" + SPLIT + username + SPLIT + password
            client.send(data_to_send.encode(FORMAT))
            
            data_back = receive(client)
            if data_back[0] == "LOGOUT":
                cmd = "LOGOUT"
                print("Access Denied")
            else:
                print(data_back[0])

        if cmd == "LOGOUT":  # disconnect from server
            data_to_send += "LOGOUT"
            client.send(data_to_send.encode(FORMAT))  # send command
            data_back = receive(client)  # get goodbye message
            if data_back:
                print("SUCCESSFULLY DISCONNECTED")
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # recreate socket

        if cmd == "ECHO":  # simple echo protocol
            data_to_send += "ECHO"
            client.send(data_to_send.encode(FORMAT))
            data_back = receive(client)
            if data_back == -1:
                print("ERROR")
                continue
            print(data_back[0])

        if cmd == "DIR":  # return contents of folder
            data_to_send += "DIR"
            client.send(data_to_send.encode(FORMAT))
            data_back = receive(client)
            for file in data_back:
                file_split = file.split("<SUBSPLIT>")
                to_print = ""
                for item in file_split:
                    to_print += item + "\t"
                print(to_print)

        if cmd == "DELETE":  # delete file from folder, takes one arg: filename
            fname = line_in_split[1]
            data_to_send += "DELETE"+SPLIT+fname
            client.send(data_to_send.encode(FORMAT))
            # add in error handling

        if cmd == "UPLOAD":  # upload specified file to folder
            fname = line_in_split[1]
            f = open(fname, "rb")
            f.seek(0, 2)  # set reader at end
            length = f.tell()  # get length
            f.seek(0, 0)  # reset pointer
            data_to_send += "UPLOAD"+SPLIT+str(length)+SPLIT+str(fname)
            client.send(data_to_send.encode(FORMAT))  # send "ready to send x bytes"
            data_back = receive(client)  # wait for ack from server
            # print("INITIAL READY RECIEVED")
            if data_back == -1:
                print("ERROR: PROBLEM IN READY ACK")
                continue
            while f.tell() < length:
                buff = f.read(BUFFLEN)
                # print(f"Sending {buff}")
                client.send(buff)  # send buffer of data
                # print("Buffer sent")
                # print("Waiting for ready ack")
                data_back = receive(client)  # wait for server to be ready for next
                if data_back[0] != "READY":
                    print("ERROR: DID NOT RECEIVE READY ACK")
                    return
                else:
                    # print("Ready received")
                    pass
            end_message = START + SPLIT + "DONE"
            client.send(end_message.encode(FORMAT))  # tell server finished sending

            f.close()

        if cmd == "DOWNLOAD":  # downloads specified file from folder
            working_dir = "./"
            file_name = line_in_split[1]
            send_data = START + SPLIT + "DOWNLOAD" + SPLIT + file_name
            client.send(send_data.encode(FORMAT))

            data_in = receive(client)
            # print(data_in)
            data_length = int(data_in[1])

            f = open(file_name, "wb")
            print(f"Ready for file of length {data_length}")
            send_data += "READY"
            client.send(send_data.encode(FORMAT))
            buff = bytes()
            while len(buff) < data_length:
                data_in = client.recv(BUFFLEN)
                buff += data_in
                # print(buff)
                send_data = START+SPLIT+"READY"  # send ready ack
                client.send(send_data.encode(FORMAT))
            f.write(buff)  # write bytes from buffer to file
            data_in = receive(client)  # get acknowledgement that client has finished
            if data_in[0] == "DONE":
                print("Done receiving")
            else:
                print("ERROR: DID NOT RECEIVE DONE")
                time.sleep(10)
            f.close()


if __name__ == "__main__":
    main()
