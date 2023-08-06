import os
import sys
from selenium import webdriver

def to_png(url, outfile):
    folder = os.path.dirname(__file__)
    driver = webdriver.PhantomJS(service_log_path='/tmp/ghostdriver.log')
    driver.set_window_size(1024, 800)
    driver.get(url)
    driver.save_screenshot(outfile)
    driver.quit()

