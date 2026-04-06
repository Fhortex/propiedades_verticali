from odoo import models, fields, _, api
import logging

_logger = logging.getLogger(__name__)

class PropertyType(models.Model):
    _name = 'property.availability'
    _description = 'Disponibilidad'
    
    name = fields.Char(string='Nombre', required=True)


    @api.model
    def get_data(self):
        records = self.sudo().search([])
        _logger.error(records)
        return {
            'records': [{"id": x.id, 
                         "name": x.name} for x in records],
        }