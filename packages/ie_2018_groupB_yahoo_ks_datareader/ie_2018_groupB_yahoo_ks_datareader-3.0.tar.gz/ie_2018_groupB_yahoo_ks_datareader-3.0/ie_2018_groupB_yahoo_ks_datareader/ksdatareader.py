def KsDataReader(symbol,sdate,edate):
    import pandas as pd
    local_df = pd.read_json("http://rimanakhala.pythonanywhere.com/alldb")
    df = local_df[(local_df.ticker == symbol) & (pd.to_datetime(local_df.timestamp) >= sdate) & (pd.to_datetime(local_df.timestamp) <= edate)]
    return (df)
    



