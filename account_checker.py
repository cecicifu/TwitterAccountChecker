#!/usr/bin/python3
# coding: utf-8

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import logging
import random
import requests
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("-U", "--username", required=True)
parser.add_argument("-H", "--headless", action='store_true', default=False)
parser.add_argument("-P", "--proxy", action='store_true', default=False)
args = parser.parse_args()

PROXY_URL = 'https://free-proxy-list.net'


def get_proxies():
    response = requests.get(PROXY_URL)
    soup = BeautifulSoup(response.text, 'lxml')
    table = soup.select_one('div.fpl-list > table')
    list_tr = table.find_all('tr')
    list_td = [elem.find_all('td') for elem in list_tr]
    list_td = list(filter(None, list_td))
    list_ip = [elem[0].text for elem in list_td]
    list_ports = [elem[1].text for elem in list_td]
    list_proxies = [':'.join(elem) for elem in list(zip(list_ip, list_ports))]

    return list_proxies


def check_account():
    try:
        chrome.get('https://twitter.com/%s' % args.username)

        WebDriverWait(chrome, 60).until(ec.visibility_of_element_located(
            (By.XPATH, "//span[text()='@%s']" % args.username)))

        acc_exists = chrome.find_elements(
            By.XPATH, "//span[@data-testid='UserJoinDate']")

        if acc_exists:
            logging.info('The account "%s" exists' % args.username)
            print('The account "%s" exists' % args.username)
        else:
            logging.info(
                'The account "%s" doesn\'t exists' % args.username)
            print('The account "%s" doesn\'t exists' % args.username)

    except NoSuchElementException:
        logging.warn('Element not found')

    except TimeoutException:
        logging.warn("TimeoutException")

    finally:
        logging.info('Quitting..')
        chrome.quit()


if __name__ == "__main__":
    try:
        logging.info('Initializing..')

        options = webdriver.ChromeOptions()

        if args.headless:
            options.add_argument("--headless")
        if args.proxy:
            proxy = random.choice(get_proxies())

            logging.info('Using proxy %s' % proxy)

            webdriver.DesiredCapabilities.CHROME['proxy'] = {
                "httpProxy": proxy,
                "ftpProxy": proxy,
                "sslProxy": proxy,
                "proxyType": "MANUAL",
            }
            webdriver.DesiredCapabilities.CHROME['acceptSslCerts'] = True

        options.add_argument("--disable-extensions")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--incognito")

        chrome = webdriver.Chrome(service=Service(
            ChromeDriverManager().install()), options=options)

        check_account()
    except WebDriverException:
        logging.exception("WebDriverException")

    except KeyboardInterrupt:
        logging.warn("Interrupted by user..")

    except Exception as e:
        logging.exception("Unexpected exception %s" % e)
