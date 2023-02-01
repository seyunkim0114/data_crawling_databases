from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
import pprint
import re

# Connect to MongoDB
client = MongoClient(host="localhost", port=27017)
db = client.webscraping
book_collection = db.books


baseURL = 'http://books.toscrape.com/'

r = requests.get('http://books.toscrape.com/')



star_conversion = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}

id = 0

page=1
while page <= 50:
    url = f'http://books.toscrape.com/catalogue/category/books_1/page-{page}.html'
    r = requests.get(url)

    soup = BeautifulSoup(r.text, 'html.parser')

    # uls = soup.findAll('ol', class_="row")
    # # print
    # for ul in uls:
    books = soup.findAll("article", class_="product_pod")

    for book in books:
        insert_book = {}

        id += 1
        insert_book["id"] = id

        # get star rate
        star_tag = book.find('p')['class'][1]
        star = star_conversion[star_tag]
        insert_book["star"] = star

        # get book name
        title = book.find("h3").find("a")["title"]
        insert_book["title"] = title

        # get book price
        image_tag = book.find("div", class_="product_price")
        price_tag = image_tag.find("p").text
        price = float(price_tag[2:])
        insert_book["price"] = price

        # get book availability
        # instock = image_tag.find("p", class_='instock availability')
    
        # # get url
        url_tag = book.find("div", class_="image_container").find("a")["href"].split('/')[2:]
        book_url = '/'.join(url.split("/")[:4] + url_tag)
        insert_book["url"] = book_url

        # print(id, title, price, star, book_url)
        
        # Individual book information
        bookSpec = requests.get(book_url)
        bookSpecSoup = BeautifulSoup(bookSpec.text, 'html.parser')
        spec = bookSpecSoup.find("table", class_="table table-striped")

        for tr in spec.findAll("tr"):
            # print(tr)
            th = tr.find("th").text
            td = tr.find("td").text
            if th == "Availability":
                td = int(re.findall(r'\d+', td)[0])
                # print(td)

            if th[:5] == "Price":
                td = float(re.findall("\d+\.\d+", td)[0])
                
            insert_book[th] = td


        res = book_collection.insert_one(insert_book)
        # print(book_collection.count_documents( {"title": "Don't Forget Steven"}))

    page += 1

# exit()
# Populate genre table 
soup = BeautifulSoup(r.text, 'html.parser')
uls = soup.findAll('ul', class_='nav nav-list')
urls = [] # url to each by-genre page 

for ul in uls:
    # Find every href tag in nav nav-list class
    for i, a in enumerate(ul.find_all('a', href=True)):
        # print(a)
        genre_info = a['href'].split('/')
        if i == 0:
            # genre_id, genre = 1, "book"
            continue
        else:
            genre_id = genre_info[2].split('_')[1]
            genre = genre_info[2].split('_')[0]
        genre_url = baseURL + "catalogue/category" + a['href'][2:]
        # print(genre_url)
        # populate book table
        targetURL = requests.get(genre_url)
        coldSoup = BeautifulSoup(targetURL.text, 'html.parser')

        books = coldSoup.findAll("article", class_="product_pod")
        for book in books:
            # insert_book = {}
            # get book name
            title = book.find("h3").find("a")["title"]
            # print(book_collection.count_documents( {"title": title}))
            if book_collection.count_documents( {"title": title}) > 0:
                # print("title")
                book_collection.update_one({"title" : title}, {'$set': {"genre" : genre} } )









client.close()


