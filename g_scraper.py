from seleniumwire import webdriver  # Import from seleniumwire
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

# Create a new instance of the Chrome driver
option = webdriver.ChromeOptions()
#option.add_argument("--headless")
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

for request in driver.requests:
    str_request = str(request)
    #print(type(str_request))
    if str_request == url:
        if request.response.status_code != 200:
            print('------------ richiesta captcha')
            rehab_keyword(keyword)
            postpone_proxy(proxy)

        else:
            print(request.url)
            print(request.response.status_code)
            print(request.response.headers['Content-Type'])

            HTML_DOM = driver.execute_script("return document.documentElement.outerHTML")

            keyword_enc = urllib.parse.quote_plus(keyword)
            proxy_enc = urllib.parse.quote_plus(proxy)
            def_date_time = get_now_time()
            with open(f'html_output/{def_date_time}-{proxy_enc}-{keyword_enc}.html', 'w+') as f:
                f.write(HTML_DOM)
                f.close()

            SERP_dict = [{
            "keyword": keyword,
            "proxy": proxy,
            "url": request.url,
            "staus_code": request.response.status_code,
            "header": request.response.headers['Content-Type']
            }]
            with open("output.json", "r+") as file:
                data = json.load(file)
                data.update(SERP_dict)
                file.seek(0)
                json.dump(data, file)

            driver.close()
