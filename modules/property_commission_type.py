from odoo import models, fields, _, api
import logging

_logger = logging.getLogger(__name__)

class PropertyCommissionType(models.Model):
    _name = 'property.commission.type'
    _description = 'Tipo de comisión'
    
    name = fields.Char(string='Nombre', required=True)