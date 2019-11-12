from typing import NamedTuple, Tuple
from datetime import datetime

import praw


class WordListRequestConfig(NamedTuple):
    platform: str  # reddit vs. Twitter
    source_type: str  # user, hashtag, subreddit, etc.
    source_value: str  # the actual source e.g. 'r/python'
    num_posts: int
    time: Tuple[datetime, datetime]  # time[0] = min time, time[1] max time
    sort: str


class DataInterfaceManager:
    """Manages multiple data interface classes at once, delegates function calls to appropriate data interfaces.
    Interfaces are stored in a dictionary that is automatically populated based on the api_key_dict passed in.
    Keys are platform names and values are the respective data interface objects initialized with their respective keys."""

    def __init__(self, api_key_dict: dict, excluded_from_autopopulate=None):
        self.api_key_dict = api_key_dict
        self.interfaces = {}
        self.autopopulate(exclude_list=excluded_from_autopopulate)
        self.platforms = self.interfaces.keys()

    def autopopulate(self, exclude_list):
        """Automatically populates the self.interfaces dict from self.api_key_dict with valid interfaces"""
        for platform, api_keys in self.api_key_dict.items():
            expected_class_name = f'{platform.capitalize()}Interface'
            if expected_class_name not in globals() or (exclude_list and platform not in exclude_list):
                print('f')
                continue
            interface_class = globals()[expected_class_name]
            self.interfaces[platform] = interface_class(api_keys)

    def request_word_list(self, request_config: WordListRequestConfig):
        if request_config.platform not in self.platforms:
            return None  # Maybe this should raise an error? e.g. APINotImplenetedError
        appropriate_interface = self.interfaces[request_config.platform]
        appropriate_interface.get_word_list(request_config)


class DataInterface:
    """Super class for all data interfaces. Initializes api client and handles getting word lists from valid sources.
    All child classes should be adhere to the following naming convention:
        -The name of the class should be "PlatformInterface", where Platform is the name of the platform
            with a capitalized first letter.
        -Functions that retrieve from sources should be named "from_source", where source is a string representation of
            what the source is called, and is also a member of the class' valid_sources list."""

    def __init__(self, api_class, api_keys, platform, valid_source_types, valid_sort_types):
        self.platform = platform
        self.valid_source_types = valid_source_types
        self.valid_sort_types = valid_sort_types
        self.api_class = api_class
        self.api_keys = api_keys
        self.api = self.init_api_client()

    def __repr__(self):
        return f'<{self.platform.upper()} INTERFACE: {self.api}>'

    def init_api_client(self):
        return self.api_class(**self.api_keys)

    def get_word_list(self, request_config: WordListRequestConfig):
        if request_config.platform != self.platform or request_config.source_type not in self.valid_source_types:
            return None
        fetch_function = getattr(self, f'from_{request_config.source_type}')
        return fetch_function(request_config)


class RedditInterface(DataInterface):
    def __init__(self, api_keys):
        valid_source_types = ['subreddit', 'user', 'post']
        valid_sort_types = ['top', 'new', 'controversial']
        super().__init__('reddit', praw.Reddit, api_keys, valid_source_types, valid_sort_types)

    def from_subreddit(self, request_config: WordListRequestConfig):
        subreddit = self.api.subreddit(request_config.source_value)
        submissions_getter = getattr(subreddit, request_config.sort)
        submissions = submissions_getter(limit=request_config.num_posts)
        words = []
        for s in submissions:
            words.extend(s.title.split())
        print(words)
        return words

    def from_user(self, request_config: WordListRequestConfig):
        pass

    def from_post(self, request_config: WordListRequestConfig):
        pass


if __name__ == '__main__':
    from config import API_KEYS
    r = RedditInterface(API_KEYS['reddit'])
    print(r)
    r.get_word_list(WordListRequestConfig('reddit', 'subreddit', 'python', 1000, 'popularity', 'new'))
