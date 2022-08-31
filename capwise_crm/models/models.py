# -*- coding: utf-8 -*-

import logging
import pytz
import threading
from collections import OrderedDict, defaultdict
from datetime import date, datetime, timedelta
from psycopg2 import sql
from geopy.geocoders import Nominatim
import xml.dom.minidom
from bs4 import BeautifulSoup
import re
from prettytable import PrettyTable

from dateutil.relativedelta import relativedelta

import base64
import xlwt
import io
from lxml import etree
import html2text

import requests
import json
from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.addons.iap.tools import iap_tools
from odoo.addons.mail.tools import mail_validation
from odoo.addons.phone_validation.tools import phone_validation
from odoo.exceptions import UserError, AccessError
from odoo.osv import expression
from odoo.tools.translate import _
from odoo.tools import date_utils, email_re, email_split, is_html_empty

_logger = logging.getLogger(__name__)

from odoo import models, fields, api


CRM_LEAD_FIELDS_TO_MERGE = [
    # UTM mixin
    'campaign_id',
    'medium_id',
    'source_id',
    # Mail mixin
    'email_cc',
    # description
    'name',
    'user_id',
    'company_id',
    'team_id',
    # pipeline
    'stage_id',
    # revenues
    'expected_revenue',
    # dates
    'create_date',
    'date_action_last',
    # partner / contact
    'partner_id',
    'title',
    'partner_name',
    'contact_name',
    'email_from',
    'mobile',
    'phone',
    'website',
    # address
    'street',
    'street2',
    'zip',
    'city',
    'state_id',
    'country_id',
]

# Subset of partner fields: sync any of those
PARTNER_FIELDS_TO_SYNC = [
    'mobile',
    'title',
    'function',
    'website',
]

# Subset of partner fields: sync all or none to avoid mixed addresses
PARTNER_ADDRESS_FIELDS_TO_SYNC = [
    'street',
    'street2',
    'city',
    'zip',
    'state_id',
    'country_id',
]

# Those values have been determined based on benchmark to minimise
# computation time, number of transaction and transaction time.
PLS_COMPUTE_BATCH_STEP = 50000  # odoo.models.PREFETCH_MAX = 1000 but larger cluster can speed up global computation
PLS_UPDATE_BATCH_STEP = 5000



class PaymentDetails(models.Model):
    _name = "payment.history"
    _description = "payment Details"
    

    Year = fields.Char("Year")
    Month = fields.Char("Month")
    Days_Past_Due = fields.Char("Days_Past_Due")
    Account_Number = fields.Char("Account_Number")


class AddressDeatilsLender(models.Model):
    _name = "address.userlender"
    _description = "Addres Details"

    address = fields.Char("Address")
    lender_data_test = fields.Many2one("lender.details", string="Lender")
    Account_Number = fields.Char("Account_Number")

class LendersDetails(models.Model):
    _name = "lender.details"
    _description = "Lender Details"

    Account_Number = fields.Char("Account_Number")
    Subscriber_Name = fields.Char("Subscriber_Name")
    Account_Type = fields.Selection([('01','AUTO LOAN'),
        ('02','HOUSING LOAN'),
        ('03','PROPERTY LOAN'),
        ('04','LOAN AGAINST SHARE/SECURITIES'),
        ('05','PERSONAL LOAN'),
        ('06','CONSUMER LOAN'),
        ('07','GOLD LOAN'),
        ('08','EDUCATIONAL LOAN'),
        ('09','LOAN TO PROFESSIONAL'),
        ('10','CREDIT CARD'),
        ('11','LEASING'),
        ('12','OVERDRAFT'),
        ('13','TWO-WHEELER LOAN'),
        ('14','NON-FUNDED CREDIT FACILITY'),
        ('15','LOAN AGAINST BANK DEPOSITS'),
        ('16','FLEET CARDS'),
        ('17','Commercial Vehicle Loan'),
        ('18','Telco-Wireless'),
        ('19','Telco-Broadband'),
        ('20','Telco-Landline'),
        ('23','GECL Secured'),
        ('24','GECL Unsecured'),
        ('31','Secured Credit Card'),
        ('32','Used Car Loan'),
        ('33','Construction Equipment Loan'),
        ('34','Tractor Loan'),
        ('35','Corporate Credit Card'),
        ('36','Kisan Credit Card'),
        ('37','Loan on Credit Card'),
        ('38','Prime Minister Jaan Dhan Yojana-Overdraft'),
        ('39','Mudra Loans – Shishu / Kishor / Tarun '),
        ('40','Microfinance – Business Loan'),
        ('41','Microfinance – Personal Loan'),
        ('42',' Microfinance – Housing Loan'),
        ('43','Microfinance – Others'),
        ('44','Pradhan Mantri Awas Yojana - Credit Link Subsidy Scheme MAY CLSS'),
        ('45','P2P Personal Loan'),
        ('46','P2P Auto Loan'),
        ('47','P2P Education Loan'),
        ('51','BUSINESS LOAN – GENERAL'),
        ('52','BUSINESS LOAN –PRIORITY SECTOR – SMALL BUSINESS '),
        ('53','BUSINESS LOAN –PRIORITY SECTOR – AGRICULTURE '),
        ('54','BUSINESS LOAN –PRIORITY SECTOR – OTHERS '),
        ('55','BUSINESS NON-FUNDED CREDIT FACILITY – GENERAL'),
        ('56','BUSINESS NON-FUNDED CREDIT FACILITY – PRIORITY SECTOR – SMALL BUSINESS'),
        ('57','BUSINESS NON-FUNDED CREDIT FACILITY – PRIORITY SECTOR – AGRICULTURE'),
        ('58','BUSINESS NON-FUNDED CREDIT FACILITY – PRIORITY SECTOR – OTHERS'),
        ('59','BUSINESS LOANS AGAINST BANK DEPOSITS'),
        ('60',' Staff Loan '),
        ('61','Business Loan - Unsecured '),
        ('00','Others')], string="Account_Type")
    Portfolio_Type = fields.Selection([('1','Individual'),
        ('2','Joint'),
        ('3','Authorized User'),
        ('7','Guarantor'),
        ('20','Deceased'),],string="Portfolio_Type")
    Open_Date = fields.Char("Open_Date")
    Account_Status = fields.Selection([('00','No Suit Filed'),
        ('89','Wilful default'),
        ('93','Suit Filed(Wilful default)'),
        ('97','Suit Filed(Wilful Default) and Written-off'),
        ('30','Restructure'),
        ('31','Restructured Loan (Govt. Mandated)'),
        ('32','Settled'),
        ('33','Post (WO) Settled '),
        ('34','Account Sold'),
        ('35','Written Off and Account Sold '),
        ('36','Account Purchased'),
        ('37','Account Purchased and Written Off'),
        ('38','Account Purchased and Settled'),
        ('39','Account Purchased and Restructured'),
        ('40','Status Cleared'),
        ('41','Restructured Loan'),
        ('42','Restructured Loan (Govt. Mandated)'),
        ('43','Written-off'),
        ('44','Settled'),
        ('45','Post (WO) Settled'),
        ('46','Account Sold'),
        ('47','Written Off and Account Sold'),
        ('48','Account Purchased'),
        ('49','Account Purchased and Written Off'),
        ('50','Account Purchased and Settled'),
        ('51','Account Purchased and Restructured'),
        ('52','Status Cleared'),
        ('53','Suit Filed'),
        ('54','Suit Filed and Written-off'),
        ('55','Suit Filed and Settled'),
        ('56','Suit Filed and Post (WO) Settled'),
        ('57','Suit Filed and Account Sold'),
        ('58','Suit Filed and Written Off and Account Sold'),
        ('59','Suit Filed and Account Purchased'),
        ('60','Suit Filed and Account Purchased and Written Off'),
        ('61','Suit Filed and Account Purchased and Settle'),
        ('62','Suit Filed and Account Purchased and Restructured'),
        ('63','Suit Filed and Status Cleared'),
        ('64','Wilful Default and Restructured Loan'),
        ('65','Wilful Default and Restructured Loan (Govt. Mandated)'),
        ('66','Wilful Default and Settled'),
        ('67','Wilful Default and Post (WO) Settled'),
        ('68','Wilful Default and Account Sold'),
        ('69','Wilful Default and Written Off and Account Sold'),
        ('70','Wilful Default and Account Purchased'),
        ('72','Wilful Default and Account Purchased and Written Off'),
        ('73','Wilful Default and Account Purchased and Settled'),
        ('74','Wilful Default and Account Purchased and Restructured'),
        ('75','Wilful Default and Status Cleared'),
        ('76','Suit filed (Wilful default) and Restructured'),
        ('77','Suit filed (Wilful default) and Restructured Loan (Govt. Mandated)'),
        ('79','Suit filed (Wilful default) and Settled'),
        ('85','Suit filed (Wilful default) and Account Sold'),
        ('81','Suit filed (Wilful default) and Post (WO) Settled'),
        ('86','Suit filed (Wilful default) and Written Off and Account Sold'),
        ('87','Suit filed (Wilful default) and Account Purchased'),
        ('88','Suit filed (Wilful default) and Account Purchased and Written Off'),
        ('94','Suit filed (Wilful default) and Account Purchased and Settled'),
        ('90','Suit filed (Wilful default) and Account Purchased and Restructured'),
        ('91','Suit filed (Wilful default) and Status Cleared'),
        ('13','CLOSED'),
        ('14','CLOSED'),
        ('15','CLOSED'),
        ('16','CLOSED'),
        ('16','CLOSED'),
        ('17','CLOSED'),
        ('12','CLOSED'),
        ('11','ACTIVE'),
        ('71','ACTIVE'),
        ('78','ACTIVE'),
        ('80','ACTIVE'),
        ('82','ACTIVE'),
        ('83','ACTIVE'),
        ('84','ACTIVE'),
        ('21','ACTIVE'),
        ('22','ACTIVE'),
        ('23','ACTIVE'),
        ('24','ACTIVE'),
        ('25','ACTIVE'),
        ('131','Restructured due to natural calamity'),
        ('130','Restructured due to COVID-19')], string="Account_Status")
    Date_Reported = fields.Char("Date_Reported")
    Open_Date = fields.Char("Open_Date")
    Highest_Credit_or_Original_Loan_Amount = fields.Char("Highest_Credit_or_Original_Loan_Amount")
    Current_Balance = fields.Char("Current_Balance")
    Amount_Past_Due = fields.Char("Amount_Past_Due")
    name = fields.Char("name")

    payment_hist = fields.Many2many("payment.history", string="payment history")

    addres_data = fields.Many2many("address.userlender", string="Address Details")



    Date_Closed = fields.Char("Date_Closed")
    Rate_of_Interest =fields.Char("Rate_of_Interest")
    Value_of_Collateral = fields.Char("Value_of_Collateral")
    Type_of_Collateral = fields.Char("Type_of_Collateral")
    SuitFiledWillfulDefaultWrittenOffStatus = fields.Char("SuitFiledWillfulDefaultWrittenOffStatus")
    Date_of_Last_Payment = fields.Char("Date_of_Last_Payment")
    SuitFiled_WilfulDefault = fields.Char("SuitFiled_WilfulDefault")
    Credit_Limit_Amount =fields.Char("Credit_Limit_Amount")
    Scheduled_Monthly_Payment_Amount = fields.Char("Scheduled_Monthly_Payment_Amount")
    Repayment_Tenure = fields.Char("Repayment_Tenure")
    Written_Off_Amt_Total = fields.Char("Written_Off_Amt_Total")
    Written_Off_Amt_Principal = fields.Char("Written_Off_Amt_Principal")
    Settlement_Amount = fields.Char("Settlement_Amount")
    Written_off_Settled_Status = fields.Selection([('00','Restructured Loan'),
            ('01','Restructured Loan(Govt. Mandated)'),
            ('02','Written-off'),
            ('03','Settled'),
            ('04','Post (WO) Settled'),
            ('05','Account Sold'),
            ('06','Written Off and Account Sold'),
            ('07','Account Purchased'),
            ('08','Account Purchased and Written Off'),
            ('09','Account Purchased and Settled'),
            ('10','Account Purchased and Restructured'),
            ('11','Restructured due to Natural Calamity'),
            ('12','Restructured due to COVID-19'),
            ('99','Clear Existing Status'),],string="Written_off_Settled_Status")
    Date_of_birth = fields.Char("Date_of_birth")
    Gender_Code = fields.Selection([('1','Male'),
        ('2','Female'),
        ('3','Transgender'),],string="Gender_Code")
    Occupation_Code = fields.Char("Occupation_Code")
    EMailId = fields.Char("EMailId")
    Telephone_Type = fields.Char("Telephone_Type")
    MobilePhoneNumber = fields.Char("MobilePhoneNumber")
    Telephone_Extension = fields.Char("Telephone_Extension")
    IncomeTaxPan=fields.Char("IncomeTaxPan")
    PAN_Issue_Date=fields.Char("PAN_Issue_Date")
    PAN_Expiration_Date=fields.Char("PAN_Expiration_Date")
    Passport_number = fields.Char("Passport_number")
    Passport_Issue_Date = fields.Char("Passport_Issue_Date")
    Passport_Expiration_Date = fields.Char("Passport_Expiration_Date")
    Voter_ID_Number = fields.Char("Voter_ID_Number")
    Voter_ID_Issue_Date = fields.Char("Voter_ID_Issue_Date")
    Voter_ID_Expiration_Date = fields.Char("Voter_ID_Expiration_Date")

    Universal_ID_Number = fields.Char("Universal_ID_Number")
    Universal_ID_Issue_Date = fields.Char("Universal_ID_Issue_Date")
    Universal_ID_Expiration_Date = fields.Char("Universal_ID_Expiration_Date")
    Driver_License_Number = fields.Char("Driver_License_Number")
    Driver_License_Issue_Date = fields.Char("Driver_License_Issue_Date")
    Driver_License_Expiration_Date = fields.Char("Driver_License_Expiration_Date")

    Ration_Card_Number = fields.Char("Ration_Card_Number")
    Ration_Card_Issue_Date = fields.Char("Ration_Card_Issue_Date")
    Ration_Card_Expiration_Date = fields.Char("Ration_Card_Expiration_Date")






class CreditEnquiry(models.Model):
    _name = "credit.enquiries"
    _description = "Credit Enquiries"

    First_Name = fields.Char("First_Name")
    Last_Name = fields.Char("Last_Name")
    Date_Of_Birth_Applicant = fields.Char("Date_Of_Birth_Applicant")
    IncomeTaxPan = fields.Char("IncomeTaxPan")
    ReportNumber = fields.Char("ReportNumber")
    Telephone_Number_Applicant_1st = fields.Char("Telephone_Number_Applicant_1st")
    Duration_Of_Agreement = fields.Char("Duration_Of_Agreement")
    Passport_number = fields.Char("Passport_number")
    Enquiry_Reason = fields.Selection([('1','Agriculture Loan'),
        ('2','Auto Loan'),
        ('3','Business Loan'),
        ('4','Commercial Vehicle Loans '),
        ('5','Construction Equipment loan'),
        ('6','Consumer Loan'),
        ('7','Credit Card'),
        ('8','Education Loan '),
        ('9','Leasing'),
        ('10','Loan against collateral'),
        ('11',' Microfinance '),
        ('12','Non-funded Credit Facility'),
        ('13','Personal Loan'),
        ('14','Property Loan'),
        ('15','Telecom'),
        ('16','Two/Three Wheeler Loan'),
        ('17','Working Capital Loan'),
        ('18','Consumer Loan'),
        ('19','Credit Review'),
        ('99','Others')], string="Enquiry_Reason")
    MobilePhoneNumber = fields.Char("MobilePhoneNumber")
    Voter_s_Identity_Card = fields.Char("Voter_s_Identity_Card")
    Subscriber_Name = fields.Char("Subscriber_Name")
    Gender_Code = fields.Selection([('1','Male'),
        ('2','Female'),
        ('3','Transgender'),],"Gender_Code")
    Driver_License_Number = fields.Char("Driver_License_Number")
    Date_of_Request = fields.Char("Date_of_Request")
    Marital_Status = fields.Selection([('1','Single'),
        ('2','Married'),
        ('3','Widow/Widower'),
        ('4','Divorced')],"Marital_Status")
    Ration_Card_Number = fields.Char("Ration_Card_Number")
    Amount_Financed = fields.Char("Amount_Financed")
    EMailId = fields.Char("EMailId")
    Duration_Of_Agreement = fields.Char("Duration_Of_Agreement")




class DailysaleReport(models.Model):
    _name = "daily.sale"
    _description = "Daily Sales"
    _rec_name = 'name_first'

    name_first= fields.Char("First Name")
    last_first= fields.Char("Last Name")
    date = fields.Date("Date")
    new_existing = fields.Selection([('new',"New"),
        ('existing',"Existing")])
    code_created = fields.Char("Code")
    pincode = fields.Char("Pincode")
    visiting_card = fields.Binary("Visiting Card Photo")
    photo_with_partner = fields.Binary("Photo with partner")
    deatils_of_discussion = fields.Text("Details of Discussion Doe")
    time_of_visit = fields.Date("Time of visit")
    file_picked_uo_date = fields.Char("File Picked Up")
    location = fields.Char("Location")
    email = fields.Char("Customer Email")
    phone = fields.Char("Customer Phone")

    # @api.model_create_multi
    # def create(self, vals_list):
    #     leads = super(DailysaleReport, self).create(vals_list)
    #     """ TO update login deatils """
    #     # vals = {}
    #     # url = 'http://ipinfo.io/json'
    #     # r = requests.get(url)
    #     # js = r.json()
    #     # city = js['city']
    #     # region = js['region']
    #     # country_code = js['country']
    #     # country_id = self.env['res.country'].search([
    #     #     ('code', '=', country_code)], limit=1)
    #     # for country in country_id:
    #     #     address = city + ', ' + region + ', ' + country.name
    #     #     leads.location = address
    #     return leads

    @api.onchange('name_first','last_first',"pincode")
    def _onchange_name(self):
        if self.name_first:
            bools = self.name_first.isalpha()
            if not bools:
                raise UserError(_('You are suppose to write only Alphabets in First Name'))

        if self.last_first:
            bools_last = self.last_first.isalpha()
            if not bools_last:
                raise UserError(_('You are suppose to write only Alphabets in Last Name'))

        if self.pincode:
            pincode = self.pincode.isnumeric()
            if not pincode or len(self.pincode) != 6:
                raise UserError(_('Kindly add the correct pincode!'))
            # if len(self.pincode) > 6:
            #     raise UserError(_('Kindly add the correct pincode!')) 

    def get_long_lat(self, lat, longs):
        geolocator = Nominatim(user_agent="capwise")
        location_code = str(lat) + "," + str(longs)
        location = geolocator.reverse(location_code)
        self.location = location.address


class FincialInstitutiononboard(models.Model):
    """ Model for case stages. This models the main stages of a document
        management flow. Main CRM objects (leads, opportunities, project
        issues, ...) will now use only stages, instead of state and stages.
        Stages are for example used to display the kanban view of records.
    """
    _name = "financial.institution.onboard"
    _description = "Financial Institution"
    _rec_name = 'vendor_name'

    # name = fields.Char("Bank Name", required=True)
    logo = fields.Binary("Logo")
    product_associate = fields.Many2one('product.template', string="Products")
    max_percentage = fields.Float("Percentage Allow")
    vendor_name = fields.Many2one("res.partner", string="Bank Name", required=True)
    # description = fields.Text("Description")
    location_pin_Code = fields.Many2many("location.pin", string="location (pin Code)")
    gst_number = fields.Char("Gst number")
    spock_name = fields.Char("Contact name")
    spock_number = fields.Char("Contact Number")
    spock_email = fields.Char("Contact Email")
    upload_signed_agreement_copy = fields.Binary("upload signed agreement copy")
    invoice_generation_date = fields.Date("Invoice Generation Date")
    product_percentage = fields.Many2many("product.percentage","fincial_institutions", string="Payout")
    # current_status_number = fields.Char("Current Status Number")
    addendum_signed = fields.Boolean("Addendum")
    Financial_email = fields.Char("Financial Email")


    def upload_all_slabs_and_pin(self):
        data_self = self.env['financial.institution.onboard'].search([])
        for data in data_self:
            data_slab = self.env['product.percentage'].search([("bank_name" ,'=',data.vendor_name.id),("product_ids",'=',data.product_associate.id)])
            data_pincode = self.env['location.pin'].search([("product_ids",'=',data.product_associate.id),("bank_name" ,'=',data.vendor_name.id)])
            data_slab_id = data_slab.mapped("id")
            data_pincode_id = data_pincode.mapped("id")
            _logger.info("pincode**************##################**%s" %data_pincode_id)
            data.update({
                # "product_percentage" : [(6, 0, data_slab_id)],
                "location_pin_Code" : [(6, 0, data_pincode_id)],
                })


    @api.model_create_multi
    def create(self, vals_list):
        leads = super(FincialInstitutiononboard, self).create(vals_list)
        user_ids = self.env['res.users'].browse(self.env.user.id)        
        if not user_ids.phone:
            raise UserError(_('Kindly contact your manager to upload your phone number'))
        headers = {
            "mobile": str(user_ids.phone),
            "password": "welcome1234"
        }
        response = requests.post("https://api.finbii.com/partners/login", json=headers)
        token = json.loads(response.content).get('token')
        print("token@@@@@@@@@@@@@@",token)
        location_data = ""
        # location_pin_Code = self.env['location.pin'].search([("product_ids","=",self.product_associate.id),("bank_name","=",self.id)])
        print("location_pin_Code@@@@@@@@@@@@@@@@@@",leads.location_pin_Code)
        location_data = leads.location_pin_Code.mapped("name")
        print("location_data@@@@@@@@@@@@@@@@@",location_data)
        lead_status = {
            "institution_name"  : leads.vendor_name.name,
            "institution_logo"  : leads.logo,
            "crm_institution_id" : leads.id,
            "product_associate" : leads.product_associate.id,
            "invoice_generation_date" : leads.invoice_generation_date.strftime("%Y-%m-%d"),
            "serviceable_pincode" : location_data
        }
        _logger.info("response.contentresponse.content****************%s" %response.content)
        response = requests.post("https://api.finbii.com/financial-institutions",headers={'Authorization': "Bearer %s" % token}, json=lead_status)
        print("response222222222222222222222222",response.content)
        _logger.info("response.contentresponse.content****************%s" %response.content)
        return leads

class LocationPinCode(models.Model):
    """ Model for case stages. This models the main stages of a document
        management flow. Main CRM objects (leads, opportunities, project
        issues, ...) will now use only stages, instead of state and stages.
        Stages are for example used to display the kanban view of records.
    """
    _name = "location.pin"
    _description = "Location Pin"
    _rec_name = 'name'

    name = fields.Char("Pincode", required=True)    
    fincial_institution = fields.Many2one("financial.institution.onboard", string="Financial Institution")
    bank_name = fields.Many2one("res.partner", string="Bank Name") 
    product_ids = fields.Many2one('product.template', string="Product Associated")

class FincialInstitution(models.Model):
    """ Model for case stages. This models the main stages of a document
        management flow. Main CRM objects (leads, opportunities, project
        issues, ...) will now use only stages, instead of state and stages.
        Stages are for example used to display the kanban view of records.
    """
    _name = "financial.institution"
    _description = "Financial Institution"
    _rec_name = 'name'

    name = fields.Char("Bank Name", required=True)
    product_associate = fields.Many2many('product.template', string="Products")
    max_percentage = fields.Float("Percentage Allow")
    

    @api.model_create_multi
    def create(self, vals_list):
        leads = super(FincialInstitution, self).create(vals_list)
        user_ids = self.env['res.users'].browse(self.env.user.id)
        # if not user_ids.phone:
        #     raise UserError(_('Kindly contact your manager to upload your phone number'))
        # headers = {
        #     "mobile": str(user_ids.phone),
        #     "password": "welcome1234"
        # }
        # response = requests.post("https://api.finbii.com/partners/login", json=headers)
        # token = json.loads(response.content).get('token')

        # fI = {
        #     "institution_name"  : leads.name,
        #     "institution_logo"  : leads.logo,
        #     "crm_institution_id" : leads.id,
        #     "institution_product_associate" : leads.product_associate,
        #     "institution_max_percentage" : leads.max_percentage,
        #     "institution_vendor_name" : leads.vendor_name,
        #     "institution_description" : leads.description,
        #     "institution_location_pin_Code" : leads.location_pin_Code,
        #     "institution_gst_number" : leads.gst_number,
        #     "institution_spock_name" : leads.spock_name,
        #     "institution_spock_number" : leads.spock_number,
        #     "institution_spock_email" : leads.spock_email,
        #     "institution_upload_signed_agreement_copy" : leads.upload_signed_agreement_copy,
        #     "institution_invoice_generation_date" : leads.invoice_generation_date,
        # }
        # response = requests.post("https://api.finbii.com/financial-institutions",headers={'Authorization': "Bearer %s" % token}, json=fI)
        return leads


class ProductPayout(models.Model):
    """ Model for case stages. This models the main stages of a document
        management flow. Main CRM objects (leads, opportunities, project
        issues, ...) will now use only stages, instead of state and stages.
        Stages are for example used to display the kanban view of records.
    """
    _inherit = "product.template"

    @api.model_create_multi
    def create(self, vals_list):
        leads = super(ProductPayout, self).create(vals_list)
        user_ids = self.env['res.users'].browse(self.env.user.id)
        if not user_ids.phone:
            raise UserError(_('Kindly contact your manager to upload your phone number'))
        headers = {
            "mobile": str(user_ids.phone),
            "password": "welcome1234"
        }
        response = requests.post("https://api.finbii.com/partners/login", json=headers)
        token = json.loads(response.content).get('token')


        fI = {
            "product_name": leads.name,
            "product_code": leads.default_code,
            "crm_product_id" : leads.id
        }
        response = requests.post("https://api.finbii.com/crms/product", headers={'Authorization': "Bearer %s" % token}, json=fI)
        return leads


class CapwiseLoan(models.Model):
    _name = 'capwise_loan.capwise_loan'
    _description = 'capwise_loan.capwise_loan'
    _rec_name = "name"

    sequence = fields.Integer(default=1, string="S. No", help="Used to order stages. Lower is better.", readonly="1")
    fincial_institution = fields.Many2one("financial.institution",string="Financial Institution")
    fincial_institutions = fields.Many2one("financial.institution.onboard",string="Financial Institution")
    product_ids = fields.Many2one("product.template", string="Product")
    crm_lead_data = fields.Many2one("crm.lead", string="Crm Lead")
    payout_percentage = fields.Float(string="Payout Percentage")    
    channel_category = fields.Selection([('bronze',"Bronze"),
        ('silver',"Silver"),
        ('gold',"Gold"),
        ('platinum',"Platinum")])  
    name = fields.Char("name" , readonly="1")

    @api.onchange("fincial_institutions",'product_ids',"payout_percentage")
    def _onchange_product_ids(self):
        # fi_data = self.env['product.percentage'].search([('fincial_institution','=',self.fincial_institutions.id)])
        self.product_ids = self.fincial_institutions.product_associate.id
        # _logger.info("prod_dataprod_dataprod_data****************%s" %fi_data)
        if self.fincial_institutions:
            _logger.info("prod_dataprod_dataprod_data****************%s" %self.fincial_institutions)
            for max_payout in self.fincial_institutions.product_percentage:
                _logger.info("prod_dataprod_dataprod_data*###########**%s" %max_payout.dsa_payout)
                if max_payout.dsa_payout == True:
                    max_data = max_payout.percentage * int(max_payout.percentage_allow) / 100
                    _logger.info("max_datamax_datamax_datamax_data*###########**%s" %max_data)
                    if max_data and max_payout.percentage_allow and self.payout_percentage:
                        _logger.info("self.payout_percentageself.payout_percentage*###########**%s" %self.payout_percentage)
                        if self.payout_percentage > max_data:
                            raise UserError(_('You are not allowed to add payout Percentage more than %s !' % max_data))
            
        # prod_data = self.env['product.percentage'].search([("dsa_payout","=",True),("product_ids",'=',self.product_ids.id),('bank_name','=',self.fincial_institutions.vendor_name.id)], limit=1)
        # max_payout = prod_data.percentage * int(prod_data.percentage_allow) / 100
        # if prod_data and prod_data.percentage_allow and self.payout_percentage:
        #     if self.payout_percentage > max_payout:
        #         raise UserError(_('You are not allowed to add payout Percentage more than %s !' % max_payout))
        # unique_list = [] 
        # # traverse for all elements
        # for x in fi_data.product_ids.mapped("id"):
        #     # check if exists in unique_list or not
        #     if x not in unique_list:
        #         unique_list.append(x)
        # res = {
        # 'domain': {
        # 'product_ids': [('id', 'in', unique_list)]
        # }
        # }
        # return res


    @api.model_create_multi
    def create(self, vals_list):
        leads = super(CapwiseLoan, self).create(vals_list)
        user_ids = self.env['res.users'].browse(self.env.user.id)
        if not user_ids.phone:
            raise UserError(_('Kindly contact your manager to upload your phone number'))
        if not leads.crm_lead_data.phone:
            raise UserError(_('Kindly add the phone number'))    
        headers = {
            "mobile": str(user_ids.phone),
            "password": "welcome1234"
        }
        response = requests.post("https://api.finbii.com/partners/login", json=headers)
        token = json.loads(response.content).get('token')
        for leass in leads:
            payout_data = {
                "payout_percent" : str(leass.payout_percentage),
                "payout_name" : str(leass.name),
                "crm_payout_id" : leass.id,
                "crm_product_id" : leass.product_ids.id,
                "crm_institution_id" : leass.fincial_institutions.id,
                "mobile" : leass.crm_lead_data.phone
            }
            response = requests.post("https://api.finbii.com/crms/payout",headers={'Authorization': "Bearer %s" % token}, json=payout_data)
            _logger.info("responseresponse**************##################**%s" %response.content)
        return leads   



    @api.onchange('product_ids', 'payout_percentage')
    def _onchange_payout(self):
        if self.product_ids and self.payout_percentage:
            self.name = self.product_ids.name + " - " + str(self.payout_percentage) + "%"


class ResPartnerData(models.Model):
    _inherit = 'res.partner'
    
    lead_id = fields.Char("Lead ID")
    sale_ceo = fields.Boolean("Ceo")
    sale_business_head = fields.Boolean("Business Head")
    sale_regional_head = fields.Boolean("Regional Head")
    sale_area_head = fields.Boolean("Area Head")
    sale_channel_sales_manager = fields.Boolean("Channel Sales Manager")
    sale_call_centre = fields.Boolean("Call Centre")
    sale_operations = fields.Boolean("Operations")            
    
class OperationsLoan(models.Model):
    _name = 'operations.stage'
    _description = 'Operations'
    _rec_name = "name"

    sequence = fields.Integer(default=1, string="S. No", help="Used to order stages. Lower is better.")
    name = fields.Char("name")
    code = fields.Char("Code")
    partner_check = fields.Boolean("Partner Check")
    operation_check = fields.Boolean("Operation Check")


class OperationsProductPercent(models.Model):
    _name = 'product.percentage'
    _description = 'Products and Percentage'
    _rec_name = "product_ids"

    sequence = fields.Integer(default=1, string="S. No", help="Used to order stages. Lower is better.")
    product_ids = fields.Many2one("product.template")
    slabs = fields.Float("Slab From")
    slabs_to = fields.Float("Slab To")
    percentage = fields.Float("Payout Percentage")
    fincial_institution = fields.Many2one("financial.institution.onboard" , string="Financial Institution")
    dsa_payout = fields.Boolean("Dsa Payout")
    percentage_allow = fields.Selection([
        ('10', '10%'), 
        ('20', '20%'),
        ('30', '30%'), 
        ('40', '40%'),
        ('50', '50%'), 
        ('60', '60%'),
        ('70', '70%'), 
        ('80', '80%'),
        ('90', '90%'), 
        ('100', '100%')
        ], string="Dsa Allow Percentage") 
    bank_name = fields.Many2one("res.partner", string="Bank Name") 


class capwise_crm(models.Model):
    _inherit = "crm.lead"


    name = fields.Char(
        "Channel Lead", index=True, required=True,
        compute='_compute_name', readonly=False, store=True)
    operations_test = fields.Many2many("operations.stage", string="Partner Check")
    operations_status = fields.Selection([
        ('pending', 'Pending'), ('approve', 'Approve'),('decline', 'Decline'), ('hold', 'Hold')], string="Operation Status")

    gender = fields.Selection([
        ('male', 'Male'), ('female', 'Female')])

    onboard_date = fields.Date("On-Boarded Date", readonly=True)

    bank_account_holder_name = fields.Char("Bank Account Holder Name")
    bank_account_number = fields.Char("Bank Account Number")
    bank_name = fields.Char("Bank Name")
    ifsc_code = fields.Char("IFSC Code")

    visited_date = fields.Date(string="Visit Date")
    product_ids = fields.Many2many('product.template', 'sale_template_partner_rel', string='Products')
    payout_ids = fields.Many2many('capwise_loan.capwise_loan', 'capwise_loan_partner_rel', string='Payout')

    address_house = fields.Char("House")
    address_area = fields.Char("Area")
    address_pincode = fields.Char("Pincode")
    address_city = fields.Char("City")
    address_state = fields.Char("State")
    address_country = fields.Char("Country")
    document_type = fields.Char("Document Type Id")
    document_proof = fields.Binary('Document Card', help="Display the pan card.")

    document_proof_pdf = fields.Binary('Document Card', help="Display the pan card.")

    partner_personal_occupation = fields.Char(string="Occupation")
    partner_type_of_firm = fields.Char(string="Type Of Firm*")
    partner_gst_no = fields.Char(string="GST Number")
    partner_business_name = fields.Char(string="Business Name")
    partner_product_associated = fields.Char(string="Product Associated With")

    partner_pan_card_proof = fields.Binary('Pan Card', help="Display the pan card.")
    partner_pan_card_proof_pdf = fields.Binary('Pan Card', help="Display the pan card.")
    partner_aadhar_card_proof_front = fields.Binary('Adhar Card Proof Front', help="Display the front side of adhar card.")
    partner_aadhar_card_proof_front_pdf = fields.Binary('Adhar Card Proof Front', help="Display the front side of adhar card.")
    partner_aadhar_card_proof_back = fields.Binary('Adhar Card Proof Back', help="Display the back side of adhar card")
    partner_aadhar_card_proof_back_pdf = fields.Binary('Adhar Card Proof Back', help="Display the back side of adhar card")
    partner_document_type = fields.Char("Document Type")
    partner_pan_no = fields.Char("Pan Card Number")
    # partner_is_pancard = fields.Boolean("Is Pancard")
    partner_adhaar_no = fields.Char("Adharcard Number")
    partner_dob = fields.Date(string="D.O.B")
    partner_upload_photo = fields.Binary('Photo', help="Display the photo of the client")
    partner_upload_photo_pdf = fields.Binary('Photo', help="Display the photo of the client")
    otp_send = fields.Boolean("otp send")
    otp = fields.Char("OTP")
    session_id = fields.Char("Session Id")

    @api.onchange('phone')
    def _onchange_phone_validation_check(self):
        if self.phone:
            phone_check = self.env['crm.lead'].search([])
            for phn in phone_check:
                if phn.phone == self.phone: 
                    raise UserError(_('This Phone number is already exist, kindly add a new phone number to proceed!'))


    # @api.model_create_multi
    # def create(self, vals_list):
    #     leads = super(capwise_crm, self).create(vals_list)
    #     user_ids = self.env['res.users'].browse(self.env.user.id)
    #     if not user_ids.phone:
    #         raise UserError(_('Kindly contact your manager to upload your phone number'))
    #     headers = {
    #         "name": leads.partner_id.name,
    #         "mobile": leads.phone
    #     }
    #     response = requests.post("https://api.uat.finbii.com/partners/register", json=headers)
    #     session_id = json.loads(response.content).get("session_id")
    #     leads.session_id = session_id
    #     if 'error' in json.loads(response.content):
    #         raise UserError(_('This Phone number is already exist!'))
    #     return leads 

    def action_hot(self):
        self.stage_id = 2

    def action_cold(self):
        self.stage_id = 3    

    def action_send_otp(self):
        if not self.otp:
            raise UserError(_('Kindly add the OTP to veryfy!'))
        phone_data = {
            "session_id" : self.session_id,
            "otp" : self.otp
        }
        response_data = requests.post("https://api.finbii.com/partners/verify-otp", json=phone_data)
        # partner_code = json.loads(response.content).get("personalInfo").get("partner_code")
        return True

    def send_mis_report(self):
        filename = 'MIS_Report.xls'
        string = 'MIS_Report.xls'
        wb = xlwt.Workbook(encoding='utf-8')
        worksheet = wb.add_sheet(string)
        header_bold = xlwt.easyxf("font: bold on; pattern: pattern solid, fore_colour gray25;")
        cell_format = xlwt.easyxf()
        filename = 'MIS_Report_%s.xls' % date.today()
        rested = self.env['crm.lead'].search([])
        row = 1
        worksheet.write(0, 0, 'Channel Lead', header_bold)
        worksheet.write(0, 1, 'Email', header_bold)
        worksheet.write(0, 2, 'Phone', header_bold)
        worksheet.write(0, 3, 'Gender', header_bold)
        worksheet.write(0, 4, 'Salesperson', header_bold)
        worksheet.write(0, 5, 'Sales Team', header_bold)
        worksheet.write(0, 6, 'Next Activity', header_bold)
        worksheet.write(0, 7, 'Stage', header_bold)
        worksheet.write(0, 8, 'Source', header_bold)
        worksheet.write(0, 9, 'Visited Date', header_bold)
        worksheet.write(0, 10, 'Created Date', header_bold)
        for material_line_id in rested.filtered(lambda v: v.create_date.date() == date.today()):
            worksheet.write(row, 0, material_line_id.name or '')
            worksheet.write(row, 1, material_line_id.email_from or '')
            worksheet.write(row, 2, material_line_id.phone or '')
            worksheet.write(row, 3, material_line_id.gender or '')
            worksheet.write(row, 4, material_line_id.user_id.name or '')
            worksheet.write(row, 5, material_line_id.team_id.name or '')
            worksheet.write(row, 6, material_line_id.activity_ids or '')
            worksheet.write(row, 7, material_line_id.stage_id.name or '')
            worksheet.write(row, 8, material_line_id.source_id.name or '')
            worksheet.write(row, 9, str(material_line_id.visited_date) or '')
            worksheet.write(row, 10, str(material_line_id.create_date) or '')
            row += 1
        fp = io.BytesIO()
        wb.save(fp)
        out = base64.encodebytes(fp.getvalue())
        ir_mail_server = self.env['ir.mail_server']
        mail_server_ids = ir_mail_server.sudo().search([], order='sequence', limit=1)
        if mail_server_ids:
            mail = ir_mail_server.browse(mail_server_ids[0]).id
            attachment = {
                           'name': str(filename),
                           'display_name': str(filename),
                           'datas': out,
                           'type': 'binary'
                       }
            ir_id = self.env['ir.attachment'].create(attachment)
            attachments = [(a['display_name'], base64.b64decode(a['datas']), a['mimetype'])
                           for a in ir_id.sudo().read(['display_name', 'datas', 'mimetype'])]
            if mail and mail.smtp_user:
                email_body = "<html><body><p>Hello, </p><p></p><p>Dear Sir/Madam,</p><p>This is an automatic mail For the DSA leads added today in the CRM. <br/>Kindly check the attached file.<b></b></p><p>Thank You</p><p>Finbii Team</p></body></html>"
                text = html2text.html2text(email_body)
                msg = ir_mail_server.build_email(
                                email_from=mail.smtp_user,
                                email_to=['aashish.dhiimaan@finbii.com'],
                                subject='DSA Lead created in the CRM',
                                body=text,
                                attachments=attachments,
                                )
                message = ir_mail_server.send_email(msg, mail_server_id=mail.id)    


    def action_pending(self):
        self.operations_status = 'pending'

    def action_hold(self):   
        print("self######################",self.operations_status)
        self.operations_status = 'hold'    


    def action_approve(self):
        self.operations_status = 'approve'
        # self.stages = 'payment_done'
        # self.hold = False
        # self.payment_done = True
        # self.payment_status_line.create({
        #         'remark_date': datetime.now(),
        #         'status': "Approved",
        #         'reason': "",
        #         'lead_id': self.id,
        #     })
        # ctx = dict(self.env.context or {})
        # template_id = self.env.ref('capwise_crm.send_invoice_to_customer')
        # mail_id = template_id.with_context(
        #             ctx).send_mail(self.id, force_send=True)
        # print("mail_id@@@@@@@@@@@@@@@@@@@",mail_id)
        
    def action_decline(self):
        self.operations_status = 'decline'
    

        


    @api.depends('partner_id')
    def _compute_name(self):
        for lead in self:
            if not lead.name and lead.partner_id and lead.partner_id.name:
                lead.name = _("%s's Channel Lead") % lead.partner_id.name

class MultipleLender(models.Model):
    _name = "multiple.lender"    
    _description = "Multiple Lender"      

    Bank_FI = fields.Many2one("financial.institution.onboard", string="Bank/FI")
    loan_lead = fields.Many2one("capwise.lead", string="Loan")
    state_id = fields.Selection([('lead_complete','Lead Complete'),
        ('lead_incomplete','Lead Incomplete'),
        ('disbursed','Disbursed'),
        ('login_with_fi','Login with FI'),
        ('Rejected','Rejected'),
        ('sanctioned','Sanctioned'),
        ('wip','WIP')
        ],string="Status")
    login_date = fields.Datetime("Login Date")
    login_amount = fields.Float("Login Amount")
    sanction_date = fields.Date("Sanction Date")
    sanction_amount = fields.Float("Sanction Amount")
    disb_Date = fields.Date("Disbursed Date")
    dis_amount = fields.Float("Disbursed Amount")



class CrmCustomer(models.Model):
    _name = "capwise.lead"
    _description = "Loan"
    _order = "id desc"
    _inherit = ['mail.thread.cc',
                'mail.thread.blacklist',
                'mail.activity.mixin',
                'utm.mixin',
                'format.address.mixin',
               ]
    _primary_email = 'email_from'
    _check_company_auto = True


    finance_for_bre = fields.Many2many('financial.finbii',"loan_type", string="BRE Financial")

    multiple_lender = fields.Many2many("multiple.lender","loan_lead" ,string="Multiple Lender")

    pan_card_verify = fields.Boolean("pan card is not verified")
    aadhar_card_verify = fields.Boolean("aadhar card is not verified")
    Date_Of_Birth_verify = fields.Boolean("Date Of Birth is not verified")
    mobile_phone_verify = fields.Boolean("mobile phone is not verified")
    email_verify = fields.Boolean("email is not verified")
    dps_one = fields.Boolean("DPD one")
    dps_two = fields.Boolean("DPD two")
    dps_three = fields.Boolean("DPD three")
    dps_four = fields.Boolean("DPD four")
    emi_total_emi = fields.Float("Total_emi")
    total_amount_overdue = fields.Float("total amount overdue")
    total_settlement_amount = fields.Float("total settlement amount")



    # name_file = fields.Char(string='Name', size=64)

    # gentextfile = fields.Binary('Click On Save As Button To Download File', readonly=True)

    credit_score = fields.Html("Credit Score Analysis")
    pdf_credit_score = fields.Binary("Credit Score")


    first_name = fields.Char("First_Name")
    Last_Name = fields.Char("Last_Name")
    SystemCode = fields.Char("SystemCode")
    MessageText = fields.Char("MessageText")
    ReportDate = fields.Char("ReportDate")
    ReportTime = fields.Char("ReportTime")
    UserMessageText = fields.Char("UserMessageText")
    Version = fields.Char("Version")
    Enquiry_Username = fields.Char("Enquiry_Username")
    ReportNumber = fields.Char("ReportNumber")
    Subscriber_Name = fields.Char("Subscriber_Name")
    Enquiry_Reason = fields.Char("Enquiry_Reason")
    Finance_Purpose = fields.Char("Finance_Purpose")
    Amount_Financed = fields.Char("Amount_Financed")
    Duration_Of_Agreement = fields.Char("Duration_Of_Agreement")
    Middle_Name1 = fields.Char("Middle_Name1")
    Middle_Name2 = fields.Char("Middle_Name2")
    Middle_Name3 = fields.Char("Middle_Name3")
    Gender_Code = fields.Selection([('1','Male'),
        ('2','Female'),
        ('3','Transgender'),],string="Gender_Code")
    IncomeTaxPan = fields.Char("IncomeTaxPan")
    PAN_Issue_Date = fields.Char("PAN_Issue_Date")
    PAN_Expiration_Date = fields.Char("PAN_Expiration_Date")
    Passport_number = fields.Char("Passport_number")
    Passport_Issue_Date = fields.Char("Passport_Issue_Date")
    Passport_Expiration_Date = fields.Char("Passport_Expiration_Date")
    Voter_s_Identity_Card = fields.Char("Voter_s_Identity_Card")
    Voter_ID_Issue_Date = fields.Char("Voter_ID_Issue_Date")
    Voter_ID_Expiration_Date = fields.Char("Voter_ID_Expiration_Date")
    Driver_License_Number = fields.Char("Driver_License_Number")
    Driver_License_Issue_Date = fields.Char("Driver_License_Issue_Date")
    Driver_License_Expiration_Date = fields.Char("Driver_License_Expiration_Date")
    Ration_Card_Number = fields.Char("Ration_Card_Number")
    Ration_Card_Issue_Date = fields.Char("Ration_Card_Issue_Date")
    Ration_Card_Expiration_Date = fields.Char("Ration_Card_Expiration_Date")
    Universal_ID_Number = fields.Char("Universal_ID_Number")
    Universal_ID_Issue_Date = fields.Char("Universal_ID_Issue_Date")
    Universal_ID_Expiration_Date = fields.Char("Universal_ID_Expiration_Date")
    Date_Of_Birth_Applicant = fields.Char("Date_Of_Birth_Applicant")
    Telephone_Number_Applicant_1st = fields.Char("Telephone_Number_Applicant_1st")
    Telephone_Extension = fields.Char("Telephone_Extension")
    Telephone_Type = fields.Char("Telephone_Type")
    MobilePhoneNumber = fields.Char("MobilePhoneNumber")
    EMailId = fields.Char("EMailId")
    Income = fields.Char("Income")
    Marital_Status = fields.Char("Marital_Status")
    Employment_Status = fields.Char("Employment_Status")
    Time_with_Employer = fields.Char("Time_with_Employer")
    Number_of_Major_Credit_Card_Held = fields.Char("Number_of_Major_Credit_Card_Held")
    FlatNoPlotNoHouseNo = fields.Char("FlatNoPlotNoHouseNo")
    BldgNoSocietyName = fields.Char("BldgNoSocietyName")
    RoadNoNameAreaLocality = fields.Char("RoadNoNameAreaLocality")
    City = fields.Char("City")
    Landmark = fields.Char("Landmark")
    State = fields.Char("State")
    PINCode = fields.Char("PINCode")
    Country_Code = fields.Char("Country_Code")
    Current_Application_Details = fields.Char("Current_Application_Details")
    CADSuitFiledCurrentBalance = fields.Char("CADSuitFiledCurrentBalance")
    CreditAccountActive = fields.Char("CreditAccountActive")
    CreditAccountClosed = fields.Char("CreditAccountClosed")
    CreditAccountDefault = fields.Char("CreditAccountDefault")
    CreditAccountTotal = fields.Char("CreditAccountTotal")
    Outstanding_Balance_Secured = fields.Char("Outstanding_Balance_Secured")
    Outstanding_Balance_Secured_Percentage = fields.Char("Outstanding_Balance_Secured_Percentage")
    Outstanding_Balance_UnSecured = fields.Char("Outstanding_Balance_UnSecured")
    Outstanding_Balance_UnSecured_Percentage = fields.Char("Outstanding_Balance_UnSecured_Percentage")
    Outstanding_Balance_All = fields.Char("Outstanding_Balance_All")
    Identification_Number = fields.Char("Identification_Number")
    Subscriber_Name = fields.Char("Subscriber_Name")
    Account_Number = fields.Char("Account_Number")
    Portfolio_Type = fields.Char("Portfolio_Type")
    Account_Type = fields.Char("Account_Type")
    Open_Date = fields.Char("Open_Date")
    Credit_Limit_Amount = fields.Char("Credit_Limit_Amount")
    Highest_Credit_or_Original_Loan_Amount = fields.Char("Highest_Credit_or_Original_Loan_Amount")
    Terms_Duration = fields.Char("Terms_Duration")
    Terms_Frequency = fields.Char("Terms_Frequency")
    Scheduled_Monthly_Payment_Amount = fields.Char("Scheduled_Monthly_Payment_Amount")
    Account_Status = fields.Selection([('00','No Suit Filed'),
        ('89','Wilful default'),
        ('93','Suit Filed(Wilful default)'),
        ('97','Suit Filed(Wilful Default) and Written-off'),
        ('30','Restructure'),
        ('31','Restructured Loan (Govt. Mandated)'),
        ('32','Settled'),
        ('33','Post (WO) Settled '),
        ('34','Account Sold'),
        ('35','Written Off and Account Sold '),
        ('36','Account Purchased'),
        ('37','Account Purchased and Written Off'),
        ('38','Account Purchased and Settled'),
        ('39','Account Purchased and Restructured'),
        ('40','Status Cleared'),
        ('41','Restructured Loan'),
        ('42','Restructured Loan (Govt. Mandated)'),
        ('43','Written-off'),
        ('44','Settled'),
        ('45','Post (WO) Settled'),
        ('46','Account Sold'),
        ('47','Written Off and Account Sold'),
        ('48','Account Purchased'),
        ('49','Account Purchased and Written Off'),
        ('50','Account Purchased and Settled'),
        ('51','Account Purchased and Restructured'),
        ('52','Status Cleared'),
        ('53','Suit Filed'),
        ('54','Suit Filed and Written-off'),
        ('55','Suit Filed and Settled'),
        ('56','Suit Filed and Post (WO) Settled'),
        ('57','Suit Filed and Account Sold'),
        ('58','Suit Filed and Written Off and Account Sold'),
        ('59','Suit Filed and Account Purchased'),
        ('60','Suit Filed and Account Purchased and Written Off'),
        ('61','Suit Filed and Account Purchased and Settle'),
        ('62','Suit Filed and Account Purchased and Restructured'),
        ('63','Suit Filed and Status Cleared'),
        ('64','Wilful Default and Restructured Loan'),
        ('65','Wilful Default and Restructured Loan (Govt. Mandated)'),
        ('66','Wilful Default and Settled'),
        ('67','Wilful Default and Post (WO) Settled'),
        ('68','Wilful Default and Account Sold'),
        ('69','Wilful Default and Written Off and Account Sold'),
        ('70','Wilful Default and Account Purchased'),
        ('72','Wilful Default and Account Purchased and Written Off'),
        ('73','Wilful Default and Account Purchased and Settled'),
        ('74','Wilful Default and Account Purchased and Restructured'),
        ('75','Wilful Default and Status Cleared'),
        ('76','Suit filed (Wilful default) and Restructured'),
        ('77','Suit filed (Wilful default) and Restructured Loan (Govt. Mandated)'),
        ('79','Suit filed (Wilful default) and Settled'),
        ('85','Suit filed (Wilful default) and Account Sold'),
        ('81','Suit filed (Wilful default) and Post (WO) Settled'),
        ('86','Suit filed (Wilful default) and Written Off and Account Sold'),
        ('87','Suit filed (Wilful default) and Account Purchased'),
        ('88','Suit filed (Wilful default) and Account Purchased and Written Off'),
        ('94','Suit filed (Wilful default) and Account Purchased and Settled'),
        ('90','Suit filed (Wilful default) and Account Purchased and Restructured'),
        ('91','Suit filed (Wilful default) and Status Cleared'),
        ('13','CLOSED'),
        ('14','CLOSED'),
        ('15','CLOSED'),
        ('16','CLOSED'),
        ('16','CLOSED'),
        ('17','CLOSED'),
        ('12','CLOSED'),
        ('11','ACTIVE'),
        ('71','ACTIVE'),
        ('78','ACTIVE'),
        ('80','ACTIVE'),
        ('82','ACTIVE'),
        ('83','ACTIVE'),
        ('84','ACTIVE'),
        ('21','ACTIVE'),
        ('22','ACTIVE'),
        ('23','ACTIVE'),
        ('24','ACTIVE'),
        ('25','ACTIVE'),
        ('131','Restructured due to natural calamity'),
        ('130','Restructured due to COVID-19')], string="Account_Status")
    Payment_Rating = fields.Char("Payment_Rating")
    Payment_History_Profile = fields.Char("Payment_History_Profile")
    Special_Comment = fields.Char("Special_Comment")
    Current_Balance = fields.Char("Current_Balance")
    Amount_Past_Due = fields.Char("Amount_Past_Due")
    Original_Charge_Off_Amount = fields.Char("Original_Charge_Off_Amount")
    Date_Reported = fields.Char("Date_Reported")
    Date_of_First_Delinquency = fields.Char("Date_of_First_Delinquency")
    Date_Closed = fields.Char("Date_Closed")
    Date_of_Last_Payment = fields.Char("Date_of_Last_Payment")
    SuitFiledWillfulDefaultWrittenOffStatus = fields.Char("SuitFiledWillfulDefaultWrittenOffStatus")
    SuitFiled_WilfulDefault = fields.Char("SuitFiled_WilfulDefault")
    Written_off_Settled_Status = fields.Char("Written_off_Settled_Status")
    Value_of_Credits_Last_Month = fields.Char("Value_of_Credits_Last_Month")
    Occupation_Code = fields.Char("Occupation_Code")
    Settlement_Amount = fields.Char("Settlement_Amount")
    Value_of_Collateral = fields.Char("Value_of_Collateral")
    Type_of_Collateral = fields.Char("Type_of_Collateral")
    Written_Off_Amt_Total = fields.Char("Written_Off_Amt_Total")
    Written_Off_Amt_Principal = fields.Char("Written_Off_Amt_Principal")
    Rate_of_Interest = fields.Char("Rate_of_Interest")
    Repayment_Tenure = fields.Char("Repayment_Tenure")
    Promotional_Rate_Flag = fields.Char("Promotional_Rate_Flag")
    Income_Indicator = fields.Char("Income_Indicator")
    Income_Frequency_Indicator = fields.Char("Income_Frequency_Indicator")
    DefaultStatusDate = fields.Char("DefaultStatusDate")
    LitigationStatusDate = fields.Char("LitigationStatusDate")
    WriteOffStatusDate = fields.Char("WriteOffStatusDate")
    DateOfAddition = fields.Char("DateOfAddition")
    CurrencyCode = fields.Char("CurrencyCode")
    Subscriber_comments = fields.Char("Subscriber_comments")
    Consumer_comments = fields.Char("Consumer_comments")
    AccountHoldertypeCode = fields.Char("AccountHoldertypeCode")
    Year = fields.Char("Year")
    Month = fields.Char("Month")
    Days_Past_Due = fields.Char("Days_Past_Due")
    Surname_Non_Normalized = fields.Char("Surname_Non_Normalized")
    First_Name_Non_Normalized = fields.Char("First_Name_Non_Normalized")
    Middle_Name_1_Non_Normalized = fields.Char("Middle_Name_1_Non_Normalized")
    Middle_Name_2_Non_Normalized = fields.Char("Middle_Name_2_Non_Normalized")
    Middle_Name_3_Non_Normalized = fields.Char("Middle_Name_3_Non_Normalized")
    Alias = fields.Char("Alias")
    Income_TAX_PAN = fields.Char("Income_TAX_PAN")
    Passport_Number = fields.Char("Passport_Number")
    Voter_ID_Number = fields.Char("Voter_ID_Number")
    Date_of_birth = fields.Char("Date_of_birth")
    First_Line_Of_Address_non_normalized = fields.Char("First_Line_Of_Address_non_normalized")
    Second_Line_Of_Address_non_normalized = fields.Char("Second_Line_Of_Address_non_normalized")
    Third_Line_Of_Address_non_normalized = fields.Char("Third_Line_Of_Address_non_normalized")
    City_non_normalized = fields.Char("City_non_normalized")
    Fifth_Line_Of_Address_non_normalized = fields.Char("Fifth_Line_Of_Address_non_normalized")
    State_non_normalized = fields.Char("State_non_normalized")
    ZIP_Postal_Code_non_normalized = fields.Char("ZIP_Postal_Code_non_normalized")
    CountryCode_non_normalized = fields.Char("CountryCode_non_normalized")
    Address_indicator_non_normalized = fields.Char("Address_indicator_non_normalized")
    Residence_code_non_normalized = fields.Char("Residence_code_non_normalized")
    Telephone_Number = fields.Char("Telephone_Number")
    Telephone_Type = fields.Char("Telephone_Type")
    Telephone_Extension = fields.Char("Telephone_Extension")
    Mobile_Number = fields.Char("Mobile_Number")
    FaxNumber = fields.Char("FaxNumber")
    Exact_match = fields.Char("Exact_match")
    Date_of_Request = fields.Char("Date_of_Request")
    TotalCAPSLast7Days = fields.Char("TotalCAPSLast7Days")
    TotalCAPSLast30Days = fields.Char("TotalCAPSLast30Days")
    TotalCAPSLast90Days = fields.Char("TotalCAPSLast90Days")
    TotalCAPSLast180Days = fields.Char("TotalCAPSLast180Days")
    CAPSLast7Days = fields.Char("CAPSLast7Days")
    CAPSLast30Days = fields.Char("CAPSLast30Days")
    CAPSLast90Days = fields.Char("CAPSLast90Days")
    CAPSLast180Days = fields.Char("CAPSLast180Days")
    NonCreditCAPSLast7Days = fields.Char("NonCreditCAPSLast7Days")
    NonCreditCAPSLast30Days = fields.Char("NonCreditCAPSLast30Days")
    NonCreditCAPSLast90Days = fields.Char("NonCreditCAPSLast90Days")
    NonCreditCAPSLast180Days = fields.Char("NonCreditCAPSLast180Days")
    BureauScore = fields.Char("BureauScore")
    CAIS_Account_History = fields.Char("CAIS_Account_History")
    CAIS_Holder_Phone_Details = fields.Char("CAIS_Holder_Phone_Details")
    CAIS_Holder_Address_Details = fields.Char("CAIS_Holder_Address_Details")
    BureauScoreConfidLevel = fields.Char("BureauScoreConfidLevel")
    BureauPLcore = fields.Char("BureauPLcore")
    LeverageScore = fields.Char("LeverageScore")
    NoHitScore = fields.Char("NoHitScore")
    bsa_attachment = fields.Many2many(
        'ir.attachment', 'dosument_upload_attachments_rel',
        string='BSA')
    bsa_end_time = fields.Datetime(string='Timestamp')

    login_date = fields.Datetime("Login Date")

    lead_id = fields.Char("Lead ID")
    operations_test = fields.Many2many("operations.stage", string="operations Check")
    constitution = fields.Char("Constitution")


    lenders_data = fields.Many2many("business_rules.business_rules" , string="Lender Data")
    

    banking_upload_passbook = fields.Char("Banking Upload's") 
    banking_upload_passbook_pdf = fields.Char("Banking Upload's")
    choose_finacial_instution = fields.Char("Choose Financial Institution")
    login_date_with_Bank_NBFC = fields.Date("Login Date With Bank/NBFC")
    dsa_code = fields.Char("Dsa Code")
    mode_of_create = fields.Char("Mode Of Create")
    Bank_FI = fields.Many2many("financial.institution.onboard", string="Bank/FI")
    documents_quality_check = fields.Boolean("Documents Quality Check")
    pre_sanction_pendency = fields.Boolean("Pre Sanction Pendency")
    pendency_complete_date = fields.Char("Pendency Complete Date")
    pendencies = fields.Char("Pendencies")
    sanction_date = fields.Date("Sanction Date")
    technical_clearance = fields.Boolean("Technical Clearance")
    legal_clearance = fields.Boolean("Legal Clearance")
    sanction_amount = fields.Monetary("Sanction Amount", currency_field='company_currency')
    runner_agency_assigned = fields.Char("Runner Agency Assigned")
    file_pick_up_date = fields.Date("File Pickup Date")
    file_submission_date = fields.Date("File Submission Date")
    disb_Date = fields.Date("Disbursed Date")
    dis_amount = fields.Monetary("Disbursed Amount", currency_field='company_currency')
    channel_sales_manager = fields.Many2one('res.partner',string="Channel Sales Manager")
    area_head = fields.Many2one('res.partner',string="Area Head")
    regional_head = fields.Many2one('res.partner',string="Regional Head")
    # physical_journey = fields.Char("Physical Journey")
    attachment_ids = fields.Many2many(
        'ir.attachment', 'dosument_upload_attachments_rel',
        string='Document Upload')
    attachment_ids_binary = fields.Binary(string='Document Upload')


    visited_date = fields.Date(string="Visit Date")
    product_ids = fields.Many2many('product.template', 'capwise_order_partner_rel', string='Products')

    # Description
    name = fields.Char(
        'Loan Name', index=True, required=True,
        compute='_compute_name', readonly=False, store=True)
    user_id = fields.Many2one(
        'res.users', string='CSM Name', default=lambda self: self.env.user,
        domain="['&', ('share', '=', False), ('company_ids', 'in', user_company_ids)]",
        check_company=True, index=True, tracking=True)
    user_company_ids = fields.Many2many(
        'res.company', compute='_compute_user_company_ids',
        help='UX: Limit to lead company or all if no company')
    user_email = fields.Char('User Email', related='user_id.email', readonly=True)
    user_login = fields.Char('User Login', related='user_id.login', readonly=True)
    location = fields.Many2one("res.country.state", string="Location")
    team_id = fields.Many2one(
        'crm.team', string='ASM Name', check_company=True, index=True, tracking=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        compute='_compute_team_id', ondelete="set null", readonly=False, store=True)
    company_id = fields.Many2one(
        'res.company', string='Company', index=True,
        compute='_compute_company_id', readonly=False, store=True)
    referred = fields.Char('Referred By')
    description = fields.Html('Notes')
    active = fields.Boolean('Active', default=True, tracking=True)
    type = fields.Selection([
        ('lead', 'Lead'), ('opportunity', 'Opportunity')],
        index=True, required=True, tracking=15,
        default=lambda self: 'lead' if self.env['res.users'].has_group('crm.group_use_lead') else 'opportunity')
    # Pipeline management
    # priority = fields.Selection(string='Priority', index=True,
    #     default=)
    stage_id = fields.Many2one(
        'loan.stage', string='Stage', index=True, tracking=True, readonly=False, store=True,
        copy=False, group_expand='_read_group_stage_ids', ondelete='restrict',
        domain="['|', ('team_id', '=', False), ('team_id', '=', team_id)]")
    # _read_group_stage_ids
    kanban_state = fields.Selection([
        ('grey', 'No next activity planned'),
        ('red', 'Next activity late'),
        ('green', 'Next activity is planned')], string='Kanban State',
        compute='_compute_kanban_state')
    tag_ids = fields.Many2many(
        'crm.tag', 'crm_capwise_lead_rel', string='Tags',
        help="Classify and analyze your lead/opportunity categories like: Training, Service")
    color = fields.Integer('Color Index', default=0)
    # Revenues
    expected_revenue = fields.Monetary('Application Amount', currency_field='company_currency', tracking=True)
    prorated_revenue = fields.Monetary('Prorated Revenue', currency_field='company_currency', store=True, compute="_compute_prorated_revenue")
    recurring_revenue = fields.Monetary('Recurring Revenues', currency_field='company_currency', groups="crm.group_use_recurring_revenues", tracking=True)
    recurring_plan = fields.Many2one('crm.recurring.plan', string="Recurring Plan", groups="crm.group_use_recurring_revenues")
    recurring_revenue_monthly = fields.Monetary('Expected MRR', currency_field='company_currency', store=True,
                                               compute="_compute_recurring_revenue_monthly",
                                               groups="crm.group_use_recurring_revenues")
    recurring_revenue_monthly_prorated = fields.Monetary('Prorated MRR', currency_field='company_currency', store=True,
                                               compute="_compute_recurring_revenue_monthly_prorated",
                                               groups="crm.group_use_recurring_revenues")
    company_currency = fields.Many2one("res.currency", string='Currency', related='company_id.currency_id', readonly=True)
    # Dates
    date_closed = fields.Datetime('Closed Date', readonly=True, copy=False)
    date_action_last = fields.Datetime('Last Action', readonly=True)
    date_open = fields.Datetime(
        'Assignment Date', compute='_compute_date_open', readonly=True, store=True)
    day_open = fields.Float('Days to Assign', compute='_compute_day_open', store=True)
    day_close = fields.Float('Days to Close', compute='_compute_day_close', store=True)
    date_last_stage_update = fields.Datetime(
        'Last Stage Update', compute='_compute_date_last_stage_update', index=True, readonly=True, store=True)
    date_conversion = fields.Datetime('Conversion Date', readonly=True)
    date_deadline = fields.Date('Expected Closing', help="Estimate of the date on which the opportunity will be won.")
    # Customer / contact
    partner_id = fields.Many2one(
        'res.partner', string='Partner', check_company=True, index=True, tracking=10,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="Linked partner (optional). Usually created when converting the lead. You can find a partner by its Name, TIN, Email or Internal Reference.")
    partner_is_blacklisted = fields.Boolean('Partner is blacklisted', related='partner_id.is_blacklisted', readonly=True)
    contact_name = fields.Char(
        'Contact Name', tracking=30,
        compute='_compute_contact_name', readonly=False, store=True)
    partner_name = fields.Char(
        'Company Name', tracking=20, index=True,
        compute='_compute_partner_name', readonly=False, store=True,
        help='The name of the future partner company that will be created while converting the lead into opportunity')
    function = fields.Char('Job Position', compute='_compute_function', readonly=False, store=True)
    title = fields.Many2one('res.partner.title', string='Title', compute='_compute_title', readonly=False, store=True)
    email_from = fields.Char(
        'Email', tracking=40, index=True, readonly=False, store=True)

    dsa_id = fields.Many2one(
        'res.partner', string='DSA name', check_company=True, index=True, tracking=10,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",)
    phone1 = fields.Char(
        'Phone', tracking=50, readonly=False, store=True)
    mobile = fields.Char('Mobile', compute='_compute_mobile', readonly=False, store=True)
    phone_state = fields.Selection([
        ('correct', 'Correct'),
        ('incorrect', 'Incorrect')], string='Phone Quality', store=True)
    email_state = fields.Selection([
        ('correct', 'Correct'),
        ('incorrect', 'Incorrect')], string='Email Quality', compute="_compute_email_state", store=True)
    website = fields.Char('Website', index=True, help="Website of the contact", compute="_compute_website", readonly=False, store=True)
    lang_id = fields.Many2one('res.lang', string='Language')
    # Address fields
    street = fields.Char('Street', compute='_compute_partner_address_values', readonly=False, store=True)
    street2 = fields.Char('Street2', compute='_compute_partner_address_values', readonly=False, store=True)
    zip = fields.Char('Zip', change_default=True, compute='_compute_partner_address_values', readonly=False, store=True)
    city = fields.Char('City', compute='_compute_partner_address_values', readonly=False, store=True)
    state_id = fields.Many2one(
        "res.country.state", string='State',
        compute='_compute_partner_address_values', readonly=False, store=True,
        domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one(
        'res.country', string='Country',
        compute='_compute_partner_address_values', readonly=False, store=True)
    # Probability (Opportunity only)
    probability = fields.Float(
        'Probability', group_operator="avg", copy=False, readonly=False, store=True)
    probability_roi = fields.Float(
        'Rate Of Interest', copy=False, readonly=False, store=True)
    automated_probability = fields.Float('Automated Probability', compute='_compute_probabilities', readonly=True, store=True)
    is_automated_probability = fields.Boolean('Is automated probability?', compute="_compute_is_automated_probability")
    # Won/Lost
    lost_reason = fields.Many2one(
        'crm.lost.reason', string='Lost Reason',
        index=True, ondelete='restrict', tracking=True)
    # Statistics
    calendar_event_ids = fields.One2many('calendar.event', 'opportunity_id', string='Meetings')
    calendar_event_count = fields.Integer('# Meetings', compute='_compute_calendar_event_count')
    duplicate_lead_ids = fields.Many2many("capwise.lead", compute="_compute_potential_lead_duplicates", string="Potential Duplicate Lead", context={"active_test": False})
    duplicate_lead_count = fields.Integer(compute="_compute_potential_lead_duplicates", string="Potential Duplicate Lead Count")
    # UX
    partner_email_update = fields.Boolean('Partner Email will Update')
    partner_phone_update = fields.Boolean('Partner Phone will Update')


    loan_type = fields.Selection([
        ('bl', 'Business Loan'),
        ('pl', 'Personal Loan'),
        ('hl', 'Home Loan'),
        ('lap', 'Loan Against Property'),], string='Loan Type')

    b_kyc_document_type = fields.Char("Document Type")
    b_kyc_adhar_front_photo = fields.Binary("Address proof 1")
    b_kyc_adhar_back_photo = fields.Binary("Address proof 2")


    lead_tenure_in_months = fields.Char("Tenure In Months")

    b_kyc_adhar_front_photo_pdf = fields.Binary("Address proof 1")
    b_kyc_adhar_back_photo_pdf = fields.Binary("Address proof 2")

    b_kyc_pan_card_front_pdf = fields.Binary("Pan Card")
    b_kyc_pan_card_front = fields.Binary("Pan Card ")
    
    b_kyc_pan_card_number = fields.Char("Pan Card Number")
    b_kyc_bate_of_birth = fields.Date("Date Of Birth")
    b_address_owned_rented = fields.Char("Residence")
    b_address_house = fields.Char("House no./Flat/Building")
    b_address_pincode = fields.Char("Pincode")
    b_address_street = fields.Char("Area/Street/Sector/Village")
    b_address_city = fields.Char("City")
    b_address_state = fields.Char("State")
    b_address_bate_of_birth = fields.Date("Date of  Birth")
    b_address_permanent_address_proof = fields.Char("Address Proof")
    is_permanent_address = fields.Boolean("Is Permanent Address")
    b_address_permanent_address_proof_front = fields.Binary("Address Proof Photo - Front")
    b_address_permanent_address_proof_back = fields.Binary("Address Proof Photo - Back")

    b_address_permanent_address_proof_front_pdf = fields.Binary("Address Proof Photo - Front")
    b_address_permanent_address_proof_back_pdf = fields.Binary("Address Proof Photo - Back")

    b_lead_upload_photo = fields.Binary("Photo")
    b_lead_upload_photo_pdf = fields.Binary("Photo")

    b_address_permanent_house = fields.Char("House no./Flat/Building")
    b_address_permanent_village = fields.Char("Area/Street/Sector/Village")
    b_address_permanent_pincode = fields.Char("Pincode")
    b_address_permanent_city = fields.Char("City")
    b_address_permanent_state = fields.Char("State")
    b_business_company_identification_number = fields.Char("Company Identification Number (If Applicable)")
    b_business_gstin = fields.Char("GSTIN (If Applicable)")
    b_business_business__name = fields.Char("Business Name")
    b_business_business_constitution = fields.Char("Business Constitution")
    b_business_date_of_incorporation = fields.Date("Date Of Incorporation")
    b_business_business_vintage = fields.Char("Business Vintage")
    b_business_business_pan_card = fields.Char("Business Pan Card Number (If Applicable)")
    b_business_tin_number = fields.Char("TIN Number (If Applicable)")
    b_business_tan_number = fields.Char("TAN Number (If Applicable)")
    b_business_current_year_turnover = fields.Char("Turnover - Assessment year (21 - 22)")
    b_business_previous_year_turnover = fields.Char("Turnover - Assessment year (20 - 21)")
    b_business_current_year_profit_after_tax = fields.Char("Profit After Tax - Assessment year (21 - 22)")
    b_business_previous_year_profit_after_tax = fields.Char("Profit After Tax - Assessment year (20 - 21)")
    b_business_industry_type = fields.Char("Industry Type")
    b_business_industry_classs = fields.Char("Industry class")
    b_business_industry_sub_classs = fields.Char("Industry Sub Class")
    b_business_register_owned_rented = fields.Char("Residence")
    b_business_register_office_addess_proof = fields.Char("Register Office Address Proof")
    b_business_register_document_photo_front = fields.Binary("Register Document Proof")
    b_business_register_document_photo_front_pdf = fields.Binary("Register Document Proof")
    b_business_register_document_photo_back = fields.Binary("Register Document Proof Back")
    b_business_register_document_photo_back_pdf = fields.Binary("Register Document Proof Back")
    b_business_register_pin_pincode = fields.Char("Pincode")
    b_business_register_building_number = fields.Char("Building Number")
    b_business_register_street = fields.Char("Street / Lane")
    b_business_register_current_office_street = fields.Char("Street / Lane")
    b_business_register_current_office_pincode = fields.Char("Pincode")
    b_business_register_city = fields.Char("City")
    b_business_register_current_office_city = fields.Char("City")
    b_business_register_current_office_state = fields.Char("State")
    b_business_register_state = fields.Char("State")
    b_business_register_current_office_addess_is_same = fields.Boolean("Current Office Address Is Same As Registered Office Address")
    b_business_register_current_office_owned_rented = fields.Char("Residence")
    b_business_register_current_office_address_proof = fields.Char("Current Office address proof")
    b_business_register_current_office_address_photo_front = fields.Binary("Address Proof Document")
    b_business_register_current_office_address_photo_front_pdf = fields.Binary("Address Proof Document")
    b_business_register_current_office_address_photo_back = fields.Binary("Current Office Address Photo")
    b_business_register_current_office_address_photo_back_pdf = fields.Binary("Current Office Address Photo")
    b_business_register_current_office_building = fields.Char("Building Number")
    b_business_register_landmark = fields.Char("Landmark")
    b_business_register_current_office_landmark = fields.Char("Landmark")
    b_existing_owned_rented = fields.Char("Residence")
    existing_loan = fields.Boolean("Existing Loan")
    b_existing_bank_name = fields.Char("Bank name")
    b_existing_type_of_loan = fields.Char("Type Of Loan")
    b_existing_loan_account_number = fields.Char("Loan Account Number")
    b_existing_loan_ammount = fields.Char("Loan Amount")
    b_address_emi = fields.Char("EMI")
    b_address_tenure = fields.Char("Tenure")
    b_address_roi = fields.Char("ROI")
    b_address_current_out_standing_ammount = fields.Char("Current Outstanding Amount")
    b_address_bank_details = fields.Char("Bank Details")
    b_address_select_bank = fields.Char("Select Bank")
    b_address_bank_account_type = fields.Char("Bank Account Type")
    b_address_is_you_bank_password_protected = fields.Char("Is You Bank Password Protected")



    p_applicant_photo = fields.Binary("Photo")
    p_applicant_photo_pdf = fields.Binary("Photo")

    p_father_husband_name = fields.Char("Father's/Husband's Name")
    p_educational_qualification = fields.Char("Educational qualification")
    p_marital_status = fields.Char("Marital Status")
    p_personal_email_id = fields.Char("Personal email id")
    p_mobile_number = fields.Char("Mobile number")
    p_relationship_with_applicant = fields.Char("Relationship with applicant")
    p_co_applicant_is = fields.Char("Co-Applicant is")
    p_co_applicant_name = fields.Char("Full name")
    p_co_applicant_gender = fields.Selection([
        ('male', 'Male'), ('female', 'Female'),('other', 'OTHER')], string="Gender")
    p_co_applicant_marital_status = fields.Char("Marital Status")
    p_co_applicant_father_husband_name = fields.Char("Father's/Husband's Name")
    p_co_applicant_educational_qualification = fields.Char("Educational Qualification")
    p_co_applicant_personal_email_d = fields.Char("Personal Email Id")
    p_co_applicant_mobile_number = fields.Char("Mobile Number")


    p2_relationship_with_applicant = fields.Char("Relationship with applicant")
    p2_co_applicant_is = fields.Char("Co-Applicant is")
    p2_co_applicant_name = fields.Char("Full name")
    p2_co_applicant_gender = fields.Selection([
        ('male', 'Male'), ('female', 'Female'),('other', 'OTHER')], string="Gender")
    p2_co_applicant_marital_status = fields.Char("Marital Status")
    p2_co_applicant_father_husband_name = fields.Char("Father's/Husband's Name")
    p2_co_applicant_educational_qualification = fields.Char("Educational Qualification")
    p2_co_applicant_personal_email_d = fields.Char("Personal Email Id")
    p2_co_applicant_mobile_number = fields.Char("Mobile Number")


    p3_relationship_with_applicant = fields.Char("Relationship with applicant")
    p3_co_applicant_is = fields.Char("Co-Applicant is")
    p3_co_applicant_name = fields.Char("Co-applicant name")
    p3_co_applicant_gender = fields.Selection([
        ('male', 'Male'), ('female', 'Female'),('other', 'OTHER')], string="Gender")
    p3_co_applicant_marital_status = fields.Char("Marital Status")
    p3_co_applicant_father_husband_name = fields.Char(" Father's/Husband's Name")
    p3_co_applicant_educational_qualification = fields.Char("Educational Qualification")
    p3_co_applicant_personal_email_d = fields.Char("Personal Email Id")
    p3_co_applicant_mobile_number = fields.Char("Mobile Number")
    p_coapplicant_business_additional_amount  = fields.Char("Amount")
    p_coapplicant_business_additional_source = fields.Char("Source")
    p2_coapplicant_business_additional_amount = fields.Char("Amount")
    p2_coapplicant_business_additional_source = fields.Char("Source")


    p_kyc_type_of_document = fields.Char("Type Of Residence Address Proof")
    p_kyc_current_address_residence_proof_front = fields.Binary("Current Address Residence Proof Front")
    p_kyc_current_address_residence_proof_back = fields.Binary("Current Address Residence Proof Back")

    p_kyc_current_address_residence_proof_front_pdf = fields.Binary("Current Address Residence Proof Front")
    p_kyc_current_address_residence_proof_back_pdf = fields.Binary("Current Address Residence Proof Back")

    p_kyc_current_pan_card_photo = fields.Binary("Pan Card Photo")
    p_kyc_current_pan_card_photo_pdf = fields.Binary("Pan Card Photo")
    p_kyc_current_pan_number = fields.Char("Pan Number")
    p_kyc_current_date_of_birth = fields.Date("Date Of Birth")


    p_kyc_coapplicant_type_of_document = fields.Char("Type Of Residence Address Proof")
    p_kyc_coapplicant_current_address_residence_proof_front = fields.Binary("Current Address Residence Proof Front")
    p_kyc_coapplicant_current_address_residence_proof_back = fields.Binary("Current Address Residence Proof Back")

    p_kyc_coapplicant_current_address_residence_proof_front_pdf = fields.Binary("Current Address Residence Proof Front")
    p_kyc_coapplicant_current_address_residence_proof_back_pdf = fields.Binary("Current Address Residence Proof Back")

    p_kyc_coapplicant_current_pan_card_photo = fields.Binary("Pan Card Photo")
    p_kyc_coapplicant_current_pan_card_photo_pdf = fields.Binary("Pan Card Photo")

    p_kyc_coapplicant_current_pan_number = fields.Char("Pan Number")
    p_kyc_coapplicant_current_date_of_birth = fields.Date("Date Of Birth")


    p2_kyc_coapplicant_type_of_document = fields.Char("Type Of Residence Address Proof")
    p2_kyc_coapplicant_current_address_residence_proof_front = fields.Binary("Current Address Residence Proof Front")
    p2_kyc_coapplicant_current_address_residence_proof_back = fields.Binary("Current Address Residence Proof Back")

    p2_kyc_coapplicant_current_address_residence_proof_front_pdf = fields.Binary("Current Address Residence Proof Front")
    p2_kyc_coapplicant_current_address_residence_proof_back_pdf = fields.Binary("Current Address Residence Proof Back")


    p2_kyc_coapplicant_current_pan_card_photo = fields.Binary("Pan Card Photo")
    p2_kyc_coapplicant_current_pan_card_photo_pdf = fields.Binary("Pan Card Photo")
    p2_kyc_coapplicant_current_pan_number = fields.Char("Pan Number")
    p2_kyc_coapplicant_current_date_of_birth = fields.Date("Date Of Birth")

    p3_kyc_coapplicant_type_of_document = fields.Char("Type Of Document")
    p3_kyc_coapplicant_current_address_residence_proof_front = fields.Binary("Current Address Residence Proof Front")
    p3_kyc_coapplicant_current_address_residence_proof_back = fields.Binary("Current Address Residence Proof Back")

    p3_kyc_coapplicant_current_address_residence_proof_front_pdf = fields.Binary("Current Address Residence Proof Front")
    p3_kyc_coapplicant_current_address_residence_proof_back_pdf = fields.Binary("Current Address Residence Proof Back")

    p3_kyc_coapplicant_current_pan_card_photo = fields.Binary("Pan Card Photo")
    p3_kyc_coapplicant_current_pan_card_photo_pdf = fields.Binary("Pan Card Photo")
    p3_kyc_coapplicant_current_pan_number = fields.Char("Pan Number")
    p3_kyc_coapplicant_current_date_of_birth = fields.Date("Date Of Birth")


    p_address_residence_owner_rent = fields.Char("Residence")
    p_address_number_of_year_in_current_residence = fields.Char("Number Of Year In Current Residence")
    p_address_flat_house = fields.Char("Flat/house no/Building")
    p_address_street_lane = fields.Char("Area/Street/Sector/Village")
    p_address_city = fields.Char("City")
    p_address_state = fields.Char("State")
    p_permant_address_proof = fields.Char("Permanent Address Proof")
    p_permant_address_proof_photo = fields.Binary("Permanent Address Proof Photo")
    p_permant_address_proof_photo_pdf = fields.Binary("Permanent Address Proof Photo")
    applicant_highest_professional_qualification = fields.Char("Applicant highest professional qualification")
    p_permant_pin_code = fields.Char("Pin Code")
    p_permant_street_lane = fields.Char("Area/Street/Sector/Village")
    p_permant_flat_house = fields.Char("Flat/house no/Building")
    p_permant_state = fields.Char("State")
    p_permant_city = fields.Char("City")
    p_coapplicant_address_residence_owner_rent = fields.Char("Residence")
    p_coapplicant_address_number_of_year_in_current_residence = fields.Char("Number Of Year In Current Residence")
    p_coapplicant_address_flat_house = fields.Char("Flat/house no/Building")
    p_coapplicant_address_street_lane = fields.Char("Area/Street/Sector/Village")
    p_coapplicant_address_city = fields.Char("City")
    p_coapplicant_address_state = fields.Char("State")
    p_coapplicant_permant_address_proof = fields.Char("Permanent Address Proof")
    p_coapplicant_permant_address_proof_photo = fields.Binary("Permanent Address Proof Photo")
    p_coapplicant_permant_pin_code = fields.Char("Pincode")
    p_coapplicant_permant_street_lane = fields.Char("Area/Street/Sector/Village")
    p_coapplicant_permant_flat_house = fields.Char("Flat/house no/Building")
    p_coapplicant_permant_state = fields.Char("State")
    p_coapplicant_permant_city = fields.Char("City")


    p3_coapplicant_address_residence_owner_rent = fields.Char("Residence")
    p3_coapplicant_address_number_of_year_in_current_residence = fields.Char("Number Of Year In Current Residence")
    p3_coapplicant_address_flat_house = fields.Char("Flat/house no/Building")
    p3_coapplicant_address_street_lane = fields.Char("Area/Street/Sector/Village")
    p3_coapplicant_address_city = fields.Char("City")
    p3_coapplicant_address_state = fields.Char("State")
    p3_coapplicant_permant_address_proof = fields.Char("Permanent Address Proof")
    p3_coapplicant_permant_address_proof_photo = fields.Binary("Permanent Address Proof Photo")
    p3_coapplicant_permant_pin_code = fields.Char("Pincode")
    p3_coapplicant_permant_street_lane = fields.Char("Area/Street/Sector/Village")
    p3_coapplicant_permant_flat_house = fields.Char("Flat/house no/Building")
    p3_coapplicant_permant_state = fields.Char("State")
    p3_coapplicant_permant_city = fields.Char("City")


    p2_coapplicant_address_residence_owner_rent = fields.Char("Residence")
    p2_coapplicant_address_number_of_year_in_current_residence = fields.Char("Number Of Year In Current Residence")
    p2_coapplicant_address_flat_house = fields.Char("Flat/house no/Building")
    p2_coapplicant_address_street_lane = fields.Char("Area/Street/Sector/Village")
    p2_coapplicant_address_city = fields.Char("City")
    p2_coapplicant_address_state = fields.Char("State")
    p2_coapplicant_permant_address_proof = fields.Char("Permanent Address Proof")
    p2_coapplicant_permant_address_proof_photo = fields.Binary("Permanent Address Proof Photo")
    p2_coapplicant_permant_pin_code = fields.Char("Pincode")
    p2_coapplicant_permant_street_lane = fields.Char("Area/Street/Sector/Village")
    p2_coapplicant_permant_flat_house = fields.Char("Flat/house no/Building")
    p2_coapplicant_permant_state = fields.Char("State")
    p2_coapplicant_permant_city = fields.Char("City")


    p_business_name_of_current_orginization = fields.Char("Name Of Current Organization")
    p_busness_orginization_type = fields.Char("Organization Type")
    p_busness_industry_type = fields.Char("Industry Type")
    p_business_employment_type = fields.Char("Employment Type")
    p_business_employeement_id_number = fields.Char("Employement Id Number")
    p_business_officail_email_id = fields.Char("Official Email Id")
    p_business_net_monthly_salary = fields.Char("Net Monthly Salary")
    p_business_gross_monthly_salary = fields.Char("Gross Monthly Salary")
    p_business_designation = fields.Char("Designation")
    p_business_department = fields.Char("Department")
    p_business_year_in_current_job = fields.Char("Months In Current Job")
    p_business_total_work_experiance = fields.Char("Total Work Experience")
    p_business_additional_amount = fields.Char("Amount")
    p_business_additional_source = fields.Char("Source")
    p2_business_additional_amount = fields.Char("Amount")
    p2_business_additional_source = fields.Char("Source")
    p_business_office_pin_code = fields.Char("Pin Code")
    p_business_office_building_numbr = fields.Char("Building Number")
    p_business_office_street_lane = fields.Char("Street/Lane")
    p_business_office_landmark = fields.Char("Landmark")
    p_business_office_city = fields.Char("City")
    p_business_building_office_state = fields.Char("State")


    p_business_co_aaplicant_year_in_current_job_year_month = fields.Char("Months In Current Job")
    p_busness_co_aaplicant_total_work_experieance = fields.Char("Total Work Experience")
    p_busness_co_aaplicant_net_monthly_salary = fields.Char("Net Monthly Salary")
    p_business_co_aaplicant_gross_monthly_salary = fields.Char("Gross Monthly Salary")
    p_business_co_aaplicant_applicant_profession = fields.Char("Applicant Profession")
    p_business_co_aaplicant_employment_type = fields.Char("Employment Type")
    p_business_co_aaplicant_orginization_name = fields.Char("Organization Name")
    p_business_co_aaplicant_designation = fields.Char("Designation")
    p_business_co_aaplicant_department = fields.Char("Department")


    p2_business_co_aaplicant_year_in_current_job_year_month = fields.Char("Months In Current Job")
    p2_busness_co_aaplicant_total_work_experieance = fields.Char("Total Work Experience")
    p2_busness_co_aaplicant_net_monthly_salary = fields.Char("Net Monthly Salary")
    p2_business_co_aaplicant_gross_monthly_salary = fields.Char("Gross Monthly Salary")
    p2_business_co_aaplicant_employment_type = fields.Char("Employment Type")
    p2_business_co_aaplicant_orginization_name = fields.Char("Organization Name")
    p2_business_co_aaplicant_designation = fields.Char("Designation")
    p2_business_co_aaplicant_department = fields.Char("Department")
    p2_business_co_aaplicant_applicant_profession = fields.Char("Applicant Profession")


    p3_business_co_aaplicant_year_in_current_job_year_month = fields.Char("Months In Current Job")
    p3_busness_co_aaplicant_total_work_experieance = fields.Char("Total Work Experience")
    p3_busness_co_aaplicant_net_monthly_salary = fields.Char("Net Monthly Salary")
    p3_business_co_aaplicant_gross_monthly_salary = fields.Char("Gross Monthly Salary")
    p3_business_co_aaplicant_employment_type = fields.Char("Employment Type")
    p3_business_co_aaplicant_orginization_name = fields.Char("Organization Name")
    p3_business_co_aaplicant_designation = fields.Char("Designation")
    p3_business_co_aaplicant_department = fields.Char("Department")
    p3_business_co_aaplicant_applicant_profession = fields.Char("Applicant Profession")


    p_obligation_loan = fields.Boolean("Loan")
    p_obligation_loan_amount = fields.Char("Loan Amount")
    p_obligation_bank_name = fields.Char("Bank Name")
    p_obligation_type_of_loan = fields.Char("Type Of Loan")
    p_obligation_account_number = fields.Char("Account Number")
    p_obligation_emi = fields.Char("EMI")
    p_obligation_loan_opening_date = fields.Date("Loan Opening Date")
    p_obligation_tenure = fields.Char("Tenure")
    p_obligation_roi = fields.Char("ROI")
    p_obligation_type_of_security = fields.Char("Type Of Security")
    p_obligation_current_out_standing_amount = fields.Char("Current Outstanding Amount")


    p2_obligation_loan = fields.Boolean("Loan")
    p2_obligation_bank_name = fields.Char("Bank Name")
    p2_obligation_type_of_loan = fields.Char("Type Of Loan")
    p2_obligation_loan_amount = fields.Char("Loan Amount")
    p2_obligation_account_number = fields.Char("Account Number")
    p2_obligation_emi = fields.Char("EMI")
    p2_obligation_loan_opening_date = fields.Date("Loan Opening Date")
    p2_obligation_tenure = fields.Char("Tenure")
    p2_obligation_roi = fields.Char("ROI")
    p2_obligation_type_of_security = fields.Char("Type Of Security")
    p2_obligation_current_out_standing_amount = fields.Char("Current Outstanding Amount")


    p3_obligation_loan = fields.Boolean("Loan")
    p3_obligation_bank_name = fields.Char("Bank Name")
    p3_obligation_loan_amount = fields.Char("Loan Amount")
    p3_obligation_type_of_loan = fields.Char("Type Of Loan")
    p3_obligation_account_number = fields.Char("Account Number")
    p3_obligation_emi = fields.Char("EMI")
    p3_obligation_loan_opening_date = fields.Date("Loan Opening Date")
    p3_obligation_tenure = fields.Char("Tenure")
    p3_obligation_roi = fields.Char("ROI")
    p3_obligation_type_of_security = fields.Char("Type Of Security")
    p3_obligation_current_out_standing_amount = fields.Char("Current Outstanding Amount")
    p3_obligation_credit_card = fields.Boolean("Credit Card")
    p3_obligation_current_credit_out_standing_amount = fields.Char("Current Outstanding Amount")
    p3_obligation_credit_bank_name = fields.Char("Bank Name")
    p3_obligation_credit_limit = fields.Char("Credit Limit")


    p_coapplicant_obligation_bank_name = fields.Char("Bank Name")
    p_coapplicant_obligation_type_of_loan = fields.Char("Type Of Loan")
    p_coapplicant_obligation_account_number = fields.Char("Account Number")
    p_coapplicant_obligation_loan_amount = fields.Char("Loan Amount")
    p_coapplicant_obligation_emi = fields.Char("EMI")
    p_coapplicant_obligation_loan_opening_date = fields.Date("Loan Opening Date")
    p_coapplicant_obligation_tenure = fields.Char("Tenure")
    p_coapplicant_obligation_roi = fields.Char("ROI")
    p_coapplicant_obligation_type_of_security = fields.Char("Type Of Security")
    p_coapplicant_obligation_current_out_standing_amount = fields.Char("Current Outstanding Amount")


    pl2_coapplicant_obligation_bank_name = fields.Char("Bank Name")
    pl2_coapplicant_obligation_type_of_loan = fields.Char("Type Of Loan")
    pl2_coapplicant_obligation_account_number = fields.Char("Account Number")
    pl2_coapplicant_obligation_loan_amount = fields.Char("Loan Amount")
    pl2_coapplicant_obligation_emi = fields.Char("EMI")
    pl2_coapplicant_obligation_loan_opening_date = fields.Date("Loan Opening Date")
    pl2_coapplicant_obligation_tenure = fields.Char("Tenure")
    pl2_coapplicant_obligation_roi = fields.Char("ROI")
    pl2_coapplicant_obligation_type_of_security = fields.Char("Type Of Security")
    pl2_coapplicant_obligation_current_out_standing_amount = fields.Char("Current Outstanding Amount")


    pl22_coapplicant_obligation_data_is = fields.Boolean("Co-Applicant")
    pl22_coapplicant_obligation_bank_name = fields.Char("Bank Name")
    pl22_coapplicant_obligation_type_of_loan = fields.Char("Type Of Loan")
    pl22_coapplicant_obligation_account_number = fields.Char("Account Number")
    pl22_coapplicant_obligation_loan_amount = fields.Char("Loan Amount")
    pl22_coapplicant_obligation_emi = fields.Char("EMI")
    pl22_coapplicant_obligation_loan_opening_date = fields.Date("Loan Opening Date")
    pl22_coapplicant_obligation_tenure = fields.Char("Tenure")
    pl22_coapplicant_obligation_roi = fields.Char("ROI")
    pl22_coapplicant_obligation_type_of_security = fields.Char("Type Of Security")
    pl22_coapplicant_obligation_current_out_standing_amount = fields.Char("Current Outstanding Amount")


    pl32_coapplicant_obligation_data_is = fields.Boolean("Co-Applicant")
    pl32_coapplicant_obligation_bank_name  = fields.Char("Bank Name")
    pl32_coapplicant_obligation_type_of_loan = fields.Char("Type Of Loan")
    pl32_coapplicant_obligation_account_number = fields.Char("Account Number")
    pl32_coapplicant_obligation_loan_amount = fields.Char("Loan Amount")
    pl32_coapplicant_obligation_emi = fields.Char("EMI")
    pl32_coapplicant_obligation_loan_opening_date = fields.Date("Loan Opening Date")
    pl32_coapplicant_obligation_tenure = fields.Char("Tenure")
    pl32_coapplicant_obligation_roi = fields.Char("ROI")
    pl32_coapplicant_obligation_type_of_security = fields.Char("Type Of Security")
    pl32_coapplicant_obligation_current_out_standing_amount = fields.Char("Current Outstanding Amount")


    pl23_coapplicant_obligation_data_is = fields.Boolean("Co-Applicant")
    pl23_coapplicant_obligation_bank_name  = fields.Char("Bank Name")
    pl23_coapplicant_obligation_type_of_loan = fields.Char("Type Of Loan")
    pl23_coapplicant_obligation_account_number = fields.Char("Account Number")
    pl23_coapplicant_obligation_loan_amount = fields.Char("Loan Amount")
    pl23_coapplicant_obligation_emi = fields.Char("EMI")
    pl23_coapplicant_obligation_loan_opening_date = fields.Date("Loan Opening Date")
    pl23_coapplicant_obligation_tenure = fields.Char("Tenure")
    pl23_coapplicant_obligation_roi = fields.Char("ROI")
    pl23_coapplicant_obligation_type_of_security = fields.Char("Type Of Security")
    pl23_coapplicant_obligation_current_out_standing_amount = fields.Char("Current Outstanding Amount")


    pl33_coapplicant_obligation_data_is = fields.Boolean("Co-Applicant")
    pl33_coapplicant_obligation_bank_name  = fields.Char("Bank Name")
    pl33_coapplicant_obligation_type_of_loan = fields.Char("Type Of Loan")
    pl33_coapplicant_obligation_account_number = fields.Char("Account Number")
    pl33_coapplicant_obligation_loan_amount = fields.Char("Loan Amount")
    pl33_coapplicant_obligation_emi = fields.Char("EMI")
    pl33_coapplicant_obligation_loan_opening_date = fields.Date("Loan Opening Date")
    pl33_coapplicant_obligation_tenure = fields.Char("Tenure")
    pl33_coapplicant_obligation_roi = fields.Char("ROI")
    pl33_coapplicant_obligation_type_of_security = fields.Char("Type Of Security")
    pl33_coapplicant_obligation_current_out_standing_amount = fields.Char("Current Outstanding Amount")


    pl3_coapplicant_obligation_bank_name = fields.Char("Bank Name")
    pl3_coapplicant_obligation_type_of_loan = fields.Char("Type Of Loan")
    pl3_coapplicant_obligation_account_number = fields.Char("Account Number")
    pl3_coapplicant_obligation_loan_amount = fields.Char("Loan Amount")
    pl3_coapplicant_obligation_emi = fields.Char("EMI")
    pl3_coapplicant_obligation_loan_opening_date = fields.Date("Loan Opening Date")
    pl3_coapplicant_obligation_tenure = fields.Char("Tenure")
    pl3_coapplicant_obligation_roi = fields.Char("ROI")
    pl3_coapplicant_obligation_type_of_security = fields.Char("Type Of Security")
    pl3_coapplicant_obligation_current_out_standing_amount = fields.Char("Current Outstanding Amount")


    p3_coapplicant_obligation_credit_card = fields.Boolean("Credit Card")
    p3_coapplicant_obligation_current_credit_out_standing_amount = fields.Char("Current Outstanding Amount")
    p3_coapplicant_obligation_credit_bank_name = fields.Char("Bank Name")
    p3_coapplicant_obligation_credit_limit = fields.Char("Credit Limit")


    p3_coapplicant_obligation_bank_name = fields.Char("Bank Name")
    p3_coapplicant_obligation_type_of_loan = fields.Char("Type Of Loan")
    p3_coapplicant_obligation_account_number = fields.Char("Account Number")
    p3_coapplicant_obligation_emi = fields.Char("EMI")
    p3_coapplicant_obligation_loan_amount = fields.Char("Loan Amount")
    p3_coapplicant_obligation_loan_opening_date = fields.Date("Loan Opening Date")
    p3_coapplicant_obligation_tenure = fields.Char("Tenure")
    p3_coapplicant_obligation_roi = fields.Char("ROI")
    p3_coapplicant_obligation_type_of_security = fields.Char("Type Of Security")
    p3_coapplicant_obligation_current_out_standing_amount = fields.Char("Current Outstanding Amount")

    p2_coapplicant_obligation_bank_name = fields.Char("Bank Name")
    p2_coapplicant_obligation_type_of_loan = fields.Char("Type Of Loan")
    p2_coapplicant_obligation_account_number = fields.Char("Account Number")
    p2_coapplicant_obligation_emi = fields.Char("EMI")
    p2_coapplicant_obligation_loan_amount = fields.Char("Loan Amount")
    p2_coapplicant_obligation_loan_opening_date = fields.Date("Loan Opening Date")
    p2_coapplicant_obligation_tenure = fields.Char("Tenure")
    p2_coapplicant_obligation_roi = fields.Char("ROI")
    p2_coapplicant_obligation_type_of_security = fields.Char("Type Of Security")
    p2_coapplicant_obligation_current_out_standing_amount = fields.Char("Current Outstanding Amount")



    p_bank_select_bank = fields.Char("Bank Name")
    p_bank_details_account_type = fields.Char("Account Type")
    p_bank_details_upload_statement_past_month = fields.Binary("Upload Bank Statement for Past 6 Month")
    p_bank_details_upload_statement_past_month_pdf = fields.Binary("Upload Bank Statement for Past 6 Month")
    p_bank_is_bank_statement_is_password_protected = fields.Char("Is Bank Statement Password Protected")
    p_bank_password = fields.Char("Bank Password")

    is_bank_1 = fields.Boolean("Bank 1")
    is_bank_2 = fields.Boolean("Bank 2")
    is_bank_3 = fields.Boolean("Bank 3")
    p2_bank_select_bank = fields.Char("Bank Name")
    p2_bank_details_account_type = fields.Char("Account Type")
    p2_bank_details_upload_statement_past_month = fields.Binary("Upload Bank Statement for Past 6 Month")
    p2_bank_details_upload_statement_past_month_pdf = fields.Binary("Upload Bank Statement for Past 6 Month")
    p2_bank_is_bank_statement_is_password_protected = fields.Char("Is Bank Statement Password Protected")
    p2_bank_password = fields.Char("Bank Password")

    p3_bank_select_bank = fields.Char("Bank Name")
    p3_bank_details_account_type = fields.Char("Account Type")
    p3_bank_details_upload_statement_past_month = fields.Binary("Upload Bank Statement for Past 6 Month")
    p3_bank_details_upload_statement_past_month_pdf = fields.Binary("Upload Bank Statement for Past 6 Month")
    p3_bank_is_bank_statement_is_password_protected = fields.Char("Is Bank Statement Password Protected")
    p3_bank_password = fields.Char("Bank Password")


    p_coapplicant_bank_select_bank = fields.Char("Bank Name")
    p_coapplicant_bank_details_account_type = fields.Char("Details Account Type")
    p_coapplicant_bank_details_upload_statement_past_month = fields.Binary("Upload Statement Past 6 Month")
    p_coapplicant_bank_details_upload_statement_past_month_pdf = fields.Binary("Upload Statement Past 6 Month")
    p_coapplicant_bank_is_bank_statement_is_password_protected = fields.Char("Is Bank Statement Password Protected")
    p_coapplicant_bank_password = fields.Char("Password")

    pbl2_coapplicant_bank_select_bank = fields.Char("Bank Name")
    pbl2_coapplicant_bank_details_account_type = fields.Char("Details Account Type")
    pbl2_coapplicant_bank_details_upload_statement_past_month = fields.Binary("Upload Statement Past 6 Month")
    pbl2_coapplicant_bank_details_upload_statement_past_month_pdf = fields.Binary("Upload Statement Past 6 Month")
    pbl2_coapplicant_bank_is_bank_statement_is_password_protected = fields.Char("Is Bank Statement Password Protected")
    pbl2_coapplicant_bank_password = fields.Char("Password")

    pbl3_coapplicant_bank_select_bank = fields.Char("Bank Name")
    pbl3_coapplicant_bank_details_account_type = fields.Char("Details Account Type")
    pbl3_coapplicant_bank_details_upload_statement_past_month = fields.Binary("Upload Statement Past 6 Month")
    pbl3_coapplicant_bank_details_upload_statement_past_month_pdf = fields.Binary("Upload Statement Past 6 Month")
    pbl3_coapplicant_bank_is_bank_statement_is_password_protected = fields.Char("Is Bank Statement Password Protected")
    pbl3_coapplicant_bank_password = fields.Char("Password")

    p2_coapplicant_bank_select_bank = fields.Char("Bank Name")
    p2_coapplicant_bank_details_account_type = fields.Char("Details Account Type")
    p2_coapplicant_bank_details_upload_statement_past_month = fields.Binary("Upload Statement Past 6 Month")
    p2_coapplicant_bank_details_upload_statement_past_month_pdf = fields.Binary("Upload Statement Past 6 Month")
    p2_coapplicant_bank_is_bank_statement_is_password_protected = fields.Char("Is Bank Statement Password Protected")
    p2_coapplicant_bank_password = fields.Char("Password")

    p3_coapplicant_bank_select_bank = fields.Char("Bank Name")
    p3_coapplicant_bank_details_account_type = fields.Char("Details Account Type")
    p3_coapplicant_bank_details_upload_statement_past_month = fields.Binary("Upload Statement Past 6 Month")
    p3_coapplicant_bank_details_upload_statement_past_month_pdf = fields.Binary("Upload Statement Past 6 Month")
    p3_coapplicant_bank_is_bank_statement_is_password_protected = fields.Char("Is Bank Statement Password Protected")
    p3_coapplicant_bank_password = fields.Char("Password")


    profession_categories_salaried = fields.Boolean("Salaried")
    profession_categories_senp = fields.Boolean("SENP")
    profession_categories_sep = fields.Boolean("SEP")
    p_business_business_name = fields.Char("Business Name")
    p_business_profession = fields.Char("Profession")
    p_business_registration_number = fields.Char("Registration Number")
    p_business_gstin = fields.Char("GSTIN Number")
    p_business_years_in_current_profession = fields.Char("Years In Current Profession/Business")
    p_business_gross_professional_receipts_as_per_ITR = fields.Char("Gross Professional Receipts As Per ITR")
    p2_business_gross_professional_receipts_as_per_ITR = fields.Char("Business Gross Professional Receipts As Per ITR (2)")
    p3_business_gross_professional_receipts_as_per_ITR = fields.Char("Business Gross Professional Receipts As Per ITR (3)")
    p_business_email_id = fields.Char("Email-Id(work)")
    p_business_phone_number = fields.Char("Phone Number(work)")
    p_business_register_pin_pincode = fields.Char("Pincode")
    p_business_register_building_number = fields.Char("Building Number")
    p_business_register_street = fields.Char("Street/Lane")
    p_business_register_landmark = fields.Char("Landmark")
    p_business_register_city = fields.Char("City")
    p_business_register_state = fields.Char("State")
    p_business_corporate_register_pin_pincode = fields.Char("pincode")
    p_business_corporate_register_building_number = fields.Char("Building Number")
    p_business_corporate_register_street = fields.Char("Street/Lane")
    p_business_corporate_register_landmark = fields.Char("Landmark")
    p_business_corporate_register_city = fields.Char("City")
    p_business_corporate_register_state = fields.Char("State")



    p_business_i_am_a = fields.Char("I am a")
    p_business_business_constitution = fields.Char("Business Constitution")
    p_business_monthly_renumeration = fields.Char("Monthly Renumeration (As per ITR)")
    p_business_share_holding = fields.Char("Share Holding %")
    p_business_annual_income = fields.Char("Annual Income")
    p_business_share_in_profit = fields.Char("% Share In Profit")
    p_business_business_name = fields.Char("Business Name")
    p_business_industry_type = fields.Char("Industry Type")
    p_business_industry_sub_class = fields.Char("Industry Sub Class")
    p_business_profit_after_tax = fields.Char("Profit After Tax")
    p_business_previous_profit_after_tax = fields.Char("Previous Profit After Tax")
    p_business_current_year_turnover = fields.Char("Current Year Turnover")
    p_business_previous_year_turnover = fields.Char("Previous Year Turnover")
    p_business_Cin_number = fields.Char("CIN Number (If Applicable)")
    p_business_gst_number = fields.Char("GST Number")
    p_business_business_pan = fields.Char("Business Pan")
    p_business_tin_number = fields.Char("TIN Number (If Applicable)")
    p_business_tan_number = fields.Char("TAN Number (If Applicable)")
    p_business_nio_of_partner_director = fields.Char("No. of partner/director")
    p_business_date_of_incorportaion = fields.Date("Date Of Incorporation")
    p_business_business_vintage = fields.Char("Business Vintage")
    p_business_email_id = fields.Char("Email Id (Work)")
    p_business_phn_number = fields.Char("Phone Number (Work)")
    p_business_year_of_current_business = fields.Char("Year Of Current Business")
    p_business_do_you_have_pos = fields.Char("Do You Have Pos")
    p_business_if_year_what_is_your_monthly_card_swipe = fields.Char("If Yes, What Is Your Monthly Card Swipe?")


    p_business_co_aaplicant_gross_professional_receipt = fields.Char("Gross Professional Receipt") 
    p_busness_co_aaplicant_business_name = fields.Char("Business Name") 
    p_busness_co_aaplicant_coaaplicant_is_a = fields.Char("Co-Applicant is a") 
    p_business_co_aaplicant_constitution = fields.Char("Constitution") 
    p_busness_co_aaplicant_amount = fields.Char("amount") 
    p_busness_co_aaplicant_share_holding = fields.Char("Share Holding") 
    p_business_co_aaplicant_monthly_renumeration = fields.Char("Monthly Renumeration") 
    p_busness_co_aaplicant_annual_income = fields.Char("Annual Income") 
    p_busness_co_aaplicant_profit_after_tax_after_current_year = fields.Char("Profit After Tax (after current year)") 
    p_business_co_aaplicant_current_year_turnover = fields.Char("Current Year Turnover") 
    p_busness_co_aaplicant_share_in_profit = fields.Char("Share In Profit") 
    p_busness_co_aaplicant_profit_after_tax_previous_year = fields.Char("Profit  After Tax (Previous year)") 
    p_business_co_aaplicant_previous_year_turn_over = fields.Char("Previous Year Turn Over") 
    p_business_co_aaplicant_source = fields.Char("Source") 


    p2_business_co_aaplicant_gross_professional_receipt = fields.Char("Gross Professional Receipt") 
    p2_busness_co_aaplicant_business_name = fields.Char("Business Name") 
    p2_busness_co_aaplicant_coaaplicant_is_a = fields.Char("Co-Applicant is a") 
    p2_business_co_aaplicant_constitution = fields.Char("Constitution") 
    p2_busness_co_aaplicant_amount = fields.Char("amount") 
    p2_busness_co_aaplicant_share_holding = fields.Char("Share Holding") 
    p2_business_co_aaplicant_monthly_renumeration = fields.Char("Monthly Renumeration") 
    p2_busness_co_aaplicant_annual_income = fields.Char("Annual Income") 
    p2_busness_co_aaplicant_profit_after_tax_after_current_year = fields.Char("Profit After Tax (after current year)") 
    p2_business_co_aaplicant_current_year_turnover = fields.Char("Current Year Turnover") 
    p2_busness_co_aaplicant_share_in_profit = fields.Char("Share In Profit") 
    p2_busness_co_aaplicant_profit_after_tax_previous_year = fields.Char("Profit  After Tax (Previous year)") 
    p2_business_co_aaplicant_previous_year_turn_over = fields.Char("Previous Year Turn Over") 
    p2_business_co_aaplicant_source = fields.Char("Source") 


    p3_business_co_aaplicant_gross_professional_receipt = fields.Char("Gross Professional Receipt") 
    p3_busness_co_aaplicant_business_name = fields.Char("Business Name") 
    p3_busness_co_aaplicant_coaaplicant_is_a = fields.Char("Co-Applicant is a") 
    p3_business_co_aaplicant_constitution = fields.Char("Constitution") 
    p3_busness_co_aaplicant_amount = fields.Char("amount") 
    p3_busness_co_aaplicant_share_holding = fields.Char("Share Holding") 
    p3_business_co_aaplicant_monthly_renumeration = fields.Char("Monthly Renumeration") 
    p3_busness_co_aaplicant_annual_income = fields.Char("Annual Income") 
    p3_busness_co_aaplicant_profit_after_tax_after_current_year = fields.Char("Profit After Tax (after current year)") 
    p3_business_co_aaplicant_current_year_turnover = fields.Char("Current Year Turnover") 
    p3_busness_co_aaplicant_share_in_profit = fields.Char("Share In Profit") 
    p3_busness_co_aaplicant_profit_after_tax_previous_year = fields.Char("Profit  After Tax (Previous year)") 
    p3_business_co_aaplicant_previous_year_turn_over = fields.Char("Previous Year Turn Over") 
    p3_business_co_aaplicant_source = fields.Char("Source") 


    p1_coapplicant_business_additional_amount = fields.Char("Amount")
    p1_coapplicant_business_additional_source = fields.Char("Source")
    p12_coapplicant_business_additional_amount = fields.Char("Amount")
    p12_coapplicant_business_additional_source = fields.Char("Source")


    p2_coapplicant_business_additional_amount = fields.Char("Amount")
    p2_coapplicant_business_additional_source = fields.Char("Source")
    p22_coapplicant_business_additional_amount = fields.Char("Amount")
    p22_coapplicant_business_additional_source = fields.Char("Source")




    h_property_identify = fields.Char("Identify")
    h_property_sub_type = fields.Char("Sub Type")
    h_property_own_by = fields.Char("Property Owned By")
    h_project_building_name = fields.Char("Builder Name")
    h_project_project_name = fields.Char("Project Name")
    h_project_pin_code = fields.Char("Pincode")
    h_project_building_area = fields.Char("Area")
    h_project_unit_no_building_no_flat_number = fields.Char("Unit No/Building No/Flat No.")
    h_project_building_street = fields.Char("Area/Street/Sector/Village")
    h_project_building_city = fields.Char("City")
    h_project_building_state = fields.Char("State")
    h_project_building_housing_authority = fields.Char("Housing Authority")
    h_project_tower = fields.Char("Tower")
    h_project_building = fields.Char("Building")
    h_project_city = fields.Char("City")
    h_project_state = fields.Char("State")
    h_project_area_of_the_property = fields.Char("Area of Property")
    h_project_documented_purchse_cost = fields.Char("Documented Purchase Cost")
    h_project_extimated_market_value = fields.Char("Estimated Market Value")

    h_property_pin_code = fields.Char("Pincode")
    h_property_housing_authority = fields.Char("Housing Authority")


    p_address_pincode = fields.Char("Pincode")
    p_coapplicant_pincode = fields.Char("Pincode")
    p2_coapplicant_pincode = fields.Char("Pincode")
    p3_coapplicant_pincode = fields.Char("Pincode")

    p_co_applicant_data = fields.Boolean("Co-Applicant")
    p2_co_applicant_data = fields.Boolean("Co-Applicant")
    p3_co_applicant_data = fields.Boolean("Co-Applicant")
    p_kyc_coapplicant_data_is = fields.Boolean("Co-Applicant")
    p2_kyc_coapplicant_data_is = fields.Boolean("Co-Applicant")
    p3_kyc_coapplicant_data_is = fields.Boolean("Co-Applicant")
    p_coapplicant_address_data_is = fields.Boolean("Co-Applicant")
    p2_coapplicant_address_data_is = fields.Boolean("Co-Applicant")
    p3_coapplicant_address_data_is = fields.Boolean("Co-Applicant")
    p_business_co_aaplicant_data_is = fields.Boolean("Co-Applicant")
    p2_business_co_aaplicant_data_is = fields.Boolean("Co-Applicant")
    p3_business_co_aaplicant_data_is = fields.Boolean("Co-Applicant")
    p_coapplicant_obligation_data_is = fields.Boolean("Co-Applicant")
    p2_coapplicant_obligation_data_is = fields.Boolean("Co-Applicant")
    p3_coapplicant_obligation_data_is = fields.Boolean("Co-Applicant")
    pl2_coapplicant_obligation_data_is = fields.Boolean("Co-Applicant")
    pl3_coapplicant_obligation_data_is = fields.Boolean("Co-Applicant")
    p_coapplicant_bank_data_is = fields.Boolean("Co-Applicant")
    pbl2_coapplicant_bank_data_is = fields.Boolean("Co-Applicant")
    pbl3_coapplicant_bank_data_is = fields.Boolean("Co-Applicant")
    p2_coapplicant_bank_data_is = fields.Boolean("Co-Applicant")
    p3_coapplicant_bank_data_is = fields.Boolean("Co-Applicant")
    MobilePhoneNumber = fields.Char("MobilePhoneNumber")

    profession = fields.Char("Profession")
    lap_lease_rental_discount = fields.Char("LAP / Lease Rental Discount")
    resident_indian_non_resident = fields.Char("resident Indian /  Non Resident Indian")
    purpose_of_loan = fields.Char("Purpose Of Loan")
    p_gender = fields.Selection([
        ('male', 'Male'), ('female', 'Female'),('other', 'OTHER')], string="Gender")


    lender_data = fields.Many2many("lender.details", string="Leander Data")
    credit_enquiries = fields.Many2many("credit.enquiries", string = "Credit Enquiry")


    new_status_operation = fields.Selection([
        ('pending', 'Pending'), ('approve', 'Approve'),('decline', 'Decline'), ('hold', 'Hold')], string="Operation Status")

    _sql_constraints = [
        ('check_probability', 'check(probability >= 0 and probability <= 100)', 'The probability of closing the deal should be between 0% and 100%!')
    ]


    def get_credit_repot(self):
        # print("self####################",self)
        # print("lead_id#$#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$",lead_id)
        # print("loan_type###########@@@@@@@@@@@####@@##@#@#@#@##@@@@",loan_type)
        # user_ids = self.env['res.users'].browse(self.env.user.id)
        # if not user_ids.phone:
        #     raise UserError(_('Kindly contact your manager to upload your phone number'))
        dct = {}
        headers = {
            "mobile": "7533043898",
            "password": "welcome1234",
            "user_type": "PARTNER"
        }
        response = requests.post("https://api.finbii.com/partners/login", json=headers)
        token = json.loads(response.content).get('token')
        if self.lead_id:
            lead_status = {
                "lead_id" : self.lead_id,
                "loan_type" : self.loan_type,
            }
            response = requests.post("https://api.finbii.com/crm/get-experian",headers={'Authorization': "Bearer %s" % token}, json=lead_status)
            print("response@@@@@@@@@@@@@@@@",json.loads(response.content))
            if isinstance(json.loads(response.content), list):
                _logger.info("pincode************reportddddddd#####**%s" %json.loads(response.content))
                if json.loads(response.content):    
                    json_object = json.loads(response.content)[0]
                    if "showHtmlReportForCreditReport" in json_object:
                        root = json.loads(json_object).get("showHtmlReportForCreditReport")    
                        soup = BeautifulSoup(root, 'html.parser')
                        print("soup$$$$$$$$$$$$$$$$$$$$$$$$$$4",soup)
                        for data in soup:
                            print("data###################",data)
                            tag_first = "First_Name"
                            reg_str_First_Name = "<" + tag_first + ">(.*?)</" + tag_first + ">"
                            res_First_Name = re.findall(reg_str_First_Name, data)
                            First_Name = res_First_Name
                            if First_Name:
                                dct['first_name'] = First_Name[0]
                                print("First_Name##############",First_Name)
                                        

                            tag_last = "Last_Name"
                            reg_str = "<" + tag_last + ">(.*?)</" + tag_last + ">"
                            res_Last_Name = re.findall(reg_str, data)
                            Last_Name = res_Last_Name
                            if Last_Name:
                                dct['Last_Name'] = Last_Name[0]
                                print("Last_name##################",Last_Name)


                            tag_systemcode="SystemCode"
                            reg_str = "<" + tag_systemcode + ">(.*?)</" + tag_systemcode + ">"
                            res_SystemCode = re.findall(reg_str,data)
                            SystemCode = res_SystemCode
                            if SystemCode:
                                dct['SystemCode'] = SystemCode[0]
                                print("SystemCode#########",SystemCode)

                            tag_msgtxt="MessageText"
                            reg_str = "<" + tag_msgtxt + ">(.*?)</" + tag_msgtxt + ">"
                            res_MessageText = re.findall(reg_str,data)
                            MessageText = res_MessageText
                            if MessageText:
                                dct['MessageText'] = MessageText[0]
                                print("MessageText#########",MessageText)

                            tag_date = "ReportDate"
                            reg_str = "<" + tag_date + ">(.*?)</" + tag_date + ">"
                            res_ReportDate = re.findall(reg_str,data)
                            ReportDate = res_ReportDate
                            print("ReportDate######################",ReportDate)
                            if ReportDate:
                                dct['ReportDate'] = self._format_date_change(ReportDate[0]) 
                                print("ReportDate#########",ReportDate)

                            tag_time = "ReportTime"
                            reg_str = "<" + tag_time + ">(.*?)</" + tag_time + ">"
                            res_ReportTime = re.findall(reg_str,data)
                            ReportTime = res_ReportTime
                            if ReportTime:
                                dct['ReportTime'] = ReportTime[0]
                                print("ReportTime#########",ReportTime)

                            tag_usermsg = "UserMessageText"
                            reg_str = "<" + tag_usermsg + ">(.*?)</" + tag_usermsg
                            res_UserMessageText = re.findall(reg_str,data)
                            UserMessageText = res_UserMessageText
                            if UserMessageText:
                                dct['UserMessageText'] = UserMessageText[0]
                                print("UserMessageText#########",UserMessageText)

                            tag_version = "Version"
                            reg_str = "<" + tag_version + ">(.*?)</" + tag_version + ">"
                            res_Version = re.findall(reg_str,data)
                            Version = res_Version
                            if Version:
                                dct['Version'] = Version[0]
                                print("Version#########",Version)

                            tag_enquiry = "Enquiry_Username"
                            reg_str = "<" + tag_enquiry + ">(.*?)</" + tag_enquiry + ">"
                            res_Enquiry_Username = re.findall (reg_str,data)
                            Enquiry_Username = res_Enquiry_Username
                            if Enquiry_Username:
                                dct['Enquiry_Username'] = Enquiry_Username[0]
                                print("Enquiry_Username#########",Enquiry_Username)

                            
                            tag_rptnum = "ReportNumber"
                            reg_str = "ReportTime><" + tag_rptnum + ">(.*?)</" + tag_rptnum + ">"
                            res_ReportNumber = re.findall (reg_str,data)
                            ReportNumber = res_ReportNumber
                            print("ReportNumber@@@@@@@@@@@@@@@@@@@@@@@",ReportNumber)
                            if ReportNumber:
                                dct['ReportNumber'] = ReportNumber[0]
                                print("ReportNumber#########",ReportNumber)

                            


                            tag_enqname = "Enquiry_Reason"
                            reg_str = "<" + tag_enqname + ">(.*?)</" + tag_enqname + ">"
                            res_Enquiry_Reason = re.findall (reg_str,data)
                            Enquiry_Reason = res_Enquiry_Reason
                            if Enquiry_Reason:
                                dct['Enquiry_Reason'] = Enquiry_Reason[0]
                                print("Enquiry_Reason#########",Enquiry_Reason)

                            tag_finpurpose = "Finance_Purpose"
                            reg_str ="<" + tag_finpurpose + ">(.*?)</" + tag_finpurpose + ">"
                            res_Finance_Purpose = re.findall (reg_str,data)
                            Finance_Purpose = res_Finance_Purpose
                            if Finance_Purpose:
                                dct['Finance_Purpose'] = Finance_Purpose[0]
                                print("Finance_Purpose#########",Finance_Purpose)

                            tag_acfinance = "Amount_Financed"
                            reg_str = "<" + tag_acfinance + ">(.*?)</" + tag_acfinance + ">"
                            res_Amount_Financed = re.findall (reg_str,data)
                            Amount_Financed = res_Amount_Financed
                            print("Amount_Financed@@@@@@@@@@@@@@@@@@@@",Amount_Financed)
                            if Amount_Financed:
                                dct['Amount_Financed'] = Amount_Financed[0]
                                print("Amount_Financed#########",Amount_Financed)

                            tag_agdur = "Duration_Of_Agreement"
                            reg_str = "<" + tag_agdur + ">(.*?)</" + tag_agdur + ">" 
                            res_Duration_Of_Agreement = re.findall (reg_str,data) 
                            Duration_Of_Agreement = res_Duration_Of_Agreement
                            if Duration_Of_Agreement:
                                dct['Duration_Of_Agreement'] = Duration_Of_Agreement[0]
                                print("Duration_Of_Agreement#########",Duration_Of_Agreement)



                            tag_md1 ="Middle_Name1"
                            reg_str = "<" + tag_md1 + ">(.*?)</" + tag_md1 + ">"
                            res_Middle_Name1 = re.findall(reg_str,data)
                            Middle_Name1 = res_Middle_Name1
                            if Middle_Name1:
                                dct['Middle_Name1'] = Middle_Name1[0]
                                print("Middle_Name1#########",Middle_Name1)

                            tag_md2 ="Middle_Name2"
                            reg_str = "<" + tag_md2 + ">(.*?)</" + tag_md2 + ">"
                            res_Middle_Name2 = re.findall(reg_str,data)
                            Middle_Name2 = res_Middle_Name2
                            if Middle_Name2:
                                dct['Middle_Name2'] = Middle_Name2[0]
                                print("Middle_Name2#########",Middle_Name2)

                            tag_md3 ="Middle_Name3"
                            reg_str = "<" + tag_md3 + ">(.*?)</" + tag_md3 + ">"
                            res_Middle_Name3 = re.findall(reg_str,data)
                            Middle_Name3 = res_Middle_Name3
                            if Middle_Name3:
                                dct['Middle_Name3'] = Middle_Name3[0]
                                print("Middle_Name3#########",Middle_Name3)

                            tag_gcode = "Gender_Code"
                            reg_str = "<" + tag_gcode + ">(,*?)</" + tag_gcode + ">"
                            res_Gender_Code = re.findall(reg_str,data)
                            Gender_Code = res_Gender_Code
                            print("Gender_Code@@@@@@@@@@@@@@@@@@@@",Gender_Code)
                            if Gender_Code:
                                dct['Gender_Code'] = Gender_Code[0]
                                print("Gender_Code#########",Gender_Code)


                            tag_pan = "IncomeTaxPan"
                            reg_str = "<" + tag_pan + ">(.*?)</" + tag_pan + ">"
                            res_IncomeTaxPan = re.findall(reg_str,data)
                            IncomeTaxPan = res_IncomeTaxPan
                            print("IncomeTaxPan#@@@@@@@@@@@@@@@@@@@@@@@",IncomeTaxPan)
                            if IncomeTaxPan:
                                dct['IncomeTaxPan'] = IncomeTaxPan[0]
                                print("IncomeTaxPan#########",IncomeTaxPan)

                            tag_pandt = "PAN_Issue_Date"
                            reg_str = "<" + tag_pandt + ">(.*?)</" + tag_pandt + ">"
                            res_PAN_Issue_Date = re.findall(reg_str,data)
                            PAN_Issue_Date = res_PAN_Issue_Date
                            if PAN_Issue_Date:
                                dct['PAN_Issue_Date'] = self._format_date_change(PAN_Issue_Date[0])
                                print("PAN_Issue_Date#########",PAN_Issue_Date)

                            tag_expdt = "PAN_Expiration_Date"
                            reg_str = "<" +tag_expdt + ">(.*?)</" + tag_expdt + ">"
                            res_PAN_Expiration_Date = re.findall(reg_str,data)
                            PAN_Expiration_Date = res_PAN_Expiration_Date
                            if PAN_Expiration_Date:
                                dct['PAN_Expiration_Date'] = self._format_date_change(PAN_Expiration_Date[0])
                                print("PAN_Expiration_Date#########",PAN_Expiration_Date)

                            tag_pno = "Passport_number"
                            reg_str = "<" + tag_pno + ">(.*?)</" + tag_pno + ">"
                            res_Passport_number = re.findall(reg_str,data)
                            Passport_number = res_Passport_number
                            if Passport_number:
                                dct['Passport_number'] = Passport_number[0]
                                print("Passport_number#########",Passport_number)

                            tag_pidt = "Passport_Issue_Date"
                            reg_str = "<" + tag_pidt + ">(.*?)</" + tag_pidt + ">"
                            res_Passport_Issue_Date = re.findall(reg_str, data)
                            Passport_Issue_Date = res_Passport_Issue_Date
                            if Passport_Issue_Date:
                                dct['Passport_Issue_Date'] = self._format_date_change(Passport_Issue_Date[0])
                                print("Passport_Issue_Date#########",Passport_Issue_Date)

                            tag_pxpdt = "Passport_Expiration_Date"
                            reg_str = "<" +tag_pxpdt + ">(.*?)</" + tag_pxpdt + ">"
                            res_Passport_Expiration_Date = re.findall(reg_str,data)
                            Passport_Expiration_Date = res_Passport_Expiration_Date
                            if Passport_Expiration_Date:
                                dct['Passport_Expiration_Date'] = self._format_date_change(Passport_Expiration_Date[0])
                                print("Passport_Expiration_Date#########",Passport_Expiration_Date)

                            tag_vidc = "Voter_s_Identity_Card"
                            reg_str = "<" +tag_vidc + ">(.*?)</" + tag_vidc + ">"
                            res_Voter_s_Identity_Card = re.findall(reg_str,data)
                            Voter_s_Identity_Card = res_Voter_s_Identity_Card
                            if Voter_s_Identity_Card:
                                dct['Voter_s_Identity_Card'] = Voter_s_Identity_Card[0]
                                print("Voter_s_Identity_Card#########",Voter_s_Identity_Card)

                            tag_vidissue = "Voter_ID_Issue_Date"
                            reg_str ="<" + tag_vidissue + ">(.*?)</" + tag_vidissue + ">"
                            res_Voter_ID_Issue_Date = re.findall(reg_str,data)
                            Voter_ID_Issue_Date = res_Voter_ID_Issue_Date
                            if Voter_ID_Issue_Date:
                                dct['Voter_ID_Issue_Date'] = self._format_date_change(Voter_ID_Issue_Date[0])
                                print("Voter_ID_Issue_Date#########",Voter_ID_Issue_Date)

                            tag_videxp = "Voter_ID_Expiration_Date"
                            reg_str = "<" + tag_videxp + ">(.*?)</" + tag_videxp + ">"
                            res_Voter_ID_Expiration_Date = re.findall(reg_str,data)
                            Voter_ID_Expiration_Date = res_Voter_ID_Expiration_Date
                            if Voter_ID_Expiration_Date:
                                dct['Voter_ID_Expiration_Date'] = self._format_date_change(Voter_ID_Expiration_Date[0])
                                print("Voter_ID_Expiration_Date#########",Voter_ID_Expiration_Date)

                            tag_dlno = "Driver_License_Number"
                            reg_str = "<" + tag_dlno + ">(.*?)</" + tag_dlno + ">"
                            res_Driver_License_Number = re.findall(reg_str,data)
                            Driver_License_Number = res_Driver_License_Number
                            if Driver_License_Number:
                                dct['Driver_License_Number'] = Driver_License_Number[0]
                                print("Driver_License_Number#########",Driver_License_Number)

                            tag_dldt = "Driver_License_Issue_Date"
                            reg_str = "<" + tag_dldt + ">(.*?)</" + tag_dldt + ">"
                            res_Driver_License_Issue_Date = re.findall(reg_str,data)
                            Driver_License_Issue_Date = res_Driver_License_Issue_Date
                            if Driver_License_Issue_Date:
                                dct['Driver_License_Issue_Date'] = self._format_date_change(Driver_License_Issue_Date[0])
                                print("Driver_License_Issue_Date#########",Driver_License_Issue_Date)

                            tag_dlexpdt = "Driver_License_Expiration_Date"
                            reg_str = "<" + tag_dlexpdt + ">(.*?)</" + tag_dlexpdt + ">"
                            res_Driver_License_Expiration_Date = re.findall(reg_str,data)
                            Driver_License_Expiration_Date = res_Driver_License_Expiration_Date
                            if Driver_License_Expiration_Date:
                                dct['Driver_License_Expiration_Date'] = self._format_date_change(Driver_License_Expiration_Date[0])
                                print("Driver_License_Expiration_Date#########",Driver_License_Expiration_Date)

                            tag_rtncrd = "Ration_Card_Number"
                            reg_str = "<" + tag_rtncrd + ">(.*?)</" + tag_rtncrd + ">"
                            res_Ration_Card_Number = re.findall(reg_str,data)
                            Ration_Card_Number = res_Ration_Card_Number
                            if Ration_Card_Number:
                                dct['Ration_Card_Number'] = Ration_Card_Number[0]
                                print("Ration_Card_Number#########",Ration_Card_Number)

                            tag_rtcrdt = "Ration_Card_Issue_Date"
                            reg_str = "<" + tag_rtcrdt + ">(.*?)</" + tag_rtcrdt + ">"
                            res_Ration_Card_Issue_Date = re.findall(reg_str,data)
                            Ration_Card_Issue_Date = res_Ration_Card_Issue_Date
                            if Ration_Card_Issue_Date:
                                dct['Ration_Card_Issue_Date'] = self._format_date_change(Ration_Card_Issue_Date[0])
                                print("Ration_Card_Issue_Date#########",Ration_Card_Issue_Date)

                            tag_rtncrdexp = "Ration_Card_Expiration_Date"
                            reg_str = "<" + tag_rtncrdexp + ">(.*?)</" + tag_rtncrdexp + ">"
                            res_Ration_Card_Expiration_Date = re.findall(reg_str,data)
                            Ration_Card_Expiration_Date = res_Ration_Card_Expiration_Date
                            if Ration_Card_Expiration_Date:
                                dct['Ration_Card_Expiration_Date'] = self._format_date_change(Ration_Card_Expiration_Date[0])
                                print("Ration_Card_Expiration_Date#########",Ration_Card_Expiration_Date)

                            tag_unividno = "Universal_ID_Number"
                            reg_str = "<" + tag_unividno + ">(.*?)</" + tag_unividno + ">"
                            res_Universal_ID_Number = re.findall(reg_str,data)
                            Universal_ID_Number = res_Universal_ID_Number
                            if Universal_ID_Number:
                                dct['Universal_ID_Number'] = self._format_date_change(Universal_ID_Number[0])
                                print("Universal_ID_Number#########",Universal_ID_Number)

                            tag_unividdet = "Universal_ID_Issue_Date"
                            reg_str ="<" + tag_unividdet + ">(.*?)</" + tag_unividdet + ">"
                            res_Universal_ID_Issue_Date = re.findall(reg_str,data)
                            Universal_ID_Issue_Date = res_Universal_ID_Issue_Date
                            if Universal_ID_Issue_Date:
                                dct['Universal_ID_Issue_Date'] = self._format_date_change(Universal_ID_Issue_Date[0])
                                print("Universal_ID_Issue_Date#########",Universal_ID_Issue_Date)


                            tag_univexp ="Universal_ID_Expiration_Date"
                            reg_str = "<" + tag_univexp + ">(.*?)</" + tag_univexp + ">"
                            res_Universal_ID_Expiration_Date = re.findall(reg_str,data)
                            Universal_ID_Expiration_Date = res_Universal_ID_Expiration_Date
                            if Universal_ID_Expiration_Date:
                                dct['Universal_ID_Expiration_Date'] = self._format_date_change(Universal_ID_Expiration_Date[0])
                                print("Universal_ID_Expiration_Date#########",Universal_ID_Expiration_Date)

                            tag_dobap ="Date_Of_Birth_Applicant"
                            reg_str = "<" + tag_dobap + ">(.*?)</" + tag_dobap + ">"
                            res_Date_Of_Birth_Applicant = re.findall(reg_str,data)
                            Date_Of_Birth_Applicant = res_Date_Of_Birth_Applicant
                            if Date_Of_Birth_Applicant:
                                dct['Date_Of_Birth_Applicant'] = self._format_date_change(Date_Of_Birth_Applicant[0])
                                print("Date_Of_Birth_Applicant#########",Date_Of_Birth_Applicant)

                            tag_tna1 = "Telephone_Number_Applicant_1st"
                            reg_str = "<" + tag_tna1 + ">(.*?)</" + tag_tna1 + ">"
                            res_Telephone_Number_Applicant_1st = re.findall(reg_str,data)
                            Telephone_Number_Applicant_1st = res_Telephone_Number_Applicant_1st
                            if Telephone_Number_Applicant_1st:
                                dct['Telephone_Number_Applicant_1st'] = self._format_date_change(Telephone_Number_Applicant_1st[0])
                                print("Telephone_Number_Applicant_1st#########",Telephone_Number_Applicant_1st)


                            tag_tpext = "Telephone_Extension"
                            reg_str = "<" + tag_tpext + ">(.*?)</" + tag_tpext + ">"
                            res_Telephone_Extension = re.findall(reg_str,data)
                            Telephone_Extension = res_Telephone_Extension
                            if Telephone_Extension:
                                dct['Telephone_Extension'] = Telephone_Extension[0]
                                print("Telephone_Extension#########",Telephone_Extension)

                            tag_ttyp = "Telephone_Type"                                   
                            reg_str = "<" + tag_ttyp + ">(.*?)</" + tag_ttyp + ">"
                            res_Telephone_Type = re.findall(reg_str,data)
                            Telephone_Type = res_Telephone_Type
                            if Telephone_Type:
                                dct['Telephone_Type'] = Telephone_Type[0]
                                print("Telephone_Type#########",Telephone_Type)

                            tag_mphno = "MobilePhoneNumber"
                            reg_str = "<" + tag_mphno + ">(.*?)</" + tag_mphno + ">"
                            res_MobilePhoneNumber = re.findall(reg_str,data)
                            MobilePhoneNumber = res_MobilePhoneNumber
                            if MobilePhoneNumber:
                                dct['MobilePhoneNumber'] = MobilePhoneNumber[0]
                                print("MobilePhoneNumber#########",MobilePhoneNumber)

                            tag_mailid = "EMailId"
                            reg_str = "<" + tag_mailid + ">(.*?)</" + tag_mailid + ">"
                            res_EMailId = re.findall(reg_str,data)
                            EMailId = res_EMailId
                            if EMailId:
                                dct['EMailId'] = EMailId[0]
                                print("EMailId#########",EMailId)


                            tag_dttre = "Date_of_Request"
                            reg_str = "<" + tag_dttre + ">(.*?)</" + tag_dttre + ">"
                            res_Date_of_Request = re.findall(reg_str,data)
                            Date_of_Request = res_Date_of_Request
                            if Date_of_Request:
                                dct['Date_of_Request'] = self._format_date_change(Date_of_Request[0])
                                print("Date_of_Request#########",Date_of_Request)


                            tag_incm = "Income"
                            reg_str = "<" + tag_incm + ">(.*?)</" + tag_incm + ">"
                            res_Income = re.findall(reg_str,data)
                            Income = res_Income
                            if Income:
                                dct['Income'] = Income[0]
                                print("Income#########",Income)

                            tag_mts = "Marital_Status"
                            reg_str = "<" + tag_mts + ">(.*?)</" + tag_mts + ">"
                            res_Marital_Status = re.findall(reg_str,data)
                            Marital_Status = res_Marital_Status
                            if Marital_Status:
                                dct['Marital_Status'] = Marital_Status[0]
                                print("Marital_Status#########",Marital_Status)

                            tag_empst = "Employment_Status"
                            reg_str = "<" + tag_empst + ">(.*?)</" + tag_empst + ">"
                            res_Employment_Status = re.findall(reg_str,data)
                            Employment_Status = res_Employment_Status
                            if Employment_Status:
                                dct['Employment_Status'] = Employment_Status[0]
                                print("Employment_Status#########",Employment_Status)

                            tag_timewemp = "Time_with_Employer"
                            reg_str = "<" + tag_timewemp + ">(.*?)</" + tag_timewemp + ">"
                            res_Time_with_Employer = re.findall(reg_str,data)
                            Time_with_Employer = res_Time_with_Employer
                            if Time_with_Employer:
                                dct['Time_with_Employer'] = Time_with_Employer[0]
                                print("Time_with_Employer#########",Time_with_Employer)

                            tag_nofcd = "Number_of_Major_Credit_Card_Held"
                            reg_str = "<" + tag_nofcd + ">(.*?)</" + tag_nofcd + ">"
                            res_Number_of_Major_Credit_Card_Held = re.findall(reg_str,data)
                            Number_of_Major_Credit_Card_Held = res_Number_of_Major_Credit_Card_Held
                            if Number_of_Major_Credit_Card_Held:
                                dct['Number_of_Major_Credit_Card_Held'] = Number_of_Major_Credit_Card_Held[0]
                                print("Number_of_Major_Credit_Card_Held#########",Number_of_Major_Credit_Card_Held)

                            tag_fnpnhn = "FlatNoPlotNoHouseNo"
                            reg_str = "<" + tag_fnpnhn + ">(.*?)</" + tag_fnpnhn + ">"
                            res_FlatNoPlotNoHouseNo = re.findall(reg_str,data)
                            FlatNoPlotNoHouseNo = res_FlatNoPlotNoHouseNo
                            if FlatNoPlotNoHouseNo:
                                dct['FlatNoPlotNoHouseNo'] = FlatNoPlotNoHouseNo[0]
                                print("FlatNoPlotNoHouseNo#########",FlatNoPlotNoHouseNo)

                            tag_bnsn = "BldgNoSocietyName"
                            reg_str = "<" + tag_bnsn + ">(.*?)</" + tag_bnsn + ">"
                            res_BldgNoSocietyName = re.findall(reg_str,data)
                            BldgNoSocietyName = res_BldgNoSocietyName
                            if BldgNoSocietyName:
                                dct['BldgNoSocietyName'] = BldgNoSocietyName[0]
                                print("BldgNoSocietyName#########",BldgNoSocietyName)

                            tag_rnal = "RoadNoNameAreaLocality"
                            reg_str = "<" + tag_rnal + ">(.*?)</" + tag_rnal + ">"
                            res_RoadNoNameAreaLocality = re.findall(reg_str,data)
                            RoadNoNameAreaLocality = res_RoadNoNameAreaLocality
                            if RoadNoNameAreaLocality:
                                dct['RoadNoNameAreaLocality'] = RoadNoNameAreaLocality[0]
                                print("RoadNoNameAreaLocality#########",RoadNoNameAreaLocality)

                            tag_cty = "City"
                            reg_str = "<" + tag_cty + ">(.*?)</" + tag_cty + ">"
                            res_City = re.findall(reg_str,data)
                            City = res_City
                            if City:
                                dct['City'] = City[0]
                                print("City#########",City)

                            tag_lmk = "Landmark"
                            reg_str = "<" + tag_lmk + ">(.*?)</" + tag_lmk + ">"
                            res_Landmark = re.findall(reg_str,data)
                            Landmark = res_Landmark
                            if Landmark:
                                dct['Landmark'] = Landmark[0]
                                print("Landmark#########",Landmark)

                            tag_stte= "State"
                            reg_str = "<" + tag_stte + ">(.*?)</" + tag_stte + ">"
                            res_State = re.findall(reg_str,data)
                            State = res_State
                            if State:
                                dct['State'] = State[0]
                                print("State#########",State)

                            tag_pco = "PINCode"
                            reg_str = "<" + tag_pco + ">(.*?)</" + tag_pco + ">"
                            res_PINCode = re.findall(reg_str,data)
                            PINCode = res_PINCode
                            if PINCode:
                                dct['PINCode'] = PINCode[0]
                                print("PINCode#########",PINCode)

                            tag_ccode = "Country_Code"
                            reg_str = "<" + tag_ccode + ">(.*?)</" + tag_ccode + ">"
                            res_Country_Code = re.findall(reg_str,data)
                            Country_Code = res_Country_Code
                            if Country_Code:
                                dct['Country_Code'] = Country_Code[0]
                                print("Country_Code#########",Country_Code)

                            # tag_cadeta = "Current_Application_Details"
                            # reg_str = "<" + tag_cadeta + ">(.*?)</" + tag_cadeta + ">"
                            # res_Current_Application_Details = re.findall(reg_str,data)
                            # Current_Application_Details = res_Current_Application_Details
                            # print("Current_Application_Details#########",Current_Application_Details)

                            tag_cadsfcb="CADSuitFiledCurrentBalance"
                            reg_str = "<" + tag_cadsfcb + ">(.*?)</" + tag_cadsfcb + ">"
                            res_CADSuitFiledCurrentBalance = re.findall(reg_str,data)
                            CADSuitFiledCurrentBalance = res_CADSuitFiledCurrentBalance
                            print("CADSuitFiledCurrentBalance@@@@@@@@@@@@@@@@",CADSuitFiledCurrentBalance)
                            if CADSuitFiledCurrentBalance:
                                dct['CADSuitFiledCurrentBalance'] = CADSuitFiledCurrentBalance[0]
                                print("CADSuitFiledCurrentBalance#########",CADSuitFiledCurrentBalance)

                            tag_cactive = "CreditAccountActive"
                            reg_str = "<" + tag_cactive + ">(.*?)</" + tag_cactive + ">"
                            res_CreditAccountActive = re.findall(reg_str,data)
                            CreditAccountActive = res_CreditAccountActive
                            if CreditAccountActive:
                                dct['CreditAccountActive'] = CreditAccountActive[0]
                                print("CreditAccountActive#########",CreditAccountActive)

                            tag_cclose = "CreditAccountClosed"
                            reg_str = "<" + tag_cclose + ">(.*?)</" + tag_cclose + ">"
                            res_CreditAccountClosed = re.findall(reg_str,data)
                            CreditAccountClosed = res_CreditAccountClosed
                            if CreditAccountClosed:
                                dct['CreditAccountClosed'] = CreditAccountClosed[0]
                                print("CreditAccountClosed#########",CreditAccountClosed)

                            tag_cadefault = "CreditAccountDefault"
                            reg_str_CreditAccountDefault = "<" + tag_cadefault + ">(.*?)</" + tag_cadefault + ">"
                            res_CreditAccountDefault = re.findall(reg_str_CreditAccountDefault,data)
                            CreditAccountDefault = res_CreditAccountDefault
                            if CreditAccountDefault:
                                dct['CreditAccountDefault'] = CreditAccountDefault[0]
                                print("CreditAccountDefault#########",CreditAccountDefault)

                            tag_catotal = "CreditAccountTotal"
                            reg_str = "<" + tag_catotal + ">(.*?)</" + tag_catotal + ">"
                            res_CreditAccountTotal = re.findall(reg_str,data)
                            CreditAccountTotal = res_CreditAccountTotal
                            if CreditAccountTotal:
                                dct['CreditAccountTotal'] = CreditAccountTotal[0]
                                print("CreditAccountTotal#########",CreditAccountTotal)

                            tag_outbalsec = "Outstanding_Balance_Secured"
                            reg_str = "<" + tag_outbalsec + ">(.*?)</" + tag_outbalsec + ">"
                            res_Outstanding_Balance_Secured = re.findall(reg_str,data)
                            Outstanding_Balance_Secured = res_Outstanding_Balance_Secured
                            if Outstanding_Balance_Secured:
                                dct['Outstanding_Balance_Secured'] = Outstanding_Balance_Secured[0]
                                print("Outstanding_Balance_Secured#########",Outstanding_Balance_Secured)

                            tag_outbalsecper = "Outstanding_Balance_Secured_Percentage"
                            reg_str = "<" + tag_outbalsecper + ">(.*?)</" + tag_outbalsecper + ">"
                            res_Outstanding_Balance_Secured_Percentage = re.findall(reg_str,data)
                            Outstanding_Balance_Secured_Percentage = res_Outstanding_Balance_Secured_Percentage
                            if Outstanding_Balance_Secured_Percentage:
                                dct['Outstanding_Balance_Secured_Percentage'] = Outstanding_Balance_Secured_Percentage[0]
                                print("Outstanding_Balance_Secured_Percentage#########",Outstanding_Balance_Secured_Percentage)
                            
                            tag_outbaluns = "Outstanding_Balance_UnSecured"
                            reg_str = "<" + tag_outbaluns + ">(.*?)</" + tag_outbaluns + ">"
                            res_Outstanding_Balance_UnSecured = re.findall(reg_str,data)
                            Outstanding_Balance_UnSecured = res_Outstanding_Balance_UnSecured
                            if Outstanding_Balance_UnSecured:
                                dct['Outstanding_Balance_UnSecured'] = Outstanding_Balance_UnSecured[0]
                                print("Outstanding_Balance_UnSecured#########",Outstanding_Balance_UnSecured)

                            tag_obup = "Outstanding_Balance_UnSecured_Percentage"
                            reg_str = "<" + tag_obup + ">(.*?)</" + tag_obup + ">"
                            res_Outstanding_Balance_UnSecured_Percentage = re.findall(reg_str,data)
                            Outstanding_Balance_UnSecured_Percentage = res_Outstanding_Balance_UnSecured_Percentage
                            if Outstanding_Balance_UnSecured_Percentage:
                                dct['Outstanding_Balance_UnSecured_Percentage'] = Outstanding_Balance_UnSecured_Percentage[0]
                                print("Outstanding_Balance_UnSecured_Percentage#########",Outstanding_Balance_UnSecured_Percentage)


                            tag_oball = "Outstanding_Balance_All"
                            reg_str = "<" + tag_oball + ">(.*?)</" + tag_oball + ">"
                            res_Outstanding_Balance_All = re.findall(reg_str,data)
                            Outstanding_Balance_All=res_Outstanding_Balance_All
                            if Outstanding_Balance_All:
                                dct['Outstanding_Balance_All'] = Outstanding_Balance_All[0]
                                print("Outstanding_Balance_All#########",Outstanding_Balance_All)

                            tag_idno = "Identification_Number"
                            reg_str = "<" + tag_oball + ">(.*?)</" + tag_oball + ">"
                            res_Identification_Number = re.findall(reg_str,data)
                            Identification_Number = res_Identification_Number
                            if Identification_Number:
                                dct['Identification_Number'] = Identification_Number[0]
                                print("Identification_Number#########",Identification_Number)

                            tag_sbsnme="Subscriber_Name"
                            reg_str = "<" + tag_sbsnme + ">(.*?)</" + tag_sbsnme + ">"
                            res_Subscriber_Name = re.findall(reg_str,data)
                            Subscriber_Name = res_Subscriber_Name
                            print("Subscriber_Name@@@@@@@@@@@@@@",Subscriber_Name)
                            if Subscriber_Name:
                                dct['Subscriber_Name'] = Subscriber_Name[0]
                                print("Subscriber_Name#########",Subscriber_Name)

                            tag_subname = "Subscriber_Name"
                            reg_str ="</Identification_Number><" + tag_subname + ">(.*?)</" + tag_subname + ">"
                            res_Subscriber_Name = re.findall (reg_str,data)
                            Subscriber_Name = res_Subscriber_Name
                            print("Subscriber_Name@@@@@@@@@@@@@@@@@",Subscriber_Name)
                            if Subscriber_Name:
                                dct['Subscriber_Name'] = Subscriber_Name[0]
                                print("Subscriber_Name#########",Subscriber_Name)


                            tag_jjjj = "Subscriber_Name"
                            reg_str ="</Subscriber_code><" + tag_jjjj + ">(.*?)</" + tag_jjjj + ">"
                            res_jjjj = re.findall (reg_str,data)
                            jjjj = res_jjjj
                            if jjjj:
                                dct['Subscriber_Name'] = jjjj[0]
                                print("Subscriber_Name#########",jjjj)     



                            tag_ptype = "Portfolio_Type"
                            res_str = "<" + tag_ptype + ">(.*?)</" + tag_ptype + ">"
                            res_Portfolio_Type = re.findall(res_str,data)
                            Portfolio_Type = res_Portfolio_Type
                            print("Portfolio_Type@@@@@@@@@@@@@@@@",Portfolio_Type)
                            if Portfolio_Type:
                                dct['Portfolio_Type'] = Portfolio_Type[0]
                                print("Portfolio_Type#########",Portfolio_Type)

                            tag_acctype = "Account_Type"
                            reg_str = "<" + tag_acctype + ">(.*?)</" + tag_acctype + ">"
                            res_Account_Type = re.findall(reg_str,data)
                            Account_Type = res_Account_Type
                            if Account_Type:
                                dct['Account_Type'] = Account_Type[0]
                                print("Account_Type#########",Account_Type) 

                            tag_dtrpt="Date_Reported"
                            reg_str = "<" + tag_dtrpt + ">(.*?)</" + tag_dtrpt + ">"
                            res_Date_Reported = re.findall(reg_str,data)
                            Date_Reported = res_Date_Reported
                            if Date_Reported:
                                dct['Date_Reported'] = self._format_date_change(Date_Reported[0])
                                print("Date_Reported#########",Date_Reported)   

                            
                                
                            tag_acstatus = "Account_Status"
                            reg_str = "<" + tag_acstatus + ">(.*?)</" + tag_acstatus + ">"
                            res_Account_Status = re.findall(reg_str,data)
                            Account_Status = res_Account_Status
                            if Account_Status:
                                dct['Account_Status'] = Account_Status[0]
                                print("Account_Status#########",Account_Status)            

                            


                            tag_hcoalt = "Highest_Credit_or_Original_Loan_Amount"
                            reg_str ="<" + tag_hcoalt + ">(.*?)</" + tag_hcoalt + ">"
                            res_Highest_Credit_or_Original_Loan_Amount = re.findall(reg_str,data)
                            Highest_Credit_or_Original_Loan_Amount = res_Highest_Credit_or_Original_Loan_Amount
                            if Highest_Credit_or_Original_Loan_Amount:
                                dct['Highest_Credit_or_Original_Loan_Amount'] = Highest_Credit_or_Original_Loan_Amount[0]
                                print("Highest_Credit_or_Original_Loan_Amount#########",Highest_Credit_or_Original_Loan_Amount)

                            tag_opdt = "Open_Date"
                            reg_str = "<" + tag_opdt + ">(.*?)</" + tag_opdt + ">"
                            res_Open_Date = re.findall(reg_str,data)
                            Open_Date = res_Open_Date
                            if Open_Date:
                                dct['Open_Date'] = self._format_date_change(Open_Date[0])
                                print("Open_Date#########",Open_Date)

                            tag_clam = "Credit_Limit_Amount"
                            reg_str = "<"+ tag_clam + ">(.*?)</" + tag_clam + ">"
                            res_Credit_Limit_Amount = re.findall(reg_str,data)
                            Credit_Limit_Amount = res_Credit_Limit_Amount
                            if Credit_Limit_Amount:
                                dct['Credit_Limit_Amount'] = Credit_Limit_Amount[0]
                                print("Credit_Limit_Amount#########",Credit_Limit_Amount)

                            
                            tag_hcoalt = "Highest_Credit_or_Original_Loan_Amount"
                            reg_str ="<" + tag_hcoalt + ">(.*?)</" + tag_hcoalt + ">"
                            res_Highest_Credit_or_Original_Loan_Amount = re.findall(reg_str,data)
                            Highest_Credit_or_Original_Loan_Amount = res_Highest_Credit_or_Original_Loan_Amount
                            if Highest_Credit_or_Original_Loan_Amount:
                                dct['Highest_Credit_or_Original_Loan_Amount'] = Highest_Credit_or_Original_Loan_Amount[0]
                                print("Highest_Credit_or_Original_Loan_Amount#########",Highest_Credit_or_Original_Loan_Amount)

                            tag_trmdur = "Terms_Duration"
                            reg_str = "<" + tag_trmdur + ">(.*?)</" + tag_trmdur + ">"
                            res_Terms_Duration = re.findall(reg_str,data)
                            Terms_Duration = res_Terms_Duration
                            if Terms_Duration:
                                dct['Terms_Duration'] = Terms_Duration[0]
                                print("Terms_Duration#########",Terms_Duration)

                            tag_trmfrq = "Terms_Frequency"
                            reg_str = "<" + tag_trmfrq + ">(.*?)</" + tag_trmfrq + ">"
                            res_Terms_Frequency = re.findall(reg_str,data)
                            Terms_Frequency = res_Terms_Frequency
                            if Terms_Frequency:
                                dct['Terms_Frequency'] = Terms_Frequency[0]
                                print("Terms_Frequency#########",Terms_Frequency)

                            tag_smpm = "Scheduled_Monthly_Payment_Amount"
                            reg_str = "<" + tag_smpm + ">(.*?)</" + tag_smpm + ">"
                            res_Scheduled_Monthly_Payment_Amount = re.findall(reg_str,data)
                            Scheduled_Monthly_Payment_Amount = res_Scheduled_Monthly_Payment_Amount
                            if Scheduled_Monthly_Payment_Amount:
                                dct['Scheduled_Monthly_Payment_Amount'] = Scheduled_Monthly_Payment_Amount[0]
                                print("Scheduled_Monthly_Payment_Amount#########",Scheduled_Monthly_Payment_Amount)

                            

                            tag_pmtrt = "Payment_Rating"
                            reg_str = "<" + tag_pmtrt + ">(.*?)</" + tag_pmtrt + ">"
                            res_Payment_Rating = re.findall(reg_str,data)
                            Payment_Rating = res_Payment_Rating
                            if Payment_Rating:
                                dct['Payment_Rating'] = Payment_Rating[0]
                                print("Payment_Rating#########",Payment_Rating)

                            tag_pmthisp ="Payment_History_Profile"
                            reg_str =  "<" + tag_pmthisp + ">(.*?)</" + tag_pmthisp + ">"
                            res_Payment_History_Profile = re.findall(reg_str,data)
                            Payment_History_Profile = res_Payment_History_Profile
                            if Payment_History_Profile:
                                dct['Payment_History_Profile'] = Payment_History_Profile[0]
                                print("Payment_History_Profile#########",Payment_History_Profile)

                            tag_spcmt = "Special_Comment"
                            reg_str = "<" + tag_spcmt + ">(.*?)</" + tag_spcmt + ">"
                            res_Special_Comment = re.findall(reg_str,data)
                            Special_Comment = res_Special_Comment
                            if Special_Comment:
                                dct['Special_Comment'] = Special_Comment[0]
                                print("Special_Comment#########",Special_Comment)


                            tag_crbal = "Current_Balance"
                            reg_str = "<" + tag_crbal + ">(.*?)</" + tag_crbal + ">"
                            res_Current_Balance = re.findall(reg_str,data)
                            Current_Balance = res_Current_Balance
                            if Current_Balance:
                                dct['Current_Balance'] = Current_Balance[0]
                                print("Current_Balance#########",Current_Balance)

                            tag_amtpdue = "Amount_Past_Due"
                            reg_str = "<" + tag_amtpdue + ">(.*?)</" + tag_amtpdue + ">"
                            res_Amount_Past_Due = re.findall(reg_str,data)
                            Amount_Past_Due = res_Amount_Past_Due
                            if Amount_Past_Due:
                                dct['Amount_Past_Due'] = Amount_Past_Due[0]
                                print("Amount_Past_Due#########",Amount_Past_Due)

                            tag_ocoa = "Original_Charge_Off_Amount"
                            reg_str = "<" + tag_ocoa + ">(.*?)</" + tag_ocoa + ">"
                            res_Original_Charge_Off_Amount = re.findall(reg_str,data)
                            Original_Charge_Off_Amount = res_Original_Charge_Off_Amount
                            if Original_Charge_Off_Amount:
                                dct['Original_Charge_Off_Amount'] = Original_Charge_Off_Amount[0]
                                print("Original_Charge_Off_Amount#########",Original_Charge_Off_Amount)

                            

                            tag_dofd = "Date_of_First_Delinquency"
                            reg_str = "<" + tag_dofd + ">(.*?)</" + tag_dofd + ">"
                            res_Date_of_First_Delinquency = re.findall(reg_str,data)
                            Date_of_First_Delinquency = res_Date_of_First_Delinquency
                            if Date_of_First_Delinquency:
                                dct['Date_of_First_Delinquency'] = self._format_date_change(Date_of_First_Delinquency[0])
                                print("Date_of_First_Delinquency#########",Date_of_First_Delinquency)

                            tag_dtcd = "Date_Closed"
                            reg_str = "<" + tag_dtcd + ">(.*?)</" + tag_dtcd + ">"
                            res_Date_Closed = re.findall(reg_str,data)
                            Date_Closed = res_Date_Closed
                            if Date_Closed:
                                dct['Date_Closed'] = self._format_date_change(Date_Closed[0])
                                print("Date_Closed#########",Date_Closed)

                            tag_dolp = "Date_of_Last_Payment"
                            reg_str = "<" + tag_dolp + ">(.*?)</" + tag_dolp + ">"
                            res_Date_of_Last_Payment = re.findall(reg_str,data)
                            Date_of_Last_Payment = res_Date_of_Last_Payment
                            if Date_of_Last_Payment:
                                dct['Date_of_Last_Payment'] = self._format_date_change(Date_of_Last_Payment[0])
                                print("Date_of_Last_Payment#########",Date_of_Last_Payment)

                            tag_suitf="SuitFiledWillfulDefaultWrittenOffStatus"
                            reg_str = "<" + tag_suitf + ">(.*?)</" + tag_suitf + ">"
                            res_SuitFiledWillfulDefaultWrittenOffStatus = re.findall(reg_str,data)
                            SuitFiledWillfulDefaultWrittenOffStatus = res_SuitFiledWillfulDefaultWrittenOffStatus
                            if SuitFiledWillfulDefaultWrittenOffStatus:
                                dct['SuitFiledWillfulDefaultWrittenOffStatus'] = SuitFiledWillfulDefaultWrittenOffStatus[0]
                                print("SuitFiledWillfulDefaultWrittenOffStatus#########",SuitFiledWillfulDefaultWrittenOffStatus)

                            tag_suitwd = "SuitFiled_WilfulDefault"
                            reg_str = "<" + tag_suitwd + ">(.*?)</" + tag_suitwd + ">"
                            res_SuitFiled_WilfulDefault = re.findall(reg_str, data)
                            SuitFiled_WilfulDefault = res_SuitFiled_WilfulDefault
                            if SuitFiled_WilfulDefault:
                                dct['SuitFiled_WilfulDefault'] = SuitFiled_WilfulDefault[0]
                                print("SuitFiled_WilfulDefault#########",SuitFiled_WilfulDefault)

                            tag_woss = "Written_off_Settled_Status"
                            reg_str = "<" + tag_woss + ">(.*?)</" + tag_woss + ">"
                            res_Written_off_Settled_Status = re.findall(reg_str,data)
                            Written_off_Settled_Status = res_Written_off_Settled_Status
                            if Written_off_Settled_Status:
                                dct['Written_off_Settled_Status'] = Written_off_Settled_Status[0]
                                print("Written_off_Settled_Status#########",Written_off_Settled_Status)

                            # tag_voclm = "Value_of_Credits_Last_Month"
                            # reg_str = "<" + tag_voclm + ">(.*?)</" + tag_voclm + ">"
                            # res_Value_of_Credits_Last_Month = re.findall(reg_str,data)
                            # Value_of_Credits_Last_Month = re.Value_of_Credits_Last_Month
                            # print("Value_of_Credits_Last_Month#########",Value_of_Credits_Last_Month)

                            tag_ocode = "Occupation_Code"
                            reg_str = "<" + tag_ocode + ">(.*?)</" + tag_ocode + ">"
                            res_Occupation_Code = re.findall(reg_str,data)
                            Occupation_Code = res_Occupation_Code
                            print("Occupation_Code@@@@@@@@@@@@@@@@@@@@@@@@",Occupation_Code)
                            if Occupation_Code:
                                dct['Occupation_Code'] = Occupation_Code[0]
                                print("Occupation_Code#########",Occupation_Code)

                            tag_smamt = "Settlement_Amount"
                            reg_str = "<" + tag_smamt + ">(.*?)</" + tag_smamt + ">" 
                            res_Settlement_Amount = re.findall(reg_str, data)
                            Settlement_Amount = res_Settlement_Amount
                            if Settlement_Amount:
                                dct['Settlement_Amount'] = Settlement_Amount[0]
                                print("Settlement_Amount#########",Settlement_Amount)

                            tag_vocol = "Value_of_Collateral"
                            reg_str = "<" + tag_vocol + ">(.*?)</" + tag_vocol + ">" 
                            res_Value_of_Collateral = re.findall(reg_str, data)
                            Value_of_Collateral = res_Value_of_Collateral
                            if Value_of_Collateral:
                                dct['Value_of_Collateral'] = Value_of_Collateral[0]
                                print("Value_of_Collateral#########",Value_of_Collateral)

                            tag_tocl = "Type_of_Collateral"
                            reg_str = "<" + tag_tocl + ">(.*?)</" + tag_tocl + ">" 
                            res_Type_of_Collateral = re.findall(reg_str, data)
                            Type_of_Collateral = res_Type_of_Collateral
                            if Type_of_Collateral:
                                dct['Type_of_Collateral'] = Type_of_Collateral[0]
                                print("Type_of_Collateral#########",Type_of_Collateral)

                            tag_woat = "Written_Off_Amt_Total"
                            reg_str = "<" + tag_woat + ">(.*?)</" + tag_woat + ">" 
                            res_Written_Off_Amt_Total = re.findall(reg_str,data)
                            Written_Off_Amt_Total = res_Written_Off_Amt_Total
                            if Written_Off_Amt_Total:
                                dct['Written_Off_Amt_Total'] = Written_Off_Amt_Total[0]
                                print("Written_Off_Amt_Total#########",Written_Off_Amt_Total)

                            tag_woap = "Written_Off_Amt_Principal"
                            reg_str = "<" + tag_woap + ">(.*?)</" + tag_woap + ">"
                            res_Written_Off_Amt_Principal = re.findall(reg_str,data)
                            Written_Off_Amt_Principal = res_Written_Off_Amt_Principal
                            if Written_Off_Amt_Principal:
                                dct['Written_Off_Amt_Principal'] = Written_Off_Amt_Principal[0]
                                print("Written_Off_Amt_Principal#########",Written_Off_Amt_Principal)

                            tag_roi ="Rate_of_Interest"
                            reg_str = "<" + tag_roi + ">(.*?)</" + tag_roi + ">"
                            res_Rate_of_Interest = re.findall(reg_str,data)
                            Rate_of_Interest = res_Rate_of_Interest
                            if Rate_of_Interest:
                                dct['Rate_of_Interest'] = Rate_of_Interest[0]
                                print("Rate_of_Interest#########",Rate_of_Interest)

                            tag_rptenure = "Repayment_Tenure"
                            reg_str = "<" + tag_rptenure + ">(.*?)</" + tag_rptenure + ">"
                            res_Repayment_Tenure = re.findall(reg_str, data)
                            Repayment_Tenure = res_Repayment_Tenure
                            if Repayment_Tenure:
                                dct['Repayment_Tenure'] = Repayment_Tenure[0]
                                print("Repayment_Tenure#########",Repayment_Tenure)
                                # print("Repayment_Tenure@@@@@@@@@@@@@@@@@@@@@@@@@@@@@",Repayment_Tenure)

                            tag_prrf = "Promotional_Rate_Flag"
                            reg_str = "<" + tag_prrf + ">(.*?)</" + tag_prrf + ">"
                            res_Promotional_Rate_Flag = re.findall(reg_str, data)
                            Promotional_Rate_Flag = res_Promotional_Rate_Flag
                            if Promotional_Rate_Flag:
                                dct['Promotional_Rate_Flag'] = Promotional_Rate_Flag[0]
                                print("Promotional_Rate_Flag#########",Promotional_Rate_Flag)

                            tag_incind = "Income_Indicator"
                            reg_str = "<" + tag_incind + ">(.*?)</" + tag_incind + ">"
                            res_Income_Indicator = re.findall(reg_str, data)
                            Income_Indicator = res_Income_Indicator
                            if Income_Indicator:
                                dct['Income_Indicator'] = Income_Indicator[0]
                                print("Income_Indicator#########",Income_Indicator)

                            tag_infrin = "Income_Frequency_Indicator"
                            reg_str = "<" + tag_infrin + ">(.*?)</" + tag_infrin + ">"
                            res_Income_Frequency_Indicator = re.findall(reg_str, data)
                            Income_Frequency_Indicator = res_Income_Frequency_Indicator
                            if Income_Frequency_Indicator:
                                dct['Income_Frequency_Indicator'] = Income_Frequency_Indicator[0]
                                print("Income_Frequency_Indicator#########",Income_Frequency_Indicator)

                            tag_defstdt = "DefaultStatusDate"
                            reg_str = "<" + tag_defstdt + ">(.*?)</" + tag_defstdt + ">"
                            res_DefaultStatusDate = re.findall(reg_str, data)
                            DefaultStatusDate = res_DefaultStatusDate
                            if DefaultStatusDate:
                                dct['DefaultStatusDate'] = self._format_date_change(DefaultStatusDate[0])
                                print("DefaultStatusDate#########",DefaultStatusDate)

                            tag_litstdt = "LitigationStatusDate"
                            reg_str = "<" + tag_litstdt + ">(.*?)</" + tag_litstdt + ">"
                            res_LitigationStatusDate = re.findall(reg_str, data)
                            LitigationStatusDate = res_LitigationStatusDate
                            if LitigationStatusDate:
                                dct['LitigationStatusDate'] = self._format_date_change(LitigationStatusDate[0])
                                print("LitigationStatusDate#########",LitigationStatusDate)

                            tag_wosdt = "WriteOffStatusDate"
                            reg_str = "<" + tag_wosdt + ">(.*?)</" + tag_wosdt + ">"
                            res_WriteOffStatusDate=re.findall(reg_str, data)
                            WriteOffStatusDate = res_WriteOffStatusDate
                            if WriteOffStatusDate:
                                dct['WriteOffStatusDate'] = self._format_date_change(WriteOffStatusDate[0])
                                print("WriteOffStatusDate#########",WriteOffStatusDate)

                            tag_dtoad = "DateOfAddition"
                            reg_str = "<" + tag_dtoad + ">(.*?)</" + tag_dtoad + ">"
                            res_DateOfAddition = re.findall(reg_str, data)
                            DateOfAddition = res_DateOfAddition
                            if DateOfAddition:
                                dct['DateOfAddition'] = DateOfAddition[0]
                                print("DateOfAddition#########",DateOfAddition)

                            tag_ccod = "CurrencyCode"
                            reg_str = "<" + tag_ccod + ">(.*?)</" + tag_ccod + ">"
                            res_CurrencyCode = re.findall(reg_str, data)
                            CurrencyCode = res_CurrencyCode
                            if CurrencyCode:
                                dct['CurrencyCode'] = CurrencyCode[0]
                                print("CurrencyCode#########",CurrencyCode)

                            tag_sbscmt = "Subscriber_comments"
                            reg_str = "<" + tag_sbscmt + ">(.*?)</" + tag_sbscmt + ">"
                            res_Subscriber_comments = re.findall(reg_str, data)
                            Subscriber_comments = res_Subscriber_comments
                            if Subscriber_comments:
                                dct['Subscriber_comments'] = Subscriber_comments[0]
                                print("Subscriber_comments#########",Subscriber_comments)

                            tag_cncmm = "Consumer_comments"
                            reg_str = "<" + tag_cncmm + ">(.*?)</" + tag_cncmm + ">"
                            res_Consumer_comments = re.findall(reg_str, data)
                            Consumer_comments = res_Consumer_comments
                            if Consumer_comments:
                                dct['Consumer_comments'] = Consumer_comments[0]
                                print("Consumer_comments#########",Consumer_comments)

                            tag_ahtc = "AccountHoldertypeCode"
                            reg_str = "<" + tag_ahtc + ">(.*?)</" + tag_ahtc + ">"
                            res_AccountHoldertypeCode = re.findall(reg_str, data)
                            AccountHoldertypeCode = res_AccountHoldertypeCode
                            if AccountHoldertypeCode:
                                dct['AccountHoldertypeCode'] = AccountHoldertypeCode[0]
                                print("AccountHoldertypeCode#########",AccountHoldertypeCode)
                            
                            tag_yr = "Year"
                            reg_str = "<" + tag_yr + ">(.*?)</" + tag_yr + ">"
                            res_Year = re.findall(reg_str, data)
                            Year = res_Year
                            if Year:
                                dct['Year'] = Year[0]
                                print("Year#########",Year)

                            tag_mnt = "Month"
                            reg_str = "<" + tag_mnt + ">(.*?)</" + tag_mnt + ">"
                            res_Month = re.findall(reg_str, data)
                            Month = res_Month
                            if Month:
                                dct['Month'] = Month
                                print("Month#########", Month)

                            tag_dypd = "Days_Past_Due"
                            reg_str = "<" + tag_dypd + ">(.*?)</" + tag_dypd + ">"
                            res_Days_Past_Due = re.findall(reg_str, data)
                            Days_Past_Due = res_Days_Past_Due
                            if Days_Past_Due:
                                dct['Days_Past_Due'] = Days_Past_Due[0]
                                print("Days_Past_Due#########",Days_Past_Due)

                            tag_snmnm = "Surname_Non_Normalized"
                            reg_str = "<CAIS_Holder_Details><" + tag_snmnm + ">(.*?)</" + tag_snmnm + ">"
                            res_Surname_Non_Normalized = re.findall(reg_str, data)
                            Surname_Non_Normalized =res_Surname_Non_Normalized
                            print("Surname_Non_Normalized@@@@@@@@@@@@@@@@@@@@@@@@",Surname_Non_Normalized)
                            if Surname_Non_Normalized:
                                dct['Surname_Non_Normalized'] = Surname_Non_Normalized[0]
                                print("Surname_Non_Normalized#########",Surname_Non_Normalized)

                            tag_fnnnn = "First_Name_Non_Normalized"
                            reg_str = "<" + tag_fnnnn + ">(.*?)</" + tag_fnnnn + ">"
                            res_First_Name_Non_Normalized = re.findall(reg_str,data)
                            First_Name_Non_Normalized = res_First_Name_Non_Normalized

                            print("First_Name_Non_Normalized@@@@@@@@@@@@@",First_Name_Non_Normalized)
                            if First_Name_Non_Normalized:
                                dct['First_Name_Non_Normalized'] = First_Name_Non_Normalized[0]
                                print("First_Name_Non_Normalized#########",First_Name_Non_Normalized)

                            tag_mn1n = "Middle_Name_1_Non_Normalized"
                            reg_str = "<" + tag_snmnm + ">(.*?)</" + tag_snmnm + ">"
                            res_Middle_Name_1_Non_Normalized = re.findall(reg_str,data)
                            Middle_Name_1_Non_Normalized = res_Middle_Name_1_Non_Normalized
                            if Middle_Name_1_Non_Normalized:
                                print("Middle_Name_1_Non_Normalized@@@@@@@@@@@@@@@@@",Middle_Name_1_Non_Normalized)
                                dct['Middle_Name_1_Non_Normalized'] = Middle_Name_1_Non_Normalized[0]
                                print("Middle_Name_1_Non_Normalized#########",Middle_Name_1_Non_Normalized)

                            tag_mn2n = "Middle_Name_2_Non_Normalized"
                            reg_str = "<" + tag_mn2n + ">(.*?)</" + tag_mn2n + ">"
                            res_Middle_Name_2_Non_Normalized = re.findall(reg_str,data)
                            Middle_Name_2_Non_Normalized = res_Middle_Name_2_Non_Normalized
                            if Middle_Name_2_Non_Normalized:
                                dct['Middle_Name_2_Non_Normalized'] = Middle_Name_2_Non_Normalized[0]
                                print("Middle_Name_2_Non_Normalized#########",Middle_Name_2_Non_Normalized)

                            tag_mn3n = "Middle_Name_3_Non_Normalized"
                            reg_str = "<" + tag_mn3n + ">(.*?)</" + tag_mn3n + ">"
                            res_Middle_Name_3_Non_Normalized = re.findall(reg_str,data)
                            Middle_Name_3_Non_Normalized = res_Middle_Name_3_Non_Normalized
                            if Middle_Name_3_Non_Normalized:
                                dct['Middle_Name_3_Non_Normalized'] = Middle_Name_3_Non_Normalized[0]
                                print("Middle_Name_3_Non_Normalized#########",Middle_Name_3_Non_Normalized)

                            tag_als = "Alias"
                            reg_str = "<" + tag_als + ">(.*?)</" + tag_als + ">"
                            res_Alias = re.findall(reg_str,data)
                            Alias = res_Alias
                            if Alias:
                                dct['Alias'] = Alias[0]
                                print("Alias#########",Alias)

                            tag_intxpn = "Income_TAX_PAN"
                            reg_str ="<" + tag_intxpn + ">(.*?)</" + tag_intxpn + ">"
                            res_Income_TAX_PAN = re.findall(reg_str,data)
                            Income_TAX_PAN = res_Income_TAX_PAN
                            if Income_TAX_PAN:
                                dct['Income_TAX_PAN'] = Income_TAX_PAN[0]
                                print("Income_TAX_PAN#########",Income_TAX_PAN)

                            tag_pssno = "Passport_number"
                            reg_str = "<" + tag_pssno + ">(.*?)</" + tag_pssno + ">"
                            res_Passport_number = re.findall(reg_str,data)
                            Passport_number = res_Passport_number
                            if Passport_number:
                                dct['Passport_number'] = Passport_number[0]
                                print("Passport_number#########",Passport_number)

                            tag_vidno = "Voter_ID_Number"
                            res_str = "<" + tag_vidno + ">(.*?)</" + tag_vidno + ">"
                            res_Voter_ID_Number = re.findall(res_str,data)
                            Voter_ID_Number = res_Voter_ID_Number
                            if Voter_ID_Number:
                                dct['Voter_ID_Number'] = Voter_ID_Number[0]
                                print("Voter_ID_Number#########",Voter_ID_Number)

                            tag_dob = "Date_of_birth"
                            reg_str = "<" + tag_dob + ">(.*?)</" + tag_dob + ">"
                            res_Date_of_birth = re.findall(reg_str,data)
                            Date_of_birth = res_Date_of_birth
                            if Date_of_birth:
                                dct['Date_of_birth'] = self._format_date_change(Date_of_birth[0])
                                print("Date_of_birth#########",Date_of_birth)


                            tag_flann = "First_Line_Of_Address_non_normalized"
                            reg_str = "<" + tag_flann + ">(.*?)</" + tag_flann + ">"
                            res_First_Line_Of_Address_non_normalized = re.findall(reg_str,data)
                            First_Line_Of_Address_non_normalized = res_First_Line_Of_Address_non_normalized
                            if First_Line_Of_Address_non_normalized:
                                print("First_Line_Of_Address_non_normalized#####$$$$$$$$$$$$$$$$$$$$$$$$$$$",First_Line_Of_Address_non_normalized)
                                dct['First_Line_Of_Address_non_normalized'] = First_Line_Of_Address_non_normalized[0]
                                print("First_Line_Of_Address_non_normalized#########",First_Line_Of_Address_non_normalized)

                            tag_slann = "Second_Line_Of_Address_non_normalized"
                            reg_str = "<" + tag_slann + ">(.*?)</" + tag_slann + ">"
                            res_Second_Line_Of_Address_non_normalized = re.findall(reg_str,data)
                            Second_Line_Of_Address_non_normalized = res_Second_Line_Of_Address_non_normalized
                            if Second_Line_Of_Address_non_normalized:
                                print("res_Second_Line_Of_Address_non_normalized@@@@@@@@@@@@",res_Second_Line_Of_Address_non_normalized)
                                dct['Second_Line_Of_Address_non_normalized'] = Second_Line_Of_Address_non_normalized[0]
                                print("Second_Line_Of_Address_non_normalized#########",Second_Line_Of_Address_non_normalized)

                            tag_tlann = "Third_Line_Of_Address_non_normalized"
                            reg_str = "<" + tag_tlann + ">(.*?)</" + tag_tlann + ">"
                            res_Third_Line_Of_Address_non_normalized = re.findall(reg_str,data)
                            Third_Line_Of_Address_non_normalized = res_Third_Line_Of_Address_non_normalized
                            if Third_Line_Of_Address_non_normalized:
                                print("Third_Line_Of_Address_non_normalized@@@@@@@@@@@@@@@",Third_Line_Of_Address_non_normalized)
                                dct['Third_Line_Of_Address_non_normalized'] = Third_Line_Of_Address_non_normalized[0]
                                print("Third_Line_Of_Address_non_normalized#########",Third_Line_Of_Address_non_normalized)

                            tag_ctynnorm = "City_non_normalized"
                            reg_str = "<" + tag_ctynnorm + ">(.*?)</" + tag_ctynnorm + ">"
                            res_City_non_normalized = re.findall(reg_str,data)
                            City_non_normalized = res_City_non_normalized
                            if City_non_normalized:
                                dct['City_non_normalized'] = City_non_normalized[0]
                                print("City_non_normalized#########",City_non_normalized)


                            tag_floann = "Fifth_Line_Of_Address_non_normalized"
                            reg_str = "<" + tag_floann + ">(.*?)</" + tag_floann + ">"
                            res_Fifth_Line_Of_Address_non_normalized = re.findall(reg_str,data)
                            Fifth_Line_Of_Address_non_normalized = res_Fifth_Line_Of_Address_non_normalized
                            if Fifth_Line_Of_Address_non_normalized:
                                print("Fifth_Line_Of_Address_non_normalized@@@@@@@@@@@@@@@@@@@@",Fifth_Line_Of_Address_non_normalized)
                                dct['Fifth_Line_Of_Address_non_normalized'] = Fifth_Line_Of_Address_non_normalized[0]
                                print("Fifth_Line_Of_Address_non_normalized#########",Fifth_Line_Of_Address_non_normalized)


                            tag_stnn = "State_non_normalized"
                            reg_str = "<" + tag_stnn + ">(.*?)</" + tag_stnn + ">"
                            res_State_non_normalized = re.findall(reg_str,data)
                            State_non_normalized = res_State_non_normalized
                            if State_non_normalized:
                                dct['State_non_normalized'] = State_non_normalized[0]
                                print("State_non_normalized#########",State_non_normalized)

                            tag_zippnn = "ZIP_Postal_Code_non_normalized"
                            reg_str = "<" + tag_zippnn + ">(.*?)</" + tag_zippnn + ">"
                            res_ZIP_Postal_Code_non_normalized = re.findall(reg_str,data)
                            ZIP_Postal_Code_non_normalized = res_ZIP_Postal_Code_non_normalized
                            print("ZIP_Postal_Code_non_normalized@@@@@@@@@@@@@@@@@@@@@@",ZIP_Postal_Code_non_normalized)
                            if ZIP_Postal_Code_non_normalized:
                                dct['ZIP_Postal_Code_non_normalized'] = ZIP_Postal_Code_non_normalized[0]
                                print("ZIP_Postal_Code_non_normalized#########",ZIP_Postal_Code_non_normalized)

                            tag_cntnn = "CountryCode_non_normalized"
                            reg_str = "<" + tag_cntnn + ">(.*?)</" + tag_cntnn + ">"
                            res_CountryCode_non_normalized = re.findall(reg_str,data)
                            CountryCode_non_normalized = res_CountryCode_non_normalized
                            if CountryCode_non_normalized:
                                dct['CountryCode_non_normalized'] = CountryCode_non_normalized[0]
                                print("CountryCode_non_normalized#########",CountryCode_non_normalized)

                            tag_aiinn = "Address_indicator_non_normalized"
                            reg_str = "<" + tag_aiinn + ">(.*?)</" + tag_aiinn + ">"
                            res_Address_indicator_non_normalized = re.findall(reg_str,data)
                            Address_indicator_non_normalized = res_Address_indicator_non_normalized
                            if Address_indicator_non_normalized:
                                dct['Address_indicator_non_normalized'] = Address_indicator_non_normalized[0]
                                print("Address_indicator_non_normalized#########",Address_indicator_non_normalized)

                            tag_recnon = "Residence_code_non_normalized"
                            reg_str = "<" + tag_recnon + ">(.*?)</" + tag_recnon + ">"
                            res_Residence_code_non_normalized = re.findall(reg_str,data)
                            Residence_code_non_normalized = res_Residence_code_non_normalized
                            if Residence_code_non_normalized:
                                dct['Residence_code_non_normalized'] = Residence_code_non_normalized[0]
                                print("Residence_code_non_normalized#########",Residence_code_non_normalized)


                            tag_telno = "Telephone_Number"
                            reg_str = "<" + tag_telno + ">(.*?)</" + tag_telno + ">"
                            res_Telephone_Number = re.findall(reg_str,data)
                            Telephone_Number = res_Telephone_Number
                            if Telephone_Number:
                                dct['Telephone_Number'] = Telephone_Number[0]
                                print("Telephone_Number#########",Telephone_Number)



                            tag_ttypp  = "Telephone_Type"
                            reg_str = "<" + tag_ttypp + ">(.*?)</" + tag_ttypp + ">"
                            res_Telephone_Type = re.findall(reg_str,data)
                            Telephone_Type = res_Telephone_Type
                            if Telephone_Type:
                                dct['Telephone_Type'] = Telephone_Type[0]
                                print("Telephone_Type#########",Telephone_Type)

                            tag_texttt  = "Telephone_Extension"
                            reg_str = "<" + tag_texttt + ">(.*?)</" + tag_texttt + ">"
                            res_Telephone_Extension = re.findall(reg_str,data)
                            Telephone_Extension = res_Telephone_Extension
                            if Telephone_Extension:
                                dct['Telephone_Extension'] = Telephone_Extension[0]
                                print("Telephone_Extension#########",Telephone_Extension)


                            tag_mttnn  = "Mobile_Number"
                            reg_str = "<" + tag_mttnn + ">(.*?)</" + tag_mttnn + ">"
                            res_Mobile_Number = re.findall(reg_str,data)
                            Mobile_Number = res_Mobile_Number
                            if Mobile_Number:
                                dct['Mobile_Number'] = Mobile_Number[0]
                                print("Mobile_Number#########",Mobile_Number)


                            tag_fxno = "FaxNumber"
                            reg_str = "<" + tag_fxno + ">(.*?)</" + tag_fxno + ">"
                            res_FaxNumber = re.findall(reg_str,data)
                            FaxNumber = res_FaxNumber
                            if FaxNumber:
                                dct['FaxNumber'] = FaxNumber[0]
                                print("FaxNumber#########",FaxNumber)


                            




                            tag_acno = "Account_Number"
                            reg_str = "<" + tag_acno + ">(.*?)</" + tag_acno + ">"
                            res_Account_Number = re.findall(reg_str,data)
                            Account_Number = res_Account_Number
                            print("Account_Number$$$$$$$$$$$$$$$$$$$$$$$$$$",len(Account_Number))
                            for x in range(len(Account_Number)):
                                print("KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKk",Account_Number[x])
                                lender_data =  self.env['lender.details'].search([("Account_Number","=",Account_Number[x])])
                                if not lender_data:
                                    address_data = self.env["address.userlender"].search([("lender_data_test","=",lender_data.id)])
                                    lender_data1 = lender_data.create({
                                        "Subscriber_Name" : Subscriber_Name[x],
                                        "Account_Type" : str(Account_Type[x]),
                                        "Account_Number" : Account_Number[x],
                                        "Portfolio_Type" : str(AccountHoldertypeCode[x]),
                                        "Date_Reported" : self._format_date_change(Date_Reported[x]),
                                        "Account_Status" : str(Account_Status[x]),
                                        "Open_Date" : self._format_date_change(Open_Date[x]),
                                        "Highest_Credit_or_Original_Loan_Amount" : Highest_Credit_or_Original_Loan_Amount[x],
                                        "Current_Balance" : Current_Balance[x],
                                        "Amount_Past_Due" : Amount_Past_Due[x],
                                        "name" : First_Name_Non_Normalized[0] + " " + " " + Surname_Non_Normalized[0],
                                        "Date_Closed" : self._format_date_change(Date_Closed[x]),
                                        "Rate_of_Interest" : Rate_of_Interest[x],
                                        "Value_of_Collateral" : Value_of_Collateral[x],
                                        "Type_of_Collateral" : Type_of_Collateral[x],
                                        "SuitFiledWillfulDefaultWrittenOffStatus" : SuitFiledWillfulDefaultWrittenOffStatus[x],
                                        "Date_of_Last_Payment" : self._format_date_change(Date_of_Last_Payment[x]),
                                        "SuitFiled_WilfulDefault" : SuitFiled_WilfulDefault[x],
                                        "Credit_Limit_Amount" : Credit_Limit_Amount[x],
                                        "Scheduled_Monthly_Payment_Amount" : Scheduled_Monthly_Payment_Amount[x],
                                        "Repayment_Tenure" : Repayment_Tenure[x],
                                        "Written_Off_Amt_Total" : Written_Off_Amt_Total[x],
                                        "Written_Off_Amt_Principal" : Written_Off_Amt_Principal[x],
                                        "Settlement_Amount" : Settlement_Amount[x],
                                        "Written_off_Settled_Status" : str(Written_off_Settled_Status[x]),
                                        "Date_of_birth" : self._format_date_change(Date_of_birth[0]),
                                        "Gender_Code" : str(Gender_Code[0]) if Gender_Code else False,
                                        # "Occupation_Code" : Occupation_Code[x],
                                        "EMailId" : EMailId[0] if EMailId else False,
                                        # "Telephone_Type" : Telephone_Type[x],
                                        "MobilePhoneNumber" : MobilePhoneNumber[0] if MobilePhoneNumber else False,
                                        # "Telephone_Extension" : Telephone_Extension[x],
                                        "IncomeTaxPan" : IncomeTaxPan[0] if IncomeTaxPan else False,
                                        # "PAN_Issue_Date" : PAN_Issue_Date[x],
                                        # "PAN_Expiration_Date" : PAN_Expiration_Date[x],
                                        # "Passport_number" : Passport_number[0],
                                        # "Passport_Issue_Date" : Passport_Issue_Date[x],
                                        # "Passport_Expiration_Date" : Passport_Expiration_Date[x],
                                        # "Voter_ID_Number" : Voter_ID_Number[x],
                                        # "Voter_ID_Issue_Date" : Voter_ID_Issue_Date[x],
                                        # "Voter_ID_Expiration_Date" : Written_off_Settled_Status[x],
                                        # "Universal_ID_Number" : Universal_ID_Number[x],
                                        # "Universal_ID_Issue_Date" : Universal_ID_Issue_Date[x],
                                        # "Universal_ID_Expiration_Date" : Universal_ID_Expiration_Date[x],
                                        # "Driver_License_Number" : Driver_License_Number[x],
                                        # "Driver_License_Issue_Date" : Driver_License_Issue_Date[x],
                                        # "Driver_License_Expiration_Date" : Driver_License_Expiration_Date[x],
                                        # "Ration_Card_Number" : Ration_Card_Number[x],
                                        # "Ration_Card_Issue_Date" : Ration_Card_Issue_Date[x],
                                        # "Ration_Card_Expiration_Date" : Ration_Card_Expiration_Date[x],

                                        })
                                    
                                    self.lender_data =  [(4, lender_data1.id)]
 

                            address_per_add = "</CAIS_Holder_Details><CAIS_Holder_Address_Details>(.*?)</CAIS_Holder_Address_Details><CAIS_Holder_Phone_Details>"
                            res_address_per_add = re.findall(address_per_add,data)
                            print("res_address_per_add@@@@@@@@@@@@@@@@@@@@@",res_address_per_add)
                            count = 0
                            for m in res_address_per_add:
                                print("mmmmmmmmmmmmmmmmmmmmmmmmmm",m)
                                address_ddtt = "<First_Line_Of_Address_non_normalized>(.*?)</First_Line_Of_Address_non_normalized><Second_Line_Of_Address_non_normalized>(.*?)</Second_Line_Of_Address_non_normalized><Third_Line_Of_Address_non_normalized>(.*?)</Third_Line_Of_Address_non_normalized><City_non_normalized>(.*?)</City_non_normalized><Fifth_Line_Of_Address_non_normalized>(.*?)</Fifth_Line_Of_Address_non_normalized><State_non_normalized>(.*?)</State_non_normalized><ZIP_Postal_Code_non_normalized>(.*?)</ZIP_Postal_Code_non_normalized><CountryCode_non_normalized>(.*?)</CountryCode_non_normalized>"    
                                res_address_datatt = re.findall(address_ddtt,m)
                                print("res_address_datatt@@@@@@@@@@@@@@@@@@@@@@@",[' '.join(tups) for tups in res_address_datatt])
                                address_data = self.env["address.userlender"].search([("Account_Number" ,"=",Account_Number[count])])
                                lender_data =  self.env['lender.details'].search([("Account_Number","=",Account_Number[count])])
                                print("lender_data@@@@@@@@@@@@@@@@@@@@@@",lender_data)
                                if lender_data and not address_data:
                                    for mmd in [' '.join(tups) for tups in res_address_datatt]:
                                        addres_data = address_data.create({
                                            "address" : mmd,
                                            "Account_Number" : Account_Number[count]
                                            })
                                        # for lendd in range(self.lender_data):
                                        #     if lendd == count:
                                        lender_data.addres_data = [(4, addres_data.id)]
                                count = count + 1    
                                # self.lender_data.addres_data =  [(4, addres_data.id)]

                            tag_Gender_Code = "Gender_Code"
                            reg_str_Gender_Code = "</First_Name><" + tag_Gender_Code + ">(.*?)</" + tag_Gender_Code + ">"
                            res_Gender_Code = re.findall(reg_str_Gender_Code, data)
                            Gender_Code = res_Gender_Code
                            if Gender_Code:
                                dct['Gender_Code'] = Gender_Code[0]
                                print("First_Name##############",Gender_Code)
                                        

                            tag_last = "Last_Name"
                            reg_str = "<" + tag_last + ">(.*?)</" + tag_last + ">"
                            res_Last_Name = re.findall(reg_str, data)
                            Last_Name = res_Last_Name
                            if Last_Name:
                                dct['Last_Name'] = Last_Name[0]
                                print("Last_name##################",Last_Name)

                            tag_agdur = "Duration_Of_Agreement"
                            reg_str = "Amount_Financed><" + tag_agdur + ">(.*?)</" + tag_agdur + ">" 
                            res_Duration_Of_Agreement = re.findall (reg_str,data) 
                            Duration_Of_Agreement = res_Duration_Of_Agreement
                            print("Duration_Of_Agreementkkkkkkkkkkkkkkkkkkkkkkk",Duration_Of_Agreement)
                            if Duration_Of_Agreement:
                                dct['Duration_Of_Agreement'] = Duration_Of_Agreement[0]
                                print("Duration_Of_Agreement#########",Duration_Of_Agreement)  

                            tag_mphno = "MobilePhoneNumber"
                            reg_str = "Middle_Name3><" + tag_mphno + ">(.*?)</" + tag_mphno + ">"
                            res_MobilePhoneNumber = re.findall(reg_str,data)
                            MobilePhoneNumber = res_MobilePhoneNumber
                            print("MobilePhoneNumber@@@@@@@@@@@@@@@@@@@@@@@",MobilePhoneNumber)
                            if MobilePhoneNumber:
                                dct['MobilePhoneNumber'] = MobilePhoneNumber[0]
                                print("MobilePhoneNumber#########",MobilePhoneNumber)      


                            tag_datamm = "EMailId"
                            reg_str_tt = "</Driver_License_Number><" + tag_datamm + ">(.*?)</" + tag_datamm + ">"
                            res_EMailId = re.findall(reg_str_tt,data)
                            EMailId = res_EMailId
                            print("Account_Number$$$$$$$$$$$$$$$$$$$$$$$$$$",len(EMailId))
                            for i in range(len(EMailId)):
                                print("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFf",EMailId[i])
                                credit_enqui =  self.env['credit.enquiries'].search([("ReportNumber","=",ReportNumber[i])])
                                if not credit_enqui:
                                    credit_enqui = credit_enqui.create({
                                        "First_Name" : First_Name[i] + " " + Last_Name[i],
                                        "Last_Name" : " " + Last_Name[i],
                                        "Date_Of_Birth_Applicant" : self._format_date_change(Date_Of_Birth_Applicant[i]),
                                        "IncomeTaxPan" : IncomeTaxPan[i],
                                        "ReportNumber" : ReportNumber[i],
                                        "Telephone_Number_Applicant_1st" : Telephone_Number_Applicant_1st[0] if Telephone_Number_Applicant_1st else False,
                                        "Duration_Of_Agreement" : Duration_Of_Agreement[i + 1],
                                        "Passport_number" : Passport_number[i],
                                        "EMailId" : EMailId[i],
                                        "Enquiry_Reason" : str(Enquiry_Reason[i]),
                                        "MobilePhoneNumber" : MobilePhoneNumber[0] if MobilePhoneNumber else False,
                                        "Voter_s_Identity_Card" : Voter_s_Identity_Card[i],
                                        "Subscriber_Name" : jjjj[i],
                                        "Gender_Code" : Gender_Code[i],
                                        "Driver_License_Number" : Driver_License_Number[i],
                                        "Date_of_Request" : self._format_date_change(Date_of_Request[i]),
                                        "Marital_Status" : Marital_Status[i],
                                        "Ration_Card_Number" : Ration_Card_Number[i],
                                        "Amount_Financed" : Amount_Financed[i + 1],
       
                                    })
                                    self.credit_enquiries = [(4, credit_enqui.id)]


                            data_payment_history = "</AccountHoldertypeCode><CAIS_Account_History>(.*?)</CAIS_Account_History><CAIS_Holder_Details>"
                            res_payment_history = re.findall(data_payment_history,data)
                            print("res_payment_history3333333333333333333333@@@@@@@@@@@@@@@@@@@@@",res_payment_history)
                            count_history = 0
                            for m_his in res_payment_history:
                                # print("mmmmmmmmjjjjjjjjjjjjjjjjjjjjjjjmmmmmmmmmmmmmmmmmm",m_his)
                                tag_yr = "Year"
                                reg_str = "<" + tag_yr + ">(.*?)</" + tag_yr + ">"
                                res_Year = re.findall(reg_str, m_his)
                                Year = res_Year
                                if Year:
                                    dct['Year'] = Year[0]
                                    print("Year#########",Year)

                                tag_mnt = "Month"
                                reg_str = "<" + tag_mnt + ">(.*?)</" + tag_mnt + ">"
                                res_Month = re.findall(reg_str, m_his)
                                Month = res_Month
                                if Month:
                                    dct['Month'] = Month
                                    print("Month#########", Month)

                                tag_dypd = "Days_Past_Due"
                                reg_str = "<" + tag_dypd + ">(.*?)</" + tag_dypd + ">"
                                res_Days_Past_Due = re.findall(reg_str, m_his)
                                Days_Past_Due = res_Days_Past_Due
                                if Days_Past_Due:
                                    dct['Days_Past_Due'] = Days_Past_Due[0]
                                    print("Days_Past_Due#########",Days_Past_Due)
                                address_data = self.env["payment.history"].search([("Account_Number" ,"=",Account_Number[count_history])])    
                                lender_data =  self.env['lender.details'].search([("Account_Number","=",Account_Number[count_history])])
                                print("lender_data@@@@@@@@@@@@@@@@@@@@@@",lender_data)
                                if lender_data and not address_data:                         
                                    for hht in range(len(Year)):
                                        payment_history = self.env["payment.history"].search([])
                                        payment_history = payment_history.create({
                                            "Year" : Year[hht],
                                            "Month" : Month[hht],
                                            "Days_Past_Due" : Days_Past_Due[hht],
                                            "Account_Number": Account_Number[count_history]
                                            }) 
                                        lender_data.payment_hist = [(4, payment_history.id)] 
                                count_history = count_history + 1
                                    # payment_hist

                                # address_ddtt = "<First_Line_Of_Address_non_normalized>(.*?)</First_Line_Of_Address_non_normalized><Second_Line_Of_Address_non_normalized>(.*?)</Second_Line_Of_Address_non_normalized><Third_Line_Of_Address_non_normalized>(.*?)</Third_Line_Of_Address_non_normalized><City_non_normalized>(.*?)</City_non_normalized><Fifth_Line_Of_Address_non_normalized>(.*?)</Fifth_Line_Of_Address_non_normalized><State_non_normalized>(.*?)</State_non_normalized><ZIP_Postal_Code_non_normalized>(.*?)</ZIP_Postal_Code_non_normalized><CountryCode_non_normalized>(.*?)</CountryCode_non_normalized>"    
                                # res_address_datatt = re.findall(address_ddtt,m)
                                # print("res_address_datatt@@@@@@@@@@@@@@@@@@@@@@@",[' '.join(tups) for tups in res_address_datatt])
                                # address_data = self.env["address.userlender"].search([("Account_Number" ,"=",Account_Number[count])])
                                # lender_data =  self.env['lender.details'].search([("Account_Number","=",Account_Number[count])])
                                # print("lender_data@@@@@@@@@@@@@@@@@@@@@@",lender_data)
                                # if lender_data and not address_data:
                                #     for mmd in [' '.join(tups) for tups in res_address_datatt]:
                                #         addres_data = address_data.create({
                                #             "address" : mmd,
                                #             "Account_Number" : Account_Number[count]
                                #             })
                                #         # for lendd in range(self.lender_data):
                                #         #     if lendd == count:
                                #         lender_data.addres_data = [(4, addres_data.id)]
                                # count = count + 1    
                                    


                            if Account_Number:
                                dct['Account_Number'] = Account_Number[0]
                                print("Account_Number#########",Account_Number)



                            # tag_exmtch = "Exact_match"
                            # reg_str = "<" + tag_exmtch + ">(.*?)</" + tag_exmtch + ">"
                            # res_Exact_match = re.findall(reg_str,data)
                            # Exact_match = res_Exact_match
                            # if Exact_match:
                            #     dct['Exact_match'] = Exact_match[0]
                            #     print("Exact_match#########",Exact_match)

                            tag_tvl7d = "TotalCAPSLast7Days"
                            reg_str = "<" + tag_tvl7d + ">(.*?)</" + tag_tvl7d + ">"
                            res_TotalCAPSLast7Days = re.findall(reg_str,data)
                            TotalCAPSLast7Days = res_TotalCAPSLast7Days
                            if TotalCAPSLast7Days:
                                dct['TotalCAPSLast7Days'] = TotalCAPSLast7Days[0]
                                print("TotalCAPSLast7Days#########",TotalCAPSLast7Days)

                            tag_tvl30d = "TotalCAPSLast30Days"
                            reg_str = "<" + tag_tvl30d + ">(.*?)</" + tag_tvl30d + ">"
                            res_TotalCAPSLast30Days = re.findall(reg_str,data)
                            TotalCAPSLast30Days = res_TotalCAPSLast30Days
                            if TotalCAPSLast30Days:
                                dct['TotalCAPSLast30Days'] = TotalCAPSLast30Days[0]
                                print("TotalCAPSLast30Days#########",TotalCAPSLast30Days)

                            tag_tvl90d = "TotalCAPSLast90Days"
                            reg_str = "<" + tag_tvl90d + ">(.*?)</" + tag_tvl90d + ">"
                            res_TotalCAPSLast90Days = re.findall(reg_str,data)
                            TotalCAPSLast90Days = res_TotalCAPSLast90Days
                            if TotalCAPSLast90Days:
                                dct['TotalCAPSLast90Days'] = TotalCAPSLast90Days[0]
                                print("TotalCAPSLast90Days#########",TotalCAPSLast90Days)

                            tag_tvl180d = "TotalCAPSLast180Days"
                            reg_str = "<" + tag_tvl180d + ">(.*?)</" + tag_tvl180d + ">"
                            res_TotalCAPSLast180Days = re.findall(reg_str,data)
                            TotalCAPSLast180Days = res_TotalCAPSLast180Days
                            if TotalCAPSLast180Days:
                                dct['TotalCAPSLast180Days'] = TotalCAPSLast180Days[0]
                                print("TotalCAPSLast180Days#########",TotalCAPSLast180Days)

                            tag_capl7d = "CAPSLast7Days"
                            reg_str = "<" + tag_capl7d + ">(.*?)</" + tag_capl7d + ">"
                            res_CAPSLast7Days = re.findall(reg_str,data)
                            CAPSLast7Days = res_CAPSLast7Days
                            if CAPSLast7Days:
                                dct['CAPSLast7Days'] = CAPSLast7Days[0]
                                print("CAPSLast7Days#########",CAPSLast7Days)

                            tag_capl30d = "CAPSLast30Days"
                            reg_str = "<" + tag_capl30d + ">(.*?)</" + tag_capl30d + ">"
                            res_CAPSLast30Days = re.findall(reg_str,data)
                            CAPSLast30Days = res_CAPSLast30Days
                            if CAPSLast30Days:
                                dct['CAPSLast30Days'] = CAPSLast30Days[0]
                                print("CAPSLast30Days#########",CAPSLast30Days)

                            tag_capl90d = "CAPSLast90Days"
                            reg_str = "<" + tag_capl90d + ">(.*?)</" + tag_capl90d + ">"
                            res_CAPSLast90Days = re.findall(reg_str,data)
                            CAPSLast90Days = res_CAPSLast90Days
                            if CAPSLast90Days:
                                dct['CAPSLast90Days'] = CAPSLast90Days[0]
                                print("CAPSLast90Days#########",CAPSLast90Days)

                            tag_capl180d = "CAPSLast180Days"
                            reg_str = "<" + tag_capl180d + ">(.*?)</" + tag_capl180d + ">"
                            res_CAPSLast180Days = re.findall(reg_str,data)
                            CAPSLast180Days = res_CAPSLast180Days
                            if CAPSLast180Days:
                                dct['CAPSLast180Days'] = CAPSLast180Days[0]
                                print("CAPSLast180Days#########",CAPSLast180Days)


                            tag_nccl7 = "NonCreditCAPSLast7Days"
                            reg_str = "<" + tag_nccl7 + ">(.*?)</" + tag_nccl7 + ">"
                            res_NonCreditCAPSLast7Days = re.findall(reg_str,data)
                            NonCreditCAPSLast7Days = res_NonCreditCAPSLast7Days
                            if NonCreditCAPSLast7Days:
                                dct['NonCreditCAPSLast7Days'] = NonCreditCAPSLast7Days[0]
                                print("NonCreditCAPSLast7Days#########",NonCreditCAPSLast7Days)

                            tag_nccl30 = "NonCreditCAPSLast30Days"
                            reg_str = "<" + tag_nccl30 + ">(.*?)</" + tag_nccl30 + ">"
                            res_NonCreditCAPSLast30Days = re.findall(reg_str,data)
                            NonCreditCAPSLast30Days = res_NonCreditCAPSLast30Days
                            if NonCreditCAPSLast30Days:
                                dct['NonCreditCAPSLast30Days'] = NonCreditCAPSLast30Days[0]
                                print("NonCreditCAPSLast30Days#########",NonCreditCAPSLast30Days)

                            tag_nccl90 = "NonCreditCAPSLast90Days"
                            reg_str = "<" + tag_nccl90 + ">(.*?)</" + tag_nccl90 + ">"
                            res_NonCreditCAPSLast90Days = re.findall(reg_str,data)
                            NonCreditCAPSLast90Days = res_NonCreditCAPSLast90Days
                            if NonCreditCAPSLast90Days:
                                dct['NonCreditCAPSLast90Days'] = NonCreditCAPSLast90Days[0]
                                print("NonCreditCAPSLast90Days#########",NonCreditCAPSLast90Days)

                            tag_nccl180 = "NonCreditCAPSLast180Days"
                            reg_str = "<" + tag_nccl180 + ">(.*?)</" + tag_nccl180 + ">"
                            res_NonCreditCAPSLast180Days = re.findall(reg_str,data)
                            NonCreditCAPSLast180Days = res_NonCreditCAPSLast180Days
                            if NonCreditCAPSLast180Days:
                                dct['NonCreditCAPSLast180Days'] = NonCreditCAPSLast180Days[0]
                                print("NonCreditCAPSLast180Days#########",NonCreditCAPSLast180Days)

                            tag_bursco = "BureauScore"
                            reg_str = "<" + tag_bursco + ">(.*?)</" + tag_bursco + ">"
                            res_BureauScore = re.findall(reg_str,data)
                            BureauScore = res_BureauScore
                            if BureauScore:
                                dct['BureauScore'] = BureauScore[0]
                                print("BureauScore#########",BureauScore)
                            
                            

                            tag_bursccl = "BureauScoreConfidLevel"
                            reg_str = "<" + tag_bursccl + ">(.*?)</" + tag_bursccl + ">"
                            res_BureauScoreConfidLevel = re.findall(reg_str,data)
                            BureauScoreConfidLevel = res_BureauScoreConfidLevel
                            if BureauScoreConfidLevel:
                                dct['BureauScoreConfidLevel'] = BureauScoreConfidLevel[0]
                                print("BureauScoreConfidLevel#########",BureauScoreConfidLevel)


                            tag_brplc = "BureauPLcore"
                            reg_str = "<" + tag_brplc + ">(.*?)</" + tag_brplc + ">"
                            res_BureauPLcore = re.findall(reg_str,data)
                            BureauPLcore = res_BureauPLcore
                            if BureauPLcore:
                                dct['BureauPLcore'] = BureauPLcore[0]
                                print("BureauPLcore#########",BureauPLcore)

                            tag_flann = "First_Line_Of_Address_non_normalized"
                            reg_str = "<" + tag_flann + ">(.*?)</" + tag_flann + ">"
                            res_First_Line_Of_Address_non_normalized = re.findall(reg_str,data)
                            First_Line_Of_Address_non_normalized = res_First_Line_Of_Address_non_normalized
                            print("First_Line_Of_Address_non_normalized#####$$$$$$$$$$$$$$$$$$$$$$$$$$$",First_Line_Of_Address_non_normalized)
                            # dct['First_Line_Of_Address_non_normalized'] = [' '.join(tups) for tups in res_address_datatt][0]

                            tag_levsc = "LeverageScore"
                            reg_str = "<" + tag_levsc + ">(.*?)</" + tag_levsc + ">"
                            res_LeverageScore = re.findall(reg_str,data)
                            LeverageScore = res_LeverageScore
                            if LeverageScore:
                                dct['LeverageScore'] = LeverageScore[0]
                                print("LeverageScore#########",LeverageScore)

                            tag_nhhc = "NoHitScore"
                            reg_str = "<" + tag_nhhc + ">(.*?)</" + tag_nhhc + ">"
                            res_NoHitScore = re.findall(reg_str,data)
                            NoHitScore = res_NoHitScore
                            if NoHitScore:
                                dct['NoHitScore'] = NoHitScore[0]
                                print("NoHitScore#########",NoHitScore)

                            tag_csh = "CAIS_Account_History"
                            reg_str = "<" + tag_csh + ">(.*?)</"

                            loan_lead = self.env['capwise.lead'].sudo().search([('lead_id','=',self.lead_id),("loan_type", '=',self.loan_type) ], limit=1)  
                            loan_lead.update(dct)  

                            # print_report = self.env.ref('capwise_crm.report_creditscore')
                            print_report = self.env.ref('capwise_crm.Credit_report')._render_qweb_pdf(self.ids)
                            print("print_report#############",print_report)
                            loan_lead.pdf_credit_score = base64.b64encode(print_report[0]) 


                else:
                    raise UserError(_('No Record found for this lead!')) 
            else:
                    raise UserError(_('No Record found for this lead!'))          


    def _format_date_change(self, date_format):
        print("date_format#@@@@@@@@@@@@@@@@@@@@@@",date_format)
        if date_format:
            date_return = date_format[6:8] + "/" + date_format[4:6] + "/" + date_format[0:4]
            print("vvvvvvvvvvvvvvvvvvvvvvv",date_return)
            return date_return     

                    
    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        # retrieve team_id from the context and write the domain
        # - ('id', 'in', stages.ids): add columns that should be present
        # - OR ('fold', '=', False): add default columns that are not folded
        # - OR ('team_ids', '=', team_id), ('fold', '=', False) if team_id: add team columns that are not folded
        team_id = self._context.get('default_team_id')
        if team_id:
            search_domain = ['|', ('id', 'in', stages.ids), '|', ('team_id', '=', False), ('team_id', '=', team_id)]
        else:
            search_domain = ['|', ('id', 'in', stages.ids), ('team_id', '=', False)]

        # perform search
        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    @api.depends('activity_date_deadline')
    def _compute_kanban_state(self):
        today = date.today()
        for lead in self:
            kanban_state = 'grey'
            if lead.activity_date_deadline:
                lead_date = fields.Date.from_string(lead.activity_date_deadline)
                if lead_date >= today:
                    kanban_state = 'green'
                else:
                    kanban_state = 'red'
            lead.kanban_state = kanban_state

    @api.depends('company_id')
    def _compute_user_company_ids(self):
        all_companies = self.env['res.company'].search([])
        for lead in self:
            if not lead.company_id:
                lead.user_company_ids = all_companies
            else:
                lead.user_company_ids = lead.company_id

    @api.depends('user_id', 'type')
    def _compute_team_id(self):
        """ When changing the user, also set a team_id or restrict team id
        to the ones user_id is member of. """
        for lead in self:
            # setting user as void should not trigger a new team computation
            if not lead.user_id:
                continue
            user = lead.user_id
            if lead.team_id and user in (lead.team_id.member_ids | lead.team_id.user_id):
                continue
            team_domain = [('use_leads', '=', True)] if lead.type == 'lead' else [('use_opportunities', '=', True)]
            team = self.env['crm.team']._get_default_team_id(user_id=user.id, domain=team_domain)
            lead.team_id = team.id

    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        user_ids = self.env['res.users'].browse(self.env.user.id)
        if not user_ids.phone:
            raise UserError(_('Kindly contact your manager to upload your phone number'))
        headers = {
            "mobile": str(user_ids.phone),
            "password": "welcome1234"
        }
        response = requests.post("https://api.finbii.com/partners/login", json=headers)
        token = json.loads(response.content).get('token')
        if self.lead_id:
            lead_status = {
                # "institution_name"  : leads.name,
                # "institution_logo"  : leads.logo,
                # "crm_institution_id" : ,
                # "institution_product_associate" : leads.product_associate,
                # "institution_max_percentage" : leads.max_percentage,
                # "institution_vendor_name" : leads.vendor_name,
                # "institution_description" : leads.description,
                # "institution_location_pin_Code" : leads.location_pin_Code,
                # "institution_gst_number" : leads.gst_number,
                # "institution_spock_name" : leads.spock_name,
                # "institution_spock_number" : leads.spock_number,
                # "institution_spock_email" : leads.spock_email,
                # "institution_upload_signed_agreement_copy" : leads.upload_signed_agreement_copy,
                # "institution_invoice_generation_date" : leads.invoice_generation_date,

                "leadId" : self.lead_id,
                "loanType" : self.loan_type,
                "leadStatus"  : self.stage_id.name,
                "lead_remark" : self.description
            }
            print("lead_status@@@@@@@@@@@@@@@@@@@",lead_status)
            response = requests.post("https://api.finbii.com/lead-update",headers={'Authorization': "Bearer %s" % token}, json=lead_status)
        

    @api.depends('user_id', 'team_id')
    def _compute_company_id(self):
        """ Compute company_id coherency. """
        for lead in self:
            proposal = lead.company_id

            # invalidate wrong configuration
            if proposal:
                # company not in responsible companies
                if lead.user_id and proposal not in lead.user_id.company_ids:
                    proposal = False
                # inconsistent
                if lead.team_id.company_id and proposal != lead.team_id.company_id:
                    proposal = False
                # void company on team and no assignee
                if lead.team_id and not lead.team_id.company_id and not lead.user_id:
                    proposal = False
                # no user and no team -> void company and let assignment do its job
                if not lead.team_id and not lead.user_id:
                    proposal = False

            # propose a new company based on responsible, limited by team
            if not proposal:
                if lead.user_id:
                    proposal = lead.team_id.company_id or lead.user_id.company_id
                elif lead.team_id:
                    proposal = lead.team_id.company_id
                else:
                    proposal = False

            # set a new company
            if lead.company_id != proposal:
                lead.company_id = proposal

    # @api.depends('team_id', 'type')
    # def _compute_stage_id(self):
    #     for lead in self:
    #         if not lead.stage_id:
    #             lead.stage_id = lead._stage_find(domain=[('fold', '=', False)]).id


    def send_mis_report(self):
        filename = 'MIS_Report.xls'
        string = 'MIS_Report.xls'
        wb = xlwt.Workbook(encoding='utf-8')
        worksheet = wb.add_sheet(string)
        header_bold = xlwt.easyxf("font: bold on; pattern: pattern solid, fore_colour gray25;")
        cell_format = xlwt.easyxf()
        filename = 'MIS_Report_loan_%s.xls' % date.today()
        rested = self.env['capwise.lead'].search([])
        row = 1
        worksheet.write(0, 0, 'Loan Type', header_bold)
        worksheet.write(0, 1, 'Loan Id', header_bold)
        worksheet.write(0, 2, 'Customer Name', header_bold)
        worksheet.write(0, 3, 'Phone', header_bold)
        worksheet.write(0, 4, 'Gender', header_bold)
        worksheet.write(0, 5, 'Dsa', header_bold)
        worksheet.write(0, 6, 'CSM', header_bold)
        worksheet.write(0, 7, 'ASM', header_bold)
        worksheet.write(0, 8, 'Regional Head', header_bold)
        worksheet.write(0, 9, 'Login Date With Bank / NBFC', header_bold)
        worksheet.write(0, 10, 'Operation Status', header_bold)
        worksheet.write(0, 11, 'Login Amount', header_bold)
        worksheet.write(0, 12, 'Sanction Date', header_bold)
        worksheet.write(0, 13, 'Sanction Amount', header_bold)
        worksheet.write(0, 14, 'Disbursed Date', header_bold)
        worksheet.write(0, 15, 'Disbursed Amount', header_bold)
        worksheet.write(0, 16, 'Status', header_bold)
        worksheet.write(0, 17, 'File Pickup Date', header_bold)
        worksheet.write(0, 18, 'File Submission Date', header_bold)
        worksheet.write(0, 19, 'Pendencies', header_bold)
        worksheet.write(0, 20, 'Pendency Complete Date', header_bold)
        # v.onboard_date >= (datetime.today().date().replace(day=1) - relativedelta(months=1)) and v.onboard_date <= (datetime.today().date() - relativedelta(months=1))
        for material_line_id in rested.filtered(lambda v: v.login_date.date() >= (datetime.today().date() - relativedelta(months=1)) and v.login_date.date() <= date.today()):
            worksheet.write(row, 0, material_line_id.loan_type or '')
            worksheet.write(row, 1, material_line_id.lead_id or '')
            worksheet.write(row, 2, material_line_id.name or '')
            worksheet.write(row, 3, material_line_id.phone1 or '')
            worksheet.write(row, 4, material_line_id.p_gender or '')
            worksheet.write(row, 5, material_line_id.dsa_id.name or '')
            worksheet.write(row, 6, material_line_id.user_id.name or '')
            worksheet.write(row, 7, material_line_id.team_id.name or '')
            worksheet.write(row, 8, material_line_id.regional_head.name or '')
            worksheet.write(row, 9, str(material_line_id.login_date_with_Bank_NBFC) or '')
            worksheet.write(row, 10, str(material_line_id.new_status_operation) or '')
            worksheet.write(row, 11, material_line_id.expected_revenue or '')
            worksheet.write(row, 12, str(material_line_id.sanction_date) or '')
            worksheet.write(row, 13, material_line_id.sanction_amount or '')
            worksheet.write(row, 14, str(material_line_id.disb_Date) or '')
            worksheet.write(row, 15, material_line_id.dis_amount or '')
            worksheet.write(row, 16, str(material_line_id.stage_id.name) or '')
            worksheet.write(row, 17, str(material_line_id.file_pick_up_date) or '')
            worksheet.write(row, 18, str(material_line_id.file_submission_date) or '')
            worksheet.write(row, 19, str(material_line_id.pendencies) or '')
            worksheet.write(row, 20, str(material_line_id.pendency_complete_date) or '')
            row += 1
        fp = io.BytesIO()
        print("fp@@@@@@@@@@@@@@@@@@",fp)
        wb.save(fp)
        out = base64.encodebytes(fp.getvalue())
        print("out@@@@@@@@@@@@@####################",out)
        ir_mail_server = self.env['ir.mail_server']
        channe_target = self.env['crm.team'].browse(1)
        channel_onboard = self.env['crm.lead'].search([("team_id","=",1)]).filtered(lambda v: v.onboard_date and v.onboard_date >= datetime.today().date().replace(day=1) and v.onboard_date <= datetime.today().date())
        lmsd_channel_onboard = self.env['crm.lead'].search([("team_id","=",1)]).filtered(lambda v: v.onboard_date and v.onboard_date >= (datetime.today().date().replace(day=1) - relativedelta(months=1)) and v.onboard_date <= (datetime.today().date() - relativedelta(months=1)))
        
        channe_target_m = self.env['crm.team'].browse(5)
        channel_onboard_m = self.env['crm.lead'].search([("team_id","=",5)]).filtered(lambda v: v.onboard_date and v.onboard_date >= datetime.today().date().replace(day=1) and v.onboard_date <= datetime.today().date())
        lmsd_channel_onboard_m = self.env['crm.lead'].search([("team_id","=",5)]).filtered(lambda v: v.onboard_date and v.onboard_date >= (datetime.today().date().replace(day=1) - relativedelta(months=1)) and v.onboard_date <= (datetime.today().date() - relativedelta(months=1)))
        mail_server_ids = ir_mail_server.sudo().search([], order='sequence', limit=1)
        shortfall = channe_target.channel_lead_target -  len(channel_onboard.mapped("id"))
        shortfall_m = channe_target_m.channel_lead_target -  len(channel_onboard_m.mapped("id"))
        if mail_server_ids:
            mail = ir_mail_server.browse(mail_server_ids[0]).id
            attachment = {
                           'name': str(filename),
                           'display_name': str(filename),
                           'datas': out,
                           'type': 'binary'
                       }
            ir_id = self.env['ir.attachment'].create(attachment)
            attachments = [(a['display_name'], base64.b64decode(a['datas']), a['mimetype'])
                           for a in ir_id.sudo().read(['display_name', 'datas', 'mimetype'])]
            if mail and mail.smtp_user:

                tabular_fields = ["ASM", "Channel Target", "Channel Onboarded", "Shortfall", "Channel Onboarded (LMSD)"]
                tabular_table = PrettyTable()
                tabular_table.field_names = tabular_fields 
                tabular_table.add_row(["Garima Garg ",channe_target.channel_lead_target, len(channel_onboard.mapped("id")), shortfall, len(lmsd_channel_onboard.mapped("id"))])
                tabular_table.add_row(["Mohit Malhotra",channe_target_m.channel_lead_target, len(channel_onboard_m.mapped("id")), shortfall_m, len(lmsd_channel_onboard_m.mapped("id"))])
                tabular_table.add_row(["Total", (channe_target.channel_lead_target + channe_target_m.channel_lead_target), (len(channel_onboard.mapped("id")) + len(channel_onboard_m.mapped("id"))), (shortfall + shortfall_m), (len(lmsd_channel_onboard.mapped("id")) + len(lmsd_channel_onboard_m.mapped("id")))])
                my_message = tabular_table.get_html_string()

                print("my_message@@@@@@@@@@@@@@@@@@@@@@",my_message)

                channel_onboard_mtd = self.env['capwise.lead'].search([("team_id","=",1)]).filtered(lambda v: v.login_date.date() and v.login_date.date() >= datetime.today().date().replace(day=1) and v.login_date.date() <= datetime.today().date())
                login_amount = 0
                for amount in channel_onboard_mtd:
                    login_amount = login_amount + amount.expected_revenue

                channel_onboard_sac = self.env['capwise.lead'].search([("team_id","=",1)]).filtered(lambda v: v.sanction_date and v.sanction_date >= datetime.today().date().replace(day=1) and v.sanction_date <= datetime.today().date())
                login_amount_sac = 0
                for amount in channel_onboard_sac:
                    login_amount_sac = login_amount_sac + amount.expected_revenue


                channel_onboard_dis = self.env['capwise.lead'].search([("team_id","=",1)]).filtered(lambda v: v.disb_Date and v.disb_Date >= datetime.today().date().replace(day=1) and v.disb_Date <= datetime.today().date())
                login_amount_dis = 0
                for amount in channel_onboard_dis:
                    login_amount_dis = login_amount_dis + amount.expected_revenue    
                        
                lmsd_channel_onboard_dsb = self.env['capwise.lead'].search([("team_id","=",1)]).filtered(lambda v: v.disb_Date and v.disb_Date >= (datetime.today().date().replace(day=1) - relativedelta(months=1)) and v.disb_Date <= (datetime.today().date() - relativedelta(months=1)))
                login_amount_dis_lms = 0
                for amount in lmsd_channel_onboard_dsb:
                    login_amount_dis_lms = login_amount_dis_lms + amount.expected_revenue





                channel_onboard_mtd_m = self.env['capwise.lead'].search([("team_id","=",5)]).filtered(lambda v: v.login_date.date() and v.login_date.date() >= datetime.today().date().replace(day=1) and v.login_date.date() <= datetime.today().date())
                login_amount_m = 0
                for amount in channel_onboard_mtd_m:
                    login_amount_m = login_amount_m + amount.expected_revenue

                channel_onboard_sac_m = self.env['capwise.lead'].search([("team_id","=",5)]).filtered(lambda v: v.sanction_date and v.sanction_date and v.sanction_date >= datetime.today().date().replace(day=1) and v.sanction_date <= datetime.today().date())
                login_amount_sac_m = 0
                for amount in channel_onboard_sac_m:
                    login_amount_sac_m = login_amount_sac_m + amount.expected_revenue


                channel_onboard_dis_m = self.env['capwise.lead'].search([("team_id","=",5)]).filtered(lambda v: v.disb_Date and v.disb_Date >= datetime.today().date().replace(day=1) and v.disb_Date <= datetime.today().date())
                login_amount_dis_m = 0
                for amount in channel_onboard_dis_m:
                    login_amount_dis_m = login_amount_dis_m + amount.expected_revenue    
                        
                lmsd_channel_onboard_dsb_m = self.env['capwise.lead'].search([("team_id","=",5)]).filtered(lambda v: v.disb_Date and v.disb_Date >= (datetime.today().date().replace(day=1) - relativedelta(months=1)) and v.disb_Date <= (datetime.today().date() - relativedelta(months=1)))
                login_amount_dis_lms_m = 0
                for amount in lmsd_channel_onboard_dsb_m:
                    login_amount_dis_lms_m = login_amount_dis_lms_m + amount.expected_revenue


                tabular_fields_mtd = ["ASM", "MTD Login (Nos)", "Login Amt  (Lacs)" , "Sanction (Nos)", "Sanction Amt (Lacs)", "Volume Target (Lacs)", "MTD Volume (Nos)", "MTD Volume (Lacs)", "Volume (Lacs) (LMSD)"]
                tabular_table_mtd = PrettyTable()
                tabular_table_mtd.field_names = tabular_fields_mtd 
                tabular_table_mtd.add_row(["Garima Garg",len(channel_onboard_mtd.mapped("id")) , (login_amount / 100000), len(channel_onboard_sac.mapped("id")), (login_amount_sac / 100000), (channe_target.invoiced_target / 100000) ,len(channel_onboard_dis.mapped("id")) ,(login_amount_dis / 100000),  (login_amount_dis_lms / 100000)])
                tabular_table_mtd.add_row(["Mohit Malhotra",len(channel_onboard_mtd_m.mapped("id")) , (login_amount_m / 100000), len(channel_onboard_sac_m.mapped("id")), (login_amount_sac_m / 100000), (channe_target_m.invoiced_target / 100000) ,len(channel_onboard_dis_m.mapped("id")) ,(login_amount_dis_m / 100000),  (login_amount_dis_lms_m / 100000)])
                my_message_mtd = tabular_table_mtd.get_html_string()


                channel_onboard_btd = self.env['crm.lead'].search([("team_id","=",1)]).filtered(lambda v: v.onboard_date and v.onboard_date == datetime.today().date())

                channel_onboard_dis_btd = self.env['capwise.lead'].search([("team_id","=",1)]).filtered(lambda v: v.disb_Date and v.disb_Date == datetime.today().date())
                login_amount_btd = 0
                for amount in channel_onboard_dis_btd:
                    login_amount_btd = login_amount_btd + amount.expected_revenue 


                channel_onboard_btd_m = self.env['crm.lead'].search([("team_id","=",5)]).filtered(lambda v: v.onboard_date and v.onboard_date == datetime.today().date())

                channel_onboard_dis_btd_m = self.env['capwise.lead'].search([("team_id","=",5)]).filtered(lambda v: v.disb_Date and v.disb_Date == datetime.today().date())
                login_amount_btd_m = 0
                for amount in channel_onboard_dis_btd_m:
                    login_amount_btd_m = login_amount_btd_m + amount.expected_revenue 


                tabular_fields_btd = ["ASM", "BTD Channel Onboarded (Nos)", "BTD Disbursement Amt (Lacs)"]
                tabular_table_btd = PrettyTable()
                tabular_table_btd.field_names = tabular_fields_btd 
                tabular_table_btd.add_row(["Garima Garg ",  len(channel_onboard_btd.mapped("id")), (login_amount_btd / 100000)])
                tabular_table_btd.add_row(["Mohit Malhotra  ",len(channel_onboard_dis_btd_m.mapped("id")), (login_amount_btd_m / 100000)])
                my_message_btd = tabular_table_btd.get_html_string()

                channel_onboard_ytd = self.env['crm.lead'].search([("team_id","=",1)]).filtered(lambda v: v.onboard_date and v.onboard_date.year == datetime.today().date().year)

                channel_onboard_dis_ytd = self.env['capwise.lead'].search([("team_id","=",1)]).filtered(lambda v: v.disb_Date and v.disb_Date.year == datetime.today().date().year)
                login_amount_ytd = 0
                for amount in channel_onboard_dis_ytd:
                    login_amount_ytd = login_amount_ytd + amount.expected_revenue

                channel_onboard_ytd_m = self.env['crm.lead'].search([("team_id","=",5)]).filtered(lambda v: v.onboard_date and v.onboard_date.year == datetime.today().date().year)

                channel_onboard_dis_ytd_m = self.env['capwise.lead'].search([("team_id","=",5)]).filtered(lambda v: v.disb_Date and v.disb_Date.year == datetime.today().date().year)
                login_amount_ytd_m = 0
                for amount in channel_onboard_dis_ytd_m:
                    login_amount_ytd_m = login_amount_ytd_m + amount.expected_revenue 

                tabular_fields_ytd = ["ASM", "YTD Channel Onboarded (Nos)", "YTD Disbursement (Lacs)"]
                tabular_table_ytd = PrettyTable()
                tabular_table_ytd.field_names = tabular_fields_ytd 
                tabular_table_ytd.add_row(["Garima Garg ", len(channel_onboard_ytd.mapped("id")) , (login_amount_ytd / 100000)])
                tabular_table_ytd.add_row(["Mohit Malhotra  ", len(channel_onboard_ytd_m.mapped("id")) , (login_amount_ytd_m / 100000)])
                my_message_ytd = tabular_table_ytd.get_html_string()

                email_body = """\
                <html>
                    <head>

                    <style>
                        table, th, td {
                            border: 1px solid black;
                            border-collapse: collapse;
                            border-style: double;
                        }
                        th, td {
                            padding: 5px;
                            text-align: center;
                            border-style: double;    
                        }    
                        thead {
                        background-color: #0081c7;
                        color: #fff;
                            font-family: 'Roboto', sans-serif;
                        }

                    </style>
                    </head>
                <body>
                <p>
                 <p>Hello, </p>
                 <p></p>
                 <p>Dear Sir/Madam,</p>
                 <p>This is an automatic mail For the business snapshot added today in the CRM.
                 <br/>Kindly check the attached file.</p>
                   %s

                   <br/>

                   %s

                   <br/>

                   %s

                   <br/>

                   %s
                   <p>Thank You</p><p>Finbii Team</p>
                </p>
                </body>
                </html>
                """ % (my_message, my_message_mtd, my_message_btd, my_message_ytd)
                text = html2text.html2text(email_body)
                msg = ir_mail_server.build_email(
                                email_from=mail.smtp_user,
                                email_to=['anuj.chauhan@finbii.com', "nadeem.khan@finbii.com",  "aashish.dhiimaan@finbii.com", "min.gurung@finbii.com"],
                                subject='business snapshot',
                                body=email_body,
                                subtype='html',
                                attachments=attachments,
                                )
                message = ir_mail_server.send_email(msg, mail_server_id=mail.id)

    def action_pending(self):
        self.new_status_operation = 'pending'

    def action_hold(self):   
        self.operations_status = 'hold'    


    def action_approve(self):
        self.new_status_operation = 'approve'
        
    def action_decline(self):
        self.new_status_operation = 'decline'
    

    @api.depends('user_id')
    def _compute_date_open(self):
        for lead in self:
            lead.date_open = fields.Datetime.now() if lead.user_id else False

    @api.depends('stage_id')
    def _compute_date_last_stage_update(self):
        for lead in self:
            lead.date_last_stage_update = fields.Datetime.now()

    @api.depends('create_date', 'date_open')
    def _compute_day_open(self):
        """ Compute difference between create date and open date """
        leads = self.filtered(lambda l: l.date_open and l.create_date)
        others = self - leads
        others.day_open = None
        for lead in leads:
            date_create = fields.Datetime.from_string(lead.create_date).replace(microsecond=0)
            date_open = fields.Datetime.from_string(lead.date_open)
            lead.day_open = abs((date_open - date_create).days)

    @api.depends('create_date', 'date_closed')
    def _compute_day_close(self):
        """ Compute difference between current date and log date """
        leads = self.filtered(lambda l: l.date_closed and l.create_date)
        others = self - leads
        others.day_close = None
        for lead in leads:
            date_create = fields.Datetime.from_string(lead.create_date)
            date_close = fields.Datetime.from_string(lead.date_closed)
            lead.day_close = abs((date_close - date_create).days)

    @api.depends('partner_id')
    def _compute_name(self):
        for lead in self:
            if not lead.name and lead.partner_id and lead.partner_id.name:
                lead.name = _("%s's Loan") % lead.partner_id.name

    # @api.depends('partner_id')
    # def _compute_contact_name(self):
    #     """ compute the new values when partner_id has changed """
    #     for lead in self:
    #         lead.update(lead._prepare_contact_name_from_partner(lead.partner_id))

    # @api.depends('partner_id')
    # def _compute_partner_name(self):
    #     """ compute the new values when partner_id has changed """
    #     for lead in self:
    #         lead.update(lead._prepare_partner_name_from_partner(lead.partner_id))

    @api.depends('partner_id')
    def _compute_function(self):
        """ compute the new values when partner_id has changed """
        for lead in self:
            if not lead.function or lead.partner_id.function:
                lead.function = lead.partner_id.function

    @api.depends('partner_id')
    def _compute_title(self):
        """ compute the new values when partner_id has changed """
        for lead in self:
            if not lead.title or lead.partner_id.title:
                lead.title = lead.partner_id.title

    @api.depends('partner_id')
    def _compute_mobile(self):
        """ compute the new values when partner_id has changed """
        for lead in self:
            if not lead.mobile or lead.partner_id.mobile:
                lead.mobile = lead.partner_id.mobile

    @api.depends('partner_id')
    def _compute_website(self):
        """ compute the new values when partner_id has changed """
        for lead in self:
            if not lead.website or lead.partner_id.website:
                lead.website = lead.partner_id.website

    # @api.depends('partner_id')
    # def _compute_partner_address_values(self):
    #     """ Sync all or none of address fields """
    #     for lead in self:
    #         lead.update(lead._prepare_address_values_from_partner(lead.partner_id))

    # @api.depends('partner_id.email')
    # def _compute_email_from(self):
    #     for lead in self:
    #         if lead.partner_id.email and lead._get_partner_email_update():
    #             lead.email_from = lead.partner_id.email

    # def _inverse_email_from(self):
    #     for lead in self:
    #         if lead._get_partner_email_update():
    #             lead.partner_id.email = lead.email_from

    # @api.depends('partner_id.phone')
    # def _compute_phone(self):
    #     for lead in self:
    #         if lead.partner_id.phone and lead._get_partner_phone_update():
    #             lead.phone = lead.partner_id.phone

    # def _inverse_phone(self):
    #     for lead in self:
    #         if lead._get_partner_phone_update():
    #             lead.partner_id.phone = lead.phone

    # @api.depends('phone', 'country_id.code')
    # def _compute_phone_state(self):
    #     for lead in self:
    #         phone_status = False
    #         if lead.phone:
    #             country_code = lead.country_id.code if lead.country_id and lead.country_id.code else None
    #             try:
    #                 if phone_validation.phone_parse(lead.phone, country_code):  # otherwise library not installed
    #                     phone_status = 'correct'
    #             except UserError:
    #                 phone_status = 'incorrect'
    #         lead.phone_state = phone_status

    @api.depends('email_from')
    def _compute_email_state(self):
        for lead in self:
            email_state = False
            if lead.email_from:
                email_state = 'incorrect'
                for email in email_split(lead.email_from):
                    if mail_validation.mail_validate(email):
                        email_state = 'correct'
                        break
            lead.email_state = email_state

    @api.depends('probability', 'automated_probability')
    def _compute_is_automated_probability(self):
        """ If probability and automated_probability are equal probability computation
        is considered as automatic, aka probability is sync with automated_probability """
        for lead in self:
            lead.is_automated_probability = tools.float_compare(lead.probability, lead.automated_probability, 2) == 0


    @api.depends('expected_revenue', 'probability')
    def _compute_prorated_revenue(self):
        for lead in self:
            lead.prorated_revenue = round((lead.expected_revenue or 0.0) * (lead.probability or 0) / 100.0, 2)

    @api.depends('recurring_revenue', 'recurring_plan.number_of_months')
    def _compute_recurring_revenue_monthly(self):
        for lead in self:
            lead.recurring_revenue_monthly = (lead.recurring_revenue or 0.0) / (lead.recurring_plan.number_of_months or 1)

    @api.depends('recurring_revenue_monthly', 'probability')
    def _compute_recurring_revenue_monthly_prorated(self):
        for lead in self:
            lead.recurring_revenue_monthly_prorated = (lead.recurring_revenue_monthly or 0.0) * (lead.probability or 0) / 100.0

    def _compute_calendar_event_count(self):
        if self.ids:
            meeting_data = self.env['calendar.event'].sudo().read_group([
                ('opportunity_id', 'in', self.ids)
            ], ['opportunity_id'], ['opportunity_id'])
            mapped_data = {m['opportunity_id'][0]: m['opportunity_id_count'] for m in meeting_data}
        else:
            mapped_data = dict()
        for lead in self:
            lead.calendar_event_count = mapped_data.get(lead.id, 0)

    
    # @api.depends('email_from', 'partner_id')
    # def _compute_partner_email_update(self):
    #     for lead in self:
    #         lead.partner_email_update = lead._get_partner_email_update()

    # @api.depends('phone', 'partner_id')
    # def _compute_partner_phone_update(self):
    #     for lead in self:
    #         lead.partner_phone_update = lead._get_partner_phone_update()

    # @api.onchange('phone', 'country_id', 'company_id')
    # def _onchange_phone_validation(self):
    #     if self.phone:
    #         self.phone = self.phone_get_sanitized_number(number_fname='phone', force_format='INTERNATIONAL') or self.phone

    

AVAILABLE_PRIORITIES = [
    ('0', 'Low'),
    ('1', 'Medium'),
    ('2', 'High'),
    ('3', 'Very High'),
]


class LoanStage(models.Model):
    """ Model for case stages. This models the main stages of a document
        management flow. Main CRM objects (leads, opportunities, project
        issues, ...) will now use only stages, instead of state and stages.
        Stages are for example used to display the kanban view of records.
    """
    _name = "loan.stage"
    _description = "Loan Stages"
    _rec_name = 'name'
    _order = "sequence, name, id"

    @api.model
    def default_get(self, fields):
        """ As we have lots of default_team_id in context used to filter out
        leads and opportunities, we pop this key from default of stage creation.
        Otherwise stage will be created for a given team only which is not the
        standard behavior of stages. """
        if 'default_team_id' in self.env.context:
            ctx = dict(self.env.context)
            ctx.pop('default_team_id')
            self = self.with_context(ctx)
        return super(LoanStage, self).default_get(fields)

    name = fields.Char('Stage Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")
    is_won = fields.Boolean('Is Won Stage?')
    requirements = fields.Text('Requirements', help="Enter here the internal requirements for this stage (ex: Offer sent to customer). It will appear as a tooltip over the stage's name.")
    team_id = fields.Many2one('crm.team', string='Sales Team', ondelete="set null",
        help='Specific team that uses this stage. Other teams will not be able to see or use this stage.')
    fold = fields.Boolean('Folded in Pipeline',
        help='This stage is folded in the kanban view when there are no records in that stage to display.')
    # This field for interface only
    team_count = fields.Integer('team_count')    


class CrmTeamDate(models.Model):

    _inherit = "crm.team"

    channel_lead_target = fields.Integer("Channel Lead target")    