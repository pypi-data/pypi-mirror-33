
def KsDataReader(tic_in="",start_in="",end_in=""):
    ''' Takes three parameters (optinal) and displays the results of a query based on them over Group's C Yahoo finance DB 
        The function can be called wihtout paremeters and will interact with the user in order to read the required data, or
        cab be called using the following parameters.
        Parameters:
            tic_in (optional): Name of the ticker which data wants to be extracted
            start_in (optional): Initial date from when the data extraction will take place
            end_in (optional): Initial date from when the data extraction will take place
            
        By: Vivianne Mahecha, Alvaro Fernández, Daniel Serrano, Marcos Ramírez, Markus Schaber and Yamil Zeledon
        GMDB-2017; Group C
    '''
    #Import functions
    import matplotlib
    import pandas as pd
    import requests
    from ie_mbdbl2017_C_yahoo_ks_datareader.check_tickers import check_tickers, df_tickers
    from ie_mbdbl2017_C_yahoo_ks_datareader.check_dates import check_dates, check_dates_correct
    #from check_tickers import check_tickers, df_tickers
    #from check_dates import check_dates, check_dates_correct
    #from send_email import send_email
    from ie_mbdbl2017_C_yahoo_ks_datareader.send_email import send_email
    
    #Obtain tickers:
    av_tickers = df_tickers()
    query = []
    
    #Check if arguemnts where provided
    #Ticker
    if tic_in == "":
        i = False
        ii = 0
        while i == False and ii <= 3:
            ii += 1
            if(ii == 1):
                print("Displaying avaiable tickers:")
                print(av_tickers.to_string(index=False))
            #Get ticker from user
            tic = input("Please select a ticker for the query: ")
            #Check if the ticker is in the list
            i = check_tickers(av_tickers,tic,ii)
    else:
        tic = tic_in
        ii = 1
        i = check_tickers(av_tickers,tic,ii,tic_in)
        while i == False and ii <= 3:
            ii += 1
            tic = input("Please select a ticker for the query: ")
            #Check if the ticker is in the list
            i = check_tickers(av_tickers,tic,ii)
    #Seguir sólo si ticker = True
    if(i == True):
        #┐Obtain dates avaiable from tickers
        min_date = check_dates(tic,"min")
        max_date = check_dates(tic,"max")
        min_date = min_date.text[24:34]
        max_date = max_date.text[24:34]
        print("")
        print("Displaying first and last dates available for ticker:",tic)
        print("- First Date Avaibale:", min_date)
        print("- Last Date Avaibale:", max_date)
        #Fecha Min   
        if start_in == "":
            i = False
            ii = 0
            while i == False and ii <= 3:
                ii += 1
                start = input("Please type the starting date for the query (YYYYMMDD)): ")
                i, start = check_dates_correct(min_date,max_date,start,"min",ii)
        else:
            start = start_in
            ii = 1
            i, start = check_dates_correct(min_date,max_date,start,"min",ii)
            while i == False and ii <= 3:
                ii += 1
                start = input("Please type the starting date for the query (YYYYMMDD)): ")
                i, start = check_dates_correct(min_date,max_date,start,"min",ii)
        #Seguir sólo si mindate = True
        if(i == True):
            #Fecha Max   
            if end_in == "":
                i = False
                ii = 0
                while i == False and ii <= 3:
                    ii += 1
                    end = input("Please type the ending date for the query (YYYYMMDD)): ")
                    i, end = check_dates_correct(min_date,max_date,end,"max",ii,start)                
            else:
                end = end_in
                ii = 1
                i, end = check_dates_correct(min_date,max_date,end,"max",ii,start)
                while i == False and ii <= 3:
                    ii += 1
                    end = input("Please type the ending date for the query (YYYYMMDD)): ")
                    i, end = check_dates_correct(min_date,max_date,end,"max",ii,start)
                
            query.append((tic, start, end))  
            print("")
            print(query, "this is your query, let´s get the data!")
            
            ## Llamada a la web 
            url_ini = "https://daniserrano.pythonanywhere.com/GroupC/"
            url = url_ini + tic + "/" + start + "/" + end
            
            # Request a pythonanywhere
            response = requests.get(url)
            response = response.json()
            df = pd.DataFrame(response)
            result = df.sort_values(['timestamp'], ascending=[1])
            
            #Imprimir resultados
            if result.empty == True:
                print("")
                print("The queried data did not produce any results")
                print("Arguemnts were:",query)
                print("Please check your arguments and try again")
                return 0
            else:
                print("")
                print("Data succesfully exported into a DataFrame")
                plt_name = "GroupC_R&Fplot.pdf"
                mail_subject = "Risk and Fraud - Group C Image"
                mail_text = "Results of your query"
                fig = result.plot(x = "timestamp", y = "Market Cap", linestyle="-", color="blue").get_figure()
                fig.savefig(plt_name)
                send_email(mail_subject, mail_text, plt_name)
                return result
        else:
            return 0
    else:
        return 0
