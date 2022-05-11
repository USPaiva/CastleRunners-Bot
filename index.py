from cv2 import cv2
from pyclick import HumanClicker
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import numpy as np
import mss
import pyautogui
import telegram
import os
import time
import sys
import yaml
import random
import requests

banner = """
#******************************* Castle Runners Bot ********************************************#
#───────────────────────────────────────────────────────────────────────────────────────────#
#*******************************************************************************************#
#*********************** Please consider buying me a coffee ********************************#
#*******************************************************************************************#
#******** BUSD (BEP20): 0x614247F846fbB18F9B25FebA48357e3336a9cDD0            **************#
#*******************************************************************************************#
---> Press CTRL+C to kill the bot or send /stop on Telegram.
---> Some configs can be found in the /config/config.yaml file.
---> futures updates can be found in the https://github.com/USPaiva/CastleRunners-Bot
============================================================================================
"""

print(banner)

P=[]

def readConfig():
    with open("./config/config.yaml", 'r', encoding='utf8') as s:
        stream = s.read()
    return yaml.safe_load(stream)


try:
    streamConfig = readConfig()
    configThreshold = streamConfig['threshold']
    configTimeIntervals = streamConfig['time_intervals']
    metamaskData = streamConfig['metamask']
    offsets = streamConfig['offsets']
    maubuntu = streamConfig['maubuntu']
    mawindows = streamConfig['mawindows']
except FileNotFoundError:
    print('Error: config.yaml file not found, rename EXAMPLE-config.yaml to config.yaml inside /config folder')
    print('Erro: Arquivo config.yaml não encontrado, renomear EXAMPLE-config.yaml para config.yaml dentro da pasta /config')
    exit()

try:
    config_version_local = streamConfig['version']
except KeyError:
    print('Error: Please update the config.yaml file.')
    print('Erro: Por favor atualize o arquivo config.yaml.')


config_version = '1.0.7' #Required config version

if config_version > config_version_local:
    print('Error: Please update the config.yaml file.')
    print('Erro: Por favor atualize o arquivo config.yaml.')

acc = configTimeIntervals['acc']
up = configTimeIntervals['up']


telegramIntegration = False
try:
    stream = open("./config/telegram.yaml", 'r', encoding='utf8')
    streamConfigTelegram = yaml.safe_load(stream)
    telegramIntegration = streamConfigTelegram['telegram_enable']
    telegramChatId = streamConfigTelegram['telegram_chat_id']
    telegramBotToken = streamConfigTelegram['telegram_bot_token']
    telegramCoinReport = streamConfigTelegram['enable_coin_report']
    telegramMapReport = streamConfigTelegram['enable_map_report']
    telegramFormatImage = streamConfigTelegram['format_of_images']
    telegramAllWorkReport = streamConfigTelegram['enable_allwork_report']
    telegramAllRestReport = streamConfigTelegram['enable_allrest_report']
    stream.close()
except FileNotFoundError:
    print('Info: Telegram not configure, rename EXAMPLE-telegram.yaml to telegram.yaml')

hc = HumanClicker()
pyautogui.PAUSE = streamConfig['time_intervals']['interval_between_movements']
pyautogui.FAILSAFE = False
general_check_time = 1
check_for_updates = 15

heroes_clicked = 0
heroes_clicked_total = 0
login_attempts = 0
next_refresh_heroes = configTimeIntervals['send_heroes_for_work'][0]


if mawindows is True: 
    import pygetwindow


go_work_img = cv2.imread('./images/targets/go-work.png')
arrow_img = cv2.imread('./images/targets/go-back-arrow.png')
hero_img = cv2.imread('./images/targets/hero-icon.png')
teasureHunt_icon_img = cv2.imread('./images/targets/treasure-hunt-icon.png')
x_button_img = cv2.imread('./images/targets/x.png')
connect_wallet_btn_img = cv2.imread('./images/targets/connect-wallet.png')
sign_btn_img = cv2.imread('./images/targets/metamask_sign.png')
new_map_btn_img = cv2.imread('./images/targets/new-map.png')
green_bar = cv2.imread('./images/targets/green-bar.png')
full_stamina = cv2.imread('./images/targets/full-stamina.png')
character_indicator = cv2.imread('./images/targets/character_indicator.png')
metamask_unlock_img = cv2.imread('./images/targets/unlock_metamask.png')
metamask_cancel_button = cv2.imread('./images/targets/metamask_cancel_button.png')
chest_button = cv2.imread('./images/targets/treasure_chest.png')
coin_icon = cv2.imread('./images/targets/coin.png')
top_coin = cv2.imread('./images/targets/top_coin.png')
####################################################################
allwork = cv2.imread('./images/targets/all_work.png')
allrest = cv2.imread('./images/targets/all_rest.png')
common = cv2.imread('./images/targets/common.png')
rest = cv2.imread('./images/targets/go-rest.png')
stop = cv2.imread('./images/targets/stop.png')
seta = cv2.imread('./images/targets/seta.png')
stamina = cv2.imread('./images/targets/stamina.png')
#########################################################
select_guia = cv2.imread('./images/targets/select_guia.png')
menu_de_guias = cv2.imread('./images/targets/menu_de_guias.png')
new_win = cv2.imread('./images/targets/new_win.png')


def dateFormatted(format = '%Y-%m-%d %H:%M:%S'):
  datetime = time.localtime()
  formatted = time.strftime(format, datetime)
  return formatted

def logger(message, telegram=False, emoji=None):
    formatted_datetime = dateFormatted()
    console_message = "{} - {}".format(formatted_datetime, message)
    service_message = "⏰{}\n{} {}".format(formatted_datetime, emoji, message)
    if emoji is not None and streamConfig['emoji'] is True:
        console_message = "{} - {} {}".format(
            formatted_datetime, emoji, message)

    print(console_message)

    if telegram == True:
        sendTelegramMessage(service_message)

    if (streamConfig['save_log_to_file'] == True):
        logger_file = open("./logs/logger.log", "a", encoding='utf-8')
        logger_file.write(console_message + '\n')
        logger_file.close()
    return True


# Initialize telegram
updater = None
if telegramIntegration == True:
    logger('Initializing Telegram...', emoji='📱')
    updater = Updater(telegramBotToken)

    try:
        TBot = telegram.Bot(token=telegramBotToken)

        def send_print(update: Update, context: CallbackContext) -> None:
            update.message.reply_text('🔃 Proccessing...')
            screenshot = printScreen()
            cv2.imwrite('./logs/print-report.%s' %
                        telegramFormatImage, screenshot)
            update.message.reply_photo(photo=open(
                './logs/print-report.%s' % telegramFormatImage, 'rb'))

        def send_id(update: Update, context: CallbackContext) -> None:
            update.message.reply_text(
                f'🆔 Your id is: {update.effective_user.id}')

        def send_map(update: Update, context: CallbackContext) -> None:
            update.message.reply_text('🔃 Proccessing...')
            if sendMapReport() is None:
                update.message.reply_text('😿 An error has occurred')

        def send_coin(update: Update, context: CallbackContext) -> None:
            update.message.reply_text('🔃 Proccessing...')
            if sendCoinReport() is None:
                update.message.reply_text('😿 An error has occurred')

        def send_wallet(update: Update, context: CallbackContext) -> None:
            update.message.reply_text ( 'BUSD/BCOIN (BEP20): \n 0x614247F846fbB18F9B25FebA48357e3336a9cDD0  \n\n Thank You! 😀')

        def send_stop(update: Update, context: CallbackContext) -> None:
            logger('Shutting down bot...', telegram=True, emoji='🛑')
            os._exit(0)
        #############################################################
        def send_refresh(update: Update, context: CallbackContext) -> None:
            update.message.reply_text('🔃 Proccessing...')
            if refreshNavigation() is None:
                update.message.reply_text('🔃 Refreshing page')
        
        def send_allwork(update: Update, context: CallbackContext) -> None:
            update.message.reply_text('🔃 Proccessing...')
            if sendallworkReport() is None:
                update.message.reply_text('Done✔️')
        
        def send_allrest(update: Update, context: CallbackContext) -> None:
            update.message.reply_text('🔃 Proccessing...')
            if sendallrestReport() is None:
                update.message.reply_text('Done✔️')
        
        commands = [
            ['print', send_print],
            ['id', send_id],
            ['map', send_map],
            ['coin', send_coin],
            ['donation', send_wallet],
            ['refresh', send_refresh],
            ['AllWork', send_allwork],
            ['AllRest', send_allrest],
            ['stop', send_stop]
        ]

        for command in commands:
            updater.dispatcher.add_handler(
                CommandHandler(command[0], command[1]))

        updater.start_polling()
        # updater.idle()
    except:
        logger('Bot not initialized, see configuration file', emoji='🤖')


def sendTelegramMessage(message):
    if telegramIntegration == False:
        return
    try:
        if(len(telegramChatId) > 0):
            for chat_id in telegramChatId:
                TBot.send_message(text=message, chat_id=chat_id)
    except:
        # logger('Error to send telegram message. See configuration file', emoji='📄')
        return

def sendTelegramPrint():
    if telegramIntegration == False:
        return
    try:
        if(len(telegramChatId) > 0):
            screenshot = printScreen()
            cv2.imwrite('./logs/print-report.%s' %
                        telegramFormatImage, screenshot)
            for chat_id in telegramChatId:
                TBot.send_photo(chat_id=chat_id, photo=open(
                    './logs/print-report.%s' % telegramFormatImage, 'rb'))
    except:
        logger('Error to send telegram message. See configuration file', emoji='📄')



def sendCoinReport():
    if telegramIntegration == False:
        return
    if(len(telegramChatId) <= 0 or telegramCoinReport is False):
        return

    if currentScreen() == "main":
            time.sleep(2)
    elif currentScreen() == "character":
        if clickButton(x_button_img):
            time.sleep(2)
    elif currentScreen() == "thunt":
        time.sleep(2)
    else:
        return

    clickButton(chest_button)

    sleep(5, 15)

    coin = positions(coin_icon, return_0=True)
    if len(coin) > 0:
        x, y, w, h = coin[0]

        with mss.mss() as sct:
            sct_img = np.array(
                sct.grab(sct.monitors[streamConfig['monitor_to_use']]))
            crop_img = sct_img[y:y+h, x:x+w]
            cv2.imwrite('./logs/bcoin-report.%s' %
                        telegramFormatImage, crop_img)
            time.sleep(1)
            try:
                for chat_id in telegramChatId:
                    # TBot.send_document(chat_id=chat_id, document=open('bcoin-report.png', 'rb'))
                    TBot.send_photo(chat_id=chat_id, photo=open(
                        './logs/bcoin-report.%s' % telegramFormatImage, 'rb'))
            except:
                logger('Telegram offline', emoji='😿')
    clickButton(x_button_img)
    logger('BCoin report sent', telegram=True, emoji='📄')
    return True


def sendMapReport():
    if telegramIntegration == False:
        return
    if(len(telegramChatId) <= 0 or telegramMapReport is False):
        return

    if currentScreen() == "main":
        if clickButton(teasureHunt_icon_img):
            time.sleep(2)
    elif currentScreen() == "character":
        if clickButton(x_button_img):
            time.sleep(2)
    elif currentScreen() == "thunt":
        time.sleep(2)
    else:
        return

    back = positions(top_coin, return_0=True)
    full_screen = positions(stop, return_0=True)
    if len(back) <= 0 or len(full_screen) <= 0:
        return
    x, y, _, _ = back[0]
    x1, y1, w, h = full_screen[0]
    newY0 = y
    newY1 = y1
    newX0 = x
    newX1 = x1 + w

    with mss.mss() as sct:
        sct_img = np.array(
            sct.grab(sct.monitors[streamConfig['monitor_to_use']]))
        crop_img = sct_img[newY0:newY1, newX0:newX1]
        # resized = cv2.resize(crop_img, (500, 250))

        cv2.imwrite('./logs/map-report.%s' % telegramFormatImage, crop_img)
        time.sleep(1)
        try:
            for chat_id in telegramChatId:
                # TBot.send_document(chat_id=chat_id, document=open('map-report.png', 'rb'))
                TBot.send_photo(chat_id=chat_id, photo=open(
                    './logs/map-report.%s' % telegramFormatImage, 'rb'))
        except:
            logger('Telegram offline', emoji='😿')

    clickButton(x_button_img)
    logger('Map report sent', telegram=True, emoji='📄')
    return True

        
def clickButton(img, name=None, timeout=3, threshold=configThreshold['default']):
    if not name is None:
        pass
    start = time.time()
    clicked = False
    while(not clicked):
        matches = positions(img, threshold=threshold)
        if(matches is False):
            hast_timed_out = time.time()-start > timeout
            if(hast_timed_out):
                if not name is None:
                    pass
                    # print('timed out')
                return False
            # print('button not found yet')
            continue

        x, y, w, h = matches[0]
        # pyautogui.moveTo(x+(w/2),y+(h/2),1)
        # pyautogui.moveTo(int(random.uniform(x, x+w)),int(random.uniform(y, y+h)),1)
        hc.move((int(random.uniform(x, x+w)), int(random.uniform(y, y+h))), 1)
        pyautogui.click()
        return True


def printScreen():
    with mss.mss() as sct:
        # The screen part to capture
        # Grab the data
        sct_img = np.array(
            sct.grab(sct.monitors[streamConfig['monitor_to_use']]))
        return sct_img[:, :, :3]


def positions(target, threshold=configThreshold['default'], base_img=None, return_0=False):
    if base_img is None:
        img = printScreen()
    else:
        img = base_img

    w = target.shape[1]
    h = target.shape[0]

    result = cv2.matchTemplate(img, target, cv2.TM_CCOEFF_NORMED)

    yloc, xloc = np.where(result >= threshold)

    rectangles = []
    for (x, y) in zip(xloc, yloc):
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])

    rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)
    if return_0 is False:
        if len(rectangles) > 0:
            # sys.stdout.write("\nGet_coords. " + str(rectangles) + " " + str(weights) + " " + str(w) + " " + str(h) + " ")
            return rectangles
        else:
            return False
    else:
        return rectangles

def show(rectangles=None, img=None):

    if img is None:
        with mss.mss() as sct:
            img = np.array(
                sct.grab(sct.monitors[streamConfig['monitor_to_use']]))

    if rectangles is not None:
        for (x, y, w, h) in rectangles:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255, 255), 2)

    # cv2.rectangle(img, (result[0], result[1]), (result[0] + result[2], result[1] + result[3]), (255,50,255), 2)
    cv2.imshow('img', img)
    cv2.waitKey(0)


def scroll():
    offset = offsets['character_indicator']
    offset_random = random.uniform(offset[0], offset[1])

    # width, height = pyautogui.size()
    # pyautogui.moveTo(width/2-200, height/2,1)
    character_indicator_pos = positions(character_indicator)
    if character_indicator_pos is False:
        return

    x, y, w, h = character_indicator_pos[0]
    hc.move((int(x+(w/2)), int(y+h+offset_random)), np.random.randint(1, 2))

    if not streamConfig['use_click_and_drag_instead_of_scroll']:
        pyautogui.click()
        pyautogui.scroll(-streamConfig['scroll_size'])
    else:
        # pyautogui.dragRel(0,-streamConfig['click_and_drag_amount'],duration=1, button='left')
        pyautogui.mouseDown(button='left')
        hc.move((int(x), int(
            y+(-streamConfig['click_and_drag_amount']))), np.random.randint(1, 2))
        pyautogui.mouseUp(button='left')


def clickButtons():
    buttons = positions(
        go_work_img, threshold=configThreshold['go_to_work_btn'])
    offset = offsets['work_button_all']

    if buttons is False:
        return

    if streamConfig['debug'] is not False:
        logger('%d buttons detected' % len(buttons), emoji='✔️')

    for (x, y, w, h) in buttons:
        offset_random = random.uniform(offset[0], offset[1])
        # pyautogui.moveTo(x+(w/2),y+(h/2),1)
        hc.move((int(x+offset_random), int(y+(h/2))), np.random.randint(1, 2))
        pyautogui.click()
        global heroes_clicked_total
        global heroes_clicked
        heroes_clicked_total = heroes_clicked_total + 1
        # cv2.rectangle(sct_img, (x, y) , (x + w, y + h), (0,255,255),2)
        if heroes_clicked > 15:
            logger('Too many hero clicks, try to increase the go_to_work_btn threshold',
                   telegram=True, emoji='⚠️')
            return
        sleep(1, 3)
    logger('Clicking in %d heroes detected.' %
           len(buttons), telegram=False, emoji='👆')
    return len(buttons)


def isWorking(bar, buttons):
    y = bar[1]

    for (_, button_y, _, button_h) in buttons:
        isBelow = y < (button_y + button_h)
        isAbove = y > (button_y - button_h)
        if isBelow and isAbove:
            return False
    return True


def clickGreenBarButtons():
    offset = offsets['work_button']
    green_bars = positions(green_bar, threshold=configThreshold['green_bar'])
    buttons = positions(
        go_work_img, threshold=configThreshold['go_to_work_btn'])

    if green_bars is False or buttons is False:
        return

    if streamConfig['debug'] is not False:
        logger('%d green bars detected' % len(green_bars), emoji='🟩')
        logger('%d buttons detected' % len(buttons), emoji='🔳')

    not_working_green_bars = []
    for bar in green_bars:
        if not isWorking(bar, buttons):
            not_working_green_bars.append(bar)
    if len(not_working_green_bars) > 0:
        logger('Clicking in %d heroes with green bar detected.' %
               len(not_working_green_bars), telegram=False, emoji='👆')

    # se tiver botao com y maior que bar y-10 e menor que y+10
    for (x, y, w, h) in not_working_green_bars:
        offset_random = random.uniform(offset[0], offset[1])
        # isWorking(y, buttons)
        # pyautogui.moveTo(x+offset+(w/2),y+(h/2),1)
        hc.move((int(x+offset_random+(w/2)), int(y+(h/2))),
                np.random.randint(1, 2))
        pyautogui.click()
        global heroes_clicked_total
        global heroes_clicked
        heroes_clicked_total = heroes_clicked_total + 1
        if heroes_clicked > 15:
            logger('Too many hero clicks, try to increase the go_to_work_btn threshold',
                   telegram=True, emoji='⚠️')
            return
        # cv2.rectangle(sct_img, (x, y) , (x + w, y + h), (0,255,255),2)
        sleep(1, 3)
    return len(not_working_green_bars)


def clickFullBarButtons():
    offset = offsets['work_button_full']
    full_bars = positions(full_stamina, threshold=configThreshold['full_bar'])
    buttons = positions(
        go_work_img, threshold=configThreshold['go_to_work_btn'])

    if full_bars is False or buttons is False:
        return

    if streamConfig['debug'] is not False:
        logger('%d FULL bars detected' % len(full_bars), emoji='🟩')
        logger('%d buttons detected' % len(buttons), emoji='🔳')

    not_working_full_bars = []
    for bar in full_bars:
        if not isWorking(bar, buttons):
            not_working_full_bars.append(bar)

    if len(not_working_full_bars) > 0:
        logger('Clicking in %d heroes with FULL bar detected.' %
               len(not_working_full_bars), telegram=True, emoji='👆')

    for (x, y, w, h) in not_working_full_bars:
        offset_random = random.uniform(offset[0], offset[1])
        # pyautogui.moveTo(x+offset+(w/2),y+(h/2),1)
        hc.move((int(x+offset_random+(w/2)), int(y+(h/2))),
                np.random.randint(1, 2))
        pyautogui.click()
        global heroes_clicked_total
        global heroes_clicked
        heroes_clicked_total = heroes_clicked_total + 1
        if heroes_clicked > 15:
            logger('Too many hero clicks, try to increase the go_to_work_btn threshold',
                   telegram=True, emoji='⚠️')
            return
        sleep(1, 3)
    return len(not_working_full_bars)


def currentScreen():
    if positions(stop) is not False:
        # sys.stdout.write("\nThunt. ")
        return "thunt"
    elif positions(teasureHunt_icon_img) is not False:
        # sys.stdout.write("\nmain. ")
        return "main"
    elif positions(connect_wallet_btn_img) is not False:
        # sys.stdout.write("\nlogin. ")
        return "login"
    elif positions(character_indicator) is not False:
        # sys.stdout.write("\ncharacter. ")
        return "character"
    elif positions(new_map_btn_img) is not False:
        # sys.stdout.write("\ncharacter. ")
        return "new_map"
    else:
        # sys.stdout.write("\nUnknown. ")
        return "unknown"


def goToHeroes():
    if currentScreen() == "thunt":
            if clickButton(hero_img):
                sleep(1, 3)
                waitForImage(allwork)
    if currentScreen() == "unknown" or currentScreen() == "login":
        checkLogout()

def goToTreasureHunt():
    if currentScreen() == "main":
        clickButton(teasureHunt_icon_img)
    if currentScreen() == "character":
        clickButton(x_button_img)
    if currentScreen() == "unknown" or currentScreen() == "login":
        checkLogout()




def login():
    global login_attempts

    randomMouseMovement()

    if clickButton(connect_wallet_btn_img):
        logger('Connect wallet button detected, logging in!', emoji='🎉')
        time.sleep(2)
        waitForImage((sign_btn_img, metamask_unlock_img), multiple=True)

    metamask_unlock_coord = positions(metamask_unlock_img)
    if metamask_unlock_coord is not False:
        if(metamaskData["enable_login_metamask"] is False):
            logger(
                'Metamask locked! But login with password is disabled, exiting', emoji='🔒')
            exit()
        logger('Found unlock button. Waiting for password', emoji='🔓')
        password = metamaskData["password"]
        pyautogui.typewrite(password, interval=0.1)
        sleep(1, 3)
        if clickButton(metamask_unlock_img):
            logger('Unlock button clicked', emoji='🔓')

    if clickButton(sign_btn_img):
        logger('Found sign button. Waiting to check if logged in', emoji='✔️')
        if clickButton(sign_btn_img):  # twice because metamask glitch
            logger(
                'Found glitched sign button. Waiting to check if logged in', emoji='✔️')
        # time.sleep(25)
        waitForImage(teasureHunt_icon_img, timeout=30)
        #handleError()

    if currentScreen() == "main":
        logger('Logged in', telegram=True, emoji='🎉')
        return True
    else:
        logger('Login failed, trying again', emoji='😿')
        login_attempts += 1

        if (login_attempts > 3):
            sendTelegramPrint()
            logger('+3 login attempts, retrying', telegram=True, emoji='🔃')
            # pyautogui.hotkey('ctrl', 'f5')
            pyautogui.hotkey('ctrl', 'shift', 'r')
            login_attempts = 0

            if clickButton(metamask_cancel_button):
                logger('Metamask is glitched, fixing', emoji='🙀')

            waitForImage(connect_wallet_btn_img)

        login()


def getMoreHeroes():
    global next_refresh_heroes
    global heroes_clicked

    logger('Search for heroes to work', emoji='🏢')

    goToHeroes()
    clickButton(seta)
    clickButton(stamina)
    clickButton(allwork)
    logger('All working report sent', telegram=True, emoji='🦸')
    clickButton(x_button_img)

def checkLogout():
    if currentScreen() == "unknown" or currentScreen() == "login":
        if positions(connect_wallet_btn_img) is not False:
            sendTelegramPrint()
            logger('Logout detected', telegram=True, emoji='😿')
            logger('Refreshing page', telegram=True, emoji='🔃')
            # pyautogui.hotkey('ctrl', 'f5')
            pyautogui.hotkey('ctrl', 'shift', 'r')
            waitForImage(connect_wallet_btn_img)
            login()
        elif positions(sign_btn_img):
            logger('Sing button detected', telegram=True, emoji='✔️')
            if clickButton(metamask_cancel_button):
                logger('Metamask is glitched, fixing',
                       telegram=True, emoji='🙀')
        else:
            return False

    else:
        return False


def waitForImage(imgs, timeout=30, threshold=0.5, multiple=False):
    start = time.time()
    while True:
        if multiple is not False:
            for img in imgs:
                matches = positions(img, threshold=threshold)
                if matches is False:
                    hast_timed_out = time.time()-start > timeout
                    if hast_timed_out is not False:
                        return False
                    continue
                return True
        else:
            matches = positions(imgs, threshold=threshold)
            if matches is False:
                hast_timed_out = time.time()-start > timeout
                if hast_timed_out is not False:
                    return False
                continue
            return True


def sleep(min, max):
    sleep = random.uniform(min, max)
    randomMouseMovement()
    return time.sleep(sleep)


def randomMouseMovement():
    x, y = pyautogui.size()
    x = np.random.randint(0, x)
    y = np.random.randint(0, y)
    hc.move((int(x), int(y)), np.random.randint(1, 3))


def checkUpdates():
    data = requests.get(
        'https://raw.githubusercontent.com/carecabrilhante/CastleRunners-Bot/main/config/version.yaml')
    try:
        streamVersionGithub = yaml.safe_load(data.text)
        version = streamVersionGithub['version']
        emergency = streamVersionGithub['emergency']
    except KeyError:
        logger('Version not found in github, securety problem', emoji='💥')
        version = "0"

    print('Git Version: ' + version)

    try:
        streamVersionLocal = open("./config/version.yaml", 'r')
        streamVersion = yaml.safe_load(streamVersionLocal)
        versionLocal = streamVersion['version']
        streamVersionLocal.close()
    except FileNotFoundError:
        versionLocal = None

   # if (emergency == 'true' and version > versionLocal):


    if versionLocal is not None:
        print('Version installed: ' + versionLocal)
        if version > versionLocal:
            logger('New version ' + version +
                   ' available, please update', telegram=True, emoji='🎉'),
    else:
        logger('Version not found, update is required',
               telegram=True, emoji='💥')


def checkThreshold():
    global configThreshold
    newStream = readConfig()
    newConfigThreshold = newStream['threshold']

    if newConfigThreshold != configThreshold:
        configThreshold = newConfigThreshold
        logger('New Threshold applied', telegram=False, emoji='⚙️')

##################################################################
def sendallworkReport():
    if telegramIntegration == False:
        return
    if(len(telegramChatId) <= 0 or telegramAllWorkReport is False):
        return
    if currentScreen() == "main":
            clickButton(teasureHunt_icon_img)
            time.sleep(2)
    elif currentScreen() == "character":
        if clickButton(x_button_img):
            time.sleep(2)
    elif currentScreen() == "thunt":
            time.sleep(2)
    else:
        return
    
    clickButton(hero_img)    
    waitForImage(allwork)
    clickButton(allwork)
    clickButton(x_button_img)
    logger('All working report sent', telegram=True, emoji='📄')

def sendallrestReport():
    if telegramIntegration == False:
        return
    if(len(telegramChatId) <= 0 or telegramAllRestReport is False):
        return
    if currentScreen() == "main":
            time.sleep(2)
    elif currentScreen() == "character":
        if clickButton(x_button_img):
            time.sleep(2)
    elif currentScreen() == "thunt":
        if clickButton(arrow_img):
            time.sleep(2)
    else:
        return
    
    clickButton(hero_img)    
    waitForImage(rest)
    clickButton(allrest)
    clickButton(x_button_img)
    clickButton(teasureHunt_icon_img)
    logger('All resting report sent', telegram=True, emoji='📄')

def refreshNavigation():
    logger('Refresh navigation', emoji='🤖')
    pyautogui.hotkey('ctrl', 'shift', 'r')    

def isresting(bar, buttons):
    y = bar[1]

    for (_, button_y, _, button_h) in buttons:
        isBelow = y < (button_y + button_h)
        isAbove = y > (button_y - button_h)
        if isBelow and isAbove:
            return False
    return True

def clickrestButtons():
    
    with mss.mss() as sct:
            sct_img = np.array(
                sct.grab(sct.monitors[streamConfig['monitor_to_use']]))
    offset = [1,10]
    commons = positions(common, threshold=0.65)
    buttons = positions(rest, threshold=1) #configThreshold['go_to_work_btn']
    
    if streamConfig['debug'] is not False:
        logger('%d commons detected' % len(commons), emoji='🟩')
        logger('%d buttons detected' % len(buttons), emoji='🔳')
        
    if commons is False or buttons is False:
        return

    not_working_commons = []
    for bar in commons:
        if not isresting(bar, buttons):
            not_working_commons.append(bar)
    if len(not_working_commons) > 0:
        logger('Clicking in %d heroes commons detected for rest.' %
               len(not_working_commons), telegram=False, emoji='👆')
        
    # se tiver botao com y maior que bar y-10 e menor que y+10
    ##########################################################
    for (x, y, w, h) in buttons:
        offset_random = random.uniform(offset[0], offset[1])
        # isWorking(y, buttons)
        # pyautogui.moveTo(x+offset+(w/2),y+(h/2),1)
        hc.move((int(x+offset_random+(w/2)), int(y+(h/2))),np.random.randint(1, 2))
        pyautogui.click()
        cv2.rectangle(sct_img, (x, y) , (x + w, y + h), (0,255,255),2)
        sleep(1, 3)
    return len(not_working_commons)

def clickwin(img, name=None, timeout=3, threshold=configThreshold['default']):
    if not name is None:
        pass
    start = time.time()
    clicked = False
    while(not clicked):
        matches = positions(img, threshold=threshold)
        if(matches is False):
            hast_timed_out = time.time()-start > timeout
            if(hast_timed_out):
                if not name is None:
                    pass
                    # print('timed out')
                return False
            # print('button not found yet')
            continue
        #print(matches)
        x, y, w, h = matches[0]
        pyautogui.moveTo(x+(w/2),y+(h/2)-up,1)
        # pyautogui.moveTo(int(random.uniform(x, x+w)),int(random.uniform(y, y+h)),1)
        #hc.move((int(random.uniform(x, x+w)), int(random.uniform(y, y+h))), 1)
        pyautogui.click()
        return True

def changewin():
    l=0
    while l < 1:
        clickButton(select_guia)
        time.sleep(5)
        clickwin(new_win)
        time.sleep(5)
        clickButton(select_guia)
        time.sleep(5)
        if positions(menu_de_guias) is not True:
            time.sleep(5)
            l=1

#############################################

def process(): 
    
    n = acc+1
    windows = []
    
    if mawindows is False and maubuntu is False:
        windows.append({
                "window": 1,
                "login" : 0,
                "heroes" : 0,
                "new_map" : 0,
                })
    
    if mawindows is True:
        for w in pygetwindow.getWindowsWithTitle('bombcrypto'):
            windows.append({
            "window": w,
            "login" : 0,
            "heroes" : 0,
            "new_map" : 0,
            })
    
    if maubuntu is True:
        for w in range(1, n) :
            windows.append({
                "window": w,
                "login" : 0,
                "heroes" : 0,
                "new_map" : 0,
                })       
    while True:
        if currentScreen() == "login":
            login()

        #handleError()

        now = time.time()
        
        
        for last in windows:
            
            #print(windows)
            #print(last["window"])
            
            if mawindows is True:
                last["window"].activate()
                time.sleep(2)
            
            
            if maubuntu is True:
                last["window"]
                changewin()
                sleep(1, 2)

            if currentScreen() == "main":
                if clickButton(teasureHunt_icon_img):
                    logger('Entering treasure hunt', emoji='▶️')

            if now - last["heroes"] > next_refresh_heroes * 60:
                last["heroes"] = now
                getMoreHeroes()
                
            if currentScreen() == "new_map":
                if clickButton(new_map_btn_img):
                    last["new_map"] = now
                    #clickNewMap()

            if currentScreen() == "character":
                clickButton(x_button_img)
                sleep(1, 3)

            checkLogout()
            #sys.stdout.flush()
            time.sleep(general_check_time)
            checkThreshold()

#########################################################################################
def main():
    checkUpdates()
    input('Press Enter to start the bot...\n')
    logger('Starting bot...', telegram=True, emoji='🤖')
    logger('Commands: \n\n /print \n /map \n /coin \n /id \n /donation \n /AllWork \n /AllRest \n /refresh \n /stop - Stop bot', telegram=True, emoji='ℹ️')
    logger('Multi Account BETA is available. enable in config.yaml and Run: python index.py for tests.', telegram=True, emoji='💡')
    process()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger('Shutting down the bot', telegram=True, emoji='😓')
        if(updater):
            updater.stop()
        exit()
