# Python NewsCollector :newspaper:

As the internet has grown, the available **sources of information at our disposal have increased**. Nowadays, if you want to update yourself with the most important news of the day, you have a **vast variety of news sources** to choose from. Since we have that many news sources at our disposal, instead of manually going through all their content…

> Couldn't we let **automation** pick the top news stories from various newspapers for us, and nicely combine them into a newsletter?

**:fire: This is what the Python NewsCollector can do for us!**

:newspaper: Read more about how the algorithm of the News Collector works in [my Medium article](TBD).

-------

## Description

The Python NewsCollector let's you define a variety of news sources from which it will pick the **most relevant articles** and bundle these in a **nice HTML-based newsletter**. 

<p align="center"> 
  <img src="misc/newsletter_rendered.png" width="700" title="Example Output: Rendered Newsletter from Python News Collector">
</p>

View a full sample newsletter in PDF format [here](https://github.com/elisemercury/news-collector/blob/main/sample_newsletter.pdf).

The NewsCollector algorithm scrapes the source links provided and compares the articles it found on their similarity. If it finds multiple articles from different sources covering similar topics, these will be considered as being relevant articles and inlcude them in the output newsletter.

<p align="center">
  <img src="misc/collected_news.png" width="300" title="Example Output: Rendered Newsletter from Python News Collector">
</p>

:newspaper: Read more about how the algorithm of the News Collector works in [my Medium article](TBD).

## Basic Usage

You can run the NewsCollector algorithm as follows:

```Python
from newscollector import *

newsletter = NewsCollector('sources.json')
newsletter.create()
```

This will run the full NewsCollector pipeline by scraping the sources from the `sources.json` file and outputting the HTML newsletter. The `sources` parameter is required and has to be provided as Python `string`.

The `sources.json` file must contain a JSON formattede collection of RSS links to various online news providers. The more different news sources provided, the better NewsCollector will be able to caputre relevant articles. You can view the sample `sources.json` file [here](https://github.com/elisemercury/news-collector/blob/main/sources.json).

:notebook: For a **detailed usage guide**, please refer to the official NewsCollector [Usage Documentatíon](https://github.com/elisemercury/News-Collector/wiki/NewsCollector-Usage-Documentation).

## CLI Usage

The NewsCollector can also be run directly via the CLI with the following parameters:

```python
newscollector.py [-h] -s SOURCES [-n [NEWS_NAME]] [-d [NEWS_DATE]] 
                 [-t TEMPLATE] [-o OUTPUT_FILENAME]
```

## Output

The NewsCollector will output an HTML newsletter with the most relevant articles it found while scraping the sources provided. 

The output newsletter will be saved as a file in the working directory under the filename `newsletter_YYYY-MM-DD.html` where the date is the respective date the NewsCollector scraped its articles from. You can adjust the date as well as the output filename by setting the `news_date` and the `output_filename` variables.

## Additional Parameters

You can customize the NewsCollector algorithm with the following optional parameters:

```Python
newsletter = NewsCollector(sources, news_name="Daily News", news_date="2023-01-22", 
                           template='newsletter.html', output_filename='default')
```

:notebook: For a **detailed usage guide**, please refer to the official NewsCollector [Usage Documentatíon](https://github.com/elisemercury/News-Collector/wiki/NewsCollector-Usage-Documentation).

-------

<p align="center"><b>
:heart: Open Source 
</b></p>
