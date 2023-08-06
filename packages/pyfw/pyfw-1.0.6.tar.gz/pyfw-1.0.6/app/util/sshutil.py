#!/usr/bin/env python
# -*- coding: utf-8 -*-

' module description'
import pexpect

__author__ = 'Andrew Wen'


import paramiko





def ssh_cmd(ip,username, passwd, cmd):

    ret = -1

    ssh = pexpect.spawn('ssh %s@%s "%s"' % (username,ip, cmd))

    try:

        i = ssh.expect(['password:', 'continue connecting (yes/no)?'], timeout=50)

        if i == 0 :

            ssh.sendline(passwd)

        elif i == 1:

            ssh.sendline('yes\n')

            ssh.expect('password: ')

            ssh.sendline(passwd)

        ssh.sendline(cmd)

        r = ssh.read()

        print(r),

        ret = 0

    except pexpect.EOF:

        print("EOF")

        ssh.close()

        ret = -1

    except pexpect.TIMEOUT:

        print("TIMEOUT")

        ssh.close()

        ret = -2
    return ret




def sshclient_execmd(hostname, port, username, password, execmd):

    paramiko.util.log_to_file("paramiko.log")

    try:

        s = paramiko.SSHClient()
        s.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        s.connect(hostname=hostname, port=port, username=username, password=password)
        stdin, stdout, stderr = s.exec_command(execmd)
        #stdin.write("Y")  # Generally speaking, the first connection, need a simple interaction.

        print(str(stdout.read(), encoding="utf-8")),

        s.close()


    except Exception:

        print("error")

def main():
    hostname = '192.168.9.51'
    port = 22
    username = 'root'
    password = '123456'
    execmd = 'docker ps -a'

    sshclient_execmd(hostname, port, username, password, execmd)

    #ssh_cmd(hostname, username, password, execmd)


if __name__ == "__main__":
    main()
