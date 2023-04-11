import datetime
import json
import os
import requests
import time
import uuid


class Sniper:
    def __init__(self) -> None:
        self.cookie = self._load_cookie()
        self.items = self._load_items()
        self.xcsrf_token = None
        self.title = "Xolo Sniper"
        self.checks = 0
        self.buys = 0
        self.user_id = self._get_user_id()
        self.request_method = 2
        self.total_ratelimits = 0
        self.last_time = 0
    
    class DotDict(dict):
        def __getattr__(self, attr):
            return self[attr]
       
    def _load_cookie(self) -> str:
        with open("cookie.txt", "r") as file:
            return file.read()
        
    def _load_items(self) -> list[str]:
        with open('limiteds.txt', 'r') as f:
            return [line.strip() for line in f.readlines()]
            
    def _get_user_id(self) -> str:
        response = requests.get(
            "https://users.roblox.com/v1/users/authenticated",
            cookies={".ROBLOSECURITY": self.cookie}
        )
        return response.json()["id"]
    
    def _print_stats(self) -> None:
        print(self.title)
        print(f"Total buys: {self.buys}")
        print(f"Total ratelimits: {self.total_ratelimits}")
        print(f"Total price checks: {self.checks}")
        print(f"Last Speed: {self.last_time}")
            
    def _get_xcsrf_token(self) -> None:
        response = requests.post(
            "https://auth.roblox.com/v2/logout",
            cookies={".ROBLOSECURITY": self.cookie}
        )
        xcsrf_token = response.headers.get("x-csrf-token")
        if xcsrf_token is None:
            raise Exception("An error occurred while getting the X-CSRF-TOKEN. "
                            "Could be due to an invalid Roblox Cookie")
        self.xcsrf_token = Sniper.DotDict({"xcsrf_token": xcsrf_token,
                                           "created": datetime.datetime.now()})
    
    def _check_xcsrf_token(self) -> bool:
        if self.xcsrf_token is None or \
                datetime.datetime.now() > (self.xcsrf_token.created + datetime.timedelta(minutes=4)):
            try:
                self._get_xcsrf_token()
            except Exception as e:
                print(f"{e.__class__.__name__}: {e}")
                return False
        return True
    
    def start(self) -> None:
        def buy_item(item_id: int, price: int, user_id: int, creator_id: int,
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
            
            print("Initiating purchase of limited item...")
            
            
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
            while True:
                 if total_errors >= 10:
                     print("Too many errors encountered. Aborting purchase.")
                     return
                 
                 data["idempotencyKey"] = str(uuid.uuid4())
                 response = requests.post(f"https://apis.roblox.com/marketplace-sales/v1/item/{item_id}/purchase-item",
                                          json=data,
                                          headers={"x-csrf-token": x_token},
                                          cookies={".ROBLOSECURITY": cookie})

                 if response.status_code == 429:
                    print("Ratelimit encountered. Retrying purchase in 0.5 seconds...")
                    time.sleep(0.5)
                    continue
                
                 try:
                   json_response = response.json()
                 except json.decoder.JSONDecodeError as e:
                   print(f"JSON decode error encountered: {e}. Retrying purchase...")
                   total_errors += 1
                   continue

                 if not json_response["purchased"]:
                    print(f"Purchase failed. Response: {json_response}. Retrying purchase...")
                    total_errors += 1
                 else:
                   print(f"Purchase successful. Response: {json_response}.")
                   self.buys += 1
            
        while True:
            t0 = time.time()
            os.system('cls')
            self._print_stats()
            
            if not self._check_xcsrf_token():
                raise Exception("x_csrf_token couldn't be generated")
            

            for currentItem in self.items:
                if self.request_method == 1:
                   response = requests.get(f"https://economy.roblox.com/v2/assets/{currentItem}/details")
                else:
                   response = requests.post("https://catalog.roblox.com/v1/catalog/items/details", json={"items": [{"itemType": "Asset", "id": int(currentItem)}]}, headers={"x-csrf-token": self.xcsrf_token.xcsrf_token}, cookies={".ROBLOSECURITY": self.cookie})
                   self.checks += 1
                
                
                if response.status_code != 200:
                    print("Rate limit hit")
                    self.total_ratelimits += 1
                    time.sleep(30)
                    continue
                if "price" in response.json()["data"][0]:
                       productid = requests.post("https://apis.roblox.com/marketplace-items/v1/items/details", json={"itemIds": [response.json()["data"][0]["collectibleItemId"]]}, headers={"x-csrf-token": self.xcsrf_token.xcsrf_token}, cookies={".ROBLOSECURITY": self.cookie})
                       buy_item(item_id = response.json()["data"][0]["collectibleItemId"], price = response.json()["data"][0]['price'], user_id = self.user_id, creator_id = response.json()["data"][0]['creatorTargetId'], product_id = productid.json()[0]["collectibleProductId"], cookie = self.cookie, x_token = self.xcsrf_token.xcsrf_token)
                       time.sleep(1)
                t1 = time.time()
                self.last_time = t1 - t0
                time.sleep(1.5)
Sniper().start()
