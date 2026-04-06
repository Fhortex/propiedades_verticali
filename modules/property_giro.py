from odoo import models, fields, _, api
import logging

_logger = logging.getLogger(__name__)

class PropertyGiro(models.Model):
    _name = 'property.giro'
    _description = 'Giro no permitido'
    
    name = fields.Char(string='Nombre', required=True)