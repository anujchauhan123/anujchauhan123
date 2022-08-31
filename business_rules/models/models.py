# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, time, date, timedelta


class BusinessRules(models.Model):
    _name = 'business_rules.business_rules'
    _description = 'Business Rule'

    fincial_institutions = fields.Many2one("financial.institution.onboard",string="Financial Institution")

    # business_loan = fields.Boolean(string="Business Loan"  )

    # personal_loan = fields.Boolean(string="Personal Loan")

    # home_loan = fields.Boolean(string="Home Loan")
  
    # loan_against_prop = fields.Boolean(string="Loan Against Prop")
    loan_type = fields.Selection([
        ('bl', 'Business Loan'),
        ('pl', 'Personal Loan'),
        ('hl', 'Home Loan'),
        ('lap', 'Loan Against Property'),], string='Loan Type')

    secured_loan = fields.Boolean("Secured Loan (HL/LAP)")

    profile_loan_proprietor=fields.Boolean(string="Proprietor")

    profile_loan_partnership=fields.Boolean(string="Partnership/LLP" )


    profile_loan_pvt_ltd=fields.Boolean(string="Pvt/Ltd")

    profile_loan_ltd=fields.Boolean(string="Ltd")

    profile_loan_salaried=fields.Boolean(string="Salaried")

    industry_margins_unsecured_loans_service=fields.Boolean(string="Service")
    industry_margins_unsecured_loans_service_from=fields.Char(string="From")
    # industry_margins_unsecured_loans_service_to=fields.Char(string="To")

    industry_margins_unsecured_loans_manufacturing=fields.Boolean(string="Manufacturing")
    industry_margins_unsecured_loans_manufacturing_from=fields.Char(string="From")
    # industry_margins_unsecured_loans_manufacturing_to=fields.Char(string="To")

    industry_margins_unsecured_loans_trade_retailer=fields.Boolean(string="Trader-Retailer")
    industry_margins_unsecured_loans_trade_retailer_from=fields.Char(string="From")
    # industry_margins_unsecured_loans_trade_retailer_to=fields.Char(string="To")

    industry_margins_unsecured_loans_trade_wholesaler=fields.Boolean(string="Trader- WholeSaler")
    industry_margins_unsecured_loans_trade_wholesaler_from=fields.Char(string="From")
    # industry_margins_unsecured_loans_trade_wholesaler_to=fields.Char(string="To")

  
    # inyears=fields.Boolean(string="In Years")

   
    vintage_in_work_business_loan=fields.Boolean(string="Business Loan")
    vintage_in_work_business_loan_from=fields.Integer(string="from")
 

    vintage_in_work_personal_loan=fields.Boolean(string="Personal Loan")
    vintage_in_work_personal_loan_from=fields.Integer(string="from")
    # vintage_in_work_personal_loan_to=fields.Char(string="to")


    vintage_in_work_business_home_loan_senp = fields.Boolean(string="Home Loan SENP/SEP")
    vintage_in_work_business_home_loan_senp_from = fields.Integer(string="from")
    # vintage_in_work_business_home_loan_senp_to=fields.Char(string="to")

    # vintage_in_work_business_home_loan_sep = fields.Boolean(string="Home Loan Sep")
    # vintage_in_work_business_home_loan_sep_from= fields.Char(string="from")
    # vintage_in_work_business_home_loan_sep_to = fields.Char(string="to")

    vintage_in_work_business_home_loan_salaried = fields.Boolean(string="Home Loan Salaried")
    vintage_in_work_business_home_loan_salaried_from = fields.Integer(string="from")
    # vintage_in_work_business_home_loan_salaried_to = fields.Char(string="to")

    vintage_in_work_business_lap_senp = fields.Boolean(string="Loan Against Property SENP/SENP")
    vintage_in_work_business_lap_senp_from = fields.Integer(string="from")
    # vintage_in_work_business_lap_senp_to = fields.Char(string="to")

    vintage_in_work_business_lap_salaried = fields.Boolean(string="Loan Against Property Salaried")
    vintage_in_work_business_lap_salaried_from = fields.Integer(string="from")
    # vintage_in_work_business_lap_salaried_to = fields.Char(string="to")

    servisable_non_servisable_pincode_unsecured_loan=fields.Boolean(string="Unsecured/Secured Loan")
    # servisable_non_servisable_pincode_secured_loan=fields.Boolean(string="Secured Loan")


    applicable_for_unsecured_loan_business_loan = fields.Selection([
        ('owned', 'Owned'),
        ('rented', 'Rented'),], string="Owned/Rented BL")
  

    applicable_for_unsecured_loan_personal_loan = fields.Selection([
        ('owned', 'Owned'),
        ('rented', 'Rented'),], string="Owned/Rented PL")


    
    age = fields.Boolean(string="Customer Age")
    age_from = fields.Integer(string="Age from")
    age_to = fields.Integer(string="Age to")

    tenor = fields.Boolean(string="Tenor (in Months)")
    tenor_from = fields.Integer(string="from")
    tenor_to = fields.Integer(string="to")

    loan_amount = fields.Boolean(string=" Loan Amount")
    loan_amount_from = fields.Float(string="from")
    loan_amount_to = fields.Float(string="to")

    property_details_secured_loan_home_loan = fields.Boolean(string=" Home Loan/LAP")

    market_value_secured_loan_market_value_require=fields.Boolean(string="Market Value Require")
    type_of_prop_ready_property=fields.Boolean(string = "Ready Property")
    under_construction_builder_prop=fields.Boolean(string="Under Construction Builder Prop")
    plot_const=fields.Boolean(string="Plot+Const")

    residential=fields.Boolean(string="Residential")
    non_resi_com_purchase=fields.Boolean(string="Non-Resi Prop Commercial Purchase")
    commercial=fields.Boolean(string="Commercial")
    institutional=fields.Boolean(string="Institutional")
    industrial=fields.Boolean(string="Industrial")
    others=fields.Boolean(string="Others- lal dora,agri,gram panchyat")




    bureau_score = fields.Boolean(string="Bureau")
    bureau_from = fields.Integer(string="from")
    bureau_to = fields.Integer(string="to")
    

    bureau_report_days_past_due_in_live_loans = fields.Boolean(string="Days Past Due Live Loans")
    bureau_report_days_past_due_in_live_loans_from = fields.Integer(string="from")
    bureau_report_days_past_due_in_live_loans_to = fields.Integer(string="to")

    bureau_report_SMA_restructed = fields.Boolean(string="SMA/SUB/LSS/SMA1 Restructed")
    bureau_report_SMA_restructed_from = fields.Integer(string="from")
    bureau_report_SMA_restructed_to = fields.Integer(string="to")

    # bureau_report_SUB_restructed = fields.Boolean(string="SUB Restructed")
    # bureau_report_SUB_restructed_from = fields.Char(string="from")
    # bureau_report_SUB_restructed_to = fields.Char(string="to")

    # bureau_report_LSS_restructed = fields.Boolean(string="LSS Restructed")
    # bureau_report_LSS_restructed_from = fields.Char(string="from")
    # bureau_report_LSS_restructed_to = fields.Char(string="to")

    # bureau_report_SMA1_restructed = fields.Boolean(string="SMA1 Restructed")
    # bureau_report_SMA1_restructed_from = fields.Char(string="from")
    # bureau_report_SMA1_restructed_to = fields.Char(string="to")

    bureau_report_Over_dues_in_creditcard_upto = fields.Boolean(string="Overdues In Credit Card Up To")
    bureau_report_Over_dues_in_creditcard_upto_from = fields.Char(string="from")
    bureau_report_Over_dues_in_creditcard_upto_to = fields.Char(string="to")

    enquiry=fields.Boolean("Enquiry")
    enquiry_from=fields.Char("from")


    itr = fields.Boolean(string="ITR in Years")
    itr_from = fields.Float(string="from")
    itr_to = fields.Float(string="to")


   
    banking = fields.Boolean(string="Banking (in Months)")
    banking_from = fields.Char(string="from")
    banking_to = fields.Char(string="to")

    gst = fields.Boolean(string="GST Return")
    gst_from = fields.Char(string="from")
    gst_to = fields.Char(string="to") 

    gst_cert = fields.Boolean(string="GST Certificate")
    rate_of_interest_from = fields.Float("Rate Of Interest From")
    rate_of_interest_to = fields.Float("Rate Of Interest To")

    business_proof = fields.Boolean(string="Business Proof")
    salary_slip = fields.Boolean(string="Salary Slip")
    form16 = fields.Boolean(string="Form 16")

    abb_business_loan=fields.Boolean(string="ABB_Business Loan")
    abb_business_loan_dates = fields.Char("abb business loan dates")
    abb_business_loan_from=fields.Char(string="from")
    abb_personal_loan=fields.Boolean(string="ABB_Personal Loan")
    abb_personal_loan_from=fields.Char(string="from")
    home_loan_abb=fields.Boolean(string="Home Loan/Loan Against Prop")
    home_loan_abb_from=fields.Char(string="from")


    # loan_against_prop_ab=fields.Boolean(string="Loan Against Property")
    # loan_against_prop_ab_from=fields.Char(string="from")
    bounce_emi=fields.Boolean(string="Bounce-EMI")
    bounce_emi_from=fields.Char(string="from")
    inward_bou=fields.Boolean(string="Inward/Outbound Bounce")
    inward_bou_from=fields.Char(string="from")
    min_turn_bl=fields.Boolean(string="Min Turnover BL")
    min_turn_bl_from=fields.Char(string="from")
    min_salary=fields.Boolean(string="Min Salary")
    min_salary_from=fields.Char(string="from")
    foir=fields.Boolean(string="FOIR")
    foir_from=fields.Char(string="from")
    noftrn = fields.Boolean(string="No. of Transaction")
    noftrn_from=fields.Char(string="from")

class DataFinbiiFinancial(models.Model):
    _name = 'financial.finbii'
    _description = 'Financial Finbii'


    financial_institue = fields.Many2one("financial.institution.onboard",string="Financial Institution")
    loan_type = fields.Selection([
        ('bl', 'Business Loan'),
        ('pl', 'Personal Loan'),
        ('hl', 'Home Loan'),
        ('lap', 'Loan Against Property'),], string='Loan Type')
    average_abb_six_month = fields.Float("average ABB 6 month")
    cheque_count = fields.Integer("Cheque Count")
    debit_transaction = fields.Float("Debit Transaction")
    credit_transaction = fields.Float("Credit Transaction")
    credit_submission = fields.Float("Credit Submission")
    roi_range = fields.Char("ROI Range")
    average_salary = fields.Float("Average Salary")
    fraud_indicate = fields.Boolean("Fraud Indicator")
    Solution = fields.Char("Per Lack EMI")
    elegible_loan_amount = fields.Char("Elegible Loan Amount(In Lac)")