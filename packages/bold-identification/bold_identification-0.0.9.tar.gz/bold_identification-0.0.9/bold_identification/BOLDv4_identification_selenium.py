#!/usr/bin/env python3
# Copyright Guanliang MENG 2018
# License: GPL v3 
import re
import sys
import time
import platform
import os
import argparse
from Bio import SeqIO
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import shutil
import requests
import pathlib
import stat
import logging


def get_parameters(logger=None):
    description='''
    To identify taxa of given sequences. If some sequences fail to get taxon information, you can run another searching for those sequences. This can be caused by TimeoutException if your network to the BOLD server is bad. Or you can lengthen the time to wait for each query (-t option). 

    By mengguanliang@genomics.cn.
    '''
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('-i', dest='infile', required=True,
        help='input fasta file')

    parser.add_argument('-o', dest='outfile', required=True,
        help='outfile')

    parser.add_argument('-d', dest='db', choices=['COX1', 'COX1_SPECIES', 'COX1_SPECIES_PUBLIC', 'COX1_L640bp', 'ITS', 'Plant'], required=False, default='COX1', help='database to search [%(default)s]')

    parser.add_argument('-b', dest='browser', choices=['Firefox', 'Chrome'], required=False, default='Chrome', help='browser to be used [%(default)s]')

    parser.add_argument('-t', dest='timeout', type=int, required=False, 
        default=30, help='the time to wait for a query [%(default)s]')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()
    else:
        args = parser.parse_args()
        logger.debug(args)
        return args


def download_browser(executable_path=None, logger=None):
    brow_plt_url = {
        'Firefox':{
            'Darwin': 'https://github.com/mozilla/geckodriver/releases/download/v0.21.0/geckodriver-v0.21.0-macos.tar.gz',
            'Linux': 'https://github.com/mozilla/geckodriver/releases/download/v0.21.0/geckodriver-v0.21.0-linux64.tar.gz',
            'Windows': 'https://github.com/mozilla/geckodriver/releases/download/v0.21.0/geckodriver-v0.21.0-win64.zip',
            },
        'Chrome':{
            'Darwin': 'https://chromedriver.storage.googleapis.com/2.40/chromedriver_mac64.zip',
            'Linux': 'https://chromedriver.storage.googleapis.com/2.40/chromedriver_linux64.zip',
            'Windows': 'https://chromedriver.storage.googleapis.com/2.40/chromedriver_win32.zip',
        },
    }

    executable_name = os.path.basename(executable_path)
    outdir = os.path.dirname(executable_path)
    platform = os.path.basename(outdir)
    browser = os.path.basename(os.path.dirname(outdir))
    url = brow_plt_url[browser][platform]

    
    pathlib.Path(outdir).mkdir(parents=True, exist_ok=True)
    zname = os.path.basename(url)
    outfile = os.path.join(outdir, zname)

    logger.warn('Downloading browser from ' + url)
    with open(outfile, 'wb') as zfile:
        try:
            resp = requests.get(url)
            zfile.write(resp.content)
        except requests.exceptions.ConnectionError:
            log = 'requests.exceptions.ConnectionError\n'
            log += 'Your network is bad. Please download the file ' + url + ' manually.\n'
            log += 'Then unpack the file and put the executable file to ' + outdir + '\n'
            log += 'And change the name to be ' + executable_name + '\n'
            log += 'You May also add executable permissions for this file, e.g. with chmod 755 command on Linux system.\n'
            log += 'Or, you may change to use another browser (-b option)\n'
            logger.error(log)
            sys.exit()


    logger.warn('Unpack the file ' + outfile)
    shutil.unpack_archive(outfile, extract_dir=outdir)

    logger.warn('Remove the file ' + outfile)
    pathlib.Path(outfile).unlink()

    logger.warn('Make the file be executable')
    os.chmod(executable_path, 0o555)    

    return None


def get_driver(browser='Firefox', logger=None):
    plt = platform.system()
    filedir = os.path.abspath(os.path.dirname(__file__))
    drivers_dir = os.path.join(filedir, 'drivers')

    if plt in ['Darwin', 'Linux']:
        if browser == 'Firefox':
            executable_path = os.path.join(drivers_dir, browser, plt, 
                'geckodriver')
        elif browser == 'Chrome':
            executable_path = os.path.join(drivers_dir, browser, plt, 
                'chromedriver')
    elif plt == 'Windows':
        if browser == 'Firefox':
            sys.exit('Firefox on Windows platform is bad, use "-b Chrome" instead.')
        elif browser == 'Chrome':
            executable_path = os.path.join(drivers_dir, browser, plt, 
                'chromedriver.exe')
    else:
        logger.error('unSupported platform: ' + plt)
        sys.exit()


    if not os.path.exists(executable_path):
        logger.warn('Local ' + executable_path + ' not found!',)
        download_browser(executable_path=executable_path, logger=logger)
        if (plt == 'Windows') and (browser == 'Chrome'):
            win_chrome = os.path.join(filedir, 'chromedriver.exe')
            if not os.path.exists(win_chrome):
                shutil.copyfile(executable_path, win_chrome)
                executable_path = win_chrome

    if browser == 'Firefox':
        driver = webdriver.Firefox(executable_path=executable_path)
    elif browser == 'Chrome':
        driver = webdriver.Chrome(executable_path=executable_path)
    else:
        logger.error('unSupported browser: ' + browser)
        sys.exit()

    return driver


def choose_db(db=None):
    # from Firefox
    db_xpath = {
    'COX1': '/html/body/div[1]/div[3]/div/div/div/div[2]/div/div[1]/div/form/table/tbody/tr[1]/td[1]/input',
    'COX1_SPECIES': '/html/body/div[1]/div[3]/div/div/div/div[2]/div/div[1]/div/form/table/tbody/tr[2]/td[1]/input',
    'COX1_SPECIES_PUBLIC': '/html/body/div[1]/div[3]/div/div/div/div[2]/div/div[1]/div/form/table/tbody/tr[3]/td[1]/input',
    'COX1_L640bp': '/html/body/div[1]/div[3]/div/div/div/div[2]/div/div[1]/div/form/table/tbody/tr[4]/td[1]/input',
    'ITS': '/html/body/div[1]/div[3]/div/div/div/div[2]/div/div[2]/div/form/table/tbody/tr/td[1]/input',
    'Plant': '/html/body/div[1]/div[3]/div/div/div/div[2]/div/div[3]/div/form/table/tbody/tr/td[1]/input',
    }
    return db_xpath[db]


def BOLD_identification(driver=None, seq=None, db=None, timeout=None, logger=None):
    BOLDdb = choose_db(db=db)

    logger.debug(BOLDdb)

    # open the search web, waiting for the presence of elements
    logger.debug('open http://www.boldsystems.org/index.php/IDS_OpenIdEngine')
    driver.get("http://www.boldsystems.org/index.php/IDS_OpenIdEngine")
    try:
        logger.debug('''driver.execute_script("document.body.style.zoom='100%'")''')

        driver.execute_script("document.body.style.zoom='100%'")

        WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, BOLDdb)))

        WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, '//*[@id="sequence"]')))
    except:
        logger.warn('bad network to open http://www.boldsystems.org/index.php/IDS_OpenIdEngine')
        return None

    assert "Identification" in driver.title

    # choose a database
    elem = driver.find_element_by_xpath(BOLDdb)
    # time.sleep(1)
    # the following expression is critical for Chrome driver!
    # if not used, Chrome fails to click when opens the searching page second time.
    logger.debug('''driver.execute_script("window.scrollTo(0,0);")''')
    driver.execute_script("window.scrollTo(0,0);")
    # time.sleep(3)
    time.sleep(1)
    elem.click()

    # input sequence
    elem = driver.find_element_by_xpath('//*[@id="sequence"]')
    elem.send_keys(seq)

    # submit
    if 'ITS' in db:
        elem = driver.find_element_by_xpath(r'//*[@id="submitFungal"]')
    elif 'Plant' in db:
        elem = driver.find_element_by_xpath(r'//*[@id="submitPlant"]')
    else:
        elem = driver.find_element_by_xpath(r'//*[@id="submitAnimal"]')
    elem.click()

    # wait returning result
    # 
    try:
        elem = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[3]/div/div[2]/div[2]/div[2]/div/div/table/tbody/tr[2]')))

        ranks = ('Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species', 'Subspecies', 'Similarity', 'Status')
        taxa = {}
        for i in ranks:
            taxa[i] = ''

        # tips: 
        # do not capture too exactly, to the 'td' level is fine, 
        # but do not capture 'h' or 'em' level. Because BOLD result page won't
        # have 'h' or 'em' item when the result is empty.

        taxa['Phylum'] = driver.find_element_by_xpath('//*[@id="searchSummary"]/div[2]/div[2]/div/div/table/tbody/tr[2]/td[1]').text
        taxa['Class'] = driver.find_element_by_xpath('//*[@id="searchSummary"]/div[2]/div[2]/div/div/table/tbody/tr[2]/td[2]').text
        taxa['Order'] = driver.find_element_by_xpath('//*[@id="searchSummary"]/div[2]/div[2]/div/div/table/tbody/tr[2]/td[3]').text
        taxa['Family'] = driver.find_element_by_xpath('//*[@id="searchSummary"]/div[2]/div[2]/div/div/table/tbody/tr[2]/td[4]').text
        taxa['Genus'] = driver.find_element_by_xpath('//*[@id="searchSummary"]/div[2]/div[2]/div/div/table/tbody/tr[2]/td[5]').text
        taxa['Species'] = driver.find_element_by_xpath('//*[@id="searchSummary"]/div[2]/div[2]/div/div/table/tbody/tr[2]/td[6]').text
        taxa['Subspecies'] = driver.find_element_by_xpath('//*[@id="searchSummary"]/div[2]/div[2]/div/div/table/tbody/tr[2]/td[7]').text
        taxa['Similarity'] = driver.find_element_by_xpath('//*[@id="searchSummary"]/div[2]/div[2]/div/div/table/tbody/tr[2]/td[8]').text
        taxa['Status'] = driver.find_element_by_xpath('//*[@id="searchSummary"]/div[2]/div[2]/div/div/table/tbody/tr[2]/td[9]').text

        # taxa['Phylum'] = driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div[2]/div[2]/div[2]/div/div/table/tbody/tr[2]/td[1]/h6').text
        # taxa['Class'] = driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div[2]/div[2]/div[2]/div/div/table/tbody/tr[2]/td[2]/h6').text
        # taxa['Order'] = driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div[2]/div[2]/div[2]/div/div/table/tbody/tr[2]/td[3]/h6').text
        # taxa['Family'] = driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div[2]/div[2]/div[2]/div/div/table/tbody/tr[2]/td[4]/h6').text
        # taxa['Genus'] = driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div[2]/div[2]/div[2]/div/div/table/tbody/tr[2]/td[5]/h6/em').text
        # taxa['Species'] = driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div[2]/div[2]/div[2]/div/div/table/tbody/tr[2]/td[6]/h6/em').text
        # taxa['Subspecies'] = driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div[2]/div[2]/div[2]/div/div/table/tbody/tr[2]/td[7]/h6/em').text
        # taxa['Similarity'] = driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div[2]/div[2]/div[2]/div/div/table/tbody/tr[2]/td[8]/h6').text
        # taxa['Status'] = driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div[2]/div[2]/div[2]/div/div/table/tbody/tr[2]/td[9]/h6').text

    except selenium.common.exceptions.TimeoutException:
        logger.warn('TimeoutException: ' + seq.split('\n')[0])
        return None

    return taxa


def main():
    # 级别排序:CRITICAL > ERROR > WARNING > INFO > DEBUG
    
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG) # must be DEBUG, then 'ch' below works.
    # logger.setFormatter(formatter)

    fh = logging.FileHandler(os.path.basename(sys.argv[0]) + '.infor')
    fh.setLevel(logging.INFO) # INFO level goes to the log file
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING) # only WARNING level will output on screen
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    args = get_parameters(logger=logger)

    driver = get_driver(browser=args.browser, logger=logger)

    ranks = ('Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species', 'Subspecies', 'Similarity', 'Status')

    fhout = open(args.outfile, 'w')
    print('Seq id\t' + '\t'.join(ranks), file=fhout)
    
    count = 0
    for rec in SeqIO.parse(args.infile, 'fasta'):
        count += 1
        logger.info(str(count) + '\t' + rec.id)

        print(rec.description, end='', file=fhout)

        seq = '>' + str(rec.id) + '\n'+ str(rec.seq)
        taxa = BOLD_identification(driver=driver, 
            seq=seq, db=args.db, timeout=args.timeout, logger=logger)
        
        if taxa:
            for i in ranks:
                print('\t'+taxa[i], end='', file=fhout)
        else:
            print('\tTimeoutException', end='', file=fhout)
            
        print(file=fhout, flush=True)

        time.sleep(1)

    driver.quit()
    fhout.close()


if __name__ == '__main__':
    main()

