import requests
from .json_query import tx_addr

url = "https://blockchain.info/q/"

def real_time():
    difficulty = requests.get(url+"getdifficulty").text
    print("Current difficulty target as a decimal number: "+difficulty)
    blockcount = requests.get(url+"getblockcount").text
    print("Current block height in the longest chain: " + blockcount)
    latesthash = requests.get(url+"latesthash").text
    print("Hash of the latest block: " + latesthash)
    bcperblock = requests.get(url+"bcperblock").text
    print("Current block reward in BTC: " + bcperblock)
    totalbc = requests.get(url+"totalbc").text
    print("Total Bitcoins in circulation (delayed by up to 1 hour]): " + totalbc)
    probability = requests.get(url+"probability").text
    print("Probability of finding a valid block each hash attempt: " + probability)
    hashestowin = requests.get(url+"hashestowin").text
    print("Average number of hash attempts needed to solve a block: " + hashestowin)
    nextretarget = requests.get(url+"bcperblock").text
    print("Block height of the next difficulty retarget: " + nextretarget)
    avgtxsize = requests.get(url+"avgtxsize").text
    print("Average transaction size for the past 1000 blocks: " + avgtxsize)
    avgtxvalue = requests.get(url+"avgtxvalue").text
    print("Average transaction value for the past 1000 blocks: " + avgtxvalue)
    interval = requests.get(url+"interval").text
    print("Average time between blocks in seconds: " + interval)
    eta = requests.get(url+"eta").text
    print("Estimated time until the next block (in seconds): " + eta)
    avgtxnumber = requests.get(url+"avgtxnumber").text
    print("Average number of transactions per block for the past 100 blocks: " + avgtxnumber)


def Address_Lookups(address):
    print("The address " + address + " has following information: ")
    received = requests.get(url+"getreceivedbyaddress/"+address).text
    print("The total number of bitcoins received: " + received)
    sent = requests.get(url+"getsentbyaddress/"+address).text
    print("The total number of bitcoins send: " + sent)
    balance = requests.get(url+"addressbalance/"+address).text
    print("The balance of " + address + ": " + balance + " * 10^-8 BTC")
    timestamp = requests.get(url+"addressfirstseen/"+address).text
    print("Timestamp of the block an address was first confirmed in: " + timestamp)


def tx_Lookups(tx):
    print("The transaction " + tx + " has following information: ")
    output = requests.get(url+"txtotalbtcoutput/"+tx).text
    print("Total output value: " + output + " * 10^-8 BTC")
    input = requests.get(url+"txtotalbtcinput/"+tx).text
    print("Total input value: " + input + " * 10^-8 BTC")
    fee = requests.get(url+"txfee/"+tx).text
    print("Fee included in: " + fee + " * 10^-8 BTC")
    tx_addr(tx)


#tx_Lookups("378a5f607645895a7ff55f6e041e5881486904aadcc8687559808cc5cc519a7a")

#Address_Lookups("1EzwoHtiXB4iFwedPr49iywjZn2nnekhoj")
#real_time()

