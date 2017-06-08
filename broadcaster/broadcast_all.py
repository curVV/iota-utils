#!/usr/bin/env python

# Traverse and broadcast

from __future__ import print_function, unicode_literals

try:
    import urllib.request as urllibreq
except ImportError:
    import urllib2 as urllibreq

import sys, json, time, datetime


complete = set(['999999999999999999999999999999999999999999999999999999999999999999999999999999999'])
count = 0
connect_retries = 3
ticker = time.time()
report_interval = 1000


def command(cmd, **args):
    args['command'] = cmd
    return json.dumps(args)


def request(cmdstring):
    url = "http://localhost:14265"
    headers = {'content-type': 'application/json'}
    request = urllibreq.Request(url=url, data=cmdstring.encode('utf-8'), headers=headers)
    for c in range(1,connect_retries+1):
        try:
            data = urllibreq.urlopen(request).read()
            break
        except Exception as e:
            print("Failed connecting to node {}".format(url))
            print("Error: {}".format(str(e.reason)))
            if c == connect_retries:
                sys.exit(1)
            else:
                print("retry ({}/{})...".format(c, connect_retries))
                time.sleep(3)
                continue
    return data


def get_tips():
    print('getting tips...')
    cmd = command('getTips')
    tips = json.loads(request(cmd))
    return tips['hashes']


def get_tip_trytes(tips):
    cmd = command('getTrytes', hashes=tips)
    trytes = json.loads(request(cmd))
    return trytes['trytes']


def get_trunk_and_branch(trytes):
    trunk = trytes[2673-(81*3):2673-(81*2)]
    branch = trytes[2673-(81*2):2673-(81)]
    if trunk == branch:
        return [trunk]
    return [trunk,branch]


def broadcast_tx(trytes):
    time.sleep(0.1)
    cmd = command('broadcastTransactions', trytes=trytes)
    request(cmd)


def traverse(lst):
    global complete
    global count
    global ticker
    current = []
    print("seeing {} tips here...".format(len(lst)))
    print("working...")
    try:
        for tip in lst:
            if tip in complete:
                continue
            trytes = get_tip_trytes([tip])
            for tryte in trytes:
                #if len(tryte) != 2673:
                #    # shouldn't ever happen
                #    continue
                broadcast_tx([tryte])
                count = count + 1
                trunk_and_branch = get_trunk_and_branch(tryte)
                current = current + trunk_and_branch
                if count % report_interval == 0 and count:
                    print("{0} total txs broadcasted, last {1} at {2:.2f}tx/s...".format(count,report_interval,report_interval / (time.time() - ticker)))
                    ticker = time.time()
            complete.add(tip)
    except KeyboardInterrupt:
        print("\nstopping...")
        return
    if not current:
        print("don't see anymore tips...")
        return
    print("going deeper, to next level...")
    print("{} tips processed...".format(len(complete)))
    traverse(current)


def main():
    global count
    start_time = time.time()
    start_human_time = datetime.datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
    print("start time: {}".format(start_human_time))
    traverse(get_tips())
    time_elapsed = time.time()-start_time
    print("")
    print("total transactions broadcasted: {}".format(count))
    print("total time elapsed: {0:.0f} seconds".format(time_elapsed))
    print("average broadcast rate: {0:.2f}tx/s".format(count / time_elapsed))
    print("Done")


if __name__ == '__main__':
    main()
