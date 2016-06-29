# -*- coding: utf-8 -*-
import webapp2
from RouteMap import RouteMap
from RouteMap import ShortestRoute
from functools import reduce
import urllib2
import json
import google.appengine.api.urlfetch


#<p><img src="~/Pictures/3.png" alt="error"/></p>

#word-shuffle page
class MainPage(webapp2.RequestHandler):
    contents = u"""
        <h1>単語シャッフル</h1>
        <form action="/" method="post">
        <input type=text name="word1"><br>
        <input type=text name="word2"><br>
        <input type=submit value=Submit size=50>
        </form>
        """

    def get(self):
        self.response.write(self.contents)

    def post(self):
        w1 = self.request.get("word1")
        w2 = self.request.get("word2")
        shuffleResult = shift(w1,w2)
        self.response.write("""<h1>"""+ shuffleResult + """</h1>""" + self.contents)

def shift(w1, w2):
    result = ""
    for (x,y) in zip(w1,w2):
        result += (x+y)
    if len(w1) > len(w2):
        result += w1[len(w2):]
    elif len(w1) < len(w2):
        result += w2[len(w1):]
    return result



#route_tokyo webpage
class Transition(webapp2.RequestHandler):
    frontPage = open('''transitionFrontPage.html''', 'r')
    contents = frontPage.read()
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(self.contents)

    def post(self):
        start = self.request.get('station1')
        print (start.encode('utf-8'))
        end = self.request.get('station2')
        print (end.encode('utf-8'))
        option = self.request.get('priority')
        print (option.encode('utf-8'))
        urlMap = u'http://tokyo.fantasy-transit.appspot.com/net?format=json'
        urlOutage = u'http://fantasy-transit.appspot.com/outtages?format=json'
        urlTimetable= u'http://tokyo.fantasy-transit.appspot.com/schedules?format=json'
        response = urllib2.urlopen(urlMap)
        data = json.loads(response.read())
        map = RouteMap(data)
        newMap, outageInfo = map.outage(urlOutage)
        outputOutage = u"<h2></h2><h3>遅延が発生している区間:<br>"+outageInfo+"</h3><br>"

        if option == u"stationNumber":
            route = map.searchShortestRoute(start, end)
            totalStationNumber = len(route)
            outputStationNumber = ""
            for stop in route[:-1]:
                outputStationNumber += (stop+"->")
            outputStationNumber += route[-1]

        elif option == u"fastest":
            outputFastest = map.searchTimeSavingRoute(start, end, urlOutage, urlTimetable)

        if option == u'fastest':
            self.response.write(outputOutage.encode('utf-8')+outputFastest.encode('utf-8')+
            self.contents)
        elif option== u"stationNumber":
            self.response.write(outputOutage.encode('utf-8')+u"<h2></h2><h3>最少駅数:{0}".format(totalStationNumber).encode('utf-8')+
            "<br>"+outputStationNumber.encode('utf-8')+self.contents)
_URLS = [('/', MainPage),('/route_tokyo', Transition)]
app = webapp2.WSGIApplication(_URLS, debug=True)
