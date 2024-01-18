
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Client(db.Model):
    client_id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100), nullable=False)
    client_address = db.Column(db.Text, nullable=False)
    telephone_number = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Manager(db.Model):
    manager_id = db.Column(db.Integer, primary_key=True)
    manager_name = db.Column(db.String(100), nullable=False)
    manager_username = db.Column(db.String(50), unique=True, nullable=False)
    manager_password = db.Column(db.String(255), nullable=False)



class Equipment(db.Model):
    equipment_id = db.Column(db.Integer, primary_key=True)
    equipment_name = db.Column(db.String(100), nullable=False)
    manufacturer = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    rent_price_per_day = db.Column(db.Float, nullable=False)
    quantity_in_store = db.Column(db.Integer, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supply.supplier_id'))

    # Define the relationship with the Supply table
    supplier = db.relationship('Supply', backref=db.backref('equipment', lazy=True))
    def rent_equipment(self, quantity_to_rent):
        # Check if there is enough quantity available for rent
        if self.quantity_in_store >= quantity_to_rent:
            # Reduce the quantity in store
            self.quantity_in_store -= quantity_to_rent
            db.session.commit()
            return True
        else:
            return False

class Supply(db.Model):
    supplier_id = db.Column(db.Integer, primary_key=True)
    supplier_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)


class Ord(db.Model):
    order_id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.client_id'), nullable=False)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.equipment_id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.Date, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    amount_paid = db.Column(db.Float, nullable=False, default=0.0)
    payment_date = db.Column(db.Date)
    
    client = db.relationship('Client', backref=db.backref('orders', lazy=True))
    equipment = db.relationship('Equipment', backref=db.backref('orders', lazy=True))

    
    