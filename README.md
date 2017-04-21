# Requirements
python，scrapy，selenium，geckodriver，firefox

# How to:
\tu> scrapy crawl quotes -o filename.csv
not including sold out hotel

# Change csv column order
Locate to \tu\tu，find settings.py
in 'FEED_EXPORT_FIELDS'

# change target city/date
open tu/spiders/quotes_spider.py
	
modify：

    # specify city(area), checkin/out date, hotel star
    destInput = "New York"
    checkInDateInput = "04/20/2017"
    checkOutDateInput = "04/21/2017"
    # Tip: set "345" to crawl 3/4/5 class, or just one "4" for 4 class only
    # for some unknown reason, expedia may not show 1 and 2 star filter for clickble
    # besides, if you choose 3 then 5, 4 will also be choosed and non-cancellable        
    # set to 0 to not use any filter.
    hotelstar = "0"

	一些属性的说明：
	hotelstar用来过滤酒店星级，0不勾选任何过滤，'345'/'35'都会选中345星。

	在起始页面指定搜索1个人，默认是2人
        # set 1 to choose 1 adult for search, set 0 to use default 2 adults.
        oneP = 0

        每页的前2个和后2个结果通常会出现sponsored酒店，这些酒店可能会重复出现，就导致了一个酒店爬了2次或更多。
	设为 0 可以保证当sponsored标签出现时，不读取该酒店的内容。
	# if it is a sponsored result, set 1 to save as usual(may cause duplicate later), set 0 to drop this result.        
        sponsorAval = 0

	在酒店的选择房型页面中，有些并没有标示出面积，设为 0 就不会抓取此条房型信息
        # if size info is unknown, set 1 to save it as 'null', set 0 to drop this room info row
        # about 10%-35%(vary) result items is null, blame expedia        
        sizeUnknow = 0

	个别酒店的选择房型页面中，面积是0，设为 0 就不会抓取此条房型信息
        # size can be 0 in some very rare condition, set 1 to save as 0, set 0 to drop this room info row
        sizeBezero = 0

	如果房型面积是一个范围，如275-350，设0取最小，1取平均值，2不变
        # if size like"275-350", set 0 to save as 275, set 1 to save as 312.5, set 2 save as "275-350" 
        # Note: items like this less than 2%
        sizeAvg = 0
	
	一些新酒店没有评价信息，当出现这样的酒店时，设为 0  就不会抓取
        # if rating info is unknown, set 1 to save it as 'null', set 0 to drop this hotel
        # Note: no rating is a very rare condition
        ratingUnknow = 0

        # if bed info is unknown, set 1 to save it as 'null', set 0 to drop this room info row
        # Note: no bed info is a very rare condition
        bedUnknow = 1

        # if guests info is unknown, set 1 to save it as 'null', set 0 to drop this room info row
        # Note: no guests info is a very rare condition
        guestsUnknow = 1
