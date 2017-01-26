from __future__ import print_function
from ripe.atlas.cousteau import ProbeRequest
from ripe.atlas.cousteau import Probe
import ipaddress
from datetime import datetime
import traceback
import configparser
import MySQLdb as pymysql
from operator import itemgetter
from contextlib import closing
import random
import time
import sys
from math import radians, cos, sin, asin, sqrt
from ripe.atlas.cousteau import (
  Ping,
  Traceroute,
  AtlasSource,
  AtlasCreateRequest
)

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6367 * c
    return km

def getCountry(ip):
    countrySet = set()
    try:
        ctry=maxmind.city(ip).country.iso_code
        if ctry != "None":
            countrySet.add(ret)
        return countrySet
    except:
        return set()

def selectProbes(prList):
    retIDList=[]
    distances=[]
    if len(prList) ==1:
        id,lat,lon=prList[0]
        retIDList.append(id)
    else:
        for iter in range(0,len(prList)-1):
            id,lat,lon=prList[iter]
            for iter2 in range(iter+1,len(prList)):
                id2,lat2,lon2=prList[iter2]
                dist=haversine(lon,lat,lon2,lat2)
                distances.append([id,id2,dist])
            #retIDList.append(id)
        sortedDistances=sorted(distances, key=itemgetter(2),reverse=True)
        ID1,ID2,dist=sortedDistances[0]#Top one
        retIDList=[ID1,ID2]
    return retIDList

def runTraceroute(target,country,asn):
    global noProbesASes
    msms=[]
    probeList=[]
    probesids=""
    prolen=0
    filters = {"country_code": country,"asn_v4":asn}
    print(filters)
    probes = ProbeRequest(**filters)
    for pb in probes:
        probe = Probe(id=pb["id"])
        lon=float(probe.geometry['coordinates'][0])
        lat=float(probe.geometry['coordinates'][1])
        print(pb["country_code"],country,pb["id"],pb["asn_v4"],lat,lon)
        if pb["country_code"] != country:
            print('Country filter didnt match: ',pb['id'],pb['country_code'],country)
            continue
        try:
            ip=str(ipaddress.IPv4Address(probe.address_v4))
        except:
            continue

        probeList.append([pb["id"],lat,lon])
    if len(probeList)==0:
        print('No probes found.')
        return msms

    selectedProbes=selectProbes(probeList)

    for prbid in selectedProbes:
        prolen+=1
        probesids=probesids+str(prbid)+","

    #print(probesids)

    if prolen==0:
        print('No probes found: '+str(prolen))
        return msms

    try:
        probesids=probesids[:-1]

        measurement=None
        #print(probesids)

        if typeRun=="traceroute":
            traceroute = Traceroute(
                        af=4,
                        target=target,
                        description="Traceroute "+str(target),
                        protocol="ICMP",
                    )
            measurement=traceroute
        elif typeRun=="ping":
            ping = Ping(af=4, target=target, description="Ping "+str(target))
            measurement=ping
        else:
            print('Need correct type of measurement specified.')
            exit(1)

        source = AtlasSource(type="probes", value=probesids,requested=prolen)
        atlas_request = AtlasCreateRequest(
                    start_time=datetime.utcnow(),
                    key=API_KEY_CREATE_UDM,
                    measurements=[measurement],
                    sources=[source],
                    is_oneoff=True
                    )
        try:
            (is_success, response) = atlas_request.create()
        except:
            traceback.print_exc()
        if is_success:
            msms=response['measurements']
        else:
            print(response)

    except:
        traceback.print_exc()
        print("ERROR in traceroute.")

    return msms

if __name__ == "__main__":

    if sys.version_info < (2, 7):
        print("ERROR: RIPE only support python2.7. Please use python2.7")
        exit(0)

    configFile = 'conf/ripe.conf'
    config = configparser.ConfigParser()
    config.read(configFile)
    config.sections()

    counter = 0
    noProbesASes = []
    try:
        dbname = config['MySQL']['dbname']
        serverIP = config['MySQL']['serverIP']
        serverPort = int(config['MySQL']['serverPort'])
        user = config['MySQL']['user']
        password = config['MySQL']['password']

        API_KEY_CREATE_UDM = config['DEFAULT']['API_KEY_CREATE_UDM']
        API_KEY_DOWNLOAD_UDM = config['DEFAULT']['API_KEY_DOWNLOAD_UDM']
        typeRun = config['DEFAULT']['typeRun']
        outFile = config['DEFAULT']['outFile']

    except:
        traceback.print_exc()


    allmsms=[]
    #Get all detoured prefixes
    db = pymysql.connect(host=serverIP,
                         port=serverPort,
                     user=user,
                     passwd=password,
                     db=dbname)
    prefixToTraceroute={}
    with closing( db.cursor() ) as cur:
        try:
            cur.execute('select are.prefix,are.as_path,u.detour_return_countries from AbnormalRibEntries are join v_all_def_paths u on are.as_path=u.as_path group by are.prefix,are.as_path,u.detour_return_countries')
            row=cur.fetchone()
            while row is not None:
                prefix=row[0]
                peerAS=row[1].split(' ')[0]
                country=row[2]
                prefixToTraceroute[prefix]=peerAS+'|'+country
                row=cur.fetchone()
        except Exception:
            raise Exception('Select Query Failed')
    db.close()

    #print(prefixToTraceroute)
    with closing(open(outFile,'w+')) as fp:
        print('prefix peerAS country ip msm',file=fp)
    try:
        prfs =  prefixToTraceroute.keys()
        random.shuffle(prfs)
        #for prefix,vals in prefixToTraceroute.items():
        for prefix in prfs:
            vals=prefixToTraceroute[prefix]
            network = ipaddress.IPv4Network(unicode(prefix))
            (peerAS,countryset)=vals.split('|')
            if peerAS in noProbesASes:
                continue
            country=None
            for ct in eval(countryset.replace('\'{','{').replace('}\'','}')):
                country=ct

            allNets = [network] if network.prefixlen >= 24 else network.subnets(new_prefix=24)
            for net in allNets:
                if peerAS in noProbesASes:
                    continue
                normalizeabnormalRibEntriesIn=[]
                randomHost=None
                allHosts = list(net.hosts())
                if(net.prefixlen==32):
                    allHosts.append(net.network_address)
                randomHost=str(random.choice(allHosts))

                if not randomHost:
                    continue

                msm=runTraceroute(randomHost,country,peerAS)

                if len(msm)==0:
                    noProbesASes.append(peerAS)

                else:
                    for ms in msm:
                        with closing(open(outFile,'a+')) as fp:
                            print(prefix,peerAS,randomHost,country,ms)
                            print(prefix,peerAS,randomHost,country,ms,file=fp)
                            counter+=1

                if counter == 90:
                    print('Sleeping...')
                    time.sleep(9*60)
                    counter=0

    except:
        traceback.print_exc()