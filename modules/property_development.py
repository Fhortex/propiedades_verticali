from odoo import models, fields, _, api
import logging

_logger = logging.getLogger(__name__)

class PropertyDevelopment(models.Model):
    _name = 'property.development'
    _description = 'Desarrollo'
    
    name = fields.Char(string='Nombre', required=True)
    property_type_id = fields.Many2one('res.property', string='Tipo de propiedad', tracking=True)
    related_business_unit_ids = fields.Many2many('property.business.unit', related='property_type_id.business_unit_ids', string='Unidad de negocio (relacionada)')
    business_unit_ids = fields.Many2many('property.business.unit', string='Unidad de negocio', tracking=True)
    development_type_ids = fields.Many2many('property.development.type', string='Tipo de desarrollo', tracking=True)

    country_id = fields.Many2one('res.country', string='País', tracking=True)
    state_id = fields.Many2one('res.country.state', string='Estado', tracking=True)
    zona_id = fields.Many2one('res.zona', string='Municipio', tracking=True)
    colony_id = fields.Many2one('res.colony', string='Colonia', tracking=True)
    street = fields.Char(string='Calle')
    street2 = fields.Char(string='Calle2')
    street3 = fields.Char(string='Calle3')
    zip = fields.Char(string='Codigo postal')