# libraries
import pandas as pd
import yfinance as yf
from datetime import date
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# user data
portfolio = pd.DataFrame({
    'ticker':['FXAIX','FSSNX','FSPSX','VDADX','FXNAX','VGAVX','FSRNX'],
    'quantity':[16.81,18.957,11.455,76.756,12.256,197.257,18.878],
    'category':['stock','stock','stock','bond','bond','bond','real estate'],
    'future_percents':[0.30,0.25,0.25,0.05,0.05,0.05,0.05]
})
# monthly amount to invest total
monthly_investments = 6000
# Number of years plan to invest
years_to_invest = 9

# data information
today = date.today()
month = today.month
year = today.year

# Function to connect to yahoo finance 
def connectYahooFinance (ticker):
    ticker_data = yf.Ticker(ticker)
    ticker_data = pd.DataFrame(ticker_data.history(period = 'max'))
    ticker_data.reset_index(inplace = True)
    return ticker_data

# function to get historical monthly cost per share
def MonthlyCost (ticker):
    # first call the connect to yahoofinance function
    ticker_data = connectYahooFinance(ticker)
    # filter data to only include info from the first of the month
    return ticker_data[ticker_data['Date'].dt.is_month_start]

# function to scrape historical dividend amt per share
def quarterlyDividends (ticker):
    # first call the conncet to yahoofinance function
    ticker_data = connectYahooFinance(ticker)
    # filter data to only include info when dividends were distributed
    return ticker_data[ticker_data['Dividends']!=0]

# function to calcuate the average dividends for each ticker
def CalculateAvgDividend(ticker):
    dividends = pd.DataFrame(quarterlyDividends(ticker))
    # need to get the data of the past five years
    five_years_ago =f'{today.year-5}-01-01'
    dividends = dividends[(dividends['Date']> five_years_ago)]
    average_dividend = dividends['Dividends'].mean()
    return average_dividend

# function to calc avg cost per share for each ticker
def CalculateAvgCostPerShare(ticker):
    cost_per_share = pd.DataFrame(MonthlyCost(ticker))
    five_years_ago =f'{today.year-5}-01-01'
    cost_per_share = cost_per_share[(cost_per_share['Date']>five_years_ago)]
    average_cost = cost_per_share['Open'].mean()
    return average_cost

# how much is your current initial investment worth
def calcCurrentWorth (ticker):
    quantity = portfolio.loc[portfolio['ticker'] == ticker]['quantity']
    cost_per_share = pd.DataFrame(MonthlyCost(ticker))
    cost_per_share = cost_per_share.iloc[-1:]
    current_value = cost_per_share['Open'].values[0]*quantity.values[0]
    return current_value

# calculate the annual interest rate of the individual stocks
def interestRate(ticker):
    # get a dataframe of the monthly costs for the specific ticker
    cost_per_share = pd.DataFrame(MonthlyCost(ticker))
    # get the current cost per share of the ticker
    current_value = cost_per_share.iloc[-1:]   
    current_value = current_value['Open'].values[0]
    # get the cost per share five years ago
    old_date =f'{today.year-6}-12-01'
    old_value = cost_per_share.loc[cost_per_share['Date']==old_date]
    old_value = old_value['Open'].values[0]
    # calculate the compounding annual growth rate of the stock
    CAGR = (current_value/old_value)**(1/(year-2015))-1
    return CAGR

def totalInvestmentPrediction (Portfolio,Monthly_investments,Years_to_invest):
    results = pd.DataFrame(columns = ['Month', 'Amount','Ticker'])

    for ticker, percent in zip(Portfolio['ticker'], Portfolio['future_percents']):

        principal = calcCurrentWorth(ticker)                        # find the current worth of the stock
        interest = interestRate(ticker)                             # find the growth rate of the stock over the past five years
        compounding_period = 12                                     # assign how often the interest will compound, 12 = monthly
        months = Years_to_invest*compounding_period                                     # assign how lond the user plans to invest for
        monthly_contribution = percent*Monthly_investments          # assign how much the user plans to invest in this stock per month
        dividends = CalculateAvgDividend(ticker)                    # calculate the average dividends returned
        dividends_compounding = 3                                   # the dividends compound quarterly
        avg_cost_per_share = CalculateAvgCostPerShare(ticker)       # calculate the average cost per share of the stock
        results =  results.append({'Month': 1, 'Amount': principal, 'Ticker':ticker}, ignore_index = True)

        for i in range(2,months+1):
            Month = i
            Ticker = ticker
            amt = results.iloc[-1:]
            amt = amt['Amount'].values[0]
            if (i%dividends_compounding)==0:
                    total = amt+(amt*(interest/12))+monthly_contribution+(amt/avg_cost_per_share)*dividends
                    results =  results.append({'Month': Month, 'Amount': total, 'Ticker':Ticker}, ignore_index = True)
            else:
                    total = amt+(amt*(interest/12))+monthly_contribution
                    results =  results.append({'Month': Month, 'Amount': total, 'Ticker':Ticker}, ignore_index = True)
    return results

# now we need to add up all of the rows that have the same years
def amountPeryear(Portfolio,Monthly_investments,Years_to_invest):
    total_portfolio = totalInvestmentPrediction(Portfolio,Monthly_investments,Years_to_invest)
    years = Years_to_invest  
    sum_portfolio = pd.DataFrame(columns = ['Year', 'Amount'])
    for i in range(1,years+1):
        per_year = total_portfolio[total_portfolio['Month']==i*12]['Amount'].sum()
        sum_portfolio =  sum_portfolio.append({'Year': i, 'Amount': per_year}, ignore_index = True)
        
    return sum_portfolio

# calculate percents
def percents(Portfolio):
    # calculate the percent each stock holds in the portfolio
    total = Portfolio['quantity'].sum()
    percents = []
    for elem in Portfolio['quantity']:
        percent = (elem/total)*100
        percents.append(percent)

    Portfolio['percent'] = percents
    return Portfolio