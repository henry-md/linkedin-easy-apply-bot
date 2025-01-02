from selenium.webdriver.support.ui import WebDriverWait # type: ignore
from selenium.webdriver.support import expected_conditions as EC # type: ignore
from selenium.webdriver.common.by import By # type: ignore

class Helper:
  def __init__(self, driver, logging):
    self.driver = driver
    self.logging = logging

  def el_slow(self, selector, parent=None):
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

  def els_slow(self, selector, parent=None):
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

  def el(self, selector, parent=None):
    try:
      if parent is None:
        parent = self.driver
      res = parent.find_element(By.CSS_SELECTOR, selector)
      self.logging.debug(f'Quick searching for: {selector}; Found')
      return res
    except:
      self.logging.debug(f'Quick searching for: {selector}; Not found')

  def click_slow(self, selector, parent=None, driver=None):
    self.logging.debug(f'Clicking: {selector}')
    if parent is None:
      parent = self.driver
    element = self.el_slow(selector, parent)
    if not element: raise Exception(f'Element not found, so can\'t click: {selector}')
    if driver is None:
      element.click()
    else:
      driver.execute_script("arguments[0].click();", element)
    self.logging.debug(f'Clicked')

  def click(self, selector, parent=None, driver=None):
    self.logging.debug(f'Quick clicking: {selector}')
    if parent is None:
      parent = self.driver
    element = self.el(selector, parent)
    if not element: raise Exception(f'Element not found, so can\'t click: {selector}')
    if driver:
      driver.execute_script("arguments[0].click();", element)
    else:
      element.click()
    self.logging.debug(f'Clicked')

  def type(self, selector, text, parent=None):
    self.logging.debug(f'Typing: {text} into: {selector}')
    if parent is None:
      parent = self.driver
    self.el_slow(selector, parent).send_keys(text)
    self.logging.debug(f'Typed')

  def stringify_elements(self, res):
    element_text = []
    for i, element in enumerate(res):
      # Handle warning messages
      if element.tag_name == 'span' and element.get_attribute('class') == 'artdeco-inline-feedback__message':
        element_text.append(f"Warning (element {i + 1}): {element.text}")
        continue
      
      # Handle all other form elements
      type_str = f" (Type: {element.get_attribute('type')})" if element.tag_name == 'input' else ''
      curr_element_text = f"Element {i + 1}: HTML Tag: {element.tag_name}{type_str}; "
      # Check input and selection default value
      if element.tag_name == 'input' or element.tag_name == 'select':
        default_value = element.get_attribute('value')
        curr_element_text += f"Default Value: '{default_value}'; "
      # Check label and span inner text
      if element.tag_name == 'label' or element.tag_name == 'span':
        try:
          child_span = element.find_element(By.CSS_SELECTOR, "span:not([class*='hidden'])")
          curr_element_text += f"Inner Text: '{child_span.text}'; "
        except:
          curr_element_text += f"Inner Text: '{element.text}'; "
      # Check selection options
      if element.tag_name == 'select':
        options = element.find_elements(By.TAG_NAME, 'option')
        curr_element_text += f"Options: {[opt.text for opt in options[:10]]}{' & other options...' if len(options) > 10 else ''}; "
      # Check if span or label is required
      if element.tag_name == 'span' or element.tag_name == 'label':
        parent = element.find_element(By.XPATH, './..')
        after_parent = self.driver.execute_script(
          "return window.getComputedStyle(arguments[0], '::after').getPropertyValue('content');",
          parent
        )
        after_element = self.driver.execute_script(
          "return window.getComputedStyle(arguments[0], '::after').getPropertyValue('content');",
          element
        )
        is_required = after_parent.strip('"') == '*' or after_element.strip('"') == '*'
        if is_required: curr_element_text += f"Required: {is_required}; "
      element_text.append(curr_element_text)
    return element_text
