from odoo import models, fields, _, api
import logging

_logger = logging.getLogger(__name__)

class ZipCode(models.Model):
    _name = 'res.zipcode'
    _description = 'Código postal'
    
    name = fields.Char(string='Código', required=True)
    municipality_id = fields.Many2one('res.zona', string='Municipio', required=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'El código postal debe ser único en el sistema.')
    ]