import requests
from bs4 import BeautifulSoup
import sqlite3

def create_db():
    conn = sqlite3.connect('books.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY,
            book_id INTEGER,
            name TEXT,
            author TEXT,
            genre TEXT,
            first_genre TEXT,
            price TEXT,
            discount_price TEXT,
            pubhouse TEXT,
            images TEXT,
            rating TEXT,
            ratings_count INTEGER,
            description TEXT
        )
    ''')
    conn.commit()
    return conn

def save_to_db(conn, book_data):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO books (
            name, author, genre, first_genre, price, discount_price, pubhouse, images, rating, ratings_count, description
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        book_data['name'], book_data['author'], book_data['genre'], book_data['first_genre'], 
        book_data['price'], book_data['discount_price'], book_data['pubhouse'], ', '.join(book_data['images']), 
        book_data['rating'], book_data['ratings_count'], book_data['description']
    ))
    conn.commit()

def get_book_data(book_id):
    url = f'https://www.labirint.ru/books/{book_id}/'
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        product_info = soup.find('div', {'id': 'product-info'})
        product_title = soup.find('div', {'id': 'product-title'})
        rating_div = soup.find('div', {'id': 'rate'})
        annotation_div = soup.find('div', {'id': 'fullannotation'})
        about_div = soup.find('div', {'id': 'product-about'})
        ratings_count_div = soup.find('div', {'id': 'product-rating-marks-label'})

        if product_info and product_title:
            data_name = product_info.get('data-name')
            data_maingenere_name = product_info.get('data-maingenere-name')
            data_price = product_info.get('data-price')
            data_discount_price = product_info.get('data-discount-price')
            data_pubhouse = product_info.get('data-pubhouse')
            data_first_genre_name = product_info.get('data-first-genre-name')
            
            # Извлекаем автора
            title_text = product_title.find('h1').text
            author = title_text.split(':')[0] if ':' in title_text else "Неизвестен"
            
            # Извлечение ссылок на изображения
            image_links = []
            image_tags = product_info.find_all('link', {'itemprop': 'image'}, limit=4)
            for tag in image_tags:
                image_links.append(tag.get('href'))

            # Извлечение рейтинга
            rating = rating_div.text.strip() if rating_div else "Нет рейтинга"
            
            # Извлечение количества оценок
            ratings_count = 0
            if ratings_count_div:
                ratings_count_text = ratings_count_div.text.strip()
                ratings_count = int(ratings_count_text.split(':')[-1].strip().replace(')', ''))
            
            # Извлечение описания: сначала ищем fullannotation, если нет, то product-about
            if annotation_div:
                description = annotation_div.get_text(separator=" ").strip()
            elif about_div:
                description = about_div.get_text(separator=" ").strip()
            else:
                description = "Нет описания"
            
            return {
                'book_id': book_id,
                'name': data_name,
                'author': author.strip(),
                'genre': data_maingenere_name,
                'first_genre': data_first_genre_name,
                'price': data_price,
                'discount_price': data_discount_price,
                'pubhouse': data_pubhouse,
                'images': image_links,
                'rating': rating,
                'ratings_count': ratings_count,
                'description': description
            }
    return None

def main():
    conn = create_db()

    book_ids = 1005952, 1002469, 992949, 923360, 1005953, 634082, 642466, 879317, 569173, 809426, 674021, 569758, 877234, 990463
    for book_id in book_ids:
        book_data = get_book_data(book_id)
        if book_data:
            save_to_db(conn, book_data)
            print(f"Book ID {book_id} saved to database.")

    conn.close()

if __name__ == "__main__":
    main()