import pkg_resources
import json
import pandas as pd
from datetime import *
from gensim.parsing.preprocessing import remove_stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize
import string
import feedparser as fp
import dateutil
import newspaper
from unidecode import unidecode
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import AgglomerativeClustering
import numpy as np
import flask
import warnings
import random
import argparse
import webbrowser
import os
warnings.filterwarnings("ignore")

class NewsCollector:

    def __init__(self, sources="sources.json", news_name="Daily News Update", news_date=date.today(), template='newsletter.html', output_filename='default', auto_open=False, return_details=False):
        self.sources = Helper.load_sources(sources)
        self.news_name = news_name  
        self.news_date, self.day_before = Helper.validate_date(news_date)
        self.template, self.template_path = Helper.validate_template(template)
        self.output_filename = Helper.validate_output_filename(output_filename, news_date)
        self.return_details = Helper.validate_return_details(return_details)
        self.auto_open = Helper.validate_auto_open(auto_open)

    def create(self):
        try:
            start = datetime.now()
            scraper = Scraper(self.sources, news_date=self.news_date)
            self.sources = scraper.scrape()

            news_df = Helper.write_dataframe(self.sources)
            end = datetime.now()
            Helper.print_scrape_result(news_df, start, end)

            news_df = Helper.clean_dataframe(news_df)
            news_df = Helper.clean_articles(news_df)

            tfidf_df = Processer.compute_tfidf(news_df)
            clusters = Processer.find_clusters(news_df, tfidf_df)
            featured_clusters = Processer.find_featured_clusters(clusters)

            Processer.build_html(featured_clusters, self.news_name, self.news_date, self.template, self.output_filename, self.template_path)
            msg = f"NewsCollector completed successfully. View the output here: {self.output_filename}"
            print(msg)
            if self.auto_open:
                webbrowser.open(self.output_filename)
            if self.return_details:
                return self.output_filename, clusters, featured_clusters
            return self.output_filename
        except:
            raise Exception(f'Error in "Newsletter.create()"')

class Scraper:

    def __init__(self, sources, news_date):
        self.sources = sources
        self.news_date = news_date

    def scrape(self):
        # Function that scrapes the content from the URLs in the source data
        try:
            articles_list = []
            for source, content in self.sources.items():
                for url in content['rss']:
                    d = fp.parse(url)
                    for entry in d.entries:
                        article = {}
                        if hasattr(entry,'published'):
                            article_date = dateutil.parser.parse(getattr(entry,'published'))
                            if (article_date.strftime('%Y-%m-%d') == str(self.news_date)):
                                try:
                                    content = newspaper.Article(entry.link)
                                    content.download()
                                    content.parse()  
                                    content.nlp()
                                    try:
                                        article['source'] = source
                                        article['url'] = entry.link
                                        article['date'] = article_date.strftime('%Y-%m-%d')
                                        article['time'] = article_date.strftime('%H:%M:%S %Z') # hour, minute, timezone (converted)
                                        article['title'] = content.title
                                        article['body'] = content.text
                                        article['summary'] = content.summary
                                        article['keywords'] = content.keywords
                                        article['image_url'] = content.top_image
                                        articles_list.append(article)
                                        Helper.print_scrape_status(len(articles_list))
                                    except Exception as e:
                                        print(e)
                                        print('continuing...')
                                except Exception as e: 
                                    print(e)
                                    print('continuing...')
            return articles_list
        except:
            raise Exception(f'Error in "Scraper.scrape()"')

class Processer:

    def compute_tfidf(df):
        # Function that computes the TFIDF values for all words in the article bodies
        try:
            tfidf_df = TfidfVectorizer().fit_transform(df['clean_body']).todense()
            return tfidf_df
        except:
            raise Exception(f'Error in "Processer.compute_tfidf()"')

    def find_clusters(df, tfidf_df, distance_threshhold=1):
        try:
            ac = AgglomerativeClustering(distance_threshold=distance_threshhold, n_clusters=None).fit(tfidf_df)
            articles_labeled = ac.fit_predict(tfidf_df)
            cluster_count = {}
            for label in range(0, len(set(ac.labels_))):
                cluster_count[label] = np.count_nonzero(articles_labeled == label)
            clusters = {}
            for n in range(0, len(cluster_count), 1):
                indexes = np.argwhere(articles_labeled == max(cluster_count, key=cluster_count.get, default=None)).flatten('C').tolist()
                if len(indexes) < 2:
                    break
                else:
                    clusters[n] = []
                    for i in indexes:
                        clusters[n].append(df.iloc[i])
                    cluster_count.pop(max(cluster_count, key=cluster_count.get, default=None))
            return clusters
        except:
             raise Exception(f'Error in "Processer.find_clusters()"')

    def find_featured_clusters(clusters, null_cluster_img="https://images.unsplash.com/photo-1505244783088-5a36f166e5b5?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2071&q=80"):
        try:
            featured_clusters = {}
            for i in clusters.keys():
                if len(set([j["source"] for j in clusters[i]])) > 1:
                    featured_clusters[i] = clusters[i]
            for i in range(len(featured_clusters), 6, 1):
                featured_clusters[f'nan_{i}'] = [{"source":None, 
                                        "url": None, 
                                        "date":None, 
                                        "time":None,
                                        "title":"No article found 😥",
                                        "body": "",
                                        "summary": None,
                                        "keywords": None,
                                        "image_url": null_cluster_img,
                                        "clean_body": None}]
            return featured_clusters
        except:
            raise Exception(f'Error in "Processer.find_featured_clusters()"')

    def build_html(clusters_dict, news_name, news_date, template, output_filename, template_path):
        try:
            newsletter = flask.Flask('newsletter', template_folder=template_path)

            Helper.shuffle_content(clusters_dict)
            similar_articles = Helper.prettify_similar(clusters_dict)

            with newsletter.app_context():
                rendered = flask.render_template(template, \
                                                news_name=news_name,\
                                                news_date=news_date,\
                                                source00=clusters_dict[list(clusters_dict)[0]][0]['source'],\
                                                source01=clusters_dict[list(clusters_dict)[1]][0]['source'],\
                                                source02=clusters_dict[list(clusters_dict)[2]][0]['source'],\
                                                source03=clusters_dict[list(clusters_dict)[3]][0]['source'],\
                                                source04=clusters_dict[list(clusters_dict)[4]][0]['source'],\
                                                source05=clusters_dict[list(clusters_dict)[5]][0]['source'],\
                                                url00=clusters_dict[list(clusters_dict)[0]][0]['url'],\
                                                url01=clusters_dict[list(clusters_dict)[1]][0]['url'],\
                                                url02=clusters_dict[list(clusters_dict)[2]][0]['url'],\
                                                url03=clusters_dict[list(clusters_dict)[3]][0]['url'],\
                                                url05=clusters_dict[list(clusters_dict)[5]][0]['url'],\
                                                pic00=clusters_dict[list(clusters_dict)[0]][0]['image_url'],\
                                                pic01=clusters_dict[list(clusters_dict)[1]][0]['image_url'],\
                                                pic02=clusters_dict[list(clusters_dict)[2]][0]['image_url'],\
                                                pic03=clusters_dict[list(clusters_dict)[3]][0]['image_url'],\
                                                pic04=clusters_dict[list(clusters_dict)[4]][0]['image_url'],\
                                                pic05=clusters_dict[list(clusters_dict)[5]][0]['image_url'],\
                                                title00=clusters_dict[list(clusters_dict)[0]][0]['title'],\
                                                title01=clusters_dict[list(clusters_dict)[1]][0]['title'],\
                                                title02=clusters_dict[list(clusters_dict)[2]][0]['title'],\
                                                title03=clusters_dict[list(clusters_dict)[3]][0]['title'],\
                                                title04=clusters_dict[list(clusters_dict)[4]][0]['title'],\
                                                title05=clusters_dict[list(clusters_dict)[5]][0]['title'],\
                                                body00=clusters_dict[list(clusters_dict)[0]][0]['body'],\
                                                body01=clusters_dict[list(clusters_dict)[1]][0]['body'],\
                                                body02=clusters_dict[list(clusters_dict)[2]][0]['body'],\
                                                body03=clusters_dict[list(clusters_dict)[3]][0]['body'],\
                                                body04=clusters_dict[list(clusters_dict)[4]][0]['body'],\
                                                body05=clusters_dict[list(clusters_dict)[5]][0]['body'],\
                                                cluster00_0_source=f"{similar_articles[list(similar_articles)[0]]['source'][0]}",\
                                                cluster00_1_source=f"{similar_articles[list(similar_articles)[0]]['source'][1]}",\
                                                cluster00_2_source=f"{similar_articles[list(similar_articles)[0]]['source'][2]}",\
                                                cluster01_0_source=f"{similar_articles[list(similar_articles)[1]]['source'][0]}",\
                                                cluster01_1_source=f"{similar_articles[list(similar_articles)[1]]['source'][1]}",\
                                                cluster01_2_source=f"{similar_articles[list(similar_articles)[1]]['source'][2]}",\
                                                cluster02_0_source=f"{similar_articles[list(similar_articles)[2]]['source'][0]}",\
                                                cluster02_1_source=f"{similar_articles[list(similar_articles)[2]]['source'][1]}",\
                                                cluster02_2_source=f"{similar_articles[list(similar_articles)[2]]['source'][2]}",\
                                                cluster03_0_source=f"{similar_articles[list(similar_articles)[3]]['source'][0]}",\
                                                cluster03_1_source=f"{similar_articles[list(similar_articles)[3]]['source'][1]}",\
                                                cluster03_2_source=f"{similar_articles[list(similar_articles)[3]]['source'][2]}",\
                                                cluster04_0_source=f"{similar_articles[list(similar_articles)[4]]['source'][0]}",\
                                                cluster04_1_source=f"{similar_articles[list(similar_articles)[4]]['source'][1]}",\
                                                cluster04_2_source=f"{similar_articles[list(similar_articles)[4]]['source'][2]}",\
                                                cluster05_0_source=f"{similar_articles[list(similar_articles)[5]]['source'][0]}",\
                                                cluster05_1_source=f"{similar_articles[list(similar_articles)[5]]['source'][1]}",\
                                                cluster05_2_source=f"{similar_articles[list(similar_articles)[5]]['source'][2]}",\
                                                cluster00_0_url=f"{similar_articles[list(similar_articles)[0]]['url'][0]}",\
                                                cluster00_1_url=f"{similar_articles[list(similar_articles)[0]]['url'][1]}",\
                                                cluster00_2_url=f"{similar_articles[list(similar_articles)[0]]['url'][2]}",\
                                                cluster01_0_url=f"{similar_articles[list(similar_articles)[1]]['url'][0]}",\
                                                cluster01_1_url=f"{similar_articles[list(similar_articles)[1]]['url'][1]}",\
                                                cluster01_2_url=f"{similar_articles[list(similar_articles)[1]]['url'][2]}",\
                                                cluster02_0_url=f"{similar_articles[list(similar_articles)[2]]['url'][0]}",\
                                                cluster02_1_url=f"{similar_articles[list(similar_articles)[2]]['url'][1]}",\
                                                cluster02_2_url=f"{similar_articles[list(similar_articles)[2]]['url'][2]}",\
                                                cluster03_0_url=f"{similar_articles[list(similar_articles)[3]]['url'][0]}",\
                                                cluster03_1_url=f"{similar_articles[list(similar_articles)[3]]['url'][1]}",\
                                                cluster03_2_url=f"{similar_articles[list(similar_articles)[3]]['url'][2]}",\
                                                cluster04_0_url=f"{similar_articles[list(similar_articles)[4]]['url'][0]}",\
                                                cluster04_1_url=f"{similar_articles[list(similar_articles)[4]]['url'][1]}",\
                                                cluster04_2_url=f"{similar_articles[list(similar_articles)[4]]['url'][2]}",\
                                                cluster05_0_url=f"{similar_articles[list(similar_articles)[5]]['url'][0]}",\
                                                cluster05_1_url=f"{similar_articles[list(similar_articles)[5]]['url'][1]}",\
                                                cluster05_2_url=f"{similar_articles[list(similar_articles)[5]]['url'][2]}",\
                                                )
            output = open(output_filename, 'w', encoding="utf-8")
            output.write(rendered)
            output.close()
            return True
        except:
            raise Exception(f'Error in "Processer.build_html()"')

class Helper:

    def validate_date(date):
        try:
            if isinstance(date, str):
                date = datetime.strptime(date, '%Y-%m-%d').date()
            day_before = date - timedelta(days=1)
            return date, day_before
        except:
            raise Exception(f'Error in "Helper.validate_date()"')

    def validate_template(template):
        try:
            if os.path.exists(os.path.join('templates', template)):
                template_path = 'templates'
                print(f'INFO: Using custom "{template}" as template file.')
                return template, template_path
            else:
                template = 'newsletter.html'
                template_path = pkg_resources.resource_filename(__name__, 'templates')
                print('INFO: Using package default "newsletter.html" as template file.')
                return template, template_path
        except:
            raise Exception(f'Error in "Helper.validate_template()"') 

    def load_sources(file):
        # Function that loads in the sources from the JSON database
        try:
            with open(file) as data:
                sources = json.load(data)
            print(f'INFO: Using custom "{file}" as source file.')
            return sources
        except:
            try:
                default_file = pkg_resources.resource_filename(__name__, 'sources.json')
                with open(default_file) as data:
                    sources = json.load(data)
                print('INFO: Using package default "sources.json" as source file.')
                return sources
            except:
                raise Exception(f'Error in "Helper.load_sources()"')

    def validate_output_filename(file, news_date):
        try:
            if file == 'default':
                output_path = pkg_resources.resource_filename(__name__, 'rendered')
                if not os.path.isdir(output_path):
                    os.makedirs(output_path)
                file = os.path.join(output_path, f'newsletter_{news_date}.html')
                return file
            else:
                head_tail = os.path.split(file)
                if head_tail[0] != '':
                    if not os.path.exists(head_tail[0]):
                        os.makedirs(head_tail[0])
                return file
        except:
            raise Exception(f'Error in "Helper.validate_output_filename()"')
        
    def validate_return_details(return_details):
        if not isinstance(return_details, bool):
            raise Exception(f'Error in "validate_return_details": parameter "return_details" must be of type "bool".')
        return return_details

    def validate_auto_open(auto_open):
        if not isinstance(auto_open, bool):
            raise Exception(f'Error in "validate_auto_open": parameter "auto_open" must be of type "bool".')
        return auto_open

    def print_scrape_status(count):
        print(f"Scraped {count} articles", end="\r")

    def print_scrape_result(df, start, end):
        time_delta = end - start
        min, sec = divmod(time_delta.days * 86400 + time_delta.seconds, 60)
        for source in set(df["source"]):
            print(f'{list(df["source"]).count(source)} articles downloaded from {source}\n', end="\r")
        print(f'{len(df["source"])} total articles downloaded in {min} min {sec} sec\n')        

    def write_dataframe(sources):
        # Function that writes the
        try:
            df = pd.json_normalize(sources)
            return df
        except:
            raise Exception(f'Error in "Helper.write_dataframe()"')

    def clean_dataframe(df):
        try:
            df = df[df.title != '']
            df = df[df.body != '']
            df = df[df.image_url != '']

            df = df[df.title.str.count('\s+').ge(3)] #keep only titles having more than 3 spaces in the title
            df = df[df.body.str.count('\s+').ge(20)] #keep only titles having more than 20 spaces in the body

            return df
        except:
            raise Exception(f'Error in "Helper.clean_dataframe()"')
        
    def clean_articles(df):
        # Function that cleans all the bodies of the articles
        try:
            # Drop Duplicates
            df = (df.drop_duplicates(subset=["title", "source"])).sort_index()
            df = (df.drop_duplicates(subset=["body"])).sort_index()
            df = (df.drop_duplicates(subset=["url"])).sort_index()
            df = df.reset_index(drop=True)
            
            # Make all letters lower case
            df['clean_body'] = df['body'].str.lower()

            # Filter out the stopwords, puntuation and digits
            df['clean_body'] = [remove_stopwords(x)\
                                .translate(str.maketrans('','',string.punctuation))\
                                .translate(str.maketrans('','',string.digits))\
                                for x in df['clean_body']]

            # Remove sources
            sources_set = [x.lower() for x in set(df['source'])]
            sources_to_replace = dict.fromkeys(sources_set, "")
            df['clean_body'] = (df['clean_body'].replace(sources_to_replace, regex=True))

            # Unidecode all characters
            df['clean_body'] = df['clean_body'].apply(unidecode)

            # Tokenize
            df['clean_body'] = df['clean_body'].apply(word_tokenize)

            # Stem words
            stemmer = SnowballStemmer(language='english')
            df['clean_body'] = df["clean_body"].apply(lambda x: [stemmer.stem(y) for y in x])
            df['clean_body'] = df["clean_body"].apply(lambda x: ' '.join([word for word in x]))

            return df
        except:
            raise Exception(f'Error in "Helper.clean_articles()"')
    
    def shuffle_content(clusters_dict):
        try:
            for i in list(clusters_dict):
                try:
                    random.shuffle(clusters_dict[i])
                except:
                    pass
        except:
            raise Exception(f'Error in "Helper.shuffle_content()"')

    def prettify_similar(clusters_dict):
        try:
            similar_articles = {}
            for i in list(clusters_dict):
                similar_articles[i] = {}
                if len(clusters_dict[i]) >= 4: 
                    similar_articles[i]['source'] = [f"{clusters_dict[i][1]['source']} ", f"| {clusters_dict[i][2]['source']} ", f"| {clusters_dict[i][3]['source']}"]
                    similar_articles[i]['url'] = [clusters_dict[i][1]['url'], clusters_dict[i][2]['url'], clusters_dict[i][3]['url']]
                elif len(clusters_dict[i]) == 3:
                    similar_articles[i]['source'] = [f"{clusters_dict[i][1]['source']} ", f"| {clusters_dict[i][2]['source']}", ""]
                    similar_articles[i]['url'] = [clusters_dict[i][1]['url'], clusters_dict[i][2]['url'], ""]
                elif len(clusters_dict[i]) == 2: 
                    similar_articles[i]['source'] = [clusters_dict[i][1]['source'], "", ""]
                    similar_articles[i]['url'] = [clusters_dict[i][1]['url'], "", ""]
                else:
                    similar_articles[i]['source'] = ["None", "", ""]
                    similar_articles[i]['url'] = ["", "", ""]
            return similar_articles
        except:
            raise Exception(f'Error in "Helper.prettify_similar()"')

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Automated News Article Collection with Python - https://github.com/elisemercury/Duplicate-Image-Finder')
    parser.add_argument("-s", "--sources", type=str, help='Path of source JSON file with news sources to be scraped.', required=False, default="sources.json")
    parser.add_argument("-n", "--news_name", type=str, help='Title name of the newsletter.', required=False, default='Daily News Update')
    parser.add_argument("-d", "--news_date", type=str, help='Date of the newsletter.', required=False, default=date.today())
    parser.add_argument("-t", "--template", type=str, help='Filename of the template HTML newsletter file.', required=False, default='newsletter.html')
    parser.add_argument("-o", "--output_filename", type=str, help='Filename of the output HTML newsletter file.', required=False, default='default')
    parser.add_argument("-r", "--return_details", type=bool, help='Choose whether to return the collected cluster data.', required=False, default=False)   
    parser.add_argument("-a", "--auto_open", type=bool, help='Choose whether to automatically open the newsletter in the browser.', required=False, default=False)   
    args = parser.parse_args()

    sources = args.sources
    news_name = args.news_name
    news_date = args.news_date
    template = args.template
    output_filename = args.output_filename
    return_details = args.return_details
    auto_open = args.auto_open

    newsletter = NewsCollector(sources, news_name, news_date, template, output_filename, return_details, auto_open)
    newsletter.create()
    
