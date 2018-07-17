# News-Scrapy-Examples

Examples of Spiders for Crawling/Scraping different News Websites.

- - -

* Depth (Pages) of Crawling is given by the user.
* Checks previous Runs in order to only Crawl new Articles.

- - -

## Available Spiders

* TheGuardian
* Vox

## Output
To a MySQL Database of the following format and to a .HTML:

| id      | rawtext | title   | author  | category| date    | url     |
|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|
| int     | text    | varchar | varchar | varchar | datetime| varchar |

## Tutorial

Install [Scrapy](https://scrapy.org/ "Scrapy's Homepage")

```
cd News-Scrapy-Examples/theguardian
scrapy crawl theguardian -a depth=10  # Depth of your Choice
```

<br/>

<img src="https://raw.githubusercontent.com/spykard/News-Scrapy-Examples/master/Screenshots/Example.PNG">