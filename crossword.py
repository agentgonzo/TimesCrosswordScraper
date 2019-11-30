import os
import pickle
from getpass import getpass

import requests
import yaml
from bs4 import BeautifulSoup


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
                self.cookies = yaml.load(configfile, Loader=yaml.FullLoader)
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

    def __del__(self):
        self.save_session()

    def get_crosswords(self, crossword_type, start, end, to_print=False):
        search_page = self.construct_url(crossword_type, start, end)
        pdfs = self.get_crosswords_from_url(search_page)
        print('Downloading {count} crosswords'.format(count=len(pdfs)))
        for pdf in pdfs:
            filename = self.download_and_save(pdf)
            if to_print:
                self.print_crossword(filename)

    def get_crosswords_from_url(self, url):
        r = self.session.get(url)
        if not r.ok:
            raise Exception("Couldn't get crosswords from", url, r)

        b = BeautifulSoup(r.text, features='html.parser')
        # Get all the printable links
        print_links = b.find_all('p', {'class': 'PuzzleItem-secondary-link PuzzleItem--print-link'})
        links = [p.contents[0]['href'] for p in print_links]
        print('Found {count} crosswords'.format(count=len(links)))
        if len(links) == 0:
            return links
        try:
            show_more_link = \
                next(f for f in b.find_all('a', {'class': 'Item-cta Link--primary'}) if f.text == 'Show more')['href']
            return links + self.get_crosswords_from_url(show_more_link)
        except StopIteration:  # No link to more. Nothing to do
            pass
            return links

    def download_and_save(self, url):
        '''
        Downloads and saves a PDF from the given URL to the current working directory
        :param url: the URL (hopefully a PDF) to download
        :return: the filename of the saved file
        '''
        resp = self.session.get(url)
        print('Saving ' + url)
        fd = open(url.split('/')[-1] + '.pdf', 'wb')
        fd.write(resp.content)
        fd.close()
        return fd.name  # Checkme

    def construct_url(self, crossword_type, start, end):
        return 'https://www.thetimes.co.uk/puzzleclub/crosswordclub/puzzles-list?search=&filter[puzzle_type]={type}&filter[publish_at][from]={start}&filter[publish_at][to]={end}' \
            .format(type=crossword_type, start=start, end=end)

    def print_crossword(self, filename):
        '''
        Prints a file (to the printer, not stdout). Very rudimentary, assumes the default printer
        :param filename: the file to print
        '''
        print('Printing ' + filename)
        os.execv('lp', filename)


crossword_types = {
    "6": "Sunday Times Concise",
    "5": "Times Concise",
    "7": "Times Concise Jumbo",
    "1": "Quick Cryptic",
    "3": "Sunday Times Cryptic",
    "2": "Times Cryptic",
    "4": "Times Cryptic Jumbo",
    "9": "General Knowledge Jumbo",
    "8": "Mephisto",
    "12": "Monthly Club Special",
    "10": "O Tempora! (Latin)",
    "11": "The Listener",
    "SPECIALIST": "Specialist",
    "CRYPTIC": "Cryptic",
}

if __name__ == '__main__':
    # Todo: Parse CLI args

    crossword_type = "hutne"
    while crossword_type not in crossword_types:  # get type from flags
        print ("Crossword types: ")
        for t in crossword_types:
            print(t + ": " + crossword_types[t])
        crossword_type = raw_input("Which Crossword Type? ")

    if True:  # get start date from flags
        start = raw_input("Start Date (dd/mm/yyyy) ")
    if True:  # get end date from flags
        end = raw_input("End Date (dd/mm/yyyy) ")
    # if not to_print:
    #     to_print = raw_input("Print downloaded crosswords?")
    to_print = False  # get this from user input
    CrosswordFetcher().get_crosswords(crossword_type, start, end, to_print=to_print)
