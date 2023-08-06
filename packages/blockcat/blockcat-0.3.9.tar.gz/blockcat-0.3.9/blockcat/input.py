import argparse
import sys
from .simple_query import real_time
from .simple_query import Address_Lookups
from .simple_query import  tx_Lookups
from .json_query import block_lookup
from .json_query import block_lookup_zcash
from .json_query import real_time_zcash
from .json_query import tx_addr_zcash
from .json_query import addr_zcash

APP_DESC="""
    This tool could help you to get information from different blockchains. 
    Type blockcat [-h] to see the usage. 
    This version supports Bitcoin.  
    
    """
print(APP_DESC)


parser = argparse.ArgumentParser()
parser.add_argument('-c','--choose', dest='blockchain', default=None, help="Choose a specified blockchain.                                                                               eg: blockcat -c Bitcoin")

parser.add_argument('-r','--real_time', dest='real_blockchain', default=None, help="The real time information of this specified blockchain will be displayed.                                  eg: blockcat -r Bitcoin")

parser.add_argument('-a','--address', dest='address', default=None, help="Lookup a particular address. Please choose the blockchain before using this.                                 eg: blockcat -c Bitcoin -a $Address")

parser.add_argument('-t','--transaction',dest='tx', default = None, help="Input the transaction hash of the transaction you want to know. Please choose the blockchain before using this.                                                                                 eg: blockcat -c Bitcoin -t $Transaction_Hash")

parser.add_argument('-b','--blockhash',dest='block', default = None, help="Input the block hash of the block you want to know. Please choose the blockchain before using this.             eg: blockcat -c Bitcoin -b $Block_Hash")

#parser.add_argument('-v','--verbose', default=0,help="print more debuging information")
args = parser.parse_args()



def main():
    # choose blockchain
    if args.blockchain == "Bitcoin":
        print("The current chosen blockchain is Bitcoin.")
    else if args.blockchain == "Zcash":
        print("The current chosen blockchain is Zcash.")
    
    # Display the real time information of specified blockchain
    if args.real_blockchain == "Bitcoin":
        print("The current chosen blockchain is Bitcoin.")
        real_time()
    else if args.real_blockchain == "Zcash":
        print("The current chosen blockchain is Zcash.")
        real_time_zcash()


    # look for the details of an address
    if not args.address == None:
        if args.blockchain == "Bitcoin":
            Address_Lookups(args.address)
        
        if args.blockchain == "Zcash":
            addr_zcash(args.address)
        
        if args.blockchain == None:
            print("You need to choose a specified blockchain first.                                    eg: blockcat -c Bitcoin -a $Address")



    # look for the details of a transaction
    if not args.tx == None:
        if args.blockchain == "Bitcoin":
            tx_Lookups(args.tx)
        
        if args.blockchain == "Zcash":
            tx_addr_zcash(args.tx)
        
        if args.blockchain == None:
            print("You need to choose a specified blockchain first.                                 eg: blockcat -c Bitcoin -t $Transaction_hash")


    # look for the details of a block
    if not args.block == None:
        if args.blockchain == "Bitcoin":
            block_lookup(args.block)
        
        if args.blockchain == "Zcash":
            block_lookup_zcash(args.block)
        
        if args.blockchain == None:
            print("You need to choose a specified blockchain first.                                        eg: blockcat -c Bitcoin -t $Block_hash")






