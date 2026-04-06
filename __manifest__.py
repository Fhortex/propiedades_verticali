{
    "name": "Propiedades Verticali",
    "version": "19.0",
    "author": "TChain",
    "license": "AGPL-3",
    "summary": "Propiedades Verticali",
    'category': 'CRM',
    'depends': ['crm_verticali'],
    'data': [
        #security
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        
        # views
        'views/verticali_property.xml',  
        'views/property_type.xml',
        'views/property_land_use.xml',
        'views/property_availability.xml',
        'views/property_status.xml',
        'views/property_commission_share.xml',
        'views/property_development.xml',
        'views/property_business_unit.xml',
        'views/property_development_type.xml',
        # 'views/res_municipaly.xml',
        'views/res_colony.xml',
        'views/res_colony_easybroker.xml',
        'views/res_zipcode.xml',
        'views/property_smoking.xml',
        'views/property_payment_method.xml',
        'views/property_invoice.xml',
        'views/property_giro.xml',
        'views/property_deposit.xml',
        'views/property_term.xml',
        'views/property_customer_profile.xml',
        'views/property_type_training.xml',
        'views/property_exclusive_time.xml',
        'views/property_commission.xml',
        'views/property_commission_type.xml',
        'views/property_fields.xml',
        'views/aval_warranty.xml',
        'views/crm_lead.xml',
        'views/commission_type.xml',
        'views/mapbox_template.xml',

        # wizard
        'wizard/update_fields.xml',
        'wizard/property_share.xml',
        'wizard/property_image_preview.xml',
        'wizard/property_report.xml',
        'wizard/property_change.xml',
        'wizard/upload_images.xml',

        # reports
        'reports/property_report_without_user.xml',
        
        #data
        'data/ir_cron.xml',
        'data/contracts_due_dates.xml',
        'data/ir_config_parameter.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # CSS
            'property_custom/static/src/css/property.css',
            'property_custom/static/src/css/custom_scroll.css',
            # OWL Templates
            'property_custom/static/src/xml/my_properties.xml',
            'property_custom/static/src/xml/image_dropzone.xml',
            'property_custom/static/src/xml/property_map.xml',
            # OWL Components
            'property_custom/static/src/js/my_properties.js',
            'property_custom/static/src/js/drag_and_drop.js',
            'property_custom/static/src/js/property_map.js',
            'property_custom/static/src/js/promotion_grid.js',
        ],
        'web.assets_frontend': [
            # Mapbox (also loaded dynamically by the map widget)
            'https://api.mapbox.com/mapbox-gl-js/v2.15.0/mapbox-gl.css',
            'https://api.mapbox.com/mapbox-gl-js/v2.15.0/mapbox-gl.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
