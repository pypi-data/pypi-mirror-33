import json
import requests

#These two functions are bitcoin functions
url = "https://blockchain.info/rawtx/"
burl = "https://blockchain.info/rawblock/"

#seek the input and output address of a specified transaction
def tx_addr(tx):
    transaction = json.loads(requests.get(url + tx).text)
    if transaction["inputs"]:
        try:
            prev_out = transaction["inputs"][0]["prev_out"]
            input_addr = prev_out["addr"]
            print("Input address is: " + input_addr)
        except KeyError:
            return
    if transaction["out"]:
        try:
            out = transaction["out"][0]
            output_addr = out["addr"]
            print("Output address is: " + output_addr)
        except KeyError:
            print("Unable to decode output address")
            return

def block_lookup(blockhash):
    block = json.loads(requests.get(burl + blockhash).text)
    print("Block "+ blockhash + " has following information: ")
    if block["ver"]:
        try:
            print("Version: " + str(block["ver"]))
        except KeyError:
            return

    if block["prev_block"]:
        try:
            print("Previous block is : " + block["prev_block"])
        except KeyError:
            return

    if block["time"]:
        try:
            print("Time: " + str(block["time"]))
        except KeyError:
            return


    if block["mrkl_root"]:
        try:
            print("Merkle Root: " + block["mrkl_root"])
        except KeyError:
            return


    if block["bits"]:
        try:
            print("Bits: " + str(block["bits"]))
        except KeyError:
            return


    if block["nonce"]:
        try:
            print("Nonce: " + str(block["nonce"]))
        except KeyError:
            return


    if block["n_tx"]:
        try:
            print("Number of transactions: " + str(block["n_tx"]))
        except KeyError:
            return


    if block["size"]:
        try:
            print("Size: " + str(block["size"]))
        except KeyError:
            return


    if block["block_index"]:
        try:
            print("Block index: " + str(block["block_index"]))
        except KeyError:
            return

    if block["height"]:
        try:
            print("Height: " + str(block["height"]))
        except KeyError:
            return

    if block["received_time"]:
        try:
            print("Received time: " + str(block["received_time"]))
        except KeyError:
            return

    if block["relayed_by"]:
        try:
            print("Relayed_by: " + block["relayed_by"])
        except KeyError:
            return

    if block["tx"]:
        try:
            print("Transactions:")
            for tx in block["tx"]:
                print(tx["hash"])
        except KeyError:
            return


# These four functions are for the Zcash
def block_lookup_zcash(blockhash):
    url = "https://api.zcha.in/v2/mainnet/blocks/"
    block = json.loads(requests.get(url + blockhash).text)
    print("Block "+ blockhash + " has following information: ")
    
    if block["version"]:
        try:
            print("Version: " + str(block["version"]))
        except KeyError:
            return

    if block["size"]:
        try:
            print("Size: " + str(block["size"]))
        except KeyError:
            return

    if block["height"]:
        try:
            print("Height: " + str(block["height"]))
        except KeyError:
            return

    if block["nonce"]:
        try:
            print("Nonce: " + str(block["nonce"]))
        except KeyError:
            return

    if block["time"]:
        try:
            print("Time: " + str(block["time"]))
        except KeyError:
            return


    if block["timestamp"]:
        try:
            print("Timestamp: " + str(block["timestamp"]))
        except KeyError:
            return


    if block["merkleRoot"]:
        try:
            print("Merkle Root: " + block["merkleRoot"])
        except KeyError:
            return


    if block["bits"]:
        try:
            print("Bits: " + str(block["bits"]))
        except KeyError:
            return

    if block["miner"]:
        try:
            print("Miner is: " + block["miner"])
        except KeyError:
            return

    if block["chainWork"]:
        try:
            print("Chain work is: " + block["chainWork"])
        except KeyError:
            return

    if block["prevHash"]:
        try:
            print("Previous block is: " + block["prevHash"])
        except KeyError:
            return


    if "nextHash" in block:
        try:
            print("Next block is: " + block["nextHash"])
        except KeyError:
            return


    if block["solution"]:
        try:
            print("Solution: " + block["solution"])
        except KeyError:
            return

    if block["transactions"]:
        try:
            print("Number of transactions: " + str(block["transactions"]))
        except KeyError:
            return


    turl = "https://api.zcha.in/v2/mainnet/blocks/" + blockhash + "/transactions?limit=10&offset=0&sort=index&direction=ascending"
    tx = json.loads(requests.get(turl).text)
    print("Transactions: ")
    for i in range(len(tx)):
        if tx[i]["hash"]:
            try:
                print(tx[i]["hash"])
            except KeyError:
                return



def real_time_zcash():
    url = "https://api.zcha.in/v2/mainnet/network"
    real = json.loads(requests.get(url).text)
    print("The real time information of Zcash: ")
    
    if real["accounts"]:
        try:
            print("Count of unique seen accounts (addresses): " + str(real["accounts"]))
        except KeyError:
            return

    if real["blockHash"]:
        try:
            print("Current block (chain head) hash: " + real["blockHash"])
        except KeyError:
            return

    if real["hashrate"]:
        try:
            print("Current estimated network hashrate over the past 120 blocks: " + str(real["hashrate"]))
        except KeyError:
            return

    if real["meanBlockTime"]:
        try:
            print("Mean block time over the past 120 blocks (seconds): " + str(real["meanBlockTime"]))
        except KeyError:
            return

    if real["relayFee"]:
        try:
            print("Current transaction relay fee: " + str(real["relayFee"]))
        except KeyError:
            return

    if real["peerCount"]:
        try:
            print("Count of connected peers: " + str(real["peerCount"]))
        except KeyError:
            return

    if real["totalAmount"]:
        try:
            print("Total amount of ZEC in circulation: " + str(real["totalAmount"]))
        except KeyError:
            return

    if real["transactions"]:
        try:
            print("All-time transaction count: " + str(real["transactions"]))
        except KeyError:
            return


def tx_addr_zcash(tx):
    url = "https://api.zcha.in/v2/mainnet/transactions/"
    transaction = json.loads(requests.get(url + tx).text)
    print("Transaction "+ tx + " has following information: ")

    if transaction["index"]:
        try:
            print("Index: " + str(transaction["index"]))
        except KeyError:
            return


    if transaction["version"]:
        try:
            print("Version: " + str(transaction["version"]))
        except KeyError:
            return

    if transaction["blockHeight"]:
        try:
            print("Inculded in Block: " + str(transaction["blockHeight"]))
        except KeyError:
            return


    if transaction["blockHash"]:
        try:
            print("Block Hash: " + transaction["blockHash"])
        except KeyError:
            return

    if transaction["timestamp"]:
        try:
            print("Timestamp: " + str(transaction["timestamp"]))
        except KeyError:
            return


    if transaction["time"]:
        try:
            print("Time: " + str(transaction["time"]))
        except KeyError:
            return


    if transaction["vin"]:
        try:
            if(transaction["vin"][0]["retrievedVout"]["scriptPubKey"]["addresses"] == None):
                print("Inputs: Newly Generated Coins")
            else:
                print("Inputs: " + str(transaction["vin"][0]["retrievedVout"]["scriptPubKey"]["addresses"]))
        except KeyError:
            return


    if transaction["vout"]:
        try:
            for i in range(len(transaction["vout"])):
                print("Outputs: " + str(transaction["vout"][i]["scriptPubKey"]["addresses"]))
        except KeyError:
            return


def addr_zcash(addr):
    url = "https://api.zcha.in/v2/mainnet/accounts/"
    address =  json.loads(requests.get(url + addr).text)
    print("Account "+ addr + " has following information: ")

    if address["balance"]:
        try:
            print("Transparent Balance: " + str(address["balance"]) + " ZEC")
        except KeyError:
            return

    if address["firstSeen"]:
        try:
            print("First seen: " + str(address["firstSeen"]))
        except KeyError:
            return

    if address["lastSeen"]:
        try:
            print("Last seen: " + str(address["lastSeen"]))
        except KeyError:
            return

    if address["minedCount"]:
        try:
            print("Blocks mined: " + str(address["minedCount"]))
        except KeyError:
            return

    if address["sentCount"] or address["sentCount"] == 0:
        try:
            print("Txns sent: " + str(address["sentCount"]))
        except KeyError:
            return

    if address["recvCount"] or address["recvCount"] == 0:
        try:
            print("Txns Received: " + str(address["recvCount"]))
        except KeyError:
            return

    if address["totalSent"] or address["totalSent"] == 0:
        try:
            print("Total sent: " + str(address["totalSent"] ) + " ZEC")
        except KeyError:
            return

    if address["totalRecv"] or address["totalRecv"] == 0:
        try:
            print("Total Received: " + str(address["totalRecv"]) + " ZEC")
        except KeyError:
            return






#addr_zcash("t3M4jN7hYE2e27yLsuQPPjuVek81WV3VbBj")
#tx_addr_zcash("209549a5b8b673806cc31e1bf4b6c597c80670b1322cc81fa42be970f41fa770")
#real_time_zcash()
#block_lookup_zcash("000000000afb9d14dee1e64ce481c2b2c20ccece41724d0dc35912f1922ee2c7")
#block_lookup("0000000000000bae09a7a393a8acded75aa67e46cb81f7acaa5ad94f9eacd103")
#tx_addr("60a44c4da9e63632a970a44adbf50f930b1114530d0af829fc7e26eee78189d8")
