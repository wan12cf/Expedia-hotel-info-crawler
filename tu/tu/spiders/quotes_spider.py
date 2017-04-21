import scrapy
import time
# import sys
from tu.items import TuItem
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def start_requests(self):
        self.driver = webdriver.Firefox()
        yield scrapy.Request('http://www.expedia.com', callback=self.parse)

    def parse(self, response):
        self.driver.get(response.url)

        # --------------------config area--------------------#
        # specify city(area), checkin/out date, hotel star
        #destInput = "Los Angeles"
        #destInput = "San Francisco"
        destInput = "New York"
        checkInDateInput = "04/21/2017"
        checkOutDateInput = "04/22/2017"
        # Tip: set "345" to crawl 3/4/5 class, or just one "4" for 4 class only
        # for some unknown reason, expedia may not show 1 and 2 star filter for clickble
        # besides, if you choose 3 then 5, 4 will also be choosed and non-cancellable
        # set to 0 to not use any filter.
        hotelstar = "0"

        # set 1 to choose 1 adult for search, set 0 to use default 2 adults.
        oneP = 0

        # if it is a sponsored result, set 1 to save as usual(may cause duplicate later), set 0 to drop this result.        
        sponsorAval = 0

        # if zipcode info is unknown, set 1 to save it as 'null', set 0 to drop this hotel
        hasZip = 1

        # if size info is unknown, set 1 to save it as 'null', set 0 to drop this room info row
        # about 10%-35%(vary) result items is null, blame expedia        
        sizeUnknow = 0

        # size can be 0 or ?, set 1 to save as 0, set 0 to drop this room info row
        # Note2: in very rare condition, size may be 0
        sizeBezero = 0

        # if size like"275-350", set 0 to save as 275, set 1 to save as 312, set 2 save as "275-350" 
        # Note: items like this about 2%
        sizeAvg = 0

        # if rating info is unknown, set 1 to save it as 'null', set 0 to drop this hotel
        # Note: no rating is a rare condition
        ratingUnknow = 0

        # if bed info is unknown, set 1 to save it as 'null', set 0 to drop this room info row
        # Note: no bed info is a very rare condition
        bedUnknow = 1

        # if guests info is unknown, set 1 to save it as 'null', set 0 to drop this room info row
        # Note: no guests info is a very rare condition
        guestsUnknow = 1

        # --------------------below is the code--------------------#
        # get the start window handle
        mainwin = self.driver.current_window_handle

        # switch to hotel search container
        htBtn = self.driver.find_element_by_id('tab-hotel-tab-hp')
        htBtn.click()

        # get input objects
        dest = self.driver.find_element_by_id('hotel-destination-hp-hotel')
        checkInDate = self.driver.find_element_by_id('hotel-checkin-hp-hotel')
        checkOutDate = self.driver.find_element_by_id('hotel-checkout-hp-hotel')
        searchButton = self.driver.find_element_by_xpath(".//*[@id='gcw-hotel-form-hp-hotel']/div[7]/label/button")
        people = self.driver.find_element_by_xpath(".//*[@id='gcw-hotel-form-hp-hotel']/div[3]/div[4]/label/select/option[@value='1']")

        # clear and write value to input objects
        dest.clear()
        dest.send_keys(destInput)
        checkInDate.clear()
        checkInDate.send_keys(checkInDateInput)
        checkOutDate.clear()
        checkOutDate.send_keys(checkOutDateInput)
        if (int(oneP) == 1):
            people.click()
        time.sleep(2)
        
        # starting search
        searchButton.click()
        
        def killwin(mainWinHandle):           
            # wait for loading and get all window handles
            time.sleep(2)
            allwin = self.driver.window_handles

            # kill popup windows that is not what we want
            for win in allwin:
                if win != mainWinHandle:
                    self.driver.switch_to_window(win)
                    self.driver.close()
                    print win," is closed."                     
            # get back to main window and prepare to work        
            self.driver.switch_to_window(mainWinHandle)
            print "backed to the main window"
            #time.sleep(4)

        killwin(mainwin)

        def starFilter (stars):        
            # get the property class container
            starxpath = ".//*[@id='star"+stars+"']"
            element = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, starxpath))
            )
            # locate the star element
            time.sleep(2)       
            star = self.driver.find_element_by_xpath(starxpath)
            star.click()
            # read total results number before click filter
            sel = scrapy.Selector(text = self.driver.page_source)
            paginginfo = sel.xpath(".//*[@id='paginationContainer']/nav/fieldset/p/text()").extract_first().strip()

            # wait for the filtered results
            print "wait for loading filtered results..."
            while (str(sel.xpath(".//*[@id='paginationContainer']/nav/fieldset/p/text()").extract_first().strip()) == paginginfo):                    
                print "still wait for loading filtered results..."
                time.sleep(1)
                sel = scrapy.Selector(text = self.driver.page_source)
            print "filtered results load completed."

        if (hotelstar == '0'):
            element = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, ".//*[@id='resultsContainer']/section/article[1]"))
            )
            time.sleep(2)
        else:
            for star in range(0,len(hotelstar)):
                starFilter(hotelstar[(star):(star+1)])

        #time.sleep(8)
        # element = WebDriverWait(self.driver, 30).until(
        #     EC.element_to_be_clickable((By.XPATH, starxpath))
        # )
        # element = WebDriverWait(self.driver, 10).until(
        #     EC.presence_of_element_located((By.XPATH, ".//*[@id='paginationContainer']/nav/fieldset/div/button[@class='pagination-next']/abbr"))
        # )

        sel = scrapy.Selector(text = self.driver.page_source)
        
        # get result number,page number by extract the property value in the tag <nav>
        totalres = int(sel.xpath(".//*[@id='paginationContainer']/nav/@data-total-results").extract_first())
        resperpage = int(sel.xpath(".//*[@id='paginationContainer']/nav/@data-per-page").extract_first())
        firstResNum = int(sel.xpath(".//*[@id='paginationContainer']/nav/@data-first-result").extract_first())
        if (int(totalres) <= int(resperpage)):
            totalpage = 1
        else:
            totalpage = int(totalres/resperpage)+1    
        print "total page is: ",totalpage
        time.sleep(4)
        

        # initialize counter
        openedPage = 0
        openingPage = 0

        for pagenum in range(1, (totalpage+1)):
        #for pagenum in range(1, 2):
            killwin(mainwin)
            print "start page loading........."
            time.sleep(1)
            sel = scrapy.Selector(text = self.driver.page_source)            
            # make sure the page load is completed by checking "nav/@data-first-result" value
            
            resultwait = 100
            while (sel.xpath(".//*[@id='paginationContainer']/nav/@data-first-result").extract_first() != str(firstResNum)):                    
                print "still wait for loading..."
                time.sleep(1)
                resultwait += 1
                if (resultwait > 130):
                    self.driver.refresh()
                    resultwait = 0
                if (resultwait == 30):
                    print "load failed, current pagenum is: ", pagenum
                    self.driver.quit()
                sel = scrapy.Selector(text = self.driver.page_source)
                if (sel.xpath(".//*[@id='errorMsg']").extract_first() is not None):
                    self.driver.refresh()
                    resultwait = 0
            print "load complete, current pagenum is: ", pagenum

            firstResNum += resperpage
            #print "current first result number: ", firstResNum

            #load the page context           
            sel = scrapy.Selector(text = self.driver.page_source)
            hotels = sel.xpath(".//*[@id='resultsContainer']/section/article")
            
            # def hotelmodelPresave(htName,htZone,lowestPrice,htLink,sponsored):
            #     hotelmodel = TuItem()
            #     hotelmodel["name"] = htName.strip()
            #     hotelmodel["zone"] = htZone.strip
            #     hotelmodel["price"] = lowestPrice.strip()[1:]
            #     hotelmodel["link"] = htLink.strip()
            #     if (sponsored == 'sponsored'):
            #         hotelmodel["name"] += ' sponsored'
            #     yield hotelmodel

            # open links in the hotels list
            #while (False): # use this line to disable save hotel function, left click 'Next' only
            for hotel in hotels:

                htName = hotel.xpath("div[2]/div/div[1]/div[2]/ul[1]/li[@class='hotelTitle']/h4/text()").extract_first().strip()
                htZone = hotel.xpath("div[2]/div/div[1]/div[2]/ul[1]/li[@class='neighborhood secondary']/text()").extract_first().strip()
                #htRating = hotel.xpath("div[2]/div[1]/div[1]/div[@class='flex-area-secondary']/div/div[@class='price-col-1']/ul[@class='hotel-ugc']/li[@class='reviewOverall']/span[2]/text()").extract_first().strip()
                #htRates = hotel.xpath("div[2]/div[1]/div[1]/div[@class='flex-area-secondary']/div/div[@class='price-col-1']/ul[@class='hotel-ugc']/li[@class='reviewCount fakeLink secondary']/span[2]/text()").extract_first().strip()
                lowestPrice =  hotel.xpath("div[2]/div/div[1]/div[3]/div/div[@class='price-col-1']/ul[@class='hotel-price']/li[@data-automation='actual-price']/text()").extract_first()
                
                if (lowestPrice is None):
                    #print "sold out detected! ",htName
                    continue
                    #self.driver.quit()
                htLink = hotel.xpath("div[2]/div[@class='flex-link-wrap']/a[@class='flex-link']/@href").extract_first()
                

                # version 1 of checking sponsor, by extract value in the tag<article>
                # I have found 3 type of status: organic, sponsored, dealofday
                sponsorChk = hotel.xpath("@data-automation").extract_first().strip()
                #print "sponsorChk status is:",sponsorChk
                
                #yield hotelmodelPresave(htName,htZone,lowestPrice,htLink,sponsorChk)

                if (sponsorChk == 'sponsored'):
                    #print "found sponsored hotel! ",htName
                    if (int(sponsorAval) ==  0):
                        continue                   


                # # version 2 of checking sponsor, by extract value under the tag<article>. Only sponsored has this <li>
                # sponsorChk = hotel.xpath("div[2]/div/div[1]/div[3]/div/div[@class='price-col-1']/ul[@class='hotel-price']/li[@class='sponsoredListing secondary']/text()").extract_first()
                # if (sponsorChk is not None):
                #     print "found sponsored hotel! ",htName
                #     continue



                js='window.open("'+htLink+'");'
                self.driver.execute_script(js)

                #print "now opening ",htName
                openingPage += 1
                openedPage += 1
                #time.sleep(2)
                # htwin[openingPage] = self.driver.current_window_handle
                # print "new window handle is: ",htwin[openingPage]
                
                def pageloadChk():                   
                    try:
                        element = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, ".//*[@id='lead-price-container']/div[@class='ajax-lead-price']/div[@class='price-per-night-wrapper']/a"))
                        )
                    except TimeoutException as e:
                        print "page load TimeoutException, refreshing in 2s..."
                        time.sleep(2)
                        self.driver.refresh()
                        return False                        
                    finally:
                        pass
                    return True

                # if price is not show up for 10s, refresh the page.
                def pageLoadwait():
                    if (pageloadChk() == False):
                        return pageloadChk()
                    else:
                        return True


                if ((openedPage > 0) and (openingPage == 1)):
                    print "total hotels saved: ",openedPage
                    print "wait for loading hotel page..."
                    #time.sleep(1)
                    allwin = self.driver.window_handles
                    for win in allwin:
                        if(win != mainwin):
                            self.driver.switch_to_window(win)

                            # if (pageLoadwait() == False):
                            #     if(pageLoadwait() == False):
                            #         print "hotel info is unavailable"
                            #         break
                            if (pageLoadwait() == False):
                                #print "hotel info is unavailable
                                break 

                            #time.sleep(2)
                            sel = scrapy.Selector(text = self.driver.page_source)
                            #htName = sel.xpath(".//*[@id='hotel-name']/text()").extract_first()
                            #htprice = sel.xpath(".//*[@id='lead-price-container']/div[@class='ajax-lead-price']/div[@class='price-per-night-wrapper']/a/text()").extract_first()
                            address = sel.xpath(".//*[@id='license-plate']/div[@class='address']/a/span[@class='street-address']/text()").extract_first()
                            star = sel.xpath(".//*[@id='license-plate']/div[@class='star-rating-wrapper']/strong/span[2]/@title").extract_first()
                            # select all rooms
                            rooms = sel.xpath(".//*[@id='rooms-and-rates']/div/article/table/tbody")

                            zipcode = sel.xpath(".//*[@id='policies-and-amenities']/div[@class='full-address-container']/div[@class='full-address']/a[@class='map-link']/span[@class='postal-code']/text()").extract_first()

                            if (zipcode is None):
                                print "couldn't find zipcode"
                                if (int(hasZip) == 1):
                                    zipcode = 'null'
                                else:
                                    continue
                            if (zipcode.strip() == ''):
                                print "zipcode is empty"
                                if (int(hasZip) == 1):
                                    zipcode = 'null'
                                else:
                                    continue

                            # version 1 to get rating, read from the top right of the page, near map
                            rating = sel.xpath(".//div[@class='guest-rating']/span[@class='rating-number']/text()").extract_first()
                            rates = sel.xpath(".//a[@class='reviews-link link-to-reviews']/span/text()").extract_first()
                            # if failed try another way, version 2
                            if (rating is None):
                                # step1 of version 2 to get rating, by click 'Guest Reviews' in the bottom of the page
                                # first check out if the button is visible
                                btnStyle = sel.xpath(".//*[@id='tabs']/ul/@style").extract_first()
                                if (btnStyle is None):
                                    print "button exsixt, prepare to click button"

                                    # click button
                                    reviewBtn = self.driver.find_element_by_xpath(".//*[@id='tab-reviews']")
                                    reviewBtn.click()

                                    # wait loading reviews
                                    try:
                                        element = WebDriverWait(self.driver, 10).until(
                                            EC.presence_of_element_located((By.XPATH, ".//*[@id='review-summary']/section"))
                                        )
                                    except TimeoutException as e:
                                        print "reviews loading failed, drop hotel"
                                        continue
                                    finally:
                                        pass

                                    # step2 of version 2 to get rating
                                    sel = scrapy.Selector(text = self.driver.page_source)
                                    rating = sel.xpath(".//*[@id='review-summary']/section/div[@class='rating-and-satisfaction']/div[1]/div[1]/span/text()").extract_first()
                                    rates = sel.xpath(".//*[@id='reviews-pagination']/fieldset/p/text()").extract_first()

                                else:
                                    if (str(btnStyle.strip()) == 'display: none;'):
                                        print "found the invisible button, no reviews available"
                                        rating = None
                                        time.sleep(2)

                            # process when rating is unavailable
                            if (rating is None):
                                if (int(ratingUnknow) == 1):
                                    rating = 'null'
                                    rates = 'null'
                                else:
                                    continue

                            for r in rooms:
                                hotelmodel = TuItem()
                                room = r.xpath("tr/td[@class='room-info']/div[@class='room-basic-info']/h3/text()").extract_first()
                                if (room is None):
                                    continue
                                #size = r.xpath("tr/td[@class='room-info']/div[@class='room-basic-info']/span[@class='square-area']/text()").extract_first()                               
                                size = r.xpath("tr/td[@class='room-info']/div[@class='room-basic-info']/span[@class='square-area']/text()").extract_first()
                                if (size is None):
                                    #print "size is None!"
                                    if (int(sizeUnknow) == 1):
                                        size = 'null'
                                    else:
                                        continue
                                        #self.driver.quit()
                                if (size.strip() == ''):
                                    #print "size is empty!"
                                    if (int(sizeUnknow) == 1):
                                        size = 'null'
                                    else:
                                        continue
                                        #self.driver.quit()
                                else:
                                    size = (str(size.strip()))[:-12]
                                    if (len(size)>4):
                                        print "long size detected!", size
                                        bit = int((len(size))/2)
                                        if (int(sizeAvg) == 0):                                           
                                            size = size[0:bit]
                                        if (int(sizeAvg) == 1):
                                            size = int(size[:(bit*-1)]) + int(size[0:bit])
                                            size /= 2
                                        if (int(sizeAvg) == 2):
                                            print "long size save as original", size            
                                    else:
                                        if (size == '?'):
                                            size = 0
                                        if (str(size) == '0'):
                                            print "zero 0 size detected!", size
                                            if(int(sizeBezero) == 0):
                                                continue

                                guests = r.xpath("tr/td[@class='room-info']/div[@class='room-basic-info']/p[@class='max-occupancy-text']/span[@class='max-guest-msg']/text()").extract_first()
                                if (guests is None or guests == ''):
                                    if (int(guestsUnknow) == 1):
                                        guests = 'null'
                                    else:
                                        continue
                                else:
                                    guests = guests.strip()
                                    if (len(guests) > 16):
                                        guests = (guests.strip()[12:])[:-7] 
                                    else:
                                        guests = (guests.strip()[7:])[:-7] 
                                
                                #bed = r.xpath("tr/td[1]/div[2]/div[1]/text()").extract_first()  
                                bed = r.xpath("tr/td[@class='room-info']/div[@class='room-basic-info']/div[1]/text()").extract_first()
                                # if (bed is None):
                                #     if (bedUnknow == 1):
                                #         bed = 'null'
                                #     if(bedUnknow == 0):
                                #         continue 
                                if (bed is None or bed == ''):
                                    if (int(bedUnknow) == 1):
                                        bed = 'null'
                                    else:
                                        continue
                                else:
                                    bed = (bed.strip()).replace("\n", "")

                                #roomprice = r.xpath("tr/td[@class='avg-rate']/div/div[@class='room-price-info-wrapper']/div[@class='price-wrapper one-night-room-price']/span[2]/text()").extract()
                                roomprice = r.xpath("tr/td[@class='avg-rate']/div/div[@class='room-price-info-wrapper']/div[1]/span[2]/text()").extract()
                                # yield result
                                for rp in roomprice:
                                    rp = rp.strip()
                                    # if (rp is None):
                                    #     rp = 'sold out'
                                    hotelmodel["guests"] = guests
                                    hotelmodel["name"] = htName
                                    #hotelmodel["lowestPrice"] = htprice[1:]
                                    hotelmodel["price"] = rp.strip()[1:]
                                    hotelmodel["room"] = room.strip()
                                    hotelmodel["size"] = size
                                    hotelmodel["star"] = star
                                    hotelmodel["address"] = address
                                    hotelmodel["zone"] = htZone
                                    hotelmodel["bed"] = bed
                                    hotelmodel["rating"] = rating.strip()
                                    hotelmodel["rates"] = rates.strip()
                                    hotelmodel["link"] = htLink
                                    hotelmodel["checkin"] = checkInDateInput
                                    hotelmodel["checkout"] = checkOutDateInput
                                    hotelmodel["zipcode"] = zipcode.strip()
                                    yield hotelmodel
                                    #print "room saved: ",room," price: ",rp.strip()
                            #print htName, " completed."
                            print "total hotels saved: ",openedPage                            
                    openingPage = 0
                    self.driver.close()
                    #mainwin = self.driver.current_window_handle
                    self.driver.switch_to_window(mainwin)
                    #killwin(mainwin)
                    # if (openedPage == 10):
                    #     self.driver.quit()

            # click next button
            if (pagenum < totalpage):
                print "preparing to click next page, pagenum: ", pagenum," total hotel saved: ",openedPage
                time.sleep(1)
                nbutton = self.driver.find_element_by_xpath(".//*[@id='paginationContainer']/nav/fieldset/div/button[@class='pagination-next']/abbr")
                nbutton.click()
            else:
                print "total page crawled: ", pagenum," total hotel saved: ",openedPage
                self.driver.quit()