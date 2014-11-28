#! /usr/bin/env bash

me=`basename $0`
pidfile=/var/run/$me.pid

mycode()
{
        touch $pidfile
        echo $$ > $pidfile
        sleep 10
}

myexit()
{
        rm -f $pidfile
        exit 0
}

trap 'myexit'  2

if test -e $pidfile
then
        kill -0 `cat $pidfile` >/dev/null 2>&1
        if [ $? -eq 0 ]; then
                echo "Another instance is running , `cat $pidfile`"
                exit 1
        else
                rm -f $pidfile
                mycode
        fi
else
        mycode
fi

myexit
