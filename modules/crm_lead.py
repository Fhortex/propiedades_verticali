from odoo import models, fields, _, api
from odoo.exceptions import AccessError
from lxml import etree
import logging

_logger = logging.getLogger(__name__)

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    property = fields.Many2one('verticali.property', string='Propiedad seleccionada')

    @api.onchange('property_identifier')
    def onchange_property_identifier(self):
        for r in self:
            if r.property_identifier:
                property = self.env['verticali.property'].search(['|',('id_eb','=',self.property_identifier),
                                                                      ('id_marketplace','=',self.property_identifier)],limit=1)
                if property:
                    for f in ['property_id','type_ope','state_id','zona_id']:
                        r[f] = property[f]
                    r.max_budget_amount = property.price
                    r.expected_revenue = property.price
                    r.property_url = property.url
                    r.probability = 0
                    r.adviser_id = property.adviser_id
                    if not r.partner_id.user_id:
                        r.user_id = property.adviser_id.user_ids
                    r.name = property.title
                    r.property = property