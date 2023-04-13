# made by xolo#4942
# version 4.0.2

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
  import fake_useragent
  import aiohttp

except ModuleNotFoundError:
    print("Modules not installed proberly installing now")
    os.system("pip install requests")
    os.system("pip install configparser")
    os.system("pip install colorama")
    os.system("pip install fake_useragent")
    os.system("pip install aiohttp")

ua = fake_useragent.UserAgent()
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
        self.task = None
        self._setup_accounts()
        # / couldn't fix errors aka aiohttp does not support proxies
        # self.proxylist = open("proxylist.txt").read().splitlines()
        # self.workingProxies = []
        # asyncio.run(self.start_proxy())
        # print(self.workingProxies)
        asyncio.run(self.start())
        
    # / couldn't fix errors aka aiohttp does not support proxies
    #async def check(self, proxy):
    #  async with aiohttp.ClientSession() as session:
    #      async with session.get('http://httpbin.org/ip', proxy=f'http://{proxy}', timeout=aiohttp.ClientTimeout(total=2), ssl = False) as resp:
    #          if resp.status == 200:
    #            self.workingProxies.append(proxy)
    #            return
            
    #def get_working_proxy(self):
    #  if len(self.workingProxies) != 0:
    #     proxy = random.choice(self.workingProxies)
    #     return f"http://{proxy}"
    #  else:
    #    return None

    #async def start_proxy(self):
    #  self.status = "Proxy checker"
    #  self._print_stats
    #  coroutines = []
    #  for proxy in self.proxylist:
    #      coroutines.append(self.check(proxy))
    #  await asyncio.gather(*coroutines)
      
    class DotDict(dict):
        def __getattr__(self, attr):
            return self[attr]
    
    def _setup_accounts(self) -> None:
        self.task = "Account Loader"
        self._print_stats
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
       async with aiohttp.ClientSession(cookies={".ROBLOSECURITY": cookie}) as client:
           response = await client.get("https://users.roblox.com/v1/users/authenticated")
           data = await response.json()
           if data.get('id') == None:
              raise Exception("Couldn't scrape user id")
           return data.get('id')
    
    def _print_stats(self) -> None:
        print("Version: 4.0.2")
        print(Fore.GREEN + Style.BRIGHT + self.title)
        print(Fore.RESET + Style.RESET_ALL)
        print(Style.BRIGHT + f"                           [ Total buys: {Fore.GREEN}{Style.BRIGHT}{self.buys}{Fore.WHITE}{Style.BRIGHT} ]")
        print(Style.BRIGHT + f"                           [ Total errors: {Fore.RED}{Style.BRIGHT}{self.errors}{Fore.WHITE}{Style.BRIGHT} ]")
        print(Style.BRIGHT + f"                           [ Last Speed: {Fore.YELLOW}{Style.BRIGHT}{self.last_time}{Fore.WHITE}{Style.BRIGHT} ]")
        print(Style.BRIGHT + f"                           [ Total ratelimits: {Fore.RED}{Style.BRIGHT}{self.total_ratelimits}{Fore.WHITE}{Style.BRIGHT} ]")
        print(Style.BRIGHT + f"                           [ Total price checks: {Fore.YELLOW}{Style.BRIGHT}{self.checks}{Fore.WHITE}{Style.BRIGHT} ]")
        print(Style.BRIGHT + f"                           [ Current Task: {Fore.GREEN}{Style.BRIGHT}{self.task}{Fore.WHITE}{Style.BRIGHT} ]")
            
    async def _get_xcsrf_token(self, cookie) -> dict:
        async with aiohttp.ClientSession(cookies={".ROBLOSECURITY": cookie}) as client:
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
         async with aiohttp.ClientSession() as client:
            while True:
                if total_errors >= 10:
                    print("Too many errors encountered. Aborting purchase.")
                    return
                 
                data["idempotencyKey"] = str(uuid.uuid4())
                response = await client.post(f"https://apis.roblox.com/marketplace-sales/v1/item/{item_id}/purchase-item",
                           json=data,
                           headers={"x-csrf-token": x_token, 'User-Agent': ua.random},
                           cookies={".ROBLOSECURITY": cookie})
                    
                if response.status == 429:
                       print("Ratelimit encountered. Retrying purchase in 0.5 seconds...")
                       await asyncio.sleep(0.5)
                       continue
            
                try:
                      json_response = await response.json()
                except aiohttp.ContentTypeError as e:
                      self.errors += 1
                      print(f"JSON decode error encountered: {e}. Retrying purchase...")
                      total_errors += 1
                      continue
                  
                if not json_response["purchased"]:
                       self.errors += 1
                       print(f"Purchase failed. Response: {json_response}. Retrying purchase...")
                       total_errors += 1
                else:
                       print(f"Purchase successful. Response: {json_response}.")
                       self.buys += 1
                       
                       
        while True:
            self.task = "Item Scraper"
            t0 = asyncio.get_event_loop().time()
            os.system(self.clear)
            self._print_stats()
            if not await self._check_xcsrf_token():
                raise Exception("x_csrf_token couldn't be generated")
            

            for currentItem in self.items:
                async with aiohttp.ClientSession() as session:
                 
                 if not currentItem.isdigit():
                     raise Exception(f"Invalid item id given ID: {currentItem}")
                 
                 currentAccount = self.accounts[str(random.randint(1, len(self.accounts)))]
                 async with session.post("https://catalog.roblox.com/v1/catalog/items/details",
                            json={"items": [{"itemType": "Asset", "id": int(currentItem)}]},
                            headers={"x-csrf-token": currentAccount['xcsrf_token']},
                            cookies={".ROBLOSECURITY": currentAccount["cookie"]}) as response:
                    self.checks += 1
                    
                    try:
                       jsonr = await response.json()
                    except:
                        print("JSON response error")
                        self.errors += 1

                    if response.status == 429:
                       print("Rate limit hit")
                       self.total_ratelimits += 1
                       await asyncio.sleep(30)
                       continue
                    
                    if response.status != 200:
                       print("Random error:", jsonr)
                       self.errors += 1
                       if jsonr.get("message") == 'Token Validation Failed':
                           self.status = "getting x token"
                           self._print_stats()
                           response = await self._get_xcsrf_token(currentAccount["cookie"])
                           currentAccount["xcsrf_token"] = response["xcsrf_token"]
                           currentAccount["created"] = response["created"]
                       elif jsonr.get("errors")[0]["message"] == 'Invalid asset type id.':
                           raise Exception("Invalid Item Id given")
                           
                       await asyncio.sleep(10)
                       continue
                    json_response = jsonr["data"][0]
                    if json_response.get("priceStatus") != "Off Sale" and 0 if json_response.get('unitsAvailableForConsumption') is None else json_response.get('unitsAvailableForConsumption') > 0:
                       productid_response = await session.post("https://apis.roblox.com/marketplace-items/v1/items/details",
                                     json={"itemIds": [json_response["collectibleItemId"]]},
                                     headers={"x-csrf-token": self.accounts[str(random.randint(1, len(self.accounts)))]["xcsrf_token"]},
                                     cookies={".ROBLOSECURITY": self.accounts[str(random.randint(1, len(self.accounts)))]["cookie"]})
                       
                       
                       if productid_response.status == 404:
                           print("Product not found")
                           self.errors += 1
                           continue
                       
                       try:
                           da = await productid_response.json()
                           productid_data = da[0]
                       except json.JSONDecodeError as e:
                           print(f'Error decoding JSON: {e}')
                           self.errors += 1
                           continue                     
                       coroutines = []
                       for i in self.accounts:
                              coroutines.append(buy_item(item_id = json_response["collectibleItemId"], price = json_response['price'], user_id = self.accounts[i]["id"], creator_id = json_response['creatorTargetId'], product_id = productid_data['collectibleProductId'], cookie = self.accounts[i]["cookie"], x_token = self.accounts[i]["xcsrf_token"]))
                       self.task = "Item Buyer"
                       self._print_stats()
                       await asyncio.gather(*coroutines)
                t1 = asyncio.get_event_loop().time()
                self.last_time = round(t1 - t0, 3)
                await asyncio.sleep(1.5)

sniper = Sniper()
sniper
