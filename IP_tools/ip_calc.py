#!/usr/bin/env python3

import ipaddress
from typing import Sequence
from argparse import ArgumentParser, Namespace

LENGTH = 32
TYPES = ("global", "private", "link-local", "loopback", "multicast", "reserved", "unspecified")


def parse_args(args: Sequence = None) -> Namespace:
    parser = ArgumentParser(description="Simple script to mimic the 'ipcalc' command on Linux. Works for both IPv4 and IPv6")
    parser.add_argument("ip_address", type=ipaddress.ip_interface, help="The IP network to calculate")
    parser.add_argument("-b", "--binary", action="store_true", help="Display binary representation")
    parser.add_argument(
        "-ls", "--last-search", action="store_true", help="Search for the last host, " "instead of deriving from bcast (CPU heavy)"
    )
    return parser.parse_args(args=args)


def get_binary_string_rep(number: int) -> str:
    """
    Converts number to binary string rep (per 8 bits)
    """
    binary = bin(number)[2:].zfill(LENGTH)
    return ".".join(binary[i: i + 8].zfill(8) for i in range(0, len(binary), 8))


def print_formatted(first: str, second: str, third: str) -> None:
    print("{:<10} {:<40} {:<10}".format(first, second, third))


def get_type(network: ipaddress.ip_network) -> str:
    """
    For all types in TYPES, check if the ip_network is of that type, if so return it's name
    """
    for t in TYPES:
        if getattr(network, f"is_{t}"):
            return t


def main(args: Sequence = None) -> None:
    global LENGTH
    args = parse_args(args=args)
    ip = args.ip_address
    LENGTH = 32 if ip.version == 4 else 128

    # Host binary
    addr_binary_string = get_binary_string_rep(int(ip.ip))
    netmask_binary_string = get_binary_string_rep(int(ipaddress.ip_address(ip.with_netmask.split("/")[1])))
    wildcard_binary_string = get_binary_string_rep(int(ipaddress.ip_address(ip.with_hostmask.split("/")[1])))

    # Network binary
    network = ip.network
    network_binary_string = get_binary_string_rep(int(network.network_address))
    broadcast_binary_string = get_binary_string_rep(int(network.broadcast_address))
    hosts = network.hosts()
    first_host = next(hosts)
    min_host_binary_string = get_binary_string_rep(int(first_host))
    if args.last_search:
        *_, last_host = hosts
    else:
        # Dirty hack to get a speedy last host
        last_host = network.broadcast_address - 1
    max_host_binary_string = get_binary_string_rep(int(last_host))

    # Host info
    print_formatted("Address:", str(ip.ip), addr_binary_string if args.binary else "")
    print_formatted("Netmask:", ip.with_netmask.split("/")[1], netmask_binary_string if args.binary else "")
    print_formatted("Wildcard:", ip.with_hostmask.split("/")[1], wildcard_binary_string if args.binary else "")
    print("=>")

    # Network Info
    print_formatted("Network:", f"{str(network.network_address)}/{network.prefixlen}", network_binary_string if args.binary else "")
    print_formatted("Broadcast:", str(network.broadcast_address), broadcast_binary_string if args.binary else "")
    print_formatted("HostMin:", str(first_host), min_host_binary_string if args.binary else "")
    print_formatted("HostMax:", str(last_host), max_host_binary_string if args.binary else "")
    print_formatted("Hosts/Net:", f"{network.num_addresses - 2}", f"{bin(network.num_addresses - 2)[2:]}" if args.binary else "")
    print_formatted("Type:", get_type(network), "")


if __name__ == "__main__":
    main()
