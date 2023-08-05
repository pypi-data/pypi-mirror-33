import configparser
import datetime
import json
import logging
#import lxml
import os
from pprint import pprint
import sys
import time

import boto3
import botocore as botocore
from bs4 import BeautifulSoup
import requests
from slackclient import SlackClient
import wget

#logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

#config_path = '../../config/config.ini'


class FlyOnTheWall:
    #url_base = 'https://boards.4chan.org/'
    #url_board = 'biz/'
    url_thread_base = 'thread/'

    #thread_limit = 99   # If set to below number of threads on front page, will only analyze that many number of threads

    excluded_threads_biz = ['4884770', '904256']    # Pinned FAQ and general info threads

    config_path = 'config/config.ini'

    config = configparser.ConfigParser()
    config.read(config_path)

    aws_key = config['aws']['api']
    aws_secret = config['aws']['secret']

    try:
        comprehend_client = boto3.client(service_name='comprehend', region_name='us-east-1',
                                         aws_access_key_id=aws_key, aws_secret_access_key=aws_secret)

    except:
        logger.warning('AWS credentials file not configured. Sentiment analysis not possible.')

        comprehend_client = None


    def __init__(self, config_path,# exchange, market,
                 forum_url='https://boards.4chan.org/',
                 board='biz/',
                 excluded_threads=excluded_threads_biz,
                 pages=1, thread_limit=99,
                 persistent=False, persistent_loop_time=1800, persistent_loops=5,
                 slack_alerts=False,
                 analyze_sentiment=False, sentiment_results_max=None):#,
                 #positive_sentiment_threshold=0.682, negative_sentiment_threshold=0.682):
        #self.url_board_base = FlyOnTheWall.url_base + board
        self.url_board_base = forum_url + board

        #self.url_prefix = FlyOnTheWall.url_base + board + FlyOnTheWall.url_thread_base
        self.url_prefix = forum_url + board + FlyOnTheWall.url_thread_base

        self.pages = pages

        self.persistent = persistent

        self.json_directory = 'json/flyonthewall/'

        if not os.path.exists(self.json_directory):
            #os.mkdir('json/')
            os.makedirs(self.json_directory, exist_ok=True)

        self.persistent_loop_time = persistent_loop_time

        self.persistent_loops = persistent_loops

        self.thread_limit = thread_limit

        self.excluded_threads = excluded_threads

        self.analyze_sentiment = analyze_sentiment

        if self.analyze_sentiment == True and FlyOnTheWall.comprehend_client == None:
            logger.error('Must configure AWS credentials file before continuing with sentiment analysis. Exiting.')

            sys.exit(1)

        """
        if self.analyze_sentiment == True:
            config = configparser.ConfigParser()
            config.read(config_path)

            aws_key = config['aws']['api']
            aws_secret = config['aws']['secret']

            self.comprehend_client = boto3.client(service_name='comprehend', region_name='us-east-1',
                                                  aws_access_key_id=aws_key, aws_secret_access_key=aws_secret)

        else:
            self.comprehend_client = None
        """

        self.sentiment_results_max = sentiment_results_max

        #positive_sentiment_threshold = positive_sentiment_threshold
        #negative_sentiment_threshold = negative_sentiment_threshold

        self.last_updated = None

        if slack_alerts == True:
            config = configparser.ConfigParser()
            config.read(config_path)

            slack_token = config['slack']['slack_token']

            self.slack_client = SlackClient(slack_token)

            self.slack_bot_user = config['settings']['slack_bot_user']

            self.slack_bot_icon = config['settings']['slack_bot_icon']

        else:
            self.slack_client = None


    def load_keywords(self, keyword_data):
        self.keyword_list = []
        self.excluded_list = []

        logger.debug('Loading keyword file.')

        if isinstance(keyword_data, dict):
            logger.debug('Using provided keyword list.')

            self.keyword_list = keyword_data['keywords']
            self.excluded_list = keyword_data['excluded']

        elif isinstance(keyword_data, str) and '.txt' in keyword_data:
            logger.debug('Using provided keyword file.')

            with open(keyword_data, 'r', encoding='utf-8') as kw:
                keyword_list_read = kw.read().split()

            #keyword_list = []
            #excluded_list = []
            for keyword in keyword_list_read:
                if '|' in keyword:
                    keyword_split = keyword.split('|')

                    self.keyword_list.append(keyword_split[0])

                    if ',' in keyword_split[1]:
                        excluded_split = keyword_split[1].split(',')

                        for word in excluded_split:
                            if word != '' and word != '\n' and word != '\r':
                                self.excluded_list.append(word)

                    else:
                        self.excluded_list.append(keyword_split[1])

                #else:
                elif keyword != '' and keyword != '\n' and keyword != '\r':
                        self.keyword_list.append(keyword)

        logger.debug('self.keyword_list: ' + str(self.keyword_list))
        logger.debug('self.excluded_list: ' + str(self.excluded_list))

        logger.info('----- KEYWORDS -----')
        for word in self.keyword_list:
            logger.info(word.upper())

        logger.info('-- EXCLUDED WORDS --')
        for word in self.excluded_list:
            logger.info(word.upper())

        #time.sleep(1)


    def run_search(self, exchange, market, slack_channel=None, slack_thread=None, purge_old_data=False,
                   positive_sentiment_threshold=0.682, negative_sentiment_threshold=0.682):
        sentiment_results_return = {'Exception': False, 'result': {}}

        thread_archive_file = 'thread_archive.json'
        #thread_archive_file = exchange.lower() + '_' + market.lower() + '_threads.json'

        def purge_old_data():
            logger.info('Purging old data.')

            if os.path.exists(thread_archive_file):
                logger.debug('Removing thread archive json file.')

                os.remove(thread_archive_file)

            downloads = os.listdir(download_directory)

            for dl in downloads:
                file_path = download_directory + dl

                logger.debug('Removing download: ' + file_path)

                os.remove(file_path)


        def send_slack_alert(channel_id, message, thread_id=None):
            alert_return = {'Exception': False, 'result': None}

            try:
                alert_return['result'] = self.slack_client.api_call(
                    'chat.postMessage',
                    channel=channel_id,
                    text=message,
                    username=self.slack_bot_user,
                    icon_url=self.slack_bot_icon,
                    thread_ts=thread_id,
                    #reply_broadcast=True
                    thread_broadcast=True
                )

            except Exception as e:
                logger.exception('Exception while sending Slack alert.')
                logger.exception(e)

                #alert_result = False
                alert_return['Exception'] = True

            finally:
                #return alert_result, alert_return
                return alert_return


        def get_threads():
            try:
                logger.debug('Retrieving thread list.')

                url = self.url_board_base

                r = requests.get(url)

                soup = BeautifulSoup(r.text, 'html.parser')# 'lxml')

                threads = soup.find_all('a', attrs={'class': 'replylink'})

                thread_list = []
                for thread in threads:
                    thread_num = thread['href'].split('/')[1]

                    thread_list.append(thread_num)

                return thread_list

            except Exception as e:
                logger.exception('Exception while getting threads.')
                logger.exception(e)

                #raise


        def get_posts(thread_num):
            try:
                logger.debug('Retrieving posts.')

                url = self.url_prefix + thread_num

                r = requests.get(url)

                soup = BeautifulSoup(r.text, 'html.parser')#'lxml')

                #posts = soup.find_all('blockquote', attrs={'class': 'postMessage'})

                data = soup.find_all('div', attrs={'class': ['post op', 'post reply']})

                post_list = []
                for post in data:
                    post_data = {}

                    post_data['post'] = post.text

                    attachments = post.find_all('a', attrs={'class': 'fileThumb'})

                    # ONLY GETS LAST FILE (MULTIPLE POSSIBLE?)
                    for file in attachments:
                        file_url = 'https:' + file['href']
                        logger.debug('file_url: ' + file_url)

                        post_data['file'] = file_url

                    post_list.append(post_data)
                    logger.debug('post_data: ' + str(post_data))

                logger.debug('post_list: ' + str(post_list))

                return post_list


            except Exception as e:
                logger.exception('Exception while getting posts.')
                logger.exception(e)

                #raise


        def filter_threads(thread_data):
            threads_filtered = {}

            try:
                logger.debug('Filtering threads.')

                #threads = thread_archive

                #thread_count = len(threads)
                thread_count = len(thread_data)

                thread_loops = 0
                #for key in threads:
                for key in thread_data:
                    thread_loops += 1

                    logger.info('Thread #' + str(thread_loops) + ' of ' + str(thread_count))

                    #posts = threads[key]
                    posts = thread_data[key]
                    logger.debug('posts: ' + str(posts))

                    found_list = []

                    post_count = len(posts)

                    post_loops = 0
                    for post in posts:
                        post_loops += 1

                        logger.info('Post #' + str(post_loops) + ' of ' + str(post_count))

                        word_count = len(self.keyword_list)

                        word_loops = 0
                        for word in self.keyword_list:
                            word_loops += 1

                            logger.debug('Word #' + str(word_loops) + ' of ' + str(word_count))

                            #word_full = ' ' + word + ' '

                            word = word.lower()

                            if word in post['post'].lower():
                            #if word_full in post['post'].lower():
                                #logger.debug('FOUND: ' + word)
                                passed_excluded = True

                                for excluded in self.excluded_list:
                                    #excluded_full = ' ' + excluded + ' '

                                    excluded = excluded.lower()

                                    if excluded in post['post'].lower():
                                    #if excluded_full in post['post'].lower():
                                        passed_excluded = False

                                        logger.debug('Found excluded word: ' + excluded)

                                        logger.debug('Excluding post: ' + str(post))

                                if passed_excluded == True:
                                    entry = word + '|' + post['post'].lower()

                                    if 'file' in post:
                                        entry = entry + '|' + post['file']

                                        logger.info('Downloading attachment.')

                                        file_name = wget.detect_filename(url=post['file'])
                                        logger.debug('file_name: ' + file_name)

                                        if not os.path.isfile(download_directory + file_name):
                                            dl_file = wget.download(post['file'], out=download_directory.rstrip('/'))

                                            logger.debug('Successful download: ' + dl_file)

                                    found_list.append(entry)

                    if len(found_list) > 0:
                        threads_filtered[key] = found_list

                #return threads_filtered


            except Exception as e:
                logger.exception('Exception while filtering threads.')
                logger.exception(e)

                #raise

            finally:
                return threads_filtered


        #def trim_relevant_posts(post_data):
        def create_trimmed_archive(thread_data):
            thread_archive_trimmed = {'Exception': False}
            #posts_trimmed = {'Exception': False}

            try:
                #for thread in thread_archive:
                    #thread_archive_trimmed[thread] = []

                for thread in thread_data:
                    #for post in thread_archive[thread]:
                    #for post in post_data:
                    for post in thread_data[thread]:
                        post_keyword = post.split('|')[0]
                        logger.debug('post_keyword: ' + post_keyword)

                        #post_truncated = post['post']
                        post_truncated = post.split('|')[1][1:]
                        logger.debug('post_truncated: ' + post_truncated)

                        post_file = ''
                        try:
                            post_file = post.split('|')[-1]
                            logger.debug('post_file: ' + post_file)

                        except:
                            logger.debug('No file present in post.')

                        logger.debug('[PRE] post_truncated: ' + post_truncated)

                        while (True):
                            post_num_index = post_truncated.lower().find('no.')

                            if post_num_index == -1:
                                while (True):
                                    post_num_index = post_truncated.lower().find('>>')

                                    if post_num_index == -1:
                                        break

                                    else:
                                        post_truncated = post_truncated[(post_num_index + 2):]

                                break

                            else:
                                post_truncated = post_truncated[(post_num_index + 3):]

                        first_letter_index = 0
                        for x in range(0, len(post_truncated)):
                            if post_truncated[x].isalpha():
                                first_letter_index = x

                                break

                        post_truncated = post_truncated[first_letter_index:]
                        logger.debug('[POST] post_truncated: ' + post_truncated)

                        if thread not in thread_archive_trimmed:
                            thread_archive_trimmed[thread] = []

                        thread_archive_trimmed[thread].append(post_truncated)

            except Exception as e:
                logger.exception('Exception while creating trimmed archive.')
                logger.exception(e)

                thread_archive_trimmed['Exception'] = True

            finally:
                return thread_archive_trimmed


        def get_entities(input_text):
            entities = None
            metadata = None

            try:
                comprehend_results = FlyOnTheWall.comprehend_client.detect_entities(Text=input_text, LanguageCode='en')

                entities = comprehend_results['Entities']
                metadata = comprehend_results['ResponseMetadata']

            except Exception as e:
                logger.exception('Exception while getting entities.')
                logger.exception(e)

            finally:
                return entities, metadata


        def get_key_phrases(input_text):
            key_phrases = None
            metadata = None

            try:
                comprehend_results = FlyOnTheWall.comprehend_client.detect_key_phrases(Text=input_text, LanguageCode='en')

                key_phrases = comprehend_results['KeyPhrases']
                metadata = comprehend_results['ResponseMetadata']

            except Exception as e:
                logger.exception('Exception while getting entities.')
                logger.exception(e)

            finally:
                return key_phrases, metadata


        def get_sentiment(input_text):
            sentiment = None
            metadata = None

            try:
                comprehend_results = FlyOnTheWall.comprehend_client.detect_sentiment(Text=input_text, LanguageCode='en')

                sentiment = {'sentiment': comprehend_results['Sentiment'], 'score': comprehend_results['SentimentScore']}
                metadata = comprehend_results['ResponseMetadata']

            except Exception as e:
                logger.exception('Exception while getting entities.')
                logger.exception(e)

            finally:
                return sentiment, metadata

        def threshold_sentiment_results(sentiment_results):
            sentiment_results_thresholded = {'positive': None, 'negative': None}

            positive_sentiment = []
            negative_sentiment = []
            for result in sentiment_results:
                if result['sentiment']['sentiment'] == 'POSITIVE':
                    positive_sentiment.append(result)

                elif result['sentiment']['sentiment'] == 'NEGATIVE':
                    negative_sentiment.append(result)

            positive_results_sorted = sorted(positive_sentiment,
                                             key=lambda sent: sent['sentiment']['score']['Positive'],
                                             reverse=True)

            logger.debug('Removing positive results with score < ' + str(positive_sentiment_threshold) + '.')

            for result in positive_results_sorted:
                if result['sentiment']['score']['Positive'] < positive_sentiment_threshold:
                    positive_results_sorted.remove(result)

            sentiment_results_thresholded['positive'] = positive_results_sorted

            negative_results_sorted = sorted(negative_sentiment,
                                             key=lambda sent: sent['sentiment']['score']['Negative'],
                                             reverse=True)

            logger.debug('Removing negative results with score < ' + str(negative_sentiment_threshold) + '.')

            for result in negative_results_sorted:
                if result['sentiment']['score']['Negative'] < negative_sentiment_threshold:
                    negative_results_sorted.remove(result)

            sentiment_results_thresholded['negative'] = negative_results_sorted

            if self.sentiment_results_max != None:
                for result in sentiment_results_thresholded:
                    if len(sentiment_results_thresholded[result]) > self.sentiment_results_max:
                        sentiment_results_thresholded[result] = sentiment_results_thresholded[result][:self.sentiment_results_max]

            return sentiment_results_thresholded


        def calc_sentiment_average(results_thresholded):
            sentiment_average_return = {'Exception': False, 'result': {'positive': {'average': None, 'posts': []},
                                                                       'negative': {'average': None, 'posts': []}}}

            try:
                positive_results = results_thresholded['positive']

                pos_sentiment_count = 0
                pos_sentiment_total = 0
                for result in positive_results:
                    pos_sentiment_count += 1

                    post = result['post']

                    score = result['sentiment']['score']['Positive']

                    sentiment_average_return['result']['positive']['posts'].append((post, score))

                    pos_sentiment_total += score

                if pos_sentiment_count > 0:
                    pos_sentiment_average = pos_sentiment_total / pos_sentiment_count

                else:
                    pos_sentiment_average = 0

                sentiment_average_return['result']['positive']['average'] = pos_sentiment_average

                negative_results = results_thresholded['negative']

                neg_sentiment_count = 0
                neg_sentiment_total = 0
                for result in negative_results:
                    neg_sentiment_count += 1

                    post = result['post']

                    score = result['sentiment']['score']['Negative']

                    sentiment_average_return['result']['negative']['posts'].append((post, score))

                    neg_sentiment_total += score

                if neg_sentiment_count > 0:
                    neg_sentiment_average = neg_sentiment_total / neg_sentiment_count

                else:
                    neg_sentiment_average = 0

                sentiment_average_return['result']['negative']['average'] = neg_sentiment_average

            except Exception as e:
                logger.exception('Exception while calculating sentiment ratio.')
                logger.exception(e)

                sentiment_average_return['Exception'] = True

            finally:
                return sentiment_average_return


        try:
            market_raw = market.lower()

            if '-' in market_raw:
                market_compact = market_raw.split('-')[0] + market_raw.split('-')[1]

            elif '/' in market_raw:
                market_compact = market_raw.split('/')[0] + market_raw.split('/')[1]

            else:
                market_compact = market_raw

            logger.debug('market_compact: ' + market_compact)

            #market_directory = 'json/flyonthewall/' + exchange.lower() + '_' + market_compact + '/'
            market_directory = self.json_directory + exchange.lower() + '_' + market_compact + '/'

            product_directory = market_directory + datetime.datetime.now().strftime('%m%d%Y_%H%M%S') + '/'

            download_directory = product_directory + 'downloads/'

            if not os.path.exists(market_directory):
                logger.debug('Creating market directory: ' + market_directory)

                #os.mkdir(market_directory)
                os.makedirs(market_directory, exist_ok=True)

            if not os.path.exists(product_directory):
                logger.debug('Creating product directory: ' + product_directory)

                #os.mkdir(product_directory)
                os.makedirs(product_directory, exist_ok=True)

            if not os.path.exists(download_directory):
                logger.debug('Creating download directory: ' + download_directory)

                #os.mkdir(download_directory)
                os.makedirs(download_directory, exist_ok=True)

            thread_archive_file = product_directory + thread_archive_file

            if self.analyze_sentiment == True:
                self.comprehend_results_file = product_directory + 'comprehend_results.json'

            # Purge old data if requested
            if purge_old_data == True:
                purge_old_data()

            thread_archive = {}

            loop_count = 0
            while (True):
                loop_count += 1
                logger.debug('loop_count: ' + str(loop_count))

                logger.info('Retrieving threads.')

                thread_list = get_threads()

                for thread in self.excluded_threads:
                    if thread in thread_list:
                        logger.debug('Removing excluded thread: ' + thread)

                        thread_list.remove(thread)

                logger.info('Gathering posts from threads.')

                thread_count = len(thread_list)

                thread_loops = 0
                for thread in thread_list:
                    thread_loops += 1

                    logger.info('Thread #' + str(thread_loops) + ' of ' + str(thread_count))

                    if thread not in thread_archive:
                        thread_archive[thread] = []

                    post_list = get_posts(thread_num=thread)
                    logger.debug('post_list: ' + str(post_list))

                    #thread_archive[thread] = post_list
                    for post in post_list:
                        if post not in thread_archive[thread]:
                            logger.debug('Appending post: ' + str(post))

                            thread_archive[thread].append(post)

                        else:
                            logger.debug('Skipping post. Already in archive.')

                    if thread_loops == self.thread_limit:
                        logger.debug('Thread limit reached. Breaking early.')

                        break

                logger.info('Filtering threads for relevant content.')

                relevant_threads = filter_threads(thread_archive)

                if os.path.isfile(thread_archive_file):
                    with open(thread_archive_file, 'r', encoding='utf-8') as file:
                        thread_data = json.load(file)

                else:
                    thread_data = {}

                for thread in relevant_threads:
                    logger.info('Relevant thread: ' + str(thread))

                    if thread not in thread_data:
                        thread_data[thread] = []

                    for post in relevant_threads[thread]:
                        logger.info('Relevant post: ' + post)

                        if post not in thread_data[thread]:
                            thread_data[thread].append(post)

                logger.info('Writing relevant posts to json archive.')

                with open(thread_archive_file, 'w', encoding='utf-8') as file:
                    json.dump(thread_data, file, indent=4, sort_keys=True, ensure_ascii=False)

                self.last_updated = datetime.datetime.now()

                if self.analyze_sentiment == True:
                    thread_archive_trimmed = create_trimmed_archive(thread_data)

                    pprint(thread_archive_trimmed)

                    if thread_archive_trimmed['Exception'] == True:
                        logger.warning('Failed to create trimmed thread archive. Bypassing sentiment analysis.')

                    else:
                        del thread_archive_trimmed['Exception']

                        sentiment_results_list = []

                        sentiment_total = 0
                        for thread in thread_archive_trimmed:
                            if thread != 'Exception':
                                sentiment_total += len(thread_archive_trimmed[thread])

                        logger.debug('sentiment_total: ' + str(sentiment_total))

                        sentiment_count = 0
                        for thread in thread_archive_trimmed:
                            logger.debug('thread: ' + thread)

                            if thread != 'Exception':
                                for post in thread_archive_trimmed[thread]:
                                    logger.debug('post: ' + post)

                                    sentiment_count += 1

                                    logger.info('Analyzing sentiment for post #' + str(sentiment_count) + ' of ' + str(sentiment_total) + '.')

                                    sentiment_results = {'entities': [], 'entities_metadata': None,
                                                         'key_phrases': [], 'key_phrases_metadata': None,
                                                         'sentiment': [], 'sentiment_metadata': None,
                                                         'post': ''}

                                    sentiment_results['post'] = post

                                    sentiment_results['entities'], sentiment_results['entities_metadata'] = get_entities(post)

                                    #print(sentiment_results['entities'], sentiment_results['entities_metadata'])

                                    time.sleep(0.05)    # To prevent hitting API throttling limit (20/sec)

                                    sentiment_results['key_phrases'], sentiment_results['key_phrases_metadata'] = get_key_phrases(post)

                                    #print(sentiment_results['key_phrases'], sentiment_results['key_phrases_metadata'])

                                    time.sleep(0.05)    # To prevent hitting API throttling limit (20/sec)

                                    sentiment_results['sentiment'], sentiment_results['sentiment_metadata'] = get_sentiment(post)

                                    #print(sentiment_results['sentiment'], sentiment_results['sentiment_metadata'])

                                    time.sleep(0.05)    # To prevent hitting API throttling limit (20/sec)

                                    sentiment_results_list.append(sentiment_results)

                        logger.info('Sorting sentiment results and thresholding by score.')

                        sentiment_thresholded = threshold_sentiment_results(sentiment_results_list)

                        sentiment_results_return['result']['data'] = sentiment_thresholded

                        logger.info('Dumping sentiment analysis results to json file.')

                        with open(self.comprehend_results_file, 'w', encoding='utf-8') as file:
                            #json.dump(sentiment_results_list, file, indent=4, sort_keys=True, ensure_ascii=False)
                            json.dump(sentiment_thresholded, file, indent=4, sort_keys=True, ensure_ascii=False)

                        sentiment_results_return['result']['json'] = self.comprehend_results_file

                        sentiment_average_data = calc_sentiment_average(sentiment_thresholded)

                        if sentiment_average_data['Exception'] == False:
                            if self.slack_client != None:
                                #### SEND ALL NECESSECARY ALERT MESSAGES ####
                                # Don't proceed to next alert until success confirmation
                                # Make sure alerts sent from highest to lowest score
                                # Use sentiment_thresholded.pop()?

                                if len(sentiment_average_data['result']['positive']['posts']) > 0 or len(sentiment_average_data['result']['negative']['posts']) > 0:
                                    sentiment_message = '*Sentiment Analysis Results*\n\n'

                                    sentiment_message += '*_Average % Positive:_* ' + "{:.2f}".format(sentiment_average_data['result']['positive']['average'] * 100) + '%\n'

                                    post_count = 0
                                    for post in sentiment_average_data['result']['positive']['posts']:
                                        post_count += 1

                                        sentiment_message += '\n*Post #' + str(post_count) + ' (' + "{:.2f}".format(post[1] * 100) + '%)' + ':* ' + post[0] + '\n'

                                    sentiment_message += '\n'

                                    sentiment_message += '*_Average % Negative:_* ' + "{:.2f}".format(sentiment_average_data['result']['negative']['average'] * 100) + '%\n'

                                    post_count = 0
                                    for post in sentiment_average_data['result']['negative']['posts']:
                                        post_count += 1

                                        sentiment_message += '\n*Post #' + str(post_count) + ' (' + "{:.2f}".format(post[1] * 100) + '%)' + ':* ' + post[0] + '\n'

                                else:
                                    if len(relevant_threads) == 0:
                                        sentiment_message = '_No relevant posts found for sentiment analysis._'

                                    else:
                                        sentiment_message = '_No significant results found in sentiment analysis._'

                                alert_result = send_slack_alert(channel_id=slack_channel, message=sentiment_message, thread_id=slack_thread)

                                logger.debug('alert_result[\'Exception\']: ' + str(alert_result['Exception']))

                                logger.debug('alert_result[\'result\']: ' + str(alert_result['result']))

                            else:
                                logger.info('Slack alerts disabled. Skipping send of sentiment data message.')

                        else:
                            logger.exception('Exception while calculating sentiment ratio. Skipping Slack alert.')

                if self.persistent == True and loop_count < self.persistent_loops:
                    logger.info('Sleeping ' + str(self.loop_time) + ' seconds.')

                    time.sleep(self.persistent_loop_time)

                elif self.persistent == True:
                    logger.info('Completed all ' + str(self.persistent_loops) + ' persistence loops.')

                    break

                else:
                    logger.info('Persistent mode disabled. Search complete.')

                    break

            logger.debug('Completed successfully. Returning results and exiting.')

        except botocore.exceptions.NoCredentialsError as e:
            logger.exception('botocore.exceptions.NoCredentialsError raised in run_search().')
            logger.exception(e)

            sentiment_results_return['Exception'] = True

        except Exception as e:
            logger.exception('Exception raised in run_search().')
            logger.exception(e)

            sentiment_results_return['Exception'] = True

        except KeyboardInterrupt:
            logger.info('Exit signal received.')

            sentiment_results_return['Exception'] = True

            #sys.exit()

        finally:
            return sentiment_results_return


class KeywordCollector:
    def __init__(self):
        pass


    # Currency data from Coinmarketcap API input as json
    def cmc_to_keywords(self, json_data):
        #sentiment_keywords_status = True

        #sentiment_keywords = []

        sentiment_keywords_return = {'Exception': False, 'result': []}

        try:
            sentiment_keywords_return['result'].append(json_data['name'].lower())
            sentiment_keywords_return['result'].append(json_data['symbol'].lower())

            if json_data['website_slug'].lower() not in sentiment_keywords_return['result']:
                sentiment_keywords_return['result'].append(json_data['website_slug'])

        except Exception as e:
            logger.exception('Exception in KeywordCollector.cmc_to_keywords().')
            logger.exception(e)

            #sentiment_keywords_status = False
            sentiment_keywords_return['Exception'] = True

        finally:
            #return sentiment_keywords, sentiment_keywords_status
            return sentiment_keywords_return


if __name__ == '__main__':
    from multiprocessing import Process
    # 1 - Get all threads on main page
    # 2 - Save thread numbers to list
    # 3 - For each:
    #       a) get_posts()
    #       b) Search posts for keywords
    #           i. If found, save text (and media) to directory
    #       c) Sentiment analysis

    config_path = '../../TeslaBot/config/config.ini'

    flyonthewall = FlyOnTheWall(config_path=config_path, slack_alerts=True,
                                thread_limit=99, persistent=False,
                                analyze_sentiment=True, sentiment_results_max=20)#,
                                #positive_sentiment_threshold=0.10, negative_sentiment_threshold=0.10)

    ## Load keywords and excluded words from keyword file ##

    #keyword_file = 'keywords.txt'
    #flyonthewall.load_keywords(keyword_file)

    ## OR load keywords and excluded words from dictionary ##

    #sample_keyword_data = ['stellar', 'lumens', 'hyperledger', 'fairx', 'xlm']
    #sample_excluded_data = ['stra', 'stre', 'stri', 'stro', 'stru', 'stry']
    sample_keyword_data = ['stellar', 'xlm', 'lumens', 'hyperledger', 'fairx', 'btc']
    sample_excluded_data = []

    keyword_dict = {'keywords': sample_keyword_data,
                    'excluded': sample_excluded_data}

    flyonthewall.load_keywords(keyword_data=keyword_dict)

    #flyonthewall.purge_old_data()

    sample_exchange = 'TestExchange'
    sample_market = 'TEST-MARKET'

    sample_slack_channel = 'CAX1A4XU1'
    sample_slack_thread = 1528088774.000041

    #arguments = (, )
    arguments = tuple()

    keyword_arguments = {'exchange': sample_exchange, 'market': sample_market,
                         'slack_channel': sample_slack_channel, 'slack_thread': sample_slack_thread,
                         'positive_sentiment_threshold': 0.682, 'negative_sentiment_threshold': 0.682,
                         'purge_old_data': True}

    sentiment_process = Process(target=flyonthewall.run_search, args=arguments, kwargs=keyword_arguments, name='sentiment_analysis_test')

    sentiment_process.start()

    """
    sentiment_results = flyonthewall.run_search(exchange=sample_exchange, market=sample_market,
                                                slack_channel=sample_slack_channel, slack_thread=sample_slack_thread,
                                                positive_sentiment_threshold=0.682, negative_sentiment_threshold=0.682,
                                                purge_old_data=True)
    """

    while (sentiment_process.is_active()):
        logger.info('Doing other stuff...')

        time.sleep(1)

    logger.info('Joining process to confirm completion and exit cleanly.')

    sentiment_process.join()

    print('SENTIMENT RESULTS:')
    pprint(sentiment_results)

    logger.debug('Last Updated: ' + str(flyonthewall.last_updated))

    logger.debug('Done.')
