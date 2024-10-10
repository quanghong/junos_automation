import sys
hostfound = False
hostname = sys.argv[1]
hosts=[]
netconf_auth="/home/quang/Desktop/JunosPyEZ/netconf_auth"
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
    if host[0] == hostname:
        hostfound = True
        user=host[1]
        passwd=host[2]
        port=host[3]
        print(user,passwd,port)
