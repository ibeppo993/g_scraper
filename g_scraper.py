from seleniumwire import webdriver  # Import from seleniumwire
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from initialize import *

create_necessary_folder()
create_db_proxy()
create_db_keywords()
proxy_user = 'ibeppo993'
proxy_pass = 'Ta802Ta802'

# Create a new instance of the Chrome driver
option = webdriver.ChromeOptions()
option.add_argument('--incognito')
option.add_argument("--window-size=1920,1080")

proxy = get_proxy()
print(proxy)
options_seleniumWire = {
    'proxy': {'https': f'https://{proxy_user}:{proxy_pass}@{proxy}',},
}


driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options = option, seleniumwire_options = options_seleniumWire)

# Go to the Google home page
url = 'https://www.ilmioip.it/'
driver.get(url)

# Access requests via the `requests` attribute
for request in driver.requests:
    str_request = str(request)
    #print(str_request)
    #print(type(str_request))
    if str_request == url:
        print(
           request.url,
           request.response.status_code,
           request.response.headers['Content-Type']
        )