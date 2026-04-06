from odoo import models, fields, _, api
import logging

_logger = logging.getLogger(__name__)

class CommissionShare(models.Model):
    _name = 'property.commission.type'
    _description = 'Tipo de comisión'
    
    name = fields.Char(string='Nombre', required=True)
    type_ope = fields.Selection([
        ('Venta', 'Venta'),
        ('Renta', 'Renta'),
        ('Preventa', 'Preventa'),
    ], string='Tipo de operacion', default=False)
    type = fields.Selection([
        ('percentage', 'Porcentaje'),
        ('fixed', 'Cantidad fija'),
        ('months', 'Meses'),
    ], string='Tipo', default=False, required=True)