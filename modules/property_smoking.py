from odoo import models, fields, _, api
import logging

_logger = logging.getLogger(__name__)

class PropertySmoking(models.Model):
    _name = 'property.smoking'
    _description = 'Permitido fumar'
    
    name = fields.Char(string='Nombre', required=True)