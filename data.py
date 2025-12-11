import sqlite3

def insert_test_data():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Insert test data into admin table
    cursor.execute("INSERT INTO admin (name, password, email) VALUES (?, ?, ?)",
                   ('admin', 'admin123', 'admin@example.com'))

    # Insert test data into users table
    users = [
        (1, 'Alice', 'Female', 'password1', 'student', 'alice@example.com', 3),
        (2, 'Bob', 'Male', 'password2', 'student', 'bob@example.com', 3),
        (3, 'Charlie', 'Male', 'password3', 'teacher', 'charlie@example.com', 5)
    ]
    cursor.executemany("INSERT INTO users (id, username, gender, password, user_type, email, maxborrow) VALUES (?, ?, ?, ?, ?, ?, ?)", users)

    # Insert test data into categories table
    categories = [
        ('Fiction',),
        ('Science',),
        ('History',)
    ]
    cursor.executemany("INSERT INTO categories (name) VALUES (?)", categories)

    # Insert test data into books table
    books = [
        ('To Kill a Mockingbird', 'Harper Lee', 'J.B. Lippincott & Co.', 1960, 'A novel about racial injustice in the Deep South.', 1, '9780061120084', 5),
        ('A Brief History of Time', 'Stephen Hawking', 'Bantam Books', 1988, 'A popular-science book on cosmology.', 2, '9780553380163', 3),
        ('Sapiens: A Brief History of Humankind', 'Yuval Noah Harari', 'Harvill Secker', 2011, 'A book exploring the history and impact of Homo sapiens.', 3, '9780099590088', 2)
    ]
    cursor.executemany("INSERT INTO books (title, author, publisher, year, description, category_id, isbn, copies) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", books)

    # Insert test data into copies table
    copies = [
        (1, 'available', 'Shelf A', 1),
        (1, 'borrowed', 'Shelf A', 1),
        (2, 'available', 'Shelf B', 1),
        (3, 'available', 'Shelf C', 1)
    ]
    cursor.executemany("INSERT INTO copies (book_id, status, location, borrowable) VALUES (?, ?, ?, ?)", copies)

    # Insert test data into borrows table
    borrows = [
        (1, 1, '2025-12-01 10:00:00', '2025-12-10 10:00:00', 1),
        (2, 2, '2025-12-05 15:00:00', None, 0)
    ]
    cursor.executemany("INSERT INTO borrows (user_id, copy_id, borrow_time, return_date, returned) VALUES (?, ?, ?, ?, ?)", borrows)

    # Insert test data into reservations table
    reservations = [
        (1, 2, '2025-12-06 12:00:00', 0),
        (2, 3, '2025-12-07 14:00:00', 1)
    ]
    cursor.executemany("INSERT INTO reservations (user_id, book_id, reservation_date, fulfilled) VALUES (?, ?, ?, ?)", reservations)

    # Insert test data into reviews table
    reviews = [
        (1, 1, 5, 'Excellent book!', '2025-12-08 09:00:00'),
        (2, 2, 4, 'Good read.', '2025-12-09 11:00:00')
    ]
    cursor.executemany("INSERT INTO reviews (user_id, book_id, rating, comment, review_date) VALUES (?, ?, ?, ?, ?)", reviews)

    conn.commit()
    conn.close()

insert_test_data()