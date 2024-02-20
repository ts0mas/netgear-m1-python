# netgear-m1-python
Inspired by  https://github.com/mtreinik/netgear-m1


usage: python main.py [-h] [-i IP] [-p PASSWORD] [-o OUTPUT] command

Python script to control netgear m1 router

positional arguments:
  command               
                        status     Output router status. Default is brief human readable output.
                        ping       Ping router until it is available.
                        reboot     Reboot router.
                        connect    Turn cellular data connection on.
                        disconnect Turn cellular data connection off.
                        reconnect  Turn cellular data connection off and on again.
                                

options:
  -h, --help            show this help message and exit
  -i IP, --ip IP        m1 ip address, defauilt to env variable NETGEAR_M1_IP, defaulted to 192.168.1.1
  -p PASSWORD, --password PASSWORD
                        m1 password, default to env varible NETGEAR_M1_PASSWORD, defaulted to admin
  -o OUTPUT, --output OUTPUT
                        Status output, can be all,json or few default to few

