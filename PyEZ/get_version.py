from lxml import etree
from ncclient import manager
from getpass import getpass

def connect(host, user, password):
    conn = manager.connect(host=host,
            port=22,
            username=user,
            password=password,
            timeout=10,
            device_params = {'name':'junos'},
            hostkey_verify=False)

def main():
    host = ''
    username = ''
    password = ''
    connect(host, username, password)

    print 'show version'
    print '*' * 30
    result = conn.command('show version', format='text')
    print result.xpath('output')[0].text

if __name__ == '__main__':
    main()
