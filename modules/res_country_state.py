from odoo import models, fields, _, api
import logging

_logger = logging.getLogger(__name__)

class State(models.Model):
    _inherit = 'res.country.state'
    
    @api.model
    def get_data(self, search, limit):
        _logger.error('get_data res.country.state')
        _logger.error(search)
        _logger.error(limit)
        # objs = self.sudo().search([])
        condition = ''
        if search:
            condition = ''' WHERE rcs.name like '%{search}%' '''.format(search=search) 
        self.env.cr.execute(f'''SELECT distinct rcs.id, rcs.name
                                FROM verticali_property vp 
                                INNER join res_country_state rcs on rcs.id = vp.state_id
                                {condition}''')
        objs = self.env.cr.dictfetchall()
        records = [{"id": 's{}'.format(x['id']), "name": 'Estado: {}'.format(x['name'])} for x in objs]
        
        #municipios
        # objs = self.env['res.zona'].sudo().search([])
        condition = ''
        if search:
            condition = ''' WHERE rz.name like '%{search}%' '''.format(search=search) 
        self.env.cr.execute(f'''SELECT distinct rz.id, rz.name
                                FROM verticali_property vp 
                                INNER join res_zona rz on rz.id = vp.zona_id
                                {condition}''')
        objs = self.env.cr.dictfetchall()
        records += [{"id": 'z{}'.format(x['id']), "name": 'Municipio: {}'.format(x['name'])} for x in objs]        

        #colony
        # objs = self.env['res.colony'].sudo().search([])
        condition = ''
        if search:
            condition = ''' WHERE rc.name like '%{search}%' '''.format(search=search) 
        self.env.cr.execute(f'''SELECT distinct rc.id, rc.name
                                FROM verticali_property vp 
                                INNER join res_colony rc on rc.id = vp.colony_id
                                {condition}''')
        objs = self.env.cr.dictfetchall()
        records += [{"id": 'c{}'.format(x['id']), "name": 'Colonia: {}'.format(x['name'])} for x in objs]        

        #desarrollo
        # objs = self.env['property.development'].sudo().search([])
        condition = ''
        if search:
            condition = ''' WHERE pd.name like '%{search}%' '''.format(search=search) 
        self.env.cr.execute(f'''SELECT distinct pd.id, pd.name
                                FROM verticali_property vp 
                                INNER join property_development pd on pd.id = vp.development_id
                                {condition}''')
        objs = self.env.cr.dictfetchall()
        records += [{"id": 'd{}'.format(x['id']), "name": 'Desarrollo: {}'.format(x['name'])} for x in objs]        
        _logger.error(records)
        return {'records': records}
