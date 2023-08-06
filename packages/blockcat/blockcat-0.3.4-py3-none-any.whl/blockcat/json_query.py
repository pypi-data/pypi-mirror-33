import json
import requests

url = "https://blockchain.info/rawtx/"
burl = "https://blockchain.info/rawblock/"

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

#block_lookup("0000000000000bae09a7a393a8acded75aa67e46cb81f7acaa5ad94f9eacd103")
#tx_addr("60a44c4da9e63632a970a44adbf50f930b1114530d0af829fc7e26eee78189d8")
