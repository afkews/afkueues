import time

from CAfkueues import CAfkueues
from CCommandLine import CCommandLine

__SERVER__ = "irc.chat.twitch.tv"
__PORT__ = 6667

__CHANNEL__ = "" # fill in with channel you want to scrape
__NICK__ = "" # fill in your bot's account name
__PASS__ = "" # fill in your bot's account oath:blablabla

if __name__ == "__main__":
    cmdline = CCommandLine()
    exit_bot = False
    while not exit_bot:
        bot = CAfkueues(__SERVER__, __PORT__, __NICK__, __PASS__)
        bot.add_auto_cmd("JOIN #%s" % __CHANNEL__)
        bot.add_auto_cmd("JOIN #%s" % __NICK__)
        bot.add_auto_cmd("CAP REQ :twitch.tv/membership")
        bot.add_auto_cmd("CAP REQ :twitch.tv/tags")
        bot.add_auto_cmd("CAP REQ :twitch.tv/commands")
        bot.connect()

        while bot.isConnected():
            cmd = cmdline.getCommand()
            if cmd in ["quit", "exit"]:
                cmdline.close()
                exit_bot = True
                break
            elif cmd:
                bot.command(cmd)
                cmdline.setDone()
            else:
                time.sleep(0.1)
        bot.close()

    print("main thread done.")
