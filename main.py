import argparse
import logging
import os
import time

from router import M1

logger = logging.getLogger(__name__)

IP = os.environ.get("NETGEAR_M1_IP", "192.168.1.1")
PASSWORD = os.environ.get("NETGEAR_M1_PASSWORD", "admin")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    p = argparse.ArgumentParser(
        description="Python script to control netgear m1 router",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    p.add_argument(
        "-i",
        "--ip",
        type=str,
        default=IP,
        help="m1 ip address, defauilt to env variable NETGEAR_M1_IP, defaulted to 192.168.1.1",
    )
    p.add_argument(
        "-p",
        "--password",
        type=str,
        default=PASSWORD,
        help="m1 password, default to env varible NETGEAR_M1_PASSWORD, defaulted to admin",
    )
    p.add_argument(
        "command",
        default="ping",
        type=str,
        help="""
status     Output router status. Default is brief human readable output.
ping       Ping router until it is available.
reboot     Reboot router.
connect    Turn cellular data connection on.
disconnect Turn cellular data connection off.
reconnect  Turn cellular data connection off and on again.
reboot_script  Turn cellular data connection off and on again.
        """,
    )
    p.add_argument(
        "-o",
        "--output",
        type=str,
        default="few",
        help="Status output, can be all,json or few default to few",
    )

    args = p.parse_args()
    router = M1(args.ip, args.password)
    if args.command == "status":
        print(router.status(info=args.output))
    elif args.command == "ping":
        router.ping()
    else:
        router.login()
        if args.command == "reboot":
            router.reboot()
        elif args.command == "connect":
            router.connect()
        elif args.command == "disconnect":
            router.disconnect()
        elif args.command == "reconnect":
            router.disconnect()
            router.conenct()
        elif args.command == "reboot_script":
            connection = router.get_info("connection")
            while connection == "Connected":
                time.sleep(5)
                connection = router.get_info("connection")
            router.reboot()
