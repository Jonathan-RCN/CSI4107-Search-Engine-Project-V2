"""
Title: Corpus Pre-processing Module

Project: CSI4107 Project
Version: Vanilla System
Component: Module 2

Created: 22 Jan 2020
Last modified: 31 Jan 2020

Author: Jonathan Boerger
Status: Completed

Description: This module takes an HTML documents and extracts course information to create
a XML document corpus.

Known issues:
    -> There is still some french text in the title/descriptions.
        |-> However there is no simple way of removing this text (would require manual extraction)
        |-> Given that it has minimal impact on other modules and zero impact on functionality,
             this is not a high priority issue
"""


import os
import xml.etree.ElementTree as xml
import bs4
from bs4 import BeautifulSoup
import config

class Course:
    """Course holds the information for courses."""

    def __init__(self, course_id, title, description, language):
        """Course init."""
        self.course_id = course_id
        self.title = title
        self.description = description
        self.language = language

    def sanitize_course_info(self):
        """Clean up the course_html_div_element information from the file."""
        # filtering out french courses
        language_specifier = self.course_id[5]

        if language_specifier in ['5', '7', '6']:
            self.language = "French"
        else:
            # Stripping french title from bilingual course_html_div_element
            if self.title.find('/') > 0:
                self.title = self.title.replace(
                    '(3 crÃ©dits / 3 units)', "(3 units)")
                self.title = self.title[self.title.find('/') + 2:]
        # Stripping french description from bilingual course_html_div_element
        if self.description.find('. / ') > 0:
            # '. /' delineates english and french description
            self.description = (self.description[self.description.find('. / ') + 4:])

    def __str__(self):
        return self.course_id

def parse(corpus):
    """
    This method takes the provided HTML file and identifies all courses, extract the relevant
     information, sanitizes the information and compiles a corpus in XML format.

    :param html_filename: Filename of the source HTML file
    :param corpus_filename: Filename of the XML corpus
    :return: Corpus of documents contained in an XML file
    """
    html_filename = config.CORPUS[corpus]['source']
    corpus_filename = config.CORPUS[corpus]['corpusxml']
    # Checking to see if file already exist
    if os.path.exists(corpus_filename) is True:
        # Ensuring file has actual content
        if os.path.getsize(corpus_filename) <= 0:
            pass
        # If file exist and has content, then the method exits
        else:
            print("Parsed file already exists")
            return

    root = xml.Element("Courses")
    with open(html_filename, "r") as file:
        data = file.read()
        soup = BeautifulSoup(data, 'html.parser')

        # course_div_list is a list of all HTML div element which contains
        # all information for one course_html_div_element

        course_div_list = soup.findAll("div", {"class": "courseblock"})

        # accessing each individual course_html_div_element course_div_block
        index = 0
        for course_div in course_div_list:

            # getting relevant information from the HTML elements
            course = get_values(course_div
                                )
            # only process courses which are english
            if course.language == "English":
                # only process course_html_div_element which have a
                # course_html_div_element description
                if course.description == "No description available for this " \
                                         "course_html_div_element":
                    pass
                # adding course_html_div_element to the XML corpus
                else:
                    xml_writer(root, course, corpus_filename, index)
                    index += 1


def xml_writer(root, course, filename, index):
    """
    This methods takes a course_html_div_element information after having been sanitized
    and adds it to the XML corpus as a new document.

    :param root: Root element of the XML corpus
    :param course: Instance of course_html_div_element object containing all
                   information to be added to corpus
    :param filename: Name of XML corpus
    :return: course_html_div_element information added to corpus
    """
    user_element = xml.Element("Course")
    user_element.set("doc_id", str(index))
    root.append(user_element)
    course_id = xml.SubElement(user_element, "course_id")
    course_id.text = course.course_id
    course_title = xml.SubElement(user_element, "course_title")
    course_title.text = course.title
    course_description = xml.SubElement(user_element, "course_description")
    course_description.text = course.description
    tree = xml.ElementTree(root)
    with open(filename, "wb") as file:
        tree.write(file)


def get_values(course_html_div_element):
    """
    This methods takes html code and extracts all relevant course information and
    instantiates a course class object to store this info

    :param course_html_div_element: HTML div element which contains course info
    :return: Instance of course class with course info for course_id, title and description
    """

    # creating instance of course class
    current_course = Course(
        "xxx", "Nil", "No description available for this course_html_div_element", "English")

    for html_element in course_html_div_element:
        element_type = type(html_element)
        if element_type is bs4.element.Tag:

            class_type = html_element['class'][0]

            if class_type == "courseblocktitle":
                title = html_element.get_text()
                current_course.course_id = title[:8]
                current_course.title = title[9:]

            if class_type == "courseblockdesc":
                description = html_element.get_text()
                current_course.description = description

    current_course.sanitize_course_info()
    return current_course
