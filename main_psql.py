import psycopg2
import requests
from bs4 import BeautifulSoup

# Establish database connection
conn = psycopg2.connect(host="127.0.0.1",
                       port="5432",
                       user="postgres",
                       password="iampw",
                       database="webscraping")

# Get a database cursor
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS book;")
cursor.execute("DROP TABLE IF EXISTS genre CASCADE;")
conn.commit()

# Create tables
cursor.execute("""
    CREATE TABLE genre (
        id INTEGER NOT NULL PRIMARY KEY,
        genre VARCHAR NOT NULL
    );
""")

cursor.execute("""
    CREATE TABLE book (
        id INTEGER NOT NULL PRIMARY KEY,
        title VARCHAR NOT NULL,
        genre_id INTEGER NOT NULL REFERENCES genre (id),
        price DECIMAL NOT NULL,
        star INTEGER NOT NULL,
        url VARCHAR NOT NULL
    );
""")

# cursor.execute("INSERT INTO genre VALUES (%s, %s)", (1, "book1") )

conn.commit()

baseURL = 'http://books.toscrape.com/'

r = requests.get('http://books.toscrape.com/')

# Populate genre table 
soup = BeautifulSoup(r.text, 'html.parser')
uls = soup.findAll('ul', class_='nav nav-list')
urls = [] # url to each by-genre page 

for ul in uls:

    # Find every href tag in nav nav-list class
    for i, a in enumerate(ul.find_all('a', href=True)):
        genre_info = a['href'].split('/')
        if i == 0:
            genre_id, genre = 1, "book"
        else:
            genre_id = genre_info[3].split('_')[1]
            genre = genre_info[3].split('_')[0]
        genre_url = baseURL + a['href']
        urls.append( [genre_url, genre_id] )
        
        # insert to genre table
        cursor.execute("""
            INSERT INTO genre (id, genre)
            VALUES (%s, %s);
        """,
        (
            genre_id,
            genre
        ))

conn.commit()

star_conversion = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}

id = 0

# populate book table
for pack in urls[1:]:
    url = pack[0]
    genre_id = pack[1]

    targetURL = requests.get(url)
    coldSoup = BeautifulSoup(targetURL.text, 'html.parser')

    books = coldSoup.findAll("article", class_="product_pod")
    
    for book in books:
        id += 1
        # get star rate
        star_tag = book.find('p')['class'][1]
        star = star_conversion[star_tag]

        # get book name
        title = book.find("h3").find("a")["title"]

        # get book price
        price_tag = book.find("div", class_="product_price").find("p").text
        price = float(price_tag[2:])
        
        # get url
        url_tag = book.find("div", class_="image_container").find("a")["href"].split("/")[3:]
        book_url = '/'.join(url.split("/")[:4] + url_tag)


        cursor.execute("""
            INSERT INTO book (id, title, genre_id, price, star, url) 
            VALUES (%s, %s, %s, %s, %s, %s);
        """, 
        (
            id,
            title,
            genre_id,
            price,
            star,
            book_url,
        ))

conn.commit()

cursor.close()
conn.close()