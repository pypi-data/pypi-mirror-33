import argparse
import sys
from .simple_query import real_time
from .simple_query import Address_Lookups
from .simple_query import  tx_Lookups
from .json_query import block_lookup

APP_DESC="""
    This tool could help you to get information from different blockchains. Type blockcat [-h] to see the usage. This version supports Bitcoin.  """
print(APP_DESC)

parser = argparse.ArgumentParser()
parser.add_argument('-r','--real_time_infomation', dest='real', default=None, help="Display the real time information of specified blockchain. eg: blockcat -r Bitcoin")
parser.add_argument('-a','--address', dest='address', default=None, help="Lookup a particular address. eg: blockcat -a $address")
parser.add_argument('-t','--transaction',dest='tx', default = None, help="Input the transaction hash of the transaction you want to know. eg: blockcat -t $Transaction_Hash")
parser.add_argument('-b','--blockhash',dest='block', default = None, help="Input the block hash of the block you want to know. eg: blockcat -b $Block_Hash")

#parser.add_argument('-v','--verbose', default=0,help="print more debuging information")


args = parser.parse_args()


def main():
    if args.real == "Bitcoin":
        real_time()
    if not args.address == None:
        Address_Lookups(args.address)
    if not args.tx == None:
        tx_Lookups(args.tx)
    if not args.block == None:
        block_lookup(args.block)
