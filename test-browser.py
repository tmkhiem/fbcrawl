from selenium import webdriver

options = webdriver.FirefoxOptions()
options.binary_location = r'D:\Downloads\FirefoxPortableLegacy115\App\Firefox64\firefox.exe'
#options.add_argument('-headless')
options.set_preference('permissions.default.image', 2)

browser = webdriver.Firefox(options=options)
browser.get('https://www.facebook.com/photo.php?fbid=708779087961738&set=pb.100064889581944.-2207520000&type=3')
input()
