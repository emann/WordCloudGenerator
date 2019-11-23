import time
import re
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

from interfaces import WordListRequestConfig, DataInterfaceManager
from config import API_KEYS

dim = DataInterfaceManager(API_KEYS)
STOPWORDS |= {'RT'}


if __name__ == '__main__':
    word_list = dim.request_word_list(WordListRequestConfig('twitter', 'hashtag', 'impeachmentinquiry', 1000, None, 'top', None))
    word_list = filter(lambda x: not re.search(r'^https|^@|^#', x), word_list)
    word_string = ' '.join(word_list)
    wordcloud = WordCloud(width=800, height=800,
                          background_color='white',
                          stopwords=set(STOPWORDS),
                          min_font_size=10).generate(word_string)
    plt.figure(figsize=(8, 8), facecolor=None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.show()
