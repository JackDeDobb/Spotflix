# packages we want to include
import requests
import re
import string
import json
import boto3
from credentials import *
from bs4 import BeautifulSoup
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options


#uses webdriver object 
def get_js_soup(url,browser):
    try:
        browser.get(url)
        res_html = browser.execute_script('return document.body.innerHTML')
        soup = BeautifulSoup(res_html,'html.parser') #beautiful soup object to be used for parsing html content
        return soup
    except:
        return None

#extracts all alphabetical urls from the directory
def scrape_dir_page(dir_url, browser):
    print ('-'*20,'Scraping movies','-'*20)
    movie_links = []
    movie_titles = []
    movie_base_url = 'https://www.imsdb.com/scripts'
    
    #execute js on webpage to load faculty listings on webpage and get ready to parse the loaded HTML 
    soup = get_js_soup(dir_url, browser)
    if soup == None:
        return None
    
    for link in soup.find_all(valign='top'):
        child = link.find_all('p')
        for script in child:
            # lots of quirky formatting issues, kind of mcguyvered this part lel
            movie_titles.append(script.find('a')['href'][15:-12])
            script_url = script.find('a')['href'][14:-12].replace(' ', '-') + '.html'
            movie_links.append(movie_base_url + script_url)
                
    print ('-'*20,'Found {} movie urls'.format(len(movie_links)),'-'*20)
    print(movie_titles)
    return movie_links, movie_titles

def make_dict(script):
    formatAndSplit = re.sub(r'[^A-Za-z]', ' ', script).lower().split()
    wordfreq = {}
    for raw_word in formatAndSplit:
        if raw_word not in wordfreq:
            wordfreq[raw_word] = 0
        wordfreq[raw_word] += 1
    return wordfreq

def get_movie_script(link):
    soup = get_js_soup(link, browser)
    try:
        script = soup.pre.get_text(strip=True)

        return make_dict(script)
    except:
        return None


if __name__ == "__main__":
    options = Options()
    options.headless = True
    browser = webdriver.Chrome('./chromedriver',options=options)


    base_url = 'https://www.imsdb.com/alphabetical/'
    alpha_d = ['0'] + list(string.ascii_uppercase)
    total_movie_links = []
    total_titles = []
    for l in alpha_d:
        print("Page: ", base_url + l)
        links, titles = scrape_dir_page(base_url + l, browser)
        print("Links: ", links)
        if links != None:
            total_movie_links.extend(links)
            total_titles.extend(titles)
    print("Total Number of Scripts : " + str(len(total_movie_links)) )


    script_dicts = []
    title_list = []
    for idx, link in enumerate(total_movie_links):
        script_dict = get_movie_script(link)
        if script_dict != None:
            print("got script dict ", idx)
            title_list.append((total_titles[idx], sum(script_dict.values())))
            script_dicts.append(script_dict)
    #print(script_dicts[0])
    print(title_list)


    #code to create df dictionary
    df_dict = dict()
    for script_dict in script_dicts:
        for word in script_dict.keys():
            if word not in df_dict:
                df_dict[word] = 0
            df_dict[word] += 1

    #AWS S3 Magic
    s3 = boto3.resource('s3', region_name='us-east-1', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    bucket = s3.Bucket('movie-dicts')
    if bucket in s3.buckets.all():
        bucket.objects.all().delete()
        bucket.delete()
    bucket = s3.create_bucket(Bucket='movie-dicts')


    obj = s3.Object('movie-dicts','movieList.json')
    obj.put(Body=json.dumps(script_dicts))

    obj = s3.Object('movie-dicts','titleList.json')
    obj.put(Body=json.dumps(title_list))

    obj = s3.Object('movie-dicts','dfDict.json')
    obj.put(Body=json.dumps(df_dict))

    #json.dump_s3(script_dicts, "listOfMovies")
    print("finished")
    #s3_connection = boto.connect_s3()
    #s3 = boto3.resource('s3')
    #s3.create_bucket(Bucket='listOfMovieDicts')