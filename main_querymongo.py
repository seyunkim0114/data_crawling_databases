import pymongo
from pymongo import MongoClient

client = pymongo.MongoClient(host="localhost", port=27017)

db = client.webscraping
book_collection = db.books

# Find books more expensive than the given amount
def find_more_expensive(price):
    return book_collection.find( {"price" : {'$gte': price}} ).pretty()
    
# Find books less expensive than the given amount
def find_less_expensive(price):
    return book_collection.find( {"price" : {'$lte':price}} ).pretty()

def find_book_by_title(title):
    return book_collection.find( {"title" : title} )

def find_book_by_UTC(utc):
    return book_collection.find( {"UTC" : utc} )

def find_book_by_star(star):
    return book_collection.find( {"star" : star} )

def find_book_more_star(star):
    return book_collection.find( {"star" : {'$gte' : star} })

def find_book_starts_with(c):
    return book_collection.find( {"title" : { "$regex": f'^{c}'}} )

def find_book_by_genre(genre):
    return book_collection.find( {"genre" : genre})

def find_book_by_gt_price(price):
    return book_collection.find( {"price" : { '$gte': price }})

def find_book_if_available(title):
    res = book_collection.find( {"title" : title} )
    for i in res:
        if i["Availability"] > 0:
            return True
    return False

res1 = find_book_by_genre("travel")
for i in res1:
    print(i["title"])

res2 = find_book_by_gt_price(40.00)
for i in res2:
    print(i["title"], i["price"])

res3 = find_book_if_available("Shameless")
print(f'Availability of Shamless: {res3}')
client.close()
