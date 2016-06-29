# -*- coding: utf-8 -*-
import urllib2
import json
import copy
import datetime
from pytz import timezone

class RouteMap:
    def __init__(self, data):
        self.stations = []
        self.StationConnection = {}
        self.drawMap(data)
        self.timeTable = {}

    def searchShortestRoute(self, start, end):
        return ShortestRoute(self.StationConnection, self.stations, start, end)

    def outage(self, url):
        response = urllib2.urlopen(url)
        data = json.loads(response.read())
        newMap = copy.deepcopy(self.StationConnection)
        outageInfo = []
        for outage in data:
            brokenStart = outage[u'From']
            brokenEnd = outage[u'To']
            brokenLine = self.searchShortestRoute(brokenStart, brokenEnd)
            outageInfo.append("->".join(brokenLine))
            for (i,station) in enumerate(brokenLine):
                preStation = brokenLine[i-1] if i>0 else None
                nextStation = brokenLine[i+1] if i<(len(brokenLine)-1) else None
                for line in newMap[station].keys():
                    for i,linkStation in enumerate(newMap[station][line]):
                        if linkStation == nextStation:
                            newMap[station][line][i]=None
        return newMap, "     ".join(outageInfo)

    def searchTimeSavingRoute(self, startStation, endStation, urlOutage, urlTimetable):
        response = urllib2.urlopen(urlTimetable)
        data = json.loads(response.read())
        self.timeTable = data[u'Schedules']
        #the group of stations that has not been reached
        stationTimeNotDetermined = {}
        #the group of stations that has been reached
        stationTimeDetermined = {}
        stationPre = {}
        finalRoute = []
        #stack to store the stations that has been reached
        determinedStationStack = [startStation]
        for station in self.stations:
            if station is not startStation:
                stationTimeNotDetermined[station] = datetime.time(23,59)
        tzinfo = timezone("Japan")
        startTime = datetime.datetime.now(tzinfo).time()
        stationTimeDetermined[startStation] = {'arriveTime': None, 'departTime': {}}
        stationTimeDetermined[startStation]['arriveTime'] = startTime
        newMap, outInfo = self.outage(urlOutage)
        #while the destination has not been reached
        while endStation not in stationTimeDetermined.keys():
            currentStation = determinedStationStack[-1]
            startTime = stationTimeDetermined[currentStation]['arriveTime']

            for (line, StationInfo) in newMap[currentStation].items():
                for (i,nextStation) in enumerate(StationInfo):
                    if nextStation not in stationTimeDetermined.keys():
                        if not nextStation:
                            continue
                        if len(newMap[currentStation][line])==1:# for debugging
                            print("error")
                            sys.exit(1)
                        elif i==0:
                            direction = -1# means direction is down
                        elif i==1:
                            direction = 1# means direction is up

                        departTime, arriveTime = self.searchArriveTime(currentStation, nextStation, line, direction, startTime)
                        if arriveTime==None:#arrive time could be None, when next Station is the end station of some line
                            #when arrive Time is None, I set this time to be 5 minutes later than the departure time of the previous station.
                            arriveTime = (datetime.datetime.combine(datetime.datetime.now().date(),departTime) + datetime.timedelta(minutes = 5)).time()
                        if departTime == None:# for debugging, departTime is never None
                            print(currentStation, nextStation, startTime, direction, line)
                            sys.exit(1)
                        if  line in stationTimeDetermined[currentStation]['departTime'].keys():
                            stationTimeDetermined[currentStation]['departTime'][line].append(departTime)
                        else: stationTimeDetermined[currentStation]['departTime'][line] = [departTime]

                        if stationTimeNotDetermined[nextStation]>arriveTime:
                            #do the refresh
                            stationTimeNotDetermined[nextStation] = arriveTime
                            stationPre[nextStation] = [currentStation, line]
            #pick out the next station to go
            stationToDetermine = sorted(stationTimeNotDetermined.items(), key = lambda x: x[1])[0][0]
            stationTimeDetermined[stationToDetermine] = {'arriveTime': None, 'departTime': {}}
            stationTimeDetermined[stationToDetermine]['arriveTime'] = stationTimeNotDetermined[stationToDetermine]
            del stationTimeNotDetermined[stationToDetermine]
            determinedStationStack.append(stationToDetermine)
        finalRoute = [[endStation]]
        now = endStation
        time = []
        #find out the final route and the arriving time of each station
        while (now != startStation):
            finalRoute.append(stationPre[now])
            line = stationPre[now][1]
            time.append(stationTimeDetermined[now]['arriveTime'])
            now = stationPre[now][0]

        time.append(stationTimeDetermined[startStation]['arriveTime'])
        finalRoute.reverse()
        time.reverse()
        return self.forDisplay(finalRoute, time)

    def searchArriveTime(self,currentStation, nextStation, line, direction, startTime):
        found = False # use flags to break out from the deeply-nested loop
        setTime = datetime.datetime.combine(datetime.datetime.now().date(),startTime)
        day = 0
        while found==False:
            for info in self.timeTable:
                if found: break
                if info['Station'] == currentStation and (info['LineId']['Direction']==direction)and (line == info['LineId']['Line']['Name'] ):
                    for time in info['Rows']:
                        if found: break
                        if (time['Hour']+day*24) < startTime.hour:
                            continue
                        for minute in time['Mins']:
                            whichday = datetime.datetime.today().date() + datetime.timedelta(days = day)
                            if (datetime.datetime.combine(whichday, datetime.time(time['Hour'] , minute)))>=setTime:
                                departTime = datetime.time(time['Hour'], minute)
                                found = True
                                break
            day += 1
        #for debugging
        if found==False:
            print("start")
            print(currentStation, nextStation, startTime)
            sys.exit(1)
        for info in self.timeTable:
            if info['Station'] == nextStation and (info['LineId']['Direction']==direction) and (line == info['LineId']['Line']['Name'] ):
                for time in info['Rows']:
                    if time['Hour'] < departTime.hour:
                        continue
                    for minute in time['Mins']:
                        if (datetime.time(time['Hour'], minute))>=departTime:
                            arriveTime = datetime.time(time['Hour'], minute)
                            return departTime, arriveTime
        return departTime, None

    def drawMap(self, data):
        for trainLine in data:
            lineLength = len(trainLine[u'Stations'])
            lineName = trainLine[u'Name']

            for (i, station) in enumerate(trainLine[u'Stations']):
                if (station not in self.StationConnection.keys()) and (i != 0) and (i != (lineLength - 1)):
                    self.StationConnection[station] = {
                        lineName: [trainLine[u'Stations'][i - 1], trainLine[u'Stations'][i + 1]]}
                elif (station in self.StationConnection.keys()) and (i != 0) and (i != (lineLength - 1)):
                    self.StationConnection[station].update(
                        {lineName: [trainLine[u'Stations'][i - 1], trainLine[u'Stations'][i + 1]]})
                elif (i is 0) and station not in self.StationConnection.keys():
                    self.StationConnection[station] = {lineName: [None, trainLine[u'Stations'][1]]}
                elif (i is (lineLength - 1)) and station not in self.StationConnection.keys():
                    self.StationConnection[station] = {lineName: [trainLine[u'Stations'][i - 1], None]}
                elif (i is 0) and station in self.StationConnection.keys():
                    self.StationConnection[station].update({lineName: [None, trainLine[u'Stations'][1]]})
                elif (i is (lineLength - 1)) and station in self.StationConnection.keys():
                    if lineName in self.StationConnection[station].keys():
                        self.StationConnection[station][lineName][0] = trainLine[u'Stations'][i - 1]##########Shinagawa
                    else:
                        self.StationConnection[station].update({lineName: [trainLine[u'Stations'][i - 1], None]})
        self.stations = self.StationConnection.keys()

    def forDisplay(self, finalRoute, time):
        result = u"""<h2></h2><h3>最短経路:<br>"""
        result += u"<h3>現在時間： "+time[0].strftime("%H:%M")+"<br>"
        #result += u"始発駅の出発時刻: " + time[1].strftime("%H:%M") + u"<br>"
        result += u"終着駅の到着時刻: " + time[-1].strftime("%H:%M") + u"<br>"
        tran = ""
        for i,station in enumerate(finalRoute):
            if i==0:
                tran += u"{:<20}".format(station[0])+u"----"+u"{:<20}".format(station[1])+u"で---->"
            elif i==len(finalRoute)-1:
                tran += u"{:<20}".format(station[0])+u"(到着："+time[i].strftime("%H:%M")+u")"
            else:
                tran += u"{:<20}".format(station[0])+u"(到着：" + time[i].strftime("%H:%M")+ u")<br>"+u"{:<20}".format(station[0])+"----"+u"{:50}".format(station[1])+u"で---->"
        result += "<h3>" + tran + "</h3><br>"
        return result

#Bellman-ford
def ShortestRoute(route, nodes, start, end):
    nodeList = {}
    nodePre = {}
    finalRoute = [end]
    for x in nodes:
        nodeList[x] = float("inf")
    nodeList[start] = 0
    for i in range(len(nodes)):
        for node in nodes:
            for nextNode in set(reduce(lambda c, x: c + x, [x for x in route[node].values()], [])):
                if nextNode is None:
                    continue
                if nodeList[node] + 1 < nodeList[nextNode]:
                    nodeList[nextNode] = nodeList[node] + 1
                    nodePre[nextNode] = node
    previous = end
    while (previous != start):
        finalRoute.append(nodePre[previous])
        previous = nodePre[previous]
    finalRoute.reverse()
    return finalRoute
