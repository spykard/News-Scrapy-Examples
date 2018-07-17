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
    query = ("INSERT INTO vox VALUES (%s, %s, %s, %s, %s, %s, %s)")
    cursor.execute(query, (countVariable, textVariable, titleVariable, authorVariable, categoryVariable, dateVariable, urlVariable))
    cnx.commit()
    
    cursor.close()
    cnx.close()    

def GetCountfromDB():  
    ''' Get number of articles in Database '''
    cnx = mysql.connector.connect(user='root', password='root', database='newsapp')
    cursor = cnx.cursor()
    query = ("SELECT id FROM vox")
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
    query = ("SELECT DATE_FORMAT(date, '%Y/%m/%d %H:%i:%S') FROM vox ORDER BY date DESC")
    cursor.execute(query)    

    row = list(cursor.fetchall())  # Must have no Unread Results    
    
    cursor.close()
    cnx.close()
    
    if not row:  # No date Found
        return "1980/1/1 10:00:00"
    else:
        return "".join(row[0])  
    
class VoxSpider(CrawlSpider):
    name = "vox"
    count = 0
    lastDate = "0"
    depth = 0   
    allowed_domains = ['www.vox.com']
         
    def start_requests(self):
        self.count = GetCountfromDB() # Count
        self.lastDate = GetLastDatefromDB() # Date        
        self.depth = int(getattr(self, 'depth', None)) # Crawl Depth
        
        urls = [
            'https://www.vox.com/news',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)   

    def parse(self, response):  
        # Per Single Page
        for i in range(0, len(response.css('h2.c-entry-box--compact__title a::attr(href)'))):
            individualArticles = response.css('h2.c-entry-box--compact__title a::attr(href)')[i].extract()
            if individualArticles is not None:
                yield scrapy.Request(individualArticles, callback=self.parse_pageX)
        
        # Next Page Recursion
        next_page = response.css('div.c-pagination__wrap a.c-pagination__next::attr(href)').extract_first()
        self.depth -= 1        
        if next_page is not None and self.depth > 0:
            yield scrapy.Request("https://www.vox.com/" + next_page, callback=self.parse)
        
    def parse_pageX(self, response):
        # Check Current Page Date vs. Last Article in DB Date
        currentPageDate = response.css('div.c-byline time.c-byline__item::text').extract_first()
        if currentPageDate is not None:
            currentPageDate = time.strptime(currentPageDate[9:30], "%b %d, %Y,  %I:%M%p")  # Dec 12, 2017, 2:01pm Format
                                                                                           # %p = PM/AM
        else:
            currentPageDate = time.strptime("Jan 1, 1980, 10:00am", "%b %d, %Y,  %I:%M%p") # Date of Article can be missing

        if currentPageDate <= time.strptime(self.lastDate, "%Y/%m/%d %H:%M:%S"):
            return  
        #

        splitUrl = response.url.split('/')

        # Rules : These are not Articles
        if (splitUrl[3] == 'cards') or (splitUrl[3] == 'a'): 
            return    
        #      

        # Text (UTF8 4 Bit)
        rawtext = response.css('div.c-entry-content p::text').extract() 
        rawtext = "".join(rawtext)
        # Title
        title = response.css('div.c-entry-hero__header-wrap h1::text').extract_first()
        if title is None:   # Vrethike Gallery/Diafimisi
            return
        title = title.strip('\n')
        title = title.replace("/", "")  # Invalid Title Characters
        title = title.replace(":", "")
        title = title.replace('"',"'")
        title = title.replace('?',"'")
        #

        # Author
        author = response.css('div.c-byline span.c-byline__item a::text').extract_first() 
        author = "".join(author)
        author = author.strip('\n')
        # Category
        category = splitUrl[3] 
        # Date (Previously created struct_time which can be converted to a MySQL Format)
        datetime = time.strftime("%Y-%m-%d %H:%M:%S", currentPageDate)
       
        WritetoDB(self.count, rawtext, title, author, category, datetime, response.url)
 
        # .HTML Output
        filename = 'Article' + str(self.count) 
        filename += ' -- ' + title + '.html'
        with open(filename, 'wb') as f:
            f.write(response.body)

        self.count += 1           