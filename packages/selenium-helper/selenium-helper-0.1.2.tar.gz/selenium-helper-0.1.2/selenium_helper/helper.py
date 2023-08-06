from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from .exceptions import UnkownExcelTypeFile
from typing import Generator
from abc import ABCMeta
import pandas as pd
from os.path import exists

class Helper(metaclass = ABCMeta):

	def send_keys_by_xpath(self, xpath: str, value: str) -> bool:
		element = self.driver.find_element_by_xpath(xpath)

		if element is None:
			return

		# clear
		element.clear()
		# send keys now
		element.send_keys(value)

	def get_input(self, to_print: str, input_style: str = '>>| ') -> str:
		print(to_print)

		return input(input_style)

	def click_by_xpath(self, xpath, ignore_error = True) -> bool:
		try:
			element = self.driver.find_element_by_xpath(xpath)
		except NoSuchElementException as e:
			return 

		if ignore_error:
			try:
				element.click()
				return True
			except Exception as e:
				return False
				pass
		else:
			element.click()

	def read_excel(self, file_addr: str) -> Generator:
		ext = file_addr.split('.')[-1].lower()

		if ext == 'csv':
			df = pd.read_csv(file_addr, na_filter = False)
		elif ext == 'xlsx':
			df = pd.read_excel(file_addr, na_filter = False)
		else:
			raise UnkownExcelTypeFile('Given File is not CSV or XLSX')

		return df.iterrows()

	def store_excel(self, data: list or dict, output: str, column_order: list = []):
		exts = ['csv', 'xlsx']

		if type(data) is dict:
			data = [data]

		df = pd.DataFrame(data)

		if len(column_order) >= 2:
			df = df[column_order]

		ext = output.split('.')[-1].lower()

		if not ext in exts:
			raise UnkownExcelTypeFile('Unkown "{}" extension for excel!'.format(ext))

		if ext == 'csv':

			if exists(output):
				df.to_csv(output, header = False, index = False, mode = 'a')
			else:
				df.to_csv(output, index = False)

		elif ext == 'xlsx':

			df.to_excel(output)

	def open_link_in_new_tab(self, element: WebElement):
		actions = ActionChains(self.driver)

		actions.key_down(Keys.CONTROL)
		actions.click(element)
		actions.key_up(Keys.CONTROL)
		actions.perform()

		return True