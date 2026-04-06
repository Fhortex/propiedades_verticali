from odoo import models, fields, _, api
import logging

_logger = logging.getLogger(__name__)

class PropertyDevelopmentType(models.Model):
    _name = 'property.development.type'
    _description = 'Tipo de Desarrollo'
    
    name = fields.Char(string='Nombre', required=True)