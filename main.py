##################################################
# Python Trading Bot
# 
# Description:
# This script simulates a trading bot for the stock market using Python.
# It retrieves stock data via TradingView's technical analysis (TA) API and uses Selenium to automate stock trades on a web-based platform (TradingView).
# The bot evaluates conditions based on RSI (Relative Strength Index) and EMA (Exponential Moving Average) indicators to decide whether to buy or sell stocks.
# 
# Execution Instructions:
# - This script should be run on open market days at 8:58 AM.
# - The trading is performed for SONATSOFTW stock on NSE (National Stock Exchange, India).
# - Selenium is used to control a web browser to place orders based on RSI and EMA signals.
# 
# Pre-requisites:
# - Ensure all required packages are installed (`nsepy`, `selenium`, `tradingview_ta`, etc.).
# - Google Chrome and the appropriate WebDriver must be installed and configured.
# - The steps to execute the code and further details are provided in the README file.
##################################################

# Import necessary libraries
from nsepy import get_history
from datetime import date, datetime
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from tradingview_ta import TA_Handler, Interval

# Display the bot title using figlet (if installed)
os.system("figlet -c Python Trading Bot")

# Set today's date
Today = date.today()
y, m, d = Today.strftime("%Y"), Today.strftime("%m"), Today.strftime("%d")

# Track last order and price variables
last_order = "sell"
current_price = 0
take_profit = 0.0
take_loss = 0.0

# Initialize the Chrome WebDriver using Selenium
try:
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    driver.get("https://in.tradingview.com/")
    time.sleep(60)  # Allow time for the page to load
except Exception as e:
    print("Error initializing browser:", e)
    exit()

# Set up the TradingView handler for SONATSOFTW on a 5-minute interval
ssw = TA_Handler(
    symbol="SONATSOFTW",
    screener="india",
    exchange="NSE",
    interval=Interval.INTERVAL_5_MINUTES
)

# Countdown function to pause between requests
def countdown(t):
    """Countdown timer for pausing the script."""
    while t:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print(timer, end="\r")
        time.sleep(1)
        t -= 1

# Main trading loop
while True:
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    # Trading window: 09:30 AM to 3:10 PM
    if "09:30:00" <= current_time < "15:10:00":
        # Get analysis data (RSI and EMA) from TradingView
        rec = ssw.get_analysis()
        RSI = rec.indicators["RSI"]
        EMA = rec.moving_averages["COMPUTE"]["EMA10"]
        print("RSI:", RSI, "EMA:", EMA)

        # Buy condition: RSI between 30 and 70, EMA is "BUY"
        if 30 <= RSI <= 70 and EMA == "BUY":
            if last_order == "sell":
                try:
                    # Execute buy order
                    print("Buying 1 stock of SONATSOFTW")
                    last_order = "buy"
                    # Selenium actions to place a buy order
                    driver.find_element(By.XPATH, "//div[8]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[2]").click()
                    driver.find_element(By.XPATH, "//div[1]/div[1]/div[6]/button[1]/div[1]/span[2]").click()
                    current_price = float(driver.find_element(By.XPATH, "//div[2]/div[8]/div[1]/div/div/div[1]/div[2]/div/div[2]/div[2]/div").text)
                    print("Current Price:", current_price)
                    take_profit = current_price + 8
                    take_loss = current_price - 5
                except Exception as e:
                    print("Error during buy operation:", e)
                    break

        # Sell condition: RSI >= 50, EMA is "SELL"
        elif RSI >= 50 and EMA == "SELL" and last_order == "buy":
            try:
                # Execute sell order
                print("Selling 1 stock of SONATSOFTW")
                driver.find_element(By.XPATH, "//body[1]/div[2]/div[8]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[2]/div[1]").click()
                time.sleep(2)
                driver.find_element(By.XPATH, "//button[1]/div[1]/span[2]").click()
                last_order = "sell"
            except Exception as e:
                print("Error during sell operation:", e)
                break

        # Check if it's time to close the market
    elif current_time >= "15:10:00":
        print("Market closing for the day.")
        try:
            # Fetch open profit (dummy action)
            open_profit = driver.find_element(By.XPATH, "//div[4]/div[1]/div[1]/div[1]/div[2]/div[3]/div[1]").text
            print("Open Profit:", open_profit)
        except Exception as e:
            print("Error fetching profit:", e)
        break

    # Pre-market analysis (before 9:30 AM)
    elif "09:15:00" <= current_time < "09:30:00":
        print("Analyzing market before opening...")

    # Waiting for market to open
    elif current_time < "09:15:00":
        print("Waiting for market to open...")

    else:
        print("No action required at this time.")

