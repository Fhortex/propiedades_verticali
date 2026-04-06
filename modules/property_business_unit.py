from odoo import models, fields, _, api
import logging

_logger = logging.getLogger(__name__)

class PropertyBusinessUnit(models.Model):
    _name = 'property.business.unit'
    _description = 'Unidad de negocio'
    
    name = fields.Char(string='Nombre', required=True)