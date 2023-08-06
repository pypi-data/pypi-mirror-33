import argparse
import sys
from .simple_query import real_time
from .simple_query import Address_Lookups
from .simple_query import  tx_Lookups
from .json_query import block_lookup

APP_DESC="""
    This tool could help you to get information from different blockchains. 
    Type blockcat [-h] to see the usage. 
    This version supports Bitcoin.  
    
    """
print(APP_DESC)

parser = argparse.ArgumentParser()
parser.add_argument('-c','--choose', dest='blockcahin', default=None, help="Choose a specified blockchain. The real time information of this specified blockchain will also be displayed. eg: blockcat -c Bitcoin")
parser.add_argument('-a','--address', dest='address', default=None, help="Lookup a particular address. eg: blockcat -a $address")
parser.add_argument('-t','--transaction',dest='tx', default = None, help="Input the transaction hash of the transaction you want to know. eg: blockcat -t $Transaction_Hash")
parser.add_argument('-b','--blockhash',dest='block', default = None, help="Input the block hash of the block you want to know. eg: blockcat -b $Block_Hash")

#parser.add_argument('-v','--verbose', default=0,help="print more debuging information")
args = parser.parse_args()


def main():
    # choose blockchain
    if args.blockchain == "Bitcoin":
        real_time()
        print("The current chosen blockchain is Bitcoin. You can change the blockchain by: blockcat -c $blockcahin ")

        # look for the details of an address
        if not args.address == None:
            print("The current chosen blockchain is Bitcoin. You can change the blockchain by: blockcat -c $blockcahin ")
            Address_Lookups(args.address)

        # look for the details of a transaction
        if not args.tx == None:
            print("The current chosen blockchain is Bitcoin. You can change the blockchain by: blockcat -c $blockcahin ")
            tx_Lookups(args.tx)

        # look for the details of a block
        if not args.block == None:
            print("The current chosen blockchain is Bitcoin. You can change the blockchain by: blockcat -c $blockcahin ")
            block_lookup(args.block)

        if args.blockchain == None:
            if not args.address == None or not args.tx == None or not args.block == None:
                print("You need to choose a specified blockchain first. eg: blockcat -c Bitcoin")






