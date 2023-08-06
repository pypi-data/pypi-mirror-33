#!/bin/bash
#
# pcrunner  Startup script for Passive Check Runner
#
# chkconfig: - 89 11
# description: Passive Check Runner runs passive checks
# processname: pcrunner
# config: /etc/pcrunner/pcrunner.yml
# pidfile: /var/run/pcrunner.pid

# Source function library.
. /etc/rc.d/init.d/functions

# Source a Python virtualenv
#. /<path>/<to>/<virtenv>/bin/activate

RETVAL=0
prog="pcrunner"
exec=/usr/bin/pcrunner
lockfile=/var/lock/subsys/pcrunner

start() {
     echo -n $"Starting $prog: "
     daemon $prog start
     retval=$?
     echo
     [ $retval -eq 0 ] && touch $lockfile
}


stop() {
    echo -n $"Stopping $prog: "
    if [ -n "`pidfileofproc $exec`" ]; then
        killproc $exec
        RETVAL=3
    else
        failure $"Stopping $prog"
    fi
    retval=$?
    echo
    [ $retval -eq 0 ] && rm -f $lockfile
}


case "$1" in
    start)
            start
            ;;
    stop)
            stop
            ;;
    restart)
            stop
            start
            ;;
    status)
            status -p /var/run/pcrunner.pid $prog
            ;;
    *)
            echo "Usage: pcrunner {start|stop|restart|status}"
            exit 1
esac
exit 0
