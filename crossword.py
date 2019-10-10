import os
import pickle
import urllib
from getpass import getpass

import requests
import yaml
from bs4 import BeautifulSoup
from enum import Enum


class CrosswordFetcher:
    SESSION_FILE = '.sessionfile'
    CONFIG_FILE = '.timescrosswords.yaml'

    def __init__(self):
        # Load the session from a saved file
        self.load_credentials()
        self.load_session()

    def load_credentials(self):
        try:
            with open(self.CONFIG_FILE, 'r') as configfile:
                self.cookies = yaml.load(configfile)
        except IOError:
            # No config file - create one
            # Warning - password is stored unencrypted.
            self.cookies = {
                'acs_tnl': getpass('acs_tnl Cookie: '),
                'sacs_tnl': getpass('sacs_tnl Cookie: ')
            }
            with open(self.CONFIG_FILE, 'w') as configfile:
                yaml.dump({
                    'acs_tnl': self.cookies['acs_tnl'],
                    'sacs_tnl': self.cookies['sacs_tnl'],
                }, configfile, default_flow_style=False)
            os.chmod(self.CONFIG_FILE, 400)

    def load_session(self):
        self.session = requests.session()
        try:
            with open(self.SESSION_FILE, 'rb') as f:
                self.session.cookies.update(pickle.load(f))
            self.session.cookies.update(self.cookies)
        except (IOError, EOFError):
            pass  # Empty cookies, ignore

    def save_session(self):
        with open(self.SESSION_FILE, 'wb') as f:
            pickle.dump(self.session.cookies, f)

    def get_query_params(self, url):
        params = url.split('?')[1]
        keyvalues = [param for param in params.split('&')]
        return {param.split('=')[0]: param.split('=')[1] for param in keyvalues}

    def get_page(self, url):
        results = self.session.get(url, allow_redirects=False)
        if results.status_code == 200:
            return results
        else:  # logged out
            self.login()
            get = self.session.get(url)
            return get

    def __del__(self):
        self.save_session()

    def get_crosswords(self, start, end):
        search_page = self.construct_url(start, end)
        pdfs = self.get_crosswords_from_url(search_page)
        print('Downloading {count} crosswords'.format(count=len(pdfs)))
        for pdf in pdfs:
            self.download_and_save(pdf)

    def get_crosswords_from_url(self, url):
        r = self.session.get(url)
        if not r.ok:
            raise Exception("Couldn't get official results from", url, r)

        b = BeautifulSoup(r.text, features='html.parser')
        # Get all the printable links
        print_links = b.find_all('p', {'class': 'PuzzleItem-secondary-link PuzzleItem--print-link'})
        links = [p.contents[0]['href'] for p in print_links]
        print('Found {count} crosswords'.format(count=len(links)))
        if len(links) == 0:
            return links
        try:
            show_more_link=next(f for f in b.find_all('a', {'class': 'Item-cta Link--primary'}) if f.text=='Show more')['href']
            return links + self.get_crosswords_from_url(show_more_link)
        except StopIteration:  # No link to more. Nothing to do
            pass
            return links

    def download_and_save(self, url):
        resp = self.session.get(url)
        print('Saving ' + url)
        fd = open(url.split('/')[-1] + '.pdf', 'wb')
        fd.write(resp.content)
        fd.close()

    def construct_url(self, start, end):
        return 'https://www.thetimes.co.uk/puzzleclub/crosswordclub/puzzles-list?search=&filter[puzzle_type]={type}&filter[publish_at][from]={start}&filter[publish_at][to]={end}'\
            .format(type=CrosswordType.QUICK_CRYPTIC, start=start, end=end)


class CrosswordType(Enum):
    QUICK_CRYPTIC = 1


if __name__ == '__main__':
    CrosswordFetcher().get_crosswords('01/09/2019', '30/09/2019')


