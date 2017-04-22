# -*- coding: utf-8 -*-
import os
import time
from selenium import webdriver
from io import BytesIO

from PIL import Image
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


os.chdir(r'.')

driver = webdriver.Chrome('./chromedriver.exe')
driver.get("https://www.jianshu.com/sign_in")

while 1:

    time.sleep(0.2)
    # 设定窗口大小
    width = 1280
    height = 800
    driver.set_window_size(width, height)

    def get_captcha_image(filename):

        screenshot = driver.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        # screenshot.show()

        captcha_el = driver.find_element_by_class_name("gt_box")
        location = captcha_el.location
        size = captcha_el.size
        left = location['x']
        top = location['y']
        right = location['x'] + size['width']
        bottom = location['y'] + size['height']
        box = (left, top, right, bottom)
        print(box)
        if box[0] == 0:
            raise(Exception('======='))
        captcha_image = screenshot.crop(box)
        captcha_image.save(filename)  # "%s.png" % uuid.uuid4().hex
        print(u'截图成功')

    time.sleep(1)
    WebDriverWait(driver, 8).until(
        EC.presence_of_element_located((By.CLASS_NAME, "gt_box")))
    knob = driver.find_element_by_class_name("gt_slider_knob")
    action = ActionChains(driver)
    action.move_to_element_with_offset(knob, 21, 21).perform()
    time.sleep(1)
    f_file = 'f-%s.png' % time.strftime("%Y%m%d-%H%M%S")
    get_captcha_image(f_file)
    ActionChains(driver).click_and_hold().perform()
    time.sleep(0.5)
    # action.drag_and_drop_by_offset(knob, x_offset, y_offset).perform()
    s_file = 's-%s.png' % time.strftime("%Y%m%d-%H%M%S")
    get_captcha_image(s_file)
    # action.move_by_offset(50, 0).release().perform()
    # action.reset_actions()

    # --------------------------------------------------------------
    import matplotlib.pylab as plt
    from PIL import Image, ImageFilter
    from PIL import ImageChops 

    # 直观感受图片差异
    image_f = Image.open(f_file)
    image_s = Image.open(s_file)
    diff = ImageChops.difference(image_f, image_s)

    # ----------------------显示图片debug----------------------------
    '''
    # if diff.getbbox() is not None:
    diff.save('x.png')
    # plt.imshow(plt.imread('x.png'))
    # plt.show()

    fig, axs = plt.subplots(nrows=1, ncols=3)
    for im, ax in zip(["f.png", "s.png", "x.png"], axs):
        image = plt.imread(im)
        ax.imshow(image)
    plt.show()

    diff_image = Image.open('x.png')
    '''
    # -------------------------debug--------------------------------
    global first_left
    first_left = 0

    def find_offset(diff_image, offset_=62):

        d = diff_image.convert("L").point(lambda i: i > 52, mode='1')
        d.save('x-%s.png' % time.strftime("%Y%m%d-%H%M%S"))
        b1 = d.getbbox()  # left, upper, right, and lower pixel coordinate
        # offset_ = 65
        b2 = d.crop((offset_, 0, d.width, d.height)).getbbox()
        global first_left
        first_left = b1[0]
        offset = b2[0] + offset_ - b1[0] - 2
        if b2[0] <= 4:
            offset = -1
        return offset
        # diff = diff_image.load()
        # http://stackoverflow.com/questions/9038160/break-two-for-loops
        # for x in range(61, width):
        #     for y in range(height):
        #         if all(i > 40 for i in diff[x, y]):
        #             return x - 6

    offset = find_offset(diff)
    if offset < 0:
        # 拖动滑块到右方160像素处保持并截图
        ActionChains(driver).move_by_offset(160, 0).perform()
        time.sleep(0.5)
        # action.drag_and_drop_by_offset(knob, x_offset, y_offset).perform()
        s_file = 's-%s.png' % time.strftime("%Y%m%d-%H%M%S")
        get_captcha_image(s_file)
        # 放下
        ActionChains(driver).release().perform()
        image_s = Image.open(s_file)
        diff = ImageChops.difference(image_f, image_s)
        d = diff.convert("L").point(lambda i: i > 60, mode='1')
        offset = d.getbbox()[0] - first_left
        time.sleep(2.5)
        ActionChains(driver).move_to_element_with_offset(
            knob, 21, 21).click_and_hold().perform()
        time.sleep(0.5)
    print(offset)

    def get_offsets(setpointX):
        '''
        切记不能移动小数个像素位置
        '''
        kp = 3.0
        ki = 0.0001
        kd = 80.0

        x = 0
        vx = 0
        prevErrorX = 0
        integralX = 0
        derivativeX = 0

        while 1:
            if x >= setpointX:
                break

            errorX = setpointX - x
            # print('xxxxx - ', x)
            integralX += errorX
            derivativeX = errorX - prevErrorX
            prevErrorX = errorX
            if offset < 100:
                K = 0.007
            elif offset < 180:
                K = 0.006
            else:
                K = 0.005
            ax = K * (kp * errorX + ki * integralX + kd * derivativeX)
            vx += ax

            if x + vx > setpointX:
                vx = setpointX - x
            vx = int(vx)
            if vx < 1:
                vx = random.randint(1, 3)
            yield vx
            print('vvvvv - ', vx)
            x += vx

    def get_offsets_back(goal):

        x = 0
        while 1:
            if x >= goal:
                break
            dx = random.randint(10, 50)
            if x + dx > goal:
                dx = goal - x
            yield dx
            x += dx

    import random
    for o in get_offsets(offset):
        y = random.randint(-1, 1)
        ActionChains(driver).move_by_offset(o, y).perform()
        # time.sleep(0.03)
        time.sleep(random.randint(2, 4) / 100)
    ActionChains(driver).release().perform()
    # action.drag_and_drop_by_offset(knob, offset, 0).perform()
    time.sleep(3)
    driver.refresh()
