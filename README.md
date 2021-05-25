# Crawling News Sites

Spiders for crawling/scraping various popular News Websites (TheGuardian, Vox etc.) into a Database.

## Available Spiders

* TheGuardian
* Vox

## Output to Database

The output of the crawling process is stored to a MySQL **Database** of the following format as well as to a .HTML file:

| id      | rawtext | title   | author  | category| date    | url     |
|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|
| int     | text    | varchar | varchar | varchar | datetime| varchar |

## Features

* Depth (Pages) of Crawling is customizable and given by the user.
* Checks previous runs in order to only crawl new Articles.

## Running the Tool

1. Install [Scrapy](https://scrapy.org/ "Scrapy's Homepage")

2. Run the following commands on the terminal of your choice:

``` bash
cd News-Scrapy-Examples/theguardian
scrapy crawl theguardian -a depth=10  # Depth of your Choice
```

<br/>

<img src="https://raw.githubusercontent.com/spykard/News-Scrapy-Examples/master/Screenshots/Example.PNG">
