#!/usr/bin/env python
# Python script to fetch interface name and their operation status
import sys
import xml.etree.ElementTree as ET
from optparse import OptionParser
from ncclient import manager
from ncclient.xml_ import new_ele, sub_ele
from jnpr.junos import Device
from lxml import etree
from collections import defaultdict

#netconf_auth="/usr/lib/python2.7/site-packages/ncclient/ncclient/Python-Pratice/netconf_auth"
netconf_auth="/home/quang/Desktop/JunosPyEZ/netconf_auth"

def buildDMMDictionary(dhost, dusername, dpassword, dport):
    DMMlist = defaultdict(dict)

    with Device(host=dhost, user=dusername, passwd=dpassword, port=dport) as dev:
        config = dev.rpc.get_config(filter_xml=etree.XML('<configuration><protocols></protocols></configuration>'))
        #print(etree.tostring(config, encoding='unicode'))
        iterators = config.xpath('/rpc-reply/configuration/protocols/oam/ethernet/connectivity-fault-management/performance-monitoring/sla-iterator-profiles')
        for i in iterators:
            if i.tag == "sla-iterator-profiles":
                itername = i.xpath('name')[0].text
                itertype = i.xpath('measurement-type')[0].text
                #print(itername,itertype)

        domains = config.xpath('/rpc-reply/configuration/protocols/oam/ethernet/connectivity-fault-management/maintenance-domain')

        for i in domains:
            remotemepid=""
            remotemepiter=""
            mdname=""
            maname=""
            mepid=""
            if i.tag == "maintenance-domain":
                mdname = i.xpath('name')[0].text
                matree = i.xpath('maintenance-association')
                print(mdname)
                for ma in matree:
                    if len(ma.xpath('name')) > 0:
                        maname = ma.xpath('name')[0].text
                        print(maname)
                    meptree = ma.xpath('mep')
                    for mep in meptree:
                        if len(mep.xpath('name')) > 0:
                            mepid = mep.xpath('name')[0].text
                        if len(mep.xpath('remote-mep/name')) > 0:
                            remotemepid = mep.xpath('remote-mep/name')[0].text
                        if len(mep.xpath('remote-mep/sla-iterator-profile/name')) > 0:
                            remotemepiter = mep.xpath('remote-mep/sla-iterator-profile/name')[0].text
                        print(mepid,remotemepid,remotemepiter)
                        DMMlist[mepid].update({"local-mep":mepid})
                        DMMlist[mepid].update({"remote-mep":remotemepid})
                        DMMlist[mepid].update({"md":mdname})
                        DMMlist[mepid].update({"ma":maname})
                        DMMlist[mepid].update({"sla-iterator":remotemepiter})
                        for k in DMMlist:
                            print (k)
                            for v in DMMlist[k]:
                                print (v,':',DMMlist[k][v])

        for dmm, v in list(DMMlist.iteritems()):
            dmmstats = dev.rpc.get_cfm_iterator_statistics(sla_iterator=v['sla-iterator'], maintenance_domain=v['md'], maintenance_association=v['ma'], local_mep=v['local-mep'], remote_mep=v['remote-mep'])
            ET.SubElement(dmmstats, 'sla-iterator').text = dmmstats.get('sla-iterator')
            ET.SubElement(dmmstats, 'md').text = dmmstats.get('md')
            ET.SubElement(dmmstats, 'ma').text = dmmstats.get('ma')
            ET.SubElement(dmmstats, 'local-mep').text = dmmstats.get('local-mep')
            ET.SubElement(dmmstats, 'remote-mep').text = dmmstats.get('remote-mep')
            #ET.dump(dmmstats)
            dmmresult = ET.tostring(dmmstats, encoding='UTF-8')
            DMMTree = ET.fromstring(dmmresult)
            for elem in DMMTree.iter():
                print (elem.text)
                if elem.tag == "cfm-average-twoway-delay": DMMlist[dmm].update({"delay":elem.text})
                if elem.tag == "cfm-average-twoway-delay-variation": DMMlist[dmm].update({"jitter":elem.text})
                if elem.tag == "sfl-measurement-loss-count": DMMlist[dmm].update({"loss":elem.text})
        return DMMlist

def main():
    output_delimeter = "!"
    hostfound = False
    fhostname = sys.argv[1]
    hosts=[]
    with open(netconf_auth,'r') as f:
        read_data = f.read()
        f.closed
    print read_data
    logininfo = read_data.split('\n')
    print logininfo
    for line in logininfo:
        login = line.split(':')
        hosts.append(login)
    for host in hosts:
        if host[0] == fhostname:
            hostfound = True
            fuser=host[1]
            fpass=host[2]
            fport=host[3]
            print(fuser,fpass,fport)

    DMMDict = buildDMMDictionary(sys.argv[1], fuser, fpass, fport)

    if sys.argv[2] == 'index':
        for dmm in DMMDict:
            print dmm

    if sys.argv[2] == 'query' and sys.argv[3] == 'index':
        for dmm in DMMDict:
            print dmm + output_delimeter + DMMDict[dmm].get('local-mep')

    if sys.argv[2] == 'query' and sys.argv[3] == 'delay':
        for dmm in DMMDict:
            print dmm + output_delimeter + DMMDict[dmm].get('delay', "NONE")

    if sys.argv[2] == 'query' and sys.argv[3] == 'jitter':
        for dmm in DMMDict:
            print dmm + output_delimeter + DMMDict[dmm].get('jitter', "NONE")

    if sys.argv[2] == 'query' and sys.argv[3] == 'loss':
        for dmm in DMMDict:
            print dmm + output_delimeter + DMMDict[dmm].get('loss', "NONE")

    if sys.argv[2] == 'query' and sys.argv[3] == 'mepinfo':
        for dmm in DMMDict:
            print dmm + output_delimeter + DMMDict[dmm].get('md') + "_" + DMMDict[dmm].get('ma') + "_" + DMMDict[dmm].get('local-mep') + "_" + DMMDict[dmm].get('remote-mep')

    if sys.argv[2] == 'get' and sys.argv[3] == 'delay':
        index = sys.argv[4]
        if index in DMMDict.keys():
            print DMMDict[index].get('delay')

    if sys.argv[2] == 'get' and sys.argv[3] == 'jitter':
        index = sys.argv[4]
        if index in DMMDict.keys():
            print DMMDict[index].get('jitter')

    if sys.argv[2] == 'get' and sys.argv[3] == 'loss':
        index = sys.argv[4]
        if index in DMMDict.keys():
            print DMMDict[index].get('loss')

if __name__ == "__main__":
    main()
