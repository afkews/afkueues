import socket
import threading
import sys
import string
import re
import os
import time

from CWatchdog import CWatchdog

regex_steamID = re.compile('.*(steamcommunity.com/id/\w+)')
regex_profileID = re.compile('.*(steamcommunity.com/profiles/\d+)')

regex_mod = re.compile('@badges=.*moderator/\d[,;]?')
regex_sub = re.compile('@badges=.*subscriber/\d[,;]?')
regex_color = re.compile('color=#([0-9a-fA-F]{6})?')


class CBotIRC:
    def privmsg_cb(self, sender_info, receiver, text):
        return None

    def part_cb(self, sender_info, chan):
        return None

    def join_cb(self, sender_info, chan):
        return None

    def quit_cb(self, sender_info):
        return None

    def parse(self, msg):
        is_mod = 0
        is_sub = 0
        color = 0
        if msg[0] == ':':
            args = msg.split(" :", 1)
            header = args[0]
            if len(args) > 1:
                message = args[1]
            else:
                message = ""
        elif msg[0] == '@':
            args = msg.split(" :", 2)
            mod_match = regex_mod.match(args[0])
            sub_match = regex_sub.match(args[0])
            color_match = regex_color.match(args[0])
            if mod_match:
                is_mod = 1
            if sub_match:
                is_sub = 1
            if color_match:
                color = int(color_match.group(1))
            header = args[1]
            if len(args) > 2:
                message = args[2]
            else:
                message = ""

        headerArgs = header.split(" ")
        sender = headerArgs[0].split("!")
        nick = re.sub('[:]', '', sender[0])
        sender_info = (nick, is_mod, is_sub, color)

        if headerArgs[1] == "PRIVMSG":
            self.privmsg_cb(sender_info, headerArgs[2], message)
        if headerArgs[1] == "WHISPER":
            self.privmsg_cb(sender_info, headerArgs[2], message)
        elif headerArgs[1] == "PART":
            self.part_cb(sender_info, headerArgs[2])
        elif headerArgs[1] == "JOIN":
            self.join_cb(sender_info, headerArgs[2])
        elif headerArgs[1] == "QUIT":
            self.quit_cb(sender_info)

    def thread_recv(self):
        while not self.irc_connected:
            time.sleep(0.1)
        readbuffer = ""
        self.irc.settimeout(0.2)

        while not self.stop_thread_recv:
            try:
                readbuffer = readbuffer + self.irc.recv(4096).decode("utf-8")
                readbuffer = readbuffer.replace('\r', '')
                sys.stdout.write(readbuffer)
                temp = str.split(readbuffer, "\n")
                readbuffer = temp.pop()
                for line in temp:
                    line1 = str.rstrip(line)
                    line2 = str.split(line1)
                    if line2[0] == "PING":
                        self.ping_watchdog.reset()
                        self.irc.sendall(
                            ("PONG %s\r\n" % line2[1]).encode('utf-8'))
                    elif line[0][0] in [':', '@']:
                        self.parse(line)
            except socket.timeout:
                True

        print("thread_recv done")

    def __init__(self):
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.irc_connected = False
        self.handler = threading.Thread(target=self.thread_recv)
        self.ping_watchdog = CWatchdog(self.watchdog_triggered, 6*60)
        self.stop_thread_recv = True
        self.auto_cmds = []

    def add_auto_cmd(self, cmd):
        self.auto_cmds.append(cmd)

    def watchdog_triggered(self):
        self.irc_connected = False

    def command(self, cmd):
        self.irc.send(("%s\r\n" % cmd).encode('utf-8'))

    def connect(self):
        self.irc_connected = False
        while not self.irc_connected:
            try:
                self.irc.settimeout(5)
                self.irc.connect((self.server, self.port))
                self.irc_connected = True
            except:
                self.irc_connected = False
                print("Connection failed, retrying...")
                time.sleep(1)
        self.stop_thread_recv = False
        self.handler.start()
        self.command("USER %s %s %s BotIRC" %
                     (self.nick, self.nick, self.nick))
        self.command("PASS %s" % (self.pwd))
        self.command("NICK %s" % (self.nick))
        time.sleep(10)
        for auto_cmd in self.auto_cmds:
            self.command(auto_cmd)
            time.sleep(1)
        self.ping_watchdog.start()

    def close(self):
        self.stop_thread_recv = True
        self.handler.join()
        self.irc.close()
        self.ping_watchdog.stop()

    def isConnected(self):
        return self.irc_connected
