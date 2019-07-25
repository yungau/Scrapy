# -*- coding: utf-8 -*-
"""
Run the script in the terminal: python linkhkSpider.py xxxx
where xxxx can only be shop or dine
"""
# -*- coding: utf-8 -*-
#encoding=utf-8
import time
import sys
import requests
import pandas as pd


class linkhkSpider:
    def __init__(self, sys_arg):
        self.sys_arg = sys_arg
        self.items = {}
        self.headers = {
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Encoding': 'br, gzip, deflate',
                        'Host': 'www.linkhk.com',
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.2 Safari/605.1.15',
                        'Accept-Language': 'en-us',
                        'DNT': '1',
                        'Connection': 'keep-alive',
                    }
        Type = {'shop': 1, 'dine': 2}
        api_url = 'http://www.linkhk.com/linkweb/api/shop/?categoryId=&districtId=&shopCentreId=&pageType={}&pageSize=10&pageNo={}'
        self.api_url = api_url.format(Type.get(sys_arg, 1), {})
        self.shop_url = 'http://www.linkhk.com/linkweb/api/shop/{}'


    def getItems(self, page):
        print('page:', page)
        response = requests.get(self.api_url.format(page), headers=self.headers)
        data = response.json()
        shops = data['data']['shopList']
        shopIds = [shop.get('shopId') for shop in shops]
        shopNamesEn = [shop.get('shopNameEn', '').strip() for shop in shops]
        shopNamesTc = [shop.get('shopNameTc', '').strip() for shop in shops]
        shopCetreNamesEn = [shop.get('shopCentreNameEn', '').strip() for shop in shops]
        shopCetreNamesTc = [shop.get('shopCentreNameTc', '').strip() for shop in shops]
        shopNos = [shop.get('shopNo', '').strip() for shop in shops]
        
        zipInfo = list(zip(shopIds, shopNamesTc, shopNamesEn, shopCetreNamesTc, shopCetreNamesEn, shopNos))
        zipInfo = [list(tup) for tup in zipInfo]
        zipInfo = {info[0]: info[1::] for info in zipInfo}
        self.items.update(zipInfo)
        
        curPage = data['data']['pageInfo']['curPage']
        totalPages = data['data']['pageInfo']['pageCount']
        
        return curPage, totalPages
        
    def crawlPages(self):
        page = 0
        while 1:
            curPage, totalPages = self.getItems(page)
            if curPage >= totalPages:
                break
            page += 1
    
    def getItemDetails(self, shopId):
        response = requests.get(self.shop_url.format(shopId), headers=self.headers)
        data_details = response.json()
        shop_details = data_details['data']['shopInfo']
        
        address_tc = shop_details.get('locationTc')
        address_en = shop_details.get('locationEn')
        shop_type_tc = shop_details.get('shopTypeTextTc')
        shop_type_en = shop_details.get('shopTypeTextEn')
        opening_hours = shop_details.get('openingHoursEn')
        telephone = shop_details.get('telephone')
        return address_tc, address_en, shop_type_tc, shop_type_en, opening_hours, telephone
        
    def getItemsDetails(self):
        shopIds = list(self.items.keys())
        for shopId in shopIds:
            print('progress: {}/{}'.format(shopIds.index(shopId)+1, len(shopIds)))
            address_tc, address_en, shop_type_tc, shop_type_en, opening_hours, telephone = self.getItemDetails(shopId)
            self.items[shopId] += [address_tc, address_en, shop_type_tc, shop_type_en, opening_hours, telephone]
            if shopIds.index(shopId) % 100 == 0:
                self.save_csv(self.items)
        self.save_csv(self.items)
            
    def save_csv(self, items):
        columns = ['shop_name_tc',
                   'shop_name_en',
                   'centre_name_tc',
                   'centre_name_en',
                   'shop_number',
                   'address_tc',
                   'address_en',
                   'shop_type_tc',
                   'shop_type_en',
                   'opening_hours',
                   'telephone',
                   ]
        df = pd.DataFrame.from_dict(items, orient='index', columns=columns)
        df = df.reset_index().rename(columns={'index': 'shop_id'})
        df.to_csv(str(pd.datetime.now().date()).replace('-', '')+'_{}.csv'.format(self.sys_arg))

def main():
    time_start = time.time()
    try:
       sys_arg = sys.argv[1]
    except:
        sys_arg = 'dine'                   
    spider = linkhkSpider(sys_arg) 
    spider.crawlPages()
    spider.getItemsDetails()
    time_end = time.time() - time_start
    print('Execution time: {} minutes'.format(time_end/60))

if __name__ == "__main__":
    main()