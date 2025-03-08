import logging
import random
import sys
import time

from DrissionPage import Chromium, ChromiumOptions
from DrissionPage.errors import ElementNotFoundError, PageDisconnectedError

strs = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
        'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']


def get_random():
    return ''.join(random.choices(strs, k=12))


CODE = get_random()


def fill_up_code(tab, code):
    ele = tab("x://html/body/div[1]/div[2]/div/div/label/input")
    ele.clear(by_js=True)
    time.sleep(0.1)
    ele.clear()
    time.sleep(0.1)
    ele.input(code)


def click_submit(tab):
    button = tab.ele("x:/html/body/div[1]/div[2]/div/div/button")
    button.click()


def write_success_code(code):
    with open("success_codes.txt", "a") as f:
        f.write(f"{code}\n")


def write_failed_code(code):
    with open("failed_codes.txt", "a") as f:
        f.write(f"{code}\n")


def fill_and_submit(tab):
    fill_up_code(tab, CODE)
    click_submit(tab)
    pack = tab.listen.wait(count=1)
    if pack.is_failed:
        logging.info(f"429 Network failed for {CODE}! Retrying...")
        return False
    elif pack.response.body['message'] != 'invalid invitation code' and "validation error" not in pack.response.body[
        'message']:
        logging.info(f"{CODE} Code Success!")
        print(pack.response.body)
        write_success_code(CODE)
        tab.get("https://manus.im/invitation")
        time.sleep(5)
        return True
    else:
        logging.info(f"{CODE} Code failed!")
        write_failed_code(CODE)
        return True


if __name__ == "__main__":
    with open("success_codes.txt", "a") as f:
        f.write("")
    with open("failed_codes.txt", "a") as f:
        f.write("")

    # write into log.log and stdout
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, handlers=[
        logging.FileHandler("manusfucker.log"),
        logging.StreamHandler(sys.stdout)
    ])

    logging.info("Starting to Fuck Manus!")

    option = ChromiumOptions()
    option.set_load_mode("eager")
    browser = Chromium(option)

    tab = browser.new_tab(url="https://manus.im/invitation")
    tab.listen.start(method="POST")
    # get sr_2

    while True:
        try:
            while True:
                try:
                    sr_2 = tab.ele("x:/html/body/div[1]/div[2]/div/div/div[2]/div", timeout=1).shadow_root.get_frame(1,
                                                                                                                     timeout=0.1).ele(
                        'xpath://body', timeout=0.1).shadow_root
                except ElementNotFoundError:
                    continue
                except:
                    logging.warning("sr_2 fucked up!")
                    exit(1)
                if sr_2: break

            container = sr_2.ele("x:/html/body//div[1]/div")
            logging.debug("Get Cloudflare container success!")

            time.sleep(0.5)
            elems = container.children("@@tag()=div@!id=branding").filter.style("display", "none", equal=False)
            if len(elems) != 1:
                continue
            ele = elems[0]

            id = ele.attr('id')
            if id == 'verifying':
                continue
            elif id == 'success':
                logging.debug("CF Fucked, filling up form and submitting...")
                if fill_and_submit(tab):
                    CODE = get_random()
                time.sleep(2)
            elif id == 'fail':
                logging.info("Cloudflare fucked up, refreshing!")
                tab.refresh()
                continue
            elif id == 'expired':
                logging.warning("Cloudflare fucked up, refreshing!")
                tab.refresh()
                continue
            elif id == 'timeout':
                logging.warning("Cloudflare fucked up, refreshing!")
                tab.refresh()
                continue
            elif id == 'challenge-error':
                logging.warning("Cloudflare fucked up, refreshing!")
                tab.refresh()
                continue
            else:
                btn = container.ele("@type=checkbox", timeout=1)
                btn.click()
                logging.info("Cloadflare button clicked!")
                continue
        except PageDisconnectedError:
            logging.warning("Tab fucked")
            tab = browser.latest_tab
        except:
            tab.refresh()
