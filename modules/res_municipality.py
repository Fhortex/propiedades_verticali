from odoo import models, fields, _, api
import logging

_logger = logging.getLogger(__name__)

class Municipio(models.Model):
    _name = 'res.municipality'
    _description = 'Municipio'
    
    name = fields.Char(string='Nombre', required=True)
    state_id = fields.Many2one('res.country.state', string='Estado', required=True)