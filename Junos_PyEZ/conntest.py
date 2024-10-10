#!/usr/bin/env python
# Python script to fetch interface name and their operation status

from ncclient import manager


def connect(host, user, password):
    conn = manager.connect(host=host,
            port=22,
            username=user,
            password=password,
            timeout=10,
            device_params = {'name':'junos'},
            hostkey_verify=False)

    rpc = "<get-cfm-iterator-statistics></get-cfm-iterator-statistics>"
    response = conn.rpc(rpc)
    delay = response.xpath('//cfm-entry/cfm-iter-ethdm-entry/cfm-average-twoway-delay')
    jitter = response.xpath('//cfm-entry/cfm-iter-ethdm-entry/cfm-average-twoway-delay-variation')
    for name, status in zip(delay, jitter):
        name = name.text.split('\n')[1]
        status = status.text.split('\n')[1]
        print ("{}-{}".format(name, status))




if __name__ == '__main__':
    connect('10.1.5.222', 'admin', 'admin@123')
