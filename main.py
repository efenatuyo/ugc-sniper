# made by xolo#4942
try:
 try:
  import logging
  import traceback
  import datetime
  import os
  import uuid
  import asyncio
  import random
  import requests
  from colorama import Fore, Back, Style
  import aiohttp
  import json
  import discord
  from discord.ext import commands
  import time
  import socketio
  from functools import partial
  from typing import Dict
  import themes
 except ModuleNotFoundError as e:
    print("Modules not installed properly installing now", e)
    os.system("pip install requests")
    os.system("pip install colorama")
    os.system("pip install colorama")
    os.system("pip install aiohttp")
    os.system("pip install discord")
    os.system("pip install logging")
    os.system("pip install python-socketio")
 logging.basicConfig(filename='logs.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
 logger = logging.getLogger(__name__)
 logger.setLevel(logging.DEBUG)

 formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

 handler = logging.StreamHandler()
 handler.setLevel(logging.DEBUG)
 handler.setFormatter(formatter)

 logger.addHandler(handler)
 

 sio = socketio.AsyncClient()
 
 if os.name == 'nt':
     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
 
 ################################################################################################################################      
 class Sniper:
    VERSION = "12.1.2"
    
    class bucket:
        def __init__(self, max_tokens: int, refill_interval: float):
            self.max_tokens = max_tokens
            self.tokens = max_tokens
            self.refill_interval = refill_interval
            self.last_refill_time = asyncio.get_event_loop().time()

        async def take(self, tokens: int, proxy=False):
            while True:
                if proxy:
                    return True
                
                elapsed = asyncio.get_event_loop().time() - self.last_refill_time
                if elapsed > self.refill_interval:
                   self.tokens = self.max_tokens
                   self.last_refill_time = asyncio.get_event_loop().time()

                if self.tokens >= tokens:
                   self.tokens -= tokens
                   return
                else:
                   await asyncio.sleep(0.01)
                   
    class ProxyHandler:
       class TokenBucket:
            def __init__(self, capacity, rate):
                self.capacity = capacity
                self.tokens = capacity
                self.rate = rate
                self.timestamp = time.monotonic()

            def consume(self):
                now = time.monotonic()
                elapsed_time = now - self.timestamp
                self.timestamp = now
                new_tokens = elapsed_time * self.rate
                if new_tokens > 0:
                   self.tokens = min(self.tokens + new_tokens, self.capacity)
                if self.tokens >= 1:
                   self.tokens -= 1
                   return True
                return False
            
       def __init__(self, proxies, requests_per_minute):
        self.proxies = proxies
        self.token_buckets = {proxy: self.TokenBucket(requests_per_minute, requests_per_minute/60) for proxy in proxies}
        self.current_proxy_index = 0

       def get_next_proxy(self):
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
        proxy = self.proxies[self.current_proxy_index]
        return proxy

       async def newprox(self):
        while True:
            proxy = self.proxies[self.current_proxy_index]
            if self.token_buckets[proxy].consume():
                return proxy
            self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)  
        
                      
    def __init__(self) -> None:
        logging.info("Started Sniper Class")
        
        self.checks = 0
        self.buys = 0
        self.last_time = 0
        self.errors = 0
        self.totalTasks = 0
        
        self.items = self.load_item_list
        
        self.users = []
        
        self.soldOut = []
        
        self._config = None
        
        self.accounts = self._setup_accounts()
        
        self.check_version()
        
        self.ratelmit = None
        asyncio.run(self.setup_ratelimit())
        
        self._task = None
        
        self.proxies = []
        
        @sio.event
        async def connect():
            print("Connected to server.")

        @sio.event
        async def disconnect():
            print("Disconnected from server.")

        async def user_disconnected(data, self):
            if data.get("room_code", "kekw") != self.config.get("rooms", {}).get("room_code"): return
            print(f"{data['user']} has left the room")
            self.users.delete(data['user'])
            
        async def new_roblox_item(self, data):
            if data.get("room_code", "kekw") != self.config.get("rooms", {}).get("room_code"): return
            
            if self.totalTasks >= 10: return
            required_args = ["CollectibleItemId", "PriceInRobux", "Creator", "CollectibleProductId", "AssetId"]
            if not all(arg in data['data'] for arg in required_args):
                return
            
            if self.config.get("rooms", {}).get("item_setup", {}).get("max_price") is not None and int(data.get("price", 0)) > self.config.get("rooms", {}).get("item_setup", {}).get("max_price"):
                print("Error: Max price has been reached.")
                return
            print(data["data"]["PriceInRobux"])
            self.totalTasks += 1
            coroutines = [self.buy_item(item_id=data["data"]["CollectibleItemId"],
            price=data["data"]["PriceInRobux"],
            user_id=self.accounts[i]["id"],
            creator_id=data["data"]["Creator"]["Id"],
            product_id=data["data"]["CollectibleProductId"],
            cookie=self.accounts[i]["cookie"],
            x_token=self.accounts[i]["xcsrf_token"],
            raw_id=data['data']["AssetId"]) for i in self.accounts for _ in range(4)]
            await asyncio.gather(*coroutines)
            
        async def new_item(self, data):
            if data.get("room_code", "kekw") != self.config.get("rooms", {}).get("room_code"): return
            required_args = ["collectibleItemId", "price", "creatorTargetId", "collectibleProductId", "id"]
            if not all(arg in data for arg in required_args):
                return
            
            if self.config.get("rooms", {}).get("item_setup", {}).get("max_price") is not None and int(data.get("price", 0)) > self.config.get("rooms", {}).get("item_setup", {}).get("max_price"):
                print("Error: Max price has been reached.")
                return
            
            self.totalTasks += 1
            coroutines = [self.buy_item(item_id=data["collectibleItemId"],
            price=data["price"],
            user_id=self.accounts[i]["id"],
            creator_id=data["creatorTargetId"],
            product_id=data["collectibleProductId"],
            cookie=self.accounts[i]["cookie"],
            x_token=self.accounts[i]["xcsrf_token"],
            raw_id=data["id"]) for i in self.accounts for _ in range(4)]
            print(f"{data['user']} FOUND A NEW ITEM")
            await asyncio.gather(*coroutines)
            
        
        async def user_joined(self, data):
            if data.get("room_code", "kekw") != self.config.get("rooms", {}).get("room_code"): return
            print(f"{data['user']} has joined your room")
            self.users.append(data['user'])
            
        sio.on("new_item")(partial(new_item, self))
        sio.on("user_joined")(partial(user_joined, self))
        sio.on("new_roblox_item")(partial(new_roblox_item, self))
        if self.config.get("discord", False)['enabled']:
            self.run_bot()
        else:
            asyncio.run(self.start())
    
    def proxy_setup(self):
        if self.config.get("proxy", {}).get("enabled", False):
            logging.info("Proxy enabled")
            lines = self.proxy_list
            response = asyncio.run(self.check_all_proxies(lines))
            self.proxies = response
            self.proxy_handler = self.ProxyHandler(self.proxies, 60)
    
    async def setup_ratelimit(self):
         self.ratelimit = self.bucket(max_tokens=60, refill_interval=60)
         
    @property
    def proxy_list(self):
            with open(self.config['proxy']['proxy_list']) as f: return [line.strip() for line in f if line.rstrip()]
            
    @property
    def rooms(self): return True if self.config.get("rooms", {}).get("enabled", None) else False
    
    @property
    def room_code(self): return self.config.get("rooms", {}).get("room_code", None)
    
    @property
    def username(self): return self.config.get("rooms", {}).get("username", None)
    
    @property
    def webhookEnabled(self): return True if self.config.get("webhook", {}).get("enabled", None) else False
    
    @property
    def webhookUrl(self): return self.config.get("webhook", {}).get("url", None)
    
    @property
    def clear(self): return "cls" if os.name == 'nt' else "clear"
    
    @property
    def themeWaitTime(self): return float(self.config.get('theme', {}).get('wait_time', 1))
    
    @property
    def proxy_auth(self): return aiohttp.BasicAuth(self.config.get("proxy", {}).get("authentication", {}).get("username", None), self.config.get("proxy", {}).get("authentication", {}).get("password", None)) if self.config.get("proxy", {}).get("authentication", {}).get("enabled", None) else None
    
    @classmethod
    @property
    def version(cls): return cls.VERSION
    
    @property
    def timeout(self): return self.config.get("proxy", {}).get("timeout_ms", None) / 1000 if self.config.get("proxy", {}).get("enabled", None) else None
    
    @property
    def load_item_list(self): return self._load_items()
      
    @property
    def config(self): 
        with open("config.json") as file: self._config = json.load(file)
        return self._config
        
    async def check_proxy(self, proxy):
        try:
          async with aiohttp.ClientSession() as session:
            response = await session.get('https://google.com/', timeout=self.timeout, proxy=f"http://{proxy}", proxy_auth = self.proxy_auth)
            if response.status == 200:
                return proxy
        except:
            pass

    async def check_all_proxies(self, proxies):
        logging.info("Checking all proxies")
        tasks = []
        for proxy in proxies:
            task = asyncio.create_task(self.check_proxy(proxy))
            tasks.append(task)
        results = await asyncio.gather(*tasks, return_exceptions=True)
        working_proxies = []
        for result in results:
            if result is not None:
               working_proxies.append(result)
        return working_proxies
    
    def run_bot(self):
        bot = commands.Bot(command_prefix=self.config.get('discord')['prefix'], intents=discord.Intents.all())
        
        @bot.command(name="queue")
        async def queue(ctx):
            try:
                embed = discord.Embed(title="Item Queue", color=0xffff00, description=f"```json\n{json.dumps(self.items, indent=2)}\n```")
                return await ctx.reply(embed=embed)
            except:
                return await ctx.reply(self.items)
        
        @bot.command(name="stats")
        async def stats(ctx):
            embed = discord.Embed(title="Sniper Stats", color=0x00ff00)
            embed.set_author(name=f"Xolo Sniper {self.version}")
            embed.add_field(name="Loaded Items", value=f"{len(self.items)}", inline=True)
            embed.add_field(name="Total Buys", value=f"{self.buys}", inline=True)
            embed.add_field(name="Total Errors", value=f"{self.errors}", inline=True)
            embed.add_field(name="Last Speed", value=f"{self.last_time}", inline=True)
            embed.add_field(name="Total Price Checks", value=f"{self.checks}", inline=True)
            if self.rooms:
                embed.add_field(name="Room Users", value=f"{len(self.users)}", inline=True)
                embed.add_field(name="Room Code", value=f"{self.room_code}", inline=True)
            embed.add_field(name="Current Task", value=f"{self.task}", inline=True)
            return await ctx.reply(embed=embed)
        
        @bot.command(name="remove_id")
        async def remove_id(ctx, arg=None):
            if arg is None:
                return await ctx.reply(":warning: | You need to enter an ID to remove!")
            
            if not arg.isdigit():
                        return await ctx.reply(f":x: | Invalid given ID: {arg}")
                        
            if not arg in self.items:
                return await ctx.reply(":grey_question: | ID is not curently running.")
            
            del self.items[arg]
            for item in self._config["items"]['item_list']:
                if item["id"] == arg:
                    self._config["items"]['item_list'].remove(item)
                    break
                
            with open('config.json', 'w') as f:
                json.dump(self._config, f, indent=4)
            logging.debug(f"removed item id {arg}")
            return await ctx.reply(":white_check_mark: | ID successfully removed!")
            
        @bot.command(name="add_id")
        async def add_id(ctx, id=None, max_price=None, max_buys=None):
            if id is None:
               return await ctx.reply(":warning: | You need to enter an ID to add!")

            if not id.isdigit():
                        return await ctx.reply(f":x: | Invalid given ID: {id}")
                        
            if id in self.items:
               return await ctx.reply(":grey_question: | ID is currently running.")
            
            self._config['items']['item_list'].append({
                "id": id,
                "max_price": None if max_price is None else int(max_price),
                "max_buys": None if max_buys is None else int(max_buys)
            })
            with open('config.json', 'w') as f:
                 json.dump(self._config, f, indent=4)
            self.items[id] = {}
            self.items[id]['current_buys'] = 0
            for item in self.config["items"]['item_list']:
                if int(item['id']) == int(id):
                    item = item
                    break
            self.items[id]['max_buys'] = float('inf') if item['max_buys'] is None else int(item['max_buys'])
            self.items[id]['max_price'] = float('inf') if item['max_price'] is None else int(item['max_price'])
                
            await ctx.reply(":white_check_mark: | ID successfully added!")
            logging.debug(f"added item id {id}")

        @bot.command(name="link")
        async def link(ctx, id=None):
            if id is None:
               return await ctx.reply(":warning: | You need to enter an ID or position to get!")

            if not id.isdigit():
                        return await ctx.reply(f":x: | Invalid given ID or position: {id}")
            
            if id in self.items:
                await ctx.reply(f"https://www.roblox.com/catalog/{id}")
            elif int(id) <= len(self.items):
                keys = list(self.items.keys())
                await ctx.reply(f"https://www.roblox.com/catalog/{keys[int(id) - 1]}")
            else:
                return await ctx.reply(f":x: | Invalid given ID or position: {id}")

        @bot.command(name="users")
        async def users(ctx):
            if self.rooms:
                return await ctx.reply(", ".join(self.users))
            else:
                return await ctx.reply(":grey_question: | You're not in a room!")

        @bot.event
        async def on_ready():
            await self.start()
            
        bot.run(self.config.get('discord')['token'])
              
    def check_version(self):
        logging.debug(f"Checking Version")
        self.task = "Github Checker"
        self._print_stats()
        response = requests.get("https://raw.githubusercontent.com/efenatuyo/ugc-sniper/main/version")
        if response.status_code != 200:
            pass
        print(response.text.rstrip())
        if not response.text.rstrip() == self.version:
                print("NEW UPDATED VERSION PLEASE UPDATE YOUR FILE")
                print("will continue in 5 seconds")
                import time
                time.sleep(5)
        
    class DotDict(dict):
        def __getattr__(self, attr):
            return self[attr]
    
    def _setup_accounts(self) -> Dict[str, Dict[str, str]]:
        logging.info(f"Setting up accounts")
        self.task = "Account Loader"
        self._print_stats
        cookies = self._load_cookies()
        for i in cookies:
              response = asyncio.run(self._get_user_id(cookies[i]["cookie"]))
              response2 = asyncio.run(self._get_xcsrf_token(cookies[i]["cookie"]))
              cookies[i]["id"] = response
              cookies[i]["xcsrf_token"] = response2["xcsrf_token"]
              cookies[i]["created"] = response2["created"]
        return cookies
        
    def _load_cookies(self) -> dict:
            lines = self.config['accounts']
            my_dict = {}
            for i, line in enumerate(lines):
                my_dict[str(i+1)] = {}
                my_dict[str(i+1)] = {"cookie": line['cookie']}
            return my_dict
        
    def _load_items(self) -> list:
            dict = {}
            for item in self.config["items"]['item_list']:
                dict[item['id']] = {}
                dict[item['id']]['current_buys'] = 0
                dict[item['id']]['max_buys'] = float('inf') if item['max_buys'] is None else int(item['max_buys'])
                dict[item['id']]['max_price'] = float('inf') if item['max_price'] is None else int(item['max_price'])
            return dict
                 
    async def _get_user_id(self, cookie) -> str:
       async with aiohttp.ClientSession(cookies={".ROBLOSECURITY": cookie}) as client:
           response = await client.get("https://users.roblox.com/v1/users/authenticated", ssl = False)
           data = await response.json()
           if data.get('id') == None:
              raise Exception("Couldn't scrape user id. Error:", data)
           return data.get('id')
    
    def _print_stats(self) -> None:
        function_name = self.config['theme']['name']
        module = getattr(themes, function_name)
        function = getattr(module, '_print_stats')
        function(self)
            
    async def _get_xcsrf_token(self, cookie) -> dict:
        logging.debug(f"Scraped x_token")
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
         product_id: int, cookie: str, x_token: str, raw_id: int) -> None:
        
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
         if raw_id in self.soldOut:
             self.totalTasks -= 1 
             return
         await asyncio.to_thread(logging.info, "New Buy Thread Started")
         async with aiohttp.ClientSession() as client: 
            while True:
                if self.items.get(raw_id, {}).get('max_buys', 0) != 0 and not float(self.items.get(raw_id, {}).get('max_buys', 0)) >= float(self.items.get(raw_id, {}).get('current_buys', 1)):
                    del self.items[id]
                    for item in self.config['items']['item_list']:
                        if str(item['id']) == (raw_id):
                           self.config["items"]['item_list'].remove(item)
                           break
                
                    with open('config.json', 'w') as f:
                        json.dump(self.config, f, indent=4)
                    self.totalTasks -= 1
                    return
                if total_errors >= 3:
                    print("Too many errors encountered. Aborting purchase.")
                    self.totalTasks -= 1
                    return
                 
                data["idempotencyKey"] = str(uuid.uuid4())
                
                try:
                    response = await client.post(f"https://apis.roblox.com/marketplace-sales/v1/item/{item_id}/purchase-item",
                           json=data,
                           headers={"x-csrf-token": x_token},
                           cookies={".ROBLOSECURITY": cookie}, ssl = False)
                
                except aiohttp.ClientConnectorError as e:
                    self.errors += 1
                    print(f"Connection error encountered: {e}. Retrying purchase...")
                    total_errors += 1
                    continue
                    
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
                       if json_response.get("errorMessage", 0) == "QuantityExhausted":
                           self.soldOut.append(raw_id)
                           self.totalTasks -= 1
                           return
                else:
                       if raw_id in self.items: self.items[raw_id]['current_buys'] += 1
                       print(f"Purchase successful. Response: {json_response}.")
                       self.buys += 1
                       if self.webhookEnabled:
                            embed_data = {
                                "title": "New Item Purchased with Xolo Sniper",
                                "url": f"https://www.roblox.com/catalog/{item_id}/Xolo-Sniper",
                                "color": 65280,
                                "author": {
                                    "name": "Purchased limited successfully!"
                                },
                                "footer": {
                                "text": "Xolo's Sniper"
                                }
                            }

                            requests.post(self.webhookUrl, json={"content": None, "embeds": [embed_data]})
        
    async def search(self, session) -> None:
      start_date  = self.config["items"]['start']
      while True:
        try:
                    if self.config['proxy']['enabled'] and len(self.proxies) > 0:
                        proxy = f"http://{await self.proxy_handler.newprox()}"
                    else:
                        proxy = None
                    try:
                      start_time = datetime.datetime.strptime(str(start_date), "%Y-%m-%d %H:%M:%S")
                      if datetime.datetime.now() >= start_time:
                         pass
                      else:
                         continue
                    except Exception as e:
                         pass
                    self.task = "Item Scraper & Searcher"
                    t0 = asyncio.get_event_loop().time()
                    for id in self.items:
                        if not id.isdigit():
                           del self.items[id]
                           
                    await self.ratelimit.take(1, proxy = True if self.proxies is not None and len(self.proxies) > 0 else False)
                    currentAccount = self.accounts[str(random.randint(1, len(self.accounts)))]
                    async with session.post("https://catalog.roblox.com/v1/catalog/items/details",
                                           json={"items": [{"itemType": "Asset", "id": id} for id in self.items]},
                                           headers={"x-csrf-token": currentAccount['xcsrf_token'], 'Accept': "application/json"},
                                           cookies={".ROBLOSECURITY": currentAccount["cookie"]}, ssl=False, proxy=proxy, timeout=self.timeout, proxy_auth = self.proxy_auth) as response:
                        response.raise_for_status()
                        response_text = await response.text()
                        json_response = json.loads(response_text)['data']
                        for i in json_response:
                         if int(i.get("price", 0)) > self.items[id]['max_price']:
                             del self.items[i]
                         if i.get("priceStatus") != "Off Sale" and i.get('unitsAvailableForConsumption', 0) > 0:
                            await self.ratelimit.take(1, proxy = True if self.proxies is not None and len(self.proxies) > 0 else False)
                            productid_response = await session.post("https://apis.roblox.com/marketplace-items/v1/items/details",
                                                                     json={"itemIds": [i["collectibleItemId"]]},
                                                                     headers={"x-csrf-token": currentAccount["xcsrf_token"], 'Accept': "application/json"},
                                                                     cookies={".ROBLOSECURITY": currentAccount["cookie"]}, ssl=False)
                            response.raise_for_status()
                            productid_data = json.loads(await productid_response.text())[0]
                            self.totalTasks += 1
                            coroutines = [self.buy_item(item_id = i["collectibleItemId"], price = i['price'], user_id = self.accounts[o]["id"], creator_id = i['creatorTargetId'], product_id = productid_data['collectibleProductId'], cookie = self.accounts[o]["cookie"], x_token = self.accounts[o]["xcsrf_token"], raw_id = id) for o in self.accounts for _ in range(4)]
                            if self.rooms:
                                await sio.emit("new_item", data={'item': {"item_id": i["collectibleItemId"], "price": i['price'], "creator_id": i['creatorTargetId'], "raw_id": id}})
                            self.task = "Item Buyer"
                            await asyncio.gather(*coroutines)
                         else:
                            if i.get('unitsAvailableForConsumption', 1) == 0:
                                    del self.items[id]
                                
                    t1 = asyncio.get_event_loop().time()
                    self.last_time = round(t1 - t0, 3) 
        except aiohttp.ClientConnectorError as e:
            print(f'Connection error: {e}')
            self.errors += 1
        except aiohttp.ContentTypeError as e:
            print(f'Content type error: {e}')
            self.errors += 1
        except aiohttp.ClientResponseError as e:
            status_code = int(str(e).split(',')[0])
            if status_code == 429:
                await asyncio.to_thread(logging.info, "Rate limit hit")
                await asyncio.sleep(1.5)
        except asyncio.CancelledError:
            return
        except asyncio.TimeoutError as e:
            print(f"Timeout error: {e}")
            self.errors += 1
        finally:
            self.checks += len(self.items)
            await asyncio.sleep(1)
            
                               
    async def given_id_sniper(self) -> None:
     self.task = "Item Scraper & Searcher"
     async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=None)) as session:
      await self.search(session=session)
    
        
    async def start(self):
            await asyncio.to_thread(logging.info, "Started sniping")
            coroutines = []
            if self.rooms:
                await sio.connect("https://electroniclightpinkfunnel.rfrrgf.repl.co", headers={'room': self.room_code, 'user': self.username})            
            coroutines.append(self.given_id_sniper())
            # coroutines.append(self.auto_search())
            coroutines.append(self.auto_update())
            coroutines.append(self.auto_xtoken())
            await asyncio.gather(*coroutines)
    
    async def auto_xtoken(self):
        while True:
            await asyncio.sleep(5)
            if not await self._check_xcsrf_token():
                raise Exception("x_csrf_token couldn't be generated")
            
    async def auto_update(self):
        while True:
            os.system(self.clear)
            self._print_stats()
            await asyncio.sleep(self.themeWaitTime)
            
 sniper = Sniper()
except Exception as e:
    logging.error(f"An error occurred: {traceback.format_exc()}")
    print("File crashed. Logs have been saved in logs.txt")
    os.system("pause")
