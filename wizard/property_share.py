# -*- coding: utf-8 -*-

from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class PropertyShare(models.TransientModel):
    _name = 'property.share'
    _description = 'Compartir propiedades'

    url = fields.Char(string='URL')
    is_owner = fields.Boolean(string='Es propietario')

    def create_report(self):
        action = self.env.ref('property_custom.action_property_report').read()[0]
        # res_id = self.env['property.report'].create({"property_id": self.env.context['active_id']})
        action['context'] = {"default_property_id": self.env.context['active_id']}
        return action