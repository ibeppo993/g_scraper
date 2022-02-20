from lib2to3.pgen2 import driver
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from initialize import *
import time, json

create_necessary_folder()
create_db_proxy()
create_db_keywords()
remaining_keyword_n = get_remaining_keywords()
proxy_user = 'ibeppo993'
proxy_pass = 'Ta802Ta802'
domain = 'www.google.it'
gl = 'it'
hl = 'IT'
uule = 'w+CAIQICIFSXRhbHk'

while remaining_keyword_n > 0:
    def_date_time = get_now_time()
    keyword = get_keyword()
    print(keyword)
    proxy = get_proxy()
    print(proxy)


    # Create a new instance of the Chrome driver
    option = webdriver.ChromeOptions()
    #option.add_argument("--headless")
    option.add_argument('--incognito')
    option.add_argument("--window-size=1920,1080")
    option.add_argument('--disable-blink-features=AutomationControlled')
    #option.add_argument(f'proxy-server={proxy}')
    option.add_experimental_option("excludeSwitches", ["enable-automation"])
    option.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Remote('http://144.91.112.166:49166/wd/hub',options = option)

    # Go to the Google home page
    url = get_url_to_scrape(keyword, domain, uule, hl, gl)
    #url = 'https://www.ilmioip.it/'
    driver.get(url)
    time.sleep(5)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    js = '''
    let callback = arguments[0];
    let xhr = new XMLHttpRequest();
    xhr.open('GET', '%s', true);
    xhr.onload = function () {
        if (this.readyState === 4) {
            callback(this.status);
        }
    };
    xhr.onerror = function () {
        callback('error');
    };
    xhr.send(null);
    ''' % (url,)

    status_code = driver.execute_async_script(js)
    print(status_code)

    if status_code != 200:
        print('------------ richiesta captcha')
        print(status_code)
        rehab_keyword(keyword)
        postpone_proxy(proxy)

        #log
        with open('debug.log', 'a') as f:
            f.write(f"{proxy};"+time.strftime('%Y%m%d-%H%M%S')+f";Richiesta Captcha;{keyword};aaPanel\n")

        driver.close()

    else:
        HTML_DOM = driver.execute_script("return document.documentElement.outerHTML")
        keyword_enc = urllib.parse.quote_plus(keyword)
        proxy_enc = urllib.parse.quote_plus(proxy)
        
        with open(f'html_output/{def_date_time}-{keyword_enc}.html', 'w+') as f:
            f.write(HTML_DOM)
            f.close()

        SERP_dict = [{
            "keyword": keyword,
            "proxy": proxy,
            "url": driver.current_url,
            "staus_code": status_code,
            'execution_time': def_date_time,
            }]

        df = pd.DataFrame.from_dict(SERP_dict)
        print(df)
        if os.path.isfile('remote_output.json'):
            df_read = pd.read_json('remote_output.json', orient='index')
            df_read = pd.concat([df_read, df], ignore_index=True)
            #df_read.drop_duplicates(inplace=True)
            df_read.to_json('remote_output.json', orient='index')
        else:
            df.to_json('remote_output.json', orient='index')
        
        #log
        with open('debug.log', 'a') as f:
            f.write(f"{proxy};"+time.strftime('%Y%m%d-%H%M%S')+f";Richiesta Completata;{keyword};aaPanel\n")

        driver.quit()
