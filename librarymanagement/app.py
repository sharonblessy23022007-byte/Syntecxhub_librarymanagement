import json
import os


class Book:
    """Represents an individual book in the library inventory."""

    def __init__(self, book_id: str, title: str, author: str, is_issued: bool = False):
        self.id = book_id.strip()
        self.title = title.strip()
        self.author = author.strip()
        self.is_issued = is_issued

    def to_dict(self) -> dict:
        """Converts Book instance to a dictionary for JSON storage."""
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "is_issued": self.is_issued
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Creates a Book instance from a raw dictionary."""
        return cls(data["id"], data["title"], data["author"], data["is_issued"])


class Library:
    """Manages collection data structures, operations, and file persistence."""

    def __init__(self, filename="library_inventory.json"):
        self.filename = filename
        # HashMap implementation: book_id string mapped directly to Book objects
        self.inventory = {} 
        self.load_data()

    def load_data(self):
        """Loads inventory data from JSON on startup."""
        if not os.path.exists(self.filename):
            self.inventory = {}
            return

        try:
            with open(self.filename, "r") as file:
                raw_data = json.load(file)
                self.inventory = {
                    bid: Book.from_dict(bdata) for bid, bdata in raw_data.items()
                }
        except (json.JSONDecodeError, KeyError):
            print("⚠️ File read error or corrupted data. Starting fresh.")
            self.inventory = {}

    def save_data(self):
        """Saves memory state back into the local JSON file."""
        try:
            with open(self.filename, "w") as file:
                serialized = {bid: book.to_dict() for bid, book in self.inventory.items()}
                json.dump(serialized, file, indent=4)
        except IOError as e:
            print(f"❌ Critical Error: Could not write tracking data: {e}")

    def add_book(self, book_id: str, title: str, author: str) -> bool:
        """Adds a unique book into the library system data-store."""
        if not book_id or not title or not author:
            print("❌ Validation Error: All attributes must contain values.")
            return False

        if book_id in self.inventory:
            print(f"❌ Conflict: Book ID '{book_id}' already tracking another entry.")
            return False

        self.inventory[book_id] = Book(book_id, title, author)
        self.save_data()
        print(f"✅ Added: '{title}' by {author} successfully registered.")
        return True

    def search_books(self, query: str, search_type: str) -> list:
        """Iterates collection to find substring matches on Title or Author."""
        query = query.lower().strip()
        results = []

        for book in self.inventory.values():
            if search_type == "title" and query in book.title.lower():
                results.append(book)
            elif search_type == "author" and query in book.author.lower():
                results.append(book)
        return results

    def checkout_book(self, book_id: str) -> bool:
        """Issues a book to a user via its unique ID."""
        if book_id not in self.inventory:
            print(f"❌ Error: Book ID '{book_id}' is not in the system registry.")
            return False

        book = self.inventory[book_id]
        if book.is_issued:
            print(f"⚠️ Status: '{book.title}' is already currently checked out.")
            return False

        book.is_issued = True
        self.save_data()
        print(f"📚 Success: '{book.title}' has been checked out.")
        return True

    def return_book(self, book_id: str) -> bool:
        """Returns an issued book back into active shelf availability."""
        if book_id not in self.inventory:
            print(f"❌ Error: Book ID '{book_id}' is not in the system registry.")
            return False

        book = self.inventory[book_id]
        if not book.is_issued:
            print(f"⚠️ Status: '{book.title}' is already sitting on the shelf.")
            return False

        book.is_issued = False
        self.save_data()
        print(f"🔄 Success: '{book.title}' has been safely returned to inventory.")
        return True

    def generate_report(self):
        """Compiles metric breakdowns across current collection states."""
        total_books = len(self.inventory)
        issued_count = sum(1 for book in self.inventory.values() if book.is_issued)
        available_count = total_books - issued_count

        print("\n" + "=" * 40)
        print("📊 INVENTORY REPORT SUMMARY")
        print("=" * 40)
        print(f"🔹 Total Unique Books : {total_books}")
        print(f"🔹 Actively Lent Out  : {issued_count}")
        print(f"🔹 Shelved/Available  : {available_count}")
        print("=" * 40)


def print_results_table(books: list):
    """Utility function to print books in a clean, aligned layout."""
    if not books:
        print("\n--- No records matched your criteria ---")
        return

    print("\n" + "-" * 65)
    print(f"{'ID':<10} | {'Title':<25} | {'Author':<18} | {'Status':<10}")
    print("-" * 65)
    for book in books:
        status = "Issued" if book.is_issued else "Available"
        print(f"{book.id:<10} | {book.title:<25} | {book.author:<18} | {status:<10}")
    print("-" * 65 + "\n")


def main():
    library = Library()

    while True:
        print("\n📚 Library Inventory Management System")
        print("1. Add Book to Inventory")
        print("2. Search Book Repository")
        print("3. Issue Book (Checkout)")
        print("4. Return Book")
        print("5. Generate Summary Report")
        print("6. Exit")

        choice = input("Enter option (1-6): ").strip()

        if choice == "1":
            print("\n--- Registering New Book ---")
            bid = input("Assign Book ID: ").strip()
            title = input("Enter Title: ").strip()
            author = input("Enter Author: ").strip()
            library.add_book(bid, title, author)

        elif choice == "2":
            print("\n--- Search Inventory Engine ---")
            print("1. Search By Title Match")
            print("2. Search By Author Match")
            sub_choice = input("Select criteria (1-2): ").strip()
            
            if sub_choice == "1":
                q = input("Enter Title search keywords: ")
                results = library.search_books(q, "title")
                print_results_table(results)
            elif sub_choice == "2":
                q = input("Enter Author search keywords: ")
                results = library.search_books(q, "author")
                print_results_table(results)
            else:
                print("❌ Invalid search parameters picked.")

        elif choice == "3":
            print("\n--- Book Dispatch Process ---")
            bid = input("Scan/Enter Book ID to Issue: ").strip()
            library.checkout_book(bid)

        elif choice == "4":
            print("\n--- Book Return Process ---")
            bid = input("Scan/Enter Book ID to Return: ").strip()
            library.return_book(bid)

        elif choice == "5":
            library.generate_report()
            # Automatically show everything alongside reports for readability
            print_results_table(list(library.inventory.values()))

        elif choice == "6":
            print("\nShutting down system interface. Safe cataloging!")
            break
        else:
            print("❌ Selection out of range. Provide a number between 1 and 6.")


if __name__ == "__main__":
    main()