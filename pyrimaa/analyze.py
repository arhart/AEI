#! /usr/bin/python

import logging
import socket
import sys
import time

from ConfigParser import SafeConfigParser

from pyrimaa import aei, board

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("analyze")

def main(args=sys.argv):
    if len(args) < 2:
        print "usage: analyze <board or movelist file> [move to analyze]"
        sys.exit()

    have_board = False
    pfile = open(args[1], 'r')
    plines = pfile.readlines()
    plines = [l.strip() for l in plines]
    plines = [l for l in plines if l]
    while plines and not plines[0][0].isdigit():
        del plines[0]
    if not plines:
        print "File %s does not appear to be a board or move list." % (args[1],)
        sys.exit()
    if len(plines) < 2 or plines[1][0] != '+':
        have_board = False
        if len(args) > 2:
            stop_move = args[2]
        else:
            stop_move = None
        move_list = []
        while plines and plines[0][0].isdigit():
            move = plines.pop(0)
            if stop_move and move.startswith(stop_move):
                break
            move_list.append(move)
    else:
        movenum, pos = board.parse_long_pos(plines)
        have_board = True

    pfile.close()

    config = SafeConfigParser()
    if config.read("analyze.cfg") != ["analyze.cfg"]:
        print "Could not open 'analyze.cfg'"
        sys.exit(1)

    strict_checks = False
    if config.has_option("global", "strict_checks"):
        strict_checks = config.getboolean("global", "strict_checks")
        if strict_checks:
            print "Enabling full legality checking on moves"

    strict_setup = None
    if config.has_option("global", "strict_setup"):
        strict_setup = config.getboolean("global", "strict_setup")
        if strict_setup:
            print "Enabling full legality checking on setup"
        else:
            print "Disabling full legality checking on setup"


    bot_section = config.get("global", "default_engine")
    if config.has_option(bot_section, "communication_method"):
        com_method = config.get(bot_section, "communication_method").lower()
    else:
        com_method = "stdio"
    enginecmd = config.get(bot_section, "cmdline")

    eng_com = aei.get_engine(com_method, enginecmd, log)
    eng = aei.EngineController(eng_com)

    for option in config.options(bot_section):
        if option.startswith("bot_"):
            value = config.get(bot_section, option)
            eng.setoption(option[4:], value)

    eng.newgame()
    if have_board:
        eng.setposition(pos)
    else:
        pos = board.Position(board.Color.GOLD, 4, board.BLANK_BOARD)
        for mnum, move in enumerate(move_list):
            move = move[3:]
            if mnum < 2 and setup_checks is not None:
                do_checks = setup_checks
            else:
                do_checks = strict_checks
            pos = pos.do_move_str(move, do_checks)
            eng.makemove(move)
    print pos.board_to_str()

    for option in config.options(bot_section):
        if option.startswith("post_pos_"):
            value = config.get(bot_section, option)
            eng.setoption(option[9:], value)

    search_position = True
    if config.has_option("global", "search_position"):
        sp_str = config.get("global", "search_position")
        search_position = not (sp_str.lower() in ["false", "0", "no"])
    if search_position:
        eng.go()

    while True:
        try:
            resp = eng.get_response(10)
            if resp.type == "info":
                print resp.message
            elif resp.type == "log":
                print "log: %s" % resp.message
            elif resp.type == "bestmove":
                print "bestmove: %s" % resp.move
                break
        except socket.timeout:
            if not search_position:
                break

    eng.quit()
    stop_waiting = time.time() + 20
    while time.time() < stop_waiting:
        try:
            resp = eng.get_response(1)
            if resp.type == "info":
                print resp.message
            elif resp.type == "log":
                print "log: %s" % (resp.message)
        except socket.timeout:
            try:
                eng.quit()
            except IOError:
                pass
        if eng.engine.proc.poll() is not None:
            break
    eng.cleanup()

if __name__ == "__main__":
    main()
