import sys
import paramiko
import json
import logging
import socket
import os
from jinja2 import Environment, FileSystemLoader
from scp import SCPClient


class SshConnect:

    def __init__(self, compress=True, verbose=False):
        self.ssh = None
        self.transport = None

    def connection(self, hostname, user, passwd, port=22):
        self.user = user
        self.passwd = passwd
        self.port = port
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.ssh.connect(hostname, username=user, password=passwd)
            logging.info("conneted")
            self.transport = self.ssh.get_transport()
            logging.info('succeeded: %s@%s:%d' % (user,
                                                  hostname,
                                                  port))
        except paramiko.SSHException, e:
            print "Password is invalid:", e
        except paramiko.AuthenticationException:
            print "Authentication failed for some reason"
        except socket.error, e:
            print "Socket connection failed:", e
        return self.transport

    def run_command(self, cmd, timeout=10):
        global err
        global out
        self.cmd = cmd
        self.timeout = timeout
        logging.info('running command: (%d) %s' % (timeout, cmd))
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        err = stderr.read().strip()
        out = stdout.read().strip()
        print " stedrr, stdout", err, out
        if not err:
            return out
        else:
            logging.exception("command %s failed to execute", cmd)
            exit("Exit program  command did not run properly")
        print "stderr : ", err

    def __del__(self):
        if self.transport is not None:
            self.transport.close()
            self.transport = None
