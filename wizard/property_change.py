# -*- coding: utf-8 -*-

from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class PropertyChange(models.TransientModel):
    _name = 'property.change'
    _description = 'Cambiar datos de propiedades'

    status_id = fields.Many2one('property.status', string='Status', tracking=True)
    availability_id = fields.Many2one('property.availability', string='Disponibilidad', tracking=True)
    parent_id = fields.Many2one('res.partner', string='Verticali', tracking=True)
    adviser_id = fields.Many2one('res.partner', domain=[('is_ct_adviser','=',True)], string='Vendedor', readonly=False)

    def default_get(self, fields_list):
        res = super(PropertyChange, self).default_get(fields_list)
        property_id = self.env['verticali.property'].browse(self.env.context['active_ids'])
        for f in ['status_id','availability_id','adviser_id']:
            res[f] = property_id[f] and property_id[f].id
        res['parent_id'] = self.env.user.company_id.partner_id.id
        return res
    
    def apply(self):
        property_id = self.env['verticali.property'].browse(self.env.context['active_ids'])
        if self.status_id:
            property_id.write({"status_id": self.status_id.id})
            #property_id.action_send()
        if self.availability_id:
            property_id.write({"availability_id": self.availability_id.id})
        if self.adviser_id:
            property_id.write({"adviser_id": self.adviser_id.id})
        return True
