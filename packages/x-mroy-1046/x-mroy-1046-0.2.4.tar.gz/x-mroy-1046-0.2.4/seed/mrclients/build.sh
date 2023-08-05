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

                     exit 0
                 else
                     apt install -y python3-pip python3-setuptools
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
echo "BuildFlag" >> /etc/ibuild 