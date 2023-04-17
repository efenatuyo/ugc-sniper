# made by xolo#4942
# version 6.1.1

try:
  import datetime
  import json
  import os
  import uuid
  import asyncio
  import random
  import requests
  from colorama import Fore, Back, Style
  import aiohttp

except ModuleNotFoundError:
    print("Modules not installed properly installing now")
    os.system("pip install requests")
    os.system("pip install colorama")
    os.system("pip install aiohttp")

with open("config.json") as file:
    config = json.load(file)
class Sniper:
    def __init__(self) -> None:
        self.webhookEnabled = False if not config["webhook"] or config["webhook"]["enabled"] == False else True
        self.webhookUrl = config["webhook"]["url"] if self.webhookEnabled else None
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
        self.version = "6.1.1"
        self.task = None
        self.scraped_ids = []
        self.latest_free_item = {}
        self._setup_accounts()

        self.iteminfo = self._load_info()
        if self.webhookEnabled:
            dumps = json.dumps(self.iteminfo, indent=2)
            requests.post(self.webhookUrl, json={"content":None,"embeds":[{"title":"Hello World!","description":f"Loaded item information:```json\n{dumps}\n```","color":16776960,"footer":{"text":"Xolo's Sniper"}}]})
        
        # / couldn't fix errors aka aiohttp does not support proxies
        # self.proxylist = open("proxylist.txt").read().splitlines()
        # self.workingProxies = []
        # asyncio.run(self.start_proxy())
        # print(self.workingProxies)
        self.check_version()
        
        # asyncio.run(self.start())
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
    
    def check_version(self):
        self.task = "Github Checker"
        self._print_stats()
        response = requests.get("https://pastebin.com/raw/MXFsQ0TQ")
        
        if response.status_code != 200:
            pass
        print(response.text)
        if not response.text == self.version:
                print("NEW UPDATED VERSION PLEASE UPDATE YOUR FILE")
                print("will continue in 5 seconds")
                import time
                time.sleep(5)
        
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
        
    def _load_info(self) -> dict:
        currentAccount = self.accounts[str(random.randint(1, len(self.accounts)))]
        iteminfo = {}
        for limited in self.items:
            info = requests.post("https://catalog.roblox.com/v1/catalog/items/details", json={"items": [{"itemType": "Asset", "id": limited}]}, headers={"x-csrf-token": currentAccount['xcsrf_token']}, cookies={".ROBLOSECURITY": currentAccount["cookie"]})
            thumbnail = requests.get(f"https://thumbnails.roblox.com/v1/assets?assetIds={limited}&returnPolicy=PlaceHolder&size=512x512&format=Png&isCircular=false", headers={"x-csrf-token": currentAccount['xcsrf_token']}, cookies={".ROBLOSECURITY": currentAccount["cookie"]})
            iteminfo[str(limited)] = {}
            if info.status_code == 200:
                iteminfo[limited]["name"] = info.json()["data"][0]["name"]
            else: 
                iteminfo[limited]["name"] = f"https://www.roblox.com/catalog/{limited}"

            if thumbnail.status_code == 200:
                iteminfo[limited]["img"] = thumbnail.json()["data"][0]["imageUrl"]
            else:
                iteminfo[limited]["img"] = None
        
        return iteminfo
            
    async def _get_user_id(self, cookie) -> str:
       async with aiohttp.ClientSession(cookies={".ROBLOSECURITY": cookie}) as client:
           response = await client.get("https://users.roblox.com/v1/users/authenticated", ssl = False)
           data = await response.json()
           if data.get('id') == None:
              raise Exception("Couldn't scrape user id. Error:", data)
           return data.get('id')
    
    def _print_stats(self) -> None:
        print(f"Version: {self.version}")
        print(Fore.GREEN + Style.BRIGHT + self.title)
        print(Fore.RESET + Style.RESET_ALL)
        print(Style.BRIGHT + f"                           [ Total buys: {Fore.GREEN}{Style.BRIGHT}{self.buys}{Fore.WHITE}{Style.BRIGHT} ]")
        print(Style.BRIGHT + f"                           [ Total errors: {Fore.RED}{Style.BRIGHT}{self.errors}{Fore.WHITE}{Style.BRIGHT} ]")
        print(Style.BRIGHT + f"                           [ Last Speed: {Fore.YELLOW}{Style.BRIGHT}{self.last_time}{Fore.WHITE}{Style.BRIGHT} ]")
        print(Style.BRIGHT + f"                           [ Total ratelimits: {Fore.RED}{Style.BRIGHT}{self.total_ratelimits}{Fore.WHITE}{Style.BRIGHT} ]")
        print(Style.BRIGHT + f"                           [ Total price checks: {Fore.YELLOW}{Style.BRIGHT}{self.checks}{Fore.WHITE}{Style.BRIGHT} ]")
        print()
        print(Style.BRIGHT + f"                           [ Current Task: {Fore.GREEN}{Style.BRIGHT}{self.task}{Fore.WHITE}{Style.BRIGHT} ]")
            
    async def _get_xcsrf_token(self, cookie) -> dict:
        async with aiohttp.ClientSession(cookies={".ROBLOSECURITY": cookie}) as client:
              response = await client.post("https://accountsettings.roblox.com/v1/email", ssl = False)
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
     
    async def buy_item(self, item_id: int, price: int, user_id: int, creator_id: int,
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
                           headers={"x-csrf-token": x_token},
                           cookies={".ROBLOSECURITY": cookie}, ssl = False)
                    
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
                       if self.webhookEnabled:
                            if self.iteminfo[item_id]:
                                requests.post(self.webhookUrl, json={"content":None,"embeds":[{"title":f"{self.iteminfo[item_id]['name']}","url":f"https://www.roblox.com/catalog/{item_id}","color":65280,"fields":[{"name":"purchaseResult","value":f"{json_response['purchaseResult']}","inline":True},{"name":"purchased","value":f"{json_response['purchased']}","inline":True},{"name":"errorMessage","value":f"{json_response['errorMessage']}"}],"author":{"name":"Purchased limited successfully!"},"footer":{"text":"Xolo's Sniper"},"thumbnail":{"url":f"{self.iteminfo[item_id]['img']}"}}]})
                            else:
                                requests.post(self.webhookUrl, json={"content":None,"embeds":[{"title":f"https://www.roblox.com/catalog/{item_id}","url":f"https://www.roblox.com/catalog/{item_id}","color":65280,"fields":[{"name":"purchaseResult","value":f"{json_response['purchaseResult']}","inline":True},{"name":"purchased","value":f"{json_response['purchased']}","inline":True},{"name":"errorMessage","value":f"{json_response['errorMessage']}"}],"author":{"name":"Purchased limited from scraper successfully!"},"footer":{"text":"Xolo's Sniper"},"thumbnail":{"url":f"{None}"}}]})
    
    async def auto_search(self) -> None:
      while True:
       try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://catalog.roblox.com/v1/search/items/details?Keyword=orange%20teal%20cyan%20red%20green%20topaz%20yellow%20wings%20maroon%20space%20dominus%20lime%20mask%20mossy%20wooden%20crimson%20salmon%20brown%20pastel%20%20ruby%20diamond%20creatorname%20follow%20catalog%20link%20rare%20emerald%20chain%20blue%20deep%20expensive%20furry%20hood%20currency%20coin%20royal%20navy%20ocean%20air%20white%20cyber%20ugc%20verified%20black%20purple%20yellow%20violet%20description%20dark%20bright%20rainbow%20pink%20cyber%20roblox%20multicolor%20light%20gradient%20grey%20gold%20cool%20indigo%20test%20hat%20limited2%20headphones%20emo%20edgy%20back%20front%20lava%20horns%20water%20waist%20face%20neck%20shoulders%20collectable&Category=11&Subcategory=19&CurrencyType=3&MaxPrice=0&salesTypeFilter=2&SortType=3&limit=30", ssl = False) as response:
                self.checks += 1       
                if response.status == 429:
                       print("Rate limit hit")
                       self.total_ratelimits += 1
                       await asyncio.sleep(20)
                       continue
                   
                if response.status == 200:
                  items = (await response.json())["data"]
                  for item in items:
                      if item["id"] not in self.scraped_ids:
                          print(f"Found new free item: {item['name']} (ID: {item['id']})")
                          self.latest_free_item = item
                          self.scraped_ids.append(item['id'])
                          
                          if self.latest_free_item.get("priceStatus", "Off Sale") == "Off Sale":
                            continue
                        
                          if self.latest_free_item.get("collectibleItemId") is None:
                              continue
                          
                          productid_response = await session.post("https://apis.roblox.com/marketplace-items/v1/items/details",
                                     json={"itemIds": [self.latest_free_item["collectibleItemId"]]},
                                     headers={"x-csrf-token": self.accounts[str(random.randint(1, len(self.accounts)))]["xcsrf_token"]},
                                     cookies={".ROBLOSECURITY": self.accounts[str(random.randint(1, len(self.accounts)))]["cookie"]}, ssl = False)
                          try:
                           da = await productid_response.json(content_type='application/json')
                           productid_data = da[0]
                          except (json.JSONDecodeError, aiohttp.ContentTypeError) as e:
                           print(f'Error decoding JSON: {e}')
                           self.errors += 1
                      
                          coroutines = []
                          for i in self.accounts:
                              coroutines.append(self.buy_item(item_id = self.latest_free_item["collectibleItemId"], price = 0, user_id = self.accounts[i]["id"], creator_id = self.latest_free_item['creatorTargetId'], product_id = productid_data['collectibleProductId'], cookie = self.accounts[i]["cookie"], x_token = self.accounts[i]["xcsrf_token"]))
                          self.task = "Item Buyer"
                          await asyncio.gather(*coroutines)
        await asyncio.sleep(5)
       except aiohttp.client_exceptions.ClientConnectorError as e:
           print(f"Error connecting to host: {e}")
           self.errors
                    
    async def given_id_sniper(self) -> None:
        while True:
         async with aiohttp.ClientSession() as session:
            self.task = "Item Scraper & Searcher"
            t0 = asyncio.get_event_loop().time()

            for currentItem in self.items:
                 if not currentItem.isdigit():
                     raise Exception(f"Invalid item id given ID: {currentItem}")
                 
                 currentAccount = self.accounts[str(random.randint(1, len(self.accounts)))]
                 async with session.post("https://catalog.roblox.com/v1/catalog/items/details",
                            json={"items": [{"itemType": "Asset", "id": int(currentItem)}]},
                            headers={"x-csrf-token": currentAccount['xcsrf_token']},
                            cookies={".ROBLOSECURITY": currentAccount["cookie"]}, ssl = False) as response:
                    self.checks += 1
                    
                    try:
                       jsonr = await response.json()
                    except:
                        print("JSON response error")
                        self.errors += 1

                    if response.status == 429:
                       print("Rate limit hit")
                       self.total_ratelimits += 1
                       await asyncio.sleep(20)
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
                       elif jsonr.get("errors")[0]["message"] is not None and jsonr.get("errors")[0]["message"] == 'Invalid asset type id.':
                           raise Exception("Invalid Item Id given")
                           
                       await asyncio.sleep(10)
                       continue
                    
                    try:
                       json_response = jsonr["data"][0]
                    except Exception as e:
                        print("Json Error:", e)
                        
                    if json_response.get("priceStatus") != "Off Sale" and 0 if json_response.get('unitsAvailableForConsumption') is None else json_response.get('unitsAvailableForConsumption') > 0:
                       productid_response = await session.post("https://apis.roblox.com/marketplace-items/v1/items/details",
                                     json={"itemIds": [json_response["collectibleItemId"]]},
                                     headers={"x-csrf-token": self.accounts[str(random.randint(1, len(self.accounts)))]["xcsrf_token"]},
                                     cookies={".ROBLOSECURITY": self.accounts[str(random.randint(1, len(self.accounts)))]["cookie"]}, ssl = False)
                       
                       
                       if productid_response.status == 404:
                           print("Product not found")
                           self.errors += 1
                           continue
                       
                       try:
                           da = await productid_response.json(content_type='application/json')
                           productid_data = da[0]
                       except (json.JSONDecodeError, aiohttp.ContentTypeError) as e:
                           print(f'Error decoding JSON: {e}')
                           self.errors += 1
                           continue                     
                       coroutines = []
                       for i in self.accounts:
                              coroutines.append(self.buy_item(item_id = json_response["collectibleItemId"], price = json_response['price'], user_id = self.accounts[i]["id"], creator_id = json_response['creatorTargetId'], product_id = productid_data['collectibleProductId'], cookie = self.accounts[i]["cookie"], x_token = self.accounts[i]["xcsrf_token"]))
                       self.task = "Item Buyer"
                       await asyncio.gather(*coroutines)
                 t1 = asyncio.get_event_loop().time()
                 self.last_time = round(t1 - t0, 3)
                 await asyncio.sleep(1)
    
    async def start(self):
            coroutines = []
            coroutines.append(self.given_id_sniper())
            coroutines.append(self.auto_search())
            coroutines.append(self.auto_update())
            await asyncio.gather(*coroutines)
    
    async def auto_update(self):
        while True:
            if not await self._check_xcsrf_token():
                raise Exception("x_csrf_token couldn't be generated")
            os.system(self.clear)
            self._print_stats()
            await asyncio.sleep(1)
        
sniper = Sniper()
sniper
