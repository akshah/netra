#!/usr/bin/python
import os
import traceback
import subprocess
import json
from pprint import PrettyPrinter


def runTraceroute(ip):
    outDir = "scamperTraces/"
    if not os.path.exists(directory):
        os.makedirs(directory)

    outfileName=outDir+ip+"-paris-traceroute.warts"
    try:
        command="sudo -S scamper -o {0} -O warts -I \'trace -P icmp-paris -q 3 -Q {1}\' < .sudo.auth".format(outfileName,ip)
        os.system(command)
    except:
        traceback.print_exc()
        print("ERROR in traceroute.")
    return outfileName

if __name__ == "__main__":
    #fileName=runTraceroute('104.145.16.23')
    fileName=runTraceroute('64.138.134.0')
    lines = subprocess.check_output(["sc_warts2json", fileName],universal_newlines=True)
    print(len(lines))
    jsonData=json.loads(lines)
    pp=PrettyPrinter()
    pp.pprint(jsonData)