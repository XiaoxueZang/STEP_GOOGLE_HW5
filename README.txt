# STEP_GOOGLE_HW5 
STEP HOMEWORK 5: Xiaoxue Zang1.	Simple explanation of class RouteMap:def drawMap: Method to generate train map.def searchTimeSavingRoute: Method to search for the fastest route.def searchArriveTime: Given the start station, end station and current time, return the depart time and arrive time of each station.def outage:Generate the information of outages.def forDisplay:Method to interpret the result of method [searchTimeSavingRoute] to make the result easy to display.2.	Explanation of def ShortestRoute(route, nodes, start, end):This function returns the shortest route between 2 points. What shortest route means here is the route with the least number of stations between 2 stations. This function is initially used to search for the delays given the information of outages. However, I found that the outage information only contains 2 adjacent stations, which makes this function redundant, so I use this function to calculate the route with the least station numbers between 2 stations (最少駅数) regardless of the outages.3.	How I define出発時刻　到着時刻 in my code:For example: 上野→御徒町　山手線(UP)I found that the current time is 6:45, so the departure time in 上野 station should be 6:54 according to the time table linkage http://tokyo.fantasy-transit.appspot.com/schedules?station=%E4%B8%8A%E9%87%8EI then check the time table of 御徒町(山手線UP) http://tokyo.fantasy-transit.appspot.com/schedules?station=%E5%BE%A1%E5%BE%92%E7%94%BAI found that the time of departure that is the most close to 6:54 is 6:57, and I set 6:57 to be the arrival time of 御徒町. I think that one train arrives at one station and leave soon. Thus, the final arrival time is usually 1 minute or 2 minutes late than the answer given by Kris’s webpage. I think that Kris considers possible stop time for a train to stop in one station. 


P.S. the dictionary that I use for finding the route.
key: the start station, value: the stations that it connects with
{'三ノ輪': {'日比谷線': ['入谷', '南千住']},
 '上野': {'山手線': ['鶯谷', '御徒町'], '日比谷線': ['仲御徒町', '入谷']},
 '上野毛': {'大井町線': ['二子玉川', '等々力']},
 '下丸子': {'多摩川線': ['鵜の木', '武蔵新田']},
 '下神明': {'大井町線': ['戸越公園', '大井町’]},......}
