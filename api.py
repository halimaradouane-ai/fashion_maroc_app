from flask import Blueprint, jsonify
from models import db, Produit, Stock

api = Blueprint('api', __name__)

@api.route('/produits', methods=['GET'])
def get_produits():
    """Récupère tous les produits avec leurs informations de stock"""
    produits_data = []
    
    # Requête pour joindre Produit et Stock
    query = db.session.query(Produit, Stock).join(Stock, Produit.reference == Stock.reference).all()
    
    for produit, stock in query:
        produit_info = {
            'id': produit.reference,
            'designation': produit.libelle,
            'quantite_stock': stock.quantite_disponible,
            'seuil_alerte': stock.seuil_minimum,
            'est_en_alerte': stock.est_en_alerte,
            'prix_vente': float(produit.prix_vente),
            'taille': produit.taille,
            'couleur': produit.couleur
        }
        produits_data.append(produit_info)
    
    return jsonify({
        'success': True,
        'count': len(produits_data),
        'data': produits_data
    })
