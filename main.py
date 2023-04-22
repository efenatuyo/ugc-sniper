# made by xolo#4942
# version 7.0.0

try:
  import datetime
  import sys
  import os
  import uuid
  import asyncio
  import random
  import requests
  import subprocess
  from colorama import Fore, Back, Style
  import aiohttp
  import json
  import time

class Sniper:
    def __init__(self) -> None:
        self.accounts = None
        self.items = self._load_items()
        self.checks = 0
        self.buys = 0
        self.request_method = 2
        self.last_time = 0
        self.errors = 0
        self.total_error = 0
        self.total_ratelimits = 0
        self.notfound = 0
        self.JSON = 0
        self.failed = 0
        self.tokeninvalid = 0
        self.clear = "cls" if os.name == 'nt' else "clear"
        self.version = "7.1.0 - Edited by Darkvsx#5191"
        self.task = None
        self._setup_accounts()
        asyncio.run(self.start())
        
        
    def _print_stats(self) -> None:
        print(f"                           Version: {self.version}")
        print(Fore.RESET + Style.RESET_ALL)
        print(f"                             {Fore.CYAN}{Style.BRIGHT}STATS{Fore.WHITE}{Style.BRIGHT}   ")
        print(Style.BRIGHT + f"                             Success: {Fore.GREEN}{Style.BRIGHT}{self.buys}{Fore.WHITE}{Style.BRIGHT} ")
        print(Style.BRIGHT + f"                             Failure: {Fore.RED}{Style.BRIGHT}{self.failed}{Fore.WHITE}{Style.BRIGHT} ")
        print(Fore.RESET + Style.RESET_ALL)
        print(f"                             {Fore.YELLOW}{Style.BRIGHT}MISC{Fore.WHITE}{Style.BRIGHT}   ")
        print(Style.BRIGHT + f"                             Speed: {Fore.YELLOW}{Style.BRIGHT}{self.last_time}{Fore.WHITE}{Style.BRIGHT} ")
        print(Style.BRIGHT + f"                             Checks: {Fore.YELLOW}{Style.BRIGHT}{self.checks}{Fore.WHITE}{Style.BRIGHT} ")
        print(Fore.RESET + Style.RESET_ALL)
        print(f"                             {Fore.RED}{Style.BRIGHT}ERRORS{Fore.WHITE}{Style.BRIGHT}    ")
        print(Style.BRIGHT + f"                             RateLimits: {Fore.RED}{Style.BRIGHT}{self.total_ratelimits}{Fore.WHITE}{Style.BRIGHT} ")
        print(Style.BRIGHT + f"                             Invalid ID: {Fore.RED}{Style.BRIGHT}{self.notfound}{Fore.WHITE}{Style.BRIGHT} ")
        print(Style.BRIGHT + f"                             Invalid Token: {Fore.YELLOW}{Style.BRIGHT}{self.tokeninvalid}{Fore.WHITE}{Style.BRIGHT} ")
        print(Style.BRIGHT + f"                             Json: {Fore.YELLOW}{Style.BRIGHT}{self.JSON}{Fore.WHITE}{Style.BRIGHT} ")
        print(Style.BRIGHT + f"                             Aiohttp: {Fore.YELLOW}{Style.BRIGHT}{self.errors}{Fore.WHITE}{Style.BRIGHT} ")
        print(Style.BRIGHT + f"                             SOMETHING: {Fore.YELLOW}{Style.BRIGHT}{self.total_error}{Fore.WHITE}{Style.BRIGHT} ")
        print()
        print(Style.BRIGHT + f"                             Current Task: {Fore.GREEN}{Style.BRIGHT}{self.task}{Fore.WHITE}{Style.BRIGHT} ")
        
        
    class DotDict(dict):
        def __getattr__(self, attr):
            return self[attr]
            
            
    class TokenBucket:
        def __init__(self, capacity, refill_rate):
            self.capacity = capacity
            self.refill_rate = refill_rate
            self.tokens = capacity
            self.last_refill_time = time.monotonic()
    
        def consume(self, tokens):
            current_time = time.monotonic()
            elapsed_time = current_time - self.last_refill_time
            self.tokens = min(self.capacity, self.tokens + elapsed_time * self.refill_rate)
            if tokens > self.tokens:
                return False
            else:
                self.tokens -= tokens
                return True
    
    def _setup_accounts(self) -> None:
        self.task = "Account Loader"
        self._print_stats()
        cookies = self._load_cookies()
        for i in cookies:
              response = asyncio.run(self._get_user_id(cookies[i]["cookie"]))
              response2 = asyncio.run(self._get_xcsrf_token(cookies[i]["cookie"]))
              cookies[i]["id"] = response
              cookies[i]["xcsrf_token"] = response2["xcsrf_token"]
              cookies[i]["created"] = response2["created"]
        self.accounts = cookies
        
    def _load_cookies(self) -> dict:
        with open("cookie.txt") as file:
            my_dict = {}
            for i, line in enumerate(file):
                my_dict[str(i+1)] = {"cookie": line.rstrip()}
            return my_dict
        
    def _load_items(self) -> list:
        with open('limiteds.txt') as f:
            return [line.rstrip() for line in f]
                 
    async def _get_user_id(self, cookie) -> str:
        async with aiohttp.ClientSession(cookies={".ROBLOSECURITY": cookie}) as client:
            data = await (await client.get("https://users.roblox.com/v1/users/authenticated")).json()
            if data.get('id') == None:
                raise Exception("Couldn't scrape user id. Error:", data)
        return data.get('id')

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
            else:
                return True
        return False

     
    async def buy_item(self, item_id: int, price: int, user_id: int, creator_id: int,
         product_id: int, cookie: str, x_token: str) -> None:       
        
         data = {
               "collectibleItemId": item_id,
               "expectedCurrency": 1,
               "expectedPrice": 0,
               "expectedPurchaserId": user_id,
               "expectedPurchaserType": "User",
               "expectedSellerId": creator_id,
               "expectedSellerType": "User",
               "idempotencyKey": "random uuid4 string that will be your key or smthn",
               "collectibleProductId": product_id
         }

         async with aiohttp.ClientSession() as client:   
            while True:
                if self.total_error >= 150:
                    print("Too many errors encountered. Restarting.")
                    python = sys.executable
                    os.execl(python, python, *sys.argv)
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
                    self.total_error += 1
                    await asyncio.sleep(0.75)
                    continue
                    
                if response.status == 429:
                       self.total_error += 1
                       print("Ratelimit encountered. Retrying purchase in 0.75 seconds...")
                       self.total_ratelimits += 1
                       await asyncio.sleep(0.75)
                       continue
            
                try:
                      json_response = await response.json()
                except aiohttp.ContentTypeError as e:
                      self.JSON += 1
                      print(f"JSON decode error encountered: {e}. Retrying purchase...")
                      self.total_error += 1
                      await asyncio.sleep(0.75)
                      continue
                  
                if not json_response["purchased"]:
                       self.failed += 1
                       print(f"Purchase failed. Response: {json_response}. Retrying purchase...")
                       self.total_error += 1
                       await asyncio.sleep(0.75)
                else:
                       print(f"Purchase successful. Response: {json_response}.")
                       self.buys += 1        
                    
    async def given_id_sniper(self) -> None:
        check_bucket = TokenBucket(capacity=10, refill_rate=1)
        buy_bucket = TokenBucket(capacity=50, refill_rate=1)
    
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=None)) as session:
            while True:
                try:
                    self.task = "Checking"
                    t0 = asyncio.get_event_loop().time()
                
                    for currentItem in self.items:
                        if not currentItem.isdigit():
                            raise Exception(f"Invalid item id given ID: {currentItem}")
                    
                        if not check_bucket.consume(1):
                            print("Checking bucket is empty, waiting...")
                            await asyncio.sleep(1)
                            continue
                    
                        currentAccount = self.accounts[str(random.randint(1, len(self.accounts)))]
                        async with session.post("https://catalog.roblox.com/v1/catalog/items/details",
                                            json={"items": [{"itemType": "Asset", "id": int(currentItem)}]},
                                            headers={"x-csrf-token": currentAccount['xcsrf_token'], 'Accept': "application/json"},
                                            cookies={".ROBLOSECURITY": currentAccount["cookie"]}, ssl=False) as response:

                            response.raise_for_status()
                            response_text = await response.text()
                            json_response = json.loads(response_text)['data'][0]
                            if json_response.get("priceStatus") != "Off Sale" and 0 if json_response.get('unitsAvailableForConsumption') is None else json_response.get('unitsAvailableForConsumption') > 0:
                                productid_response = await session.post("https://apis.roblox.com/marketplace-items/v1/items/details",
                                                                        json={"itemIds": [json_response["collectibleItemId"]]},
                                                                        headers={"x-csrf-token": currentAccount["xcsrf_token"], 'Accept': "application/json"},
                                                                        cookies={".ROBLOSECURITY": currentAccount["cookie"]}, ssl=False)
                                response.raise_for_status()
                                productid_data = json.loads(await productid_response.text())[0]
                            
                                if not buy_bucket.consume(1):
                                    print("Buying bucket is empty, waiting...")
                                    await asyncio.sleep(1)
                                    continue
                            
                                coroutines = [self.buy_item(item_id = json_response["collectibleItemId"], price = json_response['price'], user_id = self.accounts[i]["id"], creator_id = json_response['creatorTargetId'], product_id = productid_data['collectibleProductId'], cookie = self.accounts[i]["cookie"], x_token = self.accounts[i]["xcsrf_token"]) for i in self.accounts]
                                self.task = "Buying"
                                await asyncio.gather(*coroutines)
                        t1 = asyncio.get_event_loop().time()
                        self.last_time = round(t1 - t0, 3)
             except aiohttp.ClientConnectorError as e:
                print(f'Connection error: {e}')
                self.errors += 1
             except aiohttp.ContentTypeError as e:
                print(f'Content type error: {e}')
                self.errors += 1
             except aiohttp.ClientResponseError as e:
                print(f'Response error: {e}')
                self.errors += 1
             except aiohttp.client_exceptions.ClientResponseError as e:
                print(f"Response Error: {e}")
             finally:
                self.checks += 1
                await asyncio.sleep(1)

    
    async def start(self):
            coroutines = []
            coroutines.append(self.given_id_sniper())
            coroutines.append(self.auto_update())
            await asyncio.gather(*coroutines)
    
    async def auto_update(self):
        while True:
            if not await self._check_xcsrf_token():
                raise Exception("x_csrf_token couldn't be generated")
            subprocess.call('cls' if os.name == 'nt' else 'clear', shell=True)
            self._print_stats()
            await asyncio.sleep(2)
        
sniper = Sniper()
sniper

