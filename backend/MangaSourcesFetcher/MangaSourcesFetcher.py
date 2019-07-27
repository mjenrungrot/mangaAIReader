import pymongo
import datetime
import params

def addMangaSource(url, name=None, queryURLTemplate=None):
    client = pymongo.MongoClient(params.MONGODB_HOST, params.MONGODB_PORT)
    db = client[params.DB_NAME]
    manga_sources = db[params.MANGA_SOURCE_COLLECTIONS]

    now = datetime.datetime.utcnow()
    key = {params.MANGA_SOURCE_URL_FIELD: url}
    data = {
         params.MONGODB_SET_ON_INSERT: { 
             params.MANGA_SOURCE_INSERTION_DATE_FIELD: now 
             },
         params.MONGODB_SET: {
             params.MANGA_SOURCE_NAME_FIELD: name,
             params.MANGA_SOURCE_QUERYURL_FIELD: queryURLTemplate,
             params.MANGA_SOURCE_LAST_UPDATE_FIELD: now
             }
         }

    result = manga_sources.update(key, data, upsert=True)
    return result

if __name__ == '__main__':
    addMangaSource(url='http://fanfox.net/', 
                   name='Manga Fox', 
                   queryURLTemplate='http://fanfox.net/manga{/manga_name}')