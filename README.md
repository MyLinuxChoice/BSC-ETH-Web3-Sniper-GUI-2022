<h2 align="center">⭐️BSC-ETH-Web3-Sniper-GUI-2022 (WINDOWS LINUX MAC)⭐️</h2> 
        
<h4 align="center">⭐️ DO YOU TIRED OF BEAR MARKET ? USE BOTS FOR 24H TRADES ⭐️</h4>
  
<h4 align="center">⭐️ AUTO BUY TOKEN ON LAUNCH AFTER ADD LIQUIDITY ⭐️</h4>
  
![alt text](https://github.com/seeememagaiin/BSC-ETH-Web3-Sniper-GUI-2022/blob/main/bsc-gui.gif?raw=true "GIF application")
 
[![Version](https://img.shields.io/badge/Codename-BlackHat-blue.svg?maxAge=259200)]()
[![Stage](https://img.shields.io/badge/Release-Stable-brightgreen.svg)]()
[![Build](https://img.shields.io/badge/Supported_OS-MAC-red.svg)]() 
[![Available](https://img.shields.io/badge/Available-MAC-yellow.svg?maxAge=259200)]()
[![Documentation](https://img.shields.io/badge/TORNADO-CASH-red.svg?maxAge=259200)]()
[![Contributions Welcome](https://img.shields.io/badge/Type-FREE-green.svg?style=flat)]()
  
 
<h3 align="center">⭐️ First GUI SNIPER BOT for WINDOWS & LINUX ⭐️</h3>

#### Web3 Sniper GUI Take Profit/StopLose bot written in python3, For ANDROID WIN MAC & LINUX
#### Sniper bot that watches when taxes/anti buy are removed from a contract, then quick snipes, with honeypot detector, and also keybinding for fair launches
 
 
### Install
First of all, you need install Python3+
Debian/Ubuntu: $ sudo apt install python3 git make gcc
Windows: Need to install Visual Studio BuildTools & Python3
```
Install Requirements:  
```python3
python -m pip install -r requirements.txt
```  

<H2>HOW TO USE</H2>

1. An ethereum/bsc address.
2. Open "configfile.py" (with notepad) on line 3 and 4 add wallet address and phrase or private key.
3. Run python3 bsc-GUI.py

(Also you can use phrase key just use space between words)

<H2>How Find Private Key</H2>
https://metamask.zendesk.com/hc/en-us/articles/360015289632-How-to-Export-an-Account-Private-Key


<H2>Functions</H2>

<b>Main coin/token</b>: The token or coin you want to trade tokens for and with

<b>Token address</b>: Fill the token address of the token you want to trade (such as 0x0000000000000000000000000000000000000000)

<b>Notes</b>: A place to fill in notes, such as the name of the token
 
<b>Sell($)</b>: The price you want the trader to sell the token for (0.01 = 1 dollar cent)

<b>Buy($)</b>: The price you want the trader to buy the token for (0.01 = 1 dollar cent)

<b>Trade w/ main</b>: Toggle if you want to activate trading with your main-coin/token

<b>Trade w/ token (Experimental!)</b>: Toggle if you want to trade the token with other BEP20 tokens of which this option is activated (see tokentokennumerator)

<b>Stoploss</b>: Toggle to activate stoploss (0.01 = 1 dollar cent)

<b>Second(s) between checking price</b>: Standard is 4 seconds. With a infura server with max 100.000tx/day 4 seconds is good for 2 activated token 24hr/day

<b>Seconds waiting between trades</b>: depends on how fast transactions finalize

<b>Max slippage</b>: The maximum slippage you want to allow while trading (3 = 3%)
 
<b>$ to keep in ETH/BNB after trade</b>: The amount of ETH/BNB you want to keep after each trade (excluding transaction fees) in terms of $.

<b>GWEI</b>: The amount of gas you want to use for each trade (5 GWEI is fine for PCS). When trading on uniswap, This becomes the max GWEI you want to pay on the eth network, the GWEI will be determined from ethgasstation.com

<b>Different deposit address</b>: Use this if you want the swap output to go to a different address (without extra fees)

<b>Tokentokennumerator (Experimental!)</b>: This value lets you trade ERC tokens with each other. The code to create the value is as followed:
<pre>if pricetoken1usd > ((token1high + token1low) / 2) and pricetoken2usd < ((token2high + token2low) / 2):
  token1totoken2 = ((pricetoken1usd - token1low) / (token1high - token1low)) / ((pricetoken2usd - token2low) / (token2high - token2low))</pre>
  
If you dont want to wait till the token1 is sold for the maincoinoption, because you are uncertain whether token2 will still be at this price level or think that token1 will     drop, you can use this function. To use this function, "Trade with ERC" should be activated for at least 2 tokens, and the highs and lows should be set seriously.
    
  As an example, if the current price of token1 is $0.9 and its set "high"=$1 and "low"=$0, the value of this token is seen as "90%". Token2 also has a high of $1, but the         current price is 0.2$, value of this token is seen as 20%. The tokentokenmnumerator is set at 3.3. If we divide the 90% by the 20%, we get 4.5, which is higher than 3.3, which   means that token1 gets traded for token2 instantly. If the tokentokennumerator was set to 5, the swap would not happen.
  
<H3>WHAT IS UNIQUE TOKEN TRADERS</h3>
 
- AUTO BUY TOKEN ON LAUNCH AFTER ADD LIQUIDITY
- Support ANDROID ,Windows 10 ,Linux and Mac OS
- Add uniswap V3 & pancakeswap v2 
- Added multiple DEXs
- Force Buy and Force Sell buttons, when clicked it will buy or sell with your chosen settings (excluding limit price)
- set manual SLIPPAGE 
- set stop-less price
- Speed adjustable
- The program determines the name and decimals of the token automatically
