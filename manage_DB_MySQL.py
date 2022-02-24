import pandas as pd
from datetime import datetime
from os import path
from pandas import DataFrame
import mysql.connector
from sqlalchemy import create_engine
import pymysql, urllib
from datetime import timedelta

file_proxies = 'proxy.txt'
keywords_file = 'keywords.csv'

hostname = 'vmi415626.contaboserver.net'
dbname = 'wtf'
uname = 'ibeppo993'
pwd = 'Ta_802Ta_802'

def drop_proxies_table_MySQL():
    conn = mysql.connector.connect(user=uname, 
                                password=pwd,
                                host=hostname,
                                database=dbname)
    cursor = conn.cursor()                              
    cursor.execute("DROP TABLE IF EXISTS PROXIES_LIST")
    conn.close()

def drop_keywords_table_MySQL():
    conn = mysql.connector.connect(user=uname, 
                                password=pwd,
                                host=hostname,
                                database=dbname)
    cursor = conn.cursor()                              
    cursor.execute("DROP TABLE IF EXISTS KEYWORDS_LIST")
    conn.close()

def insert_proxies_data_MySQL():
    dataframe = pd.read_csv(file_proxies, encoding='utf-8', header=None)
    timestr_now = str(datetime.now())
    timestr = datetime.fromisoformat(timestr_now).timestamp()
    dataframe['TIME'] = timestr
    dataframe.columns = ['PROXIES','TIME']
    df = DataFrame(dataframe, columns= ['PROXIES','TIME'])
    # Create SQLAlchemy engine to connect to MySQL Database
    engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}"
                    .format(host=hostname, db=dbname, user=uname, pw=pwd))
    # Convert dataframe to sql table                                   
    df.to_sql('PROXIES_LIST', engine, index=True)

def insert_keywords_data_MySQL():
    dataframe = pd.read_csv(keywords_file, encoding='utf-8', sep=';', header=None)
    dataframe['CHECKING_1'] = 0
    dataframe['CHECKING_2'] = 0
    dataframe.columns = ['KEYWORDS','CHECKING_1','CHECKING_2']
    df = DataFrame(dataframe, columns= ['KEYWORDS','CHECKING_1','CHECKING_2'])
    def encoding(x):
        #return urllib.parse.quote_plus(x)
        return x.replace("'", "\'")
    df['KEYWORDS'] = df['KEYWORDS'].apply(encoding)
    #pd.set_option("display.max_rows", None, "display.max_columns", None)
    #print(df)
    # Create SQLAlchemy engine to connect to MySQL Database
    engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}"
                    .format(host=hostname, db=dbname, user=uname, pw=pwd))
    # Convert dataframe to sql table                                   
    df.to_sql('KEYWORDS_LIST', engine, index=True)

def get_proxy_MySQL():
    connection = pymysql.connect(host=hostname,
                             user=uname,
                             password=pwd,
                             database=dbname,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    data = pd.read_sql_query("SELECT PROXIES FROM PROXIES_LIST WHERE TIME = ( SELECT MIN(TIME) FROM PROXIES_LIST);",connection)
    global proxy
    proxy = (data['PROXIES'].iat[0])
    print(f'---------------------Request IP is {proxy}')
    timestr_now = str(datetime.now())
    timestr = datetime.fromisoformat(timestr_now).timestamp()
    cursor = connection.cursor()
    cursor.execute("Update PROXIES_LIST set TIME = %s where PROXIES = '%s'" % (timestr,proxy))#,(timestr,proxy))
    connection.commit()
    connection.close()
    return proxy

def postpone_proxy_MySQL(proxy):
    connection = pymysql.connect(host=hostname,
                             user=uname,
                             password=pwd,
                             database=dbname,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()
    print('---------------------Proxy da posticipare '+proxy)
    postpone_time = str(datetime.now() + timedelta(hours=2))
    timestr_postpone = datetime.fromisoformat(postpone_time).timestamp()
    cursor.execute("Update PROXIES_LIST set TIME = %s where PROXIES = '%s'" % (timestr_postpone,proxy))
    connection.commit()
    connection.close()

def get_keyword_MySQL():
    connection = pymysql.connect(host=hostname,
                             user=uname,
                             password=pwd,
                             database=dbname,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    data = pd.read_sql_query("SELECT KEYWORDS FROM KEYWORDS_LIST WHERE CHECKING_1 = 0 AND CHECKING_2 = 0 LIMIT 1;",connection)
    #print(type(data['KEYWORDS'].iat[0]))
    global keyword
    keyword = (data['KEYWORDS'].iat[0])
    print(keyword)
    cursor = connection.cursor()
    cursor.execute("Update KEYWORDS_LIST set CHECKING_1 = %s where KEYWORDS = '%s'" % (1,keyword))
    connection.commit()
    connection.close()
    return keyword

def rehab_keyword_MySQL(keyword):
    connection = pymysql.connect(host=hostname,
                             user=uname,
                             password=pwd,
                             database=dbname,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()
    cursor.execute("Update KEYWORDS_LIST set CHECKING_1 = %s AND CHECKING_2 = %s where KEYWORDS = %s",(0,0,keyword,))
    connection.commit()
    connection.close()

def get_remaining_keywords_MySQL():
    try:
        connection = pymysql.connect(host=hostname,
                                user=uname,
                                password=pwd,
                                database=dbname,
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)
        cursor = connection.cursor()
        data = pd.read_sql_query("SELECT KEYWORDS FROM KEYWORDS_LIST WHERE CHECKING_1 <> 1 AND CHECKING_2 <> 1;",connection)
        remaining_keyword_list = data['KEYWORDS'].tolist()
        remaining_keyword_n = len(remaining_keyword_list)
        connection.close()
        return remaining_keyword_n
    except:
        remaining_keyword_n = 0



#drop_proxies_table_MySQL()
#drop_keywords_table_MySQL()

#insert_proxies_data_MySQL()
#insert_keywords_data_MySQL()

#proxy = get_proxy_MySQL()
#postpone_proxy_MySQL(proxy)
#keyword = get_keyword_MySQL()
#rehab_keyword_MySQL(keyword)

#remaining_keyword_n = get_remaining_keywords_MySQL()
#print(remaining_keyword_n)






