from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import csv
import requests

url = "https://www.dst.dk/da/Statistik/emner/befolkning-og-valg/navne/HvorMange"
PATH = "C:\Program Files (x86)\ChromeDriver\chromedriver.exe"
driver = webdriver.Chrome(PATH)
driver.get(url)
# The browser we use is chrome and the driver is located in PATH
# The driver version must match the browser version


headers = {"Content-Type": "application/json"}
url = "http://localhost:3000/api/names/"
# API headers and url


cookieButton = driver.find_element_by_id("cookieDst-reject")
searchInput = driver.find_element_by_id("navnesognamefornavn")
searchButton = driver.find_element_by_id("navnesognamesog")
results = driver.find_element_by_id("navnesognameresult")
clearButton = driver.find_element_by_id("navnesognameryd")
# All the html-elements we need to interact with


nameKey = "name"
maleGenderKey = "maleGender"
femaleGenderKey = "femaleGender"
peopleCountKey = "peopleCount"
trendCountKey = "trendCount"
maleCountKey = "maleCount"
femaleCountKey = "femaleCount"
maleTrendCountKey = "maleTrendCount"
femaleTrendCountKey = "femaleTrendCount"
# The keys we use in the json object


resultList = []
# The list we will store the final json objects in

cookieButton.click()

with open("C:/codetemp/python/names.csv", "r", encoding="UTF-8") as csv_read_file:
    csv_reader = csv.reader(csv_read_file)

    for name in csv_reader:  # for every line in the csv files
        searchInput.send_keys(name)  # add line to input and search
        searchButton.click()  # click the search button

        try:
            table = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "table"))
            )  # wait until html-table is available on page

            tableData = [
                [
                    "female"
                    if cell.text.startswith("Kvinder")
                    else "male"
                    if cell.text.startswith("Mænd")
                    else ""
                    if cell.text.startswith("Der")
                    else "0"
                    if cell.text == ""
                    else cell.text
                    for cell in row.find_elements_by_tag_name("td")
                ]
                for row in table.find_elements_by_tag_name("tr")
            ][1:]
            # The [1:] removes the first row (tr) which is the header row.

            tableHeader = [
                [
                    "gender"
                    if cell.text.startswith("Resultat")
                    else "trend"
                    if cell.text.startswith("Ændring")
                    else cell.text
                    for cell in row.find_elements_by_tag_name("th")
                ]
                for row in table.find_elements_by_tag_name("tr")
            ][0]
            # The [0] selects only the first row (tr) which is the header row.

            zippedList = [dict(zip(tableHeader, t)) for t in tableData]
            # zipping the two lists together and turn them into a dictionary (like an object)

            data = {name[0]: zippedList}

            print(json.dumps(data, indent=4, ensure_ascii=False))

            new_data = {}

            for name, values in data.items():
                if len(values) == 1:
                    # if there is only one row in the table ie. one gender with that name
                    new_data = {
                        nameKey: name,
                        maleGenderKey: values[0].get("gender", "") == "male",
                        femaleGenderKey: values[0].get("gender", "") == "female",
                        # the second argument on the get method is the default value if the key is not found
                        peopleCountKey: int(values[0].get("2023", 0)),
                        trendCountKey: int(values[0].get("trend", 0)),
                        (
                            maleCountKey
                            if values[0].get("gender", "") == "male"
                            else femaleCountKey
                        ): int(values[0].get("2023", 0)),
                        (
                            femaleCountKey
                            if values[0].get("gender", "") == "male"
                            else maleCountKey
                        ): 0,
                        # setting the count of the gender that is not represented to 0
                        (
                            maleTrendCountKey
                            if values[0].get("gender", "") == "male"
                            else femaleTrendCountKey
                        ): int(values[0].get("trend", 0)),
                        (
                            femaleTrendCountKey
                            if values[0].get("gender", "") == "male"
                            else maleTrendCountKey
                        ): 0,
                        # setting the trend count of the gender that is not represented to 0
                    }
                else:
                    # if there are more rows
                    new_data = {
                        nameKey: name,
                        maleGenderKey: True,
                        femaleGenderKey: True,
                        # Since there are more than one gender, we know both genders are represented
                        peopleCountKey: int(values[0]["2023"]) + int(values[1]["2023"]),
                        trendCountKey: int(values[0]["trend"])
                        + int(values[1]["trend"]),
                        (
                            maleCountKey
                            if values[0].get("gender", "") == "male"
                            else femaleCountKey
                        ): int(values[0].get("2023", 0)),
                        (
                            maleCountKey
                            if values[1].get("gender", "") == "male"
                            else femaleCountKey
                        ): int(values[1].get("2023", 0)),
                        (
                            maleTrendCountKey
                            if values[0].get("gender", "") == "male"
                            else femaleTrendCountKey
                        ): int(values[0].get("trend", 0)),
                        (
                            maleTrendCountKey
                            if values[1].get("gender", "") == "male"
                            else femaleTrendCountKey
                        ): int(values[1].get("trend", 0)),
                    }

            response = requests.post(url, headers=headers, json=new_data)
            print(response.status_code)
            print(response.text)
            # sending the json object to the api

            resultList.append(new_data)
            # Create and append an object with the name as key and value of zippedList

            clearButton.click()

        except Exception as e:
            print(f"Something went wrong: {e}")

print(json.dumps(resultList, indent=4, ensure_ascii=False))
