def KsDataReader(tic_in="",start_in="",end_in=""):
    ''' Takes three parameters (optinal) and displays the results of a query based on them over
    Group's C Yahoo finance DB'''
    
    #Import functions
    import pandas as pd
    import requests
    
    #Check if arguemnts where provided
    #Ticker
    query = []
    if tic_in == "":
        print("Displaying avaiable tickers:")
        av_tickers = requests.get("https://daniserrano.pythonanywhere.com/GroupC")
        av_tickers = av_tickers.json()
        av_tickers = pd.DataFrame(av_tickers).sort_values(['ticker'], ascending=[1])
        print(av_tickers)
        #Get ticker from user
        tic = input("Please select a ticker for the query: ")
    else:
        tic = tic_in
    #Fecha Min   
    if start_in == "":
        print("Displaying first date available for ticker:",tic)
        min_date = requests.get("https://daniserrano.pythonanywhere.com/GroupC/" + tic + "/mindate")
        print(min_date.text[24:34])
        start = input("type the starting date for the query (YYYYMMDD)): ")
    else:
        start = start_in
    #Fecha Max   
    if end_in == "":
        print("Displaying last date available for ticker:",tic)
        max_date = requests.get("https://daniserrano.pythonanywhere.com/GroupC/" + tic + "/maxdate")
        print(max_date.text)
        end = input("type the ending date for the query (YYYYMMDD)): ")
    else:
        end = end_in
        
    query.append((tic, start, end))  
    print(query, "this is your query, let´s get the data!")
    ## el resultado de esto es una list
    
    ## Llamada a la web 
    url_ini = "https://daniserrano.pythonanywhere.com/GroupC/"
    url = url_ini + tic + "/" + start + "/" + end
    
    # Request a pythonanywhere
    response = requests.get(url)
    response = response.json()
    df = pd.DataFrame(response)
    result = df.sort_values(['timestamp'], ascending=[1])
    
    #Imprimir resultados
    print("Data succesfully exported into a DataFrame")
    return result
