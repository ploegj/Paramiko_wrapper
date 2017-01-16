import paramiko
# import threading
import re
import time
import sys
from rcstruct import rcstruct
import socket
import io
from get_userid_and_password import login_window

"""
Based on:
https://daanlenaerts.com/blog/2016/07/01/python-and-ssh-paramiko-shell/
"""


class MY_SSH(paramiko.SSHClient):
    shell = None
    client = None
    transport = None

    def __init__(self, address, username, password):
        print("Connecting to server on ip", str(address) + ".")
        self.client = paramiko.client.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
        self.client.connect(address, username=username, password=password, look_for_keys=False)
        self._debug = 0
        self._defprompt = '\n[^$# \n]*[$#>] *\Z'
        self._prompt = re.compile(self._defprompt)
        # self.transport = paramiko.Transport((address, 22))
        # self.transport.connect(username=username, password=password)

        # thread = threading.Thread(target=self.process)
        # thread.daemon = True
        # thread.start()

    def debug(self, level):
        self._debug = int(level)
        if self._debug > 12:
            logging.basicConfig(level=logging.DEBUG)


    def closeConnection(self):
        if (self.client != None):
            self.client.close()
            # self.transport.close()

    def openShell(self):
        self.shell = self.client.invoke_shell()
        self._channel = self.shell

    def sendShell(self, command,prompt_type='linux'):
        # Regular expressions which when found in the output have to be responded to
        #
        # f5 less prompt = r'---(less 0%)---'
        # the less prompt is shown when paging is not disabled
        re_f5_more_prompt = r'---\(less [0-9]*\%\)---'
        # when listing data which is more than 1 page it ends with 'END'
        # 'q' has to be send to close the 'END' prompt
        re_f5_end_prompt = r'\(END\)$'
        # Display all 1368 items? (y/n)
        # When a command returns multiple items you get asked to confirm listing of all of the objects
        re_f5_display_all_prompt = r'Display all [0-9]* items\? \(y/n\) $'
        #
        re_cisco_more_prompt = r' --More--'
        #
        # select which regex to use to check for a deviceprompt
        if prompt_type == 'linux':
            re_prompt = r'\$ $'
        elif prompt_type == 'cisco_ios':
            re_prompt = r'\$ $'
        elif prompt_type == 'bigip_tmsh':
            re_prompt = r'\)# $'
        elif prompt_type == 'bigip_bash':
            re_prompt = '~ #|\)#'
        else:
            re_prompt = r'\$ $'

        alldata = ''
        recv_data = ''

        print('----- sendshell {0}'.format(command))
        if (self.shell):
            self.shell.send(command + "\n")
            time.sleep(0.5)
            while not re.search(re_prompt, alldata):
                # Print data when available
                if self.shell != None and self.shell.recv_ready():
                    recv_data = self.shell.recv(9999)
                    while self.shell.recv_ready():
                        recv_data += self.shell.recv(9999)
                    alldata = str(recv_data,'utf-8')
                    # alldata.replace('\r','')
                    # strdata = str(alldata, "utf8")
                    # strdata.replace('\r', '')
                    # print(strdata, end="")
                    # if (strdata.endswith("$ ")):
                    #     print("\n$ ", end="")
            alldata = alldata.splitlines()

            print(type(alldata))
            return alldata
        else:
            print("Shell not opened.")



    def sendCommand(self, command):
        if (self.client):
            stdin, stdout, stderr = self.client.exec_command(command)
            while not stdout.channel.exit_status_ready():
                # Print data when available
                if stdout.channel.recv_ready():
                    alldata = stdout.channel.recv(1024)
                    prevdata = b"1"
                    while prevdata:
                        prevdata = stdout.channel.recv(1024)
                        alldata += prevdata

                    print(str(alldata, "utf8"))
        else:
            print("Connection not opened.")


    def process(self):
        global connection
        while True:
            # Print data when available
            if self.shell != None and self.shell.recv_ready():
                alldata = self.shell.recv(1024)
                while self.shell.recv_ready():
                    alldata += self.shell.recv(1024)
                strdata = str(alldata, "utf8")
                strdata.replace('\r', '')
                print(strdata, end="")
                if (strdata.endswith("$ ")):
                    print("\n$ ", end="")


    # FUNCTION: dataread(suppress)
    #
    # INPUT:
    #    suppress (optional parameter)
    #
    # RETURNS:
    #    rcstruct
    #
    # DESCRIPTION:
    # dataread will read form remote server until the prompt is recognized
    # The read will fail if the prompt is not seen in 30 attempts with 1 second
    # timeout
    #
    # The data is returned as an array of outputlines in rcstruct.data
    # rcstruct.rc is set to 0 if there is valid data, non-zero otherwise
    #
    # if the optional suppress parameter is set to True then the command echo
    # and prompt is stripped from the returned data
    def dataread(self, suppress=False):
        if self._debug > 1:
            sys.stdout.write(str(self._debug))

        if self._debug > 5:
            sys.stdout.write('dataread called\n')
            sys.stdout.flush()

        rc = rcstruct()

        t = 0
        buf = None
        msg = ''
        while True:

            t += 1
            if self._debug > 7:
                sys.stdout.write(str(t) + '\n')
                sys.stdout.flush()

            # if 30 times a timeout on recv
            if t > 30:
                sys.stderr.write("Read timeout 30s reached...skip output print\n")
                sys.stderr.flush()
                break

            try:
                msg = self._channel.recv(1024).decode()
            except socket.timeout as e:
                if self._debug > 7:
                    sys.stderr.write('Socket revc timeout\n')
                    sys.stderr.flush()
                continue
            except socket.error as e:
                # stderr
                sys.stderr.write(str(e) + '\n')
                sys.stderr.flush()
                rc.set_rc(21)
                return (rc)

            # other side closed connection?
            if not len(msg):
                sys.stderr.write('other end closed connection\n')
                sys.stderr.flush()
                rc.set_rc(22)
                return (rc)

            # We got here so we received data, reset timer
            t = 0

            # checkpoints strooien CTRL-M in echoed commando :-O
            msg = msg.replace('\r', '')
            if buf is None:
                buf = msg
            else:
                buf += msg

            if self._debug > 9:
                sys.stdout.write('\n<MSG>' + msg + '</MSG>\n')
                sys.stdout.write('\n<BUF>' + buf + '</BUF>\n')
                sys.stdout.flush()

            if self._prompt.search(buf):
                if self._debug > 7:
                    sys.stdout.write('\npromtp regex matched\n')
                break

        # Einde loop. We hebben een prompt gezien of we zijn de 30s voorbij
        if t > 30:
            rc.set_rc(30)
            return (rc)

        # Convert buf to list, one line per listelement
        data = []
        buf = io.StringIO(buf)

        if suppress:
            buf.readline()

        for line in buf:
            if line is None:
                line = ""

            data.append(line)

        if suppress:
            data.pop()

        rc.set_data(data)
        return (rc)


# str_username = "user"
# str_password = "password"
str_username, str_password = login_window()

str_server = "10.10.10.25"

print('===== Connecting =====')
connection = MY_SSH(str_server, str_username, str_password)
connection.debug(8)
print('===== Connected =====')
print('===== Opening shell command =====')
connection.openShell()


ret_val = connection.dataread()
print(ret_val.get_data())
for line in ret_val.get_data():
    print(line.strip())
# print(ret_val)

cmds = ['ls -l /home/pi','ls -l /bin']
for cmd in cmds:
    print('===== Sending command {0} ====='.format(cmd))
    ret_val = (connection.sendShell(cmd,'linux'))
    print('number of lines {0}'.format(len(ret_val)))
    for number,line in enumerate(ret_val):
        print('{0}:{1}'.format(number,line))

connection.closeConnection()
# connection.openShell()
# while True:
#     command = input('$ ')
#     if command.startswith(" "):
#         command = command[1:]
#     connection.sendShell(command)