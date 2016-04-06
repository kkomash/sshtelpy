#!/usr/bin/env python
import telnetlib
import paramico
import select

from enum import Enum


class ConnType(Enum):
    '''
    Enumeration class - types of connection for SSHTelnetConnection class

    '''
    c_none = 0
    c_telnet = 1
    c_ssh = 2
    c_fail = 255

# ----------------------------------------------------------------------------


class SSHTelnetConnection:
    '''
    Class for remote connection to network equipment by Telnet or SSH

    '''

    def __init__(self, host, user, password):
        '''
        Initialize SSHTelnetConnection instance
        '''
        self.host = host         # Host name or IP adress
        self.user = user         # User name for loging in
        self.passwd = password   # User password
        self.logging = False     # is logging enabled
        self.log_file = None     # Log file handle
        self.con_type = ConnType.c_none    # Connection type (telnet, ssh)
        self.tel_conn = None     # Telnet connection handler
        self.ssh_conn_t = paramiko.SSHClient()   # SSH connection handler
        self.ssh_conn = None     # SSH interactive shell
        # Enable auto host key addition (!not safe for security reason!)
        self.ssh_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.debug = False       # Enable additional debug output to console

    def log_to(self, message):
        '''
        Writes message to log file
        '''
        if (self.logging and (self.log_file is not None) and (message != "")):
            try:
                self.log_file.write(message)
            except IOError as e:
                print("I/O error({0}): {1}".format(e.errno, e.strerror))

    def connect(self):
        '''
        Try to connect to host by telnet and ssh
        '''
        # First of all trying to connect by telnet
        self.con_type = ConnType.c_none
        try:
            if (self.debug):
                print("Open telnet connection to {0}\n".format(self.host))
            self.log_to("Open telnet to {0} ...\n".format(self.host))
            self.tel_conn = telnetlib.Telnet(self.host, 23, 30)
            self.tel_conn.read_until("Username:")
            if (self.debug):
                print("Send login\n")
            self.tel_conn.write(user + "\n")
            self.tel_conn.read_until("Password:")
            if (self.debug):
                print("Send password\n")
            tn.write(passwd + "\n")
            self.con_type = ConnType.c_telnet
        except EOFError as e:
            self.con_type = ConnType.c_fail
            print("Telnet failure on {0}: {1}\n".
                  format(self.host, e.strerror))
            self.log_to("Telnet connection failed: {0}\n".format(e.strerror))
        except socket.error as e:
            self.con_type = ConnType.c_fail
            print("Socket error on {0}: {1}\n".format(self.host, e.strerror))
            self.log_to("Socket error: {0}\n".format(e.strerror))
        # If telnet connection was successful return Connection Type: Telnet
        if self.con_type == ConnType.c_telnet:
            return self.con_type
        # Now lets try to connect by SSH
        try:
            if (self.debug):
                print("Open ssh connection to {0}\n".format(self.host))
            self.log_to("Open ssh to {0} ...\n".format(self.host))
            self.ssh_conn_t.connect(self.host, self.user, self.passwd,
                                    look_for_keys=False, allow_agent=False)
            self.ssh_conn = self.ssh_conn_t.invoke_shell()
            self.con_type = ConnType.c_ssh
        except BadHostKeyException as e:
            self.con_type = ConnType.c_fail
            print("SSH error on {0}: {1}\n".format(self.host, e.strerror))
            self.log_to("SSH Error: {0} ...\n".format(e.strerror))
        except AuthenticationException as e:
            # SSH login authentication failed
            self.con_type = ConnType.c_fail
            print("SSH login error on {0}: {1}\n".
                  format(self.host, e.strerror))
            self.log_to("SSH Login Error: {0} ...\n".format(e.strerror))
        except SSHException as e:
            self.con_type = ConnType.c_fail
            print("SSH error on {0}: {1}\n".format(self.host, e.strerror))
            self.log_to("SSH Error: {0} ...\n".format(e.strerror))
        except socket.error as e:
            self.con_type = ConnType.c_fail
            print("Socket error on {0}: {1}\n".
                  format(self.host, e.strerror))
            self.log_to("Socket Error: {0} ...\n".format(e.strerror))
        return self.con_type

    def set_log_file(self, fh):
        '''
        Set parameters of logging to file
        '''
        self.log_file = fh   # Log file handle

    def set_host(self, host):
        '''
        Set host name to connect to
        '''
        self.host = host     # Host name

    def set_user_login(self, user, password):
        '''
        Set user login cridentials
        '''
        self.user = user         # User name
        self.passwd = password   # User password

    def enable_logging(self):
        '''
        Enable logging to file
        '''
        self.logging = True

    def disable_logging(self):
        '''
        Disable logging to file
        '''
        self.logging = False

    def read_until(self, string, timeout=None):
        '''
        Reads from telnet or ssh session until string is found.
        Returns recieved data.
        '''
        if (self.con_type == ConnType.c_telnet):
            # try:
            return tel_conn.read_until(string, timeout)
            # except socket.error as e:
            #     print("Socket error on {0}: {1}\n".
            #           format(self.host, e.strerror))
            #     self.log_to("Socket error: {0}\n".format(e.strerror))
        elif (self.con_type == ConnType.c_ssh):
            # try:
            dList = ""       # buffer to save recieved data
            l = len(string)  # length of search string
            # Lets wait for some data from socket
            while self.ssh_conn
            while string not in "".join(dList):
                dList.append(ssh_conn.recv(1))
            return "".join(dList)
            # except socket.error as e:
            # print("Socket error on {0}: {1}\n".
            #       format(self.host, e.strerror))
            # self.log_to("Socket error: {0}\n".format(e.strerror))

    def disable_paging(self):
        '''
        Disable Cisco terminal paging
        '''
        if (self.con_type == ConnType.c_telnet):
            try:
                tel_conn.write("terminal length 0\n")
                tel_conn.read_until(self.host + "#")
            except socket.error as e:
                print("Socket error on {0}: {1}\n".
                      format(self.host, e.strerror))
                self.log_to("Socket error: {0}\n".format(e.strerror))
        elif (self.con_type == ConnType.c_ssh):
            try:
                ssh_conn.send("terminal length 0\n")
                !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            except socket.error as e:
                print("Socket error on {0}: {1}\n".
                      format(self.host, e.strerror))
                self.log_to("Socket error: {0}\n".format(e.strerror))

    def write(self, string):
        '''
        Write string to opened telnet or ssh
        '''
        if (self.con_type == ConnType.c_telnet):
            try:
                tel_conn.write(string)
            except socket.error as e:
                print("Socket error on {0}: {1}\n".
                      format(self.host, e.strerror))
                self.log_to("Socket error: {0}\n".format(e.strerror))
        elif (self.con_type == ConnType.c_ssh):
            try:
                ssh_conn.send(string)
            except socket.error as e:
                print("Socket error on {0}: {1}\n".
                      format(self.host, e.strerror))
                self.log_to("Socket error: {0}\n".format(e.strerror))

    def close(self):
        '''
        Close opened connection
        '''
        if (self.con_type == ConnType.c_telnet):
            try:
                tel_conn.close()
                self.con_type = ConnType.c_none
            except socket.error as e:
                print("Socket error on {0}: {1}\n".
                      format(self.host, e.strerror))
                self.log_to("Socket error: {0}\n".format(e.strerror))
        elif (self.con_type == ConnType.c_ssh):
            try:
                ssh_conn_t.close()
                self.con_type = ConnType.c_none
            except socket.error as e:
                print("Socket error on {0}: {1}\n".
                      format(self.host, e.strerror))
                self.log_to("Socket error: {0}\n".format(e.strerror))

# ----------------------------------------------------------------------------
