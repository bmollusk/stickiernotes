from bs4 import BeautifulSoup
from PyQt5.QtNetwork import QNetworkRequest
from PyQt5.QtCore import QUrl, QObject
import urllib
import time

# basically if a function can stay unreplaced for a while, it'll run
# essentially make a thing where if a function is not called again in a certain period of time then the actual function/query runs
# perhaps after every function call set a timer and whenever the function is called again reset the timer, once the timer is set to 0 then return request
# however issue is that the actual command requesting is done within a larger block which has to be run in the main gui
# so perhaps make it so that the main gui can continue and come back for the necessary output??

# bruh just make it so that it returns whatevers been cached if the query is
# have a cache that the query function just accesses

# have an event filter that lists all the upcoming keyboard press events
# awaittime = 100
# currentwait = awaittime
# timer = None
# if timer stopped:
#     timer.start()
# else:
#     timer.reset()

# NEED TO FIND A WAY TO SEE QUEUED UP signals literally it'd just be if queued up signals == 0  then run query
connection = None


def query(self, q):
    global connection
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}
    q = urllib.parse.quote_plus(q)
    url = f'https://www.google.com/search?q={q}'

    request = QNetworkRequest(QUrl(url))
    request.setRawHeader(b'User-Agent', b'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36')
    connection = self.network.finished.connect(lambda reply: responsehandler(self, reply))
    self.network.get(request)


def responsehandler(self, resp):
    global connection
    QObject.disconnect(connection)

    soup = BeautifulSoup(str(resp.readAll(), 'utf8'), 'lxml')

    answertypes = {'instant': ['div.Z0LcW', 'text'], 'calc': ['span.qv3Wpe', 'text'], 'multiple': ['div.bVj5Zb', 'text'],
                   'translate': ['pre[id*="target-text"] span.Y2IQFc', 'text'], 'conversion': ['input.vXQmIe[jsname=fPLMtf]', 'value'],
                   'currency': ['span.DFlfde.SwHCTb', 'text'], 'graph': ['div.ayqGOc.kno-fb-ctx.KBXm4e', 'text'], 'stock':['span.IsqQVc.NprOob.XcVN5d.wT3VGc', 'text'],
                   'definition':['div[data-dobid=dfn] span', 'text']}

    text = None
    for answertype in answertypes.values():
        result = soup.select(answertype[0])
        if len(result)>0:
            result = result[0]
            if answertype[1] == 'text':
                text = result.text
            elif answertype[1] == 'value':
                text = result.attrs['value']
            else:
                text = "ANSWER NOT FOUND"
            break

    if text is None:
        self.commandfinished.emit("INVALID QUERY")
    else:
        self.commandfinished.emit(text)
