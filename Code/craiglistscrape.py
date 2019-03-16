import pandas as pd
from pandas import ExcelWriter
import html5lib
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import winsound
import time

class craiglistscrape:
    def __init__(self, starting_url):
        self.starting_url = starting_url
        self.browser = webdriver.Chrome("C:/Users/mting/Documents/chromedriver.exe", chrome_options=self.set_options())
        self.writer = pd.ExcelWriter('rentexport.xlsx')

    def set_options(self):
        path_to_extension = "C:/Users/mting/Desktop/3.31.2_0"
        chrome_options = Options()
        chrome_options.add_argument('load-extension=' + path_to_extension)
        return(chrome_options)

    def gethomeinfo(self):
        self.browser.create_options()
        self.browser.get(self.starting_url)
        df = pd.DataFrame(columns = ["price", "sqrtft", "bed", "bath", "type", "lng", "lat", "x", "y"])
        cont = 'y'
        observation = 0 
        while(cont == 'y'):
            for index in range(len(self.browser.find_elements_by_xpath("//li[@class='result-row']"))):
                price = self.browser.find_elements_by_xpath("//li[@class='result-row']")[index].text
                price = price.splitlines()[0]
                if(len(price) > 6):
                    try:
                        start = price.index("$")
                        end = price[start:].index(" ")
                        price = float(price[start+1:start + end])
                    except ValueError: 
                        price = -1
                else:
                    price = float(price[1:]) 
                try:
                    self.browser.find_elements_by_xpath("//a[@class='result-title hdrlnk']")[index].click()
                    map_att = self.browser.find_element_by_xpath("//div[@class='mapbox']")
                    lat = float(map_att.find_element_by_css_selector("div").get_attribute('data-latitude'))
                    lng = float(map_att.find_element_by_css_selector("div").get_attribute('data-longitude'))
                    attributes = self.browser.find_elements_by_xpath("//p[@class='attrgroup']")[0].text.lower().split()
                    bedrooms = -1
                    bathrooms = -1 
                    sqrft = -1 
                    for item in attributes:
                        if 'br' in item: 
                            bedrooms = float(item[:-2])
                        elif "ba" in item: 
                            bathrooms = float(item[:-2])
                        elif "ft2" in item: 
                            sqrft = float(item[:-3]) 
                    try:
                        double_check = self.browser.find_elements_by_xpath("//p[@class='attrgroup']")[1].text.lower().split()
                        for rent_type in double_check:
                            if 'duplex' in rent_type: 
                                rent_type = 'duplex'
                                break
                            elif 'condo' in rent_type:
                                rent_type = 'condo'
                                break
                            elif 'townhouse' in rent_type: 
                                rent_type = 'townhouse'
                            elif 'house' in rent_type or 'home' in rent_type:
                                rent_type = 'house'
                                break
                            elif 'apartment' in rent_type:
                                rent_type = 'apartment'
                                break
                            else:
                                rent_type = self.browser.find_element_by_xpath("//section[@id='postingbody']").text.lower()
                                if 'duplex' in rent_type: 
                                    rent_type = 'duplex'
                                elif 'condo' in rent_type:
                                    rent_type = 'condo'
                                elif 'townhouse' in rent_type: 
                                    rent_type = 'townhouse'
                                elif 'house' in rent_type or 'home' in rent_type:
                                    rent_type = 'house'
                                elif 'apartment' in rent_type:
                                    rent_type = 'apartment'
                                else:
                                   rent_type = 'n'
                    except IndexError:
                        rent_type = 'n'
                    if bedrooms > 0 and bathrooms > 0 and sqrft > 0 and price > 0 and rent_type != 'n': 
                        df.loc[observation] = [price, sqrft, bedrooms, bathrooms, rent_type, lng, lat, round(lng+117.323330, 7), round(lat-32.531890, 7)]
                        observation = observation + 1 
                        print("{}".format(observation))
                except NoSuchElementException:
                    pass
                except ValueError:
                    pass
                finally: 
                    self.browser.execute_script("window.history.go(-1)")
            winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
            print("One more page? y/n")
            cont = input().lower()
        df.to_excel(self.writer)
        self.writer.save()

test = craiglistscrape("https://sandiego.craigslist.org/d/apts-housing-for-rent/search/apa")
test.gethomeinfo()