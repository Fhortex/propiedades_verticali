from odoo import models, fields, _, api
import logging

_logger = logging.getLogger(__name__)

class PropertyType(models.Model):
    _inherit = 'res.property'
    
    business_unit_ids = fields.Many2many('property.business.unit', string='Unidad de negocio', tracking=True)

    @api.model
    def get_data(self):
        records = self.sudo().search([])
        return {
            'records': [{"id": x.id, 
                         "name": x.name} for x in records],
        }