def check_tickers(df,ticker,ii,ticker_in=""):
    if (df.apply(lambda x: ticker in x.values, axis=1).any() == False):
        if(ii > 3):
            print(str(ticker) + " is not part of the ticker list")
            print("Too many tries, execution aborted")
        else:
            print(str(ticker) + " is not part of the ticker list (try #" + str(ii) + " out of 3)")
            if(ii == 1 and ticker_in != ""):
                print("Displaying avaiable tickers:")
                print(df.to_string(index=False))
                print("Ticker list printed for reference")
            print("Please try again")      
        return False
    else:
        return True
    
def df_tickers():
    import requests
    import pandas as pd
    
    df_tickers = requests.get("https://daniserrano.pythonanywhere.com/GroupC")
    df_tickers = df_tickers.json()
    df_tickers = pd.DataFrame(df_tickers).sort_values(['ticker'], ascending=[1])
    return df_tickers
    


