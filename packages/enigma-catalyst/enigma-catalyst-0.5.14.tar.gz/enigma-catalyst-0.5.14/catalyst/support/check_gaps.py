import pandas as pd
import datetime
import sys

def read_csv(csv_filename, ascending=True):
    df = pd.read_csv(csv_filename)
    df['last_traded'] = pd.to_datetime(df['last_traded'])
    #df.set_index(
    #    'last_traded', inplace=True, drop=True
    #)
    #df.index = df.index.tz_localize('UTC')
    df.sort_index(inplace=True, ascending=False)

    return df


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        file_name = sys.argv[1]
    else:
        "no file was specified"

    df = read_csv(file_name)

    df['gap'] = df['last_traded'].diff().iloc[1:] > datetime.timedelta(minutes=1)

    print df[df['gap'] == True]

    """
    for i in xrange(len(df)-1):
        if df['last_traded'][i] - df['last_traded'][i+1] >= datetime.timedelta(minutes=1):
            print ("found gap at %s %s" % (df['last_traded'][i+1], df['last_traded'][i]))
    """
