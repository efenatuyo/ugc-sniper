try:
  import datetime
  import json
  import os
  import uuid
  import asyncio
  import random
  import requests
  import configparser
  from colorama import Fore, Back, Style
  import httpx
  from fake_useragent import UserAgent
except ModuleNotFoundError:
    print("Modules not installed proberly installing now")
    os.system("pip install requests")
    os.system("pip install httpx")
    os.system("pip install configparser")
    os.system("pip install colorama")
    os.system("pip install fake_useragent")

ua = UserAgent()
config = configparser.ConfigParser()
config.read('config.ini')
class Sniper:
    def __init__(self) -> None:
        self.webhookEnabled = False if not "configWebhook" in config or not bool(config["configWebhook"]["enabled"] == "on") else True
        self.webhookUrl = config["configWebhook"]["webhook"] if self.webhookEnabled else None
        self.accounts = None
        self.items = self._load_items()
        self.title = ("""
▒██   ██▒ ▒█████   ██▓     ▒█████             ██████  ███▄    █  ██▓ ██▓███  ▓█████  ██▀███  
▒▒ █ █ ▒░▒██▒  ██▒▓██▒    ▒██▒  ██▒         ▒██    ▒  ██ ▀█   █ ▓██▒▓██░  ██▒▓█   ▀ ▓██ ▒ ██▒
░░  █   ░▒██░  ██▒▒██░    ▒██░  ██▒         ░ ▓██▄   ▓██  ▀█ ██▒▒██▒▓██░ ██▓▒▒███   ▓██ ░▄█ ▒
 ░ █ █ ▒ ▒██   ██░▒██░    ▒██   ██░           ▒   ██▒▓██▒  ▐▌██▒░██░▒██▄█▓▒ ▒▒▓█  ▄ ▒██▀▀█▄  
▒██▒ ▒██▒░ ████▓▒░░██████▒░ ████▓▒░         ▒██████▒▒▒██░   ▓██░░██░▒██▒ ░  ░░▒████▒░██▓ ▒██▒
▒▒ ░ ░▓ ░░ ▒░▒░▒░ ░ ▒░▓  ░░ ▒░▒░▒░          ▒ ▒▓▒ ▒ ░░ ▒░   ▒ ▒ ░▓  ▒▓▒░ ░  ░░░ ▒░ ░░ ▒▓ ░▒▓░
░░   ░▒ ░  ░ ▒ ▒░ ░ ░ ▒  ░  ░ ▒ ▒░          ░ ░▒  ░ ░░ ░░   ░ ▒░ ▒ ░░▒ ░      ░ ░  ░  ░▒ ░ ▒░
 ░    ░  ░ ░ ░ ▒    ░ ░   ░ ░ ░ ▒           ░  ░  ░     ░   ░ ░  ▒ ░░░          ░     ░░   ░ 
 ░    ░      ░ ░      ░  ░    ░ ░                 ░           ░  ░              ░  ░   ░     
                                                                                             
""")
        self.checks = 0
        self.buys = 0
        self.request_method = 2
        self.total_ratelimits = 0
        self.last_time = 0
        self.errors = 0
        self.clear = "cls" if os.name == 'nt' else "clear"  
        self._setup_accounts()
        
    class DotDict(dict):
        def __getattr__(self, attr):
            return self[attr]
    
    def _setup_accounts(self) -> None:
        cookies = self._load_cookies()
        for i in cookies:
              response = asyncio.run(self._get_user_id(cookies[i]["cookie"]))
              response2 = asyncio.run(self._get_xcsrf_token(cookies[i]["cookie"]))
              cookies[i]["id"] = response
              cookies[i]["xcsrf_token"] = response2["xcsrf_token"]
              cookies[i]["created"] = response2["created"]
        self.accounts = cookies
        
    def _load_cookies(self) -> dict:
        with open("cookie.txt", "r") as file:
            lines = file.read().split('\n')
            my_dict = {}
            for i, line in enumerate(lines):
                my_dict[str(i+1)] = {}
                my_dict[str(i+1)] = {"cookie": line}
            return my_dict
        
    def _load_items(self) -> list:
        with open('limiteds.txt', 'r') as f:
            return [line.strip() for line in f.readlines()]
            
    async def _get_user_id(self, cookie) -> str:
       async with httpx.AsyncClient(cookies={".ROBLOSECURITY": cookie}) as client:
           response = await client.get("https://users.roblox.com/v1/users/authenticated")
           data = response.json()
           if data.get('id') == None:
              raise Exception("Couldn't scrape user id")
           return data.get('id')
    
    def _print_stats(self) -> None:
        print("Version: 3.8.1")
        print(Fore.GREEN + Style.BRIGHT + self.title)
        print(Style.BRIGHT + f"――――――――――――――――――――――――――――――――――――――[Total buys: {Fore.GREEN}{Style.BRIGHT}{self.buys}{Fore.WHITE}{Style.BRIGHT}]――――――――――――――――――――――――――――――――――――――")
        print(Style.BRIGHT + f"―――――――――――――――――――――――――――――――――――[Total ratelimits: {Fore.RED}{Style.BRIGHT}{self.total_ratelimits}{Fore.WHITE}{Style.BRIGHT}]―――――――――――――――――――――――――――――――――――")
        print(Style.BRIGHT + f"―――――――――――――――――――――――――――――――――――[Total errors: {Fore.RED}{Style.BRIGHT}{self.errors}{Fore.WHITE}{Style.BRIGHT}]―――――――――――――――――――――――――――――――――――")
        print(Style.BRIGHT + f"――――――――――――――――――――――――――――――――――[Total price checks: {Fore.YELLOW}{Style.BRIGHT}{self.checks}{Fore.WHITE}{Style.BRIGHT}]――――――――――――――――――――――――――――――――――")
        print(Style.BRIGHT + f"――――――――――――――――――――――――――――――――――――[Last Speed: {Fore.YELLOW}{Style.BRIGHT}{self.last_time}{Fore.WHITE}{Style.BRIGHT}]――――――――――――――――――――――――――――――――――――")
            
    async def _get_xcsrf_token(self, cookie) -> dict:
        async with httpx.AsyncClient(cookies={".ROBLOSECURITY": cookie}) as client:
              response = await client.post("https://accountsettings.roblox.com/v1/email", headers={'User-Agent': ua.random})
              xcsrf_token = response.headers.get("x-csrf-token")
              if xcsrf_token is None:
                 raise Exception("An error occurred while getting the X-CSRF-TOKEN. "
                            "Could be due to an invalid Roblox Cookie")
              return {"xcsrf_token": xcsrf_token, "created": datetime.datetime.now()}
    
    async def _check_xcsrf_token(self) -> bool:
      for i in self.accounts:
        if self.accounts[i]["xcsrf_token"] is None or \
                datetime.datetime.now() > (self.accounts[i]["created"] + datetime.timedelta(minutes=10)):
            try:
                response = await self._get_xcsrf_token(self.accounts[i]["cookie"])
                self.accounts[i]["xcsrf_token"] = response["xcsrf_token"]
                self.accounts[i]["created"] = response["created"]
                return True
            except Exception as e:
                print(f"{e.__class__.__name__}: {e}")
                return False
        return True
      return False
  
    async def start(self) -> None:
        async def buy_item(item_id: int, price: int, user_id: int, creator_id: int,
         product_id: int, cookie: str, x_token: str) -> None:
        
         """
            Purchase a limited item on Roblox.
            Args:
                item_id (int): The ID of the limited item to purchase.
                price (int): The price at which to purchase the limited item.
                user_id (int): The ID of the user who will be purchasing the limited item.
                creator_id (int): The ID of the user who is selling the limited item.
                product_id (int): The ID of the product to which the limited item belongs.
                cookie (str): The .ROBLOSECURITY cookie associated with the user's account.
                x_token (str): The X-CSRF-TOKEN associated with the user's account.
         """
        
        
         data = {
              "collectibleItemId": item_id,
               "expectedCurrency": 1,
               "expectedPrice": price,
               "expectedPurchaserId": user_id,
               "expectedPurchaserType": "User",
               "expectedSellerId": creator_id,
               "expectedSellerType": "User",
               "idempotencyKey": "random uuid4 string that will be your key or smthn",
               "collectibleProductId": product_id
         }
        
         total_errors = 0
         async with httpx.AsyncClient() as client:
            while True:
                if total_errors >= 10:
                    print("Too many errors encountered. Aborting purchase.")
                    return
                 
                data["idempotencyKey"] = str(uuid.uuid4())
                response = await client.post(f"https://apis.roblox.com/marketplace-sales/v1/item/{item_id}/purchase-item",
                           json=data,
                           headers={"x-csrf-token": x_token, 'User-Agent': ua.random},
                           cookies={".ROBLOSECURITY": cookie})
                    
                if response.status_code == 429:
                       print("Ratelimit encountered. Retrying purchase in 0.5 seconds...")
                       await asyncio.sleep(0.5)
                       continue
            
                try:
                      json_response = response.json()
                except httpx.JSONDecodeError as e:
                      self.errors += 1
                      print(f"JSON decode error encountered: {e}. Retrying purchase...")
                      total_errors += 1
                      continue
                  
                except httpx.HTTPError as e:
                        self.errors += 1
                        total_errors += 1
                        print(f"HTTP error encountered: {e}. Retrying...")
                        continue
                    
                if not json_response["purchased"]:
                       self.errors += 1
                       print(f"Purchase failed. Response: {json_response}. Retrying purchase...")
                       total_errors += 1
                else:
                       print(f"Purchase successful. Response: {json_response}.")
                       self.buys += 1
                       if self.webhookEnabled:
                          embed = {
                               'title': f'New UGC item {item_id} bought',
                               'description': f'Price: {price}\nBuyer ID: {user_id}\nSeller ID: {creator_id}\nProduct ID: {product_id}',
                               'color': 0x00ff00
                                  }
                          requests.post(self.webhookUrl, json={'embeds': [embed]})
                       
                       
        while True:
            t0 = asyncio.get_event_loop().time()
            os.system(self.clear)
            self._print_stats()
            
            if not await self._check_xcsrf_token():
                raise Exception("x_csrf_token couldn't be generated")
            

            for currentItem in self.items:
                async with httpx.AsyncClient() as client:
                    headers = {"x-csrf-token": self.accounts[str(random.randint(1, len(self.accounts)))]['xcsrf_token'], 'User-Agent': ua.random}
                    cookies = {".ROBLOSECURITY": self.accounts[str(random.randint(1, len(self.accounts)))]["cookie"]}
                    json_body = {"items": [{"itemType": "Asset", "id": int(currentItem)}]}
                    response = await client.post(
                               "https://catalog.roblox.com/v1/catalog/items/details",
                                headers=headers,
                                cookies=cookies,
                                json=json_body
                    )
                    self.checks += 1
                    jsonr = response.json()
                    
                    if response.status_code == 429:
                       print("Rate limit hit")
                       self.total_ratelimits += 1
                       await asyncio.sleep(30)
                       continue
                    
                    if response.status_code == 429:
                       print(f"Ramdom Error: {jsonr}")
                       self.total_ratelimits += 1
                       await asyncio.sleep(10)
                       continue
                    
                    try:
                       json_response = jsonr["data"][0]
                    except Exception as e:
                        print("Json error:", e)
                        self.errors += 1
                        continue
                    
                    if json_response.get("priceStatus") != "Off Sale" and json_response.get('unitsAvailableForConsumption') > 0:
                       productid_response = await client.post("https://apis.roblox.com/marketplace-items/v1/items/details",
                                     json={"itemIds": [json_response["collectibleItemId"]]},
                                     headers={"x-csrf-token": self.accounts[str(random.randint(1, len(self.accounts)))]["xcsrf_token"], 'User-Agent': ua.random},
                                     cookies={".ROBLOSECURITY": self.accounts[str(random.randint(1, len(self.accounts)))]["cookie"]})
                       
                       
                       if productid_response.status_code == 404:
                           print("Product not found")
                           self.errors += 1
                           continue
                       
                       try:
                           da = productid_response.json()
                           productid_data = da[0]
                       except json.JSONDecodeError as e:
                           print(f'Error decoding JSON: {e}')
                           self.errors += 1
                           continue                     
                       coroutines = []
                       for i in self.accounts:
                              coroutines.append(buy_item(item_id = json_response["collectibleItemId"], price = json_response['price'], user_id = self.accounts[i]["id"], creator_id = json_response['creatorTargetId'], product_id = productid_data['collectibleProductId'], cookie = self.accounts[i]["cookie"], x_token = self.accounts[i]["xcsrf_token"]))
                       await asyncio.gather(*coroutines)
                       await asyncio.sleep(1)
                t1 = asyncio.get_event_loop().time()
                self.last_time = round(t1 - t0, 3)  
                await asyncio.sleep(1.5)

sniper = Sniper()
asyncio.run(sniper.start())
