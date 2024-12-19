from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class Helper:
  def __init__(self, driver, logging):
    self.driver = driver
    self.logging = logging

  def el(self, selector, parent=None):
    try:
      if parent is None:
        parent = self.driver
      res = WebDriverWait(parent, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
      )
      self.logging.debug(f'Searching for: {selector}; Found')
      return res
    except:
      self.logging.debug(f'Searching for: {selector}; Not found')

  def els(self, selector, parent=None):
    try:
      if parent is None:
        parent = self.driver
      res = WebDriverWait(parent, 10).until(
          EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
      )
      self.logging.debug(f'Searching for: {selector}; Found')
      return res
    except:
      self.logging.debug(f'Searching for: {selector}; Not found')

  def el_quick(self, selector, parent=None):
    try:
      if parent is None:
        parent = self.driver
      res = parent.find_element(By.CSS_SELECTOR, selector)
      self.logging.debug(f'Quick searching for: {selector}; Found')
      return res
    except:
      self.logging.debug(f'Quick searching for: {selector}; Not found')

  def click(self, selector, parent=None):
    self.logging.debug(f'Clicking: {selector}')
    if parent is None:
      parent = self.driver
    self.el(selector, parent).click()
    self.logging.debug(f'Clicked')

  def click_quick(self, selector, parent=None):
    self.logging.debug(f'Quick clicking: {selector}')
    if parent is None:
      parent = self.driver
    self.el_quick(selector, parent).click()
    self.logging.debug(f'Clicked')

  def type(self, selector, text, parent=None):
    self.logging.debug(f'Typing: {text} into: {selector}')
    if parent is None:
      parent = self.driver
    self.el(selector, parent).send_keys(text)
    self.logging.debug(f'Typed')

  def print_res(self, res):
    for i, element in enumerate(res):
      type_str = f"(Type: {element.get_attribute('type')})" if element.tag_name == 'input' else ''
      print(f"\nElement {i + 1}:")
      print(f"Tag: {element.tag_name} {type_str}")
      if element.tag_name == 'input' or element.tag_name == 'select':
        print(f"Value: {element.get_attribute('value')}")
      if element.tag_name == 'label':
        print(f"Text: {element.text}")
      
      # If it's a select element, print options
      if element.tag_name == 'select':
        options = element.find_elements(By.TAG_NAME, 'option')
        print("Options:", [opt.text for opt in options[:10]], ('...' if len(options) > 10 else ''))