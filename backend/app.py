
from datetime import date, datetime, timedelta, timezone
from functools import wraps
import os

import jwt
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_

from models import (
    db,
    User,
    Medicine,
    Batch,
    DispenseRecord,
    DispenseItem,
    QuarantineRecord,
    NotificationOutbox
)


app = Flask(__name__)

CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///pharmacy.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "pharmaflow-dev-secret-change-before-production"
)

db.init_app(app)


# -------------------------------------------------
# Helpers
# -------------------------------------------------

def create_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=24)
    }

    return jwt.encode(
        payload,
        app.config["SECRET_KEY"],
        algorithm="HS256"
    )


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({
                "error": "Authorization token required"
            }), 401

        token = auth_header.split(" ", 1)[1]

        try:
            payload = jwt.decode(
                token,
                app.config["SECRET_KEY"],
                algorithms=["HS256"]
            )

            user = db.session.get(User, payload["user_id"])

            if not user:
                return jsonify({
                    "error": "User not found"
                }), 401

            request.current_user = user

        except jwt.ExpiredSignatureError:
            return jsonify({
                "error": "Token expired"
            }), 401

        except jwt.InvalidTokenError:
            return jsonify({
                "error": "Invalid token"
            }), 401

        return f(*args, **kwargs)

    return decorated


def get_sellable_stock(medicine_id):
    today = date.today()

    batches = Batch.query.filter(
        Batch.medicine_id == medicine_id,
        Batch.expiry_date >= today,
        Batch.quantity > 0
    ).all()

    return sum(batch.quantity for batch in batches)


def medicine_to_dict(medicine):
    return {
        "id": medicine.id,
        "name": medicine.name,
        "generic_name": medicine.generic_name,
        "sellable_stock": get_sellable_stock(medicine.id)
    }


# -------------------------------------------------
# Home
# -------------------------------------------------

@app.route("/")
def home():
    return jsonify({
        "message": "PharmaFlow API is running!"
    })


# -------------------------------------------------
# Authentication
# -------------------------------------------------

@app.route("/api/auth/register", methods=["POST"])
def register():

    data = request.get_json(silent=True) or {}

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not name or not email or not password:
        return jsonify({
            "error": "Name, email and password are required"
        }), 400

    if len(password) < 6:
        return jsonify({
            "error": "Password must be at least 6 characters"
        }), 400

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return jsonify({
            "error": "Email already registered"
        }), 409

    user = User(
        name=name,
        email=email,
        password_hash=generate_password_hash(password)
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "Registration successful",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }), 201


@app.route("/api/auth/login", methods=["POST"])
def login():

    data = request.get_json(silent=True) or {}

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(
        user.password_hash,
        password
    ):
        return jsonify({
            "error": "Invalid email or password"
        }), 401

    token = create_token(user.id)

    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    })


# -------------------------------------------------
# Medicines
# -------------------------------------------------

@app.route("/api/medicines", methods=["GET"])
@token_required
def get_medicines():

    search = request.args.get("search", "").strip()

    sort_by = request.args.get("sort", "name")

    order = request.args.get("order", "asc")

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    page = max(page, 1)
    per_page = min(max(per_page, 1), 100)

    query = Medicine.query

    if search:
        query = query.filter(
            or_(
                Medicine.name.ilike(f"%{search}%"),
                Medicine.generic_name.ilike(f"%{search}%")
            )
        )

    allowed_sort_fields = {
        "name": Medicine.name,
        "created_at": Medicine.created_at
    }

    sort_column = allowed_sort_fields.get(
        sort_by,
        Medicine.name
    )

    if order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return jsonify({
        "medicines": [
            medicine_to_dict(medicine)
            for medicine in pagination.items
        ],
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages
        }
    })


@app.route("/api/medicines", methods=["POST"])
@token_required
def add_medicine():

    data = request.get_json(silent=True) or {}

    name = data.get("name", "").strip()
    generic_name = data.get("generic_name", "").strip() or None

    if not name:
        return jsonify({
            "error": "Medicine name is required"
        }), 400

    medicine = Medicine(
        name=name,
        generic_name=generic_name
    )

    db.session.add(medicine)
    db.session.commit()

    return jsonify({
        "message": "Medicine created",
        "medicine": medicine_to_dict(medicine)
    }), 201


@app.route("/api/medicines/<int:medicine_id>", methods=["GET"])
@token_required
def get_medicine(medicine_id):

    medicine = db.session.get(Medicine, medicine_id)

    if not medicine:
        return jsonify({
            "error": "Medicine not found"
        }), 404

    today = date.today()

    batches = Batch.query.filter_by(
        medicine_id=medicine_id
    ).order_by(
        Batch.expiry_date.asc()
    ).all()

    return jsonify({
        "medicine": medicine_to_dict(medicine),
        "batches": [
            {
                "id": batch.id,
                "batch_number": batch.batch_number,
                "quantity": batch.quantity,
                "expiry_date": batch.expiry_date.isoformat(),
                "is_expired": batch.expiry_date < today
            }
            for batch in batches
        ]
    })


# -------------------------------------------------
# Batches / Restocking
# -------------------------------------------------

@app.route("/api/medicines/<int:medicine_id>/batches", methods=["POST"])
@token_required
def add_batch(medicine_id):

    medicine = db.session.get(Medicine, medicine_id)

    if not medicine:
        return jsonify({
            "error": "Medicine not found"
        }), 404

    data = request.get_json(silent=True) or {}

    batch_number = data.get("batch_number", "").strip()
    quantity = data.get("quantity")
    expiry_date = data.get("expiry_date", "")

    if not batch_number or quantity is None or not expiry_date:
        return jsonify({
            "error": "Batch number, quantity and expiry date are required"
        }), 400

    try:
        quantity = int(quantity)
        expiry = date.fromisoformat(expiry_date)

    except (ValueError, TypeError):
        return jsonify({
            "error": "Quantity must be an integer and expiry_date must be YYYY-MM-DD"
        }), 400

    if quantity <= 0:
        return jsonify({
            "error": "Quantity must be greater than zero"
        }), 400

    if expiry <= date.today():
        return jsonify({
            "error": "New batch must have a future expiry date"
        }), 400

    batch = Batch(
        medicine_id=medicine_id,
        batch_number=batch_number,
        quantity=quantity,
        expiry_date=expiry
    )

    db.session.add(batch)
    db.session.commit()

    return jsonify({
        "message": "Batch added",
        "batch": {
            "id": batch.id,
            "batch_number": batch.batch_number,
            "quantity": batch.quantity,
            "expiry_date": batch.expiry_date.isoformat()
        }
    }), 201


# -------------------------------------------------
# FEFO Dispensing
# -------------------------------------------------

@app.route("/api/medicines/<int:medicine_id>/dispense", methods=["POST"])
@token_required
def dispense_medicine(medicine_id):

    medicine = db.session.get(Medicine, medicine_id)

    if not medicine:
        return jsonify({
            "error": "Medicine not found"
        }), 404

    data = request.get_json(silent=True) or {}

    requested_quantity = data.get("quantity")

    try:
        requested_quantity = int(requested_quantity)

    except (ValueError, TypeError):
        return jsonify({
            "error": "Quantity must be an integer"
        }), 400

    if requested_quantity <= 0:
        return jsonify({
            "error": "Quantity must be greater than zero"
        }), 400

    today = date.today()

    batches = Batch.query.filter(
        Batch.medicine_id == medicine_id,
        Batch.expiry_date >= today,
        Batch.quantity > 0
    ).order_by(
        Batch.expiry_date.asc(),
        Batch.id.asc()
    ).all()

    available_stock = sum(
        batch.quantity for batch in batches
    )

    if available_stock < requested_quantity:
        return jsonify({
            "error": "Insufficient sellable stock",
            "available_stock": available_stock,
            "requested_quantity": requested_quantity
        }), 400

    record = DispenseRecord(
        medicine_id=medicine_id,
        quantity=requested_quantity
    )

    db.session.add(record)

    remaining = requested_quantity
    allocations = []

    for batch in batches:

        if remaining == 0:
            break

        taken = min(batch.quantity, remaining)

        batch.quantity -= taken

        item = DispenseItem(
            record=record,
            batch_id=batch.id,
            quantity=taken
        )

        db.session.add(item)

        allocations.append({
            "batch_id": batch.id,
            "batch_number": batch.batch_number,
            "quantity_dispensed": taken,
            "expiry_date": batch.expiry_date.isoformat()
        })

        remaining -= taken

    db.session.commit()

    return jsonify({
        "message": "Medicine dispensed successfully",
        "medicine": medicine.name,
        "requested_quantity": requested_quantity,
        "allocations": allocations,
        "remaining_sellable_stock": get_sellable_stock(medicine_id)
    })


# -------------------------------------------------
# Expiry Alerts
# -------------------------------------------------

@app.route("/api/alerts/expiry", methods=["GET"])
@token_required
def expiry_alerts():

    days = request.args.get("days", 30, type=int)

    days = min(max(days, 1), 365)

    today = date.today()
    alert_until = today + timedelta(days=days)

    batches = Batch.query.filter(
        Batch.expiry_date >= today,
        Batch.expiry_date <= alert_until,
        Batch.quantity > 0
    ).order_by(
        Batch.expiry_date.asc()
    ).all()

    return jsonify({
        "alert_window_days": days,
        "alerts": [
            {
                "medicine_id": batch.medicine_id,
                "medicine_name": batch.medicine.name,
                "batch_id": batch.id,
                "batch_number": batch.batch_number,
                "quantity": batch.quantity,
                "expiry_date": batch.expiry_date.isoformat(),
                "days_until_expiry": (
                    batch.expiry_date - today
                ).days
            }
            for batch in batches
        ]
    })


# -------------------------------------------------
# Create database
# -------------------------------------------------

with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True, port=5000)