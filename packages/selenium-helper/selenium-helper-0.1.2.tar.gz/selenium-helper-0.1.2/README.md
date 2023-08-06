# Simple Selenium Helper package

## installtion

```
pip3 install selenium-helper --user
```

```
from selenium_helper import Helper
from selenium import webdriver


class TestDriver(Helper):

	def __init__(self):
		self.driver = webdriver.Chrome()

	def test(self):
		self.driver.get('https://www.google.com/')
		self.send_keys_by_xpath('//*[@id="lst-ib"]', 'hello')
		self.click_by_xpath('//*[@id="tsf"]/div[2]/div[3]/center/input[1]')

TestDriver().test()
```