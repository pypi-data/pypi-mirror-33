import requests
from lxml import html
import decimal
import json

class boardGame(object):

	def __init__(self, rank=None):
		errorMessage = 'Rank variable passed is not an integer (ex. 1, 2, 3, 4...)'
		if not rank:
			raise ValueError(errorMessage)
		self.rank = rank
		self.resultDict = self.fetchByRank(rank)

	def fetchByRank(self, rank):
		boardGamePage = self.frontEndExec(rank)
		resultDict = self.backEndExec(boardGamePage)

		return resultDict

	def backEndExec(self, requestObject):
		treeStructure = html.fromstring(requestObject.content)
		
		resultDict = self.createDict(treeStructure)
		finalDict = self.pullMetrics(resultDict)
		
		return finalDict

	def pullMetrics(self, resultDict):
		self.avgRating = resultDict['stats']['average']
		self.numRatings = resultDict['stats']['usersrated']
		self.stdDev = resultDict['stats']['stddev']
		self.numFans = resultDict['stats']['numfans']
		self.pageViews = resultDict['stats']['views']
		self.allTimePlays = resultDict['stats']['numplays']
		self.monthlyPlays = resultDict['stats']['numplays_month']
		self.numOwned = resultDict['stats']['numowned']
		self.prevOwned = resultDict['stats']['numprevowned']
		self.forTrade = resultDict['stats']['numtrading']
		self.wantTrade = resultDict['stats']['numwanting']
		self.wishList = resultDict['stats']['numwish']

		self.overallRank = resultDict['rankinfo'][0]['rank']

		finalDict = {
			'gameName': self.gameName,
			'avgRating': self.avgRating,
			'numRatings': self.numRatings,
			'stdDev': self.stdDev,
			'numFans': self.numFans,
			'pageViews': self.pageViews,
			'overallRank': self.overallRank,
			'allTimePlays': self.allTimePlays,
			'monthlyPlays': self.monthlyPlays,
			'numOwned': self.numOwned,
			'prevOwned': self.prevOwned,
			'forTrade': self.forTrade,
			'wantTrade': self.wantTrade,
			'wishList': self.wishList
		}

		return finalDict

	def createDict(self, treeStructure):
		xPath = '//script/text()'
		begString = '"subtypename":"Board Game"'
		endString = '"label":'

		lxmlObj = treeStructure.xpath(xPath)
		rawJson = lxmlObj[0]
		strJson = str(rawJson)

		begCut = strJson.find(begString)
		endCut = strJson.find(endString) - 1

		cutStr = rawJson[begCut:endCut]
		enclosedStr = '{' + cutStr + '}'
		resultDict = json.loads(enclosedStr)

		return resultDict

	def frontEndExec(self, rank):
		xPathRank = '//td[@class="collection_rank"]//a/@name'
		xPathLink = '//div[@style="z-index:1000;"]//a/@href'
		xPathName = '//div[@id="results_objectname1"]//a/text()'

		pageNum = self.returnPageNum(rank)
		requestObject = self.basicReq(pageNum)

		rankList = self.listItems(requestObject, xPathRank)
		linkList = self.listItems(requestObject, xPathLink)
		nameList = self.listItems(requestObject, xPathName)

		self.gameName = nameList[0]

		boardGamePage = self.pullPage(rank, rankList, linkList)

		return boardGamePage

		
	def returnPageNum(self, rank):
		rawRank = rank / 100
		roundedRank = decimal.Decimal(rawRank).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_CEILING)

		return roundedRank

	def basicReq(self, pageNum):
		baseURL = 'https://boardgamegeek.com/browse/boardgame'
		pageParam = '/page/'
		pageNumStr = str(pageNum)
		errorMessage = 'Page not retrieved since page is non-existent or server error'

		combinedURL = baseURL + pageParam + pageNumStr
		requestObject = requests.get(combinedURL)

		return requestObject

	def listItems(self, requestObject, xPathString):
		dummyList = []
		treeStructure = html.fromstring(requestObject.content)

		dummyBuffer = treeStructure.xpath(xPathString)
		dummyList.extend(dummyBuffer)

		return dummyList

	def pullPage(self, rank, rankList, linkList):
		baseURL = 'https://boardgamegeek.com/'
		statsParam = '/stats'
		strRank = str(rank)

		indexValue = rankList.index(strRank)
		selectLink = linkList[indexValue]

		combinedURL = baseURL + selectLink + statsParam
		requestObject = requests.get(combinedURL)

		return requestObject
