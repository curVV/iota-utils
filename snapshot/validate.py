#!/usr/bin/env python

# Snapshot validation
# Was ported from js here: https://github.com/domschiener/iota-snapshot-validation


from __future__ import print_function, unicode_literals

try:
    from urllib.request import urlopen, Request
    from urllib.error import URLError
except ImportError:
    from urllib2 import urlopen, Request, URLError

import sys, json, time, math



iota_node_url = 'http://localhost:14281'



class ConnectError(Exception):
    pass



def request(options):
    connect_retries = 3
    headers = options["headers"]
    if options["method"] == "POST":
        data = options["json"].encode('utf-8')
    else:
        data = None
    request = Request(url=iota_node_url, data=data, headers=headers)

    for c in range(1,connect_retries+1):
        try:
            data = urlopen(request).read()
            break
        except URLError as e:
            print("Failed connecting to node {}. {}".format(iota_node_url, str(e)))
            if c == connect_retries:
                raise ConnectError("Could not establish connection to node {}".format(iota_node_url))
            else:
                print("retry ({}/{})...".format(c, connect_retries))
                time.sleep(3)
                continue
    return data


def add_manual_claims(snapshot, callback):

    print("ADDING MANUAL CLAIMS NOW")

    manual_claims_list = {
        'JFKECWKBTQIIBRRZFGUMEROJSSDKLCK9E9CJ9OHQIKKWRYLAZIELNQVHBADXRRNQGSXGESADYMXRANV9K' : '4302318738691',
        'TWJEAUEYTME9VCCFHNKKIJUKVDVMVHCXCYVJSQVGPMKURYZVJEXZHMOZKAP9RLF9ULN9OODUIZV9ZMBQR' : '333543720000',
        'BQTVMZFGUABNTZ9HLUAYWKOFVMFPFO9GAGPDUYXDXIRSNEYVBGHLTFHFHPIZXYWVQZJKKO9ZHYAQUEPOE' : '239017429752',
        'WYVVWUE9RVXJTDBVXRFKYOFMXNUDNSHGTNLKSVVDFAYRCMXOPCRLXANUYMXF9THCVKPDTUXS9HUIQXA9D' : '38913434000',
        'KFQFBYDCXKMEUPAVSFTNKBYSD9CZVQKI9ZQERAPARLRFQOEM9GCSVSGYMCFNSOKGBUGDMLOSHIKFZBUII' : '12166529484609',
        'GIOGHJSBRSNITUS9DWSSQRDJKLEIMNOHQBAWTOKJKMHCE9EVXB9AKYYQRTBOSJGYDKHAHJQKLBQUDF9MB' : '1085972906988',
        'ZZXXCFMPSLMJPNFZZXWICLAYEDHHIAEIJMMTMZLESWHBOAUMCMJL9MFKGPEMMGBOMYSQKGOZII9BFRKHX' : '4780354154102',
        'UQ9YHOITIZTSVSVEHGYQLVLTLBFLWBM9CQDCRIEVOMFX9SOGSGVQS9LMYUXPCIFIMFR9CIWEGXYKGUHFX' : '2366275306280',
        'YYVOIYDHRMYWHTCIDVLNWEESKQKHKPPPZIQHKULUC9ZCHXFKYCI9JDQH9DBRKLEEGRYNL9LYMPKPSTAJD' : '4541336446396',
        'FIEE9MMWGAHWFMGVOLQOSIEMIWEEXUMWZJ9ERQB9AUFFSUTJSATLQXO9BCSFQLVLAXAPEVEEBUCVUFLQX' : '2222864681657',
        'IXHNYAWKPYTSEECDNONMFAMFXMMDXRMEZHGZKYPAQROAHAXIPKTFUXMXRRESAH9AATWYXTXZMEZFKALAZ' : '1023951425090',
        'OCWLWWSDFRJYNQKLFZDAKRTFDZMTYFWZPKOUETWWYKSXFMZMRLRBHMPQFKEXPJSAQGHUMZPLNBKVUTYAF' : '38913434000',
        'ZHFHYNEGUPYVJRTHRSFITNCYYEKLWAHGPMW9VYASNOKZYJLXCUQUTQGODKLGSGNBJLIFWZFLZYZDYRVBD' : '107557843388',
        'RDZXVRWQBICNM9VVNPERMSGTBFIKGEHRYPHVZNGNTSZVSLKNYZBBSYPKLAMYVQGICKJIWVTGMJVMGPSVU' : '207635968856', 
        'XYQVEKSSCDKZPXPYIUYF9YAJGKNBXSJUQEONPMCLGWKEPOKAC9JYDVPTZADWRMSCKWEGSYNJUEGKFGTYI': '28351208889433'
    }

    added_to_snapshot = 0

    # This address is owned by the Foundation and is being used to subtract the funds from
    address_to_subtract = 'PPLNDRIWPOJZNKEGGPUNFVBEBENBBTQSXKXNOGKNVQBLQNHULLMFRT9RKHOAUCD9JAQNTRFHKEITPVJDC'

    for key in manual_claims_list:

        if manual_claims_list[key]:

            balance = int(manual_claims_list[key])

            # Add claim to snapshot
            # If address already existent, simply increment
            snapshot[key] = snapshot[key] = snapshot[key] + balance if snapshot[key] else balance
            # Subtract claim balance from IOTA Foundation address
            snapshot[address_to_subtract] = snapshot[address_to_subtract] - balance
            # Just for logging purposes
            added_to_snapshot = added_to_snapshot + balance


    print("ADDED MANUAL CLAIMS: ".format(added_to_snapshot))

    return callback(None, snapshot)


def validate_snapshot(latest_state):

    snapshot_url = 'https://gist.githubusercontent.com/domschiener/ac11dd4481f940856f07ecf4f2a6b5b9/raw/8872dd1faae3312e1fc953f5539e5cfefc6cd3a5/Snapshot.json'

    options = {
        "url": snapshot_url,
        "method": 'GET',
        "headers": None
    }

    try:
        snapshot = json.loads(request(options))
    except ConnectError as e:
        sys.exit(str(e))

    num_entries = len(snapshot)

    print("VALIDATING SNAPSHOT ENTRIES: ", num_entries)

    # We now compare the snapshot to the latest state
    for entry in snapshot:
        address = entry["address"]
        balance = entry["balance"]

        same_balance = int(latest_state[address]) == int(balance)

        if not same_balance:
            print("FATAL ERROR: Balance incorrect for: ", address)
            print("Balance (proposed snapshot vs. local): {} {}".format(balance, int(latest_state[address])))
        

        # now we remove the address from the latestState
        latest_state[address] = None

    print("LATEST STATE EQUALS SNAPSHOT: ", str(len(latest_state) == 0) and latest_state["constructor"] == dict())

    #console.log("LATEST STATE EQUALS SNAPSHOT: ", Object.keys(latestState).length === 0 && latestState.constructor === Object)


def process_request(e, updated_state):

    null_hash = '999999999999999999999999999999999999999999999999999999999999999999999999999999999'

    null_hash_balance = updated_state[null_hash]
    # empty null_hash
    updated_state[null_hash] = None

    # address controlled by the IOTA Foundation
    foundation_address = 'MCQVDPXBCCANXCFYAYWOZNYKDBTFPSUGPTOFYEMPYVOCKOTDIJLUBBUSQIEHTYUIEORPMIS9ZDXQDSJDR'

    # Send nullHashBalance to the IOTA Foundation Address
    updated_state[foundation_address] = null_hash_balance

    # Case 1
    #
    # 500Gi sent to recipient
    # Reason: Unknowingly sent funds to nullHash. Funds could be easily recovered
    # via other means
    case_1_recipient = 'M9HNETZSOLPXOFSDELYLAD9Y9YVXAWCYMLCORHGDOYYASJZUPCTGZWWSOHKSFRVNNVR9VXFXMREULIYFJ'
    case_1_funds = 500000000000
    updated_state[foundation_address] = updated_state[foundation_address] - case_1_funds
    updated_state[case_1_recipient] = updated_state[case_1_recipient] + case_1_funds if updated_state[case_1_recipient] else case_1_funds

    # Case 2
    #
    # 386697000000 sent to recipient
    # Reason: Sent funds to old address scheme. Funds could be easily recovered
    # via other means
    case_2_recipient = 'YX9PFDCREJKYOOQGKXKGPLKOEXTCOXMWCNAMQDFV9WYU9K9OOWPWD9DNBRFMKSJWYTTOGUVBNJXLQM9HF'
    case_2_old_address = 'ZQQXBSLFRN9EYOKQUKQ9RGIEFQACIEKUMLTEFSKH9NGSH9VIVJTBGYTCYSBNCJB9QLIVFCPMMTPJVVHOY'
    case_2_funds = 386697000000
    updated_state[case_2_old_address] = updated_state[case_2_old_address] - case_2_funds
    updated_state[case_2_recipient] = updated_state[case_2_recipient] + case_2_funds if updated_state[case_2_recipient] else case_2_funds

    updated_state[case_2_old_address] = None

    # Case 3
    #
    # 24497000000 sent to recipient
    # Reason: Sent funds to old address scheme. Funds could be easily recovered
    # via other means
    case_3_recipient = 'YQXBRVKJOJXWLMI9BUK9XZTOASUTTMKFYCHTQNJSFWCYKSUMB9AUZLZCPU9WFNUOYCYKEB9EXCIN9SEDW'
    case_3_old_address = 'MITICUBQBYLYOXIMOBVWSTHEDSOD9OIFNAICTOEONKQTZITZEEYCATHDLHBQULWERMXFLJHALGOG9D9RH'
    case_3_funds = 24497000000
    updated_state[case_3_old_address] = updated_state[case_3_old_address] - case_3_funds
    updated_state[case_3_recipient] = updated_state[case_3_recipient] + case_3_funds if updated_state[case_3_recipient] else case_3_funds

    updated_state[case_3_old_address] = None

    # Case 4
    #
    # 138129000000 sent to recipient
    # Reason: Sent funds to old address scheme. Funds could be easily recovered
    # via other means
    case_3_recipient = 'WP9QVUIREAXFUQH9LNQDCXDJIMWMSDUMJHAHMGCPCFLVKLHGXEIDKKCKDYQH9TXLQUEZVITSTMSMPDWUV'
    case_3_old_address = 'HYDMUQPRGGTCSVSGPDCFEZQXKHMZSKIOTJLNOSYKJCRSVMYTVEEF9YTG9LZHUJGJJRUUSPTVFNAPZOMDR'
    case_3_funds = 138129000000
    updated_state[case_3_old_address] = updated_state[case_3_old_address] - case_3_funds
    updated_state[case_3_recipient] = updated_state[case_3_recipient] + case_3_funds if updated_state[case_3_recipient] else case_3_funds

    updated_state[case_3_old_address] = None

    # as a final step, compare the two
    validate_snapshot(updated_state)



def snapshot():

    global iota_node_url

    command = json.dumps({ "command": "Snapshot.getState" })

    options = {
        "url": iota_node_url,
        "method": 'POST',
        "headers": {
            'Content-Type': 'application/json',
            'Content-Length': len(bytearray(command, 'utf-8'))
        },
        "json": command
    }

    try:
        data = request(options)
    except ConnectError as e:
        sys.exit(str(e))

    latest_state = data["ixi"]["state"]

    # FIRST VALIDATION
    # Check if total sum is equal to the supply 2779530283277761
    total_supply = (math.pow(3,33) - 1) / 2
    snapshot_balance = 0


    for key in latest_state:
        try:
            snapshot_balance = snapshot_balance + int(latest_state[key])
        except (AttributeError, IndexError):
            continue


    print("BALANCE CORRECT: ", str(snapshot_balance == total_supply))


    # Add manual claims to snapshot
    add_manual_claims(latest_state, process_request)



if __name__ == '__main__':
    snapshot()
