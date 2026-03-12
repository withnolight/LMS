"""
Unit tests for the core database logic of the Library Management System.
Tests run against a temporary SQLite database to avoid side effects.
"""
import sqlite3
import unittest
import os
import sys
import tempfile

# Mock tkinter before anything imports it
import unittest.mock as mock
sys.modules['tkinter'] = mock.MagicMock()
sys.modules['tkinter.messagebox'] = mock.MagicMock()
sys.modules['tkinter.font'] = mock.MagicMock()
sys.modules['tkinter.ttk'] = mock.MagicMock()
sys.modules['ttkbootstrap'] = mock.MagicMock()
sys.modules['ttkbootstrap.constants'] = mock.MagicMock()

# Patch DB_PATH before importing modules that depend on it
import init


class BaseDBTestCase(unittest.TestCase):
    """Base class that sets up a fresh database for each test."""

    def setUp(self):
        self._db_fd, self._db_path = tempfile.mkstemp(suffix=".db")
        os.close(self._db_fd)
        init.DB_PATH = self._db_path
        init.init_db()

        # Patch main module's DB_PATH as well
        import main
        main.DB_PATH = self._db_path

        # Patch messagebox
        import tkinter.messagebox as mb
        mb.showinfo = mock.MagicMock()
        mb.showerror = mock.MagicMock()

    def tearDown(self):
        try:
            os.unlink(self._db_path)
        except OSError:
            pass

    def _get_conn(self):
        return sqlite3.connect(self._db_path)

    def _seed_user(self, user_id=20250001, username="testuser", password="123456",
                   user_type="student", email="test@example.com", maxborrow=3):
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO users (id, username, password, user_type, email, maxborrow) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, username, password, user_type, email, maxborrow))
            conn.commit()

    def _seed_book_and_copy(self, title="TestBook", isbn="ISBN0001",
                            copies=1, status="available", borrowable=1):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO books (title, author, publisher, year, isbn, copies) VALUES (?, ?, ?, ?, ?, ?)",
                (title, "Author", "Publisher", 2024, isbn, copies))
            bid = cursor.lastrowid
            copy_ids = []
            for _ in range(copies):
                cursor.execute(
                    "INSERT INTO copies (book_id, status, location, borrowable) VALUES (?, ?, '默认位置', ?)",
                    (bid, status, borrowable))
                copy_ids.append(cursor.lastrowid)
            conn.commit()
        return bid, copy_ids


class TestInitDB(BaseDBTestCase):
    """Test that init_db creates all required tables."""

    def test_tables_created(self):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
        tables = sorted([row[0] for row in cursor.fetchall()])
        conn.close()
        expected = sorted(["admin", "users", "categories", "books", "copies",
                           "borrows", "reservations", "reviews"])
        self.assertEqual(tables, expected)

    def test_users_table_has_gender_column(self):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        conn.close()
        self.assertIn("gender", columns)


class TestGetConnection(BaseDBTestCase):
    """Test the get_connection helper."""

    def test_returns_valid_connection(self):
        import main
        conn = main.get_connection()
        self.assertIsInstance(conn, sqlite3.Connection)
        conn.close()


class TestExecuteBorrow(BaseDBTestCase):
    """Test borrow logic."""

    def test_borrow_success(self):
        import main
        from tkinter import messagebox
        self._seed_user()
        _, copy_ids = self._seed_book_and_copy()
        main.execute_borrow(20250001, copy_ids[0])
        messagebox.showinfo.assert_called()
        args = messagebox.showinfo.call_args[0]
        self.assertIn("成功", args[1])

        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT borrowed_count FROM users WHERE id=20250001")
            self.assertEqual(cursor.fetchone()[0], 1)
            cursor.execute("SELECT status FROM copies WHERE id=?", (copy_ids[0],))
            self.assertEqual(cursor.fetchone()[0], "borrowed")

    def test_borrow_nonexistent_user(self):
        import main
        from tkinter import messagebox
        _, copy_ids = self._seed_book_and_copy()
        messagebox.showerror.reset_mock()
        main.execute_borrow(99999999, copy_ids[0])
        messagebox.showerror.assert_called()
        args = messagebox.showerror.call_args[0]
        self.assertIn("读者ID不存在", args[1])

    def test_borrow_nonexistent_copy(self):
        import main
        from tkinter import messagebox
        self._seed_user()
        messagebox.showerror.reset_mock()
        main.execute_borrow(20250001, 99999)
        messagebox.showerror.assert_called()
        args = messagebox.showerror.call_args[0]
        self.assertIn("副本ID不存在", args[1])

    def test_borrow_exceeds_limit(self):
        import main
        from tkinter import messagebox
        self._seed_user(maxborrow=1)
        _, copy_ids1 = self._seed_book_and_copy(isbn="ISBN001")
        _, copy_ids2 = self._seed_book_and_copy(isbn="ISBN002")
        main.execute_borrow(20250001, copy_ids1[0])
        messagebox.showerror.reset_mock()
        main.execute_borrow(20250001, copy_ids2[0])
        messagebox.showerror.assert_called()
        args = messagebox.showerror.call_args[0]
        self.assertIn("上限", args[1])

    def test_borrow_unavailable_copy(self):
        import main
        from tkinter import messagebox
        self._seed_user()
        _, copy_ids = self._seed_book_and_copy(status="damaged", borrowable=0)
        messagebox.showerror.reset_mock()
        main.execute_borrow(20250001, copy_ids[0])
        messagebox.showerror.assert_called()
        args = messagebox.showerror.call_args[0]
        self.assertIn("不可借", args[1])


class TestExecuteReturn(BaseDBTestCase):
    """Test return logic."""

    def test_return_success(self):
        import main
        from tkinter import messagebox
        self._seed_user()
        _, copy_ids = self._seed_book_and_copy()
        main.execute_borrow(20250001, copy_ids[0])
        messagebox.showinfo.reset_mock()
        main.execute_return(20250001, copy_ids[0])
        messagebox.showinfo.assert_called()

        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT borrowed_count FROM users WHERE id=20250001")
            self.assertEqual(cursor.fetchone()[0], 0)
            cursor.execute("SELECT status FROM copies WHERE id=?", (copy_ids[0],))
            self.assertEqual(cursor.fetchone()[0], "available")

    def test_return_invalid_record(self):
        import main
        from tkinter import messagebox
        messagebox.showerror.reset_mock()
        main.execute_return(20250001, 99999)
        messagebox.showerror.assert_called()


class TestExecuteAddBook(BaseDBTestCase):
    """Test book addition logic."""

    def test_add_new_book(self):
        import main
        from tkinter import messagebox
        main.execute_add_book("TestBook", "Author", "Pub", 2024, "ISBN999", "Desc", None, "2", 1)
        messagebox.showinfo.assert_called()

        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT copies FROM books WHERE isbn='ISBN999'")
            self.assertEqual(cursor.fetchone()[0], 2)
            cursor.execute("SELECT COUNT(*) FROM copies WHERE book_id=(SELECT id FROM books WHERE isbn='ISBN999')")
            self.assertEqual(cursor.fetchone()[0], 2)

    def test_add_existing_book_increases_copies(self):
        import main
        main.execute_add_book("TestBook", "Author", "Pub", 2024, "ISBN888", "Desc", None, "1", 1)
        main.execute_add_book("TestBook", "Author", "Pub", 2024, "ISBN888", "Desc", None, "3", 1)

        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT copies FROM books WHERE isbn='ISBN888'")
            self.assertEqual(cursor.fetchone()[0], 4)  # 1 + 3
            cursor.execute("SELECT COUNT(*) FROM copies WHERE book_id=(SELECT id FROM books WHERE isbn='ISBN888')")
            self.assertEqual(cursor.fetchone()[0], 4)


class TestMarkedAsDamaged(BaseDBTestCase):
    """Test damage marking logic."""

    def test_damage_available_copy(self):
        import main
        from tkinter import messagebox
        _, copy_ids = self._seed_book_and_copy()
        messagebox.showinfo.reset_mock()
        main.marked_as_damaged(copy_ids[0])
        messagebox.showinfo.assert_called()

        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status, borrowable FROM copies WHERE id=?", (copy_ids[0],))
            row = cursor.fetchone()
            self.assertEqual(row[0], "damaged")
            self.assertEqual(row[1], 0)

    def test_damage_nonexistent_copy(self):
        import main
        from tkinter import messagebox
        messagebox.showerror.reset_mock()
        main.marked_as_damaged(99999)
        messagebox.showerror.assert_called()

    def test_damage_already_damaged(self):
        import main
        from tkinter import messagebox
        _, copy_ids = self._seed_book_and_copy(status="damaged", borrowable=0)
        messagebox.showinfo.reset_mock()
        main.marked_as_damaged(copy_ids[0])
        messagebox.showinfo.assert_called()
        args = messagebox.showinfo.call_args[0]
        self.assertIn("已标记", args[1])

    def test_damage_borrowed_copy_decrements_user_count(self):
        import main
        self._seed_user()
        _, copy_ids = self._seed_book_and_copy()
        main.execute_borrow(20250001, copy_ids[0])

        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT borrowed_count FROM users WHERE id=20250001")
            self.assertEqual(cursor.fetchone()[0], 1)

        main.marked_as_damaged(copy_ids[0])

        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT borrowed_count FROM users WHERE id=20250001")
            self.assertEqual(cursor.fetchone()[0], 0)


class TestAddUser(BaseDBTestCase):
    """Test user addition logic."""

    def test_add_student(self):
        import main
        from tkinter import messagebox
        main.add_user(20250001, "student1", "pass", "student", "s@example.com")
        messagebox.showinfo.assert_called()

        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT maxborrow FROM users WHERE id=20250001")
            self.assertEqual(cursor.fetchone()[0], 3)

    def test_add_teacher(self):
        import main
        main.add_user(20260001, "teacher1", "pass", "teacher", "t@example.com")

        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT maxborrow FROM users WHERE id=20260001")
            self.assertEqual(cursor.fetchone()[0], 10)

    def test_add_duplicate_user(self):
        import main
        from tkinter import messagebox
        main.add_user(20250001, "student1", "pass", "student", "s@example.com")
        messagebox.showerror.reset_mock()
        main.add_user(20250001, "student1", "pass", "student", "s2@example.com")
        messagebox.showerror.assert_called()


class TestDeleteUser(BaseDBTestCase):
    """Test user deletion logic."""

    def test_delete_user_success(self):
        import main
        from tkinter import messagebox
        self._seed_user()
        messagebox.showinfo.reset_mock()
        main.delete_user(20250001)
        messagebox.showinfo.assert_called()

    def test_delete_nonexistent_user(self):
        import main
        from tkinter import messagebox
        messagebox.showerror.reset_mock()
        main.delete_user(99999)
        messagebox.showerror.assert_called()

    def test_delete_user_with_borrowed_books(self):
        import main
        from tkinter import messagebox
        self._seed_user()
        _, copy_ids = self._seed_book_and_copy()
        main.execute_borrow(20250001, copy_ids[0])
        messagebox.showerror.reset_mock()
        main.delete_user(20250001)
        messagebox.showerror.assert_called()
        args = messagebox.showerror.call_args[0]
        self.assertIn("未归还", args[1])


class TestCheckLogin(BaseDBTestCase):
    """Test login logic - verify admin table works correctly."""

    def test_valid_admin_credentials(self):
        with self._get_conn() as conn:
            conn.execute("INSERT INTO admin (name, password) VALUES (?, ?)", ("admin", "pass123"))
            conn.commit()

        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM admin WHERE name=? AND password=?",
                           ("admin", "pass123"))
            result = cursor.fetchone()
        self.assertIsNotNone(result)

    def test_invalid_admin_credentials(self):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM admin WHERE name=? AND password=?",
                           ("nobody", "wrong"))
            result = cursor.fetchone()
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
