import argparse
import logging
import os
import time

import requests

logger = logging.getLogger(__name__)

IP = os.environ.get("NETGEAR_M1_IP", "192.168.1.1")
PASSWORD = os.environ.get("NETGEAR_M1_PASSWORD", "admin")


class Router:
    def __init__(self, ip, password):
        self.url_base = "http://" + ip
        self.url_json = self.url_base + "/api/model.json"
        self.url_session = self.url_base + "/sess_cd_tmp"
        self.url_config = self.url_base + "/Forms/config"
        self.error_json = "/error.json"
        self.ok_json = "/success.json"
        self.error_url = "/index.html?loginfailed"
        self.ok_url = "/index.html"
        self.ip = ip
        self.password = password
        self.s = requests.session()
        self.token = self.get_token()

    def get_infos(self):
        return self.s.get(self.url_json).json()

    def status(self, info="all"):
        few_keys = [
            "deviceName",
            "battChargeLevel",
            "curBand",
            "connection",
            "signalStrength",
        ]
        result = self.get_infos()
        if info == "json":
            return result
        elif info == "few":
            return self.pprint({key: self.get_key(result, key) for key in few_keys})
        elif info == "all":
            return self.pprint(result)

    def pprint(self, result, i=0):
        rep = ""
        for key in result:
            rep += "\t" * i + key + ": "
            if isinstance(result[key], dict):
                rep += "\n" + self.pprint(result[key], i + 1)
            elif isinstance(result[key], list):
                rep += "\n".join(
                    [
                        self.pprint(res, i + 1) if isinstance(res, dict) else str(res)
                        for res in result[key]
                    ]
                )
            else:
                rep += str(result[key]) + "\n"
        return rep

    def get_token(self):
        result = self.get_infos()
        return result["session"]["secToken"]

    def post(self, payload, command=""):
        header = {"Content-Type": "application/x-www-form-urlencoded"}
        payloads = {
            "token": self.token,
        }
        if command == "login":
            payloads.update(
                {
                    "err_redirect": self.error_url,
                    "ok_redirect": self.ok_url,
                }
            )
        else:
            payloads.update(
                {
                    "err_redirect": self.error_json,
                    "ok_redirect": self.ok_json,
                }
            )

        payloads.update(payload)
        result = self.s.post(self.url_config, headers=header, data=payloads)
        if result.url == self.url_base + payloads["ok_redirect"]:
            return True
        else:
            raise ValueError(
                "IP " + self.ip + " or payload not valid:\n" + str(payload)
            )

    def login(self):
        self.post({"session.password": self.password}, command="login")
        logger.info("Login successfull")

    def reboot(self):
        self.post({"general.shutdown": "restart"})
        logger.info("Router rebooting")

    def connect(self):
        self.post({"wwan.autoconnect": "HomeNetwork"})
        logger.info("Router data enabled")

    def disconnect(self):
        self.post({"wwan.autoconnect": "Never"})
        logger.info("Router data disabled")

    def ping(self):
        while True:
            try:
                r = requests.get(self.url_base)
                r.raise_for_status()
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                logger.error("Router down at " + self.ip)
            except requests.exceptions.HTTPError:
                logger.error("Can not connect into router" + str(r.content))
            else:
                logger.info("Router is up")
                return True
            time.sleep(2)

    def get_key(self, result, key):
        for k in result:
            if k == key:
                return result[key]
            elif isinstance(result[k], dict):
                r = self.get_key(result[k], key)
                if r is not None:
                    return r
            elif isinstance(result[k], list):
                for res in result[k]:
                    if isinstance(res, dict):
                        r = self.get_key(res, key)
                        if r is not None:
                            return r


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
    router = Router(args.ip, args.password)
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
