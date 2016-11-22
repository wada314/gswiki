#!/usr/bin/python2
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import time

# Create DO_NOT_COMMIT_sqex_passwords.py in the same directory, and write:
# SQEX_USERNAME='<your username>'
# SQEX_PASSWORD='<your password>'
from DO_NOT_COMMIT_sqex_passwords import SQEX_USERNAME, SQEX_PASSWORD

### Please change here to YOUR value!!
SELENIUM_REMOTE_URL = 'http://10.20.40.10:4444/wd/hub'


driver = webdriver.Remote(command_executor=SELENIUM_REMOTE_URL,
                          desired_capabilities=DesiredCapabilities.CHROME)
driver.implicitly_wait(1)

driver.get('http://sp3.gunslinger-stratos.net/')
driver.find_element_by_css_selector('main .jump img').click()

time.sleep(3.0)

driver.find_element_by_name('sqexid').send_keys(SQEX_USERNAME)
driver.find_element_by_name('password').send_keys(SQEX_PASSWORD)
driver.find_element_by_name('password').submit()

time.sleep(3.0)
#driver.find_element_by_css_selector('.orange').click()
driver.find_element_by_css_selector('div[data-url="player/player_top.html"]').click()

driver.get('http://sp3.gunslinger-stratos.net/page/chara/chara_select.html')
chara_num = len(driver.find_elements_by_css_selector('#chara-list-select>li'))
chara_ids = [i for i in range(1, 23)] + [24, 26, 27, 28, 29]
#print chara_ids
assert(len(chara_ids) == chara_num)

for i in chara_ids:
    time.sleep(1)
    driver.get('http://sp3.gunslinger-stratos.net/page/chara/weapon/weapon_pack_list.html?chara_type=%d' % i)
    wps1 = driver.execute_script('return JSON.stringify(weapon_pack_list)')

    time.sleep(1)
    driver.get('http://sp3.gunslinger-stratos.net/page/shop/weapon_sale_top.html?chara_type=%d' % i)
    wps2 = driver.execute_script('return JSON.stringify(weapon_pack_list)')

    print wps1.encode('utf-8')
    print wps2.encode('utf-8')
