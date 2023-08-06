Board Game Stats
=================
Introduction
------------------
Board Game Stats (BGS) is a python wrapper around the boardgamegeek database_, meant to help developers access the stats information compiled by the boardgamegeek community_. These stats span across metrics like ranking, play-time, collection, etc.

As an avid board gamer myself, I was curious to start playing with this data and thought I'd share the wrapper with the boarder open source community. That being said, contributions are definitely accepted as well as feedback (shoot me an email at dnrkaseff360@gmail.com) on how I could make the package better.

Table of Contents
------------------
* Quick Start
* Supported Stats
* Future Goals
* Changelog

Quick Start
------------------
BGS starts by initializing a boardGame object with a required rank parameter. Once the object is initialized, all stat attributes and a compiled ``resultDict`` will be embedded in the object.

.. code-block:: python

    import boardGameStats as bgs

    gloomhaven = bgs.boardGame(1)
    gloomhaven.avgRating
    gloomhaven.resultDict

    print('Avg Rating: ' + gloomhaven.avgRating)
    print('Result Dict: ' + gloomhaven.resultDict)

>>> Avg Rating: 8.98599 
>>> {'gameName': 'Gloomhaven', 'avgRating': '8.98599', 'numRatings': '15987', 
'stdDev': '1.60769', 'numFans': 3493, 'pageViews': '6444515', 'overallRank': '1',
'allTimePlays': '101589', 'monthlyPlays': '5592', 'numOwned': '27334', 
'prevOwned': '641', 'forTrade': '112', 'wantTrade': '1277', 'wishList': '9855'}


Currently the package only supports querying by rank number, as reflected on boardgamegeek, as opposed to querying with a string (i.e. "Catan"). My plan is to add string query support as the next big release.

Supported Stats
------------------
* ``gameName``: name of initialized boardgame
* ``avgRating``: blended community rating (scale of 1 - 10)
* ``numRatings``: number of community submitted ratings
* ``stdDev``: standard deviation of the ``avgRating`` metric
* ``numFans``: number of community members self-identified as "fans"
* ``pageviews``: number of page views for initialized board game
* ``overallRank``: overall rank of board game compared to all other board game ratings in the database
* ``allTimePlays``: community self-confirmed all time plays
* ``monthlyPlays``: community self-confirmed plays in current month
* ``numOwned``: community self-confirmed **current** owners of the board game
* ``prevOwned``: community self-confirmed **previous** owners of the board game
* ``forTrade``: number of units up for trade by the community
* ``wantTrade``: number of units wanted in a trade by the community
* ``forTrade``: number of community members self-identifying game as part of their wishlist
* ``resultDict``: compiled stats for board game object, output as a dictionary

Future Goals
------------------
I'd like to continue developing this package to support two big pieces of functionality in the near future:

1) Query by Board Game Title
2) Batch Download of Database

The timeline is a bit hazy at the moment, since I'm currently going through MBA applications -- but I would like to have #1 done by end of July and #2 done by end of September.

Changelog
------------------
* 1.0.0: release!

.. _database: https://boardgamegeek.com/browse/boardgame
.. _community: https://boardgamegeek.com/
