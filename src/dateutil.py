import pandas_market_calendars as mcal
from datetime import datetime, timedelta


def next_trading_day(nyt_lead=0):
    # Get the NYSE calendar
    nyse = mcal.get_calendar('NYSE')
    
    # Get the current date
    today = datetime.now()
    
    # Calculate the next trading day
    # Schedule is returned in a Pandas DataFrame with 'market_open' and 'market_close' columns
    schedule = nyse.schedule.loc[today:today + timedelta(days=30)]
    
    # The next trading day is the first day in the schedule
    next_day = schedule.iloc[nyt_lead].name
    
    return next_day

