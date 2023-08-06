def check_dates(tic,t_date):
    import requests
    if(t_date == "min"):
        j_date = requests.get("https://daniserrano.pythonanywhere.com/GroupC/" + tic + "/mindate")
    else:
        j_date = requests.get("https://daniserrano.pythonanywhere.com/GroupC/" + tic + "/maxdate")
        
    return j_date

def check_dates_correct(datemin,datemax,dateinput,t_date,ii,newdatemin=""):
    try:
        int(dateinput)
        if(len(dateinput) != 8):
            if(ii > 3):
                print("")
                print("Incorrect lenght for the date")
                print("Date needs to be introduced as numeric YYYMMDD")
                print("Too many tries, execution aborted")
            else:
                print("")
                print("Incorrect lenght for the date")
                print("Date needs to be introduced as numeric YYYMMDD (try #" + str(ii) + " out of 3)")
                print("Please try again") 
            return False, ""
        #Extract and check border conditions for date
        min_year = datemin[0:4]
        min_month = datemin[5:7]
        min_day = datemin[8:]
        min_date = min_year + min_month + min_day
        max_year = datemax[0:4]
        max_month = datemax[5:7]
        max_day = datemax[8:]
        max_date = max_year + max_month + max_day
        if(t_date == "min"):
            out = dateinput
            if(dateinput < min_date):
                print("")
                print("**WARNING: Date introduced is earlier than the fisrt date avaiable in the DB")
                print("Min. date will be coerced to:", min_date)
                out = min_date
            elif(dateinput > max_date):
                print("")
                print("**WARNING: Date introduced is is past the last date avaiable in the DB")
                print("Min. date will be coerced to:", max_date)
                out = max_date
        else:
            out = dateinput
            if(dateinput > max_date):
                print("")
                print("**WARNING: Date introduced is past the last date avaiable in the DB")
                print("Max. date will be coerced to:", max_date)
                out = max_date
            elif(dateinput < min_date):
                print("")
                print("**WARNING: Date introduced is earlier than the fisrt date avaiable in the DB")
                print("Max. date will be coerced to:", min_date)
                out = min_date
            elif(out < newdatemin):
                print("")
                print("**WARNING: Date introduced is earlier than the fisrt date selected")
                print("Max. date will be coerced to:", newdatemin)
                out = newdatemin
        #Extract and check correct days and months
        in_month = dateinput[4:6]
        in_day =   dateinput[6:]
        if(int(in_month) < 1 or int(in_month) > 12):
            if(ii > 3):
                print("")
                print("The month needs to be between 01 and 12")
                print("Too many tries, execution aborted")
            else:
                print("")
                print("The month needs to be between 01 and 12 (try #" + str(ii) + " out of 3)")
                print("Please try again") 
            return False, ""
        if(int(in_day) < 1 or int(in_day) > 31):
            if(ii > 3):
                print("")
                print("The day needs to be between 01 and 31")
                print("Too many tries, execution aborted")
            else:
                print("")
                print("The day needs to be between 01 and 31 (try #" + str(ii) + " out of 3)")
                print("Please try again") 
            return False, ""
        return True, out
    except:
        if(ii > 3):
            print("")
            print("Date needs to be introduced as numeric YYYMMDD")
            print("Too many tries, execution aborted")
        else:
            print("")
            print("Date needs to be introduced as numeric YYYMMDD (try #" + str(ii) + " out of 3)")
            print("Please try again") 
        return False, ""
    
    
    


