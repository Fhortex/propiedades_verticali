from odoo import models, fields, _, api
import logging

_logger = logging.getLogger(__name__)

class PropertyStatus(models.Model):
    _name = 'property.status'
    _description = 'Status'
    
    name = fields.Char(string='Nombre', required=True)

    @api.model
    def get_data(self):
        records = self.sudo().search([])
        return {
            'records': [{"id": x.id, 
                         "name": x.name} for x in records],
        }