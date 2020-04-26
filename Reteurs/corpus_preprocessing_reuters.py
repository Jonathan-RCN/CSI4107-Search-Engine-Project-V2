import os

from nltk.corpus import reuters
import nltk

nltk.download('reuters')
import config
import bs4
from bs4 import BeautifulSoup
import xml.etree.ElementTree as xml
from datetime import datetime
from tqdm import tqdm



def extract_reuters_articles__efficient():
    xml_corpus_filename = config.CORPUS[config.REUTERS]['corpusxml']
    if os.path.exists(xml_corpus_filename):
        if os.path.getsize(xml_corpus_filename) > 0:

            tree = xml.parse(xml_corpus_filename)
            root = tree.getroot()
            if root[21577]:
                print('The XML file exist and contains the required number of articles.')
                return
            else:
                print('The XML file exist but does not contains the required number of articles.')

    with tqdm(total=21578) as pbar:
        article_info = []
        for sgm_file in os.listdir('SGM Files'):

            with open(f'SGM Files/{sgm_file}', "r") as file:
                data = file.read()
                html_data = BeautifulSoup(data, 'html.parser')

                article_list = html_data.find_all('reuters')

                for article in article_list:

                    article_id = article.attrs['newid']
                    # print(article_id)

                    if article.find('title'):
                        article_title = article.find('title').text
                        article_title = text_filter(article_title)
                        article_title = article_title.strip()
                    # print(article_title)
                    else:
                        article_title = ""
                        # print('There is no title for this article')
                    if article.find('body'):
                        article_body = article.find('body').text

                        article_body = text_filter(article_body)

                        article_body = article_body.strip()
                    # print(article_body)
                    else:
                        article_body = ""
                    # print('There is no text body for this article')

                    if article.find('topics'):
                        article_topic_list_raw = article.topics

                        topic_list = []
                        for topics in article_topic_list_raw:
                            topic_list.append(topics.text)

                        if len(topic_list) == 0:
                            topic_string = ""
                            # print('There is no topics for this article')
                        else:

                            s = ', '
                            topic_string = s.join(topic_list)
                        # print(topic_string)
                    article_info.append([article_id, article_title, topic_string, article_body])
                    pbar.update(1)
        xml_writter__efficient(article_info, xml_corpus_filename)

        # print('===============================================================================')


def xml_writter__efficient(article_list, xml_filename):
    root = xml.Element("Reuters_Articles")
    with tqdm(total=21578) as pbar:
        with open(xml_filename, "wb") as file:
            for article in article_list:
                user_element = xml.Element("Article")
                user_element.set("doc_id", article[0])
                root.append(user_element)
                doc_id = xml.SubElement(user_element, "doc_id")
                doc_id.text = article[0]
                doc_title = xml.SubElement(user_element, "doc_title")
                doc_title.text = article[1]
                doc_body_text = xml.SubElement(user_element, "doc_body_text")
                doc_body_text.text = article[3]
                doc_topics = xml.SubElement(user_element, "doc_topics")
                doc_topics.text = article[2]
                pbar.update(1)

            tree = xml.ElementTree(root)
            tree.write(file)




def text_filter(text):
    text = text.replace('\r', "")
    text = text.replace('\n', " ")
    text = text.replace('\t', "")
    text = text.replace('     ', ' ')
    text = text.replace('Reuter ', '')
    text = text.replace('REUTER ', '')
    text = text.replace('reuter ', '')
    text = text.replace('Reuters ', '')
    text = text.replace('REUTERS ', '')
    text = text.replace('reuters ', '')
    text = text.replace('', '')
    text = text.replace('', '')
    text = text.replace('[B', '')
    return text

# def extract_reuters_articles():
#     documents = reuters.fileids()
#     doc_count=len(documents)
#     start_time=datetime.now()
#     root = xml.Element("Reuters_Articles")
#     with tqdm(total=doc_count) as pbar:
#
#         for sgm_file in os.listdir('SGM Files'):
#             print(sgm_file)
#             with open(f'SGM Files/{sgm_file}',"r") as file:
#                 data=file.read()
#                 html_data=BeautifulSoup(data, 'html.parser')
#
#
#                 article_list=html_data.find_all('reuters')
#
#                 for article in article_list:
#                     article_id=article.attrs['newid']
#                     #print(article_id)
#                     article_title=""
#                     if article.find('title'):
#                         article_title=article.find('title').text
#                         article_title=article_title.strip()
#                        # print(article_title)
#                     else:
#                         article_title = ""
#                         #print('There is no title for this article')
#                     if article.find('body'):
#                         article_body=article.find('body').text
#
#                         #get rid of tabs and newlines, carriage return and other miscanaleous items to have proper text
#                         article_body=article_body.replace('\r',"")
#                         article_body = article_body.replace('\n', " ")
#                         article_body = article_body.replace('\t', "")
#                         article_body=article_body.replace('     ',' ')
#                         article_body=article_body.replace('Reuter ','')
#                         article_body = article_body.replace('REUTER ', '')
#                         article_body = article_body.replace('reuter ', '')
#                         article_body = article_body.replace('Reuters ', '')
#                         article_body = article_body.replace('REUTERS ', '')
#                         article_body = article_body.replace('reuters ', '')
#                         article_body=article_body.replace('','')
#                         article_body=article_body.strip()
#                        # print(article_body)
#                     else:
#                         article_body = ""
#                        # print('There is no text body for this article')
#
#                     if article.find('topics'):
#                         article_topic_list_raw=article.topics
#
#                         topic_list=[]
#                         for topics in article_topic_list_raw:
#                             topic_list.append(topics.text)
#
#                         if len(topic_list)==0:
#                             topic_string = ""
#                             #print('There is no topics for this article')
#                         else:
#
#                             s = ', '
#                             topic_string = s.join(topic_list)
#                            # print(topic_string)
#                     xml_writter(article_id,article_title,article_body,topic_string,config.CORPUS[config.REUTERS]['corpusxml'],root)
#                     pbar.update(1)
#
#
#                     #print('===============================================================================')
#     end_time=datetime.now()
#     total_time=end_time-start_time
#     print(total_time)
# def xml_writter(article_id, article_title,article_body,article_topics,xml_filename,root):
#
#     user_element = xml.Element("Article")
#     user_element.set("doc_id", article_id)
#     root.append(user_element)
#     doc_id = xml.SubElement(user_element, "doc_id")
#     doc_id.text = article_id
#     doc_title = xml.SubElement(user_element, "doc_title")
#     doc_title.text = article_title
#     doc_topics = xml.SubElement(user_element, "doc_topics")
#     doc_topics.text=article_topics
#     doc_body_text = xml.SubElement(user_element, "doc_body_text")
#     doc_body_text.text =article_body
#     tree = xml.ElementTree(root)
#     with open(xml_filename, "wb") as file:
#         tree.write(file)