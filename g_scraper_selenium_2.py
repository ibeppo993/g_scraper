from lib2to3.pgen2 import driver
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from initialize import *
from manage_DB_MySQL import *
from telegram_bot import *
import undetected_chromedriver as uc
import time, json
from dotenv import load_dotenv
load_dotenv()

docker_url = os.environ.get("docker_2")

create_necessary_folder()
#create_db_proxy()
#create_db_keywords()
output_json = 'output.json'
debug_log = 'debug.log'
remaining_keyword_n = get_remaining_keywords_MySQL()
proxy_user = 'ibeppo993'
proxy_pass = 'Ta802Ta802'
domain = 'www.google.it'
gl = 'it'
hl = 'IT'
uule = 'w+CAIQICIFSXRhbHk'

while remaining_keyword_n > 0:
    def_date_time = get_now_time()
    keyword = get_keyword_MySQL()
    print(keyword)
    proxy = get_proxy_MySQL()
    print(proxy)

    # Create a new instance of the Chrome driver
    option = uc.ChromeOptions()
    #option.add_argument("--headless")
    option.add_argument('--incognito')
    option.add_argument("--window-size=1920,1080")
    option.add_argument('--disable-blink-features=AutomationControlled')
    option.add_argument(f'proxy-server={proxy}')
    option.add_argument('--no-first-run --no-service-autorun --password-store=basic')
    option.add_experimental_option("excludeSwitches", ["enable-automation"])
    option.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Remote(f'{docker_url}wd/hub',options = option)

    # Go to the Google home page
    url = get_url_to_scrape(keyword, domain, uule, hl, gl)
    #url = 'https://www.ilmioip.it/'
    driver.get(url)
    driver.implicitly_wait(10)
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
        rehab_keyword_MySQL(keyword)
        postpone_proxy_MySQL(proxy)
        test = telegram_bot_sendtext(f"{def_date_time} - {proxy} - {keyword} - {docker_url} - Richiesta Captcha")

        #log
        with open(debug_log, 'a') as f:
            f.write(f"{proxy};"+time.strftime('%Y%m%d-%H%M%S')+f";Richiesta Captcha;{keyword};{docker_url}\n")

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
        if os.path.isfile(output_json):
            df_read = pd.read_json(output_json, orient='index')
            df_read = pd.concat([df_read, df], ignore_index=True)
            #df_read.drop_duplicates(inplace=True)
            df_read.to_json(output_json, orient='index')
        else:
            df.to_json(output_json, orient='index')
        
        #log
        with open(debug_log, 'a') as f:
            f.write(f"{proxy};"+time.strftime('%Y%m%d-%H%M%S')+f";Richiesta Completata;{keyword};{docker_url}\n")

        driver.quit()
