import concurrent.futures
import os
import pdb

from bs4 import BeautifulSoup
from selenium import webdriver
import wget


def download_file(url, destination):
    return wget.download(url, out=destination)


if __name__ == '__main__':

    URL_ROOT = 'http://www.dutchpod101.com'
    INIT_URL = 'https://www.dutchpod101.com/lesson-library/'
    LEVELS = ['absolutebeginner', 'beginner', 'intermediate', 'advanced', 'bonus']

    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get(INIT_URL)
    driver_content = driver.page_source.encode('utf-8').strip()
    content = BeautifulSoup(driver_content, 'html.parser')
    # To login once through the UI
    pdb.set_trace()

    future_to_file = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for level in LEVELS:
            url = INIT_URL + level
            driver.get(url)
            driver_content = driver.page_source.encode('utf-8').strip()
            content = BeautifulSoup(driver_content, 'html.parser')
            level_tag = 'data-' + level
            atags = content.findAll(
                'a', {
                    'class': ['ll-collection-all', 'll-collection-all--private'],
                    'data-audio': '1',
                    'data-video': '0',
                    level_tag: '1'
                })
            links = [atag.get('href', '') for atag in atags]

            for link in links:
                link_local_path = link.split('/')[2]
                local_dir = os.path.join(level, link_local_path)
                os.makedirs(local_dir)

                driver.get(URL_ROOT + link)
                driver_content = driver.page_source.encode('utf-8').strip()
                content = BeautifulSoup(driver_content, 'html.parser')
                atags = content.findAll('a', {'class': 'cl-lesson__lesson'})
                lesson_links = [atag.get('href', '') for atag in atags]

                for lesson_link in lesson_links:
                    lesson_link_local_path = lesson_link.split('/')[2]
                    local_file = os.path.join(local_dir, lesson_link_local_path + '.mp3')

                    driver.get(URL_ROOT + lesson_link)
                    driver_content = driver.page_source.encode('utf-8').strip()
                    content = BeautifulSoup(driver_content, 'html.parser')
                    div = content.find('div', {'class': 'r101-headline__bar'})
                    atags = div.find_all('a')
                    dl_link = [x.get('href', '') for x in atags if 'mp3' in x.get('href', '')][0]
                    future_to_file.append(executor.submit(download_file, dl_link, local_file))

        for future in concurrent.futures.as_completed(future_to_file):
            pdb.set_trace()
            try:
                filename = future.result()
            except Exception as exc:
                print(exc)
            else:
                print(filename)

    driver.quit()
