#!/usr/bin/python
# -*- coding: utf8 -*-
"""iq-bot"""
__author__ = 'ninja_zee'
from win32gui import FindWindow, FindWindowEx, SendMessage
from win32con import EM_GETLINE
from struct import pack
from time import localtime, strftime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException
import sys

#Config
URL = 'https://iqoption.com/ru'
URL_BINAR = "https://iqoption.com/ru/options/binary"
URL_TURBO = "https://iqoption.com/ru/options/turbo"
LOGIN_EMAIL = ''
LOGIN_PWD = ''
TITLE = u'Alert'
WINDOW_ID = '#32770'
TIMEOUT = 10
BUY_TEXT = 'Buy'
SELL_TEXT = 'Sell'

#Locators
LOGIN_BUTTON = '//button[@ng-click="login()"]'
EMAIL = '//input[@name="email"]'
PASSWORD = '//input[@name="password"]'
SUBMIT = '//button[@type="submit"]'
BUY_UP_BUTTON = '//button[contains(@ng-click,"call")]'
BUY_DOWN_BUTTON = '//button[contains(@ng-click,"put")]'
BUY_UP_CONFIRM_BUTTON = '//button[contains(@ng-show, "call")][text()="Купить"]'
BUY_DOWN_CONFIRM_BUTTON = '//button[contains(@ng-show, "put")][text()="Купить"]'
CONTINUE_BUTTON = """//button[contains(@ng-click, "opt.game.newRate()")]
[text()="Продолжить демо-торги"]"""
BALANCE = '//a[contains(@value,"user.profile.balance")]'
CLOSE_BUTTON = '//button[ng-click="close()"]'


class Iq():
    """
    Iq-bot class
    """

    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.browser = webdriver.Chrome(chrome_options=self.options)
        self.browser.implicitly_wait(TIMEOUT)
        self.start_session()

    @property
    def get_time(self):
        """ Получаем текущее локальное время """
        return strftime("%Y-%m-%d %H:%M:%S", localtime())

    def check_login(self):
        """ Ищем кнопку логина """
        try:
            self.browser.find_element_by_xpath(LOGIN_BUTTON)
            return False
        except NoSuchElementException:
            assert 0, u'Не могу найти элемент %s' % LOGIN_BUTTON
            return True

    def get_balance(self):
        """ Получаем текущий баланс """
        balance = self.browser.find_element_by_xpath(BALANCE).text
        return balance

    def login_action(self):
        """ Логинимся """
        if not self.check_login():
            print u'%s Логинемся на %s' % (self.get_time, URL)
            self.browser.find_element_by_xpath(LOGIN_BUTTON).click()
            self.browser.find_element_by_xpath(EMAIL).send_keys(LOGIN_EMAIL)
            self.browser.find_element_by_xpath(PASSWORD).send_keys(LOGIN_PWD)
            self.browser.find_element_by_xpath(SUBMIT).click()
            # Ждем появления нав бара
            WebDriverWait(self.browser, 10).until(ec.presence_of_element_located((By.ID,
                                                                                  "bs-example-navbar-collapse-1")))
        else:
            print u'%s Уже залогинен...' % self.get_time
        #sleep(TIMEOUT)

    @property
    def get_message_text(self):
        """ Получаем win32 MT Alert window/panel/message Текст """
        window = FindWindow(WINDOW_ID, TITLE)
        panel = FindWindowEx(window, 0, "Edit", None)
        bufferlength = pack('i', 255)
        linetext = bufferlength + "".ljust(253)
        linelength = SendMessage(panel, EM_GETLINE,
                                 0, linetext)
        text = ''.join((linetext[:linelength]))
        return text

    def continue_button_exist(self):
        """ Ищем кнопку Продолжить торги """
        try:
            self.browser.find_element_by_xpath(CONTINUE_BUTTON)
            return True
        except NoSuchElementException:
            return False

    def continue_action(self):
        """ Нажимаем кнопку Продолжить торги """
        while not self.continue_button_exist():
            pass
        try:
            self.browser.find_element_by_xpath(CONTINUE_BUTTON).click()
        except NoSuchElementException:
            try:
                self.browser.find_element_by_xpath(CLOSE_BUTTON).click()
            except NoSuchElementException:
                self.browser.refresh()

    def sell_buy_action(self, action):
        """ Покупаем/продаем """
        if action == BUY_TEXT:
            print u'%s Покупаем...' % self.get_time
            self.browser.find_element_by_xpath(BUY_UP_BUTTON).click()
            self.browser.find_element_by_xpath(BUY_UP_CONFIRM_BUTTON).click()
        elif action == SELL_TEXT:
            print u'%s Продаем...' % self.get_time
            self.browser.find_element_by_xpath(BUY_DOWN_BUTTON).click()
            self.browser.find_element_by_xpath(BUY_DOWN_CONFIRM_BUTTON).click()
        else:
            print u'%s Нет информации о продаже/покупке' % self.get_time

    def check_result(self, begin_balance):
        """ Получаем новый баланс """
        print u'%s Ждем результата...' % self.get_time
        #sleep(TIMEOUT)
        end_balance = self.get_balance()
        profit = float(end_balance) - float(begin_balance)
        print u'%s Новый баланс = %s(%s)' % (self.get_time,
                                             end_balance, profit)

    def wait_message_update(self, work_message):
        """ Проверяем уникальность сообщения """
        print u'%s Ждем сообщение от MT alert...' % self.get_time
        while work_message == self.get_message_text:
            pass
        print u'%s Сообщение от MT Alert: "%s"' % (self.get_time,
                                                   self.get_message_text)
        updated_message = self.get_message_text
        return updated_message

    def start_session(self):
        """ Запуск сессии """
        if len(sys.argv) > 1:
            if sys.argv[1] == "turbo":
                turbo = True
            else:
                turbo = False
        else:
            turbo = False

        print u'%s Запускаемся...' % self.get_time
        self.browser.get(URL)
        self.login_action()

        if turbo:
            print u'%s Переходим на %s' % (self.get_time, URL_TURBO)
            self.browser.get(URL_TURBO)
        else:
            print u'%s Переходим на %s' % (self.get_time, URL_BINAR)
            self.browser.get(URL_BINAR)
        self.get_balance()

        while True:
            begin_balance = self.get_balance()
            work_message = self.get_message_text
            updated_message = self.wait_message_update(work_message)
            decision = make_decision(updated_message)
            self.sell_buy_action(decision)
            self.continue_action()
            self.check_result(begin_balance)
            print '-' * 19

    def stop_session(self):
        """ Close Browser """
        self.browser.close()


def make_decision(work_message):
    """ Ищем информацию о продаже/покупке в сообщении """
    if BUY_TEXT in work_message:
        return BUY_TEXT
    elif SELL_TEXT in work_message:
        return SELL_TEXT


if __name__ == '__main__':
    Iq()
