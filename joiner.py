import requests
import random
import string
import websocket
import base64
import os
from colorama import Fore, Style, init
import threading

init(autoreset=True)

def gen_name(length=6):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def gen_ws_key():
    key = base64.b64encode(os.urandom(16)).decode('utf-8')
    return key

def get_random_proxy():
    with open('proxies.txt', 'r') as file:
        proxies = file.readlines()
    return random.choice(proxies).strip()

def send_reqs(code, resend_times, use_proxies):
    url_info = "https://www.gimkit.com/api/matchmaker/find-info-from-code"
    url_join = "https://www.gimkit.com/api/matchmaker/join"

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
        "Content-Length": "17",
        "Content-Type": "application/json",
        "Cookie": "_ga=GA1.1.1846579521.1727362656; _ga_32KJCRTBF3=GS1.1.1727362656.1.0.1727362656.0.0.0",
        "Host": "www.gimkit.com",
        "Origin": "https://www.gimkit.com",
        "Referer": "https://www.gimkit.com/join",
        "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
    }

    for _ in range(resend_times):
        proxies = None
        if use_proxies:
            proxy = get_random_proxy()
            proxies = {
                "http": proxy,
                "https": proxy
            }

        payload_info = {
            "code": code
        }

        response_info = requests.post(url_info, headers=headers, json=payload_info, proxies=proxies)

        if response_info.status_code == 200:
            response_data = response_info.json()
            room_id = response_data.get("roomId")
            if room_id:
                random_name = gen_name()
                payload_join = {
                    "roomId": room_id,
                    "name": random_name,
                    "clientType": "Gimkit Web"
                }
                response_join = requests.post(url_join, headers=headers, json=payload_join, proxies=proxies)
                
                if response_join.status_code == 200:
                    join_data = response_join.json()
                    server_url = join_data.get("serverUrl")
                    room_id_join = join_data.get("roomId")
                    intent_id = join_data.get("intentId")
                    if server_url and room_id_join and intent_id:
                        final_url = f"{server_url}/matchmake/joinById/{room_id_join}"
                        headers_final = {
                            "Accept": "application/json",
                            "Accept-Encoding": "gzip, deflate, br, zstd",
                            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
                            "Connection": "keep-alive",
                            "Content-Length": "39",
                            "Content-Type": "application/json",
                            "Host": server_url.split("//")[1],
                            "Origin": "https://www.gimkit.com",
                            "Referer": "https://www.gimkit.com/",
                            "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
                            "sec-ch-ua-mobile": "?0",
                            "sec-ch-ua-platform": '"Windows"',
                            "Sec-Fetch-Dest": "empty",
                            "Sec-Fetch-Mode": "cors",
                            "Sec-Fetch-Site": "cross-site",
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
                        }
                        payload_final = {
                            "intentId": intent_id
                        }
                        response_final = requests.post(final_url, headers=headers_final, json=payload_final, proxies=proxies)
                        
                        if response_final.status_code == 200:
                            final_data = response_final.json()
                            room_info = final_data.get("room", {})
                            process_id = room_info.get("processId")
                            room_id_final = room_info.get("roomId")
                            session_id = final_data.get("sessionId")
                            if process_id and room_id_final and session_id:
                                websocket_url = f"wss://{server_url.split('//')[1]}/{process_id}/{room_id_final}?sessionId={session_id}"
                                ws = websocket.WebSocket()
                                ws.connect(websocket_url)
                                print(Fore.GREEN + f"[+]connected ({random_name})")

code = input("Enter the code: ")
resend_times = int(input("How many bots: "))
threads_count = int(input("How many threads: "))
use_proxies = input("Use proxies? (y/n): ").strip().lower() == 'y'

threads = []
for _ in range(threads_count):
    thread = threading.Thread(target=send_reqs, args=(code, resend_times, use_proxies))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()
