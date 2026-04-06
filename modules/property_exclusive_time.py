from odoo import models, fields, _, api
import logging

_logger = logging.getLogger(__name__)

class PropertyExclusiveTime(models.Model):
    _name = 'property.exclusive.time'
    _description = 'Tiempo exclusiva'
    
    name = fields.Char(string='Nombre', required=True)