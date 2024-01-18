from flask import Flask, render_template, redirect, url_for, flash,session,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm,CSRFProtect
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from forms import LoginForm, ClientRegistrationForm, ManagerRegistrationForm,RentForm,UpdateEquipmentForm,AddEquipmentForm,OrderForm
from models import Client, Manager, db,Equipment,Ord
from decimal import Decimal
from datetime import datetime
from sqlalchemy import extract


app = Flask(__name__)
csrf = CSRFProtect(app)
app.config['WTF_CSRF_ENABLED'] = True


app.config['SECRET_KEY'] = 'sai'  # Change this to a secure secret key

# Flask-SQLAlchemy configuration with pymysql
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/medicalequipment'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Existing routes...
# Your existing imports..
@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')


@app.route('/client/orders/<int:order_id>/receipt', methods=['GET'])
def view_receipt(order_id):
    client_id = session.get('client_id')
    if client_id:
        client = Client.query.get(client_id)
        order = Ord.query.get(order_id)

        if order and order.client_id == client_id:
            equipment = Equipment.query.get(order.equipment_id)

            # Fetch the manufacturer's information
            manufacturer_name = equipment.manufacturer

            # Calculate pending amount
            pending_amount = max(order.total_price - order.amount_paid, 0)

            # Format dates for display
            start_date = order.start_date.strftime('%a %b %d %Y %H:%M:%S GMT%z')
            end_date = order.end_date.strftime('%a %b %d %Y %H:%M:%S GMT%z')

            return render_template('receipt.html', order=order, client=client, equipment=equipment,
                                   manufacturer_name=manufacturer_name,
                                   start_date=start_date, end_date=end_date, pending_amount=pending_amount)
        else:
            flash('Invalid order ID or unauthorized access to receipt.', 'danger')
            return redirect(url_for('client_dashboard'))
    else:
        return redirect(url_for('client_login'))


# Placeholder for client dashboard route
# Placeholder for client dashboard route
@app.route('/client/dashboard', methods=['GET', 'POST'])
def client_dashboard():
    client_id = session.get('client_id')
    if client_id:
        client = Client.query.get(client_id)

        equipment_data = Equipment.query.with_entities(
            Equipment.equipment_id,
            Equipment.equipment_name,
            Equipment.manufacturer,
            Equipment.rent_price_per_day,
            Equipment.quantity_in_store
        ).all()
        equipment_choices = [(equipment.equipment_id, equipment.equipment_name) for equipment in equipment_data]

        orders = Ord.query.filter_by(client_id=client_id).all()


        form = RentForm()
        form.equipment.choices = equipment_choices

        if form.validate_on_submit():
            equipment_id = form.equipment.data
            quantity_to_rent = form.quantity.data
            start_date = form.start_date.data
            end_date = form.end_date.data
            amount_paid=form.amount_paid.data
            equipment = Equipment.query.get(equipment_id)

            if equipment and equipment.rent_equipment(quantity_to_rent):
                duration = (end_date - start_date).days + 1
                total_amount = float(equipment.rent_price_per_day) * quantity_to_rent * duration
                amount_to_pay = total_amount  # Modify this based on your business logic
                payment_date = datetime.now()
                # Store the rental information in the database (ord table)
                ord_entry = Ord(
                    client_id=client_id,
                    equipment_id=equipment_id,
                    start_date=start_date,
                    end_date=end_date,
                    total_price=total_amount,
                    amount_paid=amount_paid,
                    payment_date=payment_date
                )
                db.session.add(ord_entry)
                db.session.commit()

                flash('Equipment rented successfully!', 'success')
                return redirect(url_for('view_receipt',order_id=ord_entry.order_id))
            else:
                flash('Failed to rent equipment. Check availability and try again.', 'danger')

        return render_template('client_dashboard.html', client=client, equipment_data=equipment_data, form=form,orders=orders)
    else:
        return redirect(url_for('client_login'))
    
@app.route('/client/orders/<int:order_id>/edit', methods=['GET', 'POST'])
def edit_order(order_id):
    client_id = session.get('client_id')
    if client_id:
        client = Client.query.get(client_id)
        order = Ord.query.get(order_id)

        form = RentForm(obj=order)
        form.equipment.choices = [(equipment.equipment_id, equipment.equipment_name) for equipment in Equipment.query.all()]

        if form.validate_on_submit():
            order.equipment_id = form.equipment.data
            order.quantity = form.quantity.data
            order.start_date = form.start_date.data
            order.end_date = form.end_date.data
            order.amount_paid = form.amount_paid.data  
            # Update order information in the database
            db.session.commit()

            flash('Order updated successfully!', 'success')
            return redirect(url_for('client_dashboard'))

        return render_template('edit_order.html', client=client, form=form)
    else:
        return redirect(url_for('client_login'))
    
@app.route('/client/orders/<int:order_id>/cancel')
def cancel_order(order_id):
    client_id = session.get('client_id')
    if client_id:
        # Fetch the order to be canceled
        order = Ord.query.get(order_id)

        # Check if the order belongs to the logged-in client
        if order:
            # Delete the order from the database
            db.session.delete(order)
            db.session.commit()

            flash('Order canceled successfully!', 'success')
        else:
            flash('You do not have permission to cancel this order.', 'danger')

        return redirect(url_for('client_dashboard'))
    else:
        return redirect(url_for('client_login'))
@app.route('/manager/dashboard')
def manager_dashboard():
    equipment_list = Equipment.query.all()

    return render_template('manager_dashboard.html', equipment_list=equipment_list)

# Placeholder for client login route
@app.route('/client/login', methods=['GET', 'POST'])
def client_login():
    form = LoginForm()

    if form.validate_on_submit():
        # Check the database for the username and password
        client = Client.query.filter_by(username=form.username.data, password=form.password.data).first()

        if client:
            flash('Client login successful!', 'success')
            session['client_id'] = client.client_id  # Store client ID in the session
            return redirect(url_for('client_dashboard'))
        else:
            flash('Invalid client credentials. Please try again.', 'danger')

    return render_template('client_login.html', form=form)
# Placeholder for manager login route
@app.route('/manager/login', methods=['GET', 'POST'])
def manager_login():
    form = LoginForm()  # Create an instance of the LoginForm

    if form.validate_on_submit():
        # Check the database for the username and password
        manager = Manager.query.filter_by( manager_username=form.username.data,  manager_password=form.password.data).first()

        if manager:
            flash('Manager login successful!', 'success')
            session['manager_id'] = manager.manager_id  # Store manager ID in the session
            return redirect(url_for('manager_dashboard'))
        else:
            flash('Invalid manager credentials. Please try again.', 'danger')

    # If the form is not submitted or validation fails, render the login template
    return render_template('manager_login.html', form=form)
# Placeholder for client registration route
@app.route('/client/register', methods=['GET', 'POST'])
def client_register():
    form = ClientRegistrationForm()

    if form.validate_on_submit():
        # Check if the username is already taken
        existing_client = Client.query.filter_by(username=form.username.data).first()
        if existing_client:
            flash('Username is already taken. Please choose another.', 'danger')
        else:
            # Add the new client to the database
            new_client = Client(
                client_name=form.client_name.data,
                client_address=form.client_address.data,
                telephone_number=form.telephone_number.data,
                username=form.username.data,
                password=form.password.data
            )
            db.session.add(new_client)
            db.session.commit()

            flash('Client registration successful!', 'success')
            return redirect(url_for('client_login'))

    return render_template('client_register.html', form=form)

# Placeholder for manager registration route
@app.route('/manager/register', methods=['GET', 'POST'])
def manager_register():
    form = ManagerRegistrationForm()

    if form.validate_on_submit():
        # Check if the username is already taken
        existing_manager = Manager.query.filter_by(manager_username=form.username.data).first()
        if existing_manager:
            flash('Username is already taken. Please choose another.', 'danger')
        else:
            # Add the new manager to the database
            new_manager = Manager(
                manager_name=form.manager_name.data,
                manager_username=form.username.data,
                manager_password=form.password.data
            )
            db.session.add(new_manager)
            db.session.commit()

            flash('Manager registration successful!', 'success')
            return redirect(url_for('manager_login'))

    return render_template('manager_register.html', form=form)

# Your existing routes...

@app.route('/update/equipment/<int:equipment_id>', methods=['GET', 'POST'])
def update_equipment(equipment_id):
    equipment = Equipment.query.get_or_404(equipment_id)
    form = UpdateEquipmentForm(obj=equipment)

    if request.method == 'POST' and form.validate_on_submit():
        # Update equipment details based on form data
        equipment.equipment_name = form.equipment_name.data
        equipment.manufacturer = form.manufacturer.data
        equipment.description = form.description.data
        equipment.rent_price_per_day = form.rent_price_per_day.data
        equipment.quantity_in_store = form.quantity_in_store.data
        print("Form data:", request.form)

        # Commit changes to the database
        db.session.commit()

        flash('Equipment details updated successfully!', 'success')
        return redirect(url_for('manager_dashboard'))

    return render_template('update_equipment.html', equipment=equipment, form=form)
@app.route('/addequipment', methods=['GET', 'POST'])
def addeqp():
    form = AddEquipmentForm()

    return render_template('add_equipment.html',form=form)

@app.route('/add/equipment', methods=['GET', 'POST'])
def add_equipment():
    form = AddEquipmentForm()

    if form.validate_on_submit():
        # Create a new Equipment instance and set its attributes based on the form data
        new_equipment = Equipment(
            equipment_name=form.equipment_name.data,
            manufacturer=form.manufacturer.data,
            description=form.description.data,
            rent_price_per_day=form.rent_price_per_day.data,
            quantity_in_store=form.quantity_in_store.data,
            supplier_id=form.supplier_id.data,
            # Set other attributes as needed
        )

        # Add the new equipment to the database
        db.session.add(new_equipment)
        db.session.commit()

        flash('Equipment added successfully!', 'success')
        return redirect(url_for('manager_dashboard'))
    
    return render_template('add_equipment.html', form=form)
@app.route('/takeorder', methods=['GET', 'POST'])
def takeorder():
    form = OrderForm()
    form.client_selection.choices = [(client.client_id, client.client_name) for client in Client.query.all()]
    form.equipment.choices = [(equipment.equipment_id, equipment.equipment_name) for equipment in Equipment.query.all()]
    return render_template('take_order.html', form=form)


@app.route('/take/order', methods=['GET', 'POST'])
def take_order():
    form = OrderForm()

    # Populate client and equipment choices (adjust based on your models)
    form.client_selection.choices = [(client.client_id, client.client_name) for client in Client.query.all()]
    form.equipment.choices = [(equipment.equipment_id, equipment.equipment_name) for equipment in Equipment.query.all()]

    if form.validate_on_submit():
        # Calculate total amount based on quantity and days
        # (Assuming you have a function calculate_total_amount)
        price_per_day = Equipment.query.get(form.equipment.data).rent_price_per_day
        number_of_days_rented = (form.end_date.data - form.start_date.data).days
        calculated_total_amount = price_per_day * form.quantity.data * number_of_days_rented

        new_order = Ord(
            client_id=form.client_selection.data,
            equipment_id=form.equipment.data,
            quantity=form.quantity.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            total_price=calculated_total_amount,  # Rename the variable to avoid naming conflict
            amount_paid=form.amount_paid.data,
            payment_date=datetime.now(),  # Set payment date to the current date
        )

        # Add the new order to the database
        db.session.add(new_order)
        db.session.commit()

        flash('Order taken successfully!', 'success')
        return redirect(url_for('manager_dashboard'))

    return render_template('take_order.html', form=form)

@app.route('/clients', methods=['GET'])
def clients_list():
    # Fetch the list of clients from the database (adjust based on your models)
    clients = Client.query.all()

    return render_template('clients_list.html', clients=clients)

@app.route('/order/history/<int:client_id>', methods=['GET'])
def order_history(client_id):
    # Fetch the client from the database (adjust based on your models)
    client = Client.query.get(client_id)

    # Fetch the order history for the client along with equipment information
    # (adjust based on your models and relationships)
    orders = db.session.query(Ord, Equipment.equipment_name).\
        join(Equipment, Ord.equipment_id == Equipment.equipment_id).\
        filter(Ord.client_id == client_id).all()

    return render_template('order_history.html', client=client, orders=orders)

@app.route('/report/order_history', methods=['GET'])
def order_history_report():
    # Fetch all order history along with client names
    # (adjust based on your models and relationships)
    orders = db.session.query(Ord, Client.client_name, Equipment.equipment_name).\
        join(Client, Ord.client_id == Client.client_id).\
        join(Equipment, Ord.equipment_id == Equipment.equipment_id).all()

    return render_template('order_history_report.html', orders=orders)

@app.route('/report/paymentreport', methods=['GET'])
def paymentreport():
    # Fetch all order history along with client names
    # (adjust based on your models and relationships)
    orders = db.session.query(Ord, Client.client_name, Equipment.equipment_name).\
        join(Client, Ord.client_id == Client.client_id).\
        join(Equipment, Ord.equipment_id == Equipment.equipment_id).all()

    return render_template('payments_report.html', orders=orders)

@app.route('/report/pending_payments', methods=['GET'])
def pending_payments_report():
    # Fetch orders with pending payments
    # (adjust based on your models and relationships)
    pending_payments = db.session.query(Ord, Client.client_name, Equipment.equipment_name).\
        join(Client, Ord.client_id == Client.client_id).\
        join(Equipment, Ord.equipment_id == Equipment.equipment_id).\
        filter(Ord.amount_paid < Ord.total_price).all()

    return render_template('pending_payments_report.html', pending_payments=pending_payments)

@app.route('/report/monthly_profit', methods=['GET'])
def monthly_profit_report():
    selected_month = request.args.get('month')
    selected_year = request.args.get('year')

    if selected_month:
        # Filter by selected month
        filters = [extract('month', Ord.payment_date) == selected_month]
    else:
        filters = []

    if selected_year:
        # Filter by selected year
        filters.append(extract('year', Ord.payment_date) == selected_year)

    if filters:
        # Calculate profit for the selected month and year
        # (adjust based on your models and relationships)
        selected_month_profit = db.session.query(
            extract('year', Ord.payment_date).label('year'),
            extract('month', Ord.payment_date).label('month'),
            db.func.sum(Ord.total_price).label('total_monthly_amount'),
            (0.45 * db.func.sum(Ord.total_price)).label('profit')
        ).filter(*filters).group_by('year', 'month').first()

        return render_template('monthly_profit_data.html', selected_month_profit=selected_month_profit)

    else:
        # Fetch monthly profits for all months and years
        monthly_profits = db.session.query(
            extract('year', Ord.payment_date).label('year'),
            extract('month', Ord.payment_date).label('month'),
            db.func.sum(Ord.total_price).label('total_monthly_amount'),
            (0.45 * db.func.sum(Ord.total_price)).label('profit')
        ).group_by('year', 'month').all()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # If the request is an AJAX request, return JSON
            return jsonify(render_template('monthly_profit_data.html', monthly_profits=monthly_profits))
        else:
            # If the request is a regular request, return HTML
            return render_template('monthly_profit_report.html', monthly_profits=monthly_profits)

if __name__ == '__main__':
    app.run(debug=True)
