#!python
# cython: language_level=3
 
import datetime
from itertools import permutations
import time , getpip
from swap import Uniswap
from web3 import Web3, middleware, _utils
from web3.gas_strategies.time_based import fast_gas_price_strategy, glacial_gas_price_strategy
from pycoingecko import CoinGeckoAPI
import pyetherbalance
import requests
import math
import subprocess
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QApplication, QPushButton, QTextEdit, QVBoxLayout, QWidget, QGraphicsObject
from PyQt5.QtCore import QCoreApplication
from PyQt5 import QtTest
import fileinput
import re
import importlib
import os
from time import localtime, strftime
from web3 import types
import traceback

sys.path.insert(0, './')
import configfile
import json
import requests

sys.setrecursionlimit(1500)

QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)  # enable highdpi scaling
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)  # use highdpi icons


def __ne__(self, other):
    return not self.__eq__(other)


cg = CoinGeckoAPI()


class Port(object):
    def __init__(self, view):
        self.view = view

    def flush(self):
        pass

    def write(self, text):
        cursor = self.view.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.view.setTextCursor(cursor)
        self.view.ensureCursorVisible()


@pyqtSlot(str)
def trap_exc_during_debug(*args):
    if configfile.debugmode == '1':
        exception_type, exception_object, exception_traceback = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)


sys.excepthook = trap_exc_during_debug


@pyqtSlot()
class Worker(QObject):
    sig_step = pyqtSignal(int, str)  # worker id, step description: emitted every step through work() loop
    sig_done = pyqtSignal(int)  # worker id: emitted at end of work()
    sig_msg = pyqtSignal(str)  # message to be shown to user

    def __init__(self, id: int):
        super().__init__()
        self.__id = id
        self.__abort = False

    def work(self):
        while self.__abort != True:
            thread_name = QThread.currentThread().objectName()
            thread_id = int(QThread.currentThreadId())  # cast to int() is necessary
            self.sig_msg.emit('Running worker #{} from thread "{}" (#{})'.format(self.__id, thread_name, thread_id))

            if 'step' not in locals():
                step = 1
            else:
                step = 1
            self.sig_step.emit(self.__id, 'step ' + str(step))
            QCoreApplication.processEvents()
            if self.__abort == True:
                # note that "step" value will not necessarily be same for every thread
                self.sig_msg.emit('Worker #{} aborting work at step {}'.format(self.__id, step))

            importlib.reload(configfile)
            w33 = Web3()
            cg = CoinGeckoAPI()
            maxgwei = int(configfile.maxgwei)
            if configfile.maxgweinumber == '':
                maxgweinumber = 0
            else:
                maxgweinumber = int(configfile.maxgweinumber)
            diffdeposit = float(configfile.diffdeposit)
            diffdepositaddress = str(configfile.diffdepositaddress)
            speed = str(configfile.speed)
            max_slippage = float(configfile.max_slippage)
            incaseofbuyinghowmuch = int(configfile.incaseofbuyinghowmuch)
            ethtokeep = int(configfile.ethtokeep)
            timesleepaftertrade = int(configfile.secondscheckingprice_2)
            timesleep = int(configfile.secondscheckingprice)
            infura_url = str(configfile.infuraurl)
            infuraurl = infura_url
            tokentokennumerator = float(configfile.tokentokennumerator)
            mcotoseeassell = float(configfile.mcotoseeassell)
            debugmode = int(configfile.debugmode)

            ##for token_number,eth_address,high,low,activate,stoploss_value,stoploss_activate,trade_with_ERC,trade_with_ETH,fast_token in all_token_information:
            all_token_information = [
                (1, str(configfile.token1ethaddress), float(configfile.token1high), float(configfile.token1low),
                 float(configfile.activatetoken1), float(configfile.token1stoploss), float(configfile.stoplosstoken1)
                 , float(configfile.tradewithERCtoken1), float(configfile.tradewithETHtoken1), '0',
                 str(configfile.token1name), int(configfile.token1decimals)),
                (2, str(configfile.token2ethaddress), float(configfile.token2high), float(configfile.token2low),
                 float(configfile.activatetoken2), float(configfile.token2stoploss), float(configfile.stoplosstoken2)
                 , float(configfile.tradewithERCtoken2), float(configfile.tradewithETHtoken2), '0',
                 str(configfile.token2name), int(configfile.token2decimals)),
                (3, str(configfile.token3ethaddress), float(configfile.token3high), float(configfile.token3low),
                 float(configfile.activatetoken3), float(configfile.token3stoploss), float(configfile.stoplosstoken3)
                 , float(configfile.tradewithERCtoken3), float(configfile.tradewithETHtoken3), '0',
                 str(configfile.token3name), int(configfile.token3decimals)),
                (4, str(configfile.token4ethaddress), float(configfile.token4high), float(configfile.token4low),
                 float(configfile.activatetoken4), float(configfile.token4stoploss), float(configfile.stoplosstoken4)
                 , float(configfile.tradewithERCtoken4), float(configfile.tradewithETHtoken4), '0',
                 str(configfile.token4name), int(configfile.token4decimals)),
                (5, str(configfile.token5ethaddress), float(configfile.token5high), float(configfile.token5low),
                 float(configfile.activatetoken5), float(configfile.token5stoploss), float(configfile.stoplosstoken5)
                 , float(configfile.tradewithERCtoken5), float(configfile.tradewithETHtoken5), '0',
                 str(configfile.token5name), int(configfile.token5decimals)),
                (6, str(configfile.token6ethaddress), float(configfile.token6high), float(configfile.token6low),
                 float(configfile.activatetoken6), float(configfile.token6stoploss), float(configfile.stoplosstoken6)
                 , float(configfile.tradewithERCtoken6), float(configfile.tradewithETHtoken6), '0',
                 str(configfile.token6name), int(configfile.token6decimals)),
                (7, str(configfile.token7ethaddress), float(configfile.token7high), float(configfile.token7low),
                 float(configfile.activatetoken7), float(configfile.token7stoploss), float(configfile.stoplosstoken7)
                 , float(configfile.tradewithERCtoken7), float(configfile.tradewithETHtoken7), '0',
                 str(configfile.token7name), int(configfile.token7decimals)),
                (8, str(configfile.token8ethaddress), float(configfile.token8high), float(configfile.token8low),
                 float(configfile.activatetoken8), float(configfile.token8stoploss), float(configfile.stoplosstoken8)
                 , float(configfile.tradewithERCtoken8), float(configfile.tradewithETHtoken8), '0',
                 str(configfile.token8name), int(configfile.token8decimals)),
                (9, str(configfile.token9ethaddress), float(configfile.token9high), float(configfile.token9low),
                 float(configfile.activatetoken9), float(configfile.token9stoploss), float(configfile.stoplosstoken9)
                 , float(configfile.tradewithERCtoken9), float(configfile.tradewithETHtoken9), '0',
                 str(configfile.token9name), int(configfile.token9decimals)),
                (10, str(configfile.token10ethaddress), float(configfile.token10high), float(configfile.token10low),
                 float(configfile.activatetoken10), float(configfile.token10stoploss), float(configfile.stoplosstoken10)
                 , float(configfile.tradewithERCtoken10), float(configfile.tradewithETHtoken10), '0',
                 str(configfile.token10name), int(configfile.token10decimals))]

            # its now: for token_number,eth_address,high,low,activate,stoploss_value,stoploss_activate,trade_with_ERC,trade_with_ETH,fast_token,small_case_name,decimals in all_token_information:

            for token_number, eth_address, high, low, activate, stoploss_value, stoploss_activate, trade_with_ERC, trade_with_ETH, fast_token, small_case_name, decimals in all_token_information:
                if (high < low):
                    print(
                        'Stop the script, a tokenlow is higher than its tokenhigh')
                    count = 0
                    QCoreApplication.processEvents()
                    while self.__abort != True:
                        QCoreApplication.processEvents()
                        pass
                if (stoploss_value > high):
                    print(
                        'Stop the script, a stoploss is higher than the tokenhigh')
                    count = 0
                    QCoreApplication.processEvents()
                    while self.__abort != True:
                        QCoreApplication.processEvents()
                        pass
                if (ethtokeep > mcotoseeassell):
                    print(
                        'The buy/sell boundary is lower than the $ to keep in BNB after trade')
                    count = 0

            my_address = str(configfile.my_address)
            private_key = str(configfile.private_key)

            pk = private_key
            if configfile.maincoinoption == 'BNB':
                ethaddress = "0x0000000000000000000000000000000000000000"
                maindecimals = 18
            if configfile.maincoinoption == 'DAI':
                ethaddress = "0x1af3f329e8be154074d8769d1ffa4ee058b1dbc3"
                maindecimals = 18
            if configfile.maincoinoption == 'BUSD':
                ethaddress = "0xe9e7cea3dedca5984780bafc599bd69add087d56"
                maindecimals = 18
            if configfile.maincoinoption == 'USDC':
                ethaddress = "0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d"
                maindecimals = 18
            if configfile.maincoinoption == 'wBTC':
                ethaddress = "0x7130d2a12b9bcbfae4f2634d864a1ee1ce3ead9c"
                maindecimals = 18
            if configfile.maincoinoption == 'ETH':
                ethaddress = "0x2170ed0880ac9a755fd29b2688956bd959f933f8"
                maindecimals = 18
            maincoinname = configfile.maincoinoption
            maincoinoption = ethaddress
            append = QtCore.pyqtSignal(str)

            if 'step' not in locals():
                step = 1
            else:
                step = 1
            self.sig_step.emit(self.__id, 'step ' + str(step))
            QCoreApplication.processEvents()
            if self.__abort == True:
                # note that "step" value will not necessarily be same for every thread
                self.sig_msg.emit('Worker #{} aborting work at step {}'.format(self.__id, step))
            totaldollars = 1

            def gettotaltokenbalance(all_token_information, infura_url, ethaddress, maindecimals, my_address,
                                     ethtokeep):
                print('(re)Preparing bot...')
                QCoreApplication.processEvents()
                if 'step' not in locals():
                    step = 1
                else:
                    step = 1
                self.sig_step.emit(self.__id, 'step ' + str(step))
                QCoreApplication.processEvents()
                if self.__abort == True:
                    # note that "step" value will not necessarily be same for every thread
                    self.sig_msg.emit('Worker #{} aborting work at step {}'.format(self.__id, step))
                ethbalance = pyetherbalance.PyEtherBalance(infura_url)
                priceeth = int(
                    float((requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BNBUSDT').json())['price']))
                threeeth = 1
                ethereum_address = my_address
                try:  # balances
                    if ethaddress == "0x0000000000000000000000000000000000000000":
                        balance_eth = ethbalance.get_eth_balance(my_address)['balance']
                        dollarbalancemaintoken = priceeth * balance_eth
                    else:
                        details = {'symbol': 'potter', 'address': ethaddress, 'decimals': maindecimals,
                                   'name': 'potter'}
                        erc20tokens = ethbalance.add_token('potter', details)
                        balance_eth = ethbalance.get_token_balance('potter', ethereum_address)['balance']
                        maintokeneth = uniswap_wrapper.get_eth_token_input_price(w33.toChecksumAddress(ethaddress),
                                                                                 100)

                        if maindecimals != 18:
                            mainusd = (priceeth / (maintokeneth)) * 100
                        else:
                            mainusd = (priceeth / (maintokeneth)) * 100
                        dollarbalancemaintoken = mainusd * balance_eth

                    if len(all_token_information[0]) > 15:
                        all_token_information[0] = all_token_information[0][:15]
                        all_token_information[1] = all_token_information[1][:15]
                        all_token_information[2] = all_token_information[2][:15]
                        all_token_information[3] = all_token_information[3][:15]
                        all_token_information[4] = all_token_information[4][:15]
                        all_token_information[5] = all_token_information[5][:15]
                        all_token_information[6] = all_token_information[6][:15]
                        all_token_information[7] = all_token_information[7][:15]
                        all_token_information[8] = all_token_information[8][:15]
                        all_token_information[9] = all_token_information[9][:15]
                    if len(all_token_information[0]) > 14:
                        for token_number, eth_address, high, low, activate, stoploss_value, stoploss_activate, trade_with_ERC, trade_with_ETH, fast_token, small_case_name, decimals, balance, price, dollar_balance in all_token_information:
                            if eth_address != '0' or '':
                                erc20tokens = ethbalance.add_token(small_case_name,
                                                                   {'symbol': small_case_name, 'address': eth_address,
                                                                    'decimals': decimals,
                                                                    'name': small_case_name})
                                a = ethbalance.get_token_balance(small_case_name, ethereum_address)['balance']
                                all_token_information[token_number - 1] = all_token_information[token_number - 1][
                                                                          :12] + (a, all_token_information[
                                    token_number - 1][13], all_token_information[token_number - 1][14])
                            else:
                                a = 0
                                all_token_information[token_number - 1] = all_token_information[token_number - 1][
                                                                          :12] + (a, all_token_information[
                                    token_number - 1][13], all_token_information[token_number - 1][14])
                    else:
                        for token_number, eth_address, high, low, activate, stoploss_value, stoploss_activate, trade_with_ERC, trade_with_ETH, fast_token, small_case_name, decimals in all_token_information:
                            if eth_address != '0' or '':
                                details = {'symbol': small_case_name, 'address': eth_address, 'decimals': decimals,
                                           'name': small_case_name.upper}
                                erc20tokens = ethbalance.add_token(small_case_name.upper, details)
                                a = ethbalance.get_token_balance(small_case_name.upper, ethereum_address)['balance']
                                all_token_information[token_number - 1] = all_token_information[token_number - 1] + (a,)
                            else:
                                a = 0
                                all_token_information[token_number - 1] = all_token_information[token_number - 1] + (a,)
                    # its now: for token_number,eth_address,high,low,activate,stoploss_value,stoploss_activate,trade_with_ERC,trade_with_ETH,fast_token,small_case_name,decimals,balance in all_token_information:
                # Written by Aviddot: https://github.com/aviddot/Pancakeswap-v2-trading-bot
                except Exception as e:
                    exception_type, exception_object, exception_traceback = sys.exc_info()
                    if configfile.debugmode == '1':
                        print(str(e) + ' on line: ' + str(exception_traceback.tb_lineno))
                QCoreApplication.processEvents()
                if 'step' not in locals():
                    step = 1
                else:
                    step = 1
                self.sig_step.emit(self.__id, 'step ' + str(step))
                QCoreApplication.processEvents()
                if self.__abort == True:
                    # note that "step" value will not necessarily be same for every thread
                    self.sig_msg.emit('Worker #{} aborting work at step {}'.format(self.__id, step))
                try:  # prices
                    if len(all_token_information[0]) > 15:
                        all_token_information[0] = all_token_information[0][:15]
                        all_token_information[1] = all_token_information[1][:15]
                        all_token_information[2] = all_token_information[2][:15]
                        all_token_information[3] = all_token_information[3][:15]
                        all_token_information[4] = all_token_information[4][:15]
                        all_token_information[5] = all_token_information[5][:15]
                        all_token_information[6] = all_token_information[6][:15]
                        all_token_information[7] = all_token_information[7][:15]
                        all_token_information[8] = all_token_information[8][:15]
                        all_token_information[9] = all_token_information[9][:15]
                    priceeth = int(
                        float((requests.get(
                            'https://api.binance.com/api/v3/ticker/price?symbol=BNBUSDT').json())[
                                  'price']))

                    if len(all_token_information[0]) > 14:
                        for token_number, eth_address, high, low, activate, stoploss_value, stoploss_activate, trade_with_ERC, trade_with_ETH, fast_token, small_case_name, decimals, balance, price, dollar_balance in all_token_information:
                            if str(eth_address) != '0' or '':
                                token1eth = uniswap_wrapper.get_eth_token_input_price(
                                    w33.toChecksumAddress(eth_address),
                                    10000000000000)
                                if decimals != 18:
                                    pricetoken1usd = (priceeth / (token1eth)) / (10 ** (18 - (decimals)))
                                else:
                                    pricetoken1usd = (priceeth / (token1eth))
                                a = pricetoken1usd
                                all_token_information[token_number - 1] = all_token_information[token_number - 1][
                                                                          :13] + (a, all_token_information[
                                    token_number - 1][14])
                            else:
                                a = 0
                                all_token_information[token_number - 1] = all_token_information[token_number - 1][
                                                                          :13] + (a, all_token_information[
                                    token_number - 1][14])
                    else:
                        for token_number, eth_address, high, low, activate, stoploss_value, stoploss_activate, trade_with_ERC, trade_with_ETH, fast_token, small_case_name, decimals, balance in all_token_information:
                            if str(eth_address) != '0' or '':
                                try:
                                    token1eth = uniswap_wrapper.get_eth_token_input_price(
                                        w33.toChecksumAddress(eth_address),
                                        10000000000000)
                                    if decimals != 18:
                                        pricetoken1usd = (priceeth / (token1eth)) / (10 ** (18 - (decimals)))
                                    else:
                                        pricetoken1usd = (priceeth / (token1eth))
                                    a = pricetoken1usd
                                    all_token_information[token_number - 1] = all_token_information[token_number - 1][
                                                                              :13] + (a,)
                                except Exception as e:
                                    exception_type, exception_object, exception_traceback = sys.exc_info()
                                    if configfile.debugmode == '1':
                                        print(str(e) + ' on line: ' + str(exception_traceback.tb_lineno))
                                        e = (str(e))
                                    if 'Could not decode' in str(e):
                                        try:
                                            kanka = uniconnect.factory_contract.functions.getPair(
                                                w33.toChecksumAddress(eth_address),
                                                token22).call()
                                            kanka2 = uniconnect._load_contract(abi_name="erc20",
                                                                               address=w33.toChecksumAddress(
                                                                                   eth_address)).functions.balanceOf(
                                                kanka).call
                                            if kanka2 < 2:
                                                print(
                                                    'Token ' + str(token_number) + ' has no liquidity on Pancakeswap 2')
                                        except:
                                            print(
                                                'Token ' + str(token_number) + ' has no liquidity on Pancakeswap 2')
                                    b = None
                                    letsgoo = 0

                            else:
                                a = 0
                                all_token_information[token_number - 1] = all_token_information[token_number - 1] + (a,)

                    # its now: for token_number,eth_address,high,low,activate,stoploss_value,stoploss_activate,trade_with_ERC,trade_with_ETH,fast_token,small_case_name,decimals,balance,price in all_token_information:
                except Exception as e:
                    exception_type, exception_object, exception_traceback = sys.exc_info()
                    if configfile.debugmode == '1':
                        print(str(e) + ' on line: ' + str(exception_traceback.tb_lineno))
                totalbalancedollarscript = 0
                if len(all_token_information[0]) > 15:
                    all_token_information[0] = all_token_information[0][:15]
                    all_token_information[1] = all_token_information[1][:15]
                    all_token_information[2] = all_token_information[2][:15]
                    all_token_information[3] = all_token_information[3][:15]
                    all_token_information[4] = all_token_information[4][:15]
                    all_token_information[5] = all_token_information[5][:15]
                    all_token_information[6] = all_token_information[6][:15]
                    all_token_information[7] = all_token_information[7][:15]
                    all_token_information[8] = all_token_information[8][:15]
                    all_token_information[9] = all_token_information[9][:15]
                if len(all_token_information[0]) > 14:
                    for token_number, eth_address, high, low, activate, stoploss_value, stoploss_activate, trade_with_ERC, trade_with_ETH, fast_token, small_case_name, decimals, balance, price, dollar_balance in all_token_information:
                        if balance != 0:
                            a = price * balance * 100
                            all_token_information[token_number - 1] = all_token_information[token_number - 1][:14] + (
                            a,)
                        else:
                            a = 0
                            all_token_information[token_number - 1] = all_token_information[token_number - 1][:14] + (
                            a,)

                        totalbalancedollarscript += a
                        if token_number == 10:
                            totalbalancedollarscript += dollarbalancemaintoken
                else:
                    for token_number, eth_address, high, low, activate, stoploss_value, stoploss_activate, trade_with_ERC, trade_with_ETH, fast_token, small_case_name, decimals, balance, price in all_token_information:
                        if balance != 0:
                            a = price * balance * 100
                            all_token_information[token_number - 1] = all_token_information[token_number - 1] + (a,)
                        else:
                            a = 0
                            all_token_information[token_number - 1] = all_token_information[token_number - 1] + (a,)

                        totalbalancedollarscript += a
                        if token_number == 10:
                            totalbalancedollarscript += dollarbalancemaintoken

                # its now: for token_number,eth_address,high,low,activate,stoploss_value,stoploss_activate,trade_with_ERC,
                # trade_with_ETH,fast_token,small_case_name,decimals,balance,price, dollar_balance in all_token_information:

                maintokenbalance = balance_eth
                return {'all_token_information': all_token_information,
                        'totalbalancedollarscript': totalbalancedollarscript,
                        'dollarbalancemaintoken': dollarbalancemaintoken, 'maintokenbalance': maintokenbalance}

            # Written by Aviddot: https://github.com/aviddot/Pancakeswap-v2-trading-bot
            QCoreApplication.processEvents()
            if 'step' not in locals():
                step = 1
            else:
                step = 1
            self.sig_step.emit(self.__id, 'step ' + str(step))
            QCoreApplication.processEvents()
            if self.__abort == True:
                # note that "step" value will not necessarily be same for every thread
                self.sig_msg.emit('Worker #{} aborting work at step {}'.format(self.__id, step))

            def checkbalance(all_token_information, infura_url, my_address, maincoinoption, dollarbalancemaintoken,
                             mcotoseeassell):

                ethereum_address = my_address
                cg = CoinGeckoAPI()

                ethbalance = pyetherbalance.PyEtherBalance(infura_url)

                for token_number, eth_address, high, low, activate, stoploss_value, stoploss_activate, trade_with_ERC, trade_with_ETH, fast_token, small_case_name, decimals, balance, price, dollar_balance in all_token_information:
                    if (dollarbalancemaintoken > mcotoseeassell):
                        gelukt = "sell"
                    else:
                        lol543 = dollar_balance * 100000000000
                        if lol543 > mcotoseeassell:
                            gelukt = "buy " + small_case_name
                    keer = 0
                    if 'gelukt' not in locals():
                        gelukt = 'nothing'
                QCoreApplication.processEvents()
                if 'step' not in locals():
                    step = 1
                else:
                    step = 1
                self.sig_step.emit(self.__id, 'step ' + str(step))
                QCoreApplication.processEvents()
                if self.__abort == True:
                    # note that "step" value will not necessarily be same for every thread
                    self.sig_msg.emit('Worker #{} aborting work at step {}'.format(self.__id, step))
                for token_number, eth_address, high, low, activate, stoploss_value, stoploss_activate, trade_with_ERC, trade_with_ETH, fast_token, small_case_name, decimals, balance, price, dollar_balance in all_token_information:
                    if (dollarbalancemaintoken > mcotoseeassell and gelukt != "sell"):
                        gelukt2 = "sell"
                    else:
                        if dollar_balance > mcotoseeassell and gelukt != 'buy ' + small_case_name:
                            gelukt2 = "buy " + small_case_name
                    keer = 0
                    if 'gelukt2' not in locals():
                        gelukt2 = 'nothing'
                try:
                    gelukt3 = gelukt2
                except:
                    gelukt2 = '0'
                return {'keer': keer, 'gelukt': gelukt, 'gelukt2': gelukt2,
                        'all_token_information': all_token_information}

            def getprice(all_token_information, incaseofbuyinghowmuch, uniswap_wrapper, timesleep, gelukt,
                         maintokenbalance, ethaddress, maindecimals, totalbalancedollarscript):
                count = 0
                try:
                    QCoreApplication.processEvents()
                    # Written by Aviddot: https://github.com/aviddot/Pancakeswap-v2-trading-bot
                    while count < timesleep:
                        count = count + 1
                        QtTest.QTest.qWait(1000)
                        QCoreApplication.processEvents()
                    QtTest.QTest.qWait(166)
                    if ethaddress == "0x0000000000000000000000000000000000000000" and maintokenbalance > 0.001:
                        priceeth = int(float(
                            (requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BNBUSDT').json())[
                                'price']))
                        threeeth = int(maintokenbalance * 1000000000000000000)
                    if ethaddress == "0x0000000000000000000000000000000000000000" and maintokenbalance < 0.001:
                        threeeth = 1
                        priceeth = int(float(
                            (requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BNBUSDT').json())[
                                'price']))
                    if ethaddress != "0x0000000000000000000000000000000000000000":
                        if ethaddress == "0x1af3f329e8be154074d8769d1ffa4ee058b1dbc3":
                            jajaja = (float(
                                (requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BUSDDAI').json())[
                                    'price']))
                            priceeth = int(float(
                                (requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BNBUSDT').json())[
                                    'price']))
                            ethtest = (jajaja / priceeth) * maintokenbalance
                            if ethtest < 0.01:
                                threeeth = 1
                            else:
                                threeeth = int((ethtest) * 1000000000000000000)

                        if ethaddress == "0xe9e7cea3dedca5984780bafc599bd69add087d56":
                            jajaja = (float(
                                (requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BUSDUSDT').json())[
                                    'price']))
                            priceeth = int(float(
                                (requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BNBUSDT').json())[
                                    'price']))
                            ethtest = (jajaja / priceeth) * maintokenbalance

                            if ethtest < 0.01:
                                threeeth = 1
                            else:
                                threeeth = int((ethtest) * 1000000000000000000)

                        if ethaddress == "0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d":
                            jajaja = (float(
                                (requests.get('https://api.binance.com/api/v3/ticker/price?symbol=USDCBUSD').json())[
                                    'price']))
                            priceeth = int(float(
                                (requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BNBUSDT').json())[
                                    'price']))
                            ethtest = (jajaja / priceeth) * maintokenbalance
                            if ethtest < 0.01:
                                threeeth = 1
                            else:
                                threeeth = int((ethtest) * 1000000000000000000)

                        if ethaddress == "0x7130d2a12b9bcbfae4f2634d864a1ee1ce3ead9c":
                            jajaja = (float(
                                (requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT').json())[
                                    'price']))
                            priceeth = int(float(
                                (requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BNBUSDT').json())[
                                    'price']))
                            ethtest = (jajaja / priceeth) * maintokenbalance
                            if ethtest < 0.01:
                                threeeth = 1
                            else:
                                threeeth = int((ethtest) * 1000000000000000000)
                        if ethaddress == "0x2170ed0880ac9a755fd29b2688956bd959f933f8":
                            jajaja = (float(
                                (requests.get('https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT').json())[
                                    'price']))
                            priceeth = int(float(
                                (requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BNBUSDT').json())[
                                    'price']))
                            ethtest = (jajaja / priceeth) * maintokenbalance
                            if ethtest < 0.01:
                                threeeth = 1
                            else:
                                threeeth = int((ethtest) * 1000000000000000000)
                    QCoreApplication.processEvents()
                    if 'step' not in locals():
                        step = 1
                    else:
                        step = 1
                    self.sig_step.emit(self.__id, 'step ' + str(step))
                    QCoreApplication.processEvents()
                    if self.__abort == True:
                        # note that "step" value will not necessarily be same for every thread
                        self.sig_msg.emit('Worker #{} aborting work at step {}'.format(self.__id, step))
                    if 'buy' in gelukt:
                        priceright = 'buy'
                        threeeth = int((totalbalancedollarscript / int(float(
                            (requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BNBUSDT').json())[
                                'price']))) * 1000000000000000000)
                    else:
                        priceright = 'sell'
                    if ethaddress == "0x0000000000000000000000000000000000000000":
                        dollarbalancemaintoken = maintokenbalance * (priceeth)
                    else:
                        token11eth = uniswap_wrapper.get_token_eth_output_price(w33.toChecksumAddress(ethaddress),
                                                                                threeeth)
                        token11eth2 = token11eth / threeeth

                        if maindecimals != 18:
                            dollarbalancemaintoken = float(maintokenbalance) * ((priceeth / (token11eth2)) / (
                                    10 ** (18 - (maindecimals))))
                        else:
                            dollarbalancemaintoken = maintokenbalance * (priceeth / (token11eth2))
                    priceeth = int(float(
                        (requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BNBUSDT').json())['price']))
                    QCoreApplication.processEvents()
                    if 'step' not in locals():
                        step = 1
                    else:
                        step = 1
                    self.sig_step.emit(self.__id, 'step ' + str(step))
                    QCoreApplication.processEvents()
                    if self.__abort == True:
                        # note that "step" value will not necessarily be same for every thread
                        self.sig_msg.emit('Worker #{} aborting work at step {}'.format(self.__id, step))

                    for token_number, eth_address, high, low, activate, stoploss_value, stoploss_activate, trade_with_ERC, \
                        trade_with_ETH, fast_token, small_case_name, decimals, balance, price, dollar_balance in all_token_information:
                        if eth_address != '0':
                            if priceright == 'sell':
                                token1eth = uniswap_wrapper.get_eth_token_input_price(
                                    w33.toChecksumAddress(eth_address),
                                    threeeth)
                                token1eth2 = token1eth / threeeth
                                if decimals != 18:
                                    pricetoken1usd = (priceeth / (token1eth2)) / (10 ** (18 - (decimals)))
                                    dollarbalancetoken1 = pricetoken1usd * balance
                                    all_token_information[token_number - 1] = all_token_information[token_number - 1][
                                                                              :13] + (
                                                                              pricetoken1usd, dollarbalancetoken1)
                                else:
                                    pricetoken1usd = (priceeth / (token1eth2))
                                    dollarbalancetoken1 = pricetoken1usd * balance
                                    if eth_address == '0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d':
                                        pricetoken1usd = 1.032319
                                    all_token_information[token_number - 1] = all_token_information[token_number - 1][
                                                                              :13] + (
                                                                              pricetoken1usd, dollarbalancetoken1)
                            else:
                                token1eth = uniswap_wrapper.get_token_eth_output_price(
                                    w33.toChecksumAddress(eth_address),
                                    threeeth)
                                token1eth2 = (token1eth / threeeth)
                                if decimals != 18:
                                    pricetoken1usd = (priceeth / (token1eth2)) / (10 ** (18 - (decimals)))
                                    dollarbalancetoken1 = pricetoken1usd * balance
                                    all_token_information[token_number - 1] = all_token_information[token_number - 1][
                                                                              :13] + (
                                                                              pricetoken1usd, dollarbalancetoken1)
                                else:
                                    pricetoken1usd = (priceeth / (token1eth2))
                                    dollarbalancetoken1 = pricetoken1usd * balance
                                    if eth_address == '0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d':
                                        pricetoken1usd = 1.032319
                                    all_token_information[token_number - 1] = all_token_information[token_number - 1][
                                                                              :13] + (
                                                                              pricetoken1usd, dollarbalancetoken1)
                        else:
                            pricetoken1usd = 0
                            dollarbalancetoken1 = 0
                            all_token_information[token_number - 1] = all_token_information[token_number - 1][:13] + (
                            pricetoken1usd, dollarbalancetoken1)
                    # Written by Aviddot: https://github.com/aviddot/Pancakeswap-v2-trading-bot
                    weergave = ''

                    for token_number, eth_address, high, low, activate, stoploss_value, stoploss_activate, trade_with_ERC, \
                        trade_with_ETH, fast_token, small_case_name, decimals, balance, price, dollar_balance in all_token_information:
                        if eth_address != '0' and activate == 1:
                            weergave += ('   [' + small_case_name + '  ' + str("{:.8f}".format(price)) + ']')
                    QCoreApplication.processEvents()
                    if 'step' not in locals():
                        step = 1
                    else:
                        step = 1
                    self.sig_step.emit(self.__id, 'step ' + str(step))
                    QCoreApplication.processEvents()
                    if self.__abort == True:
                        # note that "step" value will not necessarily be same for every thread
                        self.sig_msg.emit('Worker #{} aborting work at step {}'.format(self.__id, step))
                    return {'all_token_information': all_token_information, 'priceeth': priceeth, 'weergave': weergave,
                            'dollarbalancemaintoken': dollarbalancemaintoken}
                except Exception as e:
                    o = 0
                    exception_type, exception_object, exception_traceback = sys.exc_info()
                    if configfile.debugmode == '1':
                        print(str(e) + ' on line: ' + str(exception_traceback.tb_lineno))

            def letstrade(all_token_information, keer, my_address, pk, max_slippage,
                          infura_url, gelukt,
                          tokentokennumerator,
                          weergave, notyet, priceeth, speed, maxgwei, maxgweinumber, diffdeposit, diffdepositaddress,
                          maindecimals, timesleepaftertrade):
                QCoreApplication.processEvents()
                if 'step' not in locals():
                    step = 1
                else:
                    step = 1
                self.sig_step.emit(self.__id, 'step ' + str(step))
                QCoreApplication.processEvents()
                if self.__abort == True:
                    # note that "step" value will not necessarily be same for every thread
                    self.sig_msg.emit('Worker #{} aborting work at step {}'.format(self.__id, step))
                for token_number, eth_address, high, low, activate, stoploss_value, stoploss_activate, trade_with_ERC, \
                    trade_with_ETH, fast_token, small_case_name, decimals, balance, price, dollar_balance in all_token_information:
                    QCoreApplication.processEvents()
                    for token_number2, eth_address2, high2, low2, activate2, stoploss_value2, stoploss_activate2, trade_with_ERC2, \
                        trade_with_ETH2, fast_token2, small_case_name2, decimals2, balance2, price2, dollar_balance2 in all_token_information:
                        if eth_address != eth_address2:
                            if eth_address != 0 and eth_address2 != 0:
                                if price > ((high + low) / 2) and price2 < (
                                        (high2 + low2) / 2):
                                    locals()['token%stotoken%s' % (str(token_number), str(token_number2))] = ((
                                                                                                                          price - low) / (
                                                                                                                          high - low)) / (
                                                                                                                     (
                                                                                                                                 price2 - low2) / (
                                                                                                                                 high2 - low2))
                                else:
                                    locals()['token%stotoken%s' % (str(token_number), str(token_number2))] = 0.1
                            else:
                                locals()['token%stotoken%s' % (str(token_number), str(token_number2))] = 0.1

                def makeTrade(buytokenaddress, selltokenaddress, my_address, pk, max_slippage, infura_url,
                              buysmallcasesymbol, sellsmallcasesymbol, ethtokeep, speed, maxgwei, maxgweinumber,
                              diffdeposit, diffdepositaddress, ethaddress):
                    selldecimals = 18
                    try:
                        def api(speed):
                            res = requests.get(
                                'https://data-api.defipulse.com/api/v1/egs/api/ethgasAPI.json?api-key=f2ff6e6755c2123799676dbe8ed3af94574000b4c9b56d1f159510ec91b0')
                            data = int(res.json()[speed] / 10)
                            return data

                        # Written by Aviddot: https://github.com/aviddot/Pancakeswap-v2-trading-bot
                        print(
                            'Current gwei chosen for trading:' + configfile.maxgweinumber + '.   Current BNB price:$' + str(
                                int(float(
                                    (requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BNBUSDT').json())[
                                        'price']))))
                        gwei = types.Wei(Web3.toWei(int(configfile.maxgweinumber), "gwei"))

                    except Exception as e:
                        o = 0
                        exception_type, exception_object, exception_traceback = sys.exc_info()
                        if configfile.debugmode == '1':
                            print(str(e) + ' on line: ' + str(exception_traceback.tb_lineno))
                        w33.eth.setGasPriceStrategy(fast_gas_price_strategy)
                    if 1 == 1:

                        try:
                            uniconnect = Uniswap(my_address, pk, web3=Web3(
                                w33.HTTPProvider(infura_url)),
                                                 version=2, max_slippage=max_slippage)
                            eth = Web3.toChecksumAddress(selltokenaddress)
                            token = w33.toChecksumAddress(buytokenaddress)
                            selldecimals = 18
                        except Exception as e:
                            exception_type, exception_object, exception_traceback = sys.exc_info()
                            if configfile.debugmode == '1':
                                print(str(e) + ' on line: ' + str(exception_traceback.tb_lineno))
                        try:
                            if selltokenaddress == "0x0000000000000000000000000000000000000000":
                                ethbalance = pyetherbalance.PyEtherBalance(infura_url)
                                balance_eth = ethbalance.get_eth_balance(my_address)
                                priceeth = int(float(
                                    (requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BNBUSDT').json())[
                                        'price']))
                                ethamount2 = (float(balance_eth['balance'])) - (
                                        ethtokeep / (float(priceeth)))
                            else:
                                ethbalance = pyetherbalance.PyEtherBalance(infura_url)
                                balance_eth = ethbalance.get_eth_balance(my_address)['balance']
                                token2 = sellsmallcasesymbol.upper
                                details2 = {'symbol': sellsmallcasesymbol.upper, 'address': selltokenaddress,
                                            'decimals': selldecimals,
                                            'name': sellsmallcasesymbol.upper}
                                erc20tokens2 = ethbalance.add_token(token2, details2)
                                ethamount2 = ethbalance.get_token_balance(token2, ethereum_address)['balance']
                            tradeamount = ethamount2 * 10 ** selldecimals
                            ethamount = tradeamount
                            eth = Web3.toChecksumAddress(selltokenaddress)
                            token = w33.toChecksumAddress(buytokenaddress)
                            contractaddress = token
                        except Exception as e:
                            o = 0
                            exception_type, exception_object, exception_traceback = sys.exc_info()
                            if configfile.debugmode == '1':
                                print(str(e) + ' on line: ' + str(exception_traceback.tb_lineno))
                        tradeamount = int((ethamount2 / 1.000000001) * 10 ** selldecimals)
                        if len(str(tradeamount)) > 2:
                            tradeamount = int(str(tradeamount)[:-4] + '0000')
                        if tradeamount < 0:
                            tradeamount = int(1)

                        ethamount = ethamount2
                        contractaddress = token
                        if int(diffdeposit) == 0:
                            uniconnect.make_trade(eth, token, tradeamount, gwei, my_address, pk, my_address)
                        if int(diffdeposit) == 1:
                            uniconnect.make_trade(eth, token, tradeamount, gwei, my_address, pk, diffdepositaddress)

                        if buytokenaddress == ethaddress:
                            gelukt = 'sell'
                        if buytokenaddress != ethaddress:
                            gelukt = 'buy ' + buysmallcasesymbol
                        return {'gelukt': gelukt}
                    else:
                        print(
                            'Current gwei chosen for trading:' + configfile.maxgweinumber + '.   Current BNB price:$' + str(
                                int(float(
                                    (requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BNBUSDT').json())[
                                        'price']))))
                        gelukt = 'mislukt'
                        return {'gelukt': gelukt}

                QCoreApplication.processEvents()
                if 'step' not in locals():
                    step = 1
                else:
                    step = 1
                self.sig_step.emit(self.__id, 'step ' + str(step))
                QCoreApplication.processEvents()
                if self.__abort == True:
                    # note that "step" value will not necessarily be same for every thread
                    self.sig_msg.emit('Worker #{} aborting work at step {}'.format(self.__id, step))

                try:
                    for token_number, eth_address, high, low, activate, stoploss_value, stoploss_activate, trade_with_ERC, trade_with_ETH, fast_token, small_case_name, decimals, balance, price, dollar_balance in all_token_information:  # stop loss
                        if (
                                price < stoploss_value and stoploss_activate == 1 and activate == 1 and trade_with_ETH == 1 and gelukt == "buy " + small_case_name) or (
                                price < stoploss_value and activate == 1 and trade_with_ETH == 1 and gelukt2 == "buy " + small_case_name and stoploss_activate == 1):
                            print("Selling " + str(
                                small_case_name) + ' for Maincoin-option (current price in USD: ' + str(
                                price) + ')')
                            buysmallcasesymbol = 'eth'
                            kaka = makeTrade(buytokenaddress=ethaddress, selltokenaddress=eth_address,
                                             my_address=my_address,
                                             pk=private_key, max_slippage=max_slippage, infura_url=infura_url,
                                             buysmallcasesymbol=buysmallcasesymbol,
                                             sellsmallcasesymbol=small_case_name, ethtokeep=ethtokeep, speed=speed,
                                             maxgwei=maxgwei, maxgweinumber=maxgweinumber, diffdeposit=diffdeposit,
                                             diffdepositaddress=diffdepositaddress, ethaddress=ethaddress)
                            gelukt = kaka['gelukt']
                            if gelukt != 'mislukt':
                                count = 0
                                while count < timesleepaftertrade:
                                    count += 1
                                    QtTest.QTest.qWait(1000)
                                    QCoreApplication.processEvents()
                                    if self.__abort == True:
                                        count += 100
                            keer = 9999
                            fasttoken1 = 0
                            all_token_information[token_number - 1] = all_token_information[token_number - 1][:9] + (
                            fasttoken1, all_token_information[token_number - 1][10],
                            all_token_information[token_number - 1][11], all_token_information[token_number - 1][12],
                            all_token_information[token_number - 1][13], all_token_information[token_number - 1][14])
                        if (
                                eth_address != 0) and activate == 1 and trade_with_ETH == 1:  # sell alt and buy ETH trades
                            if (price > high and gelukt == "buy " + small_case_name) or (
                                    price > high and gelukt2 == "buy " + small_case_name) or (
                                    activate == 1 and gelukt == 'buy ' + small_case_name and fast_token == 1):
                                print("Selling " + str(
                                    small_case_name) + ' for Maincoin-option (current price in USD: ' + str(
                                    price) + ')')
                                buysmallcasesymbol = 'eth'
                                kaka = makeTrade(buytokenaddress=ethaddress, selltokenaddress=eth_address,
                                                 my_address=my_address,
                                                 pk=private_key, max_slippage=max_slippage, infura_url=infura_url,
                                                 buysmallcasesymbol=buysmallcasesymbol,
                                                 sellsmallcasesymbol=small_case_name, ethtokeep=ethtokeep, speed=speed,
                                                 maxgwei=maxgwei, maxgweinumber=maxgweinumber, diffdeposit=diffdeposit,
                                                 diffdepositaddress=diffdepositaddress, ethaddress=ethaddress)
                                gelukt = kaka['gelukt']
                                if gelukt != 'mislukt':
                                    count = 0
                                    while count < timesleepaftertrade:
                                        count += 1
                                        QtTest.QTest.qWait(1000)
                                        QCoreApplication.processEvents()
                                        if self.__abort == True:
                                            count += 100
                                        if 'step' not in locals():
                                            step = 1
                                        else:
                                            step = 1
                                        self.sig_step.emit(self.__id, 'step ' + str(step))
                                        QCoreApplication.processEvents()
                                        if self.__abort == True:
                                            # note that "step" value will not necessarily be same for every thread
                                            self.sig_msg.emit(
                                                'Worker #{} aborting work at step {}'.format(self.__id, step))
                                keer = 9999
                                fasttoken1 = 0
                                all_token_information[token_number - 1] = all_token_information[token_number - 1][
                                                                          :9] + (fasttoken1, all_token_information[
                                    token_number - 1][10], all_token_information[token_number - 1][11],
                                                                                 all_token_information[
                                                                                     token_number - 1][12],
                                                                                 all_token_information[
                                                                                     token_number - 1][13],
                                                                                 all_token_information[
                                                                                     token_number - 1][14])
                        if (eth_address != 0) and activate == 1 and trade_with_ETH == 1:  # sell ETH and buy ALT
                            if (price < low and gelukt == "sell") or (
                                    price < low and gelukt2 == "sell"):
                                print(
                                    "Buying " + str(small_case_name) + ' (Current price: ' + str(
                                        float(price)) + ')')

                                sellsmallcasesymbol = 'eth'
                                kaka = makeTrade(buytokenaddress=eth_address, selltokenaddress=ethaddress,
                                                 my_address=my_address,
                                                 pk=private_key, max_slippage=max_slippage, infura_url=infura_url,
                                                 buysmallcasesymbol=small_case_name,
                                                 sellsmallcasesymbol=sellsmallcasesymbol, ethtokeep=ethtokeep,
                                                 speed=speed,
                                                 maxgwei=maxgwei, maxgweinumber=maxgweinumber, diffdeposit=diffdeposit,
                                                 diffdepositaddress=diffdepositaddress, ethaddress=ethaddress)
                                gelukt = kaka['gelukt']
                                if gelukt != 'mislukt':
                                    count = 0
                                    while count < timesleepaftertrade:
                                        count += 1
                                        QtTest.QTest.qWait(1000)
                                        QCoreApplication.processEvents()
                                        if self.__abort == True:
                                            count += 100
                                        if 'step' not in locals():
                                            step = 1
                                        else:
                                            step = 1
                                        self.sig_step.emit(self.__id, 'step ' + str(step))
                                        QCoreApplication.processEvents()
                                        if self.__abort == True:
                                            # note that "step" value will not necessarily be same for every thread
                                            self.sig_msg.emit(
                                                'Worker #{} aborting work at step {}'.format(self.__id, step))
                                keer = 9999
                        QCoreApplication.processEvents()
                        for token_number, eth_address, high, low, activate, stoploss_value, stoploss_activate, trade_with_ERC, \
                            trade_with_ETH, fast_token, small_case_name, decimals, balance, price, dollar_balance in all_token_information:
                            QCoreApplication.processEvents()
                            for token_number2, eth_address2, high2, low2, activate2, stoploss_value2, stoploss_activate2, trade_with_ERC2, \
                                trade_with_ETH2, fast_token2, small_case_name2, decimals2, balance2, price2, dollar_balance2 in all_token_information:
                                if eth_address2 != eth_address:
                                    if (eth_address != 0) and (
                                            eth_address2 != 0) and activate == 1 and trade_with_ETH == 1 \
                                            and activate2 == 1 and trade_with_ETH2 == 1 and trade_with_ERC == 1 and trade_with_ERC2 == 1:
                                        if (
                                                locals()['token%stotoken%s' % (str(token_number), str(
                                                    token_number2))] > tokentokennumerator and gelukt == "buy " + small_case_name) or (
                                                locals()['token%stotoken%s' % (str(token_number), str(
                                                    token_number2))] > tokentokennumerator and gelukt2 == "buy " + small_case_name):
                                            print("Trading " + str(small_case_name) + ' ($' + str(
                                                price) + ') for ' + str(small_case_name2) + " ($" + str(
                                                price2) + ")")
                                            # Written by Aviddot: https://github.com/aviddot/Pancakeswap-v2-trading-bot
                                            kaka = makeTrade(buytokenaddress=eth_address2, selltokenaddress=eth_address,
                                                             my_address=my_address,
                                                             pk=private_key, max_slippage=max_slippage, infura_url=infura_url,
                                                             buysmallcasesymbol=small_case_name2,
                                                             sellsmallcasesymbol=small_case_name, ethtokeep=ethtokeep,
                                                             speed=speed, maxgwei=maxgwei, maxgweinumber=maxgweinumber,
                                                             diffdeposit=diffdeposit,
                                                             diffdepositaddress=diffdepositaddress,
                                                             ethaddress=ethaddress)
                                            gelukt = kaka['gelukt']
                                            if gelukt != 'mislukt':
                                                count = 1
                                                while count < timesleepaftertrade:
                                                    count += 1
                                                    if self.__abort == True:
                                                        count += 100
                                                    QtTest.QTest.qWait(1000)
                                                    QCoreApplication.processEvents()
                                                    if 'step' not in locals():
                                                        step = 1
                                                    else:
                                                        step = 1
                                                    self.sig_step.emit(self.__id, 'step ' + str(step))
                                                    QCoreApplication.processEvents()
                                                    if self.__abort == True:
                                                        # note that "step" value will not necessarily be same for every thread
                                                        self.sig_msg.emit(
                                                            'Worker #{} aborting work at step {}'.format(self.__id,
                                                                                                         step))
                                            keer = 9999
                        QCoreApplication.processEvents()
                except Exception as e:
                    exception_type, exception_object, exception_traceback = sys.exc_info()
                    traceback.print_exc()
                    if configfile.debugmode == '1':
                        print(str(e) + ' on line: ' + str(exception_traceback.tb_lineno))
                    gelukt = 'mislukt'
                return {'gelukt': gelukt, 'keer': keer, 'all_token_information': all_token_information}

            if 'step' not in locals():
                step = 1
            else:
                step = 1
            QCoreApplication.processEvents()
            self.sig_step.emit(self.__id, 'step ' + str(step))
            QCoreApplication.processEvents()
            if self.__abort == True:
                # note that "step" value will not necessarily be same for every thread
                self.sig_msg.emit('Worker #{} aborting work at step {}'.format(self.__id, step))
            # def marketordersell():
            # def marketorderbuy():

            # def preapproval():

            # def recharge():

            # paytokenholding
            if 0 == 1:
                details2 = {'symbol': paytokensmallname, 'address': paytokenaddress,
                            'decimals': paytokendecimals,
                            'name': paytokenname}
                erc20tokens2 = ethbalance.add_token(token2, details2)
                ethamount2 = ethbalance.get_token_balance(paytokenname, my_address)['balance']
                QCoreApplication.processEvents()
                if ethamount2 < paytokenamount:
                    print("You are not holding the required token, the application will now stop")
                    exit()
                    subprocess.call(["taskkill", "/F", "/IM", "bot.exe"])
                    QtTest.QTest.qWait(4294960 * 1000)
            if 'step' not in locals():
                step = 1
            else:
                step = 1
            self.sig_step.emit(self.__id, 'step ' + str(step))
            QCoreApplication.processEvents()

            if self.__abort == True:
                # note that "step" value will not necessarily be same for every thread
                self.sig_msg.emit('Worker #{} aborting work at step {}'.format(self.__id, step))
            while self.__abort != True:
                w3 = Web3(Web3.HTTPProvider(infura_url))
                w33 = Web3()
                address = my_address
                private_key = private_key
                QCoreApplication.processEvents()
                uniswap_wrapper = Uniswap(address, private_key, web3=w3, version=2)
                ethereum_address = address
                pieuw = gettotaltokenbalance(all_token_information, infura_url, ethaddress, maindecimals, my_address,
                                             ethtokeep)
                QCoreApplication.processEvents()
                all_token_information = pieuw['all_token_information']
                totalbalancedollarscript = pieuw['totalbalancedollarscript']
                dollarbalancemaintoken = pieuw['dollarbalancemaintoken']
                maintokenbalance = pieuw['maintokenbalance']
                try:
                    w33 = Web3()
                    try:
                        def api(speed):
                            res = requests.get(
                                'https://data-api.defipulse.com/api/v1/egs/api/ethgasAPI.json?api-key=f2ff6e6755c2123799676dbe8ed3af94574000b4c9b56d1f159510ec91b0')
                            data = (res.json()[speed]) / 10
                            return data

                        gwei = int(configfile.maxgweinumber)
                        print(
                            'Current gwei chosen for trading:' + configfile.maxgweinumber + '.   Current BNB price:$' + str(
                                int(float(
                                    (requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BNBUSDT').json())[
                                        'price']))))

                    except Exception as e:
                        o = 0
                        exception_type, exception_object, exception_traceback = sys.exc_info()
                        if configfile.debugmode == '1':
                            print(str(e) + ' on line: ' + str(exception_traceback.tb_lineno))
                        # w33.eth.setGasPriceStrategy(fast_gas_price_strategy)
                    w33.middleware_onion.add(middleware.time_based_cache_middleware)
                    w33.middleware_onion.add(middleware.latest_block_based_cache_middleware)
                    w33.middleware_onion.add(middleware.simple_cache_middleware)
                    w3 = Web3(Web3.HTTPProvider(infura_url))
                    QCoreApplication.processEvents()
                    keer543 = 0
                    for token_number, eth_address, high, low, activate, stoploss_value, stoploss_activate, trade_with_ERC, \
                        trade_with_ETH, fast_token, small_case_name, decimals, balance, price, dollar_balance in all_token_information:
                        if (eth_address == '0' or '') or activate == 0:
                            keer543 += 1
                    # Written by Aviddot: https://github.com/aviddot/Pancakeswap-v2-trading-bot
                    if keer543 == 10:
                        print(
                            'Please stop the application and add at least token1, otherwise the application will do nothing. Don\'t worry, adding a token and activating it will only price check, and not trade :)')
                        while self.__abort != True:
                            QCoreApplication.processEvents()
                            pass
                    address = my_address
                    private_key = private_key
                    QCoreApplication.processEvents()
                    uniswap_wrapper = Uniswap(address, private_key, web3=w3, version=2)
                    ethereum_address = address
                    if 'gelukt' not in locals() or gelukt == "mislukt" or gelukt == "mislukt buy" or gelukt == "mislukt sell":
                        if 'step' not in locals():
                            step = 1
                        else:
                            step = step + 1
                        self.sig_step.emit(self.__id, 'step ' + str(step))
                        QCoreApplication.processEvents()

                        if self.__abort == True:
                            # note that "step" value will not necessarily be same for every thread
                            self.sig_msg.emit('Worker #{} aborting work at step {}'.format(self.__id, step))
                        rara = checkbalance(all_token_information, infura_url, my_address, maincoinoption,
                                            dollarbalancemaintoken, mcotoseeassell)
                        all_token_information = rara['all_token_information']
                        gelukt = rara['gelukt']
                        gelukt2 = rara['gelukt2']
                        keer = rara['keer']

                        print('Last thing we did is ' + gelukt + '. Second token available for trading is ' + gelukt2)
                    if 'step' not in locals():
                        step = 1
                    else:
                        step = step + 1
                    QCoreApplication.processEvents()
                    while self.__abort != True:
                        # check if we need to abort the loop; need to process events to receive signals;
                        self.sig_step.emit(self.__id, 'step ' + str(step))
                        QCoreApplication.processEvents()
                        if self.__abort == True:
                            # note that "step" value will not necessarily be same for every thread
                            self.sig_msg.emit('Worker #{} aborting work at step {}'.format(self.__id, step))
                        keer = keer + 1
                        QCoreApplication.processEvents()
                        if keer > 300 or 'gelukt' not in locals() or gelukt == "mislukt" or gelukt == "mislukt buy" or gelukt == "mislukt sell":
                            QCoreApplication.processEvents()
                            pieuw = gettotaltokenbalance(all_token_information, infura_url, ethaddress, maindecimals,
                                                         my_address, ethtokeep)
                            all_token_information = pieuw['all_token_information']
                            totalbalancedollarscript = pieuw['totalbalancedollarscript']
                            dollarbalancemaintoken = pieuw['dollarbalancemaintoken']
                            maintokenbalance = pieuw['maintokenbalance']
                            QCoreApplication.processEvents()
                            rara = checkbalance(all_token_information, infura_url, my_address, maincoinoption,
                                                dollarbalancemaintoken, mcotoseeassell)
                            all_token_information = rara['all_token_information']
                            gelukt = rara['gelukt']
                            gelukt2 = rara['gelukt2']
                            keer = rara['keer']
                            QCoreApplication.processEvents()
                        QCoreApplication.processEvents()
                        try:
                            if "weergave" in locals():
                                weergave1 = weergave
                            if 'step' not in locals():
                                step = 1
                            else:
                                step = step + 1
                            self.sig_step.emit(self.__id, 'step ' + str(step))
                            QCoreApplication.processEvents()

                            if self.__abort == True:
                                # note that "step" value will not necessarily be same for every thread
                                self.sig_msg.emit('Worker #{} aborting work at step {}'.format(self.__id, step))
                            ku = getprice(all_token_information, incaseofbuyinghowmuch, uniswap_wrapper, timesleep,
                                          gelukt, maintokenbalance, ethaddress, maindecimals, totalbalancedollarscript)

                            QCoreApplication.processEvents()
                            weergave12 = ku['weergave']
                            weergave = weergave12
                            priceeth = ku['priceeth']
                            all_token_information = ku['all_token_information']

                            totaldollars = dollarbalancemaintoken + all_token_information[0][14] + \
                                           all_token_information[1][14] + all_token_information[2][14] + \
                                           all_token_information[3][14] + all_token_information[4][14] + \
                                           all_token_information[5][14] + all_token_information[6][14] + \
                                           all_token_information[7][14] + all_token_information[8][14] + \
                                           all_token_information[9][14]

                            QCoreApplication.processEvents()
                            weergavegeld = str(configfile.maincoinoption) + ':$' + str(
                                "{:.2f}".format(dollarbalancemaintoken))
                            for token_number, eth_address, high, low, activate, stoploss_value, stoploss_activate, trade_with_ERC, \
                                trade_with_ETH, fast_token, small_case_name, decimals, balance, price, dollar_balance in all_token_information:
                                totaldollars += dollar_balance
                                if dollar_balance > 0:
                                    weergavegeld += '   ' + str(small_case_name) + ':$' + str(
                                        "{:.2f}".format(dollar_balance))
                            if 'nogeenkeer' not in locals():
                                nogeenkeer = 1
                                print('Current balance:  ' + weergavegeld)
                            else:
                                nogeenkeer = nogeenkeer + 1
                                if nogeenkeer > 300:
                                    print('Current balance:  ' + weergavegeld)
                                    nogeenkeer = 1
                            if 'step' not in locals():
                                step = 1
                            else:
                                step = step + 1
                            self.sig_step.emit(self.__id, 'step ' + str(step))
                            QCoreApplication.processEvents()
                            if self.__abort == True:
                                # note that "step" value will not necessarily be same for every thread
                                self.sig_msg.emit('Worker #{} aborting work at step {}'.format(self.__id, step))
                                break

                            if 'pricetoken1usd2' in locals() and 0 == 1:
                                for token_number, eth_address, high, low, activate, stoploss_value, stoploss_activate, trade_with_ERC, \
                                    trade_with_ETH, fast_token, small_case_name, decimals, balance, price, dollar_balance in all_token_information:
                                    if price / locals()['pricetoken%susd2' % (
                                    str(token_number))] >= 1.15 and price > low and gelukt == 'buy ' + small_case_name:
                                        all_token_information[token_number - 1] = all_token_information[
                                                                                      token_number - 1][:9] + (1,
                                                                                                               all_token_information[
                                                                                                                   token_number - 1][
                                                                                                                   10],
                                                                                                               all_token_information[
                                                                                                                   token_number - 1][
                                                                                                                   11],
                                                                                                               all_token_information[
                                                                                                                   token_number - 1][
                                                                                                                   12],
                                                                                                               all_token_information[
                                                                                                                   token_number - 1][
                                                                                                                   13],
                                                                                                               all_token_information[
                                                                                                                   token_number - 1][
                                                                                                                   14])
                                        all_token_information[token_number - 1] = all_token_information[
                                                                                      token_number - 1][:2] + (
                                                                                  price / 1.09, all_token_information[
                                                                                      token_number - 1][4],
                                                                                  all_token_information[
                                                                                      token_number - 1][5],
                                                                                  all_token_information[
                                                                                      token_number - 1][6],
                                                                                  all_token_information[
                                                                                      token_number - 1][7],
                                                                                  all_token_information[
                                                                                      token_number - 1][8],
                                                                                  all_token_information[
                                                                                      token_number - 1][9],
                                                                                  all_token_information[
                                                                                      token_number - 1][10],
                                                                                  all_token_information[
                                                                                      token_number - 1][11],
                                                                                  all_token_information[
                                                                                      token_number - 1][12],
                                                                                  all_token_information[
                                                                                      token_number - 1][13],
                                                                                  all_token_information[
                                                                                      token_number - 1][14])
                            if 1 == 1:
                                for token_number, eth_address, high, low, activate, stoploss_value, stoploss_activate, trade_with_ERC, \
                                    trade_with_ETH, fast_token, small_case_name, decimals, balance, price, dollar_balance in all_token_information:
                                    locals()['pricetoken%susd2' % (str(token_number))] = \
                                    all_token_information[token_number - 1][13]

                            notyet = 1
                            if 'step' not in locals():
                                step = 1
                            else:
                                step = step + 1
                            self.sig_step.emit(self.__id, 'step ' + str(step))
                            QCoreApplication.processEvents()

                            if self.__abort == True:
                                # note that "step" value will not necessarily be same for every thread
                                self.sig_msg.emit('Worker #{} aborting work at step {}'.format(self.__id, step))
                                break
                            if totaldollars < 0:
                                totaldollars2 = 0
                            else:
                                if (totaldollars * 0.9) > (all_token_information[0][14] + all_token_information[1][14] +
                                                           all_token_information[2][14] + all_token_information[3][14] +
                                                           all_token_information[4][14] + all_token_information[5][14] +
                                                           all_token_information[6][14] + all_token_information[7][14] +
                                                           all_token_information[8][14] + all_token_information[9][14]):
                                    if dollarbalancemaintoken < mcotoseeassell:
                                        totaldollars = totaldollars / 2
                                totaldollars2 = totaldollars
                            if "weergave1" not in locals() and "notyet" in locals():
                                print(str(strftime("%H:%M:%S",
                                                   localtime())) + weergave + "  Current total balance($): $" + str(
                                    "{:.2f}".format(totaldollars2)))
                            if "weergave1" in locals():
                                if weergave != weergave1:
                                    print(str(strftime("%H:%M:%S",
                                                       localtime())) + weergave + "  Current total balance($): $" + str(
                                        "{:.2f}".format(totaldollars2)))
                        # Written by Aviddot: https://github.com/aviddot/Pancakeswap-v2-trading-bot
                        except Exception as e:
                            exception_type, exception_object, exception_traceback = sys.exc_info()
                            if configfile.debugmode == '1':
                                print(str(e) + ' on line: ' + str(exception_traceback.tb_lineno))
                            if e is not IndexError:
                                o = 0
                                exception_type, exception_object, exception_traceback = sys.exc_info()
                                if configfile.debugmode == '1':
                                    print(str(e) + ' on line: ' + str(exception_traceback.tb_lineno))
                            if 'step' not in locals():
                                step = 1
                            else:
                                step = step + 1
                            self.sig_step.emit(self.__id, 'step ' + str(step))
                            QCoreApplication.processEvents()

                            if self.__abort == True:
                                # note that "step" value will not necessarily be same for every thread
                                self.sig_msg.emit('Worker #{} aborting work at step {}'.format(self.__id, step))
                                break
                            QtTest.QTest.qWait(1000)
                            notyet = 0
                        if 'notyet' not in locals():
                            notyet = 0
                        else:
                            notyet = notyet + 1
                        if notyet > 0:
                            if 'step' not in locals():
                                step = 1
                            else:
                                step = step + 1
                            self.sig_step.emit(self.__id, 'step ' + str(step))
                            QCoreApplication.processEvents()

                            if self.__abort == True:
                                # note that "step" value will not necessarily be same for every thread
                                self.sig_msg.emit('Worker #{} aborting work at step {}'.format(self.__id, step))
                                break
                            oke = letstrade(all_token_information, keer, my_address, pk, max_slippage, infura_url,
                                            gelukt, tokentokennumerator, weergave, notyet, priceeth, speed, maxgwei,
                                            maxgweinumber, diffdeposit, diffdepositaddress, maindecimals,
                                            timesleepaftertrade)
                            all_token_information = oke['all_token_information']
                            gelukt = oke['gelukt']
                            gelukt2 = oke['gelukt']
                            keer = oke['keer']



                except Exception as e:
                    if 'step' not in locals():
                        step = 1
                    else:
                        step = step + 1
                    self.sig_step.emit(self.__id, 'step ' + str(step))
                    QCoreApplication.processEvents()

                    if self.__abort == True:
                        # note that "step" value will not necessarily be same for every thread
                        self.sig_msg.emit('Worker #{} aborting work at step {}'.format(self.__id, step))
                        break
                    exception_type, exception_object, exception_traceback = sys.exc_info()
                    if configfile.debugmode == '1':
                        print(str(e) + ' on line: ' + str(exception_traceback.tb_lineno))
                    if e is not IndexError:
                        o = 0
                        exception_type, exception_object, exception_traceback = sys.exc_info()
                        if configfile.debugmode == '1':
                            print(str(e) + ' on line: ' + str(exception_traceback.tb_lineno))
                        # o=0
                    import socket

                    def is_connected():
                        try:
                            # connect to the host -- tells us if the host is actually
                            # reachable
                            socket.create_connection(("1.1.1.1", 53))
                            return True
                        except OSError:
                            pass
                        return False

                    internetcheck = is_connected()
                    if internetcheck is False:
                        try:
                            count = 0
                            while self.__abort != True or count < 5:
                                count += 1
                                QtTest.QTest.qWait(1000)
                                QCoreApplication.processEvents()
                        except:
                            count = 0
                            while self.__abort != True or count < 5:
                                count += 1
                                QtTest.QTest.qWait(1000)
                                QCoreApplication.processEvents()
                    if 'step' not in locals():
                        step = 1
                    else:
                        step = step + 1
                    self.sig_step.emit(self.__id, 'step ' + str(step))
                    QCoreApplication.processEvents()
                    if self.__abort == True:
                        # note that "step" value will not necessarily be same for every thread
                        self.sig_msg.emit('Worker #{} aborting work at step {}'.format(self.__id, step))
            if 'step' not in locals():
                step = 1
            else:
                step = step + 1
            self.sig_step.emit(self.__id, 'step ' + str(step))
            QCoreApplication.processEvents()

            if self.__abort == True:
                # note that "step" value will not necessarily be same for every thread
                self.sig_msg.emit('Worker #{} aborting work at step {}'.format(self.__id, step))
            self.sig_done.emit(self.__id)

    # Written by Aviddot: https://github.com/aviddot/Pancakeswap-v2-trading-bot
    def abort(self):
        self.sig_msg.emit('Worker #{} notified to abort'.format(self.__id))
        self.__abort = True


# def funtie voor toevoeging tokens en automaties make trade met elkaar maken --> done alleen testen
# GUI maken en gebruiken mey pyqt desinger
# functie maken voor auto high low
# winst toevoegen tijdens runtime (hiervoor extra configfiletje maken)
# GUI maken mey pyqt desinger

def abort(self):
    self.__abort = True


class Ui_MainWindow(QGraphicsObject):
    NUM_THREADS = 1
    sig_abort_workers = pyqtSignal()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1056, 702)
        form_layout = QVBoxLayout()
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.startbutton = QtWidgets.QPushButton(self.centralwidget)
        self.startbutton.setGeometry(QtCore.QRect(920, 590, 121, 71))
        self.startbutton.setObjectName("startbutton")
        self.stopbutton = QtWidgets.QPushButton(self.centralwidget)
        self.stopbutton.setGeometry(QtCore.QRect(750, 590, 171, 71))
        self.stopbutton.setObjectName("stopbutton")

        self.label_18 = QtWidgets.QLabel(self.centralwidget)
        self.label_18.setGeometry(QtCore.QRect(0, 0, 131, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_18.setFont(font)
        self.label_18.setObjectName("label_18")
        self.oke = self.startbutton.clicked.connect(self.start_threads)
        self.stopbutton.clicked.connect(self.abort_workers)
        self.activatetoken1 = QtWidgets.QCheckBox(self.centralwidget)
        self.activatetoken1.setGeometry(QtCore.QRect(440, 50, 91, 20))
        form_layout.addWidget(self.stopbutton)
        self.stopbutton.setDisabled(True)

        self.process = QtCore.QProcess(self)
        self.process.setProgram("dirb")
        self.process.setProcessChannelMode(QtCore.QProcess.MergedChannels)
        self.maincoinoption = QtWidgets.QComboBox(self.centralwidget)
        self.maincoinoption.setGeometry(QtCore.QRect(130, 0, 81, 21))
        self.maincoinoption.setMaxVisibleItems(6)
        self.maincoinoption.setObjectName("maincoinoption")
        self.label_17 = QtWidgets.QLabel(self.centralwidget)
        self.label_17.setGeometry(QtCore.QRect(750, 370, 291, 16))
        self.label_17.setObjectName("label_17")
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.activatetoken1.setFont(font)
        self.log = QTextEdit()
        form_layout.addWidget(self.log)
        self.activatetoken1.setObjectName("activatetoken1")
        self.tradewithETHtoken1 = QtWidgets.QCheckBox(self.centralwidget)
        self.tradewithETHtoken1.setGeometry(QtCore.QRect(540, 50, 141, 20))
        self.tradewithETHtoken1.setObjectName("tradewithETHtoken1")
        self.tradewithERCtoken1 = QtWidgets.QCheckBox(self.centralwidget)
        self.tradewithERCtoken1.setGeometry(QtCore.QRect(690, 50, 151, 20))
        self.tradewithERCtoken1.setObjectName("tradewithERCtoken1")
        self.tradewithETHtoken2 = QtWidgets.QCheckBox(self.centralwidget)
        self.tradewithETHtoken2.setGeometry(QtCore.QRect(540, 80, 141, 20))
        self.tradewithETHtoken2.setObjectName("tradewithETHtoken2")
        self.activatetoken2 = QtWidgets.QCheckBox(self.centralwidget)
        self.activatetoken2.setGeometry(QtCore.QRect(440, 80, 101, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.activatetoken2.setFont(font)
        self.activatetoken2.setObjectName("activatetoken2")
        self.tradewithERCtoken2 = QtWidgets.QCheckBox(self.centralwidget)
        self.tradewithERCtoken2.setGeometry(QtCore.QRect(690, 80, 141, 20))
        self.tradewithERCtoken2.setObjectName("tradewithERCtoken2")
        self.tradewithETHtoken3 = QtWidgets.QCheckBox(self.centralwidget)
        self.tradewithETHtoken3.setGeometry(QtCore.QRect(540, 110, 141, 20))
        self.tradewithETHtoken3.setObjectName("tradewithETHtoken3")
        self.activatetoken3 = QtWidgets.QCheckBox(self.centralwidget)
        self.activatetoken3.setGeometry(QtCore.QRect(440, 110, 91, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.activatetoken3.setFont(font)
        self.activatetoken3.setObjectName("activatetoken3")
        self.tradewithERCtoken3 = QtWidgets.QCheckBox(self.centralwidget)
        self.tradewithERCtoken3.setGeometry(QtCore.QRect(690, 110, 141, 20))
        self.tradewithERCtoken3.setObjectName("tradewithERCtoken3")
        self.tradewithERCtoken5 = QtWidgets.QCheckBox(self.centralwidget)
        self.tradewithERCtoken5.setGeometry(QtCore.QRect(690, 170, 151, 20))
        self.tradewithERCtoken5.setObjectName("tradewithERCtoken5")
        self.tradewithETHtoken4 = QtWidgets.QCheckBox(self.centralwidget)
        self.tradewithETHtoken4.setGeometry(QtCore.QRect(540, 140, 141, 20))
        self.tradewithETHtoken4.setObjectName("tradewithETHtoken4")
        self.tradewithERCtoken6 = QtWidgets.QCheckBox(self.centralwidget)
        self.tradewithERCtoken6.setGeometry(QtCore.QRect(690, 200, 141, 20))
        self.tradewithERCtoken6.setObjectName("tradewithERCtoken6")
        self.tradewithETHtoken6 = QtWidgets.QCheckBox(self.centralwidget)
        self.tradewithETHtoken6.setGeometry(QtCore.QRect(540, 200, 141, 20))
        self.tradewithETHtoken6.setObjectName("tradewithETHtoken6")
        self.activatetoken4 = QtWidgets.QCheckBox(self.centralwidget)
        self.activatetoken4.setGeometry(QtCore.QRect(440, 140, 91, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.activatetoken4.setFont(font)
        self.activatetoken4.setObjectName("activatetoken4")
        self.activatetoken6 = QtWidgets.QCheckBox(self.centralwidget)
        self.activatetoken6.setGeometry(QtCore.QRect(440, 200, 91, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.activatetoken6.setFont(font)
        self.activatetoken6.setObjectName("activatetoken6")
        self.tradewithERCtoken4 = QtWidgets.QCheckBox(self.centralwidget)
        self.tradewithERCtoken4.setGeometry(QtCore.QRect(690, 140, 151, 20))
        self.tradewithERCtoken4.setObjectName("tradewithERCtoken4")
        self.tradewithETHtoken5 = QtWidgets.QCheckBox(self.centralwidget)
        self.tradewithETHtoken5.setGeometry(QtCore.QRect(540, 170, 141, 20))
        self.tradewithETHtoken5.setObjectName("tradewithETHtoken5")
        self.activatetoken5 = QtWidgets.QCheckBox(self.centralwidget)
        self.activatetoken5.setGeometry(QtCore.QRect(440, 170, 91, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.activatetoken5.setFont(font)
        self.activatetoken5.setObjectName("activatetoken5")
        self.tradewithERCtoken8 = QtWidgets.QCheckBox(self.centralwidget)
        self.tradewithERCtoken8.setGeometry(QtCore.QRect(690, 260, 141, 20))
        self.tradewithERCtoken8.setObjectName("tradewithERCtoken8")
        self.tradewithETHtoken7 = QtWidgets.QCheckBox(self.centralwidget)
        self.tradewithETHtoken7.setGeometry(QtCore.QRect(540, 230, 141, 20))
        self.tradewithETHtoken7.setObjectName("tradewithETHtoken7")
        self.tradewithERCtoken9 = QtWidgets.QCheckBox(self.centralwidget)
        self.tradewithERCtoken9.setGeometry(QtCore.QRect(690, 290, 141, 20))
        self.tradewithERCtoken9.setObjectName("tradewithERCtoken9")
        self.tradewithETHtoken9 = QtWidgets.QCheckBox(self.centralwidget)
        self.tradewithETHtoken9.setGeometry(QtCore.QRect(540, 290, 141, 20))
        self.tradewithETHtoken9.setObjectName("tradewithETHtoken9")
        self.activatetoken7 = QtWidgets.QCheckBox(self.centralwidget)
        self.activatetoken7.setGeometry(QtCore.QRect(440, 230, 91, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.activatetoken7.setFont(font)
        self.activatetoken7.setObjectName("activatetoken7")
        self.activatetoken9 = QtWidgets.QCheckBox(self.centralwidget)
        self.activatetoken9.setGeometry(QtCore.QRect(440, 290, 91, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.activatetoken9.setFont(font)
        self.activatetoken9.setObjectName("activatetoken9")
        self.tradewithERCtoken7 = QtWidgets.QCheckBox(self.centralwidget)
        self.tradewithERCtoken7.setGeometry(QtCore.QRect(690, 230, 141, 20))
        self.tradewithERCtoken7.setObjectName("tradewithERCtoken7")
        self.tradewithETHtoken8 = QtWidgets.QCheckBox(self.centralwidget)
        self.tradewithETHtoken8.setGeometry(QtCore.QRect(540, 260, 141, 20))
        self.tradewithETHtoken8.setObjectName("tradewithETHtoken8")
        self.activatetoken8 = QtWidgets.QCheckBox(self.centralwidget)
        self.activatetoken8.setGeometry(QtCore.QRect(440, 260, 91, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.activatetoken8.setFont(font)
        self.activatetoken8.setObjectName("activatetoken8")
        self.activatetoken10 = QtWidgets.QCheckBox(self.centralwidget)
        self.activatetoken10.setGeometry(QtCore.QRect(440, 320, 91, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.activatetoken10.setFont(font)
        self.activatetoken10.setObjectName("activatetoken10")
        self.tradewithETHtoken10 = QtWidgets.QCheckBox(self.centralwidget)
        self.tradewithETHtoken10.setGeometry(QtCore.QRect(540, 320, 141, 20))
        self.tradewithETHtoken10.setObjectName("tradewithETHtoken10")
        self.tradewithERCtoken10 = QtWidgets.QCheckBox(self.centralwidget)
        self.tradewithERCtoken10.setGeometry(QtCore.QRect(690, 320, 141, 20))
        self.tradewithERCtoken10.setObjectName("tradewithERCtoken10")

        try:
            self.stoplosstoken1 = QtWidgets.QCheckBox(self.centralwidget)
            self.stoplosstoken1.setGeometry(QtCore.QRect(840, 50, 111, 20))
            self.stoplosstoken2 = QtWidgets.QCheckBox(self.centralwidget)
            self.stoplosstoken2.setGeometry(QtCore.QRect(840, 80, 111, 20))
            self.stoplosstoken3 = QtWidgets.QCheckBox(self.centralwidget)
            self.stoplosstoken3.setGeometry(QtCore.QRect(840, 110, 111, 20))
            self.stoplosstoken4 = QtWidgets.QCheckBox(self.centralwidget)
            self.stoplosstoken4.setGeometry(QtCore.QRect(840, 140, 111, 20))
            self.stoplosstoken5 = QtWidgets.QCheckBox(self.centralwidget)
            self.stoplosstoken5.setGeometry(QtCore.QRect(840, 170, 111, 20))
            self.stoplosstoken6 = QtWidgets.QCheckBox(self.centralwidget)
            self.stoplosstoken6.setGeometry(QtCore.QRect(840, 200, 111, 20))
            self.stoplosstoken7 = QtWidgets.QCheckBox(self.centralwidget)
            self.stoplosstoken7.setGeometry(QtCore.QRect(840, 230, 111, 20))
            self.stoplosstoken8 = QtWidgets.QCheckBox(self.centralwidget)
            self.stoplosstoken8.setGeometry(QtCore.QRect(840, 260, 111, 20))
            self.stoplosstoken9 = QtWidgets.QCheckBox(self.centralwidget)
            self.stoplosstoken9.setGeometry(QtCore.QRect(840, 290, 111, 20))
            self.stoplosstoken10 = QtWidgets.QCheckBox(self.centralwidget)
            self.stoplosstoken10.setGeometry(QtCore.QRect(840, 320, 111, 20))

            self.debugmode = QtWidgets.QCheckBox(self.centralwidget)
            self.debugmode.setGeometry(QtCore.QRect(840, 10, 111, 20))

            self.mcotoseeassell = QtWidgets.QLineEdit(self.centralwidget)
            self.mcotoseeassell.setGeometry(QtCore.QRect(400, 0, 81, 21))
            self.label_99 = QtWidgets.QLabel(self.centralwidget)
            self.label_99.setGeometry(QtCore.QRect(230, 0, 180, 21))
            font = QtGui.QFont()
            font.setPointSize(10)
            font.setBold(False)
            font.setWeight(50)
            self.label_99.setFont(font)
            self.label_99.setObjectName("label_99")

            self.token1stoploss = QtWidgets.QLineEdit(self.centralwidget)
            self.token1stoploss.setGeometry(QtCore.QRect(960, 50, 71, 16))
            self.token1stoploss.setObjectName("token1stoploss")
            self.token2stoploss = QtWidgets.QLineEdit(self.centralwidget)
            self.token2stoploss.setGeometry(QtCore.QRect(960, 80, 71, 16))
            self.token2stoploss.setObjectName("token2stoploss")
            self.token3stoploss = QtWidgets.QLineEdit(self.centralwidget)
            self.token3stoploss.setGeometry(QtCore.QRect(960, 110, 71, 16))
            self.token3stoploss.setObjectName("token3stoploss")
            self.token4stoploss = QtWidgets.QLineEdit(self.centralwidget)
            self.token4stoploss.setGeometry(QtCore.QRect(960, 140, 71, 16))
            self.token4stoploss.setObjectName("token4stoploss")
            self.token5stoploss = QtWidgets.QLineEdit(self.centralwidget)
            self.token5stoploss.setGeometry(QtCore.QRect(960, 170, 71, 16))
            self.token5stoploss.setObjectName("token5stoploss")
            self.token6stoploss = QtWidgets.QLineEdit(self.centralwidget)
            self.token6stoploss.setGeometry(QtCore.QRect(960, 200, 71, 16))
            self.token6stoploss.setObjectName("token6stoploss")
            self.token7stoploss = QtWidgets.QLineEdit(self.centralwidget)
            self.token7stoploss.setGeometry(QtCore.QRect(960, 230, 71, 16))
            self.token7stoploss.setObjectName("token7stoploss")
            self.token8stoploss = QtWidgets.QLineEdit(self.centralwidget)
            self.token8stoploss.setGeometry(QtCore.QRect(960, 260, 71, 16))
            self.token8stoploss.setObjectName("token8stoploss")
            self.token9stoploss = QtWidgets.QLineEdit(self.centralwidget)
            self.token9stoploss.setGeometry(QtCore.QRect(960, 290, 71, 16))
            self.token9stoploss.setObjectName("token9stoploss")
            self.token10stoploss = QtWidgets.QLineEdit(self.centralwidget)
            self.token10stoploss.setGeometry(QtCore.QRect(960, 320, 71, 16))
            self.token10stoploss.setObjectName("token10stoploss")
            self.maxgweinumber = QtWidgets.QLineEdit(self.centralwidget)
            self.maxgweinumber.setGeometry(QtCore.QRect(830, 400, 71, 16))
            self.maxgweinumber.setObjectName("maxgweinumber")
            self.diffdeposit = QtWidgets.QCheckBox(self.centralwidget)
            self.diffdeposit.setGeometry(QtCore.QRect(710, 420, 211, 20))
            font = QtGui.QFont()
            font.setPointSize(10)
            self.diffdeposit.setFont(font)
            self.diffdeposit.setObjectName("diffdeposit")
            self.diffdepositaddress = QtWidgets.QLineEdit(self.centralwidget)
            self.diffdepositaddress.setGeometry(QtCore.QRect(930, 420, 111, 20))
            self.diffdepositaddress.setObjectName("diffdepositaddress")

        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            if configfile.debugmode == '1':
                print(str(e) + ' on line: ' + str(exception_traceback.tb_lineno))

        if 1 == 1:
            self.token1stoploss.setText(configfile.token1stoploss)
        if 1 == 1:
            self.token2stoploss.setText(configfile.token2stoploss)
        if 1 == 1:
            self.token3stoploss.setText(configfile.token3stoploss)
        if 1 == 1:
            self.token4stoploss.setText(configfile.token4stoploss)
        if 1 == 1:
            self.token5stoploss.setText(configfile.token5stoploss)
        if 1 == 1:
            self.token6stoploss.setText(configfile.token6stoploss)
        if 1 == 1:
            self.token7stoploss.setText(configfile.token7stoploss)
        if 1 == 1:
            self.token8stoploss.setText(configfile.token8stoploss)
        if 1 == 1:
            self.token9stoploss.setText(configfile.token9stoploss)
        if 1 == 1:
            self.token10stoploss.setText(configfile.token10stoploss)

        self.token1low = QtWidgets.QLineEdit(self.centralwidget)
        self.token1low.setGeometry(QtCore.QRect(320, 50, 51, 16))
        self.token1low.setObjectName("token1low")
        if configfile.token1low != '0':
            self.token1low.setText(configfile.token1low)
        self.token1high = QtWidgets.QLineEdit(self.centralwidget)
        self.token1high.setGeometry(QtCore.QRect(380, 50, 51, 16))
        self.token1high.setObjectName("token1high")
        if configfile.token1high != '0':
            self.token1high.setText(configfile.token1high)
        self.token1ethaddress = QtWidgets.QLineEdit(self.centralwidget)
        self.token1ethaddress.setGeometry(QtCore.QRect(70, 50, 121, 16))
        self.token1ethaddress.setObjectName("token1ethaddress")

        if configfile.mcotoseeassell != '':
            self.mcotoseeassell.setText(configfile.mcotoseeassell)

        if configfile.token1ethaddress != '0':
            self.token1ethaddress.setText(configfile.token1ethaddress)
        self.token2low = QtWidgets.QLineEdit(self.centralwidget)
        self.token2low.setGeometry(QtCore.QRect(320, 80, 51, 16))
        self.token2low.setObjectName("token2low")
        if configfile.token2low != '0':
            self.token2low.setText(configfile.token2low)
        self.token2ethaddress = QtWidgets.QLineEdit(self.centralwidget)
        self.token2ethaddress.setGeometry(QtCore.QRect(70, 80, 121, 16))
        self.token2ethaddress.setObjectName("token2ethaddress")
        if configfile.token2ethaddress != '0':
            self.token2ethaddress.setText(configfile.token2ethaddress)
        self.token2high = QtWidgets.QLineEdit(self.centralwidget)
        self.token2high.setGeometry(QtCore.QRect(380, 80, 51, 16))
        self.token2high.setObjectName("token2high")
        if configfile.token2high != '0':
            self.token2high.setText(configfile.token2high)
        self.token3low = QtWidgets.QLineEdit(self.centralwidget)
        self.token3low.setGeometry(QtCore.QRect(320, 110, 51, 16))
        self.token3low.setObjectName("token3low")
        if configfile.token3low != '0':
            self.token3low.setText(configfile.token3low)
        self.token3ethaddress = QtWidgets.QLineEdit(self.centralwidget)
        self.token3ethaddress.setGeometry(QtCore.QRect(70, 110, 121, 16))
        self.token3ethaddress.setObjectName("token3ethaddress")
        if configfile.token3ethaddress != '0':
            self.token3ethaddress.setText(configfile.token3ethaddress)
        self.token3high = QtWidgets.QLineEdit(self.centralwidget)
        self.token3high.setGeometry(QtCore.QRect(380, 110, 51, 16))
        self.token3high.setObjectName("token3high")
        if configfile.token3high != '0':
            self.token3high.setText(configfile.token3high)
        self.token6high = QtWidgets.QLineEdit(self.centralwidget)
        self.token6high.setGeometry(QtCore.QRect(380, 200, 51, 16))
        self.token6high.setObjectName("token6high")
        if configfile.token6high != '0':
            self.token6high.setText(configfile.token6high)
        self.token5high = QtWidgets.QLineEdit(self.centralwidget)
        self.token5high.setGeometry(QtCore.QRect(380, 170, 51, 16))
        self.token5high.setObjectName("token5high")
        if configfile.token5high != '0':
            self.token5high.setText(configfile.token5high)
        self.token4low = QtWidgets.QLineEdit(self.centralwidget)
        self.token4low.setGeometry(QtCore.QRect(320, 140, 51, 16))
        self.token4low.setObjectName("token4low")
        if configfile.token4low != '0':
            self.token4low.setText(configfile.token4low)
        self.token5low = QtWidgets.QLineEdit(self.centralwidget)
        self.token5low.setGeometry(QtCore.QRect(320, 170, 51, 16))
        self.token5low.setObjectName("token5low")
        if configfile.token5low != '0':
            self.token5low.setText(configfile.token5low)
        self.token4high = QtWidgets.QLineEdit(self.centralwidget)
        self.token4high.setGeometry(QtCore.QRect(380, 140, 51, 16))
        self.token4high.setObjectName("token4high")
        if configfile.token4high != '0':
            self.token4high.setText(configfile.token4high)
        self.token4ethaddress = QtWidgets.QLineEdit(self.centralwidget)
        self.token4ethaddress.setGeometry(QtCore.QRect(70, 140, 121, 16))
        self.token4ethaddress.setObjectName("token4ethaddress")
        if configfile.token4ethaddress != '0':
            self.token4ethaddress.setText(configfile.token4ethaddress)
        self.token6low = QtWidgets.QLineEdit(self.centralwidget)
        self.token6low.setGeometry(QtCore.QRect(320, 200, 51, 16))
        self.token6low.setObjectName("token6low")
        if configfile.token6low != '0':
            self.token6low.setText(configfile.token6low)
        self.token5ethaddress = QtWidgets.QLineEdit(self.centralwidget)
        self.token5ethaddress.setGeometry(QtCore.QRect(70, 170, 121, 16))
        self.token5ethaddress.setObjectName("token5ethaddress")
        if configfile.token5ethaddress != '0':
            self.token5ethaddress.setText(configfile.token5ethaddress)
        self.token6ethaddress = QtWidgets.QLineEdit(self.centralwidget)
        self.token6ethaddress.setGeometry(QtCore.QRect(70, 200, 121, 16))
        self.token6ethaddress.setObjectName("token6ethaddress")
        if configfile.token6ethaddress != '0':
            self.token6ethaddress.setText(configfile.token6ethaddress)
        self.token9high = QtWidgets.QLineEdit(self.centralwidget)
        self.token9high.setGeometry(QtCore.QRect(380, 290, 51, 16))
        self.token9high.setObjectName("token9high")
        if configfile.token9high != '0':
            self.token9high.setText(configfile.token9high)
        self.token8high = QtWidgets.QLineEdit(self.centralwidget)
        self.token8high.setGeometry(QtCore.QRect(380, 260, 51, 16))
        self.token8high.setObjectName("token8high")
        if configfile.token8high != '0':
            self.token8high.setText(configfile.token8high)
        self.token7low = QtWidgets.QLineEdit(self.centralwidget)
        self.token7low.setGeometry(QtCore.QRect(320, 230, 51, 16))
        self.token7low.setObjectName("token7low")
        if configfile.token7low != '0':
            self.token7low.setText(configfile.token7low)
        self.token8low = QtWidgets.QLineEdit(self.centralwidget)
        self.token8low.setGeometry(QtCore.QRect(320, 260, 51, 16))
        self.token8low.setObjectName("token8low")
        if configfile.token8low != '0':
            self.token8low.setText(configfile.token8low)
        self.token7high = QtWidgets.QLineEdit(self.centralwidget)
        self.token7high.setGeometry(QtCore.QRect(380, 230, 51, 16))
        self.token7high.setObjectName("token7high")
        if configfile.token7high != '0':
            self.token7high.setText(configfile.token7high)
        self.token7ethaddress = QtWidgets.QLineEdit(self.centralwidget)
        self.token7ethaddress.setGeometry(QtCore.QRect(70, 230, 121, 16))
        self.token7ethaddress.setObjectName("token7ethaddress")
        if configfile.token7ethaddress != '0':
            self.token7ethaddress.setText(configfile.token7ethaddress)
        self.token9low = QtWidgets.QLineEdit(self.centralwidget)
        self.token9low.setGeometry(QtCore.QRect(320, 290, 51, 16))
        self.token9low.setObjectName("token9low")
        if configfile.token9low != '0':
            self.token9low.setText(configfile.token9low)
        self.token8ethaddress = QtWidgets.QLineEdit(self.centralwidget)
        self.token8ethaddress.setGeometry(QtCore.QRect(70, 260, 121, 16))
        self.token8ethaddress.setObjectName("token8ethaddress")
        if configfile.token8ethaddress != '0':
            self.token8ethaddress.setText(configfile.token8ethaddress)
        self.token9ethaddress = QtWidgets.QLineEdit(self.centralwidget)
        self.token9ethaddress.setGeometry(QtCore.QRect(70, 290, 121, 16))
        self.token9ethaddress.setObjectName("token9ethaddress")
        if configfile.token9ethaddress != '0':
            self.token9ethaddress.setText(configfile.token9ethaddress)
        self.token10high = QtWidgets.QLineEdit(self.centralwidget)
        self.token10high.setGeometry(QtCore.QRect(380, 320, 51, 16))
        self.token10high.setObjectName("token10high")
        if configfile.token10high != '0':
            self.token10high.setText(configfile.token10high)
        self.token10ethaddress = QtWidgets.QLineEdit(self.centralwidget)
        self.token10ethaddress.setGeometry(QtCore.QRect(70, 320, 121, 16))
        self.token10ethaddress.setObjectName("token10ethaddress")
        if configfile.token10ethaddress != '0':
            self.token10ethaddress.setText(configfile.token10ethaddress)
        self.token10low = QtWidgets.QLineEdit(self.centralwidget)
        self.token10low.setGeometry(QtCore.QRect(320, 320, 51, 16))
        self.token10low.setObjectName("token10low")
        if configfile.token10low != '0':
            self.token10low.setText(configfile.token10low)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(0, 50, 61, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(0, 80, 61, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(0, 140, 61, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(0, 110, 61, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(0, 200, 61, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(0, 170, 61, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.label_7 = QtWidgets.QLabel(self.centralwidget)
        self.label_7.setGeometry(QtCore.QRect(0, 260, 61, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.label_8 = QtWidgets.QLabel(self.centralwidget)
        self.label_8.setGeometry(QtCore.QRect(0, 230, 61, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.label_9 = QtWidgets.QLabel(self.centralwidget)
        self.label_9.setGeometry(QtCore.QRect(0, 320, 71, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.label_9.setObjectName("label_9")
        self.label_10 = QtWidgets.QLabel(self.centralwidget)
        self.label_10.setGeometry(QtCore.QRect(0, 290, 61, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.label_10.setObjectName("label_10")
        self.label_11 = QtWidgets.QLabel(self.centralwidget)
        self.label_11.setGeometry(QtCore.QRect(70, 30, 131, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setUnderline(True)
        self.label_11.setFont(font)
        self.label_11.setObjectName("label_11")
        self.label_12 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_12.setGeometry(QtCore.QRect(380, 30, 61, 16))
        self.label_12.setObjectName("label_12")
        self.label_13 = QtWidgets.QLabel(self.centralwidget)
        self.label_13.setGeometry(QtCore.QRect(320, 30, 61, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_9.setFont(font)
        self.label_8.setFont(font)
        self.label_7.setFont(font)
        self.label_12.setFont(font)
        self.label_10.setFont(font)
        self.label_11.setFont(font)
        self.label_12.setFont(font)
        self.label_13.setFont(font)

        self.label_13.setObjectName("label_13")
        self.currentstatus = QtWidgets.QTextBrowser(self.centralwidget)
        self.currentstatus.setGeometry(QtCore.QRect(0, 450, 1051, 141))
        self.currentstatus.setObjectName("currentstatus")

        self.label_14 = QtWidgets.QLabel(self.centralwidget)
        self.label_14.setGeometry(QtCore.QRect(600, 370, 81, 16))
        self.label_14.setObjectName("label_14")
        self.secondscheckingprice = QtWidgets.QSpinBox(self.centralwidget)
        self.secondscheckingprice.setGeometry(QtCore.QRect(0, 370, 31, 16))
        self.secondscheckingprice.setObjectName("secondscheckingprice")
        self.line_2 = QtWidgets.QFrame(self.centralwidget)
        self.line_2.setGeometry(QtCore.QRect(0, 350, 1041, 16))
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.sleepbox = QtWidgets.QLabel(self.centralwidget)
        self.sleepbox.setGeometry(QtCore.QRect(50, 370, 341, 16))
        self.sleepbox.setObjectName("sleepbox")
        self.tokentokennumerator = QtWidgets.QLineEdit(self.centralwidget)
        self.tokentokennumerator.setGeometry(QtCore.QRect(0, 390, 31, 16))
        font = QtGui.QFont()
        font.setPointSize(10)

        self.tokentokennumerator.setObjectName("tokentokennumerator")
        self.tokentokennumerator.setFont(font)

        self.tokentokennumeratorbox = QtWidgets.QLabel(self.centralwidget)
        self.tokentokennumeratorbox.setGeometry(QtCore.QRect(50, 390, 321, 16))
        self.tokentokennumeratorbox.setObjectName("tokentokennumeratorbox")
        font = QtGui.QFont()
        font.setPointSize(10)
        self.tokentokennumeratorbox.setFont(font)
        self.line_3 = QtWidgets.QFrame(self.centralwidget)
        self.line_3.setGeometry(QtCore.QRect(-40, 440, 1081, 20))
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.label_17 = QtWidgets.QLabel(self.centralwidget)
        self.label_17.setGeometry(QtCore.QRect(710, 360, 291, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_17.setFont(font)
        self.label_17.setObjectName("label_17")
        self.infurabox = QtWidgets.QLabel(self.centralwidget)
        self.infurabox.setGeometry(QtCore.QRect(230, 410, 81, 16))
        self.infurabox.setObjectName("infurabox")
        self.infurabox.setFont(font)
        self.infuraurl = QtWidgets.QLineEdit(self.centralwidget)
        self.infuraurl.setGeometry(QtCore.QRect(0, 410, 221, 16))
        self.infuraurl.setObjectName("infuraurl")

        self.label_15 = QtWidgets.QLabel(self.centralwidget)
        self.label_15.setGeometry(QtCore.QRect(200, 30, 81, 16))
        self.label_15.setObjectName("label_15")
        self.label_15.setFont(font)
        self.token1name = QtWidgets.QLineEdit(self.centralwidget)
        self.token1name.setGeometry(QtCore.QRect(200, 50, 71, 16))
        self.token1name.setObjectName("token1name")
        self.token2name = QtWidgets.QLineEdit(self.centralwidget)
        self.token2name.setGeometry(QtCore.QRect(200, 80, 71, 16))
        self.token2name.setObjectName("token2name")
        self.token3name = QtWidgets.QLineEdit(self.centralwidget)
        self.token3name.setGeometry(QtCore.QRect(200, 110, 71, 16))
        self.token3name.setObjectName("token3name")
        self.token4name = QtWidgets.QLineEdit(self.centralwidget)
        self.token4name.setGeometry(QtCore.QRect(200, 140, 71, 16))
        self.token4name.setObjectName("token4name")
        self.token5name = QtWidgets.QLineEdit(self.centralwidget)
        self.token5name.setGeometry(QtCore.QRect(200, 170, 71, 16))
        self.token5name.setObjectName("token5name")
        self.token6name = QtWidgets.QLineEdit(self.centralwidget)
        self.token6name.setGeometry(QtCore.QRect(200, 200, 71, 16))
        self.token6name.setObjectName("token6name")
        self.token7name = QtWidgets.QLineEdit(self.centralwidget)
        self.token7name.setGeometry(QtCore.QRect(200, 230, 71, 16))
        self.token7name.setObjectName("token7name")
        self.token8name = QtWidgets.QLineEdit(self.centralwidget)
        self.token8name.setGeometry(QtCore.QRect(200, 260, 71, 16))
        self.token8name.setObjectName("token8name")
        self.token9name = QtWidgets.QLineEdit(self.centralwidget)
        self.token9name.setGeometry(QtCore.QRect(200, 290, 71, 16))
        self.token9name.setObjectName("token9name")
        self.token10name = QtWidgets.QLineEdit(self.centralwidget)
        self.token10name.setGeometry(QtCore.QRect(200, 320, 71, 16))
        self.token10name.setObjectName("token10name")
        # self.updatename = QtWidgets.QPushButton(self.centralwidget)
        # self.updatename.setGeometry(QtCore.QRect(200, 340, 81, 20))
        # self.updatename.setObjectName("updatename")
        self.secondscheckingprice_2 = QtWidgets.QSpinBox(self.centralwidget)
        self.secondscheckingprice_2.setGeometry(QtCore.QRect(400, 370, 31, 16))
        self.secondscheckingprice_2.setObjectName("secondscheckingprice_2")
        self.sleepbox_2 = QtWidgets.QLabel(self.centralwidget)
        self.sleepbox_2.setGeometry(QtCore.QRect(450, 370, 251, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.sleepbox_2.setFont(font)
        self.sleepbox_2.setObjectName("sleepbox_2")
        self.line_4 = QtWidgets.QFrame(self.centralwidget)
        self.line_4.setGeometry(QtCore.QRect(380, 360, 20, 81))
        self.line_4.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_4.setObjectName("line_4")
        self.Maxslippage = QtWidgets.QLineEdit(self.centralwidget)
        self.Maxslippage.setGeometry(QtCore.QRect(400, 390, 31, 16))
        self.Maxslippage.setObjectName("Maxslippage")
        self.label_14 = QtWidgets.QLabel(self.centralwidget)
        self.label_14.setGeometry(QtCore.QRect(450, 390, 191, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_14.setFont(font)
        self.label_14.setObjectName("label_14")
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(400, 410, 31, 16))
        self.lineEdit.setObjectName("lineEdit")
        self.label_16 = QtWidgets.QLabel(self.centralwidget)
        self.label_16.setGeometry(QtCore.QRect(450, 410, 271, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_16.setFont(font)
        self.label_16.setObjectName("label_16")
        # self.oke2 = self.updatename.clicked.connect(self.updatenames)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1056, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.log = QTextEdit()
        form_layout.addWidget(self.log)
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(690, 360, 20, 91))
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")

        self.label_19 = QtWidgets.QLabel(self.centralwidget)
        self.label_19.setGeometry(QtCore.QRect(280, 30, 31, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_19.setFont(font)
        self.label_19.setObjectName("label_19")
        self.token1decimals = QtWidgets.QLineEdit(self.centralwidget)
        self.token1decimals.setGeometry(QtCore.QRect(280, 50, 31, 16))
        self.token1decimals.setObjectName("token1decimals")
        self.token8decimals = QtWidgets.QLineEdit(self.centralwidget)
        self.token8decimals.setGeometry(QtCore.QRect(280, 260, 31, 16))
        self.token8decimals.setObjectName("token8decimals")
        self.token10decimals = QtWidgets.QLineEdit(self.centralwidget)
        self.token10decimals.setGeometry(QtCore.QRect(280, 320, 31, 16))
        self.token10decimals.setObjectName("token10decimals")
        self.token3decimals = QtWidgets.QLineEdit(self.centralwidget)
        self.token3decimals.setGeometry(QtCore.QRect(280, 110, 31, 16))
        self.token3decimals.setObjectName("token3decimals")
        self.token5decimals = QtWidgets.QLineEdit(self.centralwidget)
        self.token5decimals.setGeometry(QtCore.QRect(280, 170, 31, 16))
        self.token5decimals.setObjectName("token5decimals")
        self.token2decimals = QtWidgets.QLineEdit(self.centralwidget)
        self.token2decimals.setGeometry(QtCore.QRect(280, 80, 31, 16))
        self.token2decimals.setObjectName("token2decimals")
        self.token6decimals = QtWidgets.QLineEdit(self.centralwidget)
        self.token6decimals.setGeometry(QtCore.QRect(280, 200, 31, 16))
        self.token6decimals.setObjectName("token6decimals")
        self.token7decimals = QtWidgets.QLineEdit(self.centralwidget)
        self.token7decimals.setGeometry(QtCore.QRect(280, 230, 31, 16))
        self.token7decimals.setObjectName("token7decimals")
        self.token4decimals = QtWidgets.QLineEdit(self.centralwidget)
        self.token4decimals.setGeometry(QtCore.QRect(280, 140, 31, 16))
        self.token4decimals.setObjectName("token4decimals")
        self.token9decimals = QtWidgets.QLineEdit(self.centralwidget)
        self.token9decimals.setGeometry(QtCore.QRect(280, 290, 31, 16))
        self.token9decimals.setObjectName("token9decimals")

        self.maxgwei = QtWidgets.QLabel(self.centralwidget)
        self.maxgwei.setGeometry(QtCore.QRect(710, 400, 111, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.maxgwei.setFont(font)
        self.maxgwei.setObjectName("maxgwei")

        self.progress = QTextEdit()
        form_layout.addWidget(self.progress)
        self.retranslateUi(MainWindow)
        QThread.currentThread().setObjectName('main')  # threads can be named, useful for log output
        self.__workers_done = None
        self.__threads = None
        # QtCore.QMetaObject.connectSlotsByName(MainWindow)
        if configfile.secondscheckingprice_2 != '0':
            self.secondscheckingprice_2.setValue(int(configfile.secondscheckingprice_2))
        if configfile.secondscheckingprice != '0':
            self.secondscheckingprice.setValue(int(configfile.secondscheckingprice))
        if configfile.infuraurl != '0':
            self.infuraurl.setText(str(configfile.infuraurl))
        if configfile.tokentokennumerator != '0':
            self.tokentokennumerator.setText(str(configfile.tokentokennumerator))

        if configfile.maxgweinumber != '0':
            self.maxgweinumber.setText(str(configfile.maxgweinumber))
        if configfile.diffdepositaddress != '0':
            self.diffdepositaddress.setText(str(configfile.diffdepositaddress))

        try:
            if configfile.maxgwei != '0':
                pass
        except:
            o = 0
        try:
            if configfile.diffdeposit != '0':
                self.diffdeposit.setChecked(1)
        except:
            o = 0
        try:
            if configfile.activatetoken1 != '0':
                self.activatetoken1.setChecked(1)
        except:
            o = 0
        try:
            if configfile.debugmode != '0':
                self.debugmode.setChecked(1)
        except:
            o = 0
        try:
            if configfile.tradewithETHtoken1 != '0':
                self.tradewithETHtoken1.setChecked(1)
        except:
            o = 0
        try:
            if configfile.tradewithERCtoken1 != '0':
                self.tradewithERCtoken1.setChecked(1)
        except:
            o = 0
        try:
            if configfile.activatetoken2 != '0':
                self.activatetoken2.setChecked(1)
        except:
            o = 0

        try:
            if configfile.tradewithETHtoken2 != '0':
                self.tradewithETHtoken2.setChecked(1)
        except:
            o = 0
        try:
            if configfile.tradewithERCtoken2 != '0':
                self.tradewithERCtoken2.setChecked(1)
        except:
            o = 0
        try:
            if configfile.activatetoken3 != '0':
                self.activatetoken3.setChecked(1)
        except:
            o = 0

        try:
            if configfile.stoplosstoken1 != '0':
                self.stoplosstoken1.setChecked(1)
        except:
            o = 0
        try:
            if configfile.stoplosstoken2 != '0':
                self.stoplosstoken2.setChecked(1)
        except:
            o = 0
        try:
            if configfile.stoplosstoken3 != '0':
                self.stoplosstoken3.setChecked(1)
        except:
            o = 0
        try:
            if configfile.stoplosstoken4 != '0':
                self.stoplosstoken4.setChecked(1)
        except:
            o = 0
        try:
            if configfile.stoplosstoken5 != '0':
                self.stoplosstoken5.setChecked(1)
        except:
            o = 0
        try:
            if configfile.stoplosstoken6 != '0':
                self.stoplosstoken6.setChecked(1)
        except:
            o = 0
        try:
            if configfile.stoplosstoken7 != '0':
                self.stoplosstoken7.setChecked(1)
        except:
            o = 0
        try:
            if configfile.stoplosstoken8 != '0':
                self.stoplosstoken8.setChecked(1)
        except:
            o = 0
        try:
            if configfile.stoplosstoken9 != '0':
                self.stoplosstoken9.setChecked(1)
        except:
            o = 0
        try:
            if configfile.stoplosstoken10 != '0':
                self.stoplosstoken10.setChecked(1)
        except:
            o = 0

        try:
            if configfile.tradewithETHtoken3 != '0':
                self.tradewithETHtoken3.setChecked(1)
        except:
            o = 0
        try:
            if configfile.tradewithERCtoken3 != '0':
                self.tradewithERCtoken3.setChecked(1)
        except:
            o = 0
        try:
            if configfile.activatetoken4 != '0':
                self.activatetoken4.setChecked(1)
        except:
            o = 0

        try:
            if configfile.tradewithETHtoken4 != '0':
                self.tradewithETHtoken4.setChecked(1)
        except:
            o = 0
        try:
            if configfile.tradewithERCtoken4 != '0':
                self.tradewithERCtoken4.setChecked(1)
        except:
            o = 0
        try:
            if configfile.activatetoken5 != '0':
                self.activatetoken5.setChecked(1)
        except:
            o = 0

        try:
            if configfile.tradewithETHtoken5 != '0':
                self.tradewithETHtoken5.setChecked(1)
        except:
            o = 0
        try:
            if configfile.tradewithERCtoken5 != '0':
                self.tradewithERCtoken5.setChecked(1)
        except:
            o = 0

        try:
            if configfile.activatetoken6 != '0':
                self.activatetoken6.setChecked(1)
        except:
            o = 0

        try:
            if configfile.tradewithETHtoken6 != '0':
                self.tradewithETHtoken6.setChecked(1)
        except:
            o = 0
        try:
            if configfile.tradewithERCtoken6 != '0':
                self.tradewithERCtoken6.setChecked(1)
        except:
            o = 0

        try:
            if configfile.activatetoken7 != '0':
                self.activatetoken7.setChecked(1)
        except:
            o = 0

        try:
            if configfile.tradewithETHtoken7 != '0':
                self.tradewithETHtoken7.setChecked(1)
        except:
            o = 0
        try:
            if configfile.tradewithERCtoken7 != '0':
                self.tradewithERCtoken7.setChecked(1)
        except:
            o = 0

        try:
            if configfile.activatetoken8 != '0':
                self.activatetoken8.setChecked(1)
        except:
            o = 0

        try:
            if configfile.tradewithETHtoken8 != '0':
                self.tradewithETHtoken8.setChecked(1)
        except:
            o = 0
        try:
            if configfile.tradewithERCtoken8 != '0':
                self.tradewithERCtoken8.setChecked(1)
        except:
            o = 0

        try:
            if configfile.activatetoken9 != '0':
                self.activatetoken9.setChecked(1)
        except:
            o = 0

        try:
            if configfile.tradewithETHtoken9 != '0':
                self.tradewithETHtoken9.setChecked(1)
        except:
            o = 0
        try:
            if configfile.tradewithERCtoken9 != '0':
                self.tradewithERCtoken9.setChecked(1)
        except:
            o = 0

        try:
            if configfile.activatetoken10 != '0':
                self.activatetoken10.setChecked(1)
        except:
            o = 0

        try:
            if configfile.tradewithETHtoken10 != '0':
                self.tradewithETHtoken10.setChecked(1)
        except:
            o = 0
        try:
            if configfile.tradewithERCtoken10 != '0':
                self.tradewithERCtoken10.setChecked(1)
        except:
            o = 0
        if configfile.token1name != '0' and self.token1ethaddress.text() != '':
            self.token1name.setText(configfile.token1name)
        if configfile.max_slippage != '0':
            self.Maxslippage.setText(configfile.max_slippage)
        if configfile.ethtokeep != '0':
            self.lineEdit.setText(configfile.ethtokeep)
        if configfile.token2name != '0' and self.token2ethaddress.text() != '':
            self.token2name.setText(configfile.token2name)
        if configfile.token3name != '0' and self.token3ethaddress.text() != '':
            self.token3name.setText(configfile.token3name)
        if configfile.token4name != '0' and self.token4ethaddress.text() != '':
            self.token4name.setText(configfile.token4name)
        if configfile.token5name != '0' and self.token5ethaddress.text() != '':
            self.token5name.setText(configfile.token5name)
        if configfile.token6name != '0' and self.token6ethaddress.text() != '':
            self.token6name.setText(configfile.token6name)
        if configfile.token7name != '0' and self.token7ethaddress.text() != '':
            self.token7name.setText(configfile.token7name)
        if configfile.token8name != '0' and self.token8ethaddress.text() != '':
            self.token8name.setText(configfile.token8name)
        if configfile.token9name != '0' and self.token9ethaddress.text() != '':
            self.token9name.setText(configfile.token9name)
        if configfile.token10name != '0' and self.token10ethaddress.text() != '':
            self.token10name.setText(configfile.token10name)

        if configfile.token1decimals != '0':
            self.token1decimals.setText(configfile.token1decimals)
        if configfile.token2decimals != '0':
            self.token2decimals.setText(configfile.token2decimals)
        if configfile.token3decimals != '0':
            self.token3decimals.setText(configfile.token3decimals)
        if configfile.token4decimals != '0':
            self.token4decimals.setText(configfile.token4decimals)
        if configfile.token5decimals != '0':
            self.token5decimals.setText(configfile.token5decimals)
        if configfile.token6decimals != '0':
            self.token6decimals.setText(configfile.token6decimals)
        if configfile.token7decimals != '0':
            self.token7decimals.setText(configfile.token7decimals)
        if configfile.token8decimals != '0':
            self.token8decimals.setText(configfile.token8decimals)
        if configfile.token9decimals != '0':
            self.token9decimals.setText(configfile.token9decimals)
        if configfile.token10decimals != '0':
            self.token10decimals.setText(configfile.token10decimals)

        self.sleepbox.setFont(font)
        self.label_18.setFont(font)

        self.maincoinoption.addItem('BNB', userData='BNB')
        self.maincoinoption.addItem('BUSD', userData='BUSD')
        self.maincoinoption.addItem('DAI', userData='DAI')
        self.maincoinoption.addItem('USDC', userData='USDC')
        self.maincoinoption.addItem('wBTC', userData='wBTC')
        self.maincoinoption.addItem('ETH', userData='ETH')
        if configfile.maincoinoption == 'BNB':
            self.maincoinoption.setCurrentIndex(0)
        if configfile.maincoinoption == 'BUSD':
            self.maincoinoption.setCurrentIndex(1)
        if configfile.maincoinoption == 'DAI':
            self.maincoinoption.setCurrentIndex(2)
        if configfile.maincoinoption == 'USDC':
            self.maincoinoption.setCurrentIndex(3)
        if configfile.maincoinoption == 'wBTC':
            self.maincoinoption.setCurrentIndex(4)
        if configfile.maincoinoption == 'ETH':
            self.maincoinoption.setCurrentIndex(5)
        self.tradewithETHtoken1.setFont(font)
        self.tradewithETHtoken2.setFont(font)
        self.tradewithETHtoken3.setFont(font)
        self.tradewithETHtoken4.setFont(font)
        self.tradewithETHtoken5.setFont(font)
        self.tradewithETHtoken6.setFont(font)
        self.tradewithETHtoken7.setFont(font)
        self.tradewithETHtoken8.setFont(font)
        self.tradewithETHtoken9.setFont(font)
        self.tradewithETHtoken10.setFont(font)
        self.tradewithERCtoken1.setFont(font)
        self.tradewithERCtoken2.setFont(font)
        self.tradewithERCtoken3.setFont(font)
        self.tradewithERCtoken4.setFont(font)
        self.tradewithERCtoken5.setFont(font)
        self.tradewithERCtoken6.setFont(font)
        self.tradewithERCtoken7.setFont(font)
        self.tradewithERCtoken8.setFont(font)
        self.tradewithERCtoken9.setFont(font)
        self.tradewithERCtoken10.setFont(font)
        self.stoplosstoken10.setFont(font)
        self.stoplosstoken9.setFont(font)
        self.stoplosstoken8.setFont(font)
        self.stoplosstoken7.setFont(font)
        self.stoplosstoken6.setFont(font)
        self.stoplosstoken5.setFont(font)
        self.stoplosstoken4.setFont(font)
        self.stoplosstoken3.setFont(font)
        self.stoplosstoken2.setFont(font)
        self.stoplosstoken1.setFont(font)
        self.maincoinoption.setFont(font)
        self.token1low.setFont(font)
        self.token2low.setFont(font)
        self.token3low.setFont(font)
        self.token4low.setFont(font)
        self.token5low.setFont(font)
        self.token6low.setFont(font)
        self.token7low.setFont(font)
        self.token8low.setFont(font)
        self.token9low.setFont(font)
        self.token10low.setFont(font)
        self.token1high.setFont(font)
        self.token2high.setFont(font)
        self.token3high.setFont(font)
        self.token4high.setFont(font)
        self.token5high.setFont(font)
        self.token6high.setFont(font)
        self.token7high.setFont(font)
        self.token8high.setFont(font)
        self.token9high.setFont(font)
        self.token10high.setFont(font)
        self.token1ethaddress.setFont(font)
        self.token2ethaddress.setFont(font)
        self.token3ethaddress.setFont(font)
        self.token4ethaddress.setFont(font)
        self.token5ethaddress.setFont(font)
        self.token6ethaddress.setFont(font)
        self.token7ethaddress.setFont(font)
        self.token8ethaddress.setFont(font)
        self.currentstatus.setFont(font)
        self.token9ethaddress.setFont(font)
        self.token10ethaddress.setFont(font)
        self.secondscheckingprice.setFont(font)
        self.secondscheckingprice_2.setFont(font)
        self.tokentokennumerator.setFont(font)
        self.Maxslippage.setFont(font)
        self.lineEdit.setFont(font)
        self.infuraurl.setFont(font)
        font = QtGui.QFont()
        font.setPointSize(7)
        # self.updatename.setFont(font)
        self.retranslateUi(MainWindow)
        sys.stdout = Port(self.currentstatus)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Pancakeswap trading bot no.2"))
        self.startbutton.setText(_translate("MainWindow", "Start"))
        self.activatetoken1.setText(_translate("MainWindow", "Activate"))
        self.tradewithETHtoken1.setText(_translate("MainWindow", "Trading w/ main"))
        self.tradewithERCtoken1.setText(_translate("MainWindow", "Trade w/ token"))
        self.tradewithETHtoken2.setText(_translate("MainWindow", "Trading w/ main"))
        self.activatetoken2.setText(_translate("MainWindow", "Activate"))
        self.tradewithERCtoken2.setText(_translate("MainWindow", "Trade w/ token"))
        self.tradewithETHtoken3.setText(_translate("MainWindow", "Trading w/ main"))
        self.activatetoken3.setText(_translate("MainWindow", "Activate"))
        self.tradewithERCtoken3.setText(_translate("MainWindow", "Trade w/ token"))
        self.tradewithERCtoken5.setText(_translate("MainWindow", "Trade w/ token"))
        self.tradewithETHtoken4.setText(_translate("MainWindow", "Trading w/ main"))
        self.tradewithERCtoken6.setText(_translate("MainWindow", "Trade w/ token"))
        self.tradewithETHtoken6.setText(_translate("MainWindow", "Trading w/ main"))
        self.activatetoken4.setText(_translate("MainWindow", "Activate"))
        self.activatetoken6.setText(_translate("MainWindow", "Activate"))
        self.tradewithERCtoken4.setText(_translate("MainWindow", "Trade w/ token"))
        self.tradewithETHtoken5.setText(_translate("MainWindow", "Trading w/ main"))
        self.activatetoken5.setText(_translate("MainWindow", "Activate"))
        self.tradewithERCtoken8.setText(_translate("MainWindow", "Trade w/ token"))
        self.tradewithETHtoken7.setText(_translate("MainWindow", "Trading w/ main"))
        self.tradewithERCtoken9.setText(_translate("MainWindow", "Trade w/ token"))
        self.tradewithETHtoken9.setText(_translate("MainWindow", "Trading w/ main"))
        self.activatetoken7.setText(_translate("MainWindow", "Activate"))
        self.activatetoken9.setText(_translate("MainWindow", "Activate"))
        self.maxgwei.setText(_translate("MainWindow", "GWEI for Trading w/ main:"))
        self.tradewithERCtoken7.setText(_translate("MainWindow", "Trade w/ token"))
        self.tradewithETHtoken8.setText(_translate("MainWindow", "Trading w/ main"))
        self.activatetoken8.setText(_translate("MainWindow", "Activate"))
        self.activatetoken10.setText(_translate("MainWindow", "Activate"))
        self.tradewithETHtoken10.setText(_translate("MainWindow", "Trading w/ main"))
        self.tradewithERCtoken10.setText(_translate("MainWindow", "Trade w/ token"))
        self.label.setText(_translate("MainWindow", "Token 1"))
        self.label_2.setText(_translate("MainWindow", "Token 2"))
        self.label_3.setText(_translate("MainWindow", "Token 4"))
        self.label_4.setText(_translate("MainWindow", "Token 3"))
        self.label_5.setText(_translate("MainWindow", "Token 6"))
        self.label_6.setText(_translate("MainWindow", "Token 5"))
        self.label_7.setText(_translate("MainWindow", "Token 8"))
        self.label_8.setText(_translate("MainWindow", "Token 7"))
        self.label_9.setText(_translate("MainWindow", "Token 10"))
        self.label_10.setText(_translate("MainWindow", "Token 9"))
        self.label_11.setText(_translate("MainWindow", "Token address"))
        self.label_12.setText(_translate("MainWindow", "Sell($)"))
        self.label_13.setText(_translate("MainWindow", "Buy($)"))
        self.label_99.setText(_translate("MainWindow", "Buy/Sell boundary ($):"))
        self.stopbutton.setText(_translate("MainWindow", "Stop"))
        self.sleepbox.setText(_translate("MainWindow", "Seconds between checking price (min. 1 sec)"))
        self.tokentokennumeratorbox.setText(_translate("MainWindow", "Tokentokennumerator (3.3= standard)"))
        self.infurabox.setText(_translate("MainWindow", "Router URL"))
        self.label_15.setText(_translate("MainWindow", "Name"))
        self.sleepbox_2.setText(_translate("MainWindow", "Seconds waiting after trade"))
        self.label_14.setText(_translate("MainWindow", "Max slippage (1%=0.01)"))
        self.label_16.setText(_translate("MainWindow", "$ to keep in BNB after trade"))
        self.label_18.setText(_translate("MainWindow", "Main coin/token:"))
        self.stoplosstoken1.setText(_translate("MainWindow", "Stoploss($):"))
        self.stoplosstoken2.setText(_translate("MainWindow", "Stoploss($):"))
        self.stoplosstoken3.setText(_translate("MainWindow", "Stoploss($):"))
        self.stoplosstoken6.setText(_translate("MainWindow", "Stoploss($):"))
        self.stoplosstoken4.setText(_translate("MainWindow", "Stoploss($):"))
        self.diffdeposit.setText(_translate("MainWindow", "Different deposit address:"))
        self.debugmode.setText(_translate("MainWindow", "Debug mode"))
        self.stoplosstoken5.setText(_translate("MainWindow", "Stoploss($):"))
        self.stoplosstoken9.setText(_translate("MainWindow", "Stoploss($):"))
        self.stoplosstoken7.setText(_translate("MainWindow", "Stoploss($):"))
        self.stoplosstoken8.setText(_translate("MainWindow", "Stoploss($):"))
        self.stoplosstoken10.setText(_translate("MainWindow", "Stoploss($):"))
        # self.updatename.setText(_translate("MainWindow", "Update names"))
        self.label_19.setText(_translate("MainWindow", "Dec."))

    def updatenames(self):
        try:
            if self.token1ethaddress.text() != '' or '0':
                token1smallcasename = 0
                token1smallcasename = \
                    cg.get_coin_info_from_contract_address_by_id(contract_address=self.token1ethaddress.text(),
                                                                 id='binancecoin')['symbol']
                self.token1name.setText(token1smallcasename)
        except:
            pass
        try:
            if self.token2ethaddress.text() != '' or '0':
                token2smallcasename = 0
                token2smallcasename = \
                    cg.get_coin_info_from_contract_address_by_id(contract_address=self.token2ethaddress.text(),
                                                                 id='binancecoin')['symbol']
                self.token2name.setText(token2smallcasename)
        except:
            pass
        try:
            if self.token3ethaddress.text() != '' or '0':
                token3smallcasename = 0
                token3smallcasename = \
                    cg.get_coin_info_from_contract_address_by_id(contract_address=self.token3ethaddress.text(),
                                                                 id='binancecoin')['symbol']
                self.token3name.setText(token3smallcasename)
        except:
            pass
        try:
            if self.token4ethaddress.text() != '' or '0':
                token4smallcasename = 0
                token4smallcasename = \
                    cg.get_coin_info_from_contract_address_by_id(contract_address=self.token4ethaddress.text(),
                                                                 id='binancecoin')['symbol']
                self.token4name.setText(token4smallcasename)
        except:
            pass
        try:
            if self.token5ethaddress.text() != '' or '0':
                token5smallcasename = 0
                token5smallcasename = \
                    cg.get_coin_info_from_contract_address_by_id(contract_address=self.token5ethaddress.text(),
                                                                 id='binancecoin')['symbol']
                self.token5name.setText(token5smallcasename)
        except:
            pass
        try:
            if self.token6ethaddress.text() != '' or '0':
                token6smallcasename = 0
                token6smallcasename = \
                    cg.get_coin_info_from_contract_address_by_id(contract_address=self.token6ethaddress.text(),
                                                                 id='binancecoin')['symbol']
                self.token6name.setText(token6smallcasename)
        except:
            pass
        try:
            if self.token7ethaddress.text() != '' or '0':
                token7smallcasename = 0
                token7smallcasename = \
                    cg.get_coin_info_from_contract_address_by_id(contract_address=self.token7ethaddress.text(),
                                                                 id='binancecoin')['symbol']
                self.token7name.setText(token7smallcasename)
        except:
            pass
        try:
            if self.token8ethaddress.text() != '' or '0':
                token8smallcasename = 0
                token8smallcasename = \
                    cg.get_coin_info_from_contract_address_by_id(contract_address=self.token8ethaddress.text(),
                                                                 id='binancecoin')[
                        'symbol']
                self.token8name.setText(token8smallcasename)
        except:
            pass
        try:
            if self.token9ethaddress.text() != '' or '0':
                token9smallcasename = 0
                token9smallcasename = \
                    cg.get_coin_info_from_contract_address_by_id(contract_address=self.token9ethaddress.text(),
                                                                 id='binancecoin')[
                        'symbol']
                self.token9name.setText(token9smallcasename)
        except:
            pass
        try:
            if self.token10ethaddress.text() != '' or '0':
                token10smallcasename = 0
                token10smallcasename = \
                    cg.get_coin_info_from_contract_address_by_id(contract_address=self.token10ethaddress.text(),
                                                                 id='binancecoin')[
                        'symbol']
                self.token10name.setText(token10smallcasename)
        except:
            pass
        # if token1smallcasename == 0:
        #   self.token1name.setText('')
        # if token2smallcasename == 0:
        #   self.token2name.setText('')
        # if token3smallcasename == 0:
        #   self.token3name.setText('')
        # if token4smallcasename == 0:
        #    self.token4name.setText('')
        # if token5smallcasename == 0:
        #    self.token5name.setText('')
        # if token6smallcasename == 0:
        #    self.token6name.setText('')
        # if token7smallcasename == 0:
        #    self.token7name.setText('')
        # if token8smallcasename == 0:
        #    self.token8name.setText('')
        # if token9smallcasename == 0:
        #    self.token9name.setText('')
        # if token10smallcasename == 0:
        #    self.token10name.setText('')

    @QtCore.pyqtSlot()
    def start_threads(self):
        try:
            print('Starting bot')
            maincoinoption = self.maincoinoption.currentText()
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            if configfile.debugmode == '1':
                print(str(e) + ' on line: ' + str(exception_traceback.tb_lineno))
        try:
            self.secondscheckingprice_2.setEnabled(False)
            self.secondscheckingprice.setEnabled(False)
            self.infuraurl.setEnabled(False)
            self.tokentokennumerator.setEnabled(False)
            self.activatetoken1.setEnabled(False)
            self.tradewithETHtoken1.setEnabled(False)
            self.tradewithERCtoken1.setEnabled(False)
            self.token1ethaddress.setReadOnly(True)
            self.token1low.setReadOnly(True)
            self.token1high.setReadOnly(True)
            self.token1ethaddress.setDisabled(True)
            self.token1low.setDisabled(True)
            self.token1high.setDisabled(True)
            self.debugmode.setDisabled(True)
            self.diffdeposit.setDisabled(True)
            self.maxgweinumber.setReadOnly(True)
            self.diffdepositaddress.setReadOnly(True)
            self.maxgweinumber.setDisabled(True)
            self.diffdepositaddress.setDisabled(True)

            self.token1decimals.setDisabled(True)
            self.token2decimals.setDisabled(True)
            self.token3decimals.setDisabled(True)
            self.token4decimals.setDisabled(True)
            self.token5decimals.setDisabled(True)
            self.token6decimals.setDisabled(True)
            self.token7decimals.setDisabled(True)
            self.token8decimals.setDisabled(True)
            self.token9decimals.setDisabled(True)
            self.token10decimals.setDisabled(True)

            self.activatetoken2.setEnabled(False)
            self.tradewithETHtoken2.setEnabled(False)
            self.tradewithERCtoken2.setEnabled(False)
            self.token2ethaddress.setReadOnly(True)
            self.token2low.setReadOnly(True)
            self.token2high.setReadOnly(True)
            self.token2ethaddress.setDisabled(True)
            self.token2low.setDisabled(True)
            self.token2high.setDisabled(True)

            self.token1name.setReadOnly(True)
            self.token2name.setReadOnly(True)
            self.token3name.setReadOnly(True)
            self.token4name.setReadOnly(True)
            self.token5name.setReadOnly(True)
            self.token6name.setReadOnly(True)
            self.token7name.setReadOnly(True)
            self.token8name.setReadOnly(True)
            self.token9name.setReadOnly(True)
            self.token10name.setReadOnly(True)

            self.activatetoken3.setEnabled(False)
            self.tradewithETHtoken3.setEnabled(False)
            self.tradewithERCtoken3.setEnabled(False)
            self.token3ethaddress.setReadOnly(True)
            self.token3low.setReadOnly(True)
            self.token3high.setReadOnly(True)
            self.token3ethaddress.setDisabled(True)
            self.token3low.setDisabled(True)
            self.token3high.setDisabled(True)

            self.activatetoken4.setEnabled(False)
            self.tradewithETHtoken4.setEnabled(False)
            self.tradewithERCtoken4.setEnabled(False)
            self.token4ethaddress.setReadOnly(True)
            self.token4low.setReadOnly(True)
            self.token4high.setReadOnly(True)
            self.token4ethaddress.setDisabled(True)
            self.token4low.setDisabled(True)
            self.token4high.setDisabled(True)

            self.activatetoken5.setEnabled(False)
            self.tradewithETHtoken5.setEnabled(False)
            self.tradewithERCtoken5.setEnabled(False)
            self.token5ethaddress.setReadOnly(True)
            self.token5low.setReadOnly(True)
            self.token5high.setReadOnly(True)
            self.token5ethaddress.setDisabled(True)
            self.token5low.setDisabled(True)
            self.token5high.setDisabled(True)

            self.activatetoken6.setEnabled(False)
            self.tradewithETHtoken6.setEnabled(False)
            self.tradewithERCtoken6.setEnabled(False)
            self.token6ethaddress.setReadOnly(True)
            self.token6low.setReadOnly(True)
            self.token6high.setReadOnly(True)
            self.token6ethaddress.setDisabled(True)
            self.token6low.setDisabled(True)
            self.token6high.setDisabled(True)

            self.activatetoken7.setEnabled(False)
            self.tradewithETHtoken7.setEnabled(False)
            self.tradewithERCtoken7.setEnabled(False)
            self.token7ethaddress.setReadOnly(True)
            self.token7low.setReadOnly(True)
            self.token7high.setReadOnly(True)
            self.token7ethaddress.setDisabled(True)
            self.token7low.setDisabled(True)
            self.token7high.setDisabled(True)

            # self.updatename.setDisabled(True)

            self.activatetoken8.setEnabled(False)
            self.tradewithETHtoken8.setEnabled(False)
            self.tradewithERCtoken8.setEnabled(False)
            self.token8ethaddress.setReadOnly(True)
            self.token8low.setReadOnly(True)
            self.token8high.setReadOnly(True)
            self.token8ethaddress.setDisabled(True)
            self.token8low.setDisabled(True)
            self.token8high.setDisabled(True)

            self.activatetoken9.setEnabled(False)
            self.tradewithETHtoken9.setEnabled(False)
            self.tradewithERCtoken9.setEnabled(False)
            self.token9ethaddress.setReadOnly(True)
            self.token9low.setReadOnly(True)
            self.token9high.setReadOnly(True)
            self.token9ethaddress.setDisabled(True)
            self.token9low.setDisabled(True)
            self.token9high.setDisabled(True)

            self.activatetoken10.setEnabled(False)
            self.tradewithETHtoken10.setEnabled(False)
            self.tradewithERCtoken10.setEnabled(False)
            self.token10ethaddress.setReadOnly(True)
            self.token10low.setReadOnly(True)
            self.token10high.setReadOnly(True)
            self.token10ethaddress.setDisabled(True)
            self.token10low.setDisabled(True)
            self.token10high.setDisabled(True)
            self.Maxslippage.setDisabled(True)
            self.lineEdit.setDisabled(True)
            self.maincoinoption.setDisabled(True)

            self.token1stoploss.setDisabled(True)
            self.token2stoploss.setDisabled(True)
            self.token3stoploss.setDisabled(True)
            self.token4stoploss.setDisabled(True)
            self.token5stoploss.setDisabled(True)
            self.token6stoploss.setDisabled(True)
            self.token7stoploss.setDisabled(True)
            self.token8stoploss.setDisabled(True)
            self.token9stoploss.setDisabled(True)
            self.token10stoploss.setDisabled(True)
            self.token1stoploss.setEnabled(False)
            self.token2stoploss.setEnabled(False)
            self.token3stoploss.setEnabled(False)
            self.token4stoploss.setEnabled(False)
            self.token5stoploss.setEnabled(False)
            self.token6stoploss.setEnabled(False)
            self.token7stoploss.setEnabled(False)
            self.token8stoploss.setEnabled(False)
            self.token9stoploss.setEnabled(False)
            self.token10stoploss.setEnabled(False)

            self.stoplosstoken1.setDisabled(True)
            self.stoplosstoken2.setDisabled(True)
            self.stoplosstoken3.setDisabled(True)
            self.stoplosstoken4.setDisabled(True)
            self.stoplosstoken5.setDisabled(True)
            self.stoplosstoken6.setDisabled(True)
            self.stoplosstoken7.setDisabled(True)
            self.stoplosstoken8.setDisabled(True)
            self.stoplosstoken9.setDisabled(True)
            self.stoplosstoken10.setDisabled(True)
            self.mcotoseeassell.setDisabled(True)
            self.mcotoseeassell.setReadOnly(True)

        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            if configfile.debugmode == '1':
                print(str(e) + ' on line: ' + str(exception_traceback.tb_lineno))

        try:
            if self.activatetoken1.isChecked():
                activatetoken1 = 1
                with open("./configfile.py", "r", encoding="utf-8") as f:
                    poepie = f.read()
                    a = 'activatetoken1='
                    b = '\n'
                    regex = "(?<=%s).*?(?=%s)" % (a, b)
                    lol2 = re.sub(regex, '\'1\'', poepie)
                    f.close()

            else:
                activatetoken1 = 0
                with open("./configfile.py", "r", encoding="utf-8") as f:
                    poepie = f.read()
                    a = 'activatetoken1='
                    b = '\n'
                    regex = "(?<=%s).*?(?=%s)" % (a, b)
                    lol2 = re.sub(regex, '\'0\'', poepie)
                    f.close()
            if self.activatetoken2.isChecked():
                activatetoken2 = 1
                a = 'activatetoken2='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol3 = re.sub(regex, '\'1\'', lol2)
            else:
                activatetoken2 = 0
                a = 'activatetoken2='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol3 = re.sub(regex, '\'0\'', lol2)
            if self.activatetoken3.isChecked():
                activatetoken3 = 1
                a = 'activatetoken3='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol4 = re.sub(regex, '\'1\'', lol3)
            else:
                activatetoken3 = 0
                a = 'activatetoken3='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol4 = re.sub(regex, '\'0\'', lol3)
            if self.activatetoken4.isChecked():
                activatetoken4 = 1
                a = 'activatetoken4='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol5 = re.sub(regex, '\'1\'', lol4)
            else:
                activatetoken4 = 0
                a = 'activatetoken4='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol5 = re.sub(regex, '\'0\'', lol4)
            if self.activatetoken5.isChecked():
                activatetoken5 = 1
                a = 'activatetoken5='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol6 = re.sub(regex, '\'1\'', lol5)
            else:
                activatetoken5 = 0
                a = 'activatetoken5='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol6 = re.sub(regex, '\'0\'', lol5)
            if self.activatetoken6.isChecked():
                activatetoken6 = 1
                a = 'activatetoken6='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol7 = re.sub(regex, '\'1\'', lol6)
            else:
                activatetoken6 = 0
                a = 'activatetoken6='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol7 = re.sub(regex, '\'0\'', lol6)
            if self.activatetoken7.isChecked():
                activatetoken7 = 1
                a = 'activatetoken7='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol8 = re.sub(regex, '\'1\'', lol7)
            else:
                activatetoken7 = 0
                a = 'activatetoken7='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol8 = re.sub(regex, '\'0\'', lol7)
            if self.activatetoken8.isChecked():
                activatetoken8 = 1
                a = 'activatetoken8='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol9 = re.sub(regex, '\'1\'', lol8)
            else:
                activatetoken8 = 0
                a = 'activatetoken8='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol9 = re.sub(regex, '\'0\'', lol8)
            if self.activatetoken9.isChecked():
                activatetoken9 = 1
                a = 'activatetoken9='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol10 = re.sub(regex, '\'1\'', lol9)
            else:
                activatetoken9 = 0
                a = 'activatetoken9='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol10 = re.sub(regex, '\'0\'', lol9)
            if self.activatetoken10.isChecked():
                activatetoken10 = 1
                a = 'activatetoken10='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol11 = re.sub(regex, '\'1\'', lol10)
            else:
                activatetoken10 = 0
                a = 'activatetoken10='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol11 = re.sub(regex, '\'0\'', lol10)
            if self.tradewithETHtoken1.isChecked():
                tradewithETHtoken1 = 1
                a = 'tradewithETHtoken1='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol22 = re.sub(regex, '\'1\'', lol11)
            else:
                tradewithETHtoken1 = 0
                a = 'tradewithETHtoken1='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol22 = re.sub(regex, '\'0\'', lol11)
            if self.tradewithETHtoken2.isChecked():
                tradewithETHtoken2 = 1
                a = 'tradewithETHtoken2='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol23 = re.sub(regex, '\'1\'', lol22)
            else:
                tradewithETHtoken2 = 0
                a = 'tradewithETHtoken2='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol23 = re.sub(regex, '\'0\'', lol22)
            if self.tradewithETHtoken3.isChecked():
                tradewithETHtoken3 = 1
                a = 'tradewithETHtoken3='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol24 = re.sub(regex, '\'1\'', lol23)
            else:
                tradewithETHtoken3 = 0
                a = 'tradewithETHtoken3='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol24 = re.sub(regex, '\'0\'', lol23)
            if self.tradewithETHtoken4.isChecked():
                tradewithETHtoken4 = 1
                a = 'tradewithETHtoken4='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol25 = re.sub(regex, '\'1\'', lol24)
            else:
                tradewithETHtoken4 = 0
                a = 'tradewithETHtoken4='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol25 = re.sub(regex, '\'0\'', lol24)
            if self.tradewithETHtoken5.isChecked():
                tradewithETHtoken5 = 1
                a = 'tradewithETHtoken5='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol26 = re.sub(regex, '\'1\'', lol25)
            else:
                tradewithETHtoken5 = 0
                a = 'tradewithETHtoken5='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol26 = re.sub(regex, '\'0\'', lol25)
            if self.tradewithETHtoken6.isChecked():
                tradewithETHtoken6 = 1
                a = 'tradewithETHtoken6='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol27 = re.sub(regex, '\'1\'', lol26)
            else:
                tradewithETHtoken6 = 0
                a = 'tradewithETHtoken6='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol27 = re.sub(regex, '\'0\'', lol26)
            if self.tradewithETHtoken7.isChecked():
                tradewithETHtoken7 = 1
                a = 'tradewithETHtoken7='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol28 = re.sub(regex, '\'1\'', lol27)
            else:
                tradewithETHtoken7 = 0
                a = 'tradewithETHtoken7='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol28 = re.sub(regex, '\'0\'', lol27)
            if self.tradewithETHtoken8.isChecked():
                tradewithETHtoken8 = 1
                a = 'tradewithETHtoken8='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol29 = re.sub(regex, '\'1\'', lol28)
            else:
                tradewithETHtoken8 = 0
                a = 'tradewithETHtoken8='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol29 = re.sub(regex, '\'0\'', lol28)
            if self.tradewithETHtoken9.isChecked():
                tradewithETHtoken9 = 1
                a = 'tradewithETHtoken9='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol30 = re.sub(regex, '\'1\'', lol29)
            else:
                tradewithETHtoken9 = 0
                a = 'tradewithETHtoken9='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol30 = re.sub(regex, '\'0\'', lol29)
            if self.tradewithETHtoken10.isChecked():
                tradewithETHtoken10 = 1
                a = 'tradewithETHtoken10='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol31 = re.sub(regex, '\'1\'', lol30)
            else:
                tradewithETHtoken10 = 0
                a = 'tradewithETHtoken10='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol31 = re.sub(regex, '\'0\'', lol30)
            if self.tradewithERCtoken1.isChecked():
                tradewithERCtoken1 = 1
                a = 'tradewithERCtoken1='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol32 = re.sub(regex, '\'1\'', lol31)
            else:
                tradewithERCtoken1 = 0
                a = 'tradewithERCtoken1='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol32 = re.sub(regex, '\'0\'', lol31)
            if self.tradewithERCtoken2.isChecked():
                tradewithERCtoken2 = 1
                a = 'tradewithERCtoken2='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol33 = re.sub(regex, '\'1\'', lol32)
            else:
                tradewithERCtoken2 = 0
                a = 'tradewithERCtoken2='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol33 = re.sub(regex, '\'0\'', lol32)
            if self.tradewithERCtoken3.isChecked():
                tradewithERCtoken3 = 1
                a = 'tradewithERCtoken3='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol34 = re.sub(regex, '\'1\'', lol33)
            else:
                tradewithERCtoken3 = 0
                a = 'tradewithERCtoken3='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol34 = re.sub(regex, '\'0\'', lol33)
            if self.tradewithERCtoken4.isChecked():
                tradewithERCtoken4 = 1
                a = 'tradewithERCtoken4='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol35 = re.sub(regex, '\'1\'', lol34)
            else:
                tradewithERCtoken4 = 0
                a = 'tradewithERCtoken4='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol35 = re.sub(regex, '\'0\'', lol34)
            if self.tradewithERCtoken5.isChecked():
                tradewithERCtoken5 = 1
                a = 'tradewithERCtoken5='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol36 = re.sub(regex, '\'1\'', lol35)
            else:
                tradewithERCtoken5 = 0
                a = 'tradewithERCtoken5='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol36 = re.sub(regex, '\'0\'', lol35)
            if self.tradewithERCtoken6.isChecked():
                tradewithERCtoken6 = 1
                a = 'tradewithERCtoken6='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol37 = re.sub(regex, '\'1\'', lol36)
            else:
                tradewithERCtoken6 = 0
                a = 'tradewithERCtoken6='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol37 = re.sub(regex, '\'0\'', lol36)
            if self.tradewithERCtoken7.isChecked():
                tradewithERCtoken7 = 1
                a = 'tradewithERCtoken7='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol38 = re.sub(regex, '\'1\'', lol37)
            else:
                tradewithERCtoken7 = 0
                a = 'tradewithERCtoken7='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol38 = re.sub(regex, '\'0\'', lol37)
            if self.tradewithERCtoken8.isChecked():
                tradewithERCtoken8 = 1
                a = 'tradewithERCtoken8='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol39 = re.sub(regex, '\'1\'', lol38)
            else:
                tradewithERCtoken8 = 0
                a = 'tradewithERCtoken8='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol39 = re.sub(regex, '\'0\'', lol38)
            if self.tradewithERCtoken9.isChecked():
                tradewithERCtoken9 = 1
                a = 'tradewithERCtoken9='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol40 = re.sub(regex, '\'1\'', lol39)
            else:
                tradewithERCtoken9 = 0
                a = 'tradewithERCtoken9='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol40 = re.sub(regex, '\'0\'', lol39)
            if self.tradewithERCtoken10.isChecked():
                tradewithERCtoken10 = 1
                a = 'tradewithERCtoken10='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol41 = re.sub(regex, '\'1\'', lol40)
            else:
                tradewithERCtoken10 = 0
                a = 'tradewithERCtoken10='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol41 = re.sub(regex, '\'0\'', lol40)

            token1low = self.token1low.text()
            a = 'token1low='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol42 = re.sub(regex, '\'' + str(token1low) + '\'', lol41)
            token2low = self.token2low.text()
            a = 'token2low='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol43 = re.sub(regex, '\'' + str(token2low) + '\'', lol42)
            token3low = self.token3low.text()
            a = 'token3low='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol44 = re.sub(regex, '\'' + str(token3low) + '\'', lol43)
            token4low = self.token4low.text()
            a = 'token4low='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol45 = re.sub(regex, '\'' + str(token4low) + '\'', lol44)
            token5low = self.token5low.text()
            a = 'token5low='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol46 = re.sub(regex, '\'' + str(token5low) + '\'', lol45)
            token6low = self.token6low.text()
            a = 'token6low='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol47 = re.sub(regex, '\'' + str(token6low) + '\'', lol46)
            token7low = self.token7low.text()
            a = 'token7low='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol48 = re.sub(regex, '\'' + str(token7low) + '\'', lol47)
            token8low = self.token8low.text()
            a = 'token8low='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol49 = re.sub(regex, '\'' + str(token8low) + '\'', lol48)
            token9low = self.token9low.text()
            a = 'token9low='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol50 = re.sub(regex, '\'' + str(token9low) + '\'', lol49)
            token10low = self.token10low.text()
            a = 'token10low='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol51 = re.sub(regex, '\'' + str(token10low) + '\'', lol50)
            token1high = self.token1high.text()
            a = 'token1high='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol52 = re.sub(regex, '\'' + str(token1high) + '\'', lol51)
            token2high = self.token2high.text()
            a = 'token2high='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol53 = re.sub(regex, '\'' + str(token2high) + '\'', lol52)
            token3high = self.token3high.text()
            a = 'token3high='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol54 = re.sub(regex, '\'' + str(token3high) + '\'', lol53)
            token4high = self.token4high.text()
            a = 'token4high='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol55 = re.sub(regex, '\'' + str(token4high) + '\'', lol54)
            token5high = self.token5high.text()
            a = 'token5high='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol56 = re.sub(regex, '\'' + str(token5high) + '\'', lol55)
            token6high = self.token6high.text()
            a = 'token6high='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol57 = re.sub(regex, '\'' + str(token6high) + '\'', lol56)
            token7high = self.token7high.text()
            a = 'token7high='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol58 = re.sub(regex, '\'' + str(token7high) + '\'', lol57)
            token8high = self.token8high.text()
            a = 'token8high='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol59 = re.sub(regex, '\'' + str(token8high) + '\'', lol58)
            token9high = self.token9high.text()
            a = 'token9high='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol60 = re.sub(regex, '\'' + str(token9high) + '\'', lol59)
            token10high = self.token10high.text()
            a = 'token10high='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol61 = re.sub(regex, '\'' + str(token10high) + '\'', lol60)
            token1ethaddress = self.token1ethaddress.text()
            a = 'token1ethaddress='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol62 = re.sub(regex, '\'' + str(token1ethaddress) + '\'', lol61)
            token2ethaddress = self.token2ethaddress.text()
            a = 'token2ethaddress='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol63 = re.sub(regex, '\'' + str(token2ethaddress) + '\'', lol62)
            token3ethaddress = self.token3ethaddress.text()
            a = 'token3ethaddress='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol64 = re.sub(regex, '\'' + str(token3ethaddress) + '\'', lol63)
            token4ethaddress = self.token4ethaddress.text()
            a = 'token4ethaddress='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol65 = re.sub(regex, '\'' + str(token4ethaddress) + '\'', lol64)
            token5ethaddress = self.token5ethaddress.text()
            a = 'token5ethaddress='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol66 = re.sub(regex, '\'' + str(token5ethaddress) + '\'', lol65)
            token6ethaddress = self.token6ethaddress.text()
            a = 'token6ethaddress='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol67 = re.sub(regex, '\'' + str(token6ethaddress) + '\'', lol66)
            token7ethaddress = self.token7ethaddress.text()
            a = 'token7ethaddress='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol68 = re.sub(regex, '\'' + str(token7ethaddress) + '\'', lol67)
            token8ethaddress = self.token8ethaddress.text()
            a = 'token8ethaddress='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol69 = re.sub(regex, '\'' + str(token8ethaddress) + '\'', lol68)
            token9ethaddress = self.token9ethaddress.text()
            a = 'token9ethaddress='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol70 = re.sub(regex, '\'' + str(token9ethaddress) + '\'', lol69)
            token10ethaddress = self.token10ethaddress.text()
            a = 'token10ethaddress='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol71 = re.sub(regex, '\'' + str(token10ethaddress) + '\'', lol70)
            infuraurl = self.infuraurl.text()
            a = 'infuraurl='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol72 = re.sub(regex, '\'' + str(infuraurl) + '\'', lol71)
            tokentokennumerator = self.tokentokennumerator.text()
            a = 'tokentokennumerator='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol73 = re.sub(regex, '\'' + str(tokentokennumerator) + '\'', lol72)
            secondscheckingprice = self.secondscheckingprice.value()
            a = 'secondscheckingprice='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol74 = re.sub(regex, '\'' + str(secondscheckingprice) + '\'', lol73)
            secondswaitaftertrade = self.secondscheckingprice_2.value()
            a = 'secondswaitaftertrade='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol75 = re.sub(regex, '\'' + str(secondswaitaftertrade) + '\'', lol74)
            secondscheckingprice_2 = self.secondscheckingprice_2.value()
            a = 'secondscheckingprice_2='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol76 = re.sub(regex, '\'' + str(secondscheckingprice_2) + '\'', lol75)
            lol77 = re.sub('\'\'', '\'0\'', lol76)
            token1name = self.token1name.text()
            a = 'token1name='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol78 = re.sub(regex, '\'' + str(token1name) + '\'', lol77)
            token2name = self.token2name.text()
            a = 'token2name='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol79 = re.sub(regex, '\'' + str(token2name) + '\'', lol78)
            token3name = self.token3name.text()
            a = 'token3name='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol80 = re.sub(regex, '\'' + str(token3name) + '\'', lol79)
            token4name = self.token4name.text()
            a = 'token4name='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol81 = re.sub(regex, '\'' + str(token4name) + '\'', lol80)
            token5name = self.token5name.text()
            a = 'token5name='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol82 = re.sub(regex, '\'' + str(token5name) + '\'', lol81)
            token6name = self.token6name.text()
            a = 'token6name='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol83 = re.sub(regex, '\'' + str(token6name) + '\'', lol82)
            token7name = self.token7name.text()
            a = 'token7name='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol84 = re.sub(regex, '\'' + str(token7name) + '\'', lol83)
            token8name = self.token8name.text()
            a = 'token8name='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol85 = re.sub(regex, '\'' + str(token8name) + '\'', lol84)
            token9name = self.token9name.text()
            a = 'token9name='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol86 = re.sub(regex, '\'' + str(token9name) + '\'', lol85)
            token10name = self.token10name.text()
            a = 'token10name='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol87 = re.sub(regex, '\'' + str(token10name) + '\'', lol86)
            maxslippage = self.Maxslippage.text()
            a = 'max_slippage='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol88 = re.sub(regex, '\'' + str(maxslippage) + '\'', lol87)
            ethtokeep = self.lineEdit.text()
            a = 'ethtokeep='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol89 = re.sub(regex, '\'' + str(ethtokeep) + '\'', lol88)
            a = 'speed='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol90 = re.sub(regex, '\'' + 'schnell' + '\'', lol89)
            a = 'maincoinoption='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol91 = re.sub(regex, '\'' + str(maincoinoption) + '\'', lol90)
            lol92 = re.sub('\'\'', '\'0\'', lol91)

            if self.stoplosstoken1.isChecked():
                stoplosstoken1 = 1
                a = 'stoplosstoken1='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol93 = re.sub(regex, '\'1\'', lol92)
            else:
                stoplosstoken1 = 0
                a = 'stoplosstoken1='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol93 = re.sub(regex, '\'0\'', lol92)
            if self.stoplosstoken2.isChecked():
                stoplosstoken2 = 1
                a = 'stoplosstoken2='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol94 = re.sub(regex, '\'1\'', lol93)
            else:
                stoplosstoken2 = 0
                a = 'stoplosstoken2='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol94 = re.sub(regex, '\'0\'', lol93)
            if self.stoplosstoken3.isChecked():
                stoplosstoken3 = 1
                a = 'stoplosstoken3='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol95 = re.sub(regex, '\'1\'', lol94)
            else:
                stoplosstoken3 = 0
                a = 'stoplosstoken3='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol95 = re.sub(regex, '\'0\'', lol94)
            if self.stoplosstoken4.isChecked():
                stoplosstoken4 = 1
                a = 'stoplosstoken4='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol96 = re.sub(regex, '\'1\'', lol95)
            else:
                stoplosstoken4 = 0
                a = 'stoplosstoken4='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol96 = re.sub(regex, '\'0\'', lol95)
            if self.stoplosstoken5.isChecked():
                stoplosstoken5 = 1
                a = 'stoplosstoken5='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol97 = re.sub(regex, '\'1\'', lol96)
            else:
                stoplosstoken5 = 0
                a = 'stoplosstoken5='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol97 = re.sub(regex, '\'0\'', lol96)
            if self.stoplosstoken6.isChecked():
                stoplosstoken6 = 1
                a = 'stoplosstoken6='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol98 = re.sub(regex, '\'1\'', lol97)
            else:
                stoplosstoken6 = 0
                a = 'stoplosstoken6='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol98 = re.sub(regex, '\'0\'', lol97)
            if self.stoplosstoken7.isChecked():
                stoplosstoken7 = 1
                a = 'stoplosstoken7='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol99 = re.sub(regex, '\'1\'', lol98)
            else:
                stoplosstoken7 = 0
                a = 'stoplosstoken7='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol99 = re.sub(regex, '\'0\'', lol98)
            if self.stoplosstoken8.isChecked():
                stoplosstoken8 = 1
                a = 'stoplosstoken8='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol100 = re.sub(regex, '\'1\'', lol99)
            else:
                stoplosstoken8 = 0
                a = 'stoplosstoken8='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol100 = re.sub(regex, '\'0\'', lol99)
            if self.stoplosstoken9.isChecked():
                stoplosstoken9 = 1
                a = 'stoplosstoken9='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol101 = re.sub(regex, '\'1\'', lol100)
            else:
                stoplosstoken9 = 0
                a = 'stoplosstoken9='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol101 = re.sub(regex, '\'0\'', lol100)
            if self.stoplosstoken10.isChecked():
                stoplosstoken10 = 1
                a = 'stoplosstoken10='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol102 = re.sub(regex, '\'1\'', lol101)
            else:
                stoplosstoken10 = 0
                a = 'stoplosstoken10='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol102 = re.sub(regex, '\'0\'', lol101)

            token1stoploss = self.token1stoploss.text()
            a = 'token1stoploss='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol103 = re.sub(regex, '\'' + str(token1stoploss) + '\'', lol102)
            token2stoploss = self.token2stoploss.text()
            a = 'token2stoploss='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol104 = re.sub(regex, '\'' + str(token2stoploss) + '\'', lol103)
            token3stoploss = self.token3stoploss.text()
            a = 'token3stoploss='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol105 = re.sub(regex, '\'' + str(token3stoploss) + '\'', lol104)
            token4stoploss = self.token4stoploss.text()
            a = 'token4stoploss='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol106 = re.sub(regex, '\'' + str(token4stoploss) + '\'', lol105)
            token5stoploss = self.token5stoploss.text()
            a = 'token5stoploss='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol107 = re.sub(regex, '\'' + str(token5stoploss) + '\'', lol106)
            token6stoploss = self.token6stoploss.text()
            a = 'token6stoploss='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol108 = re.sub(regex, '\'' + str(token6stoploss) + '\'', lol107)
            token7stoploss = self.token7stoploss.text()
            a = 'token7stoploss='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol109 = re.sub(regex, '\'' + str(token7stoploss) + '\'', lol108)
            token8stoploss = self.token8stoploss.text()
            a = 'token8stoploss='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol110 = re.sub(regex, '\'' + str(token8stoploss) + '\'', lol109)
            token9stoploss = self.token9stoploss.text()
            a = 'token9stoploss='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol111 = re.sub(regex, '\'' + str(token9stoploss) + '\'', lol110)
            token10stoploss = self.token10stoploss.text()
            a = 'token10stoploss='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol112 = re.sub(regex, '\'' + str(token10stoploss) + '\'', lol111)

            if self.debugmode.isChecked():
                debugmode = 1
                a = 'debugmode='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol113 = re.sub(regex, '\'1\'', lol112)
            else:
                debugmode = 0
                a = 'debugmode='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol113 = re.sub(regex, '\'0\'', lol112)

            if 1 == 1:
                maxgwei = 1
                a = 'maxgwei='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol114 = re.sub(regex, '\'1\'', lol113)
            else:
                maxgwei = 0
                a = 'maxgwei='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol114 = re.sub(regex, '\'0\'', lol113)

            if self.diffdeposit.isChecked():
                diffdeposit = 1
                a = 'diffdeposit='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol115 = re.sub(regex, '\'1\'', lol114)
            else:
                diffdeposit = 0
                a = 'diffdeposit='
                b = '\n'
                regex = "(?<=%s).*?(?=%s)" % (a, b)
                lol115 = re.sub(regex, '\'0\'', lol114)
            maxgweinumber = self.maxgweinumber.text()
            a = 'maxgweinumber='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol116 = re.sub(regex, '\'' + str(maxgweinumber) + '\'', lol115)
            diffdepositaddress = self.diffdepositaddress.text()
            a = 'diffdepositaddress='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol117 = re.sub(regex, '\'' + str(diffdepositaddress) + '\'', lol116)
            mcotoseeassell = self.mcotoseeassell.text()
            a = 'mcotoseeassell='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol118 = re.sub(regex, '\'' + str(mcotoseeassell) + '\'', lol117)
            token1decimals = self.token1decimals.text()
            a = 'token1decimals='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol119 = re.sub(regex, '\'' + str(token1decimals) + '\'', lol118)
            token2decimals = self.token2decimals.text()
            a = 'token2decimals='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol120 = re.sub(regex, '\'' + str(token2decimals) + '\'', lol119)
            token3decimals = self.token3decimals.text()
            a = 'token3decimals='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol121 = re.sub(regex, '\'' + str(token3decimals) + '\'', lol120)
            token4decimals = self.token4decimals.text()
            a = 'token4decimals='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol122 = re.sub(regex, '\'' + str(token4decimals) + '\'', lol121)
            token5decimals = self.token5decimals.text()
            a = 'token5decimals='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol123 = re.sub(regex, '\'' + str(token5decimals) + '\'', lol122)
            token6decimals = self.token6decimals.text()
            a = 'token6decimals='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol124 = re.sub(regex, '\'' + str(token6decimals) + '\'', lol123)
            token7decimals = self.token7decimals.text()
            a = 'token7decimals='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol125 = re.sub(regex, '\'' + str(token7decimals) + '\'', lol124)
            token8decimals = self.token8decimals.text()
            a = 'token8decimals='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol126 = re.sub(regex, '\'' + str(token8decimals) + '\'', lol125)
            token9decimals = self.token9decimals.text()
            a = 'token9decimals='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol127 = re.sub(regex, '\'' + str(token9decimals) + '\'', lol126)
            token10decimals = self.token10decimals.text()
            a = 'token10decimals='
            b = '\n'
            regex = "(?<=%s).*?(?=%s)" % (a, b)
            lol128 = re.sub(regex, '\'' + str(token10decimals) + '\'', lol127)
            with open("./configfile.py", "w", encoding="utf-8") as f:
                f.write(lol128)
                f.close()
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            if configfile.debugmode == '1':
                print(str(e) + ' on line: ' + str(exception_traceback.tb_lineno))
        self.log.append('starting {} threads'.format(self.NUM_THREADS))
        self.startbutton.setDisabled(True)
        self.stopbutton.setEnabled(True)

        self.__workers_done = 0
        self.__threads = []
        for idx in range(self.NUM_THREADS):
            worker = Worker(idx)
            thread = QThread()
            thread.setObjectName('thread_' + str(idx))
            self.__threads.append((thread, worker))  # need to store worker too otherwise will be gc'd
            worker.moveToThread(thread)

            # get progress messages from worker:
            worker.sig_step.connect(self.on_worker_step)
            worker.sig_done.connect(self.on_worker_done)
            worker.sig_msg.connect(self.log.append)

            # control worker:
            self.sig_abort_workers.connect(worker.abort)

            # get read to start worker:
            # self.sig_start.connect(worker.work)  # needed due to PyCharm debugger bug (!); comment out next line

            thread.started.connect(worker.work)
            thread.start()  # this will emit 'started' and start thread's event loop
        # self.sig_start.emit()  # needed due to PyCharm debugger bug (!)

    @pyqtSlot(int, str)
    def on_worker_step(self, worker_id: int, data: str):
        self.log.append('Worker #{}: {}'.format(worker_id, data))
        self.progress.append('{}: {}'.format(worker_id, data))

    @pyqtSlot(int)
    def on_worker_done(self, worker_id):
        self.log.append('worker #{} done'.format(worker_id))
        self.progress.append('-- Worker {} DONE'.format(worker_id))
        self.__workers_done += 1
        if self.__workers_done == self.NUM_THREADS:
            self.log.append('No more workers active')
            self.startbutton.setEnabled(True)
            self.stopbutton.setDisabled(True)
            # self.__threads = None

    @pyqtSlot()
    def abort_workers(self):
        self.startbutton.setDisabled(True)
        self.stopbutton.setDisabled(True)
        self.sig_abort_workers.emit()
        self.log.append('Asking each worker to abort')
        for thread, worker in self.__threads:  # note nice unpacking by Python, avoids indexing
            thread.quit()  # this will quit **as soon as thread event loop unblocks**
            print('Stopping bot (takes 15 seconds)')
            thread.wait()  # <- so you need to wait for it to *actually* quit

        # even though threads have exited, there may still be messages on the main thread's
        # queue (messages that threads emitted before the abort):
        self.log.append('All threads exited')

        def lol2():
            self.startbutton.setEnabled(True)
            self.stopbutton.setDisabled(True)
            self.token1name.setReadOnly(False)
            self.token2name.setReadOnly(False)
            self.token3name.setReadOnly(False)
            self.token4name.setReadOnly(False)
            self.token5name.setReadOnly(False)
            self.token6name.setReadOnly(False)
            self.token7name.setReadOnly(False)
            self.token8name.setReadOnly(False)
            self.token9name.setReadOnly(False)
            self.token10name.setReadOnly(False)
            try:
                self.secondscheckingprice_2.setEnabled(True)
                self.secondscheckingprice.setEnabled(True)
                self.infuraurl.setEnabled(True)
                self.tokentokennumerator.setEnabled(True)
                self.activatetoken1.setEnabled(True)
                self.tradewithETHtoken1.setEnabled(True)
                self.tradewithERCtoken1.setEnabled(True)
                self.token1ethaddress.setReadOnly(False)
                self.token1low.setReadOnly(False)
                self.token1high.setReadOnly(False)
                self.token1ethaddress.setEnabled(True)
                self.token1low.setEnabled(True)
                self.token1high.setEnabled(True)

                self.maincoinoption.setEnabled(True)

                self.activatetoken2.setEnabled(True)
                self.tradewithETHtoken2.setEnabled(True)
                self.tradewithERCtoken2.setEnabled(True)
                self.token2ethaddress.setReadOnly(False)
                self.token2low.setReadOnly(False)
                self.token2high.setReadOnly(False)
                self.token2ethaddress.setEnabled(True)
                self.token2low.setEnabled(True)
                self.token2high.setEnabled(True)

                self.mcotoseeassell.setEnabled(True)
                self.mcotoseeassell.setReadOnly(False)

                self.activatetoken3.setEnabled(True)
                self.tradewithETHtoken3.setEnabled(True)
                self.tradewithERCtoken3.setEnabled(True)
                self.token3ethaddress.setReadOnly(False)
                self.token3low.setReadOnly(False)
                self.token3high.setReadOnly(False)
                self.token3ethaddress.setEnabled(True)
                self.token3low.setEnabled(True)
                self.token3high.setEnabled(True)

                # self.updatename.setEnabled(True)

                self.activatetoken4.setEnabled(True)
                self.tradewithETHtoken4.setEnabled(True)
                self.tradewithERCtoken4.setEnabled(True)
                self.token4ethaddress.setReadOnly(False)
                self.token4low.setReadOnly(False)
                self.token4high.setReadOnly(False)
                self.token4ethaddress.setEnabled(True)
                self.token4low.setEnabled(True)
                self.token4high.setEnabled(True)

                self.activatetoken5.setEnabled(True)
                self.tradewithETHtoken5.setEnabled(True)
                self.tradewithERCtoken5.setEnabled(True)
                self.token5ethaddress.setReadOnly(False)
                self.token5low.setReadOnly(False)
                self.token5high.setReadOnly(False)
                self.token5ethaddress.setEnabled(True)
                self.token5low.setEnabled(True)
                self.token5high.setEnabled(True)

                self.activatetoken6.setEnabled(True)
                self.tradewithETHtoken6.setEnabled(True)
                self.tradewithERCtoken6.setEnabled(True)
                self.token6ethaddress.setReadOnly(False)
                self.token6low.setReadOnly(False)
                self.token6high.setReadOnly(False)
                self.token6ethaddress.setEnabled(True)
                self.token6low.setEnabled(True)
                self.token6high.setEnabled(True)

                self.activatetoken7.setEnabled(True)
                self.tradewithETHtoken7.setEnabled(True)
                self.tradewithERCtoken7.setEnabled(True)
                self.token7ethaddress.setReadOnly(False)
                self.token7low.setReadOnly(False)
                self.token7high.setReadOnly(False)
                self.token7ethaddress.setEnabled(True)
                self.token7low.setEnabled(True)
                self.token7high.setEnabled(True)

                self.activatetoken8.setEnabled(True)
                self.tradewithETHtoken8.setEnabled(True)
                self.tradewithERCtoken8.setEnabled(True)
                self.token8ethaddress.setReadOnly(False)
                self.token8low.setReadOnly(False)
                self.token8high.setReadOnly(False)
                self.token8ethaddress.setEnabled(True)
                self.token8low.setEnabled(True)
                self.token8high.setEnabled(True)

                self.activatetoken9.setEnabled(True)
                self.tradewithETHtoken9.setEnabled(True)
                self.tradewithERCtoken9.setEnabled(True)
                self.token9ethaddress.setReadOnly(False)
                self.token9low.setReadOnly(False)
                self.token9high.setReadOnly(False)
                self.token9ethaddress.setEnabled(True)
                self.token9low.setEnabled(True)
                self.token9high.setEnabled(True)

                self.activatetoken10.setEnabled(True)
                self.tradewithETHtoken10.setEnabled(True)
                self.tradewithERCtoken10.setEnabled(True)
                self.token10ethaddress.setReadOnly(False)
                self.token10low.setReadOnly(False)
                self.token10high.setReadOnly(False)
                self.token10ethaddress.setEnabled(True)
                self.token10low.setEnabled(True)
                self.token10high.setEnabled(True)
                self.Maxslippage.setEnabled(True)
                self.lineEdit.setEnabled(True)

                self.token1decimals.setEnabled(True)
                self.token2decimals.setEnabled(True)
                self.token3decimals.setEnabled(True)
                self.token4decimals.setEnabled(True)
                self.token5decimals.setEnabled(True)
                self.token6decimals.setEnabled(True)
                self.token7decimals.setEnabled(True)
                self.token8decimals.setEnabled(True)
                self.token9decimals.setEnabled(True)
                self.token10decimals.setEnabled(True)

                self.token1stoploss.setEnabled(True)
                self.token2stoploss.setEnabled(True)
                self.token3stoploss.setEnabled(True)
                self.token4stoploss.setEnabled(True)
                self.token5stoploss.setEnabled(True)
                self.token6stoploss.setEnabled(True)
                self.token7stoploss.setEnabled(True)
                self.token8stoploss.setEnabled(True)
                self.token9stoploss.setEnabled(True)
                self.token10stoploss.setEnabled(True)

                self.stoplosstoken1.setEnabled(True)
                self.stoplosstoken2.setEnabled(True)
                self.stoplosstoken3.setEnabled(True)
                self.stoplosstoken4.setEnabled(True)
                self.stoplosstoken5.setEnabled(True)
                self.stoplosstoken6.setEnabled(True)
                self.stoplosstoken7.setEnabled(True)
                self.stoplosstoken8.setEnabled(True)
                self.stoplosstoken9.setEnabled(True)
                self.stoplosstoken10.setEnabled(True)
                self.debugmode.setEnabled(True)
                self.diffdeposit.setEnabled(True)
                self.maxgweinumber.setReadOnly(False)
                self.diffdepositaddress.setReadOnly(False)
                self.maxgweinumber.setEnabled(True)
                self.diffdepositaddress.setEnabled(True)
            except Exception as e:
                exception_type, exception_object, exception_traceback = sys.exc_info()
                if configfile.debugmode == '1':
                    print(str(e) + ' on line: ' + str(exception_traceback.tb_lineno))

        print('Bot stopped')
        lol2()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    lollol = ui.setupUi(MainWindow)
    lollol2 = MainWindow.show()
    try:
        sys.exit(app.exec_())
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        if configfile.debugmode == '1':
            print(str(e) + ' on line: ' + str(exception_traceback.tb_lineno))
    print(lollol2)
