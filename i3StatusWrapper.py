#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This script is a simple wrapper which prefixes each i3status line with custom
# information. It is a python reimplementation of:
# http://code.stapelberg.de/git/i3status/tree/contrib/wrapper.pl
#
# To use it, ensure your ~/.i3status.conf contains this line:
#     output_format = "i3bar"
# in the 'general' section.
# Then, in your ~/.i3/config, use:
#     status_command i3status | ~/i3status/contrib/wrapper.py
# In the 'bar' section.
#
# In its current version it will display the cpu frequency governor, but you
# are free to change it to display whatever you like, see the comment in the
# source code below.
#
# ? 2012 Valentin Haenel <valentin.haenel@gmx.de>
#
# This program is free software. It comes without any warranty, to the extent
# permitted by applicable law. You can redistribute it and/or modify it under
# the terms of the Do What The Fuck You Want To Public License (WTFPL), Version
# 2, as published by Sam Hocevar. See http://sam.zoy.org/wtfpl/COPYING for more
# details.

import sys
import os
import json

def get_governor():
    """ Get the current governor for cpu0, assuming all CPUs use the same. """
    with open('/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor') as fp:
        return fp.readlines()[0].strip()

def print_line(message):
    """ Non-buffered printing to stdout. """
    sys.stdout.write(message + '\n')
    sys.stdout.flush()

def read_line():
    """ Interrupted respecting reader for stdin. """
    # try reading a line, removing any extra whitespace
    try:
        line = sys.stdin.readline().strip()
        # i3status sends EOF, or an empty line
        if not line:
            sys.exit(3)
        return line
    # exit on ctrl-c
    except KeyboardInterrupt:
        sys.exit()

def makeMem():
  # memory from proc
  # memory=float(os.popen("awk '/MemFree/ {print $2}' /proc/meminfo").read())
  memory=float(os.popen("free -m | sed -n '/Mem/s/ \+/ /gp' | cut -d ' ' -f7").read())
  memory/=1e3
  memory=round(memory,1)
  return memory

def makeVolume():
  import re
  amixer=os.popen("amixer sget Master").read()
  percents=re.compile("\d\d%").findall(amixer)
  volume=" ".join(percents)
  return volume

def getClip():
    """ get xclipboard, truncate """
    clip = os.popen("xclip -o").read()
    clip = clip.replace("\n"," ")
    # clip = str(repr(clip))
    # clip = clip[1:-1]
    # clip = clip.replace(" ","")
    maxLen = 15
    if len(clip)>maxLen:
        clip=clip[:maxLen-3]+"..."
    return '"{0}"'.format(clip)

def getTemp():
    """ get temperatuire """
    import os, json
    f= os.popen("sensors -j").readlines()
    f = json.load(os.popen("sensors -j"))
    temp = f["pch_skylake-virtual-0"]["temp1"]["temp1_input"]
    return str(temp)


if __name__ == '__main__':
    # Skip the first line which contains the version header.
    print_line(read_line())

    # The second line contains the start of the infinite array.
    print_line(read_line())

    while True:
        line, prefix = read_line(), ''
        # ignore comma at start of lines
        if line.startswith(','):
            line, prefix = line[1:], ','

        j = json.loads(line)
        # insert information into the start of the json, but could be anywhere
        # CHANGE THIS LINE TO INSERT SOMETHING ELSE
        brightness=os.popen("cat /sys/class/backlight/intel_backlight/brightness").read()[:-1]
        brightness="S:{0}".format(brightness)
        j.insert(0, {'full_text' : '%s' % brightness, 'name' : 'bright'})
        #
        volume=makeVolume()
        volume="V:{0}".format(volume)
        j.insert(0, {'full_text' : '%s' % volume, 'name' : 'bright'})
        #
        memory="M:{0}G".format(makeMem())
        j.insert(0, {'full_text' : '%s' % memory, 'name' : 'bright'})

        # temperature
        temp=getTemp()
        j.insert(0, {'full_text':"T:"+temp})

        clipboard=getClip()
        j.insert(0, {'full_text':clipboard})


        # and echo back new encoded json
        print_line(prefix+json.dumps(j))
