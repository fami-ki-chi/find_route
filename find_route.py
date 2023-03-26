# coding: UTF-8
from __future__ import annotations
import sys
import csv


class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_leaf = False
        self.prefix = None
        self.nexthoptype = None
        self.nexthop = None


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, prefix, nexthoptype, nexthop):
        node = self.root

        tmp = prefix.split('/')
        binary_addr = decimal_to_binary(tmp[0])
        prefix_length = int(tmp[1])

        for char in str(binary_addr)[:prefix_length]:
            if char not in node.children:
                node.children[char] = TrieNode()

            node = node.children[char]

        node.is_leaf = True
        node.prefix = prefix   

        if node.nexthoptype:
            node.nexthoptype = node.nexthoptype + ' ,' + nexthoptype
            node.nexthop = node.nexthop + ' ,' + nexthop
        else:
            node.nexthoptype = nexthoptype
            node.nexthop = nexthop


    def longest_match(self, ip_address) -> 'Trie':
        node = self.root
        
        for char in ip_address:
            if char in node.children:
                node = node.children[char]
            else:
                break
        
        return node


def decimal_to_binary(decimal_addr):
        tmp = decimal_addr.split('.')
        binary_addr = ''
        for octet in tmp:
            binary_addr = binary_addr + format(int(octet),'08b')

        return binary_addr

def find_route(dest_addr, csv_file):

    try:
        # Open CSV file
        with open(csv_file, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)

            trie = Trie()
            default_gateway_type = ''
            default_gateway = ''

            for row in reader:

                # NIC effective route: row = [RouteSource, DestinationSubnets, DestinationServiceTags, NextHopType, NextHops, IsEnabled]
                if row[1] == '0.0.0.0/0':
                    default_gateway_type = default_gateway_type + row[3]
                    default_gateway =  default_gateway + row[4]
                else:
                    # Insert routes
                    trie.insert(row[1],row[3],row[4])

            binary_dest_addr = decimal_to_binary(dest_addr)
            match = trie.longest_match(binary_dest_addr)

            if match.is_leaf == False:
                if default_gateway_type:
                    print(f"Route to {dest_addr} is found!")
                    print(f"  Prefix: 0.0.0.0/0")
                    print(f"  NextHopType: {default_gateway_type}")
                    print(f"  NextHop: {default_gateway}")
                else:
                    print(f"There is no route to {dest_addr}")
            else:
                    print(f"Route to {dest_addr} is found!")
                    print(f"  Prefix: {match.prefix}")
                    print(f"  NextHopType: {match.nexthoptype}")
                    print(f"  NextHop: {match.nexthop}")

            return 0

    except ValueError:
        print("Error!")
        return 1


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python longest_match.py Dest_Addr(X.X.X.X) RouteTable.csv")
        sys.exit()

    dest_addr = str(sys.argv[1])
    csv_file = str(sys.argv[2])
    sys.exit(find_route(dest_addr, csv_file))
