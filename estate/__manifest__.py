{

    "name":"Estate Management",
    "summary":"Estate management model",
    "license":"LGPL-3",
    "depends":['base','base_automation','crm'],
    "data":[#security
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        #views
        'views/estate_view.xml',
        'views/type_view.xml',
        'views/estate_tag.xml',
        'views/menus.xml',
        'wizard/negotiation_wizard_view.xml',
        #data
        'data/server_actions.xml',
        'data/mail_template_data.xml',
        #reports
        'report/estate_property_templates.xml',
        'report/estate_property_reports.xml',
        ],
    "demo":['demo/data.xml',]


}