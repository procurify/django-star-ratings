from __future__ import unicode_literals

import swapper

from .app_settings import Settings

__version__ = '0.9.2'

app_settings = Settings()


def get_star_ratings_rating_model_name():
    return swapper.get_model_name('star_ratings', 'Rating')


def get_star_ratings_rating_model():
    return swapper.load_model('star_ratings', 'Rating')