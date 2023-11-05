# a class to manage image caching

from database.database_util_postgres import DBPostgreSQL
from sql.schema import DB_KEYS_POSTGRES, ALL_TABLES, ALL_ENT
from urllib.request import urlretrieve
from dash import get_asset_url
import os
import os.path
import logging


class ImageCache(object):
    def __init__(self):
        self.db = DBPostgreSQL(DB_KEYS_POSTGRES)
        for entity in ALL_ENT:
            if not os.path.isdir(f'assets/{entity}'):
                os.mkdir(f'assets/{entity}')

    def cache_image(self, url, entity, id_val):
        image_ext = url.split('.')[-1]
        assert image_ext.lower() in ('jpg', 'jpeg')
        local_file_name, headers = urlretrieve(
            url, f'assets/{entity}/{id_val}.jpg')
        logging.info('downloaded image from discogs')
        return local_file_name

    def get_discogs_image_url(self, entity, id_val):
        tbl, id_col = self.get_table_name(entity)
        id_val = int(id_val)
        output = self.db._query(
            f"select image from public.{tbl} where {id_col} = {id_val};")
        image_url = output[0][0]
        return image_url

    @staticmethod
    def get_table_name(entity):
        tbl_name = f'{entity}s'
        id_col = f'{entity}_id'
        return tbl_name, id_col

    def get_image(self, entity, id_val):
        tbl_name, id_col = self.get_table_name(entity)
        try:
            image_path = f'assets/{entity}/{id_val}.jpg'
            assert os.path.isfile(image_path)
            logging.info('image found in cache')
        except:
            logging.info('image not found in cache, downloading from discogs')
            url = self.get_discogs_image_url(entity, id_val)
            image_path = self.cache_image(url, entity, id_val)
        return image_path
    
    def get_artist_image(self, artist_id):
        return self.get_image(entity='artist', id_val=artist_id)

    def get_label_image(self, label_id):
        return self.get_image(entity='label', id_val=label_id)

    def get_release_image(self, release_id):
        return self.get_image(entity='release', id_val=release_id)



