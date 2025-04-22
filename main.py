import os
import sys
import json
import time
import requests
from base64 import urlsafe_b64decode
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)
reset = Style.RESET_ALL
red = Fore.LIGHTRED_EX
blue = Fore.LIGHTBLUE_EX
black = Fore.LIGHTBLACK_EX
green = Fore.LIGHTGREEN_EX
white = Fore.LIGHTWHITE_EX
yellow = Fore.LIGHTYELLOW_EX


def http(ses: requests.Session, url, data=None):
    attemp = 0
    while True:
        try:
            if data is None:
                res = ses.get(url=url)
            elif data == "":
                res = ses.post(url=url)
            else:
                res = ses.post(url=url, data=data)
            if (
                not os.path.exists("http.log")
                or os.path.getsize("http.log") / 1024 > 1024
            ):
                open("http.log", "w").write("")
            open("http.log", "a", encoding="utf-8").write(f"{res.text}\n")
            return res
        except requests.exceptions.ConnectionError:
            print(f"{black}[x] {yellow}connection error !")
            attemp += 1
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectTimeout):
            print(f"{black}[x] {yellow}connection timeout !")
            attemp += 1


def is_expired(token=None):
    if token is None:
        return False
    header, payload, sign = token.split(".")
    deload = urlsafe_b64decode(payload + "==")
    jeload = json.loads(deload)
    now = int(datetime.now().timestamp()) + 60
    if now > jeload.get("exp"):
        return True
    return False

def renew_token(refresh_token):
    url = "https://app-auth.jp.stork-oracle.network/token?grant_type=refresh_token"
    data = {"refresh_token": "-E8Ux7QmAPQdTmOBw_wGrQ"}
    headers = {
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Host": "app-auth.jp.stork-oracle.network",
        "Origin": "chrome-extension://knnliglhgkmlblppdejchidfihjnockl",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    }
    ses = requests.Session()
    ses.headers.update(headers)
    res = http(ses=ses, url=url, data=json.dumps(data))
    access_token = res.json().get("access_token")
    if access_token is None:
        print(f"{black}[x] {red}failed get access token !")
        return None
    print(f"{black}[+] {green}success get access token !")
    return access_token


def validation(access_token):
    headers = {
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Authorization": f"Bearer {access_token}",
        "Connection": "keep-alive",
        "Host": "app-api.jp.stork-oracle.network",
        "Origin": "chrome-extension://knnliglhgkmlblppdejchidfihjnockl",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    }
    ses = requests.Session()
    ses.headers.update(headers)
    price_url = "https://app-api.jp.stork-oracle.network/v1/stork_signed_prices"
    validation_url = (
        "https://app-api.jp.stork-oracle.network/v1/stork_signed_prices/validations"
    )
    me_url = "https://app-api.jp.stork-oracle.network/v1/me"
    while True:
        try:
            if is_expired(access_token):
                print(f"{black}[x] {red}access token expired !")
                return None
            res = http(ses=ses, url=me_url)
            data = res.json().get("data")
            stats = data.get("stats")
            valid_count = stats.get("stork_signed_prices_valid_count")
            invalid_count = stats.get("stork_signed_prices_invalid_count")
            print(
                f"{black}[+] {green}stork valid signed : {white}{valid_count} | {green}stork invalid signed : {white}{invalid_count}"
            )
            res = http(ses=ses, url=price_url)
            data = res.json().get("data")
            key = list(data.keys())[0]
            msg_hash = data.get(key).get("timestamped_signature", {}).get("msg_hash")
            data = {
                "msg_hash": msg_hash,
                "valid": True,
            }
            res = http(ses=ses, url=validation_url, data=json.dumps(data))
            if (
                res.json().get("message") == "validation inserted successfully"
                or res.json().get("message") == "ok"
            ):
                print(f"{black}[+] {green}success insert validation !")
            else:
                print(f"{black}[x] {red}failed insert validation !")
            www = 5 * 60
            countdown(www)
        except KeyboardInterrupt:
            sys.exit()
        except Exception as e:
            print(f"{black}[x] {yellow}error {e}")


def countdown(t):
    for i in range(t, 0, -1):
        print(f"{black}waiting {i} ", flush=True, end="\r")
        time.sleep(1)


def main():
    menu = """
1.) add account
2.) start
0.) exit"""
    bann = """
>
> lazy-stroke
> join @sdsproject_chat
>
"""
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print(bann)
        print(menu)
        choice = input("input number : ")
        print()
        if choice == "1":
            rtoken = input("input refresh token : ")
            atoken = input("input access token : ")
            with open("account.json", "r") as r:
                account = json.loads(r.read())
                account["refresh_token"] = rtoken
                account["access_token"] = atoken
                open("account.json", "w").write(json.dumps(account, indent=4))
                input(f"{black}[x] {blue}press enter to continue !")
                continue

        elif choice == "2":
            with open("account.json", "r") as r:
                account = json.loads(r.read())
            refresh_token = account.get("refresh_token")
            access_token = account.get("access_token")
            status_rtoken = f"{red}not found" if refresh_token is None else f"{green}ok"
            status_atoken = f"{red}not found" if access_token is None else f"{green}ok"
            print(f"{blue}refresh token : {status_rtoken}")
            print(f"{blue}access token : {status_atoken}")
            print()
            if refresh_token is None or access_token is None:
                print(f"{black}[x] {yellow}you haven't added an account yet.{reset}")
                input(f"{black}[x] {blue}press enter to continue !{reset}")
                continue
            while True:
                access_token = renew_token(
                    refresh_token=refresh_token
                )
                if access_token is None:
                    print(f"{black}[x] {red}access token not found in response !")
                    sys.exit()
                result = validation(access_token=access_token)
                if result is None:
                    continue
                break
        elif choice == "0":
            sys.exit()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit()
