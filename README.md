# Python NewsCollector :newspaper:

As the internet has grown, the available **sources of information at our disposal have grown**. Nowadays, if you want to update yourself with the most important news of the day, you will have a **vast variety news sources** to choose from. Since we have that many news sources at our disposal, instead of manually going through all the news content…

> Couldn't we let automation pick the top news stories from various newspapers for us, and nicely combine them into a single newsletter?

**:fire: This is what the Python NewsCollector can do for us!**

:newspaper: Read more about how the algorithm of the News Collector works in [my Medium article](TBD).

## Description

The Python NewsCollector let's you define a variety of news sources from which it will pick the **most relevant articles** and bundle these in a **nice HTML-based newsletter**. 

<p align="center">
  <img src="misc/newsletter_rendered.png" width="700" title="Example Output: Rendered Newsletter from Python News Collector">
</p>

View a full sample newsletter in PDF format [here](https://github.com/elisemercury/news-collector/blob/main/sample_newsletter.pdf).

It scrapes the source links provided and compares the articles it found on their similarity. If it finds multiple articles from different sources covering similar topics, these will be considered as being relevant articles and inlcude them in the output newsletter.

<p align="center">
  <img src="misc/collected_news.png" width="400" title="Example Output: Rendered Newsletter from Python News Collector">
</p>

:newspaper: Read more about how the algorithm of the News Collector works in [my Medium article](TBD).

## Basic Usage

You can run the NewsCollector algortihm as follows:

```Python
from newscollector import *

newsletter = NewsCollector('sources.json')
newsletter.create()
```

This will run the full NewsCollector pipeline by scraping the sources from the `sources.json` file and outputting the HTML newsletter. The `sources` parameter is required and has to be provided as Python `string`.

The `sources.json` file must contain a JSON formattede collection of RSS links to various online news providers. The more news sources provided, the better NewsCollector will be able to caputre relevant articles. You can view the sample `sources.json` file [here](https://github.com/elisemercury/news-collector/blob/main/sources.json).

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
newsletter = NewsCollector(sources, news_name="Daily News", news_date="2023-01-22", template='newsletter.html', output_filename='default')
```

| Parameter | Type | Default Value | Other Values |
| ------ | :---: | :---: | ------ | 
| news_name | `str` | `'Daily News'` | any str |
| news_date | `str` | `date.today()` | any string in date format `'YYYY-MM-DD'` |
| template| `str` | `'newsletter.html'` | filename of any `html` template |
| output_filename | `str` | `'newsletter_<news_date>.html'` | filename to be used for the output `html` |

### news_name (str)

The title you would like to give to the output newsletter. By default, the title will be 'Daily News'.

### news_date (str)

The date for which the newsletter should be generated from. The articles will be scraped if their `publishedDate` corresponds to `news_date`. By default, NewsCollector will scrape the articles from today's date.

### template (str)

The template NewsCollector will use to generate the output HTML newsletter. You can use the default template `newsletter.html` or use your own custom template. The template used by NewsCollector must be located within the `\templates` folder of the working directory.

*Using a custom template*

When using a custom template, it should include standardized variable placeholders in certain positions within the HTML file. Upon rendering the newsletter, these placeholders will be filled by NewsCollector with the respective relevant article content it found. 

Variable placeholders should be surrounded by double curly brackets `{{ }}` as is done with Flask's `render_template()` function. You can read mor about this in [Flask's documentation](https://flask.palletsprojects.com/en/2.2.x/quickstart/#rendering-templates).

Placeholder variables include the following:  
`{{news_name}}`, `{{news_date}}`, `{{sourceXX}}`, `{{urlXX}}`, `{{picXX}}`, `{{titleXX}}`, `{{bodyXX}}`, `{{clusterXX_Y_source}}` and `{{clusterXX_Y_url}}`

where:  
... `XX` ranges from `[00 to 05]`  
... `Y` ranges from `[0 to 2]`

The templates used by NewsCollector must be located within the `\templates` folder of the working directory.

For more details, I suggest looking into the default example template `newsletter.html` [here](https://github.com/elisemercury/news-collector/blob/main/templates/newsletter.html).

### output_filename (str)

The filename of the output HTML newsletter. By default, NewsCollector will output an HTML file with the filename which will include the respective date: `newsletter_<news_date>.html`, where `<news_date>` is replaced by the value of the parameter. 

As an example, the following would be the output newsletter filename for the 22nd of January: `newsletter_2023-01-22.html`.

-------

:newspaper: Read more about how the algorithm of the News Collector works in [my Medium article](TBD).

-------

<p align="center"><b>
We :heart: Open Source 
</b></p>