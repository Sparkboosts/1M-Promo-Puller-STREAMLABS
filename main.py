import curl_cffi.requests
import time
import json
import urllib.parse
import requests
from concurrent.futures import ThreadPoolExecutor
import os
import ctypes
import threading
from logg import CustomLogger
import yaml
import discord
import asyncio 
import sys
import os
import requests
from colorama import Fore
import json
import threading
from datetime import datetime
Log = CustomLogger()
lock = threading.Lock()
import re
from linker import linkpromo
os.system('cls' if os.name == 'nt' else 'clear')
os.system('mode con: cols=120 lines=30')
ctypes.windll.kernel32.SetConsoleTitleW("Streamlabs Nitro Fetcher Made by SparkBoosts")
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)
scrappey = config['scrappey']['api_key']

def remove_line(file, line):
    lines = open(file, "r").read().splitlines()
    with open(file, "w") as f:
        for l in lines:
            if l != line:
                f.write(f"{l}\n")
def mask_promo_url(promo_url):

    parts = promo_url.rsplit('/', 1)
    if len(parts) == 2:

        masked_part = parts[1][:10] + '**********'
        return f"{parts[0]}/{masked_part}"
    return promo_url 
def puller(Cookiex, email, password, Og_sslid, Og_xsrf):
    try:
        Log.info(f"Fetching Now for {email}")

        headers = {
            'Content-Type': 'application/json',
        }

        json_data = {
            'cmd': 'request.get',
            'url': 'https://streamlabs.com/discord/nitro',
            "cloudflareBypass": True,
            'cookies': Cookiex,
        }

        while True:
            try:
                response = requests.post(f'https://publisher.scrappey.com/api/v1?key={scrappey}', 
                                      headers=headers, json=json_data)
                if response.status_code != 200:
                    Log.info(f"Retrying: {str(response.status_code)}")
                    continue
                else:
                    break
            except Exception as e:
                if "curl: (16)" in str(e):
                    Log.error("Curl error 16, retrying...")
                    time.sleep(1)
                    continue
                Log.error(f"Error: {str(e)}")
                time.sleep(1)

        response.raise_for_status()  
        data = response.json()

        try:
            promo = data['solution']['currentUrl']
        except KeyError:
            return puller(Cookiex, email, password, Og_sslid, Og_xsrf)

        if 'https://discord.com/billing/partner-promotions/' not in promo:
            Log.error(f"Failed to fetch promo for [{email}:{password}] - Response: {promo}")
            remove_line("success.txt", f"{email}:{password}:{Og_xsrf}:{Og_sslid}")
            with open("failed_promo.txt", "a") as f:
                f.write(f"{email}:{password}\n")
            return None
        masked_promo = mask_promo_url(promo)
        Log.promo(f"Fetched promo {masked_promo}")
    
        with open("promo_links.txt", "a") as f:
            f.write(f"{promo}\n")
        linkpromo(promo)
        remove_line("success.txt", f"{email}:{password}:{Og_xsrf}:{Og_sslid}")
        time.sleep(3)
        return promo
    except Exception as e:
        Log.error(f"Error: {str(e)}")

        with open("failed_promo.txt", "a") as f:
            f.write(f"{email}:{password}\n")

class Streamlabs:
        def __init__(self, email, password):
            self.email = email
            self.password = password
            self.session = curl_cffi.requests.session.Session(impersonate="chrome")
            self.session.proxies = config['proxy']

        def _login(self):
            url = "https://api-id.streamlabs.com/v1/auth/login"
            payload = {
                "email": self.email,
                "password": self.password
            }
            headers = {
                "host": "api-id.streamlabs.com",
                "connection": "keep-alive",
                "sec-ch-ua-platform": "\"Windows\"",
                "sec-ch-ua": "\"Not(A:Brand\";v=\"24\", \"Google Chrome\";v=\"134\", \"Chromium\";v=\"134\"",
                "sec-ch-ua-mobile": "?0",
                "client-id": "419049641753968640",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
                "accept": "application/json, text/plain, */*",
                "content-type": "application/json",
                "origin": "https://streamlabs.com",
                "sec-fetch-site": "same-site",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "referer": "https://streamlabs.com/",
                "accept-language": "en-US,en;q=0.9",
                "x-xsrf-token": self.XSRF_TOKEN
            }

            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self.session.post(url, json=payload, headers=headers)
                    if response.status_code == 200:
                        Log.success(f"Login Success | email:{self.email} | password:{self.password}")
                        return True

                    if "curl: (16)" in str(response.text):
                        if attempt < max_retries - 1:
                            Log.info("CURL ERR 16.... RETRYING ....")
                            time.sleep(1)
                            continue

                except Exception as e:
                    if "curl: (16)" in str(e) and attempt < max_retries - 1:
                        Log.info("CURL ERR 16.... RETRYING ....")
                        time.sleep(1)
                        continue
                    Log.error(f"Login error: {str(e)}")

            Log.error(f"Login Failed | email:{self.email} | password:{self.password}")
            Log.error(f"response - {response.text}")
            with open("failed.txt", "a") as file:
                file.write(f"{self.email}:{self.password}\n")
            return False

        def _get_default_cookies(self):
            headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'en-GB,en;q=0.9',
                'priority': 'u=0, i',
                'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            }

            response = self.session.get(url='https://streamlabs.com/slid/signup?r=https%3A%2F%2Fstreamlabs.com%2Fdashboard', headers=headers)
            self.XSRF_TOKEN = urllib.parse.unquote(self.session.cookies["XSRF-TOKEN"])
            return self.XSRF_TOKEN

        def _connect(self):
            url = "https://api-id.streamlabs.com/v1/identity/clients/419049641753968640/oauth2"
            payload = {
                "origin": "https://streamlabs.com",
                "intent": "connect",
                "state": "e30="
            }
            headers = {
                "host": "api-id.streamlabs.com",
                "connection": "keep-alive",
                "sec-ch-ua-platform": "\"Windows\"",
                "x-xsrf-token": self.XSRF_TOKEN,
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                "accept": "application/json, text/plain, */*",
                "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
                "content-type": "application/json",
                "sec-ch-ua-mobile": "?0",
                "origin": "https://streamlabs.com",
                "sec-fetch-site": "same-site",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "referer": "https://streamlabs.com/",
                "accept-language": "en-US,en;q=0.9",
            }

            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self.session.post(url, json=payload, headers=headers, allow_redirects=True)
                    redirect_url = response.json()["redirect_url"].replace('\/', '/')
                    break
                except Exception as e:
                    if "curl: (16)" in str(e) and attempt < max_retries - 1:
                        Log.info("Curl error 16, retrying connect...")
                        time.sleep(1)
                        continue
                    Log.error(f"Failed to connect streamlabs account - retry later - {self.email}:{self.password}")
                    with open("retry.txt", "a") as file:
                        file.write(f"{self.email}:{self.password}\n")
                    return False

            headers = {
                "host": "streamlabs.com",
                "connection": "keep-alive",
                "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Windows\"",
                "upgrade-insecure-requests": "1",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "sec-fetch-site": "same-origin",
                "sec-fetch-mode": "navigate",
                "sec-fetch-dest": "document",
                "referer": "https://streamlabs.com/slid/verify-email?email=",
                "accept-language": "en-US,en;q=0.9",
            }

            response = self.session.get(redirect_url, headers=headers, allow_redirects=True)

            if "https://streamlabs.com/slid/authorize" in response.url:
                response = self.session.get(response.url, headers=headers, allow_redirects=True)

            if "https://streamlabs.com/connect" in response.url:
                redirectUrl = response.text.split("var redirectUrl = '")[1].split("'")[0]
                response = self.session.get(url=redirectUrl, headers=headers, allow_redirects=True)

                if "https://streamlabs.com/dashboard" in response.url:
                    csrf_token = response.text.split('name="csrf-token" content="')[1].split('"')[0]

                    with open("success.txt", "a") as file:
                        file.write(f"{self.email}:{self.password}:{urllib.parse.unquote(self.session.cookies.get('XSRF-TOKEN'))}:{urllib.parse.unquote(self.session.cookies.get('slsid'))}\n")
                    return csrf_token
                else:
                    Log.error(f"Failed to connect streamlabs account - retry later - {self.email}:{self.password}")
                    return False
            else:
                Log.error(f"> Failed to connect streamlabs account - retry later - {self.email}:{self.password}")
                return False

        def _start(self):
            try:
                login_status = False
                XSRF_TOKEN = self._get_default_cookies()
                if XSRF_TOKEN:
                    login_status = self._login()
                if login_status:
                    Streamlabs = self._connect()
                remove_line("accounts.txt", f"{self.email}:{self.password}")
            except Exception as e:
                Log.error(f"Failed: {str(e)}")
                with open("failed.txt", "a") as file:
                    file.write(f"{self.email}:{self.password}\n")

if __name__ == "__main__":

            os.system('cls' if os.name == 'nt' else 'clear')

            accounts = open("accounts.txt", "r").read().splitlines()
            threadcount = config['settings']['threads']

            Log.info(f"Loaded {len(accounts)} accounts")
            Log.info(f"Using {threadcount} threads")

            with ThreadPoolExecutor(max_workers=threadcount) as executor:
                for account in accounts:
                    if len(account.split(":")) == 2:
                        email, password = account.split(":")
                    elif len(account.split(":")) == 3:
                        email, password, nil = account.split(":")
                    else:
                        continue
                    executor.submit(Streamlabs(email, password)._start)

            print()

            accounts_fetched = open("success.txt", "r").read().splitlines()

            for account in accounts_fetched:
                while threading.active_count() > 100:
                    continue

                parts = account.split(":")
                if len(parts) != 4:
                    Log.error(f"Invalid account: {account}")
                    continue

                try:
                    email, password, Og_xsrf, Og_sslid = parts
                    threading.Thread(target=puller, args=(
                        "slsid=" + Og_sslid, 
                        email, 
                        password, 
                        Og_sslid, 
                        Og_xsrf
                    )).start()

                except Exception as e:
                    Log.error(f"Error: {str(e)}")
                    continue