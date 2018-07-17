import time
import mysql.connector
import scrapy
from scrapy.spiders import CrawlSpider

def WritetoDB(countVariable, textVariable, titleVariable, authorVariable, categoryVariable, dateVariable, urlVariable):
    ''' MySQL Database : --------------------------------------------------------- '''
    '''                  | id | rawtext | title | author | category | date | url | '''
    '''                  --------------------------------------------------------- '''
    cnx = mysql.connector.connect(user='root', password='root', database='newsapp')
    cursor = cnx.cursor()
    cursor.execute('SET NAMES utf8mb4')  # Some symbols are in fact UTF8 4 Bit
    cursor.execute("SET CHARACTER SET utf8mb4")
    cursor.execute("SET character_set_connection=utf8mb4")
    query = ("INSERT INTO theguardian VALUES (%s, %s, %s, %s, %s, %s, %s)")
    cursor.execute(query, (countVariable, textVariable, titleVariable, authorVariable, categoryVariable, dateVariable, urlVariable))
    cnx.commit()
    
    cursor.close()
    cnx.close()    

def GetCountfromDB():  
    ''' Get number of articles in Database '''
    cnx = mysql.connector.connect(user='root', password='root', database='newsapp')
    cursor = cnx.cursor()
    query = ("SELECT id FROM theguardian")
    cursor.execute(query)    
    cursor.fetchall()   
    
    count = cursor.rowcount + 1
       
    cursor.close()
    cnx.close()
        
    return count

def GetLastDatefromDB():
    ''' Get date of last article in Database ''' 
    cnx = mysql.connector.connect(user='root', password='root', database='newsapp')
    cursor = cnx.cursor()
    query = ("SELECT DATE_FORMAT(date, '%Y/%m/%d') FROM theguardian ORDER BY date DESC")
    cursor.execute(query)    

    row = list(cursor.fetchall())  # Must have no Unread Results    
    
    cursor.close()
    cnx.close()
    
    if not row:  # No date Found
        return "1980/1/1"
    else:
        return "".join(row[0])  
    
class GuardianSpider(CrawlSpider):
    name = "theguardian"
    count = 0
    lastDate = "0"
    depth = 0
    allowed_domains = ['www.theguardian.com']
         
    def start_requests(self):
        self.count = GetCountfromDB() # Count
        print(GetCountfromDB()) 
        self.lastDate = GetLastDatefromDB() # Date
        print(GetLastDatefromDB())         
        self.depth = int(getattr(self, 'depth', None)) # Crawl Depth

        urls = [
            'https://www.theguardian.com/' + 'world/all',
            'https://www.theguardian.com/' + 'sport/all',
            'https://www.theguardian.com/' + 'politics/all',
            #'https://www.theguardian.com/' + 'culture/all',
            #'https://www.theguardian.com/' + 'commentisfree/all',
            #'https://www.theguardian.com/' + 'environment/all',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)   

    def parse(self, response):                
        # Check Current Page Date vs. Last Article in DB Date
        currentPageDate = [] 
        for y in range(0, len(response.css('div.fc-container__header time.fc-date-headline::attr(datetime)'))):
            x = time.strptime(response.css('div.fc-container__header time.fc-date-headline::attr(datetime)')[y].extract(), "%Y-%m-%d")
            currentPageDate.append(x)
    
        if min(currentPageDate) <= time.strptime(self.lastDate, "%Y/%m/%d"):
            return
        #

        # Per Single Page
        for i in range(0, len(response.css('div.fc-item__header a::attr(href)'))):
            individualArticles = response.css('div.fc-item__header a::attr(href)')[i].extract()
            if individualArticles is not None:
                yield scrapy.Request(individualArticles, callback=self.parse_pageX)
        
        # Next Page Recursion (TheGuardian's buttons have the exact same classes so use XPath)
        next_page = response.xpath('//a[@aria-label=" next page"]/@href').extract_first()
        #next_page = response.css('div.pagination__list a.button::attr(href)').extract_first()
        self.depth -= 1        
        if next_page is not None and self.depth > 0:
            yield scrapy.Request(next_page, callback=self.parse)
        
    def parse_pageX(self, response):
        splitUrl = response.url.split('/')

        # Rules : These are not Articles
        if (splitUrl[4] == 'live') or (splitUrl[5] == 'live') or (splitUrl[4] == 'ng-interactive'): 
            return
        #

        #Title
        title = response.css('div.content__main-column h1.content__headline::text').extract_first()
        if title is None:   # Found Galery/ad
            return
        if title == '\n':   # Found Video Report
            return 
        title = title.strip( '\n' )
        title = title.replace("/", "")  # Invalid Title Characters   
        title = title.replace(":", "")
        title = title.replace('"',"'")
        title = title.replace('?',"'")
        #
        
        # Text (UTF8 4 Bit)
        rawtext = response.css('div.content__article-body p::text').extract() 
        rawtext = "".join(rawtext)
        # Author
        author = response.css('div.content__main-column p.byline a.tone-colour span::text').extract() 
        author = "".join(author)
        author = author.strip('\n')
        # Category
        category = splitUrl[3] 
        # Date
        datetime = response.css('div.content__main-column time.content__dateline-wpd::attr(datetime)').extract_first()  # dateline-wpd always has Dates
        datetime = "".join(datetime)
        datetime = datetime.replace('T'," ")
        datetime = datetime[:-5]
       
        # DB Output
        WritetoDB(self.count, rawtext, title, author, category, datetime, response.url)
 
        # .HTML Output
        filename = 'Article' + str(self.count) 
        filename += ' -- ' + title + '.html'
        with open(filename, 'wb') as f:
            f.write(response.body)

        self.count += 1           