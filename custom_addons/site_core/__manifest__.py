# -*- coding: utf-8 -*-
{
    'name': 'Site Core',
    'version': '19.0.1.0.0',
    'category': 'Custom',
    'summary': 'Custom module for Site Core',
    'author': 'Independent Developer',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/menus.xml',
    ],
    'installable': True,
    'application': True,
}
