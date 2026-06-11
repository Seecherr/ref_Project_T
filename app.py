"""Library Management System — Flask REST API entry point.

Exposes the library management system as an HTTP REST API,
making it accessible over the network when deployed in a container.
"""

from datetime import date, datetime
from decimal import Decimal

from flask import Flask, jsonify, render_template, request

from main import create_application, seed_data


# ---------------------------------------------------------------------------
# Serialization helpers
# ---------------------------------------------------------------------------

def serialize_date(d):
    """Convert date/datetime to ISO string, or None."""
    if d is None:
        return None
    if isinstance(d, datetime):
        return d.isoformat()
    if isinstance(d, date):
        return d.isoformat()
    return str(d)


def serialize_book(book):
    """Serialize a Book dataclass to a JSON-safe dict."""
    return {
        "isbn": book.isbn,
        "title": book.title,
        "author": book.author,
        "subject": book.subject,
        "year": book.year,
        "total_copies": book.total_copies(),
        "available_copies": len(book.get_available_items()),
        "items": [serialize_book_item(item) for item in book.items],
    }


def serialize_book_item(item):
    """Serialize a BookItem dataclass to a JSON-safe dict."""
    return {
        "barcode": item.barcode,
        "book_isbn": item.book_isbn,
        "status": item.status.value,
        "rack_number": item.rack_number,
        "due_date": serialize_date(item.due_date),
    }


def serialize_member(member):
    """Serialize a Member dataclass to a JSON-safe dict."""
    result = {
        "member_id": member.member_id,
        "name": member.name,
        "email": member.email,
        "status": member.status.value,
        "created_at": serialize_date(member.created_at),
        "type": type(member).__name__,
    }
    if hasattr(member, "max_books_limit"):
        result["max_books_limit"] = member.max_books_limit
        result["total_books_checked_out"] = member.total_books_checked_out
    if hasattr(member, "employee_id"):
        result["employee_id"] = member.employee_id
    return result


def serialize_loan(loan):
    """Serialize a Loan dataclass to a JSON-safe dict."""
    return {
        "loan_id": loan.loan_id,
        "member_id": loan.member_id,
        "book_item_barcode": loan.book_item_barcode,
        "issue_date": serialize_date(loan.issue_date),
        "due_date": serialize_date(loan.due_date),
        "return_date": serialize_date(loan.return_date),
        "is_active": loan.is_active(),
        "is_overdue": loan.is_overdue(),
    }


def serialize_reservation(reservation):
    """Serialize a Reservation dataclass to a JSON-safe dict."""
    return {
        "reservation_id": reservation.reservation_id,
        "member_id": reservation.member_id,
        "book_isbn": reservation.book_isbn,
        "created_at": serialize_date(reservation.created_at),
        "status": reservation.status.value,
    }


def serialize_notification(notification):
    """Serialize a Notification dataclass to a JSON-safe dict."""
    return {
        "notification_id": notification.notification_id,
        "member_id": notification.member_id,
        "message": notification.message,
        "created_at": serialize_date(notification.created_at),
        "is_read": notification.is_read,
    }


def serialize_fine(fine):
    """Serialize a Fine dataclass to a JSON-safe dict."""
    return {
        "fine_id": fine.fine_id,
        "loan_id": fine.loan_id,
        "member_id": fine.member_id,
        "amount": str(fine.amount),
        "paid": str(fine.paid),
        "outstanding": str(fine.outstanding),
        "is_fully_paid": fine.is_fully_paid(),
        "created_at": serialize_date(fine.created_at),
    }


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

def create_flask_app():
    """Create and configure the Flask application."""
    flask_app = Flask(__name__)

    # Wire up the domain services
    services = create_application()
    seed_data(services)

    catalog = services["catalog"]
    members = services["members"]
    loans = services["loans"]
    fines = services["fines"]
    reservations = services["reservations"]
    notifications = services["notifications"]

    # -------------------------------------------------------------------
    # Health
    # -------------------------------------------------------------------
    @flask_app.route("/")
    def index():
        return render_template("index.html")

    @flask_app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"})

    # -------------------------------------------------------------------
    # Books
    # -------------------------------------------------------------------
    @flask_app.route("/api/books", methods=["GET"])
    def list_books():
        query = request.args.get("q", "").strip()
        if query:
            books = catalog.search_books(query)
        else:
            books = catalog.get_all_books()
        return jsonify([serialize_book(b) for b in books])

    @flask_app.route("/api/books/<isbn>", methods=["GET"])
    def get_book(isbn):
        try:
            book = catalog.get_book(isbn)
            return jsonify(serialize_book(book))
        except Exception as e:
            return jsonify({"error": str(e)}), 404

    @flask_app.route("/api/books", methods=["POST"])
    def add_book():
        data = request.get_json(silent=True) or {}
        try:
            book = catalog.add_book(
                isbn=data.get("isbn", ""),
                title=data.get("title", ""),
                author=data.get("author", ""),
                subject=data.get("subject", ""),
                year=data.get("year", 0),
            )
            return jsonify(serialize_book(book)), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @flask_app.route("/api/books/<isbn>/items", methods=["POST"])
    def add_book_item(isbn):
        data = request.get_json(silent=True) or {}
        try:
            item = catalog.add_book_item(
                isbn=isbn,
                barcode=data.get("barcode"),
                rack_number=data.get("rack_number", ""),
            )
            return jsonify(serialize_book_item(item)), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    # -------------------------------------------------------------------
    # Members
    # -------------------------------------------------------------------
    @flask_app.route("/api/members", methods=["GET"])
    def list_members():
        all_members = members.get_all_members()
        return jsonify([serialize_member(m) for m in all_members])

    @flask_app.route("/api/members/<member_id>", methods=["GET"])
    def get_member(member_id):
        try:
            member = members.get_member(member_id)
            return jsonify(serialize_member(member))
        except Exception as e:
            return jsonify({"error": str(e)}), 404

    @flask_app.route("/api/members", methods=["POST"])
    def register_member():
        data = request.get_json(silent=True) or {}
        member_type = data.get("type", "reader").lower()
        try:
            if member_type == "librarian":
                member = members.register_librarian(
                    name=data.get("name", ""),
                    email=data.get("email", ""),
                    employee_id=data.get("employee_id", ""),
                    member_id=data.get("member_id"),
                )
            else:
                member = members.register_reader(
                    name=data.get("name", ""),
                    email=data.get("email", ""),
                    member_id=data.get("member_id"),
                    max_books_limit=data.get("max_books_limit", 5),
                )
            return jsonify(serialize_member(member)), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    # -------------------------------------------------------------------
    # Loans
    # -------------------------------------------------------------------
    @flask_app.route("/api/loans", methods=["GET"])
    def list_loans():
        all_loans = loans.get_all_loans()
        return jsonify([serialize_loan(l) for l in all_loans])

    @flask_app.route("/api/loans", methods=["POST"])
    def borrow_book():
        data = request.get_json(silent=True) or {}
        try:
            loan = loans.borrow_book(
                member_id=data.get("member_id", ""),
                barcode=data.get("barcode", ""),
            )
            return jsonify(serialize_loan(loan)), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @flask_app.route("/api/loans/return", methods=["POST"])
    def return_book():
        data = request.get_json(silent=True) or {}
        try:
            loan = loans.return_book(barcode=data.get("barcode", ""))
            result = serialize_loan(loan)
            # Auto-create fine if overdue
            if loan.is_overdue():
                fine = fines.create_fine(loan)
                if fine:
                    result["fine_created"] = serialize_fine(fine)
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    # -------------------------------------------------------------------
    # Reservations
    # -------------------------------------------------------------------
    @flask_app.route("/api/reservations", methods=["GET"])
    def list_reservations():
        all_reservations = reservations.get_all_reservations()
        return jsonify([serialize_reservation(r) for r in all_reservations])

    @flask_app.route("/api/reservations", methods=["POST"])
    def place_reservation():
        data = request.get_json(silent=True) or {}
        try:
            reservation = reservations.place_reservation(
                member_id=data.get("member_id", ""),
                book_isbn=data.get("book_isbn", ""),
            )
            return jsonify(serialize_reservation(reservation)), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    # -------------------------------------------------------------------
    # Notifications
    # -------------------------------------------------------------------
    @flask_app.route("/api/notifications/<member_id>", methods=["GET"])
    def get_notifications(member_id):
        unread_only = request.args.get("unread", "false").lower() == "true"
        if unread_only:
            notifs = notifications.get_unread_notifications(member_id)
        else:
            notifs = notifications.get_notifications(member_id)
        return jsonify([serialize_notification(n) for n in notifs])

    # -------------------------------------------------------------------
    # Fines
    # -------------------------------------------------------------------
    @flask_app.route("/api/fines/<member_id>", methods=["GET"])
    def get_member_fines(member_id):
        unpaid = fines.get_unpaid_fines(member_id)
        total = fines.get_total_unpaid(member_id)
        return jsonify({
            "member_id": member_id,
            "total_unpaid": str(total),
            "fines": [serialize_fine(f) for f in unpaid],
        })

    @flask_app.route("/api/fines/<fine_id>/pay", methods=["POST"])
    def pay_fine(fine_id):
        data = request.get_json(silent=True) or {}
        try:
            amount = Decimal(str(data.get("amount", "0")))
            fine = fines.pay_fine(fine_id, amount)
            return jsonify(serialize_fine(fine))
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    return flask_app


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
app = create_flask_app()

if __name__ == "__main__":
    print("🏛️  Library Management System v1.0.0 — REST API")
    print("   Listening on http://0.0.0.0:8000")
    app.run(host="0.0.0.0", port=8000, debug=False)
