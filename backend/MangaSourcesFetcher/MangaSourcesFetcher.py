import pymongo
import datetime
import params

def addMangaSource(url, name=None, queryURLTemplate=None):
    if name is None:
        name = url
    name = name.strip()

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

def addManga(mangaName, otherNames=[]):
    mangaName = mangaName.strip()

    client = pymongo.MongoClient(params.MONGODB_HOST, params.MONGODB_PORT)
    db = client[params.DB_NAME]
    manga = db[params.MANGA_COLLECTIONS]
    
    # Find if manga is already in the collection
    if manga.find_one({params.MANGA_NAMES_FIELD: mangaName}):
        return 0
    
    # Find manga by other names in current collection
    found = False
    manga_id = None
    currentNames = []
    for name in otherNames:
        key = {params.MANGA_NAMES_FIELD: name}
        result = manga.find_one(key)
        if result is None: 
            continue
        found = True
        manga_id = result[params.MANGA_ID_FIELD]
        currentNames = result[params.MANGA_NAMES_FIELD]
        break

    now = datetime.datetime.utcnow()
    if found:
        key = {params.MANGA_ID_FIELD: manga_id}
        data = {
            params.MONGODB_SET_ON_INSERT: { 
                 params.MANGA_INSERTION_DATE_FIELD: now 
                 },
             params.MONGODB_SET: {
                 params.MANGA_NAMES_FIELD: list(set(currentNames + [mangaName] + otherNames)),
                 params.MANGA_LAST_UPDATE_FIELD: now
                 }
            }
        result = manga.update(key, data, upsert=True)
    else: 
        data = {
            params.MANGA_INSERTION_DATE_FIELD: now,
            params.MANGA_NAMES_FIELD: list(set(currentNames + [mangaName] + otherNames)),
            params.MANGA_LAST_UPDATE_FIELD: now
        }
        result = manga.insert(data),
    return result

def findMangaSourceID(sourceName):
    client = pymongo.MongoClient(params.MONGODB_HOST, params.MONGODB_PORT)
    db = client[params.DB_NAME]
    manga_source = db[params.MANGA_SOURCE_COLLECTIONS]
    
    key = {params.MANGA_SOURCE_NAME_FIELD: sourceName}
    result = manga_source.find_one(key)

    if result:
        return result[params.MANGA_SOURCE_ID_FIELD]
    else:
        return -1

def findMangaID(mangaName):
    client = pymongo.MongoClient(params.MONGODB_HOST, params.MONGODB_PORT)
    db = client[params.DB_NAME]
    manga = db[params.MANGA_COLLECTIONS]
    
    key = {params.MANGA_NAMES_FIELD: mangaName}
    result = manga.find_one(key)

    if result:
        return result[params.MANGA_ID_FIELD]
    else:
        return -1

def addManga_MangaSource_Pair(Manga_id, MangaSource_id, url):
    client = pymongo.MongoClient(params.MONGODB_HOST, params.MONGODB_PORT)
    db = client[params.DB_NAME]
    manga_source_pair = db[params.MANGA_SOURCE_PAIR_COLLECTIONS]
    
    now = datetime.datetime.utcnow()
    key = {
        params.MANGA_SOURCE_PAIR_MANGA_ID_FIELD: Manga_id,
        params.MANGA_SOURCE_PAIR_SOURCE_ID_FIELD: MangaSource_id
        }
    data = {
        params.MONGODB_SET_ON_INSERT: { 
            params.MANGA_SOURCE_PAIR_INSERTION_DATE_FIELD: now 
            },
        params.MONGODB_SET: {
            params.MANGA_SOURCE_PAIR_URL_FIELD: url,
            params.MANGA_SOURCE_PAIR_LAST_UPDATE_FIELD: now
            }
    }
    result = manga_source_pair.update(key, data, upsert=True)
    return result

if __name__ == '__main__':
    addMangaSource(url='http://fanfox.net/', 
                   name='Manga Fox', 
                   queryURLTemplate='http://fanfox.net/manga{/manga_name}')
    
    addMangaSource(url='https://mangakakalot.com/',
                   name='Mangakakalot',
                   queryURLTemplate='https://mangakakalot.com/search{/manga_name}')

    addManga("Ms. Corporate Slave Wants to be Healed by a Loli Spirit")
    addManga("Shachiku-san wa Youjo Yuurei ni Iyasaretai", otherNames=['Ms. Corporate Slave Wants to be Healed by a Loli Spirit', '社畜さんは幼女幽霊に癒されたい'])

    source_id = findMangaSourceID('Manga Fox')
    manga_id = findMangaID('Shachiku-san wa Youjo Yuurei ni Iyasaretai')
    addManga_MangaSource_Pair(manga_id, source_id, 
                              url='http://fanfox.net/manga/ms_corporate_slave_wants_to_be_healed_by_a_loli_spirit/')
    source_id = findMangaSourceID('Mangakakalot')
    addManga_MangaSource_Pair(manga_id, source_id, 
                              url='https://mangakakalot.com/manga/my918978')
    