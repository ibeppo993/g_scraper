import os, urllib, subprocess, signal, sqlite3, random
from subprocess import Popen, PIPE
import pandas as pd
from pandas import DataFrame
from os import path
from datetime import datetime
from datetime import timedelta
from urllib.parse import unquote_plus


folder_list = ['html_output']
file_list = ['output.json']
db_name_proxy = 'db_proxy.db'
file_proxies = 'proxy.txt'
db_name_keyword = 'db_keyword.db'
keywords_file = 'keywords.csv'

def create_necessary_folder():
    for folder_ in folder_list:
        if not os.path.exists(folder_):
            os.makedirs(folder_)
    for file_ in file_list:
        if not os.path.isfile(file_):
            open(file_, mode='a').close()    
    


def create_db_proxy():
    dataframe = pd.read_csv(file_proxies, encoding='utf-8', header=None)
    timestr_now = str(datetime.now())
    timestr = datetime.fromisoformat(timestr_now).timestamp()
    dataframe['TIME'] = timestr
    dataframe.columns = ['PROXY','TIME']
    # Creazione DB da Dataframe PROXY
    check_db = path.exists(db_name_proxy)
    #print(check_db)
    if check_db == False:
        conn = sqlite3.connect(db_name_proxy,detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        c = conn.cursor()
        c.execute('CREATE TABLE PROXY_LIST (PROXY text, TIME timestamp)')
        conn.commit()
        df = DataFrame(dataframe, columns= ['PROXY','TIME'])
        df.to_sql('PROXY_LIST', conn, if_exists='replace', index = True)
        c.execute('''SELECT * FROM PROXY_LIST''')
        del df
        del dataframe
        conn.close()
    else:
        print('DB già presente PROXY')



def get_proxy():
    conn = sqlite3.connect(db_name_proxy)
    c = conn.cursor()
    data=pd.read_sql_query("SELECT PROXY FROM PROXY_LIST WHERE TIME = ( SELECT MIN(TIME) FROM PROXY_LIST);",conn)
    global proxy
    proxy = (data['PROXY'].iat[0])
    #print(f'---------------------Request IP is {proxy}')
    timestr_now = str(datetime.now())
    timestr = datetime.fromisoformat(timestr_now).timestamp()
    c.execute("Update PROXY_LIST set TIME = ? where PROXY = ?",(timestr,proxy))
    conn.commit()
    c.execute("Update PROXY_LIST set TIME = ? where PROXY = ?",(timestr,proxy,))
    conn.commit()
    conn.close()
    return proxy

def postpone_proxy(proxy):
    conn = sqlite3.connect(db_name_proxy)
    c = conn.cursor()
    #print('---------------------Proxy da posticipare '+proxy)
    postpone_time = str(datetime.now() + timedelta(hours=2))
    timestr_postpone = datetime.fromisoformat(postpone_time).timestamp()
    c.execute("Update PROXY_LIST set TIME = ? where PROXY = ?",(timestr_postpone,proxy))
    conn.commit()
    conn.close()

def create_list_url_from_keyword(domain,gl,hl,uule):
    df = pd.read_csv (keywords_file, header=None)
    df['url'] = 'url'
    df = df.set_axis(['keywords', 'url'], axis=1, inplace=False)
    result = []
    for keyword in df['keywords']:
        keyword_encoding = urllib.parse.quote_plus(keyword)
        #url = f'https://{domain}/search?q={keyword_encoding}&oq={keyword_encoding}&uule={uule}&hl={hl}&gl={gl}&sourceid=chrome&ie=UTF-8'
        url_1 = f'https://{domain}/'
        url_2 = urllib.parse.quote_plus(f'search?q={keyword_encoding}&oq={keyword_encoding}&uule={uule}&hl={hl}&gl={gl}&sourceid=chrome&ie=UTF-8')
        url = url_1 + url_2
        result.append(url)
    df["url_to_scrape"] = result
    df.drop('keywords', axis=1, inplace=True)
    list_of_urls = df['url_to_scrape'].tolist()
    #print(list_of_urls)
    return list_of_urls

def get_now_time():
    now = datetime.now()
    def_date_time = now.strftime("%Y%m%d-%H%M%S-%fZ")
    return def_date_time

def create_db_keywords():
    # Creazione dataframe keyword
    dataframe = pd.read_csv(keywords_file, encoding='utf-8', sep=';', header=None)
    dataframe['CHECKING_1'] = 0
    dataframe['STATUS_CODE'] = 0
    dataframe.columns = ['KEYWORDS','CHECKING_1','STATUS_CODE']
    #print(dataframe)
    # Creazione DB da Dataframe KEYWORD
    check_db = path.exists(db_name_keyword)
    #print(check_db)
    if check_db == False:
        conn = sqlite3.connect(db_name_keyword)
        c = conn.cursor()
        c.execute('CREATE TABLE KEYWORDS_LIST (KEYWORDS text, CHECKING_1 number, STATUS_CODE number)')
        conn.commit()
        df = DataFrame(dataframe, columns= ['KEYWORDS', 'CHECKING_1', 'STATUS_CODE'])
        df.to_sql('KEYWORDS_LIST', conn, if_exists='replace', index = True)
        c.execute('''  
        SELECT * FROM KEYWORDS_LIST
                ''')
        #for row in c.fetchall():
        #    print(row)
        del df
        del dataframe
        conn.close()
    else:
        pass
        #print('DB già presente KEYWORDS')

def get_remaining_keywords():
    check_db = path.exists(db_name_keyword)
    if check_db == True:
        conn = sqlite3.connect(db_name_keyword)
        c = conn.cursor()
        try:
            data = pd.read_sql_query("SELECT KEYWORDS FROM KEYWORDS_LIST WHERE CHECKING_1 <> 1 AND STATUS_CODE = 0;",conn)
            remaining_keyword_list = data['KEYWORDS'].tolist()
            remaining_keyword_n = len(remaining_keyword_list)
            #print('###############################')
            #print(remaining_keyword_n)
            conn.close()
            
        except IndexError:
            conn.close()
            #print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
            remaining_keyword_n = 0

        return remaining_keyword_n


def get_keyword():
    #print('-------------------------')
    conn = sqlite3.connect(db_name_keyword)
    c = conn.cursor()
    data = pd.read_sql_query("SELECT KEYWORDS FROM KEYWORDS_LIST WHERE STATUS_CODE = 0 AND CHECKING_1 = 0 LIMIT 1;",conn)
    #print(type(data['KEYWORDS'].iat[0]))
    global keyword
    keyword = (data['KEYWORDS'].iat[0])
    c.execute("Update KEYWORDS_LIST set CHECKING_1 = 1 where KEYWORDS = ?",(keyword,))
    conn.commit()
    conn.close()
    num = random.randint(1,2)
    #print(f'pausa {num} sec')
    return keyword

# def set_200_to_keyword(keyword):
#     conn = sqlite3.connect(db_name_keyword)
#     c = conn.cursor()
#     c.execute("Update KEYWORDS_LIST set CHECKING_1 = 1 where KEYWORDS = ?",(keyword,))
#     conn.commit()
#     conn.close()
#     num = random.randint(1,2)


def get_url_to_scrape(keyword, domain, uule, hl, gl):
    keyword_encoding = urllib.parse.quote_plus(keyword)
    # url_1 = f'https://{domain}/'
    # url_2 = urllib.parse.quote_plus(f'search?q={keyword_encoding}&oq={keyword_encoding}&uule={uule}&hl={hl}&gl={gl}&sourceid=chrome&ie=UTF-8')
    # url = url_1 + url_2
    url = f'https://{domain}/search?q={keyword_encoding}&oq={keyword_encoding}&uule={uule}&hl={hl}&gl={gl}&sourceid=chrome&ie=UTF-8'
    return url

def get_keyword_from_url(url_error, domain, uule, hl, gl):
    kw = url_error.replace(f'https://{domain}/search?q=','')
    kw = kw.replace(f'&uule={uule}&hl={hl}&gl={gl}&sourceid=chrome&ie=UTF-8', '')
    kw = kw.split("&oq=")
    kw = str(kw[0])
    print(kw)
    keyword=unquote_plus(kw)
    #print(keyword)
    return keyword



def rehab_keyword(keyword):
    conn = sqlite3.connect(db_name_keyword)
    c = conn.cursor()
    c.execute("Update KEYWORDS_LIST set CHECKING_1 = 0 where KEYWORDS = ?",(keyword,))
    conn.commit()
    conn.close()

def get_proxy_number():
    file = open(file_proxies, "r")
    nonempty_lines = [line.strip("\n") for line in file if line != "\n"]
    line_count = len(nonempty_lines)
    file.close()
    return line_count

