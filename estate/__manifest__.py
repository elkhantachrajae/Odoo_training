{

    "name":"Estate Management",
    "summary":"Estate management model",
    "license":"LGPL-3",
    "depends":['base','crm'],
    "data":[#security
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        #views
        'views/estate_view.xml',
        'views/type_view.xml',
        'views/estate_tag.xml',
        'views/menus.xml',
        ],
    "demo":['data/data.xml']


}