def  datareader_doc():
    """ function to return the string 'My first Python package that anyone call install it! How cool!!!' """
    return("Group D first package that anyone can install it! How cool!!!")

def KsDataReader(URL, ticker, start_date, end_date):
    import pandas as pd
    df = pd.read_json(URL + ticker +"/" + start_date + "/" + end_date + "/")  
    return(df)
    
#import pandas as pd
#url = "http://dlichti.pythonanywhere.com/IEGMBD/"
#ticker = '2885.TW'
#start_date = '2018-01-01'
#end_date = '2018-06-06'
#
#print(get_data(url, ticker, start_date, end_date))