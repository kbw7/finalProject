import csv
import json
import requests
import datetime
import time
import os
import pandas as pd



idInfo = [{"location": "Bae", "meal" : "Breakfast", "locationID" : "96", "mealID" : "148"},
          {"location": "Bae", "meal" : "Lunch", "locationID" : "96", "mealID" : "149"},
          {"location": "Bae", "meal" : "Dinner", "locationID" : "96", "mealID" : "312"},
          {"location": "Bates", "meal" : "Breakfast", "locationID" : "95", "mealID" : "145"},
          {"location": "Bates", "meal" : "Lunch", "locationID" : "95", "mealID" : "146"},
          {"location": "Bates", "meal" : "Dinner", "locationID" : "95", "mealID" : "311"},
          {"location": "StoneD", "meal" : "Breakfast", "locationID" : "131", "mealID" : "261"},
          {"location": "StoneD", "meal" : "Lunch", "locationID" : "131", "mealID" : "262"},
          {"location": "StoneD", "meal" : "Dinner", "locationID" : "131", "mealID" : "263"},
          {"location": "Tower", "meal" : "Breakfast", "locationID" : "97", "mealID" : "153"},
          {"location": "Tower", "meal" : "Lunch", "locationID" : "97", "mealID" : "154"},
          {"location": "Tower", "meal" : "Dinner", "locationID" : "97", "mealID" : "310"}
        ]

with open("wellesley-dining.csv", "w") as fileToWrite:
    csvWriter = csv.DictWriter(fileToWrite, fieldnames = idInfo[0].keys())
    csvWriter.writeheader()
    csvWriter.writerows(idInfo)

def get_menu(date, locationID, mealID):
    base_url = "https://dish.avifoodsystems.com/api/menu-items/week"

    params = {"date" : date, "locationID" : locationID, "mealID" : mealID}

    response = requests.get(base_url, params = params)

    fullUrl = response.url

    data = requests.get(fullUrl).json()

    return data

def write_menus(csvFile, date):
    # first we have to access content in csv file!
    with open(csvFile) as fileToRead:
        csvReader = csv.DictReader(fileToRead)
        rows = [row for row in csvReader]

    # rows is a list of dictionaries!
    for dct in rows:
        menuDate = date

        # if user did put slashes in date, otherwise if they put hyphens we will not use datetime
        if "/" in date:
            dmy = date.split("/") # Want individual day, month, year for datetime
          
            # found .date() from https://docs.python.org/3/library/datetime.html
            # .date(y, m, d)
            convertDate = datetime.date(int(dmy[2]), int(dmy[0]), int(dmy[1]))
        
            menuDate = convertDate.strftime("%m-%d-%Y")


        jsonFileName = dct["location"] + "-" + dct["meal"] + "-" + menuDate + ".json"

        with open(jsonFileName, "w") as outFile:
            menu = get_menu(date, dct["locationID"], dct["mealID"])
            json.dump(menu, outFile)
        
        time.sleep(2)
# add Streamlit option of date widget to add in for write_menus() function

files = os.listdir(os.getcwd())

names = []
for file in files:
    if ".json" in file:
        names.append(file)

mergeDf = pd.DataFrame()

# iterate through list of file names
for elt in names:
    df = pd.read_json(elt)

    mergeDf = pd.concat([mergeDf, df], ignore_index = True)

mergeDf = mergeDf.drop(columns = ["date", "image", "stationName", "stationOrder", "price"])
mergeDf = mergeDf.drop_duplicates(subset= ["id"], keep = "first")

def transform(cell):
    result = ""
    if cell:
        # result is a string where each allergen in the list in the cell is brought together
        result = ",".join([item["name"] for item in cell])
    
    return result

mergeDf["allergens"] = mergeDf["allergens"].apply(transform)

mergeDf["preferences"] = mergeDf["preferences"].apply(transform)

dfFinal = mergeDf.copy()

def dropKeys(cell):
    cell.pop("id")
    cell.pop("corporateProductId")
    cell.pop("caloriesFromSatFat")
    return cell

mergeDf["nutritionals"] = mergeDf["nutritionals"].apply(dropKeys)

colNames = mergeDf.iloc[0].nutritionals.keys()

# to convert all values into floats, except for col "servingSizeUOM", which would be a string.
for key in colNames:
    if key == "servingSizeUOM":
        mergeDf[key] = mergeDf["nutritionals"].apply(lambda dct: str(dct["servingSizeUOM"]))
    else:
        mergeDf[key] = mergeDf["nutritionals"].apply(lambda dct: float(dct[key]))

mergeDf = mergeDf.drop("nutritionals", axis = 1)

mergeDf.to_csv("wellesley-meals.csv", index = False)