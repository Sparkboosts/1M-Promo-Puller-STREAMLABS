import os
import requests
from colorama import Fore
import json
import threading
from datetime import datetime
from logg import CustomLogger
lock = threading.Lock()
Log = CustomLogger()


def linkpromo(promo):
    inputTokens = "data/discord.txt"
    outputFolder = "Output"
    outputTokens = os.path.join(outputFolder, "tokens.txt")
    outputPromos = os.path.join(outputFolder, "promos.txt")
    outputCombined = os.path.join(outputFolder, "combined.txt")
    outputUsedPromos = os.path.join(outputFolder, "usedpromos.txt")
    Failedtokens = os.path.join(outputFolder, "failed.txt")

    def shorten_token(token, length=50):
        if len(token) > length:
            return token[:length] + "...."
        return token
    
    def fileExithm(file_path):
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            open(file_path, 'w').close()

    def loadLines(file_path):
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                return [line.strip() for line in file.readlines() if line.strip()]
        return []

    def update_file(file_path, lines):
        with open(file_path, 'w') as file:
            file.writelines(line + '\n' for line in lines)

    def writeFile(file_path, content):
        fileExithm(file_path)
        with open(file_path, 'a') as file:
            file.write(content + '\n')


    fileExithm(outputTokens)
    fileExithm(outputPromos)
    fileExithm(outputCombined)
    fileExithm(outputUsedPromos)
    fileExithm(Failedtokens)

    while True:
        with lock:
            tokens = loadLines(inputTokens)
            if not tokens:
                Log.error("No tokens available.")
                return
            token_line = tokens.pop(0)
            update_file(inputTokens, tokens)

        token = token_line.split(":")[-1]

        try:
            promo_id, promo_jwt = promo.split('/')[5:7]
            promo_url = f"https://discord.com/api/v9/entitlements/partner-promotions/{promo_id}"
            headers = {
                "authorization": token,
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.9',
                'content-type': 'application/json',
                'origin': 'https://discord.com',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            }

            response = requests.post(promo_url, headers=headers, json={"jwt": promo_jwt})

            if response.status_code == 200:
                promo_data = response.json()
                promo_redemption_id = promo_data.get("code")

                if promo_redemption_id:
                    Log.linked(f"Successfully Linked Token | {Fore.BLACK}token : {Fore.RESET} {shorten_token(token)} | {Fore.BLACK}promo: {Fore.RESET} {promo_redemption_id}")
                    writeFile(outputPromos, f"https://promos.discord.gg/{promo_redemption_id}")
                    writeFile(outputTokens, token_line)
                    writeFile(outputCombined, f"{token_line}|https://promos.discord.gg/{promo_redemption_id}")
                    writeFile(outputUsedPromos, promo)
                    break  # Exit the loop after successful redemption
            else:
                # Check if the error indicates that the promo has already been redeemed
                if "already redeemed" in response.text.lower() or "405: Method Not Allowed" in response.text:
                    Log.error(f"Promo already redeemed with token: {shorten_token(token)}. Moving to next token.")
                    writeFile(Failedtokens, token_line)  # Add the token to failed.txt
                else:
                    Log.error(f"Failed to retrieve promo with token: {shorten_token(token)}. Error: {response.text}")
                    writeFile(Failedtokens, token_line)  # Add the token to failed.txt

        except Exception as e:
            Log.error(f"An error occurred with token: {shorten_token(token)}. Error: {e}")