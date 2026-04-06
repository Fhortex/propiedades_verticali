# -*- coding: utf-8 -*-

from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class PropertyShare(models.TransientModel):
    _name = 'property.report'
    _description = 'Ficha técnica'

    property_id = fields.Many2one('verticali.property', string='Propiedad')
    title = fields.Char(string='Título del anuncio')
    description = fields.Text(string='Descripción anuncio')
    image_ids = fields.Many2many('verticali.property.image', string='Imagenes')
    user_id = fields.Many2one('res.users', string='Comercial')
    show_investment = fields.Boolean(string='¿Mostrar información para inversión?', default=False)

    @api.onchange('property_id')
    def onchange_property(self):
        for r in self:
            r.title = r.property_id.title
            r.description = r.property_id.description
            r.image_ids = [(6,0,r.property_id.image_ids.ids)]

    def print_report(self):
        report = self.env.ref('property_custom.property_report_without_user_report')
        if self.user_id:
            report = self.env.ref('property_custom.property_report_with_user_report')
        return report.report_action(self.property_id.ids)
            