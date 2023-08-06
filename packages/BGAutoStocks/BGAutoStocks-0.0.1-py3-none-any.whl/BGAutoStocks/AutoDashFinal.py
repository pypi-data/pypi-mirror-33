import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests

myFile = "client_secret.json"

# authorize API
scope = ['https://spreadsheets.google.com/feeds']
#creds = ServiceAccountCredentials.from_json_keyfile_name("client_secret.json", scope)
creds = ServiceAccountCredentials.from_json_keyfile_name(myFile, scope)
client = gspread.authorize(creds)

myurl = "https://docs.google.com/spreadsheets/d/1NxZUxmYXTMN08X9-icagqytE4ghRr7SiUF5NaUjxXEg/edit#gid=0"

# Open spreadsheet
sheet = client.open_by_url(myurl).worksheet("Dashboard")

# put important variables here because I can't code
portfolioValueStart = sheet.cell(2, 1)
portfolioValueNext = (str(portfolioValueStart).split("'")[1])
portfolioValue = portfolioValueNext[1:len(portfolioValueNext)]

buyingPowerStart = sheet.cell(2, 2)
buyingPowerNext = (str(buyingPowerStart).split("'")[1])
buyingPowerFun = buyingPowerNext[1:len(buyingPowerNext)]
buyingPower = buyingPowerFun.replace(",", "")

sheetTwo = client.open_by_url(myurl).worksheet("Log")

# before a new log entry is made try to resize the worksheet so it runs faster
# the current method of inserting a row essentially copies and pastes all content just a row below
# resizing can speed this up as the default is 1000 rows
# write a function that only runs the first time the sheet is opened.

buyThis = ""
buyQuant = ""

def buyStock(buyThis, buyQuant):
    RowNum = 0
    # write a function for buying stock
    # Must make sure there are funds in buying power to do so
    r = requests.get("https://api.robinhood.com/quotes/" + buyThis + "/")
    # print(r.status_code)
    data = r.json()
    if float(data.get("bid_price"))*buyQuant > float(buyingPower):
        print("You don't have enough buying power for this!  Either sell some of your current holdings or buy something cheaper.")
    else:
        sheetTwo.insert_row([data.get("symbol"), float(data.get("bid_price")), buyQuant, "Buy", data.get("updated_at"), "-" + str(float(data.get("bid_price"))*buyQuant)], index=2)
        sheetTwo.update_cell(2, 6, "-"+str(float(data.get("bid_price"))*buyQuant))
        for x in range(len(sheet.col_values(1))):
            RowNum += 1
            if str(sheet.col_values(1)[x]) == str(data.get("symbol")):
                sheet.update_cell(RowNum, 4, int(str(sheet.cell(RowNum, 4)).split("'")[1])+buyQuant)
                break
            if RowNum == len(sheet.col_values(1)):
                sheet.insert_row([data.get("symbol"), "Long", "", buyQuant], 4)
                sheet.update_cell(4, 5, "=C4*D4")


sellThis = ""
sellQuant = ""


def sellStock(sellThis, sellQuant):
    RowNum = 0
    # write a function for selling stock
    # Must make sure the stock is actually in portfolio as well
    # If not, throw an error that says hey sorry you don't own that
    r = requests.get("https://api.robinhood.com/quotes/" + sellThis + "/")
    data = r.json()
    for x in range(len(sheet.col_values(1))):
        RowNum += 1
        if str(sheet.col_values(1)[x]) == str(data.get("symbol")):
            if int(sheet.col_values(4)[RowNum-1]) < int(sellQuant):
                print("You're trying to sell more shares than you own!")
                break
            else:
                sheetTwo.insert_row([data.get("symbol"), float(data.get("ask_price")), sellQuant, "Sell", data.get("updated_at"), str(float(data.get("bid_price"))*sellQuant)], index=2)
                sheetTwo.update_cell(2, 6, str(float(data.get("ask_price"))*sellQuant))
                sheet.update_cell(RowNum, 4, int(str(sheet.cell(RowNum, 4)).split("'")[1])-sellQuant)
                if int(str(sheet.cell(RowNum, 4)).split("'")[1]) == 0:
                    sheet.delete_row(RowNum)
                    break
                break
        if RowNum == len(sheet.col_values(1)):
            print("You are trying to sell shares that you don't own!")
buyStock("AMZN", 1)
sellStock("GE", 2)
