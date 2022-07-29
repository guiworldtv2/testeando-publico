import re
import urllib.request
from urllib.request import urlopen

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests


# Function to map category IDs to category names
def map_categories(clip_categories, category_map):
    clip_categories['main categories'] = np.empty((len(clip_categories), 0)).tolist()
    clip_categories['sub categories'] = np.empty((len(clip_categories), 0)).tolist()

    for i in range(len(clip_categories)):
        all_categories = clip_categories.at[i, 'categories'].split(', ')
        for cat in all_categories:
            cat_map = category_map[category_map['category_id'] == int(cat)]
            parent_id = cat_map.at[cat_map.index[0], 'parent_id']
            if parent_id == 0:
                clip_categories.at[i, 'main categories'].append(cat_map.at[cat_map.index[0], 'name'])
            else:
                parent_cat_map = category_map[category_map['category_id'] == parent_id]
                clip_categories.at[i, 'sub categories'].append([cat_map.at[cat_map.index[0], 'name'],
                                                                parent_cat_map.at[parent_cat_map.index[0], 'name']])

    return clip_categories


# Function to append categories to initial dataframe, takes in two Pandas dataframes
def insert_categories(data, clip_categories):
    data['main categories'] = np.empty((len(data), 0)).tolist()
    data['sub categories'] = np.empty((len(data), 0)).tolist()
    no_matching_clip_id = 0

    for i in range(len(clip_categories)):
        clip_info = clip_categories.iloc[[i]]
        clip_id = clip_info.at[i, 'clip_id']
        clip_id_index1 = data[data['id'] == clip_id]
        clip_id_index2 = data[data['clip_id'] == clip_id]
        if len(clip_id_index1) is 0:
            if len(clip_id_index2) is 0:
                no_matching_clip_id += 1
            else:
                data.at[(clip_id_index2.index[0]), 'main categories'] = clip_info.at[i, 'main categories']
                data.at[(clip_id_index2.index[0]), 'sub categories'] = clip_info.at[i, 'sub categories']
        else:
            data.at[(clip_id_index1.index[0]), 'main categories'] = clip_info.at[i, 'main categories']
            data.at[(clip_id_index1.index[0]), 'sub categories'] = clip_info.at[i, 'sub categories']

    return data


def load_whole_file(file_path, clip_category_file_path, category_map_file_path):
    data = pd.read_csv(file_path, encoding="ISO-8859-1")
    clip_categories = pd.read_csv(clip_category_file_path)
    category_map = pd.read_csv(category_map_file_path)
    clip_categories = map_categories(clip_categories, category_map)
    data = insert_categories(data, clip_categories)
    return data


def get_updated_captions_for_whole_file(data):
    print("Getting new captions for the whole dataset...")

    for id in data['id']:

        url = 'https://vimeo.com/' + str(id)
        url_valid = url_is_alive(url)

        if url_valid:  # check if url is valid
            vimeo_webpage = requests.get(url)

            content = vimeo_webpage.text  # get content from webpage
            soup = BeautifulSoup(content, 'html.parser')

            if soup.find('div', attrs={
                'class': 'clip_details-description description-wrapper iris_desc'}) is not None:
                # get the video description (all paragraphs instead of first paragraph
                article_soup = [s.get_text(separator=" ", strip=True) for s in soup.find('div', attrs={
                    'class': 'clip_details-description description-wrapper iris_desc'}).find_all(
                    'p')]

                index = data.loc[data['id'] == id].index[0]

                data.loc[index, 'caption'] = ' '.join(article_soup)  # update the caption of our train dataset
    print("Finished getting new captions for the train file. ")

    return data


def load_train_and_test_files(file_path, clip_category_file_path, category_map_file_path):
    """Loads excel files into train and test dataframes"""

    data = load_whole_file(file_path, clip_category_file_path, category_map_file_path)

    np.random.seed(seed=0)
    indices = np.random.rand(len(data)) < 0.8
    train = data[indices]
    test = data[~indices]
    return [train, test]


def load_clips_categories(file_path):
    clip_categories = pd.read_csv(file_path, encoding="ISO-8859-1")
    return clip_categories


def url_is_alive(url):
    """Checks that a given URL is reachable."""
    request = urllib.request.Request(url)
    request.get_method = lambda: 'HEAD'

    try:
        urllib.request.urlopen(request)
        return True
    except urllib.request.HTTPError:
        return False


def get_unknown_clip_categories(data_path, clip_category_file_path, category_map_file_path):
    data = load_whole_file(data_path, clip_category_file_path, category_map_file_path)
    clip_categories = load_clips_categories(clip_category_file_path)
    counter = 0
    clip_counter = 0
    print("Trying to extract categories for videos that do not have a category...")
    for id in data['id']:

        if id not in clip_categories.clip_id.values:  # For each clip id that does not have a category
            url = 'https://vimeo.com/' + str(id)
            url_valid = url_is_alive(url)

            if url_valid:  # check if url is valid

                vimeo_webpage = urlopen(url)

                content = vimeo_webpage.read()  # get content from webpage
                soup = BeautifulSoup(content, 'lxml')

                scripts = soup.find_all('script')  # get all scripts of webpage
                for script in scripts:

                    if script.string is not None:

                        if "var _gtm" in script.string:  # if the script starts with var _gtm

                            text = [x.strip() for x in script.text.split(';')]
                            clip_variables = text[0]
                            var = [re.sub(r'\W+', '', x.strip().split(':')[1]) for x in clip_variables.split(',') if
                                   "category" in x]
                            clip_counter = clip_counter + 1
                            if var[0] is not '':
                                # print(var[0])
                                # print("buraya girdim")
                                counter = counter + 1
    print("Number of new clips with categories {}".format(counter))
    print("Number of total clips investigated {}".format(clip_counter))
    return counter


class PandaFrames(object):
    def __init__(self, filepath, clip_category_file_path, category_map_file_path):
        """Loads excel files into DataFrames and updated the captions of the videos."""

        print("Loading training and test files into Panda Data Frames..")
        self.pandaframes = load_train_and_test_files(filepath, clip_category_file_path, category_map_file_path)
        print("Panda Data Frames are ready.")
        # self.get_new_captions_for_train_file()
        # self.get_new_captions_for_test_file()
        print("We are not extracting new captions temporarily. ")

    def get_train_file(self):
        """Return Panda Dataframe Training File."""
        train = self.pandaframes[0]
        train = train.reset_index()
        train = train.drop(['Unnamed: 0', 'index'], axis=1)
        return train

    def get_test_file(self):
        """Return Panda Dataframe Test File."""

        test = self.pandaframes[1]
        test = test.reset_index()
        test = test.drop(['Unnamed: 0', 'index'], axis=1)
        return test

    def get_new_captions_for_train_file(self):
        """Gets extended captions for each video in Training Dataset"""

        print("Getting new captions for the train file...")
        train = self.get_train_file()

        for id in train['id']:

            url = 'https://vimeo.com/' + str(id)
            url_valid = url_is_alive(url)

            if url_valid:  # check if url is valid
                vimeo_webpage = urlopen(url)

                content = vimeo_webpage.read()  # get content from webpage
                soup = BeautifulSoup(content, 'html.parser')

                if soup.find('div', attrs={
                    'class': 'clip_details-description description-wrapper iris_desc'}) is not None:
                    # get the video description (all paragraphs instead of first paragraph
                    article_soup = [s.get_text(separator=" ", strip=True) for s in soup.find('div', attrs={
                        'class': 'clip_details-description description-wrapper iris_desc'}).find_all(
                        'p')]

                    index = train.loc[train['id'] == id].index[0]

                    train.loc[index, 'caption'] = ' '.join(article_soup)  # update the caption of our train dataset

        print("Finished getting new captions for the train file. ")

    def get_new_captions_for_test_file(self):
        """Gets extended captions for each video in Test Dataset"""

        print("Getting new captions for the test file...")

        test = self.get_test_file()

        for id in test['id']:

            url = 'https://vimeo.com/' + str(id)
            url_valid = url_is_alive(url)

            if url_valid:  # check if url is valid
                vimeo_webpage = urlopen(url)

                content = vimeo_webpage.read()  # get content from webpage
                soup = BeautifulSoup(content, 'html.parser')

                if soup.find('div', attrs={
                    'class': 'clip_details-description description-wrapper iris_desc'}) is not None:
                    # get the video description (all paragraphs instead of first paragraph)
                    article_soup = [s.get_text(separator=" ", strip=True) for s in soup.find('div', attrs={
                        'class': 'clip_details-description description-wrapper iris_desc'}).find_all(
                        'p')]

                    index = test.loc[test['id'] == id].index[0]

                    test.loc[index, 'caption'] = ' '.join(article_soup)  # update the caption of our train dataset
        print("Finished getting new captions for the test file.")
