{
    'name': 'Real Estate',
    'category' : 'Tools',
    'application' : True,
    #'description': """Real Estate model"""
    #'depends': ['base']
    'data': [
        'security/estate_security.xml',
        'security/ir.model.access.csv',
        'data/seq.xml',
        'views/estate_property_views.xml',
        'views/estate_property_manus.xml',
        'views/my_property_views.xml',
        'views/estate_template.xml',
        'wizard/estate_wizard_views.xml',
    ],

}
