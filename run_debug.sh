#! /usr/bin/env bash

me=`cat named_socket`
pidfile=$me.pid
outlg=$me.out.log
errlg=$me.err.log

#echo $pidfile

run_fcgi()
{
        touch $pidfile
        
        python manage.py runfcgi --settings=dev-settings daemonize=false socket=`cat named_socket` outlog=$outlg errlog=$errlg&

        echo $! > $pidfile
}

myexit()
{
        rm -f $pidfile
        exit 0
}

case $1 in
    start)
    if test -e $pidfile
    then
            kill -0 `cat $pidfile` >/dev/null 2>&1
            if [ $? -eq 0 ]; then
                    echo "Another instance is running , `cat $pidfile`"
                    exit 1
            else
                    rm -f $pidfile
                    run_fcgi
            fi
    else
            run_fcgi
    fi
    ;;
    stop)
    if test -e $pidfile
    then
            kill -9 `cat $pidfile` >/dev/null 2>&1
            echo "killing `cat $pidfile` ..."
            myexit
    fi
    ;;
    *)
    echo "Usage: `basename $0` {start|stop}" 1>&2
    exit 1
    ;;
esac

exit 0