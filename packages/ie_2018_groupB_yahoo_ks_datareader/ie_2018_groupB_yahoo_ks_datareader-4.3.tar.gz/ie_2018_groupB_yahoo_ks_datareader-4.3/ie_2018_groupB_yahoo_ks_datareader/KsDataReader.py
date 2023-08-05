def KsDataReader(symbol,sdate,edate):
    import pandas as pd
#    symbol = "LWLG"
#    sdate = '2018-04-01'
#    edate = '2018-04-30'
    ssdate = sdate.replace("-","")
    eedate= edate.replace("-","")
    strSt = "http://rimanakhala.pythonanywhere.com/yahooks/" + symbol + "/" + ssdate + "/" + eedate + "/"
    local_df = pd.read_json(strSt)
    #local_df = pd.read_json("http://rimanakhala.pythonanywhere.com/alldb")
    #df = local_df[(local_df.ticker == symbol) & (pd.to_datetime(local_df.timestamp) >= sdate) & (pd.to_datetime(local_df.timestamp) <= edate)]
    
    return (local_df)
    



