# made by xolo#4942
# version 8.0.0

try:
  import datetime
  import os
  import uuid
  import asyncio
  import random
  import requests
  from rgbprint import gradient_print, Color
  import aiohttp
  import json   

except ModuleNotFoundError:
    print("Modules not installed properly, installing now.")
    os.system("pip install requests")
    os.system("pip install rgbprint")
    os.system("pip install aiohttp")
    os.system("pip install rapidjson")

class Sniper:
    class bucket:
        def __init__(self, max_tokens: int, refill_interval: float):
            self.max_tokens = max_tokens
            self.tokens = max_tokens
            self.refill_interval = refill_interval
            self.last_refill_time = asyncio.get_event_loop().time()

        async def take(self, tokens: int):
            while True:
                elapsed = asyncio.get_event_loop().time() - self.last_refill_time
                if elapsed > self.refill_interval:
                   self.tokens = self.max_tokens
                   self.last_refill_time = asyncio.get_event_loop().time()

                if self.tokens >= tokens:
                   self.tokens -= tokens
                   return
                else:
                   await asyncio.sleep(0.01)
                
    def __init__(self) -> None:
        with open("config.json") as file:
             config = json.load(file)
        self.clear = "cls" if os.name == 'nt' else "clear"
        if os.name == "nt":
            os.system("title Xolo Sniper")
        os.system(self.clear)
        self.webhookEnabled = False if not config["webhook"] or config["webhook"]["enabled"] == False else True
        self.webhookUrl = config["webhook"]["url"] if self.webhookEnabled else None
        self.accounts = None
        self.items = self._load_items()
        self.title = ("""  
  ▀████    ▐████▀  ▄██████▄   ▄█        ▄██████▄  
    ███▌   ████▀  ███    ███ ███       ███    ███           _.._
     ███  ▐███    ███    ███ ███       ███    ███         .' .-'`
     ▀███▄███▀    ███    ███ ███       ███    ███        /  /
     ████▀██▄     ███    ███ ███       ███    ███        |  |
    ▐███  ▀███    ███    ███ ███       ███    ███        \  '.___.;
   ▄███     ███▄  ███    ███ ███▌    ▄ ███    ███         '._  _.'
  ████       ███▄  ▀██████▀  █████▄▄██  ▀██████▀             ``
                             ▀                    
		> the best one out there (yet again) <""") if config["title"]["minimal"] else ("""  
  ▀████    ▐████▀  ▄██████▄   ▄█        ▄██████▄          ▄████████ ███▄▄▄▄    ▄█     ▄███████▄    ▄████████    ▄████████ 
    ███▌   ████▀  ███    ███ ███       ███    ███        ███    ███ ███▀▀▀██▄ ███    ███    ███   ███    ███   ███    ███           _.._
     ███  ▐███    ███    ███ ███       ███    ███        ███    █▀  ███   ███ ███▌   ███    ███   ███    █▀    ███    ███         .' .-'`
     ▀███▄███▀    ███    ███ ███       ███    ███        ███        ███   ███ ███▌   ███    ███  ▄███▄▄▄      ▄███▄▄▄▄██▀        /  /
     ████▀██▄     ███    ███ ███       ███    ███      ▀███████████ ███   ███ ███▌ ▀█████████▀  ▀▀███▀▀▀     ▀▀███▀▀▀▀▀          |  |
    ▐███  ▀███    ███    ███ ███       ███    ███               ███ ███   ███ ███    ███          ███    █▄  ▀███████████        \  '.___.;
   ▄███     ███▄  ███    ███ ███▌    ▄ ███    ███         ▄█    ███ ███   ███ ███    ███          ███    ███   ███    ███         '._  _.'
  ████       ███▄  ▀██████▀  █████▄▄██  ▀██████▀        ▄████████▀   ▀█   █▀  █▀    ▄████▀        ██████████   ███    ███            ``
                             ▀                                                                                 ███    ███ 
						    > the best one out there (yet again) <""")
        self.checks = 0
        self.buys = 0
        self.request_method = 2
        self.last_time = 0
        self.errors = 0
        self.version = "8.0.0"
        self.task = None
        self.scraped_ids = []
        self.latest_free_item = {}
        self._setup_accounts()
        self.check_version()
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
    
    def check_version(self):
        self.task = "GitHub Checker"
        self._print_stats()
        response = requests.get("https://pastebin.com/raw/MXFsQ0TQ")
        
        if response.status_code != 200:
            pass
        if not response.text == self.version:
                print(f"""{Color(0xf2f24e)}! NEW UPDATED VERSION ({response.text}) !
{Color(0x7e33ff)}Please update your version at {Color(0xf2f24e)}https://github.com/efenatuyo/ugc-sniper
{Color(0x7e33ff)}Continuing in 5 seconds.{Color(0xffffff)}
""")
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
            return [line.rstrip() for line in f.readlines()]
                 
    async def _get_user_id(self, cookie) -> str:
       async with aiohttp.ClientSession(cookies={".ROBLOSECURITY": cookie}) as client:
           response = await client.get("https://users.roblox.com/v1/users/authenticated", ssl = False)
           data = await response.json()
           if data.get('id') == None:
              raise Exception("Couldn't scrape user id. Error:", data)
           return data.get('id')
    
    def _print_stats(self) -> None:
        gradient_print(self.title, start_color=Color(0x5916cc), end_color=Color(0xf2f24e))
        print(f""" 
 {Color(0xffffff)}-----------
  {Color(0x7e33ff)}Script  {Color(0xffffff)}:  {Color(0xf2f24e)}xolo#4249
  {Color(0x7e33ff)}Theme   {Color(0xffffff)}:  {Color(0xf2f24e)}SleepyLuc#9967
 {Color(0xffffff)}-----------
  {Color(0x7e33ff)}Version {Color(0xffffff)}:  {Color(0xf2f24e)}{self.version}
  {Color(0x7e33ff)}Task    {Color(0xffffff)}:  {Color(0xf2f24e)}{self.task}
 {Color(0xffffff)}-----------
  {Color(0x7e33ff)}Snipes  {Color(0xffffff)}:  {Color(0xf2f24e)}{self.buys}
  {Color(0x7e33ff)}Errors  {Color(0xffffff)}:  {Color(0xf2f24e)}{self.errors}
  {Color(0x7e33ff)}Speed   {Color(0xffffff)}:  {Color(0xf2f24e)}{self.last_time}
  {Color(0x7e33ff)}Checks  {Color(0xffffff)}:  {Color(0xf2f24e)}{self.checks}
 {Color(0xffffff)}-----------
""")

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
                print(f"{Color(0xff0000)}{e.__class__.__name__}: {e}{Color(0xffffff)}")
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
                    print(f"{Color(0xff8080)}Too many errors encountered. Aborting purchase.{Color(0xffffff)}")
                    return
                 
                data["idempotencyKey"] = str(uuid.uuid4())
                
                try:
                    response = await client.post(f"https://apis.roblox.com/marketplace-sales/v1/item/{item_id}/purchase-item",
                           json=data,
                           headers={"x-csrf-token": x_token},
                           cookies={".ROBLOSECURITY": cookie}, ssl = False)
                
                except aiohttp.ClientConnectorError as e:
                    self.errors += 1
                    print(f"{Color(0xff0000)}Connection error encountered: {e}. Retrying purchase...{Color(0xffffff)}")
                    total_errors += 1
                    continue
                    
                if response.status == 429:
                       print(f"{Color(0xffff00)}Ratelimit encountered. Retrying purchase in 0.5 seconds...{Color(0xffffff)}")
                       await asyncio.sleep(0.5)
                       continue
            
                try:
                      json_response = await response.json()
                except aiohttp.ContentTypeError as e:
                      self.errors += 1
                      print(f"{Color(0xff0000)}JSON decode error encountered: {e}. Retrying purchase...{Color(0xffffff)}")
                      total_errors += 1
                      continue
                  
                if not json_response["purchased"]:
                       self.errors += 1
                       print(f"{Color(0xff0000)}Purchase failed. Response: {json_response}. Retrying purchase...{Color(0xffffff)}")
                       total_errors += 1
                else:
                       print(f"{Color(0x00ff00)}Purchase successful! Response: {json_response}{Color(0xffffff)}")
                       self.buys += 1
                       if self.webhookEnabled:
                            embed_data = {
                                "title": "New Item purchased with Moon Sniper!",
                                "url": f"https://www.roblox.com/catalog/{item_id}/Xolo-Sniper",
                                "color": 65280,
                                "author": {
                                    "name": "Purchased limited successfully!"
                                },
                                "footer": {
                                "text": "Moon's Sniper"
                                }
                            }

                            requests.post(self.webhookUrl, json={"content": None, "embeds": [embed_data]})

    
    async def auto_search(self) -> None:
     async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=None)) as session:
      while True:
        try:
            async with session.get("https://catalog.roblox.com/v2/search/items/details?Keyword=orange%20teal%20cyan%20red%20green%20topaz%20yellow%20wings%20maroon%20space%20dominus%20lime%20mask%20mossy%20wooden%20crimson%20salmon%20brown%20pastel%20%20ruby%20diamond%20creatorname%20follow%20catalog%20link%20rare%20emerald%20chain%20blue%20deep%20expensive%20furry%20hood%20currency%20coin%20royal%20navy%20ocean%20air%20white%20cyber%20ugc%20verified%20black%20purple%20yellow%20violet%20description%20dark%20bright%20rainbow%20pink%20cyber%20roblox%20multicolor%20light%20gradient%20grey%20gold%20cool%20indigo%20test%20hat%20limited2%20headphones%20emo%20edgy%20back%20front%20lava%20horns%20water%20waist%20face%20neck%20shoulders%20collectable&Category=11&Subcategory=19&CurrencyType=3&MaxPrice=0&salesTypeFilter=2&SortType=3&limit=120", ssl = False) as response:
                  await self.ratelimit.take(1)
                  response.raise_for_status()
                   
                  items = (json.loads(await response.text())['data'])
                  
                  for item in items:
                      if item["id"] not in self.scraped_ids:
                          print(f"{Color(0xff0000)}Found new free item: {item['name']} (ID: {item['id']}){Color(0xffffff)}")
                          self.latest_free_item = item
                          self.scraped_ids.append(item)
                          
                          if self.latest_free_item.get("priceStatus", "Off Sale") == "Off Sale":
                            continue
                        
                          if self.latest_free_item.get("collectibleItemId") is None:
                              continue
                          await self.ratelimit.take(1)
                          productid_response = await session.post("https://apis.roblox.com/marketplace-items/v1/items/details",
                                     json={"itemIds": [self.latest_free_item["collectibleItemId"]]},
                                     headers={"x-csrf-token": self.accounts[str(random.randint(1, len(self.accounts)))]["xcsrf_token"], 'Accept': "application/json"},
                                     cookies={".ROBLOSECURITY": self.accounts[str(random.randint(1, len(self.accounts)))]["cookie"]}, ssl = False)
                          response.raise_for_status()
                          productid_data = json.loads(await  productid_response.text())[0]
                          coroutines = [self.buy_item(item_id = self.latest_free_item["collectibleItemId"], price = 0, user_id = self.accounts[i]["id"], creator_id = self.latest_free_item['creatorTargetId'], product_id = productid_data['collectibleProductId'], cookie = self.accounts[i]["cookie"], x_token = self.accounts[i]["xcsrf_token"]) for i in self.accounts]
                          self.task = "Item Buyer"
                          await asyncio.gather(*coroutines)
                          
        except aiohttp.client_exceptions.ClientConnectorError as e:
            print(f"{Color(0xff0000)}Error connecting to host: {e}{Color(0xffffff)}")
            self.errors += 1
        except aiohttp.client_exceptions.ServerDisconnectedError as e:
            print(f"{Color(0xff0000)}Server disconnected error: {e}{Color(0xffffff)}")
            self.errors += 1
        except aiohttp.client_exceptions.ClientOSError as e:
            print(f"{Color(0xff0000)}Client OS error: {e}{Color(0xffffff)}")
            self.errors += 1
        except aiohttp.client_exceptions.ClientResponseError as e:
            print(f"{Color(0xff0000)}Response Error: {e}{Color(0xffffff)}")
            self.errors += 1
            await asyncio.sleep(5)
        finally:
            self.checks += 1
            await asyncio.sleep(5)
            
                    
    async def given_id_sniper(self) -> None:
     async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=None)) as session:
      while True:
        try:
                self.task = "Item Scraper & Searcher"
                t0 = asyncio.get_event_loop().time()
                
                for currentItem in self.items:
                    if not currentItem.isdigit():
                        raise Exception(f"Invalid item id given ID: {currentItem}")
                    
                    await self.ratelimit.take(1)
                    currentAccount = self.accounts[str(random.randint(1, len(self.accounts)))]
                    async with session.post("https://catalog.roblox.com/v1/catalog/items/details",
                                           json={"items": [{"itemType": "Asset", "id": int(currentItem)}]},
                                           headers={"x-csrf-token": currentAccount['xcsrf_token'], 'Accept': "application/json"},
                                           cookies={".ROBLOSECURITY": currentAccount["cookie"]}, ssl=False) as response:
                        response.raise_for_status()
                        response_text = await response.text()
                        json_response = json.loads(response_text)['data'][0]
                        if json_response.get("priceStatus") != "Off Sale" and 0 if json_response.get('unitsAvailableForConsumption') is None else json_response.get('unitsAvailableForConsumption') > 0:
                            await self.ratelimit.take(1)
                            productid_response = await session.post("https://apis.roblox.com/marketplace-items/v1/items/details",
                                                                     json={"itemIds": [json_response["collectibleItemId"]]},
                                                                     headers={"x-csrf-token": currentAccount["xcsrf_token"], 'Accept': "application/json"},
                                                                     cookies={".ROBLOSECURITY": currentAccount["cookie"]}, ssl=False)
                            response.raise_for_status()
                            productid_data = json.loads(await productid_response.text())[0]
                            
                            coroutines = [self.buy_item(item_id = json_response["collectibleItemId"], price = json_response['price'], user_id = self.accounts[i]["id"], creator_id = json_response['creatorTargetId'], product_id = productid_data['collectibleProductId'], cookie = self.accounts[i]["cookie"], x_token = self.accounts[i]["xcsrf_token"]) for i in self.accounts]
                            self.task = "Item Buyer"
                            await asyncio.gather(*coroutines)
                    t1 = asyncio.get_event_loop().time()
                    self.last_time = round(t1 - t0, 3)
        except aiohttp.ClientConnectorError as e:
            print(f'{Color(0xff0000)}Connection error: {e}{Color(0xffffff)}')
            self.errors += 1
        except aiohttp.ContentTypeError as e:
            print(f'{Color(0xff0000)}Content type error: {e}{Color(0xffffff)}')
            self.errors += 1
        except aiohttp.ClientResponseError as e:
            pass
        finally:
            self.checks += 1
            await asyncio.sleep(0.5)
             
    
    async def start(self):   
            self.ratelimit = self.bucket(max_tokens=60, refill_interval=60)     
            coroutines = []
            coroutines.append(self.given_id_sniper())
            # coroutines.append(self.auto_search())
            coroutines.append(self.auto_update())
            await asyncio.gather(*coroutines)
    
    async def auto_update(self):
        while True:
            if not await self._check_xcsrf_token():
                raise Exception("x_csrf_token couldn't be generated")
            os.system(self.clear)
            self._print_stats()
            await asyncio.sleep(0.5)
        
sniper = Sniper()
sniper
