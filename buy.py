#!/usr/bin/python3.6
# coding=UTF-8


import os
import sys
import signal
import argparse
import datetime

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


class LogType(Enum):
    INFO = 'INFO'
    ERROR = 'ERROR'


def exit(msg, exitcode=1, type=LogType.ERROR):
    log(msg, type=type)
    sys.exit(exitcode)


def log(msg, type=LogType.INFO):
    if args.verbose or type == LogType.ERROR:
        caller = getframeinfo(stack()[1][0])
        print('{} {}:{} {}: {}'.format(
                datetime.datetime.now(),
                caller.filename,
                caller.lineno,
                type.name,
                msg
            ),
            file = sys.stderr if type == LogType.ERROR else sys.stdout,
            flush = True,
            end = '\n'
        )
    else:
        pass


def signal_handler(signal, frame):
    sys.stdout.write("\n\nInterrupt from keyboard.\n")
    sys.exit(0)


def is_date(msg):
    try:
        datetime.datetime.strptime(msg, '%d.%m.%Y')
    except ValueError:
        exit('Wrong date option!', exitcode=2)


def is_time(msg):
    try:
        datetime.datetime.strptime(msg, '%H:%M')
    except ValueError:
        exit('Wrong time option!', exitcode=3)


def load_user_credentials(filename):
    import imp
    f = open(filename)
    credentials = imp.load_source('person', '', f)
    f.close()
    return credentials


def buy_ticket():

    # FIREFOX DESTINATION FOLDER
    folder = os.path.dirname(os.path.realpath(__file__))

    # FIREFOX OPTIONS
    options = Options();

    # Use headless mode.
    if args.headless:
        options.headless = args.headless

    # FIREFOX PROFILE
    profile = FirefoxProfile()
    profile.set_preference('browser.download.folderList',2);
    profile.set_preference('browser.download.manager.showWhenStarting', False);
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/octet-stream,application/vnd.ms-excel');
    profile.set_preference('browser.download.dir',str(folder));
    log('FirefoxProfile: "browser.download.dir" = "{}"'.format(str(folder)))

    # Launch Firefox web browser.
    driver = webdriver.Firefox(options=options, firefox_profile=profile)

    # Use full screen mode.
    if args.fullscreen:
        driver.maximize_window()

    # Logging information
    log('Opened {} (version {})'.format(
            driver.capabilities['browserName'],
            driver.capabilities['browserVersion']
        )
    )

    # Sets a sticky timeout to implicitly wait for an element to be found, or a command to complete.
    driver.implicitly_wait(30)

    # Load page 'Vyhľadanie spojenia'
    driver.get('https://ikvc.slovakrail.sk/esales/search')

    # Info
    log('Loading page "Vyhľadanie spojenia"')

    try:
        delay = 30  # wait seconds for web page to load, added more second

        WebDriverWait(driver, delay).until(
            EC.presence_of_all_elements_located(
                (By.ID, 'searchPanel')
            )
        )

        # Logging information
        log('Loaded page "Vyhľadanie spojenia"')

    except TimeoutException:
        log('Loading took too much time.')
        log('Closed {} (version {}).'.format(
               driver.capabilities['browserName'],
               driver.capabilities['browserVersion']
           )
        )
        driver.close()
        exit('Page loading failure.', exitcode=1)

    sleep(1)

    # Info
    log('Page title is "{}".'.format(driver.title))

    # Check if 'ZSSK' is in the page title
    assert 'ZSSK' in driver.title

    # FROM
    elem_city_from = driver.find_element_by_id('fromInput')
    elem_city_from.clear()
    elem_city_from.send_keys(args.departure)
    driver.find_element_by_xpath(
        '/html/body/div[1]/div/div[2]/div[3]/div/div/form/div[1]/div/div[1]/div[1]/div[1]/ul/li/a'
    ).click
    log('Filling "Odkiaľ" in "Vyhľadanie spojenia" with "{}".'.format(args.departure))
    sleep(0.5)

    # TO
    elem_city_to = driver.find_element_by_id('toInput')
    elem_city_to.clear()
    elem_city_to.send_keys(args.arrival)
    driver.find_element_by_xpath(
        '/html/body/div[1]/div/div[2]/div[3]/div/div/form/div[1]/div/div[1]/div[1]/div[3]/ul/li/a'
    ).click
    log('Filling "Kam" in "Vyhľadanie spojenia" with "{}".'.format(args.arrival))
    sleep(0.5)

    # DATE
    elem_date = driver.find_element_by_id('departDate')
    elem_date.clear()
    elem_date.send_keys(args.date)
    driver.find_element_by_xpath('//html').click();
    log('Filling "Dátum cesty tam" in "Vyhľadanie spojenia" with "{}".'.format(args.date))
    sleep(0.5)

    # TIME
    elem_time = driver.find_element_by_id('departTime')
    elem_time.clear()
    elem_time.send_keys(args.time)
    driver.find_element_by_xpath('//html').click();
    log('Filling "Odchod" in "Vyhľadanie spojenia" with "{}".'.format(args.time))
    sleep(0.5)

    log('Filled train credentials in "Vyhľadanie spojenia".')

    # CONFIRM
    driver.find_element_by_id('actionSearchConnectionButton').click()
    log('Clicked on "Vyhľadať spojenie".')
    sleep(2)

    # CLICK ON FIRST
    driver.find_element_by_css_selector(
        'div.connection-group:nth-child(2) > div:nth-child(1)'
    ).click()
    log('Clicked on first train.')
    sleep(1)

    # BUY TICKET
    driver.find_element_by_xpath(
        '//*[@id="dayGroupLoop:0:eSalesConnectionLoop:0:j_idt302"]'
    ).click()
    log('Clicked on "Kúpiť lístok".')
    sleep(1)

    # PASSENGER TYPE SELECTION
    driver.find_element_by_xpath(
        '/html/body/div[1]/div/div[2]/div[3]/span/div/div[1]/form/div/div/div/div/div/div/div[1]/div[1]/div/div/div/div/a[1]/span[2]'
    ).click()
    log('Choosing passenger type.')
    sleep(1)

    # JUNIOR SELECTION
    driver.find_element_by_xpath(
        '/html/body/div[1]/div/div[2]/div[3]/span/div/div[1]/form/div/div/div/div/div/div/div[1]/div[1]/div/div/div[1]/div/a[1]/ul/li[3]'
    ).click()
    log('Selected "Mladý (16 - 25 r.)".')
    sleep(1)

    # DISCOUNT SELECTION
    driver.find_element_by_xpath(
        '/html/body/div[1]/div/div[2]/div[3]/span/div/div[1]/form/div/div/div/div/div/div/div[1]/div[1]/div/div/div/div/a[2]/span[2]'
    ).click()
    log('Choosing card type.')
    sleep(1)

    # CARD SELECTION
    driver.find_element_by_xpath(
        '/html/body/div[1]/div/div[2]/div[3]/span/div/div[1]/form/div/div/div/div/div/div/div[1]/div[1]/div/div/div[1]/div/a[2]/ul/li[2]'
    ).click()
    log('Selected "Preukaz pre žiaka/Študenta".')
    sleep(1)

    # ENABLED OPTION FOR FREE TICKET
    driver.find_element_by_xpath(
        '/html/body/div[1]/div/div[2]/div[3]/span/div/div[1]/form/div/div/div/div/div/div/div[1]/div[1]/div/div/div[2]/div/div/label'
    ).click()
    log('Checkbox enabled for "Nárok na bezplatnú prepravu".')
    sleep(1)

    # CONTINUE
    driver.find_element_by_xpath(
        '//*[@id="actionIndividualContinue"]'
    ).click()
    log('Clicked on "Pokračovať" at "Voľba cestujúcich".')
    sleep(3)

    # CONTINUE
    driver.find_element_by_xpath(
        '//*[@id="ticketsForm:connection-offer:final-price:j_idt198"]'
    ).click()
    log('Clicked on "Pokračovať" at "Voľba cestovného lístka".')
    sleep(1)

    # CONTINUE
    driver.find_element_by_xpath(
        '//*[@id="ticketsForm:j_idt97"]'
    ).click()
    log('Clicked on "Pokračovať" at "Doplnkové služby".')
    sleep(1)

    # CONTINUE
    driver.find_element_by_xpath(
        '//*[@id="cartForm:j_idt284"]'
    ).click()
    log('Clicked on "Pokračovať" at "Obsah košíka (1)".')
    sleep(1)

    # LOAD PERSONAL INFORMATION
    person = load_user_credentials('person.txt')

    # FILL EMAIL
    email = driver.find_element_by_id('email')
    email.clear()
    email.send_keys(person.email)
    log('Filling "Váš e-mail" at "Osobné údaje (2)".')

    # FILL NAME
    name = driver.find_element_by_id('cartItemLoop:0:connectionPersonal:passengerLoop:0:firstname')
    name.clear()
    name.send_keys(person.name)
    log('Filling "Meno" at "Osobné údaje (2)".')

    # FILL SURNAME
    surname = driver.find_element_by_id('cartItemLoop:0:connectionPersonal:passengerLoop:0:lastname')
    surname.clear()
    surname.send_keys(person.surname)
    log('Filling "Priezvisko" at "Osobné údaje (2)".')

    # FILL REGISTRATION NUMBER
    card_number = driver.find_element_by_id('cartItemLoop:0:connectionPersonal:passengerLoop:0:cislo-registracie-p1')
    card_number.clear()
    card_number.send_keys(person.train_card)
    log('Filling "Číslo registrácie:" at "Osobné údaje (2)".')

    log('All personal informations filled at "Osobné údaje (2)".')

    # CONTINUE
    driver.find_element_by_xpath(
        '//*[@id="j_idt177"]'
    ).click()
    log('Clicked on "Pokračovať" at "Osobné údaje (2)".')
    sleep(1)

    # I AGREE WITH THE TERMS AND CONDITIONS
    driver.find_element_by_xpath(
        '/html/body/div[1]/div/div[2]/div[3]/div[2]/div/form/div/div/div[1]/div/div/div/label'
    ).click()
    log('Checkbox enabled for "Súhlasím s obchodnými podmienkami " at "Výber platby (3)".')
    sleep(1)

    # CONTINUE
    driver.find_element_by_xpath(
        '//*[@id="j_idt107"]'
    ).click()
    log('Clicked on "Pokračovať" at "Výber platby (3)".')
    sleep(1)

    # PAY
    driver.find_element_by_xpath(
        '//*[@id="cartForm:j_idt240"]'
    ).click()
    log('Clicked on "Zaplatiť" at "Súhrn (4)".')
    sleep(1)

    """
    TODO

    # DOWNLOAD PDF
    log('DOWNLOAD: Clicked on "Uložiť lístok".')
    driver.find_element_by_xpath(
        '/html/body/div[1]/div/div[2]/div[3]/div[2]/div/form/div/div/div[3]/div[1]/a'
    ).click()

    log('DOWNLOAD: PDF downloaded to "{}".'.format(str(folder)))
    """

    # Waiting 10 seconds
    log('Waiting 10 seconds before closing {} (version {}).'.format(
            driver.capabilities['browserName'],
            driver.capabilities['browserVersion']
        )
    )
    sleep(10)

    # Close the web browser (Firefox).
    driver.close()

    # Info
    log('Closed {} (version {}).'.format(
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
            '       python3.6 buy_ticket -h\n'
            '       python3.6 buy_ticket --help\n'
            '\n'
            '       python3.6 buy_ticket.py -D "Bratislava hl.st." -A "Kúty" -t "05:16" -d "18.03.2019" -v\n'
            '       python3.6 buy_ticket.py --departure "Bratislava hl.st." --arrival "Kúty" --time "05:16" --date "18.03.2019" --verbose\n'
            '\n'
            '       python3.6 buy_ticket.py -D "Bratislava hl.st." -A "Kúty" -t "05:16" -d "18.03.2019" -H -v\n'
            '       python3.6 buy_ticket.py --departure "Bratislava hl.st." --arrival "Kúty" --time "05:16" --date "18.03.2019" --headless --verbose\n'
            '\n'
            '       python3.6 buy_ticket.py -D "Bratislava hl.st." -A "Kúty" -t "05:16" -d "18.03.2019" -F -v\n'
            '       python3.6 buy_ticket.py --departure "Bratislava hl.st." --arrival "Kúty" --time "05:16" --date "18.03.2019" --fullscreen --verbose'
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

    # Argument parsing.
    global args
    args = parser.parse_args()

    # Info
    log('Running {}'.format(str(__file__)))

    # Date check
    is_date(args.date)
    log('DATE = {}'.format(args.date))

    # Time check
    is_time(args.time)
    log('TIME = {}'.format(args.time))

    # Departure destination check
    if isinstance(args.departure, str):
        log('DEPARTURE = {}'.format(args.departure))
    else:
        exit('Wrong departure option!', exitcode=4)

    # Arrival destination check
    if isinstance(args.arrival, str):
        log('ARRIVAL = {}'.format(args.arrival))
    else:
        exit('Wrong arrival option!', exitcode=5)

    # Headless browser mode
    log('HEADLESS = {}'.format(args.headless))

    # Full screen browser mode
    log('FULLSCREEN = {}'.format(args.fullscreen))

    # Buy ticket
    try:
        buy_ticket()
    except WebDriverException:
        exit('An unexpected error occurred when buying a ticket!', exitcode=101)

    # Info
    log("Terminating {}".format(str(__file__)))

    # Terminate the program with exit status 0.
    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    try:
        main()
    except Exception as e:
        exit(e.__str__(), exitcode=100, type='EXCEPTION')
