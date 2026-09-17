from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(
        db.String(150),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )


class Medicine(db.Model):
    __tablename__ = "medicines"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(150),
        nullable=False,
        index=True
    )

    generic_name = db.Column(
        db.String(150),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    batches = db.relationship(
        "Batch",
        backref="medicine",
        lazy=True,
        cascade="all, delete-orphan"
    )


class Batch(db.Model):
    __tablename__ = "batches"

    id = db.Column(db.Integer, primary_key=True)

    medicine_id = db.Column(
        db.Integer,
        db.ForeignKey("medicines.id"),
        nullable=False
    )

    batch_number = db.Column(
        db.String(100),
        nullable=False
    )

    quantity = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    expiry_date = db.Column(
        db.Date,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )


class DispenseRecord(db.Model):
    __tablename__ = "dispense_records"

    id = db.Column(db.Integer, primary_key=True)

    medicine_id = db.Column(
        db.Integer,
        db.ForeignKey("medicines.id"),
        nullable=False
    )

    quantity = db.Column(
        db.Integer,
        nullable=False
    )

    dispensed_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    items = db.relationship(
        "DispenseItem",
        backref="record",
        lazy=True,
        cascade="all, delete-orphan"
    )


class DispenseItem(db.Model):
    __tablename__ = "dispense_items"

    id = db.Column(db.Integer, primary_key=True)

    dispense_record_id = db.Column(
        db.Integer,
        db.ForeignKey("dispense_records.id"),
        nullable=False
    )

    batch_id = db.Column(
        db.Integer,
        db.ForeignKey("batches.id"),
        nullable=False
    )

    quantity = db.Column(
        db.Integer,
        nullable=False
    )


# =====================================================
# NEW MODEL 1: QuarantineRecord
# =====================================================

class QuarantineRecord(db.Model):
    __tablename__ = "quarantine_records"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    batch_id = db.Column(
        db.Integer,
        db.ForeignKey("batches.id"),
        nullable=False
    )

    quantity = db.Column(
        db.Integer,
        nullable=False
    )

    reason = db.Column(
        db.String(255),
        nullable=False,
        default="Expired batch"
    )

    quarantined_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    batch = db.relationship("Batch")


# =====================================================
# NEW MODEL 2: NotificationOutbox
# =====================================================

class NotificationOutbox(db.Model):
    __tablename__ = "notification_outbox"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    medicine_id = db.Column(
        db.Integer,
        db.ForeignKey("medicines.id"),
        nullable=False
    )

    message = db.Column(
        db.String(500),
        nullable=False
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="pending"
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    medicine = db.relationship("Medicine")