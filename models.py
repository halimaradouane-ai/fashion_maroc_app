from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class Categorie(db.Model):
    __tablename__ = 'categorie'
    id_categorie = db.Column(db.Integer, primary_key=True)
    libelle_categorie = db.Column(db.String(100), nullable=False)
    produits = db.relationship('Produit', backref='categorie', lazy=True)

class Produit(db.Model):
    __tablename__ = 'produit'
    reference = db.Column(db.String(50), primary_key=True)
    libelle = db.Column(db.String(100), nullable=False)
    prix_vente = db.Column(db.Numeric(10, 2), nullable=False)
    taille = db.Column(db.String(20))
    couleur = db.Column(db.String(50))
    id_categorie = db.Column(db.Integer, db.ForeignKey('categorie.id_categorie'), nullable=False)
    stock = db.relationship('Stock', backref='produit', lazy=True, uselist=False)
    lignes_commande = db.relationship('LigneCommande', backref='produit', lazy=True)

class Stock(db.Model):
    __tablename__ = 'stock'
    reference = db.Column(db.String(50), db.ForeignKey('produit.reference'), primary_key=True)
    quantite_disponible = db.Column(db.Integer, default=0, nullable=False)
    seuil_minimum = db.Column(db.Integer, default=0, nullable=False)
    emplacement_rayon = db.Column(db.String(50))
    
    @property
    def est_en_alerte(self):
        return self.quantite_disponible <= self.seuil_minimum

class Fournisseur(db.Model):
    __tablename__ = 'fournisseur'
    id_fournisseur = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    telephone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    adresse = db.Column(db.Text)
    commandes = db.relationship('CommandeFournisseur', backref='fournisseur', lazy=True)

class CommandeFournisseur(db.Model):
    __tablename__ = 'commande_fournisseur'
    id_commande = db.Column(db.Integer, primary_key=True)
    id_fournisseur = db.Column(db.Integer, db.ForeignKey('fournisseur.id_fournisseur'), nullable=False)
    date_commande = db.Column(db.Date, nullable=False)
    statut = db.Column(db.String(20), default='EN_ATTENTE', nullable=False)
    date_livraison_prev = db.Column(db.Date)
    lignes = db.relationship('LigneCommande', backref='commande', lazy=True)

class LigneCommande(db.Model):
    __tablename__ = 'ligne_commande'
    id_commande = db.Column(db.Integer, db.ForeignKey('commande_fournisseur.id_commande'), primary_key=True)
    reference = db.Column(db.String(50), db.ForeignKey('produit.reference'), primary_key=True)
    quantite_commandee = db.Column(db.Integer, nullable=False)
    prix_unitaire_achat = db.Column(db.Numeric(10, 2), nullable=False)
    quantite_recue = db.Column(db.Integer, default=0, nullable=False)
