import time

from steampy.client import SteamClient, Asset
from steampy.utils import GameOptions
import json


class BotTrade:
    def __init__(self, col):
        self.user = col['username']
        self.psw = col['password']
        self.apikey = col['dev_key']
        self.guard_info = {
            "steamid": str(col['SteamID']),
            "shared_secret": col['configs']['shared_secret'],
            "identity_secret": col['configs']['identity_secret'],
        }
        self.steam_client = SteamClient(self.apikey)
        self.steam_client.login(self.user, self.psw, json.dumps(self.guard_info))

    def send_all_items(self, trade_url, max_for_offer=300):
        my_asset_list = self.get_all_tradable_assetid()
        offer_id_list = []
        while my_asset_list:
            send_asset_list = my_asset_list[:max_for_offer]
            del my_asset_list[:max_for_offer]
            resp_dict = self.steam_client.make_offer_with_url(send_asset_list, [], trade_url, '')
            print(resp_dict)
            offer_id_list.append(resp_dict['tradeofferid'])
            time.sleep(10)
        return offer_id_list

    def send_all_items_to_many(self, trade_url_list):
        result = []
        my_asset_list = self.get_all_tradable_assetid()
        count = len(my_asset_list) // len(trade_url_list)  # 整除
        for index, value in enumerate(trade_url_list):
            if index == len(trade_url_list) - 1:
                data = my_asset_list[count * index:]
            else:
                data = my_asset_list[count * index:count * (index + 1)]
            resp_dict = self.steam_client.make_offer_with_url(data, [], value, '')
            result.append((value, resp_dict['tradeofferid']))
        return result

    def accept(self, trade_offer_id):
        resp = self.steam_client.accept_trade_offer(trade_offer_id)
        print('Accept trade', resp)
        if 'tradeid' in resp:
            return True
        return False

    def get_all_tradable_assetid(self):
        game = GameOptions.DOTA2
        my_items = self.steam_client.get_my_inventory_by_eshao(game)
        my_asset_list = []
        for i in my_items:
            if i['tradable'] == 1:
                my_asset_list.append(Asset(i['assetid'], game))
        return my_asset_list
