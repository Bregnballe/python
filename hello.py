from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import time
import csv
import pandas as pd

url = "https://www.dst.dk/da/Statistik/emner/befolkning-og-valg/navne/HvorMange"
PATH = "C:\Program Files (x86)\ChromeDriver\chromedriver.exe"
driver = webdriver.Chrome(PATH)
# The browser we use is chrome and the driver is located in PATH


driver.get(url)


cookieButton = driver.find_element_by_id("cookieDst-reject")
searchInput = driver.find_element_by_id("navnesognamefornavn")
searchButton = driver.find_element_by_id("navnesognamesog")
results = driver.find_element_by_id("navnesognameresult")
clearButton = driver.find_element_by_id("navnesognameryd")
resultList = []

cookieButton.click()

with open("C:/codetemp/python/names.csv", "r", encoding="UTF-8") as csv_read_file:
    csv_reader = csv.reader(csv_read_file)

    for line in csv_reader:  # for every line in the csv files
        searchInput.send_keys(line)  # add line to input and search
        searchButton.click()

        try:
            table = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "table"))
            )  # wait until table is available

            tableData = [
                [cell.text for cell in row.find_elements_by_tag_name("td")]
                for row in table.find_elements_by_tag_name("tr")
            ][1:]

            tableHeader = [
                [cell.text for cell in row.find_elements_by_tag_name("th")]
                for row in table.find_elements_by_tag_name("tr")
            ][0]

            zippedList = [dict(zip(tableHeader, t)) for t in tableData]

            resultList.append(zippedList)

            clearButton.click()

        except:
            print("Something went wrong")
print(json.dumps(resultList, indent=4, ensure_ascii=False))
