import os
import socket
import time
import matplotlib.pyplot as plt
import math


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


def smooth(data, smooth_factor):
    smoothed_data = []
    for n in range(len(data) - smooth_factor):
        sum = 0
        highest = 0
        for k in range(smooth_factor):
            highest = max(highest, data[n + k])
            sum += data[n + k]
        smoothed_data.append(highest)
        # smoothed_data.append(sum / smooth_factor)

    return smoothed_data


def upload_plot():
    speeds = []
    times = []
    with open("upload_speed.txt") as file:
        for line in file:
            split_line = line.split()
            speeds.append(float(split_line[0]) / (10 ** 6))
            times.append(float(split_line[1]))

    smooth_speeds = smooth(speeds, 10)
    smooth_times = smooth(times, 10)

    # print(times)
    # print(speeds)
    # plt.scatter(times, speeds, s=1)
    # plt.show()
    fig, ax = plt.subplots()
    ax.plot(smooth_times, smooth_speeds, lw=1)
    scale = 1
    while 10 * scale < math.ceil(max(smooth_times)):
        scale *= 10
    plt.xticks(range(0, math.ceil(max(smooth_times)) + 1, scale))
    plt.title("Upload Speed vs. Time")
    plt.xlabel("Time (sec)")
    plt.ylabel("Speed (MB/sec)")
    plt.show()


def download_plot():
    speeds = []
    times = []
    with open("download_speed.txt") as file:
        for line in file:
            split_line = line.split()
            speeds.append(float(split_line[0]) / (10 ** 6))
            times.append(float(split_line[1]))

    smooth_speeds = smooth(speeds, 10)
    smooth_times = smooth(times, 10)

    # print(times)
    # print(speeds)
    # plt.scatter(times, speeds, s=1)
    # plt.show()
    fig, ax = plt.subplots()
    ax.plot(smooth_times, smooth_speeds, lw=0.5)
    scale = 1
    while 10 * scale < math.ceil(max(smooth_times)):
        scale *= 10
    plt.xticks(range(0, math.ceil(max(smooth_times)) + 1, scale))
    plt.title("Download Speed vs. Time")
    plt.xlabel("Time (sec)")
    plt.ylabel("Speed (MB/sec)")
    plt.show()


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

        if cmd == "MKDIR":  # make directory with the name given
            new_dir_name = line_in_split[1]
            data_to_send += "MKDIR" + SPLIT + new_dir_name
            client.send(data_to_send.encode(FORMAT))

        if cmd == "CD":  # change directory
            new_dir_name = line_in_split[1]
            data_to_send += "CD" + SPLIT + new_dir_name
            client.send(data_to_send.encode(FORMAT))

        if cmd == "DELETE":  # delete file from folder, takes one arg: filename
            fname = line_in_split[1]
            data_to_send += "DELETE"+SPLIT+fname
            client.send(data_to_send.encode(FORMAT))
            # add in error handling

        if cmd == "DELDIR": # delete folder, takes one arg: directory name
            dir_name = line_in_split[1]
            data_to_send += "DELDIR" + SPLIT + dir_name
            client.send(data_to_send.encode(FORMAT))

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
            file = open("upload_speed.txt", "w") #
            file.close() #
            base_time = time.time_ns() #
            num_bytes = 0 #
            file = open("upload_speed.txt", "a") #
            print_time = time.time() #
            print_bytes = 0 #
            total_bytes = 0
            while f.tell() < length:
                buff = f.read(BUFFLEN)
                # print(f"Sending {buff}")
                start_time = time.time_ns() #
                client.send(buff)  # send buffer of data
                # print("Buffer sent")
                # print("Waiting for ready ack")
                data_back = receive(client)  # wait for server to be ready for next
                end_time = time.time_ns() #
                if data_back[0] != "READY":
                    print("ERROR: DID NOT RECEIVE READY ACK")
                    return
                else:
                    num_bytes += len(buff) #
                    print_bytes += len(buff) #
                    total_bytes += len(buff) #
                    if end_time > start_time: #
                        time_passed = end_time - start_time #
                        speed = num_bytes / (time_passed / (10 ** 9)) #
                        current_time = end_time - base_time #
                        file.write(str(speed) + " " + str(current_time / (10 ** 9)) + "\n") #
                        num_bytes = 0 #
                    if time.time() >= print_time + 1: #
                        print_speed = print_bytes / (time.time() - print_time) #
                        print_time = time.time() #
                        print_bytes = 0 #
                        percent_done = round(100 * total_bytes / length)
                        print("\r" + str(round(print_speed / (10 ** 6), 3)) + " MB/sec - " + str(percent_done) + "%", end="") #
                    # print("Ready received")
                    pass
            file.close() #
            print()
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
            file = open("download_speed.txt", "w") #
            file.close() #
            base_time = time.time_ns() #
            start_time = 1000000000 #
            num_bytes = 0 #
            file = open("download_speed.txt", "a") #
            print_time = time.time() #
            print_bytes = 0
            while len(buff) < data_length:
                data_in = client.recv(BUFFLEN)
                end_time = time.time_ns() #
                num_bytes += len(data_in) #
                print_bytes += len(data_in) #
                if end_time > start_time: #
                    time_passed = end_time - start_time #
                    speed = num_bytes / (time_passed / (10 ** 9)) #
                    current_time = end_time - base_time #
                    file.write(str(speed) + " " + str(current_time / (10 ** 9)) + "\n") #
                    num_bytes = 0 #
                if time.time() >= print_time + 1:  #
                    print_speed = print_bytes / (time.time() - print_time)  #
                    print_time = time.time()  #
                    print_bytes = 0  #
                    percent_done = round(100 * len(buff) / data_length)
                    print("\r" + str(round(print_speed / (10 ** 6), 3)) + " MB/sec - " + str(percent_done) + "%", end="")  #
                buff += data_in
                # print(buff)
                send_data = START+SPLIT+"READY"  # send ready ack
                if end_time > start_time: #
                    start_time = time.time_ns() #
                client.send(send_data.encode(FORMAT))
            file.close() #
            f.write(buff)  # write bytes from buffer to file
            data_in = receive(client)  # get acknowledgement that client has finished
            if data_in[0] == "DONE":
                print()
                print("Done receiving")
            else:
                print("ERROR: DID NOT RECEIVE DONE")
                time.sleep(10)
            f.close()


if __name__ == "__main__":
    main()
    # upload_plot()
    # download_plot()
