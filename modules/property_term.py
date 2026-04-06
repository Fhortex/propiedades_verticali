from odoo import models, fields, _, api
import logging

_logger = logging.getLogger(__name__)

class PropertyTerm(models.Model):
    _name = 'property.term'
    _description = 'Plazo mínimo'
    
    name = fields.Char(string='Nombre', required=True)