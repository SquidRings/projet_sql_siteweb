from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import urllib.parse
import pymysql

app = Flask(__name__)
# Database credentials
username = ''
password = ''
hostname = 'instance-mysql-8036.cnscfol279pa.eu-west-3.rds.amazonaws.com'
database = 'base_equipea'

# URL-encode the password
encoded_password = urllib.parse.quote_plus(password)

# Create the connection string
connection_string = f"mysql+pymysql://{username}:{encoded_password}@{hostname}/{database}"

# JWT configuration
app.config['SECRET_KEY'] = '56dfababe6b729f1802275c8fbcb4f01a45991f44e2d122f81561038778d94e0'
app.config['JWT_TOKEN_LOCATION'] = ['headers']
jwt = JWTManager(app)

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = connection_string
pymysql.install_as_MySQLdb()
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models for the views
class Role(db.Model):
    __tablename__ = 'role'
    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(255), unique=True, nullable=False)

class Permission(db.Model):
    __tablename__ = 'permission'
    permission_id = db.Column(db.Integer, primary_key=True)
    permission_name = db.Column(db.String(255), unique=True, nullable=False)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.role_id'))

    def get_id(self):
        return self.user_id

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

class RolePermission(db.Model):
    __tablename__ = 'role_permission'
    role_id = db.Column(db.Integer, db.ForeignKey('role.role_id'), primary_key=True)
    permission_id = db.Column(db.Integer, db.ForeignKey('permission.permission_id'), primary_key=True)
    role = db.relationship('Role', backref=db.backref('role_permissions', lazy=True))
    permission = db.relationship('Permission', backref=db.backref('role_permissions', lazy=True))
    
    
class ViewDriverPerformance(db.Model):
    __tablename__ = 'view_driver_performance'
    driver_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    total_wins = db.Column(db.Integer)
    total_podiums = db.Column(db.Integer)
    total_points = db.Column(db.Integer)
    total_fastest_laps = db.Column(db.Integer)

class F1Order(db.Model):
    order_id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.Date)
    vendor_id = db.Column(db.Integer)
    total_cost = db.Column(db.Integer)
    total_cost_excl_vat = db.Column(db.Float)
    order_status_id = db.Column(db.Integer)

class F1Car(db.Model):
    car_id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(255))
    year = db.Column(db.Integer)
    weight = db.Column(db.Numeric)
    fuel_capacity = db.Column(db.Numeric)
    technical_director = db.Column(db.String(255))
    main_driver_id = db.Column(db.Integer)
    co_driver_id = db.Column(db.Integer)

class F1Driver(db.Model):
    driver_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    nationality = db.Column(db.String(255))
    date_of_birth = db.Column(db.Date)
    years_active = db.Column(db.String(255))
    championships_won = db.Column(db.Integer)
    role = db.Column(db.String(255))
    measurement_id = db.Column(db.Integer)
    stat_id = db.Column(db.Integer)
    team_id = db.Column(db.Integer)

class F1DriverStats(db.Model):
    stat_id = db.Column(db.Integer, primary_key=True)
    season_year = db.Column(db.Integer)
    races_participated = db.Column(db.Integer)
    wins = db.Column(db.Integer)
    podiums = db.Column(db.Integer)
    points = db.Column(db.Integer)
    fastest_laps = db.Column(db.Integer)

class F1OrderStatus(db.Model):
    order_status_id = db.Column(db.Integer, primary_key=True)
    order_status = db.Column(db.String(255))
    description = db.Column(db.Text)

class F1Payment(db.Model):
    payment_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer)

class F1OrderItem(db.Model):
    order_item_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
    unit_price = db.Column(db.Integer)
    part_id = db.Column(db.Integer)

class F1CarConfig(db.Model):
    config_id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, nullable=False)
    driver_id = db.Column(db.Integer)
    brake_pressure = db.Column(db.Integer)
    aero = db.Column(db.Integer)
    transmission = db.Column(db.Integer)
    suspensions = db.Column(db.Integer)
    suspensions_geometry = db.Column(db.Integer)
    tyre_pressure = db.Column(db.Integer)
    tire_type = db.Column(db.String(255))
    weather_type = db.Column(db.String(255))
    livery = db.Column(db.String(255))
    car_config_part_id = db.Column(db.Integer)

class F1Race(db.Model):
    race_id = db.Column(db.Integer, primary_key=True)
    config_id = db.Column(db.Integer)
    season_year = db.Column(db.SmallInteger)
    round_number = db.Column(db.Integer)
    race_name = db.Column(db.String(255))
    circuit_id = db.Column(db.Integer)
    race_date = db.Column(db.Date)
    laps = db.Column(db.Integer)
    distance = db.Column(db.Numeric)
    winning_driver = db.Column(db.String(255))
    winning_team = db.Column(db.String(255))
    weather_conditions = db.Column(db.String(255))
    attendance = db.Column(db.Integer)
    championship_id = db.Column(db.Integer, nullable=False)

class F1Championship(db.Model):
    championship_id = db.Column(db.Integer, primary_key=True)
    season_year = db.Column(db.Integer)
    driver_champion = db.Column(db.String(255))
    team_champion = db.Column(db.String(255))
    total_races = db.Column(db.Integer)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)

class F1DriverMeasurements(db.Model):
    measurement_id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer)
    height_cm = db.Column(db.Numeric)
    weight_kg = db.Column(db.Numeric)
    seat_size = db.Column(db.String(255))
    helmet_size = db.Column(db.String(255))
    glove_size = db.Column(db.String(255))
    shoe_size = db.Column(db.String(255))
    measurement_date = db.Column(db.Date)

class F1Circuit(db.Model):
    circuit_id = db.Column(db.Integer, primary_key=True)
    circuit_name = db.Column(db.String(255))
    location = db.Column(db.String(255))
    country_id = db.Column(db.Integer)
    length_km = db.Column(db.Integer)
    number_of_corners = db.Column(db.Integer)
    capacity = db.Column(db.Integer)
    opened_year = db.Column(db.Integer)
    lap_record_time = db.Column(db.Time)
    lap_record_driver = db.Column(db.String(255))

class F1Team(db.Model):
    team_id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(255))
    team_budget = db.Column(db.Float)

class F1Vendor(db.Model):
    __tablename__ = 'f1_vendors' 
    vendor_id = db.Column(db.Integer, primary_key=True)
    vendor_name = db.Column(db.String(255), nullable=False, unique=True)
    location = db.Column(db.Text)
    contact_number = db.Column(db.Text)
    email = db.Column(db.Text)
    website = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP)
    updated_at = db.Column(db.TIMESTAMP)
    vendor_type_id = db.Column(db.Integer)

class F1Part(db.Model):
    part_id = db.Column(db.Integer, primary_key=True)
    part_name = db.Column(db.String(255))
    part_type = db.Column(db.String(255))
    serial_number = db.Column(db.Integer)
    vendor_id = db.Column(db.Integer)
    manufacture_date = db.Column(db.TIMESTAMP)
    last_inspection = db.Column(db.TIMESTAMP)
    status = db.Column(db.Integer)
    specifications = db.Column(db.Text)
    quantity = db.Column(db.Integer)
    condition = db.Column(db.String(255))
    number_of_uses = db.Column(db.Text)

class VendorType(db.Model):
    vendor_type_id = db.Column(db.Integer, primary_key=True)
    vendor_type = db.Column(db.String(255))


class ViewOrderDetails(db.Model):
    __tablename__ = 'view_order_details'
    order_id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.Date)
    vendor_name = db.Column(db.String(255))
    order_status = db.Column(db.String(255))
    total_cost = db.Column(db.Numeric(10, 2))
    total_cost_excl_vat = db.Column(db.Numeric(10, 2))

class ViewDriverDetails(db.Model):
    __tablename__ = 'view_driver_details'
    driver_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    nationality = db.Column(db.String(255))
    date_of_birth = db.Column(db.Date)
    years_active = db.Column(db.String(255))
    championships_won = db.Column(db.Integer)
    role = db.Column(db.String(255))
    team_name = db.Column(db.String(255))
    height_cm = db.Column(db.Numeric)
    weight_kg = db.Column(db.Numeric)
    seat_size = db.Column(db.String(255))
    helmet_size = db.Column(db.String(255))
    glove_size = db.Column(db.String(255))
    shoe_size = db.Column(db.String(255))

class ViewVendorPartsCount(db.Model):
    __tablename__ = 'view_vendor_parts_count'
    vendor_id = db.Column(db.Integer, primary_key=True)
    vendor_name = db.Column(db.String(255))
    vendor_type = db.Column(db.String(255))
    parts_count = db.Column(db.Integer)

class ViewRaceDetails(db.Model):
    race_id = db.Column(db.Integer, primary_key=True)
    race_name = db.Column(db.String(255))
    season_year = db.Column(db.Integer)
    round_number = db.Column(db.Integer)
    race_date = db.Column(db.Date)
    laps = db.Column(db.Integer)
    distance = db.Column(db.Numeric)
    winning_driver = db.Column(db.String(255))
    winning_team = db.Column(db.String(255))
    weather_conditions = db.Column(db.String(255))
    attendance = db.Column(db.Integer)
    circuit_name = db.Column(db.String(255))
    location = db.Column(db.String(255))
    country_name = db.Column(db.String(255))
    championship_year = db.Column(db.Integer)
    driver_champion = db.Column(db.String(255))
    team_champion = db.Column(db.String(255))

class ViewCarConfigDetails(db.Model):
    __tablename__ = 'view_car_config_details'
    config_id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(255))
    year = db.Column(db.Integer)
    driver_name = db.Column(db.String(255))
    brake_pressure = db.Column(db.Integer)
    aero = db.Column(db.Integer)
    transmission = db.Column(db.Integer)
    suspensions = db.Column(db.Integer)
    suspensions_geometry = db.Column(db.Integer)
    tyre_pressure = db.Column(db.Integer)
    tire_type = db.Column(db.String(255))
    weather_type = db.Column(db.String(255))
    livery = db.Column(db.String(255))

class ViewOrderItemsVendors(db.Model):
    __tablename__ = 'view_order_items_vendors'
    order_id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.Date)
    vendor_name = db.Column(db.String(255))
    order_status = db.Column(db.String(255))
    quantity = db.Column(db.Integer)
    unit_price = db.Column(db.Integer)
    part_name = db.Column(db.String(255))
    part_type = db.Column(db.String(255))
    serial_number = db.Column(db.Integer)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes for UI
@app.route('/')
@login_required
def root():
    return render_template('index.html')

@app.route('/home')
@login_required
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/api/login', methods=['POST'])
@login_required
def api_login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    user = User.query.filter_by(username=username, password=password).first()
    if user:
        access_token = create_access_token(identity={'username': user.username, 'role': user.role_id})
        return jsonify(access_token=access_token)
    else:
        return jsonify({"msg": "Invalid username or password"}), 401

@app.route('/drivers')
@login_required
def drivers():
    drivers = ViewDriverDetails.query.all()
    return render_template('drivers.html', drivers=drivers)

@app.route('/add_driver', methods=['GET', 'POST'])
@login_required
def add_driver():
    if request.method == 'POST':
        name = request.form['name']
        nationality = request.form['nationality']
        date_of_birth = request.form['date_of_birth']
        years_active = request.form['years_active']
        championships_won = request.form['championships_won']
        role = request.form['role']
        measurement_id = request.form['measurement_id']
        stat_id = request.form['stat_id']
        team_id = request.form['team_id']
        
        new_driver = F1Driver(name=name, nationality=nationality, date_of_birth=date_of_birth, years_active=years_active, championships_won=championships_won, role=role, measurement_id=measurement_id, stat_id=stat_id, team_id=team_id)
        db.session.add(new_driver)
        db.session.commit()
        
        return redirect(url_for('drivers'))
    
    return render_template('add_driver.html')

@app.route('/edit_driver/<int:driver_id>', methods=['GET', 'POST'])
@login_required
def edit_driver(driver_id):
    driver = F1Driver.query.get(driver_id)
    
    if request.method == 'POST':
        driver.name = request.form['name']
        driver.nationality = request.form['nationality']
        driver.date_of_birth = request.form['date_of_birth']
        driver.years_active = request.form['years_active']
        driver.championships_won = request.form['championships_won']
        driver.role = request.form['role']
        driver.measurement_id = request.form['measurement_id']
        driver.stat_id = request.form['stat_id']
        driver.team_id = request.form['team_id']
        
        db.session.commit()
        
        return redirect(url_for('drivers'))
    
    return render_template('edit_driver.html', driver=driver)

@app.route('/delete_driver/<int:driver_id>', methods=['POST', 'GET'])
@login_required
def delete_driver(driver_id):
    driver = F1Driver.query.get(driver_id)
    if driver:
        db.session.delete(driver)
        db.session.commit()
    return redirect(url_for('drivers'))

@app.route('/orders')
@login_required
def orders():
    orders = ViewOrderDetails.query.all()
    return render_template('orders.html', orders=orders)

@app.route('/add_order', methods=['GET', 'POST'])
@login_required
def add_order():
    if request.method == 'POST':
        order_date = request.form['order_date']
        vendor_id = request.form['vendor_id']
        total_cost = request.form['total_cost']
        total_cost_excl_vat = request.form['total_cost_excl_vat']
        order_status_id = request.form['order_status_id']

        new_order = F1Order(order_date=order_date, vendor_id=vendor_id, total_cost=total_cost, total_cost_excl_vat=total_cost_excl_vat, order_status_id=order_status_id)

        try:
            db.session.add(new_order)
            db.session.commit()
            return redirect(url_for('orders'))
        except pymysql.IntegrityError:
            db.session.rollback()
            error = "Invalid vendor ID. Please select a valid vendor."
            vendors = F1Vendor.query.all()
            order_statuses = F1OrderStatus.query.all()
            return render_template('add_orders.html', order_statuses=order_statuses, vendors=vendors, error=error)

    vendors = F1Vendor.query.all()
    order_statuses = F1OrderStatus.query.all()
    return render_template('add_orders.html', order_statuses=order_statuses, vendors=vendors)

@app.route('/edit_order/<int:order_id>', methods=['GET', 'POST'])
@login_required
def edit_order(order_id):
    order = F1Order.query.get(order_id)
    
    if request.method == 'POST':
        order.order_date = request.form['order_date']
        order.vendor_id = request.form['vendor_id']
        order.total_cost = request.form['total_cost']
        order.total_cost_excl_vat = request.form['total_cost_excl_vat']
        order.order_status_id = request.form['order_status_id']
        
        try:
            db.session.commit()
            return redirect(url_for('orders'))
        except pymysql.IntegrityError:
            db.session.rollback()
            error = "Invalid vendor ID. Please select a valid vendor."
            vendors = F1Vendor.query.all()
            order_statuses = F1OrderStatus.query.all()
            return render_template('edit_orders.html', order=order, order_statuses=order_statuses, vendors=vendors, error=error)
    
    vendors = F1Vendor.query.all()
    order_statuses = F1OrderStatus.query.all()
    return render_template('edit_orders.html', order=order, order_statuses=order_statuses, vendors=vendors)

@app.route('/delete_order/<int:order_id>', methods=['GET', 'POST'])
@login_required
def delete_order(order_id):
    order = F1Order.query.get(order_id)
    if order:
        db.session.delete(order)
        db.session.commit()
    return redirect(url_for('orders'))

@app.route('/cars')
@login_required
def cars():
    cars = F1Car.query.all()
    return render_template('cars.html', cars=cars)

@app.route('/driver_performance/<int:driver_id>', methods=['GET'])
@login_required
def get_driver_performance(driver_id):
    driver_performance = ViewDriverPerformance.query.get(driver_id)
    if driver_performance is None:
        return render_template('404.html'), 404
    return render_template('driver_performance.html', driver=driver_performance)

@app.route('/races', methods=['GET'])
@login_required
def races():
    races = ViewRaceDetails.query.all()
    return render_template('races.html', races=races)

@app.route('/car_config_details')
def car_config_details():
    details = ViewCarConfigDetails.query.all()
    return render_template('car_config_details.html', details=details)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
