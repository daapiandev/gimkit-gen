#made with love
import requests
import random
import string
import threading
from colorama import init, Fore

init(autoreset=True)

def gen_str(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))

def load_proxies():
    with open("proxies.txt", "r") as file:
        proxies = [line.strip() for line in file.readlines()]
    return proxies

def send(account_type, use_proxies, proxies):
    url = 'https://www.gimkit.com/api/register'
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Content-Length': '289',
        'Content-Type': 'application/json',
        'Cookie': '',
        'Host': 'www.gimkit.com',
        'Origin': 'https://www.gimkit.com',
        'Referer': 'https://www.gimkit.com/signup',
        'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
    }

    first_name = gen_str(10)
    last_name = gen_str(10)
    email = gen_str(10) + "@outlook.com"
    password = "Daapdev"

    payload = {
        "firstName": first_name,
        "lastName": last_name,
        "email": email,
        "googleToken": "",
        "password": password,
        "accountType": account_type,
        "country": "EN",
        "schoolId": "",
        "districtId": "",
        "areaOfExpertise": "Computer Science" if account_type == "educator" else "",
        "organization": "",
        "gradeLevel": "Middle School" if account_type == "educator" else "",
        "groupJoining": ""
    }

    proxy = None
    if use_proxies and proxies:
        proxy = random.choice(proxies)
        proxies_dict = {
            "http": proxy,
            "https": proxy
        }
    else:
        proxies_dict = None

    response = requests.post(url, headers=headers, json=payload, proxies=proxies_dict)
    response_data = response.json()

    with open("accounts.txt", "a") as cred_file:
        cred_file.write(f"{email}:{password}\n")

    with open("token.txt", "a") as token_file:
        token_file.write(f"{response_data.get('token', 'No token found')}\n")

    print(Fore.GREEN + f"[+] Genned {account_type} account {email}:{password}")

def main():
    account_type = input("Enter account type (educator/student): ").strip().lower()
    if account_type not in ["educator", "student"]:
        print("Invalid account type. Please enter 'educator' or 'student'.")
        return

    use_proxies = input("Use proxies? (y/n): ").strip().lower() == 'y'
    proxies = load_proxies() if use_proxies else None

    num_accounts = int(input("Enter the number of accounts to generate: "))
    num_threads = int(input("Enter the number of threads: "))

    threads = []
    for _ in range(num_accounts):
        thread = threading.Thread(target=send, args=(account_type, use_proxies, proxies))
        threads.append(thread)
        thread.start()

        if len(threads) >= num_threads:
            for thread in threads:
                thread.join()
            threads = []

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
