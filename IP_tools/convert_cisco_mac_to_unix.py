#!/usr/bin/env python3

from sys import argv


def usage():
    print("Script for converting Cisco style MAC addresses to Unix format")
    print("Eg. hhhh.hhhh.hhhh to hh:hh:hh:hh:hh:hh")
    print(f"Usage: {argv[0]}: <mac>")
    exit(2)


if len(argv) != 2:
    usage()

mac = argv[1].replace(".", "")
gen = iter(mac)
print(':'.join(a+b for a, b in zip(gen, gen)))
