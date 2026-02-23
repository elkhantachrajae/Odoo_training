{
    'name': 'Gestion des Réservations',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Gérer les réservations et générer des devis',
    'depends': ['base','sale', 'website','portal','mail'],
    'data': [
        'security/ir.model.access.csv', 
        'data/ir_sequence_data.xml',
        'views/reservation_report_views.xml',
        'views/reservation_views.xml',
        'views/reservation_menu.xml',
        'views/portal_templates.xml',
        'report/reservation_report_template.xml',
        'report/reservation_report.xml',
        'wizard/reservation_report_wizard_view.xml',
    ],
    'installable': True,
    'application': True,

}