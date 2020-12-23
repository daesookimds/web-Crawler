import re
import os
import pandas as pd
from tqdm import tqdm
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver

def set_driver(driver_path='chromedriver', download_folder=os.getcwd(), url='about:blank') :

    option = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": download_folder,
        "profile.managed_default_content_settings.images": 2
    }
    option.add_experimental_option("prefs", prefs)
    option.add_argument("--log-level=3")
    option.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
    option.add_argument("lang=ko_KR")
    # option.add_argument('--headless')
    option.add_argument('--no-sandbox')
    option.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(driver_path, chrome_options=option)
    driver.get(url)
    driver.set_window_size(1920, 1080)
    driver.implicitly_wait(3)
    return driver

def get_text(elem, selector) :
    target_elems = elem.select(selector)
    if target_elems :
        return target_elems[0].text.strip()
    else :
        return ""

def get_attr(elem, selector, attr) :
    target_elems = elem.select(selector)
    if target_elems :
        return target_elems[0].attrs.get(attr, '').strip()
    else :
        return ""


def get_cat_lst(driver) :
    driver.get(url='http://earlymorning.ssg.com/')
    driver.implicitly_wait(5)

    cat_lst = driver.find_elements_by_css_selector('.mnmorning_ctg_topmn')
    cat_dict = {}
    for elem in cat_lst:
        cat_dict[elem.find_element_by_css_selector('a').get_attribute('aria-label').replace('바로가기', '').strip()] = elem.get_attribute('data-ctg-code')

    return cat_dict


def item_crawl(driver, cat_nm, cat_no) :

    url = 'http://earlymorning.ssg.com/disp/category.ssg?dispCtgId={}'.format(cat_no)
    driver.get(url=url)
    driver.implicitly_wait(5)

    data = []

    if len(driver.find_elements_by_css_selector('.com_paginate > a')) < 11:
        is_last_page = len(driver.find_elements_by_css_selector('.com_paginate > a')) + 1
    else:
        is_last_page = int(re.findall('[0-9,]+', driver.find_element_by_css_selector('.btn_last').get_attribute('onclick'))[0]) + 1

    sleep(5)

    for page in range(1, is_last_page):
        sleep(2)
        page_url = url + "&page={}".format(page)
        driver.get(url=page_url)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        items = soup.select('.cunit_t232')
        for item in items:
            data.append(
                [cat_no,
                 cat_nm,
                 get_attr(item, '.title > a', 'data-info'),
                 get_text(item, '.title > a > .tx_ko'),
                 get_text(item, '.opt_price > .ssg_price'),
                 get_text(item, '.unit'),
                 get_text(item, '.rate_bg'),
                 get_text(item, '.rate_tx')]
            )

    return data


def run():
    whole_data_lst = []
    driver = set_driver()
    cat_lst = get_cat_lst(driver)

    for cat_nm, cat_no in tqdm(cat_lst.items()):
        data = item_crawl(driver, cat_nm, cat_no)
        whole_data_lst += data

    result = pd.DataFrame(whole_data_lst, columns=['cat_no', 'cat_nm', 'item_cd', 'item_nm', 'ssg_price', 'unit', 'rate', 'rate_cnt'])
    result.to_csv("ssg.csv", index=False)

if __name__ == '__main__' :
    run()



