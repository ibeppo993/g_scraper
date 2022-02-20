from seleniumwire import webdriver  # Import from seleniumwire
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from initialize import *
import time, json
import logging, logging.config

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
    logging.info(f'{def_date_time}--------- Start request')
    # Create a new instance of the Chrome driver
    option = webdriver.ChromeOptions()
    option.add_argument("--headless")
    option.add_argument('--incognito')
    option.add_argument("--window-size=1920,1080")
    option.add_argument('--disable-blink-features=AutomationControlled')
    option.add_experimental_option("excludeSwitches", ["enable-automation"])
    option.add_experimental_option('useAutomationExtension', False)

    keyword = get_keyword()
    print(keyword)
    proxy = get_proxy()
    print(proxy)
    options_seleniumWire = {
        'proxy': {'https': f'https://{proxy_user}:{proxy_pass}@{proxy}',},
    }

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options = option, seleniumwire_options = options_seleniumWire)

    # Go to the Google home page
    url = get_url_to_scrape(keyword, domain, uule, hl, gl)
    #url = 'https://www.ilmioip.it/'
    driver.get(url)
    time.sleep(0.5)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    for request in driver.requests:
        str_request = str(request)
        #print(type(str_request))
        if str_request == url:
            if request.response.status_code != 200:
                print(request.response.status_code)
                print('------------ richiesta captcha')
                rehab_keyword(keyword)
                postpone_proxy(proxy)
                def_date_time = get_now_time()
                logging.error(f'{def_date_time}--------- Captcha request')
                driver.close()

            else:
                print(request.url)
                print(request.response.status_code)
                print(request.response.headers['Content-Type'])

                HTML_DOM = driver.execute_script("return document.documentElement.outerHTML")

                keyword_enc = urllib.parse.quote_plus(keyword)
                proxy_enc = urllib.parse.quote_plus(proxy)
                
                with open(f'html_output/{def_date_time}-{keyword_enc}.html', 'w+') as f:
                    f.write(HTML_DOM)
                    f.close()

                SERP_dict = [{
                    "keyword": keyword,
                    "proxy": proxy,
                    "url": request.url,
                    "staus_code": request.response.status_code,
                    "header": request.response.headers['Content-Type'],
                    'execution_time': def_date_time,
                    }]

                df = pd.DataFrame.from_dict(SERP_dict)
                print(df)
                if os.path.isfile('output.json'):
                    df_read = pd.read_json('output.json', orient='index')
                    df_read = pd.concat([df_read, df], ignore_index=True)
                    df_read.drop_duplicates(inplace=True)
                    df_read.to_json('output.json', orient='index')
                else:
                    df.to_json('output.json', orient='index')
                def_date_time = get_now_time()
                logging.info(f'{def_date_time}--------- Finish request')

                driver.close()
