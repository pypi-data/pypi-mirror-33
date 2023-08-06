#!/bin/bash
#install python

hash apt 2>/dev/null
if [ $? -eq 0 ];then
    echo "apt is existed install apt-lib"
    apt-get install -y libc6-dev gcc
    apt-get install -y make build-essential libssl-dev zlib1g-dev libreadline-dev libsqlite3-dev wget curl llvm
else
    hash yum 2>/dev/null
    if [ $? -eq 0 ];then
        echo "yum is existed install yum-lib"
        yum -y install wget gcc make epel-release
        yum update -y
        yum -y install  net-tools
        yum -y install zlib1g-dev bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel
    fi
fi


hash python3 2>/dev/null
    if  [ $? -eq 0 ];then
    res=$(python3 -V 2>&1 | awk '{print $1}')
    version=$(python3 -V 2>&1 | awk '{print $2}')
    #echo "check command(python) available resutls are: $res"
    if [ "$res" == "Python" ];then
        if   [ "${version:0:3}" == "3.6" ];then
            echo "Command python3 could be used already."
                 hash pip3 2>/dev/null;
                 if [ $? -eq  0 ];then
                    pip3 install -U git+https://github.com/shadowsocks/shadowsocks.git@master
                    pip3 install x-mroy-1045
                    pip3 install x-mroy-1046
                    pip3 install x-mroy-1047
                    pip3 install x-mroy-1048
                    echo "BuildFlag" >> /etc/ibuild
                    cat << EOF >> /etc/shadowsocks.json
{
    "server":"0.0.0.0",
    "port_password": {
        "13001": "thefoolish1",
        "13002": "thefoolish2",
        "13003": "thefoolish3",
        "13004": "thefoolish4",
        "13005": "thefoolish5",
        "13006": "thefoolish6",
        "13007": "thefoolish7",
        "13008": "thefoolish8",
        "13009": "thefoolish9",
        "13010": "thefoolish10",
        "13011": "thefoolish11",
        "13012": "thefoolish12",
        "13013": "thefoolish13"
    },
    "workers": 15,
    "method":"aes-256-cfb"
}
EOF
                    ssserver -c /etc/shadowsocks.json -d start
                    x-relay start
                    exit 0
                 else
                    apt install -y python3-pip python3-setuptools
                    pip3 install -U git+https://github.com/shadowsocks/shadowsocks.git@master
                    pip3 install x-mroy-1045
                    pip3 install x-mroy-1046
                    pip3 install x-mroy-1047
                    pip3 install x-mroy-1048
                    echo "BuildFlag" >> /etc/ibuild
                    cat << EOF >> /etc/shadowsocks.json
{
    "server":"0.0.0.0",
    "port_password": {
        "13001": "thefoolish1",
        "13002": "thefoolish2",
        "13003": "thefoolish3",
        "13004": "thefoolish4",
        "13005": "thefoolish5",
        "13006": "thefoolish6",
        "13007": "thefoolish7",
        "13008": "thefoolish8",
        "13009": "thefoolish9",
        "13010": "thefoolish10",
        "13011": "thefoolish11",
        "13012": "thefoolish12",
        "13013": "thefoolish13"
    },
    "workers": 15,
    "method":"aes-256-cfb"
}
EOF
                    ssserver -c /etc/shadowsocks.json -d start
                    x-relay start
                    exit 0
                 fi
        fi
    fi
fi

echo "command python can't be used.start installing python3.6."
cd /tmp
    if [ -f /tmp/Python-3.6.1.tgz ];then
      rm /tmp/Python-3.6.1.tgz;
    fi
wget https://www.python.org/ftp/python/3.6.1/Python-3.6.1.tgz
tar -zxvf Python-3.6.1.tgz
cd Python-3.6.1
mkdir /usr/local/python3
./configure --prefix=/usr/local/python3
make
make install
if [ -f /usr/bin/python3 ];then
   rm /usr/bin/python3;
   rm /usr/bin/pip3;
fi

if [ -f /usr/bin/lsb_release ];then
  rm /usr/bin/lsb_release;
fi

ln -s /usr/local/python3/bin/python3 /usr/bin/python3
ln -s /usr/local/python3/bin/pip3 /usr/bin/pip3

echo 'export PATH="$PATH:/usr/local/python3/bin"' >> ~/.bashrc

pip3 install -U git+https://github.com/shadowsocks/shadowsocks.git@master
pip3 install x-mroy-1045
pip3 install x-mroy-1046
pip3 install x-mroy-1047
pip3 install x-mroy-1048

echo "BuildFlag" >> /etc/ibuild
cat << EOF >> /etc/shadowsocks.json
{
    "server":"0.0.0.0",
    "port_password": {
        "13001": "thefoolish1",
        "13002": "thefoolish2",
        "13003": "thefoolish3",
        "13004": "thefoolish4",
        "13005": "thefoolish5",
        "13006": "thefoolish6",
        "13007": "thefoolish7",
        "13008": "thefoolish8",
        "13009": "thefoolish9",
        "13010": "thefoolish10",
        "13011": "thefoolish11",
        "13012": "thefoolish12",
        "13013": "thefoolish13"
    },
    "workers": 15,
    "method":"aes-256-cfb"
}
EOF

ssserver -c /etc/shadowsocks.json -d start
x-relay start