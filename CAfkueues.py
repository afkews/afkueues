# encoding: utf-8
import datetime
import time
import re

from CBotIRC import CBotIRC
from CExecutiveSQL import CExecutiveSQL

__MINUTE = 60
__HOUR = 60 * __MINUTE
__DAY = 24 * __HOUR

__WHISPER_PUB__ = "Viva, reparei que procuras pessoal para jogar. O https://electrack.ddns.net organiza "
"e filtra as últimas 24 horas do chat do Zorlak para te ajudar nisso. Beep boop sou um"
" bot :) https://twitter.com/afkews"

levels = ["nivel", "nível", "level", "lvl", "nvl", "lv", "nv"]

keywords = [
    ["s1", "silvers", "silver s", "si", "silver1", "silveri", "silver 1", "silver i", "silvers 1",
        "silvers i", "p1", "pi", "prata1", "pratai", "prata 1", "prata i", "silver um", "prata um"],
    ["s2", "silvers", "silver s", "sii", "silver2", "silverii", "silver 2", "silver ii", "silvers 2",
     "silvers ii", "p2", "pii", "prata2", "prataii", "prata 2", "prata ii", "silver dois", "prata dois"],
    ["s3", "silvers", "silver s", "siii", "silver3", "silveriii", "silver 3", "silver iii", "silvers 3",
     "silvers iii", "p3", "piii", "prata3", "prataiii", "prata 3", "prata iii", "silver tres", "prata tres"],
    ["s4", "silvers", "silver s", "siv", "silver4", "silveriv", "silver 4", "silver iv", "silvers 4",
     "silvers iv", "p4", "piv", "prata4", "prataiv", "prata 4", "prata iv", "silver quatro", "prata quatro"],
    ["sv", "silvers", "silver s", "silver5", "silverv", "silver 5", "silver v", "silvers 5", "silvers v",
     "p5", "pv", "prata5", "pratav", "prata 5", "prata v", "silver elite", "prata elite", "prata de elite"],
    ["svi", "silvers", "silver s", "silver6", "silvervi", "silver 6", "silver vi", "silvers 6", "silvers vi",
            "p6", "pvi", "prata6", "pratavi", "prata 6", "prata vi", "silver elite master", "prata elite mestre "],
    ["g1", "gn1", "gn 1", "golds", "gold s", "gi", "gold1", "goldi", "gold 1", "gold i", "golds 1",
     "golds i", "o1", "oi", "ouro1", "ouroi", "ouro 1", "ouro i", "gold um", "ouro um"],
    ["g2", "gn2", "gn 2", "golds", "gold s", "gii", "gold2", "goldii", "gold 2", "gold ii", "golds 2",
     "golds ii", "o2", "oii", "ouro2", "ouroii", "ouro 2", "ouro ii", "gold dois", "ouro dois"],
    ["g3", "gn3", "gn 3", "golds", "gold s", "giii", "gold3", "goldiii", "gold 3", "gold iii", "golds 3",
     "golds iii", "o3", "oiii", "ouro3", "ouroiii", "ouro 3", "ouro iii", "gold tres", "ouro tres"],
    ["g4", "gn4", "gn 4", "golds", "gold s", "gnm", "gold4", "gold 4",  "golds 4", "gold iv", "golds iv",
     "gold nm", "o4", "ouro4", "ouro 4", "gold quatro", "gold nova master", "ouro nova mestre"],
    ["mg1", "aks", "ak", "ak1", "aks1", "aki", "mg", "mgi", "ak 1", "aks 1",
            "mg 1", "mg i", "ak i", "master guardian 1", "master guardian i"],
    ["mg2", "aks", "ak2", "aks2", "akii", "mgii", "ak 2", "aks 2", "mg 2",
            "mg ii", "ak ii", "master guardian 2", "master guardian ii"],
    ["mge", "aks", "ak3", "akx", "ak x", "master guardian elite",
            "eximio", "cruzada", "cruzado", "cruzadas", "cruzados"],
    ["dmg", "distinguished master guardian", "eximio",
            "eximios", "exímio", "exímios", "dmgs"],
    ["le", "legendary eagle", "les"],
    ["lem", "legendary eagle master", "lems"],
    ["sup", "smfc", "supremo", "supremos", "supreme"],
    ["ge", "tge", "global", "globals", "globais", "globas"]
]

regex_steamID = re.compile('.*(steamcommunity.com/id/[a-zA-Z0-9\-\_]+)')
regex_profileID = re.compile('.*(steamcommunity.com/profiles/\d+)')
regex_faceit = re.compile('.*(beta.faceit.com/[a-zA-Z]{2}/players/[a-zA-Z0-9\-\_]+)')
regex_betafaceit = re.compile('.*(www.faceit.com/[a-zA-Z]{2}/players/[a-zA-Z0-9\-\_]+)')

regex_lvls = []
for keyword in levels:
    regex_lvls.append(re.compile('.*?%s[ ]*(\d+)[ ]*' % keyword))

regex_number = re.compile('(\d+)')


class CAfkueues(CBotIRC):
    def __init__(self, server, port, nick, pwd):
        self.flat_ordered_keywords = []
        for synonyms in keywords:
            for synonym in synonyms:
                self.flat_ordered_keywords.append(synonym)
        self.flat_ordered_keywords.sort(key=len, reverse=True)
        print(self.flat_ordered_keywords)
        self.server = server
        self.port = port
        self.nick = nick
        self.pwd = pwd
        CBotIRC.__init__(self)
        self.database = CExecutiveSQL('/var/www/afkueues/Afkueues.db')
        self.database.verbose = True
        logfile_name = datetime.datetime.fromtimestamp(
            time.time()).strftime('Afkeueues_%d_%m_%Y__%H_%M_%S.log')
        self.logfile = open("/var/www/afkueues/logs/%s" % logfile_name, 'w')

    def print_log(self, msg):
        timestamp = datetime.datetime.fromtimestamp(
            time.time()).strftime('%d-%m-%Y %H:%M:%S')
        self.logfile.write('[%s] %s\n' % (timestamp, msg))
        self.logfile.flush()

    def __updated_lvls(self, current, new):
        if current:
            (min_lvl, max_lvl) = current
            min_lvl = str(min(int(min_lvl), int(new)))
            max_lvl = str(max(int(max_lvl), int(new)))
            return (min_lvl, max_lvl)
        else:
            return (new, new)

    def privmsg_cb(self, sender_info, receiver, text):
        (sender_nick, sender_mod, sender_sub, sender_color) = sender_info
        text = text.replace("'", " ")
        text = text.replace('"', " ")
        if receiver == self.nick:
            self.command("PRIVMSG %s :/w yourpersonalnickhere <%s>%s" %
                         (receiver, sender_nick, text))

        if receiver != self.nick:
            st = text
            link = None
            faceit_link = None
            index_min = index_max = None

            steamID = regex_steamID.match(text)
            profileID = regex_profileID.match(text)
            faceitID = regex_faceit.match(text)
            beta_faceitID = regex_betafaceit.match(text)
            if steamID:
                link = "http://%s" % steamID.group(1)
            if profileID:
                link = "http://%s" % profileID.group(1)
            if faceitID:
                faceit_link = "http://%s" % faceitID.group(1)
            if beta_faceitID:
                faceit_link = "http://%s" % beta_faceitID.group(1)

            if not (link or faceit_link):
                return

            st = st.replace("/", " ")
            st = st.replace("+", " ")
            st = st.replace("=", " ")
            st = st.replace("-", " ")
            st = st.replace("\\", " ")
            st = st.replace("|", " ")
            st = st.replace("{", " ")
            st = st.replace("}", " ")
            st = st.replace("(", " ")
            st = st.replace(")", " ")
            st = st.replace(",", " ")
            st = st.replace(".", " ")
            st = st.replace(":", " ")
            st = st.replace(";", " ")
            st = st.replace("[", " ")
            st = st.replace("]", " ")
            st = st.replace('*', ' ')
            st = st.replace('_', ' ')
            st = st.replace('~', ' ')
            st = st.replace('^', ' ')
            st = st.replace('<', ' ')
            st = st.replace('>', ' ')
            st = st.replace('!', ' ')
            st = st.replace('?', ' ')
            st = st.replace('%', ' ')
            st = st.replace('#', ' ')
            st = st.replace('&', ' ')
            st = st.replace(' e ', ' ')
            st = ' '.join(st.split())
            st = st.lower()

            st_steam = st
            index_found = []
            for keyword in self.flat_ordered_keywords:
                if " %s " % keyword in " %s " % st_steam:
                    for synonyms in keywords:
                        rank = keywords.index(synonyms)
                        for synonym in synonyms:
                            if keyword == synonym:
                                index_found.append(rank)
                    st_steam = st_steam.replace(keyword, '')
            index_found = list(set(index_found))
            index_found.sort()

            if len(index_found) > 0:
                index_min = index_found[0]
                index_max = index_found[-1]

            st_faceit = st
            print("searching in '%s'" % st_faceit)
            faceit_lvls = None
            for regex in regex_lvls:
                regex_match = regex.match(st_faceit)
                if regex_match:
                    print("found %s" % regex_match.group(1))
                    faceit_lvls = self.__updated_lvls(
                        faceit_lvls, regex_match.group(1))
                    new_st = st_faceit.replace(
                        st_faceit[regex_match.start():regex_match.end()], "")
                    parts = new_st.split(" ")
                    for part in parts:
                        print("found %s" % regex_match.group(1))
                        number_match = regex_number.match(part)
                        if number_match:
                            faceit_lvls = self.__updated_lvls(
                                faceit_lvls, number_match.group(1))
                        else:
                            break

            rank_min = str(index_min) if index_min != None else "NULL"
            rank_max = str(index_max) if index_max != None else "NULL"
            (lvl_min, lvl_max) = faceit_lvls if faceit_lvls != None else (
                "NULL", "NULL")
            if (lvl_min == lvl_max == rank_min == rank_max == "NULL"):
                return

            sql = 'SELECT Whisper FROM Log WHERE Nick == "%s"' % sender_nick
            whisper = self.database.execute(sql)
            if not whisper or whisper == [(None,)]:
                self.command("PRIVMSG %s :/w %s %s" %
                             (receiver, sender_nick, __WHISPER_PUB__))

            reg = '(\"%s\", %s, %s, \"%s\", %s, %s, %.0f, \"%s\", %d, \"%s\", %s, %s, 1)' % (sender_nick, sender_mod, sender_sub,
                                                                                             link if link else "", rank_min, rank_max, time.time(), text, sender_color, faceit_link if faceit_link else "", lvl_min, lvl_max)
            self.database.execute('INSERT or REPLACE into Log values %s' % reg)

            ranks = ""
            if index_min != None:
                if index_min == index_max:
                    ranks = "%s" % keywords[index_min][0].upper()
                else:
                    ranks = "[%s-%s]" % (keywords[index_min]
                                         [0].upper(), keywords[index_max][0].upper())

            self.print_log("\033[0;31m%s%s%s %s %s from \"%s\"\033[0m" % (
                "MOD " if sender_mod == 1 else "", "SUB " if sender_sub == 1 else "", sender_nick, link, ranks, text))

    def close(self):
        CBotIRC.close(self)
        self.database.stop()
