========
Usage
========

*pcrunner* can run as a daemon on Linux, as a service on win32 and has a
command.

*pcrunner*'s has sensible defaults which can be overridden by the configuration
file. Most of the options in the configuration file can be overriden by command
line options.

pcrunner command line arguments and options::

    $ pcrunner --help
    usage: pcrunner [-h] [-c CONFIG_FILE] [-n NSCA_WEB_URL] [-u NSCA_WEB_USERNAME]
                    [-p NSCA_WEB_PASSWORD] [-o COMMAND_FILE] [-H HOSTNAME]
                    [-i INTERVAL] [-m MAX_PROCS] [-e LINES_PER_POST]
                    [-r RESULT_FILE] [-d RESULT_DIR] [-f PID_FILE]
                    [-t HTTP_TIMEOUT] [-s MAX_LINE_SIZE] [-l LOG_FILE] [-a] [-v]
                    [--version]
                    [{start,stop}]

    Passive Command Runner.

    positional arguments:
      {start,stop}          Start or stop pcrunner runloop

    optional arguments:
      -h, --help            show this help message and exit
      -c CONFIG_FILE, --config-file CONFIG_FILE
                            Configuration file
      -n NSCA_WEB_URL, --nsca_web_url NSCA_WEB_URL
                            NSCA server url.
      -u NSCA_WEB_USERNAME, --nsca-web-username NSCA_WEB_USERNAME
                            NSCA Web username.
      -p NSCA_WEB_PASSWORD, --nsca-web-password NSCA_WEB_PASSWORD
                            NSCA Web password.
      -o COMMAND_FILE, --command-file COMMAND_FILE
                            Command file.
      -H HOSTNAME, --hostname HOSTNAME
                            Hostname excpected by Nagios/Icinga.
      -i INTERVAL, --interval INTERVAL
                            Time interval between checks in seconds.
      -m MAX_PROCS, --max-procs MAX_PROCS
                            Max processes to run simultaneously.
      -e LINES_PER_POST, --lines-per-post LINES_PER_POST
                            number of lines per HTTP post
      -r RESULT_FILE, --result-file RESULT_FILE
                            File to where results are written to when NSCA
                            webserver is not reachable.
      -d RESULT_DIR, --result-dir RESULT_DIR
                            Directory for results from external commands.
      -f PID_FILE, --pid-file PID_FILE
                            PID file
      -t HTTP_TIMEOUT, --http-timeout HTTP_TIMEOUT
                            Max secs to timeout when posting results to NSCA
                            webserver
      -s MAX_LINE_SIZE, --max-line-size MAX_LINE_SIZE
                            Maximum result data to post to NSCA webserver in bytes
                            per line.
      -l LOG_FILE, --log-file LOG_FILE
                            log file
      -a, --no-daemon       Run pcrunner in foreground
      -v, --verbose         Show verbose info (level DEBUG).
      --version             Show version


