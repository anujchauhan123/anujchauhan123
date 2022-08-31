# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Callingata(models.Model):
    _name = 'calling_data.calling_data'
    _order = "id desc"
    _description = 'calling_data calling_data'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _primary_email = 'e_mail'


    s_no = fields.Integer()
    company_name = fields.Char()
    address_details = fields.Char()
    city = fields.Char()
    mobile = fields.Char()
    e_mail = fields.Char("E-mail")
    lead_manager = fields.Char()
    assigned_to = fields.Char()
    status = fields.Selection([
        ('interested', 'Interested'), ('nointerested', 'Not Interested')], string="Status")

    lead_manager = fields.Many2one('res.users',string="Lead Manager")
    assigned_to = fields.Many2one('res.users',string="Assigned To")
    loan_amount = fields.Char("loan amount")
    year = fields.Char("year")
    Approved_loan = fields.Char("Approved loan")

