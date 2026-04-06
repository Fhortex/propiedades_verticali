from odoo import models, fields, _, api
import urllib.request
import urllib.parse
import json

import requests
from urllib.parse import quote

import logging

_logger = logging.getLogger(__name__)

BASE_URL = "https://api.verticali.mx/api/locations"

class Colony(models.Model):
    _name = 'res.colony'
    _description = 'Colonia'
    
    name = fields.Char(string='Nombre', required=True)
    zona_id = fields.Many2one('res.zona', string='Municipio', required=True)
    zipcode_id = fields.Many2one('res.zipcode', string='Código postal', required=True)

class ColonyEasyBroker(models.Model):
    _name = 'res.colony.easybroker'
    _inherit = 'res.colony'
    _description = 'Colonia'

    location = fields.Char(string='Ubicacion', required=True)
    zipcode_id = fields.Many2one(required=False)

    @api.depends('name', 'location')
    def _compute_display_name(self):
        for record in self:
            if record.location:
                record.display_name = f"{record.name} ({record.location})"
            else:
                record.display_name = record.name or ''

    @api.onchange('zona_id')
    def onchange_cities(self):
        for r in self:
            params = {
                "state": r.zona_id.state_id.name,
                "city": r.zona_id.name,
            }
            # if r.colony_id:
            #     params.update({"name": r.colony_id.name})
            url = f"{BASE_URL}?{urllib.parse.urlencode(params)}"
            try:
                with urllib.request.urlopen(url) as response:
                    data = json.loads(response.read().decode("utf-8"))
                    _logger.error(data)
                    for i in data.get('data', []):
                        if r['name'] == r.name:
                            r.location = i['id']
                            break
            except urllib.error.HTTPError as e:
                response_data = e.read().decode('utf‑8')
                raise UserError("Error en la petición: %s" %(response_data))
            except urllib.error.URLError as e:
                raise UserError("Error de conexión: %s"% e.reason)

    # @api.model
    # def create_locations(self):
    #     zonas = self.env['res.zona'].sudo().search([])

    #     total = len(zonas)
    #     if total == 0:
    #         _logger.warning("No hay zonas configuradas para procesar.")
    #         return

    #     for index, zona in enumerate(zonas, start=1):
    #         state_name = zona.state_id.name
    #         city_name = zona.name

    #         _logger.info("🔄 Procesando zona: %s (%d/%d - %.2f%%)", city_name, index, total, index / total * 100)

    #         params = {
    #             "state": state_name,
    #             "city": city_name,
    #         }

    #         url = f"{BASE_URL}?{urllib.parse.urlencode(params)}"

    #         try:
    #             with urllib.request.urlopen(url) as response:
    #                 response_data = response.read().decode("utf-8")
    #                 json_data = json.loads(response_data)
    #                 colonies = json_data.get('data', [])

    #                 for col in colonies:
    #                     if col.get('city') == city_name and col.get('state', '').lower() == state_name.lower():
    #                         self.env['res.colony.easybroker'].sudo().create({
    #                             "name": col.get('name'),
    #                             "location": col.get('id'),
    #                             "zona_id": zona.id
    #                         })
    #                         self.env.cr.commit()
    #         except urllib.error.HTTPError as e:
    #             error_body = e.read().decode('utf-8')
    #             _logger.error("❌ HTTPError para zona '%s': %s", city_name, error_body)
    #         except urllib.error.URLError as e:
    #             _logger.error("❌ URLError para zona '%s': %s", city_name, e.reason)
    #         except json.JSONDecodeError as e:
    #             _logger.error("❌ JSON inválido recibido para zona '%s': %s", city_name, str(e))
    #         except Exception as e:
    #             _logger.exception("❌ Error inesperado para zona '%s': %s", city_name, str(e))
