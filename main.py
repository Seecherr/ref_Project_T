"""Library Management System — Application entry point.

Demonstrates the library management system with sample data
and provides a simple interactive CLI.
"""

from datetime import date, timedelta
from decimal import Decimal

from src.models.book import Book, BookItem
from src.models.member import Reader, Librarian
from src.services.catalog_service import CatalogService
from src.services.member_service import MemberService
from src.services.loan_service import LoanService
from src.services.fine_service import FineService
from src.services.reservation_service import ReservationService
from src.services.notification_service import NotificationService, BookAvailabilityListener
from src.storage.in_memory_book_repository import InMemoryBookRepository, InMemoryBookItemRepository
from src.storage.in_memory_member_repository import InMemoryMemberRepository
from src.storage.in_memory_loan_repository import InMemoryLoanRepository
from src.storage.in_memory_fine_repository import InMemoryFineRepository
from src.storage.in_memory_reservation_repository import InMemoryReservationRepository
from src.storage.in_memory_notification_repository import InMemoryNotificationRepository
from src.utils.event_manager import Event, EventManager
from src.utils.fine_strategy import StandardFineStrategy, ProgressiveFineStrategy


def create_application():
    """Wire up all dependencies and return service instances."""
    # Repositories
    book_repo = InMemoryBookRepository()
    book_item_repo = InMemoryBookItemRepository()
    member_repo = InMemoryMemberRepository()
    loan_repo = InMemoryLoanRepository()
    fine_repo = InMemoryFineRepository()
    reservation_repo = InMemoryReservationRepository()
    notification_repo = InMemoryNotificationRepository()

    # Event manager (Observer pattern)
    event_manager = EventManager()

    # Services
    catalog_service = CatalogService(book_repo, book_item_repo)
    member_service = MemberService(member_repo)
    loan_service = LoanService(loan_repo, book_item_repo, member_repo, event_manager)
    fine_service = FineService(fine_repo, member_repo, event_manager=event_manager)
    reservation_service = ReservationService(reservation_repo, book_item_repo, member_repo, event_manager)
    notification_service = NotificationService(notification_repo)

    # Wire up Observer — BookAvailabilityListener
    listener = BookAvailabilityListener(notification_service, reservation_repo)
    event_manager.subscribe(Event.BOOK_RETURNED, listener)
    event_manager.subscribe(Event.RESERVATION_FULFILLED, listener)
    event_manager.subscribe(Event.MEMBER_BLOCKED, listener)
    event_manager.subscribe(Event.MEMBER_UNBLOCKED, listener)

    return {
        "catalog": catalog_service,
        "members": member_service,
        "loans": loan_service,
        "fines": fine_service,
        "reservations": reservation_service,
        "notifications": notification_service,
    }


def seed_data(services: dict) -> None:
    """Populate the system with sample data."""
    catalog = services["catalog"]
    members = services["members"]

    # Add books
    catalog.add_book("9780134685991", "Effective Java", "Joshua Bloch", "Programming", 2018)
    catalog.add_book("9780132350884", "Clean Code", "Robert C. Martin", "Programming", 2008)
    catalog.add_book("9780201633610", "Design Patterns", "Gang of Four", "Software Engineering", 1994)
    catalog.add_book("9780596007126", "Head First Design Patterns", "Eric Freeman", "Programming", 2004)
    catalog.add_book("9780137081073", "The Clean Coder", "Robert C. Martin", "Programming", 2011)

    # Add book items (physical copies)
    catalog.add_book_item("9780134685991", "EJ-001", "A-1")
    catalog.add_book_item("9780134685991", "EJ-002", "A-1")
    catalog.add_book_item("9780132350884", "CC-001", "A-2")
    catalog.add_book_item("9780132350884", "CC-002", "A-2")
    catalog.add_book_item("9780201633610", "DP-001", "B-1")
    catalog.add_book_item("9780596007126", "HF-001", "B-2")
    catalog.add_book_item("9780137081073", "TC-001", "B-3")

    # Register members
    members.register_reader("Alice Johnson", "alice@library.com", member_id="R001")
    members.register_reader("Bob Smith", "bob@library.com", member_id="R002")
    members.register_reader("Charlie Brown", "charlie@library.com", member_id="R003")
    members.register_librarian("Diana Prince", "diana@library.com", employee_id="EMP001", member_id="L001")

    print("✅ Seeded: 5 books, 7 copies, 3 readers, 1 librarian")


def demo_workflow(services: dict) -> None:
    """Run a demonstration workflow."""
    catalog = services["catalog"]
    members = services["members"]
    loans = services["loans"]
    fines = services["fines"]
    reservations = services["reservations"]
    notifications = services["notifications"]

    print("\n" + "=" * 60)
    print("📚 LIBRARY MANAGEMENT SYSTEM — DEMO")
    print("=" * 60)

    # 1. Search catalog
    print("\n🔍 Searching for 'programming'...")
    results = catalog.search_books("programming")
    for book in results:
        available = len(catalog.get_available_items(book.isbn))
        print(f"   📖 {book.title} by {book.author} ({available} copies available)")

    # 2. Borrow books
    print("\n📤 Alice borrows 'Effective Java'...")
    loan1 = loans.borrow_book("R001", "EJ-001")
    print(f"   Loan created: due {loan1.due_date}")

    print("📤 Bob borrows 'Clean Code'...")
    loan2 = loans.borrow_book("R002", "CC-001")
    print(f"   Loan created: due {loan2.due_date}")

    # 3. Reserve an unavailable book
    print("\n📋 Charlie reserves 'Effective Java' (1 copy left)...")
    loans.borrow_book("R003", "EJ-002")  # Take the last copy
    print("📋 Bob tries to reserve 'Effective Java'...")
    res = reservations.place_reservation("R002", "9780134685991")
    print(f"   Reservation placed: {res.reservation_id[:8]}... (status: {res.status.value})")

    # 4. Return a book (triggers Observer notification)
    print("\n📥 Alice returns 'Effective Java'...")
    returned = loans.return_book("EJ-001")
    print(f"   Returned on: {returned.return_date}")

    # Check notifications (Observer pattern in action)
    bob_notifications = notifications.get_unread_notifications("R002")
    if bob_notifications:
        print(f"   🔔 Bob received notification: \"{bob_notifications[0].message[:60]}...\"")

    # 5. Fine calculation (Strategy pattern)
    print("\n💰 Fine calculation demo (Strategy pattern)...")
    fines.set_strategy(StandardFineStrategy())
    print(f"   Standard strategy (5 days overdue): ${fines._strategy.calculate(5)}")
    fines.set_strategy(ProgressiveFineStrategy())
    print(f"   Progressive strategy (5 days overdue): ${fines._strategy.calculate(5)}")

    # 6. Show system state
    print("\n📊 System Status:")
    print(f"   Total books: {len(catalog.get_all_books())}")
    print(f"   Active loans: {len(loans.get_all_loans())}")
    all_members = members.get_all_members()
    print(f"   Registered members: {len(all_members)}")
    print(f"   Pending reservations: {len(reservations.get_all_reservations())}")

    print("\n" + "=" * 60)
    print("✅ Demo complete!")
    print("=" * 60)


def interactive_menu(services: dict) -> None:
    """Simple interactive CLI menu."""
    while True:
        print("\n" + "-" * 40)
        print("📚 Library Management System")
        print("-" * 40)
        print("1. Search books")
        print("2. List all books")
        print("3. List all members")
        print("4. Borrow a book")
        print("5. Return a book")
        print("6. View active loans")
        print("7. View notifications")
        print("8. Run demo workflow")
        print("0. Exit")
        print("-" * 40)

        choice = input("Select option: ").strip()

        if choice == "0":
            print("👋 Goodbye!")
            break
        elif choice == "1":
            query = input("Search query: ").strip()
            results = services["catalog"].search_books(query)
            if not results:
                print("   No books found.")
            for book in results:
                avail = len(services["catalog"].get_available_items(book.isbn))
                print(f"   📖 {book.title} by {book.author} [{avail} available]")
        elif choice == "2":
            books = services["catalog"].get_all_books()
            for book in books:
                avail = len(services["catalog"].get_available_items(book.isbn))
                print(f"   📖 {book.title} by {book.author} (ISBN: {book.isbn}) [{avail} available]")
        elif choice == "3":
            for m in services["members"].get_all_members():
                print(f"   👤 {m.name} ({m.email}) — {m.status.value}")
        elif choice == "4":
            mid = input("Member ID: ").strip()
            barcode = input("Book barcode: ").strip()
            try:
                loan = services["loans"].borrow_book(mid, barcode)
                print(f"   ✅ Borrowed! Due: {loan.due_date}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        elif choice == "5":
            barcode = input("Book barcode: ").strip()
            try:
                loan = services["loans"].return_book(barcode)
                print(f"   ✅ Returned! Was due: {loan.due_date}")
                if loan.is_overdue():
                    fine = services["fines"].create_fine(loan)
                    if fine:
                        print(f"   💰 Fine created: ${fine.amount}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        elif choice == "6":
            all_loans = [l for l in services["loans"].get_all_loans() if l.is_active()]
            if not all_loans:
                print("   No active loans.")
            for l in all_loans:
                print(f"   📋 {l.book_item_barcode} → Member {l.member_id} (due: {l.due_date})")
        elif choice == "7":
            mid = input("Member ID: ").strip()
            notifs = services["notifications"].get_notifications(mid)
            if not notifs:
                print("   No notifications.")
            for n in notifs:
                status = "📬" if not n.is_read else "📭"
                print(f"   {status} {n.message[:80]}")
        elif choice == "8":
            services = create_application()
            seed_data(services)
            demo_workflow(services)
        else:
            print("   Invalid option.")


def main():
    """Application entry point."""
    print("🏛️  Library Management System v1.0.0")
    print("    In-Memory | Strategy + Observer Patterns | SOLID\n")

    services = create_application()
    seed_data(services)
    demo_workflow(services)
    interactive_menu(services)


if __name__ == "__main__":
    main()
