#!/usr/bin/python3.6
# coding=UTF-8


import argparse
import datetime
import logging
import os
import signal
import sys


from enum import Enum
from inspect import getframeinfo, stack
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep


class Logger(logging.Logger):

    def __init__(self, name, level = logging.NOTSET):
        return super(Logger, self).__init__(name, level)

    def error(self, msg, *args, **kwargs):
        logging.error(msg, *args, **kwargs)
        sys.exit(1)

    def exception(self, msg, *args, **kwargs):
        logging.exception(msg, *args, **kwargs)
        sys.exit(2)


# handling a signal capture routine
def signal_handler(signal, frame):
    sys.stdout.write("\n\nInterrupt from keyboard.\n")
    sys.exit(0)


# check if string is date
def is_date(string):
    try:
        datetime.datetime.strptime(string, '%d.%m.%Y')
    except ValueError:
        logger.error('Wrong date option!')


# check if string is time
def is_time(string):
    try:
        datetime.datetime.strptime(string, '%H:%M')
    except ValueError:
        logger.error('Wrong time option!')


# user credential loader from file
def load_user_credentials(filename):
    import imp
    f = open(filename)
    credentials = imp.load_source('person', '', f)
    f.close()
    return credentials


# core function providing the ticket buying
def buy_ticket():


    # Firefox options configuration
    options = Options();
    options.headless = args.headless
    logger.info('FirefoxOptions: headless = "{}"'.format(args.headless))


    # Firefox profile configuration
    profile = FirefoxProfile()

    value = 2
    profile.set_preference('browser.download.folderList', value)
    logger.info('FirefoxProfile: browser.download.folderList = "{}"'.format(value))

    value = False
    profile.set_preference('browser.download.manager.showWhenStarting', value)
    logger.info('FirefoxProfile: browser.download.manager.showWhenStarting = {}'.format(value))

    value = 'application/octet-stream,application/vnd.ms-excel'
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', value)
    logger.info('FirefoxProfile: browser.helperApps.neverAsk.saveToDisk = "{}"'.format(value))

    value = str(os.path.dirname(os.path.realpath(__file__)))
    profile.set_preference('browser.download.dir', value);
    logger.info('FirefoxProfile: browser.download.dir = "{}"'.format(value))


    # Firefox web browser launch
    driver = webdriver.Firefox(options=options, firefox_profile=profile)

    # Use full screen mode if enabled.
    logger.info('FirefoxWebdriver: fullscreen = "{}"'.format(args.fullscreen))
    if args.fullscreen:
        driver.maximize_window()

    # Firefox version
    logger.info('Firefox: version = "{}"'.format(driver.capabilities['browserVersion']))

    # Sets a sticky timeout to implicitly wait for an element to be found, or a command to complete.
    driver.implicitly_wait(30)

    # Load page 'Vyhľadanie spojenia'
    driver.get('https://ikvc.slovakrail.sk/esales/search')

    # Info
    logger.info('Loading page "Vyhľadanie spojenia"')

    try:
        delay = 30  # wait seconds for web page to load, added more second

        WebDriverWait(driver, delay).until(
            EC.presence_of_all_elements_located(
                (By.ID, 'searchPanel')
            )
        )

        # Logging information
        logger.info('Loaded page "Vyhľadanie spojenia"')

    except TimeoutException:
        logger.info('Loading took too much time.')
        logger.info('Closed {} (version {}).'.format(
               driver.capabilities['browserName'],
               driver.capabilities['browserVersion']
           )
        )
        driver.close()
        logger.error('Page loading failure.')

    sleep(1)

    # Info
    logger.info('Page title is "{}".'.format(driver.title))

    # Check if 'ZSSK' is in the page title
    assert 'ZSSK' in driver.title

    # FROM
    elem_city_from = driver.find_element_by_id('fromInput')
    elem_city_from.clear()
    elem_city_from.send_keys(args.departure)
    driver.find_element_by_xpath(
        '/html/body/div[1]/div/div[2]/div[3]/div/div/form/div[1]/div/div[1]/div[1]/div[1]/ul/li/a'
    ).click
    logger.info('Filling "Odkiaľ" in "Vyhľadanie spojenia" with "{}".'.format(args.departure))
    sleep(0.5)

    # TO
    elem_city_to = driver.find_element_by_id('toInput')
    elem_city_to.clear()
    elem_city_to.send_keys(args.arrival)
    driver.find_element_by_xpath(
        '/html/body/div[1]/div/div[2]/div[3]/div/div/form/div[1]/div/div[1]/div[1]/div[3]/ul/li/a'
    ).click
    logger.info('Filling "Kam" in "Vyhľadanie spojenia" with "{}".'.format(args.arrival))
    sleep(0.5)

    # DATE
    elem_date = driver.find_element_by_id('departDate')
    elem_date.clear()
    elem_date.send_keys(args.date)
    driver.find_element_by_xpath('//html').click();
    logger.info('Filling "Dátum cesty tam" in "Vyhľadanie spojenia" with "{}".'.format(args.date))
    sleep(0.5)

    # TIME
    elem_time = driver.find_element_by_id('departTime')
    elem_time.clear()
    elem_time.send_keys(args.time)
    driver.find_element_by_xpath('//html').click();
    logger.info('Filling "Odchod" in "Vyhľadanie spojenia" with "{}".'.format(args.time))
    sleep(0.5)

    logger.info('Filled train credentials in "Vyhľadanie spojenia".')

    # CONFIRM
    driver.find_element_by_id('actionSearchConnectionButton').click()
    logger.info('Clicked on "Vyhľadať spojenie".')
    sleep(2)

    # CLICK ON FIRST
    driver.find_element_by_xpath(
        '/html/body/div[1]/div/div[2]/div[3]/div/span/div/form/div/div[2]/div/div[2]/div/div/div/div[1]/div[1]'
    ).click()
    logger.info('Clicked on first train.')
    sleep(1)

    # BUY TICKET
    driver.find_element_by_xpath(
        '//*[@id="dayGroupLoop:0:eSalesConnectionLoop:0:j_idt323"]'
    ).click()
    logger.info('Clicked on "Kúpiť lístok".')
    sleep(1)

    # PASSENGER TYPE SELECTION
    driver.find_element_by_xpath(
        '/html/body/div[1]/div/div[2]/div[3]/span/div/div[1]/form/div/div/div/div/div/div/div[1]/div[1]/div/div/div/div/a[1]/span[2]'
    ).click()
    logger.info('Choosing passenger type.')
    sleep(1)

    # JUNIOR SELECTION
    driver.find_element_by_xpath(
        '/html/body/div[1]/div/div[2]/div[3]/span/div/div[1]/form/div/div/div/div/div/div/div[1]/div[1]/div/div/div[1]/div/a[1]/ul/li[3]'
    ).click()
    logger.info('Selected "Mladý (16 - 25 r.)".')
    sleep(1)

    # DISCOUNT SELECTION
    driver.find_element_by_xpath(
        '/html/body/div[1]/div/div[2]/div[3]/span/div/div[1]/form/div/div/div/div/div/div/div[1]/div[1]/div/div/div/div/a[2]/span[2]'
    ).click()
    logger.info('Choosing card type.')
    sleep(1)

    # CARD SELECTION
    driver.find_element_by_xpath(
        '/html/body/div[1]/div/div[2]/div[3]/span/div/div[1]/form/div/div/div/div/div/div/div[1]/div[1]/div/div/div[1]/div/a[2]/ul/li[4]'
    ).click()
    logger.info('Selected "Preukaz pre žiaka/Študenta".')
    sleep(1)

    # ENABLED OPTION FOR FREE TICKET
    driver.find_element_by_xpath(
        '/html/body/div[1]/div/div[2]/div[3]/span/div/div[1]/form/div/div/div/div/div/div/div[1]/div[1]/div/div/div[2]/div/div/label'
    ).click()
    logger.info('Checkbox enabled for "Nárok na bezplatnú prepravu".')
    sleep(1)

    # CONTINUE
    driver.find_element_by_xpath(
        '//*[@id="actionIndividualContinue"]'
    ).click()
    logger.info('Clicked on "Pokračovať" at "Voľba cestujúcich".')
    sleep(7.5)

    # CONTINUE
    driver.find_element_by_xpath(
        '//*[@id="ticketsForm:connection-offer:final-price:j_idt219"]'
    ).click()
    logger.info('Clicked on "Pokračovať" at "Voľba cestovného lístka".')
    sleep(7.5)

    # CONTINUE
    driver.find_element_by_xpath(
        '//*[@id="ticketsForm:j_idt118"]'
    ).click()
    logger.info('Clicked on "Pokračovať" at "Doplnkové služby".')
    sleep(10)

    # CONTINUE
    driver.find_element_by_xpath(
        '//*[@id="cartForm:j_idt305"]'
    ).click()
    logger.info('Clicked on "Pokračovať" at "Obsah košíka (1)".')
    sleep(1)

    # LOAD PERSONAL INFORMATION
    person = load_user_credentials('person.txt')

    # FILL EMAIL
    email = driver.find_element_by_id('email')
    email.clear()
    email.send_keys(person.email)
    logger.info('Filling "Váš e-mail" at "Osobné údaje (2)".')

    # FILL NAME
    name = driver.find_element_by_id('cartItemLoop:0:connectionPersonal:passengerLoop:0:firstname')
    name.clear()
    name.send_keys(person.name)
    logger.info('Filling "Meno" at "Osobné údaje (2)".')

    # FILL SURNAME
    surname = driver.find_element_by_id('cartItemLoop:0:connectionPersonal:passengerLoop:0:lastname')
    surname.clear()
    surname.send_keys(person.surname)
    logger.info('Filling "Priezvisko" at "Osobné údaje (2)".')

    # FILL REGISTRATION NUMBER
    card_number = driver.find_element_by_id('cartItemLoop:0:connectionPersonal:passengerLoop:0:cislo-registracie-p1')
    card_number.clear()
    card_number.send_keys(person.train_card)
    logger.info('Filling "Číslo registrácie:" at "Osobné údaje (2)".')

    logger.info('All personal informations filled at "Osobné údaje (2)".')

    # CONTINUE
    driver.find_element_by_xpath(
        '//*[@id="j_idt198"]'
    ).click()
    logger.info('Clicked on "Pokračovať" at "Osobné údaje (2)".')
    sleep(1)

    # I AGREE WITH THE TERMS AND CONDITIONS
    driver.find_element_by_xpath(
        '/html/body/div[1]/div/div[2]/div[3]/div[2]/div/form/div/div/div[1]/div/div/div/label'
    ).click()
    logger.info('Checkbox enabled for "Súhlasím s obchodnými podmienkami " at "Výber platby (3)".')
    sleep(1)

    # CONTINUE
    driver.find_element_by_xpath(
        '//*[@id="j_idt128"]'
    ).click()
    logger.info('Clicked on "Pokračovať" at "Výber platby (3)".')
    sleep(1)

    # PAY
    driver.find_element_by_xpath(
        '//*[@id="cartForm:j_idt261"]'
    ).click()
    logger.info('Clicked on "Zaplatiť" at "Súhrn (4)".')
    sleep(1)

    """
    TODO

    # DOWNLOAD PDF
    logger.info('DOWNLOAD: Clicked on "Uložiť lístok".')
    driver.find_element_by_xpath(
        '/html/body/div[1]/div/div[2]/div[3]/div[2]/div/form/div/div/div[3]/div[1]/a'
    ).click()

    logger.info('DOWNLOAD: PDF downloaded to "{}".'.format(str(folder)))
    """

    # Waiting 10 seconds
    logger.info('Waiting 10 seconds before closing {} (version {}).'.format(
            driver.capabilities['browserName'],
            driver.capabilities['browserVersion']
        )
    )
    sleep(10)

    # Close the web browser (Firefox).
    driver.close()

    # Info
    logger.info('Closed {} (version {}).'.format(
            driver.capabilities['browserName'],
            driver.capabilities['browserVersion']
        )
    )


def main():

    # Argument parser
    parser = argparse.ArgumentParser(
        description = (
            'Automated webticket buying for "slovakrail.sk". You have to specify\n'
            'departure and arrival stations, date and time in an exact form, like\n'
            'it is on the website of the "slovakrail.sk".\n'
        ),
        epilog = (
            'EXAMPLES\n'
            '       python3.6 buy.py -h\n'
            '       python3.6 buy.py --help\n'
            '\n'
            '       python3.6 buy.py -D "Bratislava hl.st." -A "Kúty" -t "05:16" -d "18.03.2019" -v\n'
            '       python3.6 buy.py --departure "Bratislava hl.st." --arrival "Kúty" --time "05:16" --date "18.03.2019" --verbose\n'
            '\n'
            '       python3.6 buy.py -D "Bratislava hl.st." -A "Kúty" -t "05:16" -d "18.03.2019" -H -v\n'
            '       python3.6 buy.py --departure "Bratislava hl.st." --arrival "Kúty" --time "05:16" --date "18.03.2019" --headless --verbose\n'
            '\n'
            '       python3.6 buy.py -D "Bratislava hl.st." -A "Kúty" -t "05:16" -d "18.03.2019" -F -v\n'
            '       python3.6 buy.py --departure "Bratislava hl.st." --arrival "Kúty" --time "05:16" --date "18.03.2019" --fullscreen --verbose'
        ),
        formatter_class = argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--departure',
        '-D',
        default=None,
        required=True,
        help='Exact departure station.'
    )
    parser.add_argument(
        '--arrival',
        '-A',
        default=None,
        required=True,
        help='Exact arrival station.'
    )
    parser.add_argument(
        '--time',
        '-t',
        default=None,
        required=True,
        help='Exact departure time in format: HH:MM.'
    )
    parser.add_argument(
        '--date',
        '-d',
        default=None,
        required=True,
        help='Exact departure date in format: DD.MM.YYYY.'
    )
    parser.add_argument(
        '--verbose',
        '-v',
        default=False,
        action='store_true',
        help='Explain what is being done.'
    )

    # arguments that are not allowed together at the same time
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-H',
        '--headless',
        default=False,
        action='store_true',
        help='Run browser in a headless mode.'
    )
    group.add_argument(
        '-F',
        '--fullscreen',
        default=False,
        action='store_true',
        help='Run browser in a full screen mode.'
    )

    global args
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.INFO)

    # Date check
    is_date(args.date)
    logger.info('value DATE = "{}"'.format(args.date))

    # Time check
    is_time(args.time)
    logger.info('value TIME = "{}"'.format(args.time))

    # Departure destination check
    if isinstance(args.departure, str):
        logger.info('value DEPARTURE = "{}"'.format(args.departure))
    else:
        logger.error('Wrong departure option!')

    # Arrival destination check
    if isinstance(args.arrival, str):
        logger.info('value ARRIVAL = "{}"'.format(args.arrival))
    else:
        logger.error('Wrong arrival option!')

    # Buy the specified ticket
    try:
        buy_ticket()
    except WebDriverException:
        logger.exception('An exception raised while buying a ticket!')


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)

    logging.setLoggerClass(Logger)
    logging.basicConfig(
        format='%(asctime)-19s | %(pathname)s:%(lineno)-3d | %(levelname)-5s | %(message)s',
        datefmt='%d-%m-%Y %H:%M:%S'
    )

    logger = logging.getLogger("Logger")

    main()
    logger.info("Successful termination.")
    sys.exit(0)
