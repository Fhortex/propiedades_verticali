from odoo import models, fields, _, api
import logging

_logger = logging.getLogger(__name__)

class PropertyCommission(models.Model):
    _name = 'property.commission'
    _description = 'Comisión'
    
    name = fields.Char(string='Nombre', required=True)