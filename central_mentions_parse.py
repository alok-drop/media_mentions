import bs4
import csv
import email
from itertools import zip_longest
from os import listdir
from os.path import isfile, join
from pprint import pprint as pprint
import random
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import TimeoutException
import time


class Media_Mentions():

    def __init__(self, path):
        
        self.path = "##path" + path

        with open(self.path, 'r') as f:
            email_1 = email.message_from_file(f)
            iterator = email_1.walk()

            for x in iterator:
                if x.get_content_type() == 'text/html':
                    html_string = x.get_payload(decode=True)

        
            self.soup = bs4.BeautifulSoup(html_string, features="html.parser")

            self.lab = self.soup.find("span", text="#organisation_name", style=True)
            self.lab_i_tags = self.lab.find_all_next("i")
            self.lab_span_tags = self.lab.find_all_next("span", text=True)
            self.lab_a_tags = self.lab.find_all_next("a", href=True)
            self.url_list = []
            for tag in self.lab_a_tags:
                if tag.parent.name == 'p':
                    self.url_list.append(tag['href'])



    def outlet_find(self):
        outlet_list = []
        for tag in self.lab_span_tags:
            try:

                if tag.next_sibling.name == 'br' and tag.get_text() != '\n':
                    outlet_list.append((tag.get_text().strip('(').strip(')')))
                    print(tag.get_text().strip('(').strip(')'))
        
            except AttributeError:
                pass
        return outlet_list
        
    def date_find(self):
        date_list = []
        for tag in self.lab_i_tags:
            if len(tag.get_text()) > 7 and "Also appeared in:" not in tag.get_text():
                date_list.append(tag.get_text())
                print(tag.get_text())
        
        return date_list

    def also_appeared_find(self):
        also_appeared_list = []
        for tag in self.lab_i_tags:
            if tag.get_text().startswith("Also appeared in:"):
                also_appeared_list.append(tag.get_text().replace('\n', '').strip(
                    "Also appeared in:"))
        
        print(also_appeared_list)

        return also_appeared_list
    
    def selenium_search(self):
        options = FirefoxOptions()
        options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)
        driver.set_page_load_timeout(60)
        print("\nFirefox driver has started")

        selenium_list = []
        for tag in self.url_list:

            try:
                selenium_dictionary = {'article_name': None, 'article_url(s)': 
                                        {'article_1': None, 'article_2': None}}
        
                driver.get(tag)
                print('\n url sent to google')
                time.sleep(random.uniform(1.00, 5.00))
                if driver.title:
                    article_title = driver.title
                selenium_dictionary['article_name']= article_title
                driver.get(f"https://google.com/search?q={article_title}")
                time.sleep(random.uniform(1.00, 5.00))
                soup1 = bs4.BeautifulSoup(driver.page_source, 'html.parser')
                url_tag = soup1.find_all('h3', {'class': 'LC20lb'})[0].parent['href']

                if url_tag != tag:
                    selenium_dictionary['article_url(s)']['article_1'] = tag
                    selenium_dictionary['article_url(s)']['article_2'] = url_tag
                    print('\npossible rogue URL found', url_tag, '\n')

                else:
                    selenium_dictionary['article_url(s)']['article_1'] = tag
                    selenium_dictionary['article_url(s)']['article_2'] = '' #so the index remains the same between the two lists
                
                selenium_list.append(selenium_dictionary)
                time.sleep(random.uniform(1.00, 10.00))
            
            except TimeoutException:
                print("TIME  OUT")
                selenium_dictionary['article_name']= "NOT_FOUND_TIMEOUT"
                selenium_dictionary['article_url(s)']['article_1'] = "NOT_FOUND_TIMEOUT"
                selenium_list.append(selenium_dictionary)
        
        print('selenium list completed!')
        driver.close()
        
        return selenium_list


    def csv_create(self, outlets, dates, titles, url_1, url_2, appears):
        with open('##path', "a", newline='',
            encoding='utf-8-sig') as f:

            rows = [outlets, dates, titles, url_1, url_2, appears]  
            combined_row = zip_longest(*rows)

            writer = csv.writer(f)
            writer.writerows(combined_row)

        


    def main(self):
        # I want to run all of the methods with one line of code...
 
        outlets = Media_Mentions.outlet_find(self)
        dates = Media_Mentions.date_find(self)
        appears = Media_Mentions.also_appeared_find(self)
        selenium_output = Media_Mentions.selenium_search(self)
        titles = []
        url_1 = []
        url_2 = []
        for article in selenium_output:
            for key, value in article.items():
                if key == 'article_name':
                    titles.append(value)
                if key == 'article_url(s)':
                    url_1.append(value['article_1'])
                    url_2.append(value['article_2'])
        Media_Mentions.csv_create(self, outlets, dates, titles, url_1, url_2, appears)

     

if __name__ == "__main__":
    onlyfiles = [f for f in listdir("##path"
    ) if isfile(join("##path", f))]

    for file_iter in onlyfiles:

        mention_1 = Media_Mentions(file_iter)
        mention_1.main()
        




