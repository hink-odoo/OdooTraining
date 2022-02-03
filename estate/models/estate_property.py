from operator import truediv
from signal import default_int_handler
from unicodedata import name
from odoo import models,fields,api,_
from odoo.exceptions import UserError, ValidationError


class EstatePropertOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Estate Property Offer'
    _order = 'price desc'

    price = fields.Float()
    status = fields.Selection([('accepted', 'Accepted'),('refuse', 'Refused')])
    partner_id = fields.Many2one('res.partner')
    property_id = fields.Many2one('estate.property')
    property_type_id = fields.Many2one(related='property_id.property_type_id', store=True)
    my_property_id = fields.Many2one('my.property')
    
    def action_accepted(self):
        for record in self:
            record.status = 'accepted'

    
    def action_refused(self):
        for record in self:
            record.status = 'refuse'

class ResPartner(models.Model):
    _inherit = 'res.partner'

    buyer_property_id = fields.One2many('estate.property', 'buyer_id')
    is_buyer = fields.Boolean()
    offer_ids = fields.One2many('estate.property.offer', 'partner_id')

# class ResUser(models.Model):
#     _inherit = "res.users"

#     property_id = fields.One2many('estate.property', 'salesman_id')
#     is_buyer=fields.Boolean()


class MyProperty(models.Model):
    _name = 'my.property'
    _description = 'My Property'

    name = fields.Char()
    property_offer_ids = fields.One2many('estate.property.offer', 'my_property_id')
    partner_id = fields.Many2one('res.partner')

class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Estate Property Type'
    _sql_constraints = [('postive_price', 'check(expected_price >0)', 'Enter positive value')]


    name = fields.Char(string="Property Type", default="Unknown", required=True)
    
class EstatePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Estate Property Tag'

    name = fields.Char(string="Property Tag", default="Unknown", required=True)




class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'real estate module'


    def _get_description(self):
        if self.env.context.get('is_my_property'):
            return self.env.user.name +'\'s property'

    ref_seq = fields.Char(string="Reference ID",default="New")
    name = fields.Char(string="Name", default="Unknown", required=True)
    description = fields.Text(default=_get_description)
    postcode = fields.Char()
    date_availability = fields.Date()
    expected_price = fields.Float()
    selling_price = fields.Float(copy=False, readonly=True)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection([
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West')        
        ])
    image = fields.Image()
    property_type_id = fields.Many2one('estate.property.type',string="Property Type")
    property_tag_ids = fields.Many2many('estate.property.tag',string="Property Tag")
    state = fields.Selection([('new', 'New'), ('sold', 'Sold'), ('cancel', 'Cancelled')], default='new')
    # validity = fields.Integer(default=7)
    # date_deadline = fields.Date(compute="_compute_date_deadline")
    total_area = fields.Float(compute='_compute_area',inverse='_inverse_area',store=True)
    property_offer_ids = fields.One2many('estate.property.offer', 'property_id')
    salesman_id = fields.Many2one('res.users')
    buyer_id = fields.Many2one('res.partner')

       
    def action_sold(self):
        for record in self:
            if record.state == 'cancel':
                raise UserError("Cancel Property cannot be sold")
            record.state = 'sold'

    def action_cancel(self):
        for record in self:
            if record.state == 'sold':
                raise UserError("Sold Property cannot be canceled")
            record.state = 'cancel'


    @api.depends('living_area','garden_area')
    def _compute_area(self):
        for record in self:
            record.total_area=record.living_area + record.garden_area


    def _inverse_area(self):
        for record in self:
            record.living_area = record.garden_area = record.total_area / 2



    @api.constrains('living_area', 'garden_area')
    def _check_garden_area(self):
        for record in self:
            if record.living_area < record.garden_area:
                raise ValidationError("Garden cannot be bigger than living area")

    def open_offers(self):
        view_id = self.env.ref('estate.estate_property_offer_tree').id
        return {
            "name": "Offers",
            "type": "ir.actions.act_window",
            "res_model": "estate.property.offer",
            "views": [[view_id, 'tree']],
            "target": "new",
            "domain": [('property_id', '=', self.id)]
        }

    def confirm_offers(self):
        view_id = self.env.ref('estate.estate_property_offer_tree').id
        return {
            "name": "Offers",
            "type": "ir.actions.act_window",
            "res_model": "estate.property.offer",
            "views": [[view_id, 'tree']],
            "target": "new",
            "domain": [('status', '=', 'accepted')]
        }

    @api.onchange("garden")
    def _onchange_area(self):
        for record in self:
            if record.garden:
                record.garden_area=10
                record.garden_orientation='north'
            else:
                record.garden_area=None
                record.garden_orientation=None

    # @api.model
    # def create(self,vals):
    #     vals = {'name': 'Azure', 'expected_price':'300000'}
    #     res = super(EstateProperty, self).create(vals)
    #     return res
 
    # def write(self,vals):
    #     print("\n write method is call",vals)
    #     res =  super(EstateProperty, self).write(vals)
    #     return res


    # def unlink(self):
    #     print("\nDelete method is    call")
    #     res =  super(EstateProperty, self).unlink()
    #     return res

    # def search(self):
    #     rec = self.env['Module.EstateProperty'].search([('id', '=', self.id),('id','=',self.id)])


