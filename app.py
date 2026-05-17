from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_required
from dotenv import load_dotenv
import os
from datetime import datetime
from models import db, Produit, Stock, CommandeFournisseur, Categorie
from api import api

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Register API Blueprint
app.register_blueprint(api, url_prefix='/api/v1')

# Simple activity log for dashboard (in-memory for demo)
activities = []

# Configure Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'

# User loader temporaire (stub) pour éviter l'erreur Flask-Login
# Note: La table utilisateur n'existe pas dans la base actuelle
@login_manager.user_loader
def load_user(user_id):
    # Retourne None temporairement pour éviter le blocage lors de la soutenance
    return None

@app.route('/dashboard')
def dashboard():
    with app.app_context():
        # Récupérer le nombre total de produits distincts
        total_produits = Produit.query.count()
        
        # Récupérer le nombre de produits en alerte (via la table Stock)
        produits_en_alerte = 0
        for stock in Stock.query.all():
            if stock.est_en_alerte:
                produits_en_alerte += 1
        
        # Récupérer le nombre de commandes fournisseurs avec le statut 'EN_ATTENTE'
        commandes_en_cours = CommandeFournisseur.query.filter_by(statut='EN_ATTENTE').count()
        
        return render_template('dashboard.html', 
                              total_produits=total_produits,
                              produits_en_alerte=produits_en_alerte,
                              commandes_en_cours=commandes_en_cours,
                              activities=activities)

@app.route('/reception', methods=['GET', 'POST'])
def reception():
    if request.method == 'POST':
        with app.app_context():
            # Récupérer les données du formulaire
            reference = request.form.get('reference')
            quantite = request.form.get('quantite')
            
            if reference and quantite:
                try:
                    quantite_int = int(quantite)
                    
                    # Mettre à jour le stock pour le produit
                    stock = Stock.query.get(reference)
                    if stock:
                        ancien_stock = stock.quantite_disponible
                        stock.quantite_disponible += quantite_int
                        db.session.commit()
                        
                        # Ajouter l'activité à l'historique
                        activities.append({
                            'type': 'Réception',
                            'reference': reference,
                            'quantite': quantite_int,
                            'ancien_stock': ancien_stock,
                            'nouveau_stock': stock.quantite_disponible,
                            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                        
                        flash(f'Réception enregistrée avec succès ! Stock mis à jour pour {reference}', 'success')
                    else:
                        flash(f'Produit avec référence {reference} non trouvé', 'error')
                    
                    return redirect(url_for('dashboard'))
                except Exception as e:
                    db.session.rollback()
                    flash(f'Erreur lors de l\'enregistrement: {str(e)}', 'error')
            else:
                flash('Veuillez remplir tous les champs obligatoires', 'error')
    
    return render_template('reception.html')

@app.route('/dashboard/rapports')
def rapports():
    with app.app_context():
        # Calculer la valeur totale du stock (quantite_disponible * prix_vente)
        valeur_totale_stock = 0
        produits_en_alerte = 0
        produits_normaux = 0
        
        # Requête pour joindre Produit et Stock
        query = db.session.query(Produit, Stock).join(Stock, Produit.reference == Stock.reference).all()
        
        for produit, stock in query:
            # Calculer la valeur de ce produit en stock
            valeur_produit = stock.quantite_disponible * float(produit.prix_vente)
            valeur_totale_stock += valeur_produit
            
            # Compter les produits en alerte vs normaux
            if stock.est_en_alerte:
                produits_en_alerte += 1
            else:
                produits_normaux += 1
        
        return render_template('rapports.html',
                              valeur_totale_stock=valeur_totale_stock,
                              produits_en_alerte=produits_en_alerte,
                              produits_normaux=produits_normaux)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
