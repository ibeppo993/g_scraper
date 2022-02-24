from lib2to3.pgen2 import driver
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
from initialize import *
#from manage_DB_MySQL import *
from telegram_bot import *
import time, json
from fake_useragent import UserAgent
from dotenv import load_dotenv
load_dotenv()

docker_url = os.environ.get("docker_1")

create_necessary_folder()
create_db_proxy()
create_db_keywords()
output_json = 'output.json'
debug_log = 'debug.log'

#remaining_keyword_n = get_remaining_keywords_MySQL()
remaining_keyword_n = get_remaining_keywords()


proxy_user = 'ibeppo993'
proxy_pass = 'Ta802Ta802'
domain = 'www.google.it'
gl = 'it'
hl = 'IT'
uule = 'w+CAIQICIFSXRhbHk'

while remaining_keyword_n > 0:
    def_date_time = get_now_time()
    #keyword = get_keyword_MySQL()
    keyword = get_keyword()
    print(keyword)
    #proxy = get_proxy_MySQL()
    proxy = get_proxy()
    print(proxy)

    # Create a new instance of the Chrome driver
    option = webdriver.ChromeOptions()
    ua = UserAgent()
    userAgent = ua.random
    #option.add_argument("--headless")
    option.add_argument('--incognito')
    #option.add_argument(f'--user-agent={userAgent}')
    option.add_argument("--window-size=1920,1080")
    option.add_argument("--disable-infobars")
    option.add_argument("--disable-popup-blocking")
    option.add_argument('--disable-blink-features=AutomationControlled')
    option.add_argument(f'proxy-server={proxy}')
    option.add_argument('--no-first-run --no-service-autorun --password-store=basic')
    option.add_experimental_option("excludeSwitches", ["enable-automation"])
    option.add_argument('--disable-blink-features=AutomationControlled')
    option.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Remote(f'{docker_url}wd/hub',options = option)
    #driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=option)
    
    # stealth(driver,
    #         languages=["en-US", "en"],
    #         vendor="Google Inc.",
    #         platform="Win32",
    #         webgl_vendor="Intel Inc.",
    #         renderer="Intel Iris OpenGL Engine",
    #         fix_hairline=True,
    #         )
    # driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    # "source": """
    #     Object.defineProperty(navigator, 'webdriver', {
    #     get: () => undefined
    #     })
    # """
    # })
    # Go to the Google home page
    url = get_url_to_scrape(keyword, domain, uule, hl, gl)
    #driver.get('https://bot.sannysoft.com/')
    #time.sleep(5)
    driver.get(url)
    time.sleep(3)
    random_number = random.choice([1,2])
    if random_number == 1:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # driver.refresh()

    check_captcha = driver.current_url
    captcha_url = 'sorry/index?continue='
    print(check_captcha)
    if captcha_url in check_captcha:
        print('------------ richiesta captcha')
        print(check_captcha)
        #rehab_keyword_MySQL(keyword)
        #postpone_proxy_MySQL(proxy)
        rehab_keyword(keyword)
        postpone_proxy(proxy)
        log_telegram = telegram_bot_sendtext(f"{def_date_time}\nkw mancanti {remaining_keyword_n}\n{proxy}\n{keyword}\n{docker_url}\nRichiesta Captcha")

        #log
        with open(debug_log, 'a') as f:
            f.write(f"{proxy};"+time.strftime('%Y%m%d-%H%M%S')+f";Richiesta Captcha;{keyword};{docker_url}\n")

        driver.quit()

        #remaining_keyword_n = get_remaining_keywords_MySQL()
        remaining_keyword_n = get_remaining_keywords()

    else:
        HTML_DOM = driver.execute_script("return document.documentElement.outerHTML")
        keyword_enc = urllib.parse.quote_plus(keyword)
        
        with open(f'html_output/{def_date_time}-{keyword_enc}.html', 'w+') as f:
            f.write(HTML_DOM)
            f.close()

        SERP_dict = [{
            "keyword": keyword,
            "proxy": proxy,
            "url": driver.current_url,
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

        #remaining_keyword_n = get_remaining_keywords_MySQL()
        remaining_keyword_n = get_remaining_keywords()
        print(remaining_keyword_n)
        if int(remaining_keyword_n) % 100 == 0:
            log_telegram = telegram_bot_sendtext(f"{def_date_time}\nkw mancanti {remaining_keyword_n}\n{proxy}\n{keyword}\n{docker_url}\nRichiesta Eseguite")
