import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import csv
import boto3

s3Bucket = 'NAME_OF_THE_S3_BUCKET'
s3CsvFileToRead = 'CSV FILE IN S3 BUCKET'


def setUpChromeDriver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1280x1696')
    chrome_options.add_argument('--user-data-dir=/tmp/user-data')
    chrome_options.add_argument('--hide-scrollbars')
    chrome_options.add_argument('--enable-logging')
    chrome_options.add_argument('--log-level=0')
    chrome_options.add_argument('--v=99')
    chrome_options.add_argument('--single-process')
    chrome_options.add_argument('--data-path=/tmp/data-path')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--homedir=/tmp')
    chrome_options.add_argument('--disk-cache-dir=/tmp/cache-dir')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')
    chrome_options.binary_location = "/opt/python/bin/headless-chromium"
    prefs = {
        "browser.downloads.dir": "//tmp//",
        "download.default_directory": "//tmp//",
        "directory_upgrade" : True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    browser = webdriver.Chrome(chrome_options=chrome_options, executable_path='/opt/python/bin/chromedriver')
    return browser

def getSummary(ticker, count):
    browser = setUpChromeDriver()
    summaryUrl = f"https://finance.yahoo.com/quote/{ticker}"
    try:
        browser.get(summaryUrl)
        WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, "//*[@id='quote-summary']/div[2]/table/tbody/tr[1]/td[2]")))
    except:
        if count < 4:
            count += 1
            getSummary(ticker, count)
        else:
            print(f"Error occured at {ticker} URL:{summaryUrl}")
    else:
        price = browser.find_element(By.XPATH, "//*[@id='quote-header-info']/div[3]/div[1]/div[1]/fin-streamer[1]").text
        marketCap = browser.find_element(By.XPATH, "//*[@id='quote-summary']/div[2]/table/tbody/tr[1]/td[2]").text
        beta = browser.find_element(By.XPATH, "//*[@id='quote-summary']/div[2]/table/tbody/tr[2]/td[2]").text
        peRatio = browser.find_element(By.XPATH, "//*[@id='quote-summary']/div[2]/table/tbody/tr[3]/td[2]").text
        eps = browser.find_element(By.XPATH, "//*[@id='quote-summary']/div[2]/table/tbody/tr[4]/td[2]").text
        writeCsvSummary([ticker, price, marketCap, beta, peRatio, eps])
        print(f"{ticker} Price: {price} Market Cap:{marketCap} Beta:{beta} Pe Ratio:{peRatio} EPS:{eps}")
        
    finally:
        browser.quit()

def writeCsvSummary(list):
     with open('/tmp/companySummaries.csv','a',newline='') as f:
            writer = csv.writer(f)
            writer.writerow(list)

def read_urls():
    s3 = boto3.resource('s3')
    csvFile = s3.Object(s3Bucket, s3CsvFileToRead)
    data = csvFile.get()['Body'].read().decode('utf-8').splitlines()
    lines = csv.reader(data)
    sectors = dict()
    return sectors
    
def lambda_handler(event, context):
    header = ["ticker", "price", "marketCap", "beta", "peRatio", "eps"]
    with open('/tmp/companySummaries.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
    sectors = read_urls()
    count = 1
    for sector in sectors:
        print(count)
        getSummary(sector,0)
        count += 1
    s3 = boto3.client('s3')
    s3.upload_file('/tmp/companySummaries.csv', s3Bucket, 'S3 Bucket')
    return {
        'statusCode': 200
    }