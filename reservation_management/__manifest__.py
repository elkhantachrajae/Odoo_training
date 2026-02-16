{
    'name': 'Gestion des Réservations',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Gérer les réservations et générer des devis',
    'depends': ['base','sale', 'website','portal','mail'],
    'data': [
        'security/ir.model.access.csv', 
    ],
    'installable': True,
    'application': True,

}