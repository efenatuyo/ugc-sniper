# made by xolo#4942
try:
 try:
  import datetime
  import logging
  import traceback
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
  from itertools import islice, cycle
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
    VERSION = "14.2.10"
                   
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
        self.itemsByAuto = []
        
        self.users = 0
        
        self.soldOut = []
        
        self._config = None
        
        self.accounts = self._setup_accounts()
        
        self.check_version()
        
        self.ratelmit = None
        
        self._task = None
        
        self.proxies = []
        
        @sio.event
        async def connect():
            print("Connected to server.")

        @sio.event
        async def disconnect():
            print("Disconnected from server.")

        async def user_disconnected(self, data):
            self.users = int(data["users"])  
    
        async def user_joined(self, data):
            self.users = int(data["users"])
        
        async def new_auto_search_items(self, data):
            for key, value in data['data'].items():
                if int(key) not in self.items['cheap_price_snipe'] and int(key) not in self.items['item_on_release_snipe'] and str(key) not in self.items['cheap_price_snipe'] and str(key) not in self.items['item_on_release_snipe'] and key not in self.items['cheap_price_snipe'] and key not in self.itemsByAuto:
                    self.items["item_on_release_snipe"][key] = value
                    self.itemsByAuto.append(key)
                      
        sio.on("new_auto_search_items")(partial(new_auto_search_items, self))
        sio.on("user_disconnected")(partial(user_disconnected, self))
        sio.on("user_joined")(partial(user_joined, self))
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
                embed = discord.Embed(title="Item Queue", color=0xffff00, description=f"```json\n{json.load(self.items)}\n```")
                return await ctx.reply(embed=embed)
            except:
                return await ctx.reply(self.items)
        
        @bot.command(name="stats")
        async def stats(ctx):
            embed = discord.Embed(title="Sniper Stats", color=0x00ff00)
            embed.set_author(name=f"Xolo Sniper {self.version}")
            embed.add_field(name="Loaded Items", value=f"{len(self.items['item_on_release_snipe']) + len(self.items['cheap_price_snipe'])}", inline=True)
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
                        
            if not arg in self.items['item_on_release_snipe'] and not arg in self.items['cheap_price_snipe']:
                return await ctx.reply(":grey_question: | ID is not curently running.")
            
            if arg in self.items['item_on_release_snipe']:
                del self.items['item_on_release_snipe'][arg]
            elif arg in self.items['cheap_price_snipe']:
                del self.items['cheap_price_snipe'][arg]
            
            if arg in self.items['item_on_release_snipe']:
                for item in self._config["items"]['item_on_release_snipe']:
                    if item["id"] == arg:
                        self._config["items"]['item_on_release_snipe'].remove(item)
                        break
            elif arg in self.items['cheap_price_snipe']:
                for item in self._config["items"]['cheap_price_snipe']:
                    if item["id"] == arg:
                        self._config["items"]['cheap_price_snipe'].remove(item)
                        break    
                
            with open('config.json', 'w') as f:
                json.dump(self._config, f, indent=4)
            logging.debug(f"removed item id {arg}")
            return await ctx.reply(":white_check_mark: | ID successfully removed!")
            
        @bot.command(name="add_id")
        async def add_id(ctx, id=None, type=None, max_price=None, max_buys=None):
            if id is None:
               return await ctx.reply(":warning: | You need to enter an ID to add!")
            
            if type is None or type.lower() not in ['release', "cheap"]:
                return await ctx.reply(":warning: | You need to enter a type! Ex: {prefix}add_id {id} release or {prefix}add_id {id} cheap")
            
            if not id.isdigit():
                        return await ctx.reply(f":x: | Invalid given ID: {id}")
                        
            if id in self.items['cheap_price_snipe'] or id in self.items['item_on_release_snipe']:
               return await ctx.reply(":grey_question: | ID is currently running.")
            if type.lower() == "release":
                self._config['items']['item_on_release_snipe'].append({
                    "id": id,
                    "max_price": None if max_price is None else int(max_price),
                    "max_buys": None if max_buys is None else int(max_buys)
                })
            elif type.lower() == "cheap":
                self._config['items']['cheap_price_snipe'].append({
                    "id": id,
                    "max_price": None if max_price is None else int(max_price),
                    "max_buys": None if max_buys is None else int(max_buys)
                })
                
            with open('config.json', 'w') as f:
                 json.dump(self._config, f, indent=4)
            
            if type.lower() == "release":
                self.items["item_on_release_snipe"][id] = {}
                self.items["item_on_release_snipe"][id]['current_buys'] = 0
                for item in self.config["items"]['item_on_release_snipe']:
                    if int(item['id']) == int(id):
                        item = item
                        break
                self.items["item_on_release_snipe"][id]['max_buys'] = float('inf') if item['max_buys'] is None else int(item['max_buys'])
                self.items["item_on_release_snipe"][id]['max_price'] = float('inf') if item['max_price'] is None else int(item['max_price'])
            elif type.lower() == "cheap":
                self.items["cheap_price_snipe"][id] = {}
                self.items["cheap_price_snipe"][id]['current_buys'] = 0
                for item in self.config["items"]['cheap_price_snipe']:
                    if int(item['id']) == int(id):
                        item = item
                        break
                self.items["cheap_price_snipe"][id]['max_buys'] = float('inf') if item['max_buys'] is None else int(item['max_buys'])
                self.items["cheap_price_snipe"][id]['max_price'] = float('inf') if item['max_price'] is None else int(item['max_price'])
                
            await ctx.reply(":white_check_mark: | ID successfully added!")
            logging.debug(f"added item id {id}")

        @bot.command(name="link")
        async def link(ctx, id=None, type=None):
            if id is None:
               return await ctx.reply(":warning: | You need to enter an ID or position to get!")

            if not id.isdigit():
                        return await ctx.reply(f":x: | Invalid given ID or position: {id}")

            if type is None or type.lower() not in ['release', "cheap"]:
                return await ctx.reply(":warning: | You need to enter a type! Ex: {prefix}link release or {prefix}link cheap")
             
            if id in self.items['cheap_price_snipe'] or self.items['item_on_release_snipe']:
                await ctx.reply(f"https://www.roblox.com/catalog/{id}")
            elif type.lower() == "cheap":
                if int(id) <= len(self.items['cheap_price_snipe']):
                    keys = list(self.items['cheap_price_snipe'].keys())
                    await ctx.reply(f"https://www.roblox.com/catalog/{keys[int(id) - 1]}")
            elif type.lower() == "release":
                if int(id) <= len(self.items["release"]):
                    keys = list(self.items["release"].keys())
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
            total = 0
            for i in lines:
                my_dict[str(total+1)] = {}
                my_dict[str(total+1)] = {"cookie": i}
            return my_dict
        
    def _load_items(self) -> list:
            item_on_release_snipe = {}
            cheap_price_snipe = {}
            for item in self.config["items"]['item_on_release_snipe']:
                item_on_release_snipe[item['id']] = {}
                item_on_release_snipe[item['id']]['current_buys'] = 0
                item_on_release_snipe[item['id']]['max_buys'] = float('inf') if item['max_buys'] is None else int(item['max_buys'])
                item_on_release_snipe[item['id']]['max_price'] = float('inf') if item['max_price'] is None else int(item['max_price'])
            for item in self.config["items"]['cheap_price_snipe']:
                cheap_price_snipe[item['id']] = {}
                cheap_price_snipe[item['id']]['current_buys'] = 0
                cheap_price_snipe[item['id']]['max_buys'] = float('inf') if item['max_buys'] is None else int(item['max_buys'])
                cheap_price_snipe[item['id']]['max_price'] = float('inf') if item['max_price'] is None else int(item['max_price'])
            return {"cheap_price_snipe": cheap_price_snipe, "item_on_release_snipe": item_on_release_snipe}
                 
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
         product_id: int, cookie: str, x_token: str, raw_id: str, bypass=False, method=None, collectibleItemInstanceId=None, url=None) -> None:
        
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
               "idempotencyKey": str(uuid.uuid4()),
               "collectibleProductId": product_id
         }
         raw_id = str(raw_id)
         total_errors = 0
         if raw_id in self.soldOut:
             self.totalTasks -= 1 
             return
         await asyncio.to_thread(logging.info, "New Buy Thread Started")
         async with aiohttp.ClientSession() as client: 
            while True:
                if not bypass:
                    if method == "release":
                        item = self.items["item_on_release_snipe"].get(raw_id, {})
                        max_buys = float(item.get('max_buys', 0))
                        current_buys = float(item.get('current_buys', 1))
                        if max_buys != 0 and not max_buys >= current_buys:
                            del self.items["item_on_release_snipe"][id]
                            for item in self.config['items']['item_on_release_snipe']:
                                if str(item['id']) == (raw_id):
                                    self.config["items"]['item_on_release_snipe'].remove(item)
                                    break

                            with open('config.json', 'w') as f:
                                json.dump(self.config, f, indent=4)
                                self.totalTasks -= 1
                                return
                            
                    elif method == "cheap":
                        item = self.items['cheap_price_snipe'].get(raw_id, {})
                        max_buys = float(item.get('max_buys', 0))
                        current_buys = float(item.get('current_buys', 1))
                        if max_buys != 0 and not max_buys >= current_buys:
                            del self.items['cheap_price_snipe'][id]
                            for item in self.config['items']['cheap_price_snipe']:
                                if str(item['id']) == (raw_id):
                                    self.config["items"]['cheap_price_snipe'].remove(item)
                                    break
                            with open('config.json', 'w') as f:
                                json.dump(self.config, f, indent=4)
                                self.totalTasks -= 1
                                return
                        data["collectibleItemInstanceId"] = collectibleItemInstanceId
                
                try:
                        async with client.post(url,
                                json=data,
                                headers={"x-csrf-token": x_token, 'Accept-Encoding': 'gzip'},
                                cookies={".ROBLOSECURITY": cookie}, ssl = False) as response:
                            await asyncio.to_thread(logging.info, f"{await response.json()}")
                            if response.status == 429:
                                print("Ratelimit encountered. Retrying purchase in 0.5 seconds...")
                                await asyncio.sleep(0.5)
                                continue
                            if total_errors >= 3:
                                print("Too many errors encountered. Aborting purchase.")
                                self.totalTasks -= 1
                                return
                            try:
                                json_response = await response.json()
                            except aiohttp.ContentTypeError as e:
                                self.errors += 1
                                print(f"JSON decode error encountered: {e}. Retrying purchase...")
                                await asyncio.to_thread(logging.error, f"JSON decode error encountered in buy process.")
                                total_errors += 1
                                continue
                  
                            if not json_response["purchased"]:
                                self.errors += 1
                                print(f"Purchase failed. Response: {json_response}. Retrying purchase...")
                                await asyncio.to_thread(logging.error, f"Purchase failed. Response: {json_response}.")
                                total_errors += 1
                                if json_response.get("errorMessage", 0) == "QuantityExhausted":
                                    self.soldOut.append(raw_id)
                                    self.totalTasks -= 1
                                    if method == "cheap":
                                        if raw_id in self.items['cheap_price_snipe']:
                                            del self.items['cheap_price_snipe'][raw_id]
                                    elif method == "release":
                                        if raw_id in self.items['item_on_release_snipe']:
                                            del self.items['item_on_release_snipe'][raw_id]
                                    return
                                elif json_response.get("errorMessage", 0) == "InsufficientBalance":
                                    self.soldOut.append(raw_id)
                                    self.totalTasks -= 1
                                    if method == "cheap":
                                        if raw_id in self.items['cheap_price_snipe']:
                                            del self.items['cheap_price_snipe'][raw_id]
                                    elif method == "release":
                                        if raw_id in self.items['item_on_release_snipe']:
                                            del self.items['item_on_release_snipe'][raw_id]
                                    return
                            else:
                                if method == "release":
                                    if raw_id in self.items['item_on_release_snipe']: self.items['item_on_release_snipe'][raw_id]['current_buys'] += 1
                                elif method == "cheap":
                                    if raw_id in self.items['cheap_price_snipe']: self.items['cheap_price_snipe'][raw_id]['current_buys'] += 1
                                
                                print(f"Purchase successful. Response: {json_response}.")
                                self.buys += 1
                                if self.webhookEnabled:
                                    embed_data = {
                                        "title": "New Item Purchased with Xolo Sniper",
                                        "url": f"https://www.roblox.com/catalog/{raw_id}/Xolo-Sniper",
                                        "color": 65280,
                                        "author": {
                                            "name": "Purchased limited successfully!"
                                        },
                                        "footer": {
                                            "text": "Xolo's Sniper"
                                        }
                                    }

                                    requests.post(self.webhookUrl, json={"content": None, "embeds": [embed_data]})
                        
                
                except aiohttp.ClientConnectorError as e:
                    self.errors += 1
                    print(f"Connection error encountered: {e}. Retrying purchase...")
                    total_errors += 1
                    continue
        
    async def search(self) -> None:
     async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=None), timeout=aiohttp.ClientTimeout(total=None)) as session:
      self.task = "Item Scraper & Searcher"
      cheap_price_snipe_items = self.items['cheap_price_snipe'].copy()
      item_on_release_snipe_items = self.items['item_on_release_snipe'].copy()
      while True:
        try:
                    cycler = cycle(list(cheap_price_snipe_items.keys()) + list(item_on_release_snipe_items.keys()))
                    if self.config['proxy']['enabled'] and len(self.proxies) > 0:
                        proxy = f"http://{await self.proxy_handler.newprox()}"
                    else:
                        proxy = None
                    t0 = asyncio.get_event_loop().time()
                    for id in list(cheap_price_snipe_items.keys()) + list(item_on_release_snipe_items.keys()):
                        if not id.isdigit():
                           if id in cheap_price_snipe_items: del cheap_price_snipe_items[id]; del self.item["cheap_price_snipe"][id]
                           elif id in item_on_release_snipe_items: del item_on_release_snipe_items[id]; del self.item["item_on_release_snipe"][id]
                    
                            
                    combined_dict = {}
                    combined_dict |= cheap_price_snipe_items
                    combined_dict |= item_on_release_snipe_items
                    items = {k: combined_dict[k] for k in islice(cycler, 120)}
                               
                    currentAccount = self.accounts["1"]
                    async with session.post("https://catalog.roblox.com/v1/catalog/items/details",
                                           json={"items": [{"itemType": "Asset", "id": id} for id in items]},
                                           headers={"x-csrf-token": currentAccount['xcsrf_token'], 'Accept-Encoding': 'gzip'},
                                           cookies={".ROBLOSECURITY": currentAccount["cookie"]}, ssl=False, proxy=proxy, timeout=self.timeout, proxy_auth = self.proxy_auth) as response:
                        response.raise_for_status()
                        json_response = (await response.json())['data']
                        for i in json_response:
                         creator = None
                         price = None
                         productid_data = None
                         collectibleItemId = i.get("collectibleItemId")
                         collectibleItemInstanceId = None
                         location = None
                         item_id = str(i.get("id"))
                         cheap_price_snipe_item = cheap_price_snipe_items.get(item_id)
                         if not cheap_price_snipe_item:
                            location = "item_on_release_snipe"
                            if int(i.get("price", 0)) > item_on_release_snipe_items[item_id]['max_price']:
                                del self.items['item_on_release_snipe'][item_id]
                                del item_on_release_snipe_items[item_id] 
                                continue
                            if not (i.get("priceStatus") != "Off Sale" and i.get('unitsAvailableForConsumption', 0) > 0):
                                if i.get('unitsAvailableForConsumption', 1) == 0:
                                    del self.items['item_on_release_snipe'][item_id]; del item_on_release_snipe_items[item_id] 
                                continue
                            if int(i.get("quantityLimitPerUser", 0)) != 0:
                                self.items['item_on_release_snipe'][item_id]["max_buys"] = int(i.get("quantityLimitPerUser", 0)); item_on_release_snipe_items[item_id]["max_buys"] = int(i.get("quantityLimitPerUser", 0))
                                
                            creator = i['creatorTargetId']
                            price = i['price']
                         else:
                            location = 'cheap_price_snipe'
                            if not i.get("hasResellers") or i.get("lowestResalePrice") >= cheap_price_snipe_items[item_id]['max_price']:
                                continue
                            else:
                                async with await session.get(f"https://apis.roblox.com/marketplace-sales/v1/item/{i['collectibleItemId']}/resellers?limit=1",
                                                                     headers={"x-csrf-token": currentAccount["xcsrf_token"], 'Accept': "application/json", 'Accept-Encoding': 'gzip'},
                                                                     cookies={".ROBLOSECURITY": currentAccount["cookie"]}, ssl=False) as resell:
                                    rps = (await resell.json())["data"][0]
                                    productid_data = rps["collectibleProductId"]
                                    creator = rps["seller"]["sellerId"]
                                    price = i['lowestResalePrice']
                                    collectibleItemInstanceId = rps["collectibleItemInstanceId"]
                         if i["saleLocationType"] == 'ExperiencesDevApiOnly':
                            # SINCE ROBLOX DOES NOT HAVE IT CURRENTLY ENABLED THIS WON'T WORK YET / beta
                            del self.items[location][str(i['id'])]
                            continue
                        
                            # if roblox decides to turn it online we will scrape the game id
                            async with await session.get(f"https://economy.roblox.com/v2/assets/{i['id']}/details", cookies={".ROBLOSECURITY": currentAccount["cookie"]}, ssl=False) as first:
                                first.raise_for_status()
                                if not ((first.json())["SaleLocation"] is None or len((first.json())["SaleLocation"].get("UniverseIds", [])) == 0):
                                    universe_ids = (first.json())['SaleLocation'].get('UniverseIds', [])
                                    async with await session.get(f"https://games.roblox.com/v1/games?universeIds={','.join(str(id) for id in universe_ids)}", cookies={".ROBLOSECURITY": currentAccount["cookie"]}, ssl=False) as second:
                                        second.raise_for_status()
                                        game_list = []
                                        for current in (second.json())["data"]:
                                            game_list.append(current['rootPlaceId'])
                                        
                                        # we now have a list of games linked to it.
                                        
                         if not productid_data:
                            async with await session.post("https://apis.roblox.com/marketplace-items/v1/items/details",
                                                                     json={"itemIds": [collectibleItemId]},
                                                                     headers={"x-csrf-token": currentAccount["xcsrf_token"], 'Accept': "application/json", 'Accept-Encoding': 'gzip'},
                                                                     cookies={".ROBLOSECURITY": currentAccount["cookie"]}, ssl=False) as productid_response:
                                productid_response.raise_for_status()
                                productid_data = (await productid_response.json())[0]['collectibleProductId']
                         self.totalTasks += 1
                         if item_id not in cheap_price_snipe_items:
                             coroutines = [self.buy_item(item_id=collectibleItemId, price=price, user_id=self.accounts[o]['id'], creator_id=creator, product_id=productid_data, cookie=self.accounts[o]['cookie'], x_token=self.accounts[o]['xcsrf_token'], raw_id=i.get('id'), method='release', bypass=True, url=f"https://apis.roblox.com/marketplace-sales/v1/item/{collectibleItemId}/purchase-item") for o in (range(1, len(self.accounts)) if len(self.accounts) > 1 else self.accounts)]  
                         else:
                             coroutines = [self.buy_item(item_id = collectibleItemId, price = price, user_id = self.accounts[o]["id"], creator_id = creator, product_id = productid_data, cookie = self.accounts[o]["cookie"], x_token = self.accounts[o]["xcsrf_token"], raw_id = i.get("id"), method="cheap", collectibleItemInstanceId=collectibleItemInstanceId, location="cheap_price_snipe", url=f"https://apis.roblox.com/marketplace-sales/v1/item/{collectibleItemId}/purchase-resale") for o in (range(1, len(self.accounts)) if len(self.accounts) > 1 else self.accounts)]
                         self.task = "Item Buyer"
                         await asyncio.gather(*coroutines)
                         self.task = "Item Scraper & Searcher"
                                
                    t1 = asyncio.get_event_loop().time()
                    self.last_time = round(t1 - t0, 3)
        except aiohttp.ClientConnectorError as e:
            print(f'Connection error: {e}')
            self.errors += 1
        except AssertionError as e:
            continue
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
        except aiohttp.ServerDisconnectedError:
            return
        finally:
            self.checks += len(items)
            cheap_price_snipe_items = self.items['cheap_price_snipe'].copy()
            item_on_release_snipe_items = self.items['item_on_release_snipe'].copy()
            await asyncio.sleep(1)
            
                               
    async def given_id_sniper(self) -> None:
     self.task = "Item Scraper & Searcher"
     try: 
         await self.search()
     except aiohttp.ServerDisconnectedError: return
                  
    async def start(self):
            await asyncio.to_thread(logging.info, "Started sniping")
            coroutines = []
            if self.rooms:
                while True:
                 try:
                    await sio.connect("https://webserver--xolobang.repl.co/:8080")
                    break
                 except: print("Couldn't connect to server. Reconncting..."); await asyncio.to_thread(logging.error, "Couldn't connect to site. Retrying...")
                while True:
                    try: 
                        req = requests.post("https://webserver--xolobang.repl.co/items")
                        formatted = req.json()
                        for key, value in formatted.items():
                            if key not in self.items:
                                self.items['item_on_release_snipe'][key] = value
                        break
                    except: print("Couldn't scrape item ids from site. Retrying..."); await asyncio.to_thread(logging.error, "couldn't scrape item ids from site. Retrying...")
                    
                
            coroutines.append(self.given_id_sniper())
                
            coroutines.append(self.auto_update())
            coroutines.append(self.auto_xtoken())
            await asyncio.gather(*coroutines)
    
    async def auto_xtoken(self):
        while True:
            await asyncio.sleep(5)
            assert await self._check_xcsrf_token(), "x_csrf_token couldn't be generated"
            
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
