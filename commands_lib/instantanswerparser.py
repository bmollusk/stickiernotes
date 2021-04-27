from bs4 import BeautifulSoup
import requests
import time

#basically if a function can stay unreplaced for a while, it'll run
#essentially make a thing where if a function is not called again in a certain period of time then the actual function/query runs
#perhaps after every function call set a timer and whenever the function is called again reset the timer, once the timer is set to 0 then return request
#however issue is that the actual command requesting is done within a larger block which has to be run in the main gui
#so perhaps make it so that the main gui can continue and come back for the necessary output??

#bruh just make it so that it returns whatevers been cached if the query is
#have a cache that the query function just accesses

#have an event filter that lists all the upcoming keyboard press events
# awaittime = 100
# currentwait = awaittime
# timer = None
# if timer stopped:
#     timer.start()
# else:
#     timer.reset()

#NEED TO FIND A WAY TO SEE QUEUED UP signals literally it'd just be if queued up signals == 0  then run query


def query(q):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}
    resp = requests.get(f'https://www.google.com/search?q={q}', headers=headers)
    soup = BeautifulSoup(resp.text, 'lxml')
    result = soup.find('div', class_='Z0LcW')
    return result.text
