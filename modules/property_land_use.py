from odoo import models, fields, _, api
import logging

_logger = logging.getLogger(__name__)

class PropertyLandUse(models.Model):
    _name = 'property.land.use'
    _description = 'Uso del suelo'
    
    name = fields.Char(string='Nombre')