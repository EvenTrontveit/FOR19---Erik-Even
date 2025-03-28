from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Erstatt med din egen nøkkel
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///carbon_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modell for transportdata
class TransportData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transport_mode = db.Column(db.String(50), nullable=False)
    distance = db.Column(db.Float, nullable=False)
    carbon_footprint = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# Modell for brukere
class User(db.Model):
    __tablename__ = "user_table"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)

def calculate_carbon(transport_mode, distance):
    # Utslippsfaktorer i kg CO₂ per km
    emission_factors = {
        'bil': 0.192,
        'buss': 0.105,
        'tog': 0.041,
        'fly': 0.254
    }
    factor = emission_factors.get(transport_mode, 0)
    return distance * factor

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        transport_mode = request.form.get('transport_mode')
        distance = request.form.get('distance')
        try:
            distance = float(distance)
        except ValueError:
            flash("Distanse må være et tall.")
            return redirect(url_for('index'))
        
        carbon = calculate_carbon(transport_mode, distance)
        new_entry = TransportData(
            transport_mode=transport_mode,
            distance=distance,
            carbon_footprint=carbon
        )
        try:
            db.session.add(new_entry)
            db.session.commit()
            flash(f'Data lagret! Karbonavtrykk: {carbon:.2f} kg CO₂')
        except Exception as e:
            db.session.rollback()
            flash(f'Databasefeil: {str(e)}')
        
        return redirect(url_for('index'))
    
    return render_template('index.html')

if __name__ == '__main__':
    # Oppretter alle tabeller (både TransportData og User)
    with app.app_context():
        db.create_all()
    app.run(debug=True)
