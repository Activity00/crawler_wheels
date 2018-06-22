# coding: utf-8

"""
@author: 武明辉 
@time: 2018/6/21 16:20
"""
import random
import time

from PIL import ImageDraw, ImageChops
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from utils import base64_to_image, thresholding


class SlideVerification:
    def __init__(self, executable_path='chromedriver'):

        self.driver = webdriver.Chrome(executable_path)

    def vertify(self, url, slide_elem_xpath, img_box_xpath, wait_elems_xpath=None, ):
        self.driver.get(url)
        # 等待页面重新所需元素加载
        for xp in wait_elems_xpath:
            WebDriverWait(self.driver, 30).until(lambda the_driver: the_driver.find_element_by_xpath(xp).is_displayed())

        # 找到滑动的块
        element = self.driver.find_element_by_xpath(slide_elem_xpath)
        # 滑动码图片块元素
        img_box = self.driver.find_element_by_xpath(img_box_xpath)

        # 点住滑块不放
        ActionChains(self.driver).click_and_hold(on_element=element).perform()
        time.sleep(1)

        # 滚动屏幕到滑动验证码位置方便截图
        win_height = self.driver.get_window_size()['height']
        self.driver.execute_script('scrollTo(0,{})'.format((2 * img_box.location['y'] - img_box.size['height']) // 2 - win_height // 2))
        # 全屏图片
        # driver.get_screenshot_as_file('C:\\Users\\lenovo\\Desktop\\a.png')
        full_screen_img_str = self.driver.get_screenshot_as_base64()
        full_img = base64_to_image(full_screen_img_str)

        img = self._get_vertify_img(full_img, img_box.location_once_scrolled_into_view, img_box.size)
        offset = self._get_block_offset(img)

        track_list = self._get_track_list(offset - 10)
        half_elem_size = element.size['width'] // 2
        # 拖动元素（注意这里位置是相对于元素左上角的相对值）
        for i in track_list:
            xoffset = i + half_elem_size
            ActionChains(self.driver).move_to_element_with_offset(to_element=element, xoffset=xoffset, yoffset=0).perform()
            time.sleep(random.randint(1, 5) / 1000)

        # 释放鼠标
        ActionChains(self.driver).release(on_element=element).perform()
        time.sleep(3)
        return True

    @staticmethod
    def _get_vertify_img(full_img, location, size):
        left = location['x']
        top = location['y']
        right = left + size['width']
        bottom = top + size['height']
        new_img = full_img.crop((left, top, right, bottom))
        return new_img

    @staticmethod
    def _get_block_offset(img):
        # 灰度与二值化
        img = thresholding(img.convert('L'), 50)
        i, j = img.size
        offset = 0
        flat = False
        for x in range(70, i):
            for y in range(j):
                if img.getpixel((x, y)) == 0:
                    offset = x
                    flat = True
                    break
            if flat:
                break
        # img.save('aaa.png')
        return offset

    @staticmethod
    def _get_block_offset2(img):
        # 灰度与二值化
        img = thresholding(img.convert('L'), 50)
        i, j = img.size
        img_tmp = img.copy()
        draw = ImageDraw.Draw(img_tmp)
        draw.rectangle([70, 0, i, j], 1)
        df = ImageChops.difference(img, img_tmp)
        offset = 0
        if df:
            offset = df.getbbox()[0]
        return offset

    @staticmethod
    def _get_track_list(offset):
        _list = []
        x = random.randint(1, 3)
        while offset - x >= 5:
            _list.append(x)
            offset = offset - x
            x = random.randint(1, 3)

        for _ in range(offset):
            _list.append(1)
        return _list


if __name__ == '__main__':
    sv = SlideVerification(executable_path='D:/Program Files (x86)/browser_drivers/chromedriver')
    kwargs = {
        'url': 'http://localhost:8000/',
        'slide_elem_xpath': '//div[@class="gt_slider_knob gt_show"]',
        'img_box_xpath': '//div[@class="gt_box"]',
        'wait_elems_xpath': [
            '//div[@class="gt_cut_bg gt_show"]',
            '//div[@class="gt_cut_fullbg gt_show"]',
           '//div[@class="gt_box"]'
        ],
    }
    result = sv.vertify(**kwargs)
    print(result)
