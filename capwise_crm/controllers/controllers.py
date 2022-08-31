# -*- coding: utf-8 -*-
from odoo import http
from odoo import http
from odoo.http import request
from datetime import datetime, time, date, timedelta
import requests
import json
from subprocess import check_output
from bs4 import BeautifulSoup
import html
import logging
import re
import base64


_logger = logging.getLogger(__name__)


class CapwiseCrm(http.Controller):
    @http.route('/capwise/create_lead', type="json", auth='public',website=True, method=['POST'])
    def create_lead(self, **kw):
        _logger.info("Mobile APP create lead data****************%s" %request.jsonrequest)
        vals = {}
        email = False
        phone = False
        name = False
        if request.jsonrequest:
            kw = request.jsonrequest
            if 'bank_account_holder_name' in kw:
                vals['bank_account_holder_name'] = kw['bank_account_holder_name']
            if 'bank_account_number' in kw:
                vals['bank_account_number'] = kw['bank_account_number']
            if 'bank_name' in kw:
                vals['bank_name'] = kw['bank_name']
            if 'ifsc_code' in kw:
                vals['ifsc_code'] = kw['ifsc_code']            

            if 'address_house' in kw:
                vals['address_house'] = kw['address_house']
            if 'address_area' in kw:
                vals['address_area'] = kw['address_area']
            if 'address_pincode' in kw:
                vals['address_pincode'] = kw['address_pincode']
            if 'address_city' in kw:
                vals['address_city'] = kw['address_city']
            if 'address_state' in kw:
                vals['address_state'] = kw['address_state']
            if 'address_country' in kw:
                vals['address_country'] = kw['address_country']

            if 'gender' in kw:
                vals['gender'] = kw['gender'].lower()
                    
            if 'document_type' in kw:
                vals['document_type'] = kw['document_type']
            if 'document_proof' in kw:
                if 'base64,' in kw['document_proof']:
                    if "pdf" in kw['document_proof'].split('base64,')[0]:
                        vals['document_proof_pdf'] = kw['document_proof'].split('base64,')[1].replace(" ", "+")
                    else:    
                        vals['document_proof'] = kw['document_proof'].split('base64,')[1].replace(" ", "+")
            if 'partner_personal_occupation' in kw:
                vals['partner_personal_occupation'] = kw['partner_personal_occupation']
            if 'partner_type_of_firm' in kw:
                vals['partner_type_of_firm'] = kw['partner_type_of_firm']
            if 'partner_gst_no' in kw:
                vals['partner_gst_no'] = kw['partner_gst_no']
            if 'partner_business_name' in kw:
                vals['partner_business_name'] = kw['partner_business_name']
            if 'partner_product_associated' in kw:
                vals['partner_product_associated'] = kw['partner_product_associated']
            if 'partner_pan_card_proof' in kw:
                if 'base64,' in kw['partner_pan_card_proof']:
                    if "pdf" in kw['partner_pan_card_proof'].split('base64,')[0]:
                        vals['partner_pan_card_proof_pdf'] = kw['partner_pan_card_proof'].split('base64,')[1].replace(" ", "+")
                    else:
                        vals['partner_pan_card_proof'] = kw['partner_pan_card_proof'].split('base64,')[1].replace(" ", "+")
            if 'partner_aadhar_card_proof_front' in kw:
                if 'base64,' in kw['partner_aadhar_card_proof_front']:
                    if "pdf" in kw['partner_aadhar_card_proof_front'].split('base64,')[0]:
                        vals['partner_aadhar_card_proof_front_pdf'] = kw['partner_aadhar_card_proof_front'].split('base64,')[1].replace(" ", "+")
                    else:
                        vals['partner_aadhar_card_proof_front'] = kw['partner_aadhar_card_proof_front'].split('base64,')[1].replace(" ", "+")
            if 'partner_aadhar_card_proof_back' in kw:
                if 'base64,' in kw['partner_aadhar_card_proof_back']:
                    if "pdf" in kw['partner_aadhar_card_proof_back'].split('base64,')[0]:
                        vals['partner_aadhar_card_proof_back_pdf'] = kw['partner_aadhar_card_proof_back'].split('base64,')[1].replace(" ", "+")
                    else:
                        vals['partner_aadhar_card_proof_back'] = kw['partner_aadhar_card_proof_back'].split('base64,')[1].replace(" ", "+")
            if 'partner_document_type' in kw:
                vals['partner_document_type'] = kw['partner_document_type']
            if 'partner_pan_no' in kw:
                vals['partner_pan_no'] = kw['partner_pan_no']
            if 'partner_adhaar_no' in kw:
                vals['partner_adhaar_no'] = kw['partner_adhaar_no']
            if 'partner_dob' in kw:
                vals['partner_dob'] = kw['partner_dob']
            if 'partner_upload_photo' in kw:
                if 'base64,' in kw['partner_upload_photo']:
                    if "pdf" in kw['partner_upload_photo'].split('base64,')[0]:
                        vals['partner_upload_photo_pdf'] = kw['partner_upload_photo'].split('base64,')[1].replace(" ", "+")
                    else:
                        vals['partner_upload_photo'] = kw['partner_upload_photo'].split('base64,')[1].replace(" ", "+")
            if 'name' in kw:
                vals['name'] = kw['name']
                name = kw['name']
            if 'email_from' in kw:
                vals['email_from'] = kw['email_from']
                email = kw['email_from']
            if 'phone' in kw:
                vals['phone'] = kw['phone']
                phone = kw['phone']    
            source_id = request.env['utm.source'].sudo().search([('name','=', 'Finbii Dashboard')], limit=1)

            _logger.info("phone###########****************%s" %phone)
            if not phone:
                args = {'success': False, 'message': 'Send The phoney'}
                return args
            dsa_name = request.env['res.partner'].sudo().search([('phone','=', phone)], limit=1)
            _logger.info("dsa_name##@@@@@###########****************%s" %dsa_name)
            if not dsa_name:
                if not name:
                    args = {'success': False, 'message': 'Send The Name'}
                    return args       
                if not phone:
                    args = {'success': False, 'message': 'Send The Phone Number'}
                    return args              
                dsa_name = dsa_name.create({
                    'name' : name,
                    'phone': phone,
                    'email' : email,
                    })
            vals['partner_id'] = dsa_name.id

            if not source_id:
                source_id = request.env['utm.source'].sudo().create({
                        'name':'Finbii Dashboard'
                    })
            vals['source_id'] = source_id.id
            crm_obj = request.env['crm.lead'].sudo().search([('phone','=', phone)], limit=1)
            if crm_obj:
                if 'bank_account_number' in kw:
                    crm_obj.stage_id = 4
                    crm_obj.onboard_date = datetime.today()
                crm_obj.update(vals)
            if not crm_obj:
                if not name:
                    _logger.info("Mobilenamea****************%s" %name)
                    args = {'success': False, 'message': 'Send The Dsa Name'}
                    return args
                crm_obj = crm_obj.create(vals) 

        args = {'success': True, 'message': 'Success', 'ID':crm_obj.id}
        return args      

    @http.route('/capwise/create_loan', type="json", auth='public',website=True, method=['GET', 'POST'])
    def loan_lead(self, **kw):
        dct = {}
        dsa_name = False
        dsa_email = False
        dsa_name = False
        dsa_phone = False
        if request.jsonrequest:
            kw = request.jsonrequest
            _logger.info("dsa_name##@@@@@###########****************%s" %kw)
            if 'partner_mobile' in kw:
                dsa_phone   = kw['partner_mobile']
            if 'dsa_email' in kw:
                dsa_email   = kw['dsa_email']
            if 'loan_type' in kw:
                dct['loan_type'] = kw['loan_type'].lower()
                loan_type = kw['loan_type'].lower()
            if 'lead_id' in kw:
                lead_id = str(kw['lead_id'])
                dct['lead_id'] = kw['lead_id']
            if "lead_tenure_in_months" in kw:
                dct["lead_tenure_in_months"] = kw["lead_tenure_in_months"]    

            if "lead_loan_amount" in kw:
                dct['expected_revenue'] = kw['lead_loan_amount']
            if "lead_business_constitution" in kw:
                dct['constitution'] = kw['lead_business_constitution']    
            if "lead_profession_type" in kw:
                dct['profession'] = kw['lead_profession_type']
            if "lead_purpose" in kw:
                dct['purpose_of_loan'] = kw['lead_purpose']

            # if "creditScore" in kw:
            #     credit_loop = 0
            #     for credit in kw['creditScore']:
            #         if "vendor_payload_response":
            #             # json_data = json.loads(credit["vendor_payload_response"])
            #             # _logger.info("json_data##@@@@@###########****************%s" %json_data)
            #             if "{" in credit["vendor_payload_response"]:
            #                 print("data")
            #             else:    
            #                 data = request._get_credit_repot(lead_id, loan_type)
            #         credit_loop = credit_loop + 1   


            if isinstance(kw['lead_data'], list):
                data_line = 0
                for existing_obligation in kw['lead_data']:  
                    if data_line == 0:
                        if "lead_id" in existing_obligation:
                            dct['p_obligation_loan'] = True  
                        if 'loan_amount' in existing_obligation:
                            dct['p_obligation_loan_amount'] = existing_obligation['loan_amount'] 
                        if 'lead_bank_id' in existing_obligation:
                            dct['p_obligation_bank_name'] = existing_obligation['lead_bank_id']
                        if 'lead_type_of_loan' in existing_obligation:
                            dct['p_obligation_type_of_loan'] = existing_obligation['lead_type_of_loan']
                        if 'loan_account_number' in existing_obligation:
                            dct['p_obligation_account_number'] = existing_obligation['loan_account_number']
                        if 'emi' in existing_obligation:
                            dct['p_obligation_emi'] = existing_obligation['emi']
                        if 'lead_loan_opening_date' in existing_obligation:
                            dct['p_obligation_loan_opening_date'] = existing_obligation['lead_loan_opening_date']
                        if 'lead_tenure' in existing_obligation:
                            dct['p_obligation_tenure'] = existing_obligation['lead_tenure']
                        if 'lead_rate_of_interest' in existing_obligation:
                            dct['p_obligation_roi'] = existing_obligation['lead_rate_of_interest']
                        if 'lead_type_of_security' in existing_obligation:
                            dct['p_obligation_type_of_security'] = existing_obligation['lead_type_of_security']
                        if 'lead_current_outstanding_amount' in existing_obligation:
                            dct['p_obligation_current_out_standing_amount'] = existing_obligation['lead_current_outstanding_amount']
                    if data_line == 1:
                        if "lead_id" in existing_obligation:
                            dct['p2_obligation_loan'] = True
                        if "lead_bank_id" in existing_obligation:
                            dct['p2_obligation_bank_name'] = existing_obligation['lead_bank_id']
                        if "lead_type_of_loan" in existing_obligation:
                            dct['p2_obligation_type_of_loan'] = existing_obligation['lead_type_of_loan']
                        if "loan_amount" in existing_obligation:
                            dct['p2_obligation_loan_amount'] = existing_obligation['loan_amount']
                        if "loan_account_number" in existing_obligation:
                            dct['p2_obligation_account_number'] = existing_obligation['loan_account_number']
                        if "emi" in existing_obligation:
                            dct['p2_obligation_emi'] = existing_obligation['emi']
                        if "lead_loan_opening_date" in existing_obligation:
                            dct['p2_obligation_loan_opening_date'] = existing_obligation['lead_loan_opening_date']
                        if "lead_tenure" in existing_obligation:
                            dct['p2_obligation_tenure'] = existing_obligation['lead_tenure']
                        if "lead_rate_of_interest" in existing_obligation:
                            dct['p2_obligation_roi'] = existing_obligation['lead_rate_of_interest']
                        if "lead_type_of_security" in existing_obligation:
                            dct['p2_obligation_type_of_security'] = existing_obligation['lead_type_of_security']
                        if "lead_current_outstanding_amount" in existing_obligation:
                            dct['p2_obligation_current_out_standing_amount'] = existing_obligation['lead_current_outstanding_amount']
                        if "p3_obligation_loan" in existing_obligation:
                            dct['p3_obligation_loan'] = existing_obligation['p3_obligation_loan']
                        if "p3_obligation_bank_name" in existing_obligation:
                            dct['p3_obligation_bank_name'] = existing_obligation['p3_obligation_bank_name']
                        if "p3_obligation_loan_amount" in existing_obligation:
                            dct['p3_obligation_loan_amount'] = existing_obligation['p3_obligation_loan_amount']
                        if "p3_obligation_type_of_loan" in existing_obligation:
                            dct['p3_obligation_type_of_loan'] = existing_obligation['p3_obligation_type_of_loan']
                        if "p3_obligation_account_number" in existing_obligation:
                            dct['p3_obligation_account_number'] = existing_obligation['p3_obligation_account_number']
                        if "p3_obligation_emi" in existing_obligation:
                            dct['p3_obligation_emi'] = existing_obligation['p3_obligation_emi']
                        if "p3_obligation_loan_opening_date" in existing_obligation:
                            dct['p3_obligation_loan_opening_date'] = existing_obligation['p3_obligation_loan_opening_date']
                        if "p3_obligation_tenure" in existing_obligation:
                            dct['p3_obligation_tenure'] = existing_obligation['p3_obligation_tenure']
                        if "p3_obligation_roi" in existing_obligation:
                            dct['p3_obligation_roi'] = existing_obligation['p3_obligation_roi']
                        if "p3_obligation_type_of_security" in existing_obligation:
                            dct['p3_obligation_type_of_security'] = existing_obligation['p3_obligation_type_of_security']
                        if "p3_obligation_current_out_standing_amount" in existing_obligation:
                            dct['p3_obligation_current_out_standing_amount'] = existing_obligation['p3_obligation_current_out_standing_amount']
                        if "p3_obligation_credit_card" in existing_obligation:
                            dct['p3_obligation_credit_card'] = existing_obligation['p3_obligation_credit_card']
                        if "p3_obligation_current_credit_out_standing_amount" in existing_obligation:
                            dct['p3_obligation_current_credit_out_standing_amount'] = existing_obligation['p3_obligation_current_credit_out_standing_amount']
                        if "p3_obligation_credit_bank_name" in existing_obligation:
                            dct['p3_obligation_credit_bank_name'] = existing_obligation['p3_obligation_credit_bank_name']
                        if "p3_obligation_credit_limit" in existing_obligation:
                            dct['p3_obligation_credit_limit'] = existing_obligation['p3_obligation_credit_limit']
                    data_line = data_line + 1
            if 'lead_data' in kw:
                kw = kw['lead_data']
                if 'lead_id' in kw:
                    lead_id = str(kw['lead_id'])
                    dct['lead_id'] = kw['lead_id']
                if "lead_loan_amount" in kw:
                    dct['expected_revenue'] = kw['lead_loan_amount']
                if "lead_business_constitution" in kw:
                    dct['constitution'] = kw['lead_business_constitution']    
                if "lead_profession_type" in kw:
                    dct['profession'] = kw['lead_profession_type']
                if "lead_purpose" in kw:
                    dct['purpose_of_loan'] = kw['lead_purpose']
                if "lead_tenure_in_months" in kw:
                    dct["lead_tenure_in_months"] = kw["lead_tenure_in_months"]    
                if "lead_gender" in kw:
                    dct['p_gender'] = kw['lead_gender'].lower()    
                last = ""
                first = ""
                coapplicant_first = ""
                coapplicant_last = ""
                if "lead_firstname" in kw:
                    first = kw['lead_firstname']
                if "lead_lastname" in kw:
                    last = kw['lead_lastname']

                if "lead_firstname" in kw:
                    customer_name   = first + " " + last
                    dct['name'] = customer_name
                if 'lead_email' in kw:
                    customer_email   = kw['lead_email']
                    dct['email_from'] = kw['lead_email']
                if 'lead_phone' in kw:
                    customer_phone   = kw['lead_phone']
                    dct['phone1'] = kw['lead_phone']    

                 

                if "p_coapplicant_name_first" in kw:
                    coapplicant_first = kw['p_coapplicant_name_first']
                if "p_coapplicant_name_second" in kw:
                    coapplicant_last = kw['p_coapplicant_name_second']

                if 'p_coapplicant_name_first' in kw:
                    coapplicant_name = coapplicant_first + " " + coapplicant_last
                    dct['p_co_applicant_name'] = coapplicant_name       


                if "p_address_pincode" in kw:
                    dct['p_address_pincode'] = kw['p_address_pincode']
                if "p_coapplicant_pincode" in kw:
                    dct['p_coapplicant_pincode'] = kw['p_coapplicant_pincode']

                if "lap_lease_rental_discount" in kw:
                    dct['lap_lease_rental_discount'] = kw['lap_lease_rental_discount']  
                if "resident_indian_non_resident" in kw:
                    dct['resident_indian_non_resident'] = kw['resident_indian_non_resident']       
                        

                if 'banking_upload_passbook' in kw:
                    if 'base64,' in kw['banking_upload_passbook']:
                        if "pdf" in kw['banking_upload_passbook'].split('base64,')[0]:
                            dct['banking_upload_passbook_pdf'] = kw['banking_upload_passbook'].split('base64,')[1].replace(" ", "+")
                        else:
                            dct['banking_upload_passbook']   = kw['banking_upload_passbook'].split('base64,')[1].replace(" ", "+")
                if 'choose_finacial_instution' in kw:
                    dct['choose_finacial_instution'] = kw['choose_finacial_instution']
                if 'physical_journey' in kw:
                    dct['physical_journey'] = kw['physical_journey']
                if 'lead_document_type_id' in kw:
                    dct['b_kyc_document_type'] = kw['lead_document_type_id']
                if 'lead_address_document_1' in kw:
                    if 'base64,' in kw['lead_address_document_1']:
                        if "pdf" in kw['lead_address_document_1'].split('base64,')[0]:
                            dct['b_kyc_adhar_front_photo_pdf'] = kw['lead_address_document_1'].split('base64,')[1].replace(" ", "+")
                        else:
                            dct['b_kyc_adhar_front_photo'] = kw['lead_address_document_1'].split('base64,')[1].replace(" ", "+")
                if 'lead_address_document_2' in kw:
                    if 'base64,' in kw['lead_address_document_2']:
                        if "pdf" in kw['lead_address_document_2'].split('base64,')[0]:
                            dct['b_kyc_adhar_back_photo_pdf'] = kw['lead_address_document_2'].split('base64,')[1].replace(" ", "+")
                        else:
                            dct['b_kyc_adhar_back_photo'] = kw['lead_address_document_2'].split('base64,')[1].replace(" ", "+")
                if 'lead_pan_card_proof' in kw:
                    if 'base64,' in kw['lead_pan_card_proof']:
                        if "pdf" in kw['lead_pan_card_proof'].split('base64,')[0]:
                            dct['b_kyc_pan_card_front_pdf'] = kw['lead_pan_card_proof'].split('base64,')[1].replace(" ", "+")
                        else:
                            dct['b_kyc_pan_card_front'] = kw['lead_pan_card_proof'].split('base64,')[1].replace(" ", "+")

                if 'lead_upload_photo' in kw:
                    _logger.info("llllllllll###########****************%s" %kw['lead_upload_photo'])
                    if 'base64,' in kw['lead_upload_photo']:
                        _logger.info("kwwwwwwwwww###########****************%s" %kw['lead_upload_photo'])
                        if "pdf" in kw['lead_upload_photo'].split('base64,')[0]:
                            dct['b_lead_upload_photo_pdf'] = kw['lead_upload_photo'].split('base64,')[1].replace(" ", "+")
                        else:
                            _logger.info("jjjjjjjjjjjjjjjjjjj###########****************%s" %kw['lead_upload_photo'])
                            dct['b_lead_upload_photo'] = kw['lead_upload_photo'].split('base64,')[1].replace(" ", "+")              
                if 'lead_pan_number' in kw:
                    dct['b_kyc_pan_card_number'] = kw['lead_pan_number']
                if 'lead_date_of_birth' in kw:
                    dct['b_kyc_bate_of_birth'] = kw['lead_date_of_birth']
                if "address_type" in kw and kw["address_type"] == "CURRENT":    
                    if 'address_residence_type' in kw:
                        dct['b_address_owned_rented'] = kw['address_residence_type']
                    if 'address_house' in kw:
                        dct['b_address_house'] = kw['address_house']
                    if 'address_pincode' in kw:
                        dct['b_address_pincode'] = kw['address_pincode']
                    if 'address_area' in kw:
                        dct['b_address_street'] = kw['address_area']    
                    if 'address_city' in kw:
                        dct['b_address_city'] = kw['address_city']
                    if 'address_state' in kw:
                        dct['b_address_state'] = kw['address_state']

                if "address_type" in kw and kw["address_type"] == "PERMANENT": 
                    if 'b_address_bate_of_birth' in kw:
                        dct['b_address_bate_of_birth'] = kw['b_address_bate_of_birth']
                    if 'is_permanent_address' in kw:
                        dct['is_permanent_address'] = kw['is_permanent_address']


                    if "address_document_type" in kw:
                        dct["b_address_permanent_address_proof"] = kw["address_document_type"]    

                    if 'address_document_1' in kw:
                        dct['is_permanent_address'] = False
                        if 'base64,' in kw['address_document_1']:
                            if "pdf" in kw['address_document_1'].split('base64,')[0]:
                                dct['b_address_permanent_address_proof_front_pdf'] = kw['address_document_1'].split('base64,')[1].replace(" ", "+")
                            else:
                                dct['b_address_permanent_address_proof_front'] = kw['address_document_1'].split('base64,')[1].replace(" ", "+")

                    if 'address_document_2' in kw:
                        if 'base64,' in kw['address_document_2']:
                            if "pdf" in kw['address_document_2'].split('base64,')[0]:
                                dct['b_address_permanent_address_proof_back_pdf'] = kw['address_document_2'].split('base64,')[1].replace(" ", "+")
                            else:
                                dct['b_address_permanent_address_proof_back'] = kw['address_document_2'].split('base64,')[1].replace(" ", "+")        
                    if 'address_house' in kw:
                        dct['is_permanent_address'] = False
                        dct['b_address_permanent_house'] = kw['address_house']
                    if 'address_area' in kw:
                        dct['b_address_permanent_village'] = kw['address_area']
                    if 'address_pincode' in kw:
                        dct['is_permanent_address'] = False
                        dct['b_address_permanent_pincode'] = kw['address_pincode']
                    if 'address_city' in kw:
                        dct['b_address_permanent_city'] = kw['address_city']
                    if 'address_state' in kw:
                        dct['is_permanent_address'] = False
                        dct['b_address_permanent_state'] = kw['address_state']

                if 'lead_company_identification_number' in kw:
                    dct['b_business_company_identification_number'] = kw['lead_company_identification_number']
                if 'lead_gstin' in kw:
                    dct['b_business_gstin'] = kw['lead_gstin']
                if 'lead_business_name' in kw:
                    dct['b_business_business__name'] = kw['lead_business_name']
                if 'lead_business_constitution' in kw:
                    dct['b_business_business_constitution'] = kw['lead_business_constitution']
                if 'lead_date_of_in_corporation' in kw:
                    dct['b_business_date_of_incorporation'] = kw['lead_date_of_in_corporation']
                if 'lead_business_vintage' in kw:
                    dct['b_business_business_vintage'] = kw['lead_business_vintage']
                if 'lead_business_pan_number' in kw:
                    dct['b_business_business_pan_card'] = kw['lead_business_pan_number']
                if 'lead_tin_number' in kw:
                    dct['b_business_tin_number'] = kw['lead_tin_number']
                if 'lead_tan_number' in kw:
                    dct['b_business_tan_number'] = kw['lead_tan_number']
                if 'lead_current_year_turnover' in kw:
                    dct['b_business_current_year_turnover'] = kw['lead_current_year_turnover']
                if 'lead_previous_year_turnover' in kw:
                    dct['b_business_previous_year_turnover'] = kw['lead_previous_year_turnover']
                if 'lead_current_year_profit_after_tax' in kw:
                    dct['b_business_current_year_profit_after_tax'] = kw['lead_current_year_profit_after_tax']
                if 'lead_previous_year_profit_after_tax' in kw:
                    dct['b_business_previous_year_profit_after_tax'] = kw['lead_previous_year_profit_after_tax']
                if 'industry_id' in kw:
                    dct['b_business_industry_type'] = kw['industry_id']    

                if "industryType" in kw:
                    industry = kw['industryType']
                    if 'industryClass' in industry:
                        dct['b_business_industry_classs']  = industry['industryClass']
                    if 'industrySubClass' in industry:
                        dct['b_business_industry_sub_classs'] = industry['industrySubClass']
                
                if 'LEAD_ADDRESSES' in kw:
                    rit = 0
                    for lead_address in kw['LEAD_ADDRESSES']:
                        if rit == 0:
                            if 'address_residence_type' in lead_address:
                                dct['b_business_register_owned_rented'] = lead_address['address_residence_type']
                            if 'address_document_type' in lead_address:
                                dct['b_business_register_office_addess_proof'] = lead_address['address_document_type']
                            if 'address_document_1' in lead_address:
                                if 'base64,' in lead_address['address_document_1']:
                                    if "pdf" in lead_address['address_document_1'].split('base64,')[0]:
                                        dct['b_address_permanent_address_proof_front_pdf'] = lead_address['address_document_1'].split('base64,')[1].replace(" ", "+")
                                    else:
                                        dct['b_business_register_document_photo_front'] = lead_address['address_document_1'].split('base64,')[1].replace(" ", "+")
                            if 'address_document_2' in lead_address:
                                if 'base64,' in lead_address['address_document_2']:
                                    if "pdf" in lead_address['address_document_2'].split('base64,')[0]:
                                        dct['b_business_register_document_photo_back_pdf'] = lead_address['address_document_2'].split('base64,')[1].replace(" ", "+")
                                    else:
                                        dct['b_business_register_document_photo_back'] = lead_address['address_document_2'].split('base64,')[1].replace(" ", "+")
                            if 'address_pincode' in lead_address:
                                dct['b_business_register_pin_pincode'] = lead_address['address_pincode']
                            if 'address_house' in lead_address:
                                dct['b_business_register_building_number'] = lead_address['address_house']
                            if 'address_area' in lead_address:
                                dct['b_business_register_street'] = lead_address['address_area']
                            if 'address_area' in lead_address:
                                dct['b_business_register_city'] = lead_address['address_area'] 
                            if 'address_landmark' in lead_address:
                                dct['b_business_register_landmark'] = lead_address['address_landmark']       
                            if 'address_state' in lead_address:
                                dct['b_business_register_state'] = lead_address['address_state']    
                        if rit == 1:
                            if "address_area" in lead_address:
                                dct['b_business_register_current_office_street'] = lead_address['address_area']   
                            if 'address_city' in lead_address:
                                dct['b_business_register_current_office_city'] = lead_address['address_city'] 
                            if "address_state" in lead_address:
                                dct['b_business_register_current_office_state'] = lead_address['address_state']       
                            if 'b_business_register_current_office_addess_is_same' in lead_address:
                                dct['b_business_register_current_office_addess_is_same'] = lead_address['b_business_register_current_office_addess_is_same']

                            if 'address_residence_type' in lead_address:
                                dct['b_business_register_current_office_owned_rented'] = lead_address['address_residence_type']
                                
                            if 'address_document_type' in lead_address:
                                dct['b_business_register_current_office_address_proof'] = lead_address['address_document_type']
                            if 'address_document_1' in lead_address:
                                if 'base64,' in lead_address['address_document_1']:
                                    if "pdf" in lead_address['address_document_1'].split('base64,')[0]:
                                        dct['b_business_register_current_office_address_photo_front_pdf'] = lead_address['address_document_1'].split('base64,')[1].replace(" ", "+")
                                    else:
                                        dct['b_business_register_current_office_address_photo_front'] = lead_address['address_document_1'].split('base64,')[1].replace(" ", "+")
                            if 'address_document_2' in lead_address:
                                if 'base64,' in lead_address['address_document_2']:
                                    if "pdf" in lead_address['address_document_2'].split('base64,')[0]:
                                        dct['b_business_register_current_office_address_photo_back_pdf'] = lead_address['address_document_2'].split('base64,')[1].replace(" ", "+")
                                    else:
                                        dct['b_business_register_current_office_address_photo_back'] = lead_address['address_document_2'].split('base64,')[1].replace(" ", "+")
                            if 'address_house' in lead_address:
                                dct['b_business_register_current_office_building'] = lead_address['address_house']
                            
                            if "address_landmark" in lead_address:
                                dct['b_business_register_current_office_landmark'] = lead_address['address_landmark'] 
                            if "address_pincode" in lead_address:
                                dct['b_business_register_current_office_pincode'] = lead_address['address_pincode'] 
                        rit = rit + 1

                if "existing_obligation" in kw:
                    data_line = 0
                    for existing_obligation in kw['existing_obligation']:  
                        if data_line == 0:
                            if "lead_id" in existing_obligation:
                                dct['p_obligation_loan'] = True  
                            if 'loan_amount' in existing_obligation:
                                dct['p_obligation_loan_amount'] = existing_obligation['loan_amount'] 
                            if 'lead_bank_id' in existing_obligation:
                                dct['p_obligation_bank_name'] = existing_obligation['lead_bank_id']
                            if 'lead_type_of_loan' in existing_obligation:
                                dct['p_obligation_type_of_loan'] = existing_obligation['lead_type_of_loan']
                            if 'loan_account_number' in existing_obligation:
                                dct['p_obligation_account_number'] = existing_obligation['loan_account_number']
                            if 'emi' in existing_obligation:
                                dct['p_obligation_emi'] = existing_obligation['emi']
                            if 'lead_loan_opening_date' in existing_obligation:
                                dct['p_obligation_loan_opening_date'] = existing_obligation['lead_loan_opening_date']
                            if 'lead_tenure' in existing_obligation:
                                dct['p_obligation_tenure'] = existing_obligation['lead_tenure']
                            if 'lead_rate_of_interest' in existing_obligation:
                                dct['p_obligation_roi'] = existing_obligation['lead_rate_of_interest']
                            if 'lead_type_of_security' in existing_obligation:
                                dct['p_obligation_type_of_security'] = existing_obligation['lead_type_of_security']
                            if 'lead_current_outstanding_amount' in existing_obligation:
                                dct['p_obligation_current_out_standing_amount'] = existing_obligation['lead_current_outstanding_amount']
                        if data_line == 1:
                            if "lead_id" in existing_obligation:
                                dct['p2_obligation_loan'] = True
                            if "lead_bank_id" in existing_obligation:
                                dct['p2_obligation_bank_name'] = existing_obligation['lead_bank_id']
                            if "lead_type_of_loan" in existing_obligation:
                                dct['p2_obligation_type_of_loan'] = existing_obligation['lead_type_of_loan']
                            if "loan_amount" in existing_obligation:
                                dct['p2_obligation_loan_amount'] = existing_obligation['loan_amount']
                            if "loan_account_number" in existing_obligation:
                                dct['p2_obligation_account_number'] = existing_obligation['loan_account_number']
                            if "emi" in existing_obligation:
                                dct['p2_obligation_emi'] = existing_obligation['emi']
                            if "lead_loan_opening_date" in existing_obligation:
                                dct['p2_obligation_loan_opening_date'] = existing_obligation['lead_loan_opening_date']
                            if "lead_tenure" in existing_obligation:
                                dct['p2_obligation_tenure'] = existing_obligation['lead_tenure']
                            if "lead_rate_of_interest" in existing_obligation:
                                dct['p2_obligation_roi'] = existing_obligation['lead_rate_of_interest']
                            if "lead_type_of_security" in existing_obligation:
                                dct['p2_obligation_type_of_security'] = existing_obligation['lead_type_of_security']
                            if "lead_current_outstanding_amount" in existing_obligation:
                                dct['p2_obligation_current_out_standing_amount'] = existing_obligation['lead_current_outstanding_amount']
                            if "p3_obligation_loan" in existing_obligation:
                                dct['p3_obligation_loan'] = existing_obligation['p3_obligation_loan']
                            if "p3_obligation_bank_name" in existing_obligation:
                                dct['p3_obligation_bank_name'] = existing_obligation['p3_obligation_bank_name']
                            if "p3_obligation_loan_amount" in existing_obligation:
                                dct['p3_obligation_loan_amount'] = existing_obligation['p3_obligation_loan_amount']
                            if "p3_obligation_type_of_loan" in existing_obligation:
                                dct['p3_obligation_type_of_loan'] = existing_obligation['p3_obligation_type_of_loan']
                            if "p3_obligation_account_number" in existing_obligation:
                                dct['p3_obligation_account_number'] = existing_obligation['p3_obligation_account_number']
                            if "p3_obligation_emi" in existing_obligation:
                                dct['p3_obligation_emi'] = existing_obligation['p3_obligation_emi']
                            if "p3_obligation_loan_opening_date" in existing_obligation:
                                dct['p3_obligation_loan_opening_date'] = existing_obligation['p3_obligation_loan_opening_date']
                            if "p3_obligation_tenure" in existing_obligation:
                                dct['p3_obligation_tenure'] = existing_obligation['p3_obligation_tenure']
                            if "p3_obligation_roi" in existing_obligation:
                                dct['p3_obligation_roi'] = existing_obligation['p3_obligation_roi']
                            if "p3_obligation_type_of_security" in existing_obligation:
                                dct['p3_obligation_type_of_security'] = existing_obligation['p3_obligation_type_of_security']
                            if "p3_obligation_current_out_standing_amount" in existing_obligation:
                                dct['p3_obligation_current_out_standing_amount'] = existing_obligation['p3_obligation_current_out_standing_amount']
                            if "p3_obligation_credit_card" in existing_obligation:
                                dct['p3_obligation_credit_card'] = existing_obligation['p3_obligation_credit_card']
                            if "p3_obligation_current_credit_out_standing_amount" in existing_obligation:
                                dct['p3_obligation_current_credit_out_standing_amount'] = existing_obligation['p3_obligation_current_credit_out_standing_amount']
                            if "p3_obligation_credit_bank_name" in existing_obligation:
                                dct['p3_obligation_credit_bank_name'] = existing_obligation['p3_obligation_credit_bank_name']
                            if "p3_obligation_credit_limit" in existing_obligation:
                                dct['p3_obligation_credit_limit'] = existing_obligation['p3_obligation_credit_limit']
                        data_line = data_line + 1

                if "bank_details" in kw:
                    bank_loop = 0
                    for bank_details  in kw['bank_details']:
                        if bank_loop == 0:
                            if "bank_id" in bank_details:
                                dct['is_bank_1'] = True
                            if 'bank_id' in bank_details:
                                dct['is_bank_1'] = True
                                dct['p_bank_select_bank'] = bank_details['bank_id']
                            if 'lead_bank_account_type' in bank_details:
                                dct['is_bank_1'] = True
                                dct['p_bank_details_account_type'] = bank_details['lead_bank_account_type']
                            if 'lead_bank_statement_file' in bank_details:
                                if "base64," in bank_details['lead_bank_statement_file']:
                                    if "pdf" in bank_details['lead_bank_statement_file'].split('base64,')[0]:
                                        dct['p_bank_details_upload_statement_past_month_pdf'] = bank_details['lead_bank_statement_file'].split('base64,')[1].replace(" ", "+")
                                    else:
                                        dct['p_bank_details_upload_statement_past_month'] = bank_details['lead_bank_statement_file'].split('base64,')[1].replace(" ", "+")
                            if 'p_bank_is_bank_statement_is_password_protected' in bank_details:
                                dct['is_bank_1'] = True
                                dct['p_bank_is_bank_statement_is_password_protected'] = bank_details['p_bank_is_bank_statement_is_password_protected']
                            if 'lead_bank_statement_file_password' in bank_details:
                                dct['p_bank_password'] = bank_details['lead_bank_statement_file_password']

                        
                        if bank_loop == 1:
                            if "bank_id" in bank_details:
                                dct['is_bank_2'] = True
                                dct['p2_bank_select_bank'] = bank_details['bank_id']
                            if "lead_bank_account_type" in bank_details:
                                dct['is_bank_2'] = True
                                dct['p2_bank_details_account_type'] = bank_details['lead_bank_account_type']
                            if "lead_bank_statement_file" in bank_details:
                                if "base64," in bank_details['lead_bank_statement_file']:
                                    dct['is_bank_2'] = True
                                    if "pdf" in bank_details['lead_bank_statement_file'].split('base64,')[0]:
                                        dct['p2_bank_details_upload_statement_past_month_pdf'] = bank_details['lead_bank_statement_file'].split('base64,')[1].replace(" ", "+")
                                    else:
                                        dct['p2_bank_details_upload_statement_past_month'] = bank_details['p2_bank_is_bank_statement_is_password_protected'].split('base64,')[1].replace(" ", "+")
                            if "p2_bank_is_bank_statement_is_password_protected" in bank_details:
                                if "base64," in bank_details['lead_bank_statement_file']:
                                    dct['is_bank_2'] = True
                                    if "pdf" in bank_details['p2_bank_is_bank_statement_is_password_protected'].split('base64,')[0]:
                                        dct['p2_bank_is_bank_statement_is_password_protected_pdf'] = bank_details['p2_bank_is_bank_statement_is_password_protected'].split('base64,')[1].replace(" ", "+")
                                    else:
                                        dct['p2_bank_is_bank_statement_is_password_protected'] = bank_details['p2_bank_is_bank_statement_is_password_protected'].split('base64,')[1].replace(" ", "+")
                            if "lead_bank_statement_file_password" in bank_details:
                                dct['p2_bank_password'] = bank_details['lead_bank_statement_file_password']
                            if "bank_id" in bank_details:
                                dct['is_bank_2'] = True

                        if bank_loop ==2:
                            if "bank_id" in bank_details:
                                dct['is_bank_3'] = True     
                            if "p3_bank_select_bank" in bank_details:
                                dct['is_bank_3'] = True
                                dct['p3_bank_select_bank'] = bank_details['p3_bank_select_bank']
                            if "lead_bank_account_type" in bank_details:
                                dct['p3_bank_details_account_type'] = bank_details['lead_bank_account_type']
                            if "lead_bank_statement_file" in bank_details:
                                if "base64," in bank_details['lead_bank_statement_file']:
                                    dct['is_bank_3'] = True
                                    if "pdf" in bank_details['lead_bank_statement_file'].split('base64,')[0]:
                                        dct['p3_bank_details_upload_statement_past_month_pdf'] = bank_details['lead_bank_statement_file'].split('base64,')[1].replace(" ", "+")
                                    else:
                                        dct['p3_bank_details_upload_statement_past_month'] = bank_details['lead_bank_statement_file'].split('base64,')[1].replace(" ", "+")
                            if "p3_bank_is_bank_statement_is_password_protected" in bank_details:
                                dct['p3_bank_is_bank_statement_is_password_protected'] = bank_details['p3_bank_is_bank_statement_is_password_protected']
                            if "lead_bank_statement_file_password" in bank_details:
                                dct['p3_bank_password'] = bank_details['lead_bank_statement_file_password']  
                        bank_loop = bank_loop + 1          
                if "applicant" in kw:
                    applicant = kw['applicant']
                    if isinstance(kw['applicant'], list):
                        first_loop = 0
                        for app in kw['applicant']:
                            if "address_type" in app and app['address_type'] == "CURRENT":
                                if 'address_residence_type' in app:
                                    dct['p_address_residence_owner_rent'] = app['address_residence_type']
                                if 'p_address_number_of_year_in_current_residence' in app:
                                    dct['p_address_number_of_year_in_current_residence'] = app['p_address_number_of_year_in_current_residence']
                                if 'address_house' in app:
                                    dct['p_address_flat_house'] = app['address_house']
                                if 'address_area' in app:
                                    dct['p_address_street_lane'] = app['address_area']
                                if 'address_city' in app:
                                    dct['p_address_city'] = app['address_city']
                                if 'address_state' in app:
                                    dct['p_address_state'] = app['address_state']  
                                if "address_pincode" in app:
                                    dct['p_address_pincode'] = app['address_pincode'] 
                            if "address_type" in app and app['address_type'] == "PERMANENT":
                                if 'address_document_type' in app:
                                    dct['p_permant_address_proof'] = app['address_document_type']
                                if 'address_document' in app:
                                    if "base64," in app['address_document']:
                                        if "pdf" in app['address_document'].split('base64,')[0]:
                                            dct['p_permant_address_proof_photo_pdf'] = app['address_document'].split('base64,')[1].replace(" ", "+")
                                        else:
                                            dct['p_permant_address_proof_photo'] = app['address_document'].split('base64,')[1].replace(" ", "+")
                                if 'address_area' in app:
                                    dct['p_permant_street_lane'] = app['address_area']
                                if 'address_house' in app:
                                    dct['p_permant_flat_house'] = app['address_house']
                                if 'address_state' in app:
                                    dct['p_permant_state'] = app['address_state']
                                if 'address_city' in app:
                                    dct['p_permant_city'] = app['address_city']  
                                if 'address_pincode' in app:
                                    dct['p_permant_pin_code'] = app['address_pincode']     
                                        

                    if "applicant_gender" in applicant:
                        dct['p_gender'] = applicant['applicant_gender'].lower()    
                    last = ""
                    first = ""
                    if "applicant_first_name" in applicant:
                        first = applicant['applicant_first_name']
                    if "applicant_last_name" in applicant:
                        last = applicant['applicant_last_name']

                    if "applicant_first_name" in applicant:
                        customer_name   = first + " " + last
                        dct['name'] = customer_name
                    if 'applicant_email_id' in applicant:
                        customer_email   = applicant['applicant_email_id']
                        dct['email_from'] = applicant['applicant_email_id']
                        dct['p_personal_email_id'] = applicant['applicant_email_id']
                    if 'applicant_phone' in applicant:
                        customer_phone   = applicant['applicant_phone']
                        dct['phone1'] = applicant['applicant_phone'] 
                        dct['p_mobile_number'] = applicant['applicant_phone'] 
                    if 'applicant_father_husband_name' in applicant:
                        dct['p_father_husband_name'] = applicant['applicant_father_husband_name']
                    if 'applicant_educational_qualification' in applicant:
                        dct['p_educational_qualification'] = applicant['applicant_educational_qualification']
                    if 'applicant_marital_status' in applicant:
                        dct['p_marital_status'] = applicant['applicant_marital_status']
                    if 'applicant_current_address_document_type' in applicant:
                        dct['p_kyc_type_of_document'] = applicant['applicant_current_address_document_type']
                    if 'applicant_current_address_document_front' in applicant:
                        if 'base64,' in applicant['applicant_current_address_document_front']:
                            if "pdf" in applicant['applicant_current_address_document_front'].split('base64,')[0]:
                                dct['p_kyc_current_address_residence_proof_front_pdf'] = applicant['applicant_current_address_document_front'].split('base64,')[1].replace(" ", "+")
                            else:
                                dct['p_kyc_current_address_residence_proof_front'] = applicant['applicant_current_address_document_front'].split('base64,')[1].replace(" ", "+")
                    if 'applicant_current_address_document_back' in applicant:
                        if 'base64,' in applicant['applicant_current_address_document_back']:
                            if "pdf" in applicant['applicant_current_address_document_back'].split('base64,')[0]:
                                dct['p_kyc_current_address_residence_proof_back_pdf'] = applicant['applicant_current_address_document_back'].split('base64,')[1].replace(" ", "+")
                            else:
                                dct['p_kyc_current_address_residence_proof_back'] = applicant['applicant_current_address_document_back'].split('base64,')[1].replace(" ", "+")
                    if 'applicant_pan_card_document' in applicant:
                        if 'base64,' in applicant['applicant_pan_card_document']:
                            if "pdf" in applicant['applicant_pan_card_document'].split('base64,')[0]:
                                dct['p_kyc_current_pan_card_photo_pdf'] = applicant['applicant_pan_card_document'].split('base64,')[1].replace(" ", "+")
                            else:
                                dct['p_kyc_current_pan_card_photo'] = applicant['applicant_pan_card_document'].split('base64,')[1].replace(" ", "+")
                    if 'applicant_photo' in applicant:
                        if 'base64,' in applicant['applicant_photo']:
                            if "pdf" in applicant['applicant_photo'].split('base64,')[0]:
                                dct['p_applicant_photo_pdf'] = applicant['applicant_photo'].split('base64,')[1].replace(" ", "+")
                            else:
                                dct['p_applicant_photo'] = applicant['applicant_photo'].split('base64,')[1].replace(" ", "+")            
                    if 'applicant_pan_number' in applicant:
                        dct['p_kyc_current_pan_number'] = applicant['applicant_pan_number']
                    if 'applicant_date_of_birth' in applicant:
                        dct['p_kyc_current_date_of_birth'] = applicant['applicant_date_of_birth']    
                    
                    if 'applicant_current_organization_name' in applicant:
                        dct['p_business_name_of_current_orginization'] = applicant['applicant_current_organization_name']
                    if 'applicant_current_organization_type' in applicant:
                        dct['profession_categories_salaried'] = True
                        dct['p_busness_orginization_type'] = applicant['applicant_current_organization_type']
                    if 'applicant_industry_type' in applicant:
                        dct['p_busness_industry_type'] = applicant['applicant_industry_type']
                    if 'applicant_employment_type' in applicant:
                        dct['profession_categories_salaried'] = True
                        dct['p_business_employment_type'] = applicant['applicant_employment_type']
                    if 'applicant_employment_identification_number' in applicant:
                        dct['p_business_employeement_id_number'] = applicant['applicant_employment_identification_number']
                    if 'applicant_work_email_address' in applicant:
                        dct['profession_categories_salaried'] = True
                        dct['p_business_officail_email_id'] = applicant['applicant_work_email_address']
                    if 'applicant_monthly_net_salary' in applicant:
                        dct['profession_categories_salaried'] = True
                        dct['p_business_net_monthly_salary'] = applicant['applicant_monthly_net_salary']
                    if 'applicant_monthly_gross_salary' in applicant:
                        dct['p_business_gross_monthly_salary'] = applicant['applicant_monthly_gross_salary']
                    if 'applicant_designation' in applicant:
                        dct['profession_categories_salaried'] = True
                        dct['p_business_designation'] = applicant['applicant_designation']
                    if 'applicant_department' in applicant:
                        dct['p_business_department'] = applicant['applicant_department']
                    p_business_year_in_current_job_year = 0
                    p_business_year_in_current_job_month = 0
                    if 'applicant_total_exp_current_role' in applicant:
                        p_business_year_in_current_job_year = float(applicant['applicant_total_exp_current_role'])
                    if 'p_business_year_in_current_job_month' in applicant:
                        p_business_year_in_current_job_month = float(applicant['p_business_year_in_current_job_month']) / 12

                    if 'applicant_total_exp_current_role' in applicant:
                        dct['p_business_year_in_current_job'] = p_business_year_in_current_job_year  + p_business_year_in_current_job_month
                    
                    p_business_total_work_experiance_year = 0
                    p_business_total_work_experiance_month = 0

                    if 'applicant_total_exp' in applicant:
                        p_business_total_work_experiance_year = float(applicant['applicant_total_exp'])
                    if 'p_business_total_work_experiance_month' in applicant:
                        p_business_total_work_experiance_month = float(applicant['p_business_total_work_experiance_month']) / 12

                    if 'applicant_total_exp' in applicant:
                        dct['p_business_total_work_experiance'] = p_business_total_work_experiance_year + p_business_total_work_experiance_month    
                    
                    if "applicant_current_organization_name" in applicant:
                        dct['p_business_business_name'] = applicant['applicant_current_organization_name']
                    if "applicant_profession" in applicant:
                        dct['p_business_profession'] = applicant['applicant_profession']
                    if "applicant_registration_number" in applicant:
                        dct['profession_categories_sep'] = True
                        dct['p_business_registration_number'] = applicant['applicant_registration_number']
                    if "applicant_gst_number" in applicant:
                        dct['profession_categories_sep'] = True
                        dct['p_business_gstin'] = applicant['applicant_gst_number']
                    if "applicant_total_exp_current_role" in applicant:
                        dct['p_business_years_in_current_profession'] = applicant['applicant_total_exp_current_role']
                    if "applicant_professional_receipts" in applicant:
                        dct['profession_categories_sep'] = True
                        dct['p_business_gross_professional_receipts_as_per_ITR'] = applicant['applicant_professional_receipts']
                    if "p2_business_gross_professional_receipts_as_per_ITR" in applicant:
                        dct['p2_business_gross_professional_receipts_as_per_ITR'] = applicant['p2_business_gross_professional_receipts_as_per_ITR']
                    if "p3_business_gross_professional_receipts_as_per_ITR" in applicant:
                        dct['p3_business_gross_professional_receipts_as_per_ITR'] = applicant['p3_business_gross_professional_receipts_as_per_ITR']
                    if "applicant_work_email_address" in applicant:
                        dct['p_business_email_id'] = applicant['applicant_work_email_address']
                    if "applicant_work_phone" in applicant:
                        dct['p_business_phone_number'] = applicant['applicant_work_phone']
                    if "profession_categories_salaried" in kw:
                        dct['profession_categories_salaried'] = True
                    if "profession_categories_senp" in kw:
                        dct['profession_categories_senp'] = kw['profession_categories_senp']
                    if "profession_categories_sep" in kw:
                        dct['profession_categories_sep'] = kw['profession_categories_sep']    

                    if 'applicant_role' in applicant:
                        dct['p_business_i_am_a'] = applicant['applicant_role']
                    if 'applicant_constitution' in applicant:
                        dct['p_business_business_constitution'] = applicant['applicant_constitution']
                    if 'applicant_monthly_renumeration' in applicant:
                        dct['p_business_monthly_renumeration'] = applicant['applicant_monthly_renumeration']
                    if 'applicant_share_holding_percentage' in applicant:
                        dct['profession_categories_senp'] = True
                        dct['p_business_share_holding'] = applicant['applicant_share_holding_percentage']
                    if 'applicant_annual_income' in applicant:
                        dct['profession_categories_senp'] = True
                        dct['p_business_annual_income'] = applicant['applicant_annual_income']
                    if 'applicant_profit_percentage' in applicant:
                        dct['profession_categories_senp'] = True
                        dct['p_business_share_in_profit'] = applicant['applicant_profit_percentage']    
                    if "applicant_business_details" in applicant:
                        applicant_business_details  = applicant["applicant_business_details"]
                        if 'applicant_profit_percentage' in applicant_business_details:
                            dct['p_business_share_in_profit'] = applicant_business_details['applicant_profit_percentage']
                        if 'business_name' in applicant_business_details:
                            dct['p_business_business_name'] = applicant_business_details['business_name']
                        if 'business_industry_type' in applicant_business_details:
                            dct['p_business_industry_type'] = applicant_business_details['business_industry_type']
                        if 'business_industry_subclass' in applicant_business_details:
                            dct['p_business_industry_sub_class'] = applicant_business_details['business_industry_subclass']
                        if 'business_current_year_profit_after_tax' in applicant_business_details:
                            dct['p_business_profit_after_tax'] = applicant_business_details['business_current_year_profit_after_tax']
                        if 'business_previous_year_profit_after_tax' in applicant_business_details:
                            dct['p_business_previous_profit_after_tax'] = applicant_business_details['business_previous_year_profit_after_tax']
                        if 'business_current_year_turnover' in applicant_business_details:
                            dct['p_business_current_year_turnover'] = applicant_business_details['business_current_year_turnover']
                        if 'business_previous_year_turnover' in applicant_business_details:
                            dct['p_business_previous_year_turnover'] = applicant_business_details['business_previous_year_turnover']
                        if 'business_tin_number' in applicant_business_details:
                            dct['p_business_Cin_number'] = applicant_business_details['business_tin_number']
                        if 'business_gst_number' in applicant_business_details:
                            dct['p_business_gst_number'] = applicant_business_details['business_gst_number']
                        if 'business_pan_number' in applicant_business_details:
                            dct['p_business_business_pan'] = applicant_business_details['business_pan_number']
                        if 'business_tin_number' in applicant_business_details:
                            dct['p_business_tin_number'] = applicant_business_details['business_tin_number']
                        if 'business_tan_number' in applicant_business_details:
                            dct['p_business_tan_number'] = applicant_business_details['business_tan_number']
                        if 'p_business_nio_of_partner_director' in applicant_business_details:
                            dct['p_business_nio_of_partner_director'] = applicant_business_details['p_business_nio_of_partner_director']
                        if 'business_incorporation_date' in applicant_business_details:
                            dct['p_business_date_of_incorportaion'] = applicant_business_details['business_incorporation_date']
                        if 'business_vintage' in applicant_business_details:
                            dct['p_business_business_vintage'] = applicant_business_details['business_vintage']
                        if 'business_email' in applicant_business_details:
                            dct['p_business_email_id'] = applicant_business_details['business_email']
                        if 'business_phone' in applicant_business_details:
                            dct['p_business_phn_number'] = applicant_business_details['business_phone']
                        if 'p_business_year_of_current_business' in applicant_business_details:
                            dct['p_business_year_of_current_business'] = applicant_business_details['p_business_year_of_current_business']
                        if 'business_pos_enabled' in applicant_business_details:
                            dct['p_business_do_you_have_pos'] = applicant_business_details['business_pos_enabled']
                        if 'business_pos_monthly_sales' in applicant_business_details:
                            dct['p_business_if_year_what_is_your_monthly_card_swipe'] = applicant_business_details['business_pos_monthly_sales']    
                        
                    if "applicant_additional_income" in applicant:
                        data_applicant = 0
                        for applicant_additional_income in applicant['applicant_additional_income']:
                            if data_applicant == 0:
                                if 'income_amount' in applicant_additional_income:
                                    dct['p_business_additional_amount'] = applicant_additional_income['income_amount']
                                if 'income_source' in applicant_additional_income:
                                    dct['p_business_additional_source'] = applicant_additional_income['income_source']
                            if data_applicant == 1:
                                if 'income_amount' in applicant_additional_income:
                                    dct['p2_business_additional_amount'] = applicant_additional_income['income_amount']
                                if 'income_source' in applicant_additional_income:
                                    dct['p2_business_additional_source'] = applicant_additional_income['income_source']
                            data_applicant = data_applicant + 1    
                    if "applicant_business_addresses" in applicant:
                        vvfr = 0
                        for applicant_business_addresses in applicant['applicant_business_addresses']:
                            if "address_type" in applicant_business_addresses and applicant_business_addresses["address_type"] == "OFFICE":
                                if 'address_pincode' in applicant_business_addresses:
                                    dct['p_business_office_pin_code'] = applicant_business_addresses['address_pincode']
                                if 'address_house' in applicant_business_addresses:
                                    dct['p_business_office_building_numbr'] = applicant_business_addresses['address_house']
                                if 'address_area' in applicant_business_addresses:
                                    dct['p_business_office_street_lane'] = applicant_business_addresses['address_area']
                                if 'address_landmark' in applicant_business_addresses:
                                    dct['p_business_office_landmark'] = applicant_business_addresses['address_landmark']
                                if 'address_city' in applicant_business_addresses:
                                    dct['p_business_office_city'] = applicant_business_addresses['address_city']
                                if 'address_state' in applicant_business_addresses:
                                    dct['p_business_building_office_state'] = applicant_business_addresses['address_state']   
                            if "address_type" in applicant_business_addresses and applicant_business_addresses["address_type"] == "REGISTERED_OFFICE" or applicant_business_addresses["address_type"] == "REGISTERED":
                                if "address_pincode" in applicant_business_addresses:
                                    dct['p_business_register_pin_pincode'] = applicant_business_addresses['address_pincode']
                                if "address_house" in applicant_business_addresses:
                                    dct['p_business_register_building_number'] = applicant_business_addresses['address_house']
                                if "address_area" in applicant_business_addresses:
                                    dct['p_business_register_street'] = applicant_business_addresses['address_area']
                                if "address_landmark" in applicant_business_addresses:
                                    dct['p_business_register_landmark'] = applicant_business_addresses['address_landmark']
                                if "address_city" in applicant_business_addresses:
                                    dct['p_business_register_city'] = applicant_business_addresses['address_city']
                                if "address_state" in applicant_business_addresses:
                                    dct['p_business_register_state'] = applicant_business_addresses['address_state']
                            if "address_type" in applicant_business_addresses and applicant_business_addresses["address_type"] == "CORPORATE_OFFICE" or applicant_business_addresses["address_type"] == "CORPORATE":
                                if "address_pincode" in applicant_business_addresses:
                                    dct['p_business_corporate_register_pin_pincode'] = applicant_business_addresses['address_pincode']
                                if "address_house" in applicant_business_addresses:
                                    dct['p_business_corporate_register_building_number'] = applicant_business_addresses['address_house']
                                if "address_area" in applicant_business_addresses:
                                    dct['p_business_corporate_register_street'] = applicant_business_addresses['address_area']
                                if "address_landmark" in applicant_business_addresses:
                                    dct['p_business_corporate_register_landmark'] = applicant_business_addresses['address_landmark']
                                if "address_city" in applicant_business_addresses:
                                    dct['p_business_corporate_register_city'] = applicant_business_addresses['address_city']
                                if "address_state" in applicant_business_addresses:
                                    dct['p_business_corporate_register_state'] = applicant_business_addresses['address_state']            
                            vvfr = vvfr + 1
                    if 'loans' in applicant:
                        loan_ppd = 0
                        for loans in applicant['loans']: 
                            if loan_ppd == 0:
                                if 'loan_amount' in loans:
                                    dct['p_obligation_loan_amount'] = loans['loan_amount'] 
                                    dct['p_obligation_loan'] = True
                                if 'loan_bank_id' in loans:
                                    dct['p_obligation_loan'] = True
                                    dct['p_obligation_bank_name'] = loans['loan_bank_id']
                                if 'loan_type' in loans:
                                    dct['p_obligation_type_of_loan'] = loans['loan_type']
                                if 'loan_account_number' in loans:
                                    dct['p_obligation_account_number'] = loans['loan_account_number']
                                if 'loan_emi' in loans:
                                    dct['p_obligation_loan'] = True
                                    dct['p_obligation_emi'] = loans['loan_emi']
                                if 'loan_opening_date' in loans:
                                    dct['p_obligation_loan_opening_date'] = loans['loan_opening_date']
                                if 'loan_tenure_months' in loans:
                                    dct['p_obligation_tenure'] = loans['loan_tenure_months']
                                if 'loan_rate_of_interest' in loans:
                                    dct['p_obligation_loan'] = True
                                    dct['p_obligation_roi'] = loans['loan_rate_of_interest']
                                if 'loan_type_of_security' in loans:
                                    dct['p_obligation_type_of_security'] = loans['loan_type_of_security']
                                if 'loan_current_outstanding_amount' in loans:
                                    dct['p_obligation_loan'] = True
                                    dct['p_obligation_current_out_standing_amount'] = loans['loan_current_outstanding_amount'] 
                                

                            if loan_ppd == 1:   
                                if "loan_bank_id" in loans:
                                    dct['p2_obligation_bank_name'] = loans['loan_bank_id']
                                if "loan_type" in loans:
                                    dct['p2_obligation_type_of_loan'] = loans['loan_type']
                                if "loan_amount" in loans:
                                    dct['p2_obligation_loan'] = True
                                    dct['p2_obligation_loan_amount'] = loans['loan_amount']
                                if "loan_account_number" in loans:
                                    dct['p2_obligation_loan'] = True
                                    dct['p2_obligation_account_number'] = loans['loan_account_number']
                                if "loan_emi" in loans:
                                    dct['p2_obligation_emi'] = loans['loan_emi']
                                if "loan_opening_date" in loans:
                                    dct['p2_obligation_loan'] = True
                                    dct['p2_obligation_loan_opening_date'] = loans['loan_opening_date']
                                if "loan_tenure_months" in loans:
                                    dct['p2_obligation_tenure'] = loans['loan_tenure_months']
                                if "loan_rate_of_interest" in loans:
                                    dct['p2_obligation_loan'] = True
                                    dct['p2_obligation_roi'] = loans['loan_rate_of_interest']
                                if "loan_type_of_security" in loans:
                                    dct['p2_obligation_type_of_security'] = loans['loan_type_of_security']
                                if "loan_current_outstanding_amount" in loans:
                                    dct['p2_obligation_current_out_standing_amount'] = loans['loan_current_outstanding_amount']
                            
                            if loan_ppd == 2:
                                if "loan_bank_id" in loans:
                                    dct['p3_obligation_loan'] = True
                                    dct['p3_obligation_bank_name'] = loans['loan_bank_id']
                                if "loan_amount" in loans:
                                    dct['p3_obligation_loan_amount'] = loans['loan_amount']
                                if "loan_type" in loans:
                                    dct['p3_obligation_loan'] =  True
                                    dct['p3_obligation_type_of_loan'] = loans['loan_type']
                                if "loan_account_number" in loans:
                                    dct['p3_obligation_loan'] = True
                                    dct['p3_obligation_account_number'] = loans['loan_account_number']
                                if "loan_emi" in loans:
                                    dct['p3_obligation_emi'] = loans['loan_emi']
                                if "loan_opening_date" in loans:
                                    dct['p3_obligation_loan'] = True
                                    dct['p3_obligation_loan_opening_date'] = loans['loan_opening_date']
                                if "loan_tenure_months" in loans:
                                    dct['p3_obligation_tenure'] = loans['loan_tenure_months']
                                if "loan_rate_of_interest" in loans:
                                    dct['p3_obligation_roi'] = loans['loan_rate_of_interest']
                                if "loan_type_of_security" in loans:
                                    dct['p3_obligation_loan'] = True
                                    dct['p3_obligation_type_of_security'] = loans['loan_type_of_security']
                                if "loan_current_outstanding_amount" in loans:
                                    dct['p3_obligation_current_out_standing_amount'] = loans['loan_current_outstanding_amount']
                            loan_ppd = loan_ppd + 1
                                    
                    if "credit_cards" in applicant:
                        for credit_cards in applicant["credit_cards"]: 
                            if "cc_current_outstanding_amount" in credit_cards:
                                dct['p3_obligation_credit_card'] = True
                                dct['p3_obligation_current_credit_out_standing_amount'] = credit_cards['cc_current_outstanding_amount']
                            if "cc_bank_id" in credit_cards:
                                dct['p3_obligation_credit_card'] = True
                                dct['p3_obligation_credit_bank_name'] = credit_cards['cc_bank_id']
                            if "cc_credit_limit" in credit_cards:
                                dct['p3_obligation_credit_limit'] = credit_cards['cc_credit_limit']
                    if isinstance(kw['applicant'], list):
                        banl_test_loop = 0
                        for bank_details in applicant: 
                            if banl_test_loop == 0:
                                if 'account_bank_id' in bank_details:
                                    dct['is_bank_1'] = True
                                    dct['p_bank_select_bank'] = bank_details['account_bank_id']
                                if 'account_type' in bank_details:
                                    dct['is_bank_1'] = True
                                    dct['p_bank_details_account_type'] = bank_details['account_type']
                                if 'account_statement_document' in bank_details:
                                    dct['is_bank_1'] = True
                                    if 'base64,' in bank_details['account_statement_document']:
                                        if "pdf" in bank_details['account_statement_document'].split('base64,')[0]:
                                            dct['p_bank_details_upload_statement_past_month_pdf'] = bank_details['account_statement_document'].split('base64,')[1].replace(" ", "+")
                                        else:
                                            dct['p_bank_details_upload_statement_past_month'] = bank_details['account_statement_document'].split('base64,')[1].replace(" ", "+")
                                if 'account_statement_document_password_protected' in bank_details:
                                    dct['is_bank_1'] = True
                                    dct['p_bank_is_bank_statement_is_password_protected'] = bank_details['account_statement_document_password_protected']
                                if 'account_statement_document_password' in bank_details:
                                    dct['is_bank_1'] = True
                                    dct['p_bank_password'] = bank_details['account_statement_document_password']   
                            if banl_test_loop == 1:
                                # if "is_bank_3" in bank_details:
                                #     dct['is_bank_3'] = bank_details['is_bank_3']    
                                if "account_bank_id" in bank_details:
                                    dct['is_bank_2'] = True
                                    dct['p2_bank_select_bank'] = bank_details['account_bank_id']
                                if "account_type" in bank_details:
                                    dct['is_bank_2'] = True
                                    dct['p2_bank_details_account_type'] = bank_details['account_type']
                                if 'account_statement_document' in bank_details:
                                    dct['is_bank_2'] = True
                                    if 'base64,' in bank_details['account_statement_document']:
                                        if "pdf" in bank_details['account_statement_document'].split('base64,')[0]:
                                            dct['p2_bank_details_upload_statement_past_month_pdf'] = bank_details['account_statement_document'].split('base64,')[1].replace(" ", "+")
                                        else:
                                            dct['p2_bank_details_upload_statement_past_month'] = bank_details['account_statement_document'].split('base64,')[1].replace(" ", "+")                                            
                                if "account_statement_document_password_protected" in bank_details:
                                    dct['is_bank_2'] = True
                                    dct['p2_bank_is_bank_statement_is_password_protected'] = bank_details['account_statement_document_password_protected']
                                if "account_statement_document_password" in bank_details:
                                    dct['is_bank_2'] = True
                                    dct['p2_bank_password'] = bank_details['account_statement_document_password']
                            if banl_test_loop == 2:
                                if "account_bank_id" in bank_details:
                                    dct['p3_bank_select_bank'] = bank_details['account_bank_id']
                                if "account_type" in bank_details:
                                    dct['p3_bank_details_account_type'] = bank_details['account_type']
                                if 'account_statement_document' in bank_details:
                                    dct['is_bank_3'] = True
                                    if 'base64,' in bank_details['account_statement_document']:
                                        if "pdf" in bank_details['account_statement_document'].split('base64,')[0]:
                                            dct['p3_bank_details_upload_statement_past_month_pdf'] = bank_details['account_statement_document'].split('base64,')[1].replace(" ", "+")
                                        else:
                                            dct['p3_bank_details_upload_statement_past_month'] = bank_details['account_statement_document'].split('base64,')[1].replace(" ", "+")     
                                if "account_statement_document_password_protected" in bank_details:
                                    dct['p3_bank_is_bank_statement_is_password_protected'] = bank_details['account_statement_document_password_protected']
                                if "account_statement_document_password" in bank_details:
                                    dct['p3_bank_password'] = bank_details['account_statement_document_password']
                            banl_test_loop = banl_test_loop + 1

                if "co_applicant" in kw:
                    co_applicant = kw['co_applicant']
                    coapplicant_first = ""
                    coapplicant_last = ""
                    if "applicant_first_name" in co_applicant:
                        coapplicant_first = co_applicant['applicant_first_name']
                    if "applicant_last_name" in co_applicant:
                        coapplicant_last = co_applicant['applicant_last_name']
                    if 'applicant_first_name' in co_applicant:
                        coapplicant_name = coapplicant_first + " " + coapplicant_last
                        dct['p_co_applicant_name'] = coapplicant_name   
                        dct['p_co_applicant_data'] = True    
                    if 'applicant_relation' in co_applicant:
                        dct['p_relationship_with_applicant'] = co_applicant['applicant_relation']
                    if 'applicant_is' in co_applicant:
                        dct['p_co_applicant_is'] = co_applicant['applicant_is']
                    if 'applicant_gender' in co_applicant:
                        dct['p_co_applicant_gender'] = co_applicant['applicant_gender'].lower()
                    if 'applicant_marital_status' in co_applicant:
                        dct['p_co_applicant_marital_status'] = co_applicant['applicant_marital_status']
                    if 'applicant_father_husband_name' in co_applicant:
                        dct['p_co_applicant_father_husband_name'] = co_applicant['applicant_father_husband_name']
                    if 'applicant_educational_qualification' in co_applicant:
                        dct['p_co_applicant_educational_qualification'] = co_applicant['applicant_educational_qualification']
                    if 'applicant_email_id' in co_applicant:
                        dct['p_co_applicant_personal_email_d'] = co_applicant['applicant_email_id']
                    if 'applicant_phone' in co_applicant:
                        dct['p_co_applicant_mobile_number'] = co_applicant['applicant_phone'] 
                    if 'applicant_current_address_document_type' in co_applicant:
                        dct['p_kyc_coapplicant_type_of_document'] = co_applicant['applicant_current_address_document_type']
                        dct['p_kyc_coapplicant_data_is'] = True
                    if 'applicant_current_address_document_front' in co_applicant:
                        if 'base64,' in co_applicant['applicant_current_address_document_front']:
                            if "pdf" in co_applicant['applicant_current_address_document_front'].split('base64,')[0]:
                                dct['p_kyc_coapplicant_current_address_residence_proof_front_pdf'] = co_applicant['applicant_current_address_document_front'].split('base64,')[1].replace(" ", "+")
                            else:
                                dct['p_kyc_coapplicant_current_address_residence_proof_front'] = co_applicant['applicant_current_address_document_front'].split('base64,')[1].replace(" ", "+")
                    if 'applicant_current_address_document_back' in co_applicant:
                        if 'base64,' in co_applicant['applicant_current_address_document_back']:
                            if "pdf" in co_applicant['applicant_current_address_document_back'].split('base64,')[0]:
                                dct['p_kyc_coapplicant_current_address_residence_proof_back_pdf'] = co_applicant['applicant_current_address_document_back'].split('base64,')[1].replace(" ", "+")
                            else:
                                dct['p_kyc_coapplicant_current_address_residence_proof_back'] = co_applicant['applicant_current_address_document_back'].split('base64,')[1].replace(" ", "+")
                    if 'applicant_pan_card_document' in co_applicant:
                        if 'base64,' in co_applicant['applicant_pan_card_document']:
                            if "pdf" in co_applicant['applicant_pan_card_document'].split('base64,')[0]:
                                dct['p_kyc_coapplicant_current_pan_card_photo_pdf'] = co_applicant['applicant_pan_card_document'].split('base64,')[1].replace(" ", "+")
                            else:
                                dct['p_kyc_coapplicant_current_pan_card_photo'] = co_applicant['applicant_pan_card_document'].split('base64,')[1].replace(" ", "+")
                    if 'applicant_pan_number' in co_applicant:
                        dct['p_kyc_coapplicant_current_pan_number'] = co_applicant['applicant_pan_number']
                    if 'applicant_date_of_birth' in co_applicant:
                        dct['p_kyc_coapplicant_data_is'] = True
                        dct['p_kyc_coapplicant_current_date_of_birth'] = co_applicant['applicant_date_of_birth']


                    if isinstance(kw['co_applicant'], list):
                        first_co_loop = 0
                        for coapp in kw['co_applicant']:   
                            if 'address_type' in coapp and coapp["address_type"] == 'CURRENT': 
                                if 'address_residence_type' in coapp:
                                    dct['p_coapplicant_address_residence_owner_rent'] = coapp['address_residence_type']
                                if 'p_coapplicant_address_number_of_year_in_current_residence' in coapp:
                                    dct['p_coapplicant_address_data_is'] = True
                                    dct['p_coapplicant_address_number_of_year_in_current_residence'] = coapp['p_coapplicant_address_number_of_year_in_current_residence']
                                if 'address_house' in coapp:
                                    dct['p_coapplicant_address_flat_house'] = coapp['address_house']
                                if 'address_area' in coapp:
                                    dct['p_coapplicant_address_street_lane'] = coapp['address_area']
                                if 'address_city' in coapp:
                                    dct['p_coapplicant_address_data_is'] = True
                                    dct['p_coapplicant_address_city'] = coapp['address_city']
                                if 'address_state' in coapp:
                                    dct['p_coapplicant_address_data_is'] = True
                                    dct['p_coapplicant_address_state'] = coapp['address_state']
                                if "address_pincode" in coapp:
                                    dct['p_coapplicant_pincode'] = coapp['address_pincode'] 
                            if 'address_type' in coapp and coapp["address_type"] == "PERMANENT":            
                                if 'p_coapplicant_permant_address_proof' in coapp:
                                    dct['p_coapplicant_address_data_is'] = True
                                    dct['p_coapplicant_permant_address_proof'] = coapp['p_coapplicant_permant_address_proof']
                                if 'address_document' in coapp:
                                    if 'base64,' in coapp['address_document']:
                                        if "pdf" in coapp['address_document'].split('base64,')[0]:
                                            dct['p_coapplicant_permant_address_proof_photo_pdf'] = coapp['address_document'].split('base64,')[1].replace(" ", "+")
                                        else:
                                            dct['p_coapplicant_permant_address_proof_photo'] = coapp['address_document'].split('base64,')[1].replace(" ", "+")
                                if 'address_pincode' in coapp:
                                    dct['p_coapplicant_permant_pin_code'] = coapp['address_pincode']
                                if 'address_area' in coapp:
                                    dct['p_coapplicant_permant_street_lane'] = coapp['address_area']
                                if 'address_house' in coapp:
                                    dct['p_coapplicant_permant_flat_house'] = coapp['address_house']
                                if 'address_state' in coapp:
                                    dct['p_coapplicant_permant_state'] = coapp['address_state']
                                if 'address_city' in coapp:
                                    dct['p_coapplicant_permant_city'] = coapp['address_city']
                            first_co_loop = first_co_loop + 1

                    p_business_co_aaplicant_year_in_current_job_year = 0
                    p_business_co_aaplicant_year_in_current_job_month = 0
                    if 'applicant_total_exp_current_role' in co_applicant:
                        p_business_co_aaplicant_year_in_current_job_year = int(co_applicant['applicant_total_exp_current_role'])
                    if 'p_business_co_aaplicant_year_in_current_job_month' in co_applicant:
                        p_business_co_aaplicant_year_in_current_job_month = int(co_applicant['p_business_co_aaplicant_year_in_current_job_month']) / 12       
                    if 'applicant_total_exp_current_role' in co_applicant:
                        dct['p_business_co_aaplicant_year_in_current_job_year_month'] = p_business_co_aaplicant_year_in_current_job_year + p_business_co_aaplicant_year_in_current_job_month
                    
                    p_busness_co_aaplicant_total_work_experieance_year = 0
                    p_busness_co_aaplicant_total_work_experieance_month = 0
                    if 'applicant_total_exp' in co_applicant:
                        p_busness_co_aaplicant_total_work_experieance_year = int(co_applicant['applicant_total_exp'])
                    if 'p_busness_co_aaplicant_total_work_experieance_month' in co_applicant:
                        p_busness_co_aaplicant_total_work_experieance_month = int(co_applicant['p_busness_co_aaplicant_total_work_experieance_month']) / 12

                    if 'applicant_total_exp' in co_applicant:
                        dct['p_business_co_aaplicant_data_is'] = True
                        dct['p_busness_co_aaplicant_total_work_experieance'] = p_busness_co_aaplicant_total_work_experieance_year + p_busness_co_aaplicant_total_work_experieance_month
                    if 'applicant_monthly_net_salary' in co_applicant:
                        dct['p_business_co_aaplicant_data_is'] = True
                        dct['p_busness_co_aaplicant_net_monthly_salary'] = co_applicant['applicant_monthly_net_salary']
                    if 'applicant_monthly_gross_salary' in co_applicant:
                        dct['p_business_co_aaplicant_gross_monthly_salary'] = co_applicant['applicant_monthly_gross_salary']
                    if 'applicant_employment_type' in co_applicant:
                        dct['p_business_co_aaplicant_data_is'] = True
                        dct['p_business_co_aaplicant_employment_type'] = co_applicant['applicant_employment_type']
                    if 'applicant_current_organization_name' in co_applicant:
                        dct['p_business_co_aaplicant_orginization_name'] = co_applicant['applicant_current_organization_name']
                    if 'applicant_designation' in co_applicant:
                        dct['p_business_co_aaplicant_data_is'] = True
                        dct['p_business_co_aaplicant_designation'] = co_applicant['applicant_designation']
                    if 'p_business_co_aaplicant_department' in co_applicant:
                        dct['p_business_co_aaplicant_department'] = co_applicant['p_business_co_aaplicant_department'] 
                    if 'applicant_professional_receipts' in co_applicant:
                        dct['p_business_co_aaplicant_gross_professional_receipt'] = co_applicant['applicant_professional_receipts']
                    if 'applicant_employer_name' in co_applicant:
                        dct['p_busness_co_aaplicant_business_name'] = co_applicant['applicant_employer_name']
                    if 'applicant_role' in co_applicant:
                        dct['p_busness_co_aaplicant_coaaplicant_is_a'] = co_applicant['applicant_role']
                    if 'p_business_co_aaplicant_constitution' in co_applicant:
                        dct['p_business_co_aaplicant_constitution'] = co_applicant['p_business_co_aaplicant_constitution']
                    if 'p_busness_co_aaplicant_amount' in co_applicant:
                        dct['p_busness_co_aaplicant_amount'] = co_applicant['p_busness_co_aaplicant_amount']
                    if 'applicant_share_holding_percentage' in co_applicant:
                        dct['p_busness_co_aaplicant_share_holding'] = co_applicant['applicant_share_holding_percentage']
                    if 'applicant_monthly_renumeration' in co_applicant:
                        dct['p_business_co_aaplicant_monthly_renumeration'] = co_applicant['applicant_monthly_renumeration']
                    if 'applicant_annual_income' in co_applicant:
                        dct['p_busness_co_aaplicant_annual_income'] = co_applicant['applicant_annual_income']
                    
                    if "applicant_business_details" in co_applicant:
                        applicant_business_detail = co_applicant['applicant_business_details']
                        if 'business_current_year_profit_after_tax' in applicant_business_detail:
                            dct['p_busness_co_aaplicant_profit_after_tax_after_current_year'] = applicant_business_detail['business_current_year_profit_after_tax']
                        if 'business_current_year_turnover' in applicant_business_detail:
                            dct['p_business_co_aaplicant_current_year_turnover'] = applicant_business_detail['business_current_year_turnover']
                        if 'applicant_profit_percentage' in applicant_business_detail:
                            dct['p_busness_co_aaplicant_share_in_profit'] = applicant_business_detail['applicant_profit_percentage']
                        if 'business_previous_year_profit_after_tax' in applicant_business_detail:
                            dct['p_busness_co_aaplicant_profit_after_tax_previous_year'] = applicant_business_detail['business_previous_year_profit_after_tax']
                        if 'business_previous_year_turnover' in applicant_business_detail:
                            dct['p_business_co_aaplicant_previous_year_turn_over'] = applicant_business_detail['business_previous_year_turnover']
                        if 'p_business_co_aaplicant_source' in applicant_business_detail:
                            dct['p_business_co_aaplicant_source'] = applicant_business_detail['p_business_co_aaplicant_source']
                        

                    if "p2_business_co_aaplicant_gross_professional_receipt" in co_applicant:
                        dct['p2_business_co_aaplicant_gross_professional_receipt'] = co_applicant['p2_business_co_aaplicant_gross_professional_receipt']
                    if "p2_busness_co_aaplicant_business_name" in co_applicant:
                        dct['p2_busness_co_aaplicant_business_name'] = co_applicant['p2_busness_co_aaplicant_business_name']
                    if "p2_busness_co_aaplicant_coaaplicant_is_a" in co_applicant:
                        dct['p2_busness_co_aaplicant_coaaplicant_is_a'] = co_applicant['p2_busness_co_aaplicant_coaaplicant_is_a']
                    if "p2_business_co_aaplicant_constitution" in co_applicant:
                        dct['p2_business_co_aaplicant_constitution'] = co_applicant['p2_business_co_aaplicant_constitution']
                    if "p2_busness_co_aaplicant_amount" in co_applicant:
                        dct['p2_busness_co_aaplicant_amount'] = co_applicant['p2_busness_co_aaplicant_amount']
                    if "p2_busness_co_aaplicant_share_holding" in co_applicant:
                        dct['p2_busness_co_aaplicant_share_holding'] = co_applicant['p2_busness_co_aaplicant_share_holding']
                    if "p2_business_co_aaplicant_monthly_renumeration" in co_applicant:
                        dct['p2_business_co_aaplicant_monthly_renumeration'] = co_applicant['p2_business_co_aaplicant_monthly_renumeration']
                    if "p2_busness_co_aaplicant_annual_income" in co_applicant:
                        dct['p2_busness_co_aaplicant_annual_income'] = co_applicant['p2_busness_co_aaplicant_annual_income']
                    if "p2_busness_co_aaplicant_profit_after_tax_after_current_year" in co_applicant:
                        dct['p2_busness_co_aaplicant_profit_after_tax_after_current_year'] = co_applicant['p2_busness_co_aaplicant_profit_after_tax_after_current_year']
                    if "p2_business_co_aaplicant_current_year_turnover" in co_applicant:
                        dct['p2_business_co_aaplicant_current_year_turnover'] = co_applicant['p2_business_co_aaplicant_current_year_turnover']
                    if "p2_busness_co_aaplicant_share_in_profit" in co_applicant:
                        dct['p2_busness_co_aaplicant_share_in_profit'] = co_applicant['p2_busness_co_aaplicant_share_in_profit']
                    if "p2_busness_co_aaplicant_profit_after_tax_previous_year" in co_applicant:
                        dct['p2_busness_co_aaplicant_profit_after_tax_previous_year'] = co_applicant['p2_busness_co_aaplicant_profit_after_tax_previous_year']
                    if "p2_business_co_aaplicant_previous_year_turn_over" in co_applicant:
                        dct['p2_business_co_aaplicant_previous_year_turn_over'] = co_applicant['p2_business_co_aaplicant_previous_year_turn_over']
                    if "p2_business_co_aaplicant_source" in co_applicant:
                        dct['p2_business_co_aaplicant_source'] = co_applicant['p2_business_co_aaplicant_source']
                    if "p3_business_co_aaplicant_gross_professional_receipt" in co_applicant:
                        dct['p3_business_co_aaplicant_gross_professional_receipt'] = co_applicant['p3_business_co_aaplicant_gross_professional_receipt']
                    if "p3_busness_co_aaplicant_business_name" in co_applicant:
                        dct['p3_busness_co_aaplicant_business_name'] = co_applicant['p3_busness_co_aaplicant_business_name']
                    if "p3_busness_co_aaplicant_coaaplicant_is_a" in co_applicant:
                        dct['p3_busness_co_aaplicant_coaaplicant_is_a'] = co_applicant['p3_busness_co_aaplicant_coaaplicant_is_a']
                    if "p3_business_co_aaplicant_constitution" in co_applicant:
                        dct['p3_business_co_aaplicant_constitution'] = co_applicant['p3_business_co_aaplicant_constitution']
                    if "p3_busness_co_aaplicant_amount" in co_applicant:
                        dct['p3_busness_co_aaplicant_amount'] = co_applicant['p3_busness_co_aaplicant_amount']
                    if "p3_busness_co_aaplicant_share_holding" in co_applicant:
                        dct['p3_busness_co_aaplicant_share_holding'] = co_applicant['p3_busness_co_aaplicant_share_holding']
                    if "p3_business_co_aaplicant_monthly_renumeration" in co_applicant:
                        dct['p3_business_co_aaplicant_monthly_renumeration'] = co_applicant['p3_business_co_aaplicant_monthly_renumeration']
                    if "p3_busness_co_aaplicant_annual_income" in co_applicant:
                        dct['p3_busness_co_aaplicant_annual_income'] = co_applicant['p3_busness_co_aaplicant_annual_income']
                    if "p3_busness_co_aaplicant_profit_after_tax_after_current_year" in co_applicant:
                        dct['p3_busness_co_aaplicant_profit_after_tax_after_current_year'] = co_applicant['p3_busness_co_aaplicant_profit_after_tax_after_current_year']
                    if "p3_business_co_aaplicant_current_year_turnover" in co_applicant:
                        dct['p3_business_co_aaplicant_current_year_turnover'] = co_applicant['p3_business_co_aaplicant_current_year_turnover']
                    if "p3_busness_co_aaplicant_share_in_profit" in co_applicant:
                        dct['p3_busness_co_aaplicant_share_in_profit'] = co_applicant['p3_busness_co_aaplicant_share_in_profit']
                    if "p3_busness_co_aaplicant_profit_after_tax_previous_year" in co_applicant:
                        dct['p3_busness_co_aaplicant_profit_after_tax_previous_year'] = co_applicant['p3_busness_co_aaplicant_profit_after_tax_previous_year']
                    if "p3_business_co_aaplicant_previous_year_turn_over" in co_applicant:
                        dct['p3_business_co_aaplicant_previous_year_turn_over'] = co_applicant['p3_business_co_aaplicant_previous_year_turn_over']
                    if "p3_business_co_aaplicant_source" in co_applicant:
                        dct['p3_business_co_aaplicant_source'] = co_applicant['p3_business_co_aaplicant_source']           
                    # if isinstance(kw['co_applicant'], list):
                    loan_data = kw['co_applicant']
                    if "loans" in loan_data:
                        for loan in loan_data['loans']:
                            print("loans################",loan)
                            if 'loan_bank_id' in loan:
                                dct['p_coapplicant_obligation_data_is'] = True
                                dct['p_coapplicant_obligation_bank_name'] = loan['loan_bank_id']
                            if 'loan_type' in loan:
                                dct['p_coapplicant_obligation_type_of_loan'] = loan['loan_type']
                            if 'loan_account_number' in loan:
                                dct['p_coapplicant_obligation_data_is'] = True
                                dct['p_coapplicant_obligation_account_number'] = loan['loan_account_number']
                            if 'loan_emi' in loan:
                                dct['p_coapplicant_obligation_emi'] = loan['loan_emi']
                            if 'loan_opening_date' in loan:
                                dct['p_coapplicant_obligation_data_is'] = True
                                dct['p_coapplicant_obligation_loan_opening_date'] = loan['loan_opening_date']
                            if 'loan_tenure_months' in loan:
                                dct['p_coapplicant_obligation_tenure'] = loan['loan_tenure_months']
                            if 'loan_rate_of_interest' in loan:
                                dct['p_coapplicant_obligation_data_is'] = True
                                dct['p_coapplicant_obligation_roi'] = loan['loan_rate_of_interest']
                            if 'loan_type_of_security' in loan:
                                dct['p_coapplicant_obligation_type_of_security'] = loan['loan_type_of_security']
                            if 'loan_current_outstanding_amount' in loan:
                                dct['p_coapplicant_obligation_data_is'] = True
                                dct['p_coapplicant_obligation_current_out_standing_amount'] = loan['loan_current_outstanding_amount']
                            if "loan_amount" in loan:
                                dct['p_coapplicant_obligation_loan_amount'] = loan['loan_amount'] 

                            if "pl2_coapplicant_obligation_data_is" in loan:
                                dct['pl2_coapplicant_obligation_data_is'] = loan['pl2_coapplicant_obligation_data_is']
                            if "pl2_coapplicant_obligation_bank_name" in loan:
                                dct['pl2_coapplicant_obligation_bank_name'] = loan['pl2_coapplicant_obligation_bank_name']
                            if "pl2_coapplicant_obligation_type_of_loan" in loan:
                                dct['pl2_coapplicant_obligation_type_of_loan'] = loan['pl2_coapplicant_obligation_type_of_loan']
                            if "pl2_coapplicant_obligation_account_number" in loan:
                                dct['pl2_coapplicant_obligation_account_number'] = loan['pl2_coapplicant_obligation_account_number']
                            if "pl2_coapplicant_obligation_loan_amount" in loan:
                                dct['pl2_coapplicant_obligation_loan_amount'] = loan['pl2_coapplicant_obligation_loan_amount']    
                            if "pl2_coapplicant_obligation_emi" in loan:
                                dct['pl2_coapplicant_obligation_emi'] = loan['pl2_coapplicant_obligation_emi']
                            if "pl2_coapplicant_obligation_loan_opening_date" in loan:
                                dct['pl2_coapplicant_obligation_loan_opening_date'] = loan['pl2_coapplicant_obligation_loan_opening_date']
                            if "pl2_coapplicant_obligation_tenure" in loan:
                                dct['pl2_coapplicant_obligation_tenure'] = loan['pl2_coapplicant_obligation_tenure']
                            if "pl2_coapplicant_obligation_roi" in loan:
                                dct['pl2_coapplicant_obligation_roi'] = loan['pl2_coapplicant_obligation_roi']
                            if "pl2_coapplicant_obligation_type_of_security" in loan:
                                dct['pl2_coapplicant_obligation_type_of_security'] = loan['pl2_coapplicant_obligation_type_of_security']
                            if "pl2_coapplicant_obligation_current_out_standing_amount" in loan:
                                dct['pl2_coapplicant_obligation_current_out_standing_amount'] = loan['pl2_coapplicant_obligation_current_out_standing_amount']
                            if "pl3_coapplicant_obligation_data_is" in loan:
                                dct['pl3_coapplicant_obligation_data_is'] = loan['pl3_coapplicant_obligation_data_is']
                            if "pl3_coapplicant_obligation_bank_name" in loan:
                                dct['pl3_coapplicant_obligation_bank_name'] = loan['pl3_coapplicant_obligation_bank_name']
                            if "pl3_coapplicant_obligation_type_of_loan" in loan:
                                dct['pl3_coapplicant_obligation_type_of_loan'] = loan['pl3_coapplicant_obligation_type_of_loan']
                            if "pl3_coapplicant_obligation_account_number" in loan:
                                dct['pl3_coapplicant_obligation_account_number'] = loan['pl3_coapplicant_obligation_account_number']
                            if "pl3_coapplicant_obligation_loan_amount" in loan:
                                dct['pl3_coapplicant_obligation_loan_amount'] = loan['pl3_coapplicant_obligation_loan_amount']       
                            if "pl3_coapplicant_obligation_emi" in loan:
                                dct['pl3_coapplicant_obligation_emi'] = loan['pl3_coapplicant_obligation_emi']
                            if "pl3_coapplicant_obligation_loan_opening_date" in loan:
                                dct['pl3_coapplicant_obligation_loan_opening_date'] = loan['pl3_coapplicant_obligation_loan_opening_date']
                            if "pl3_coapplicant_obligation_tenure" in loan:
                                dct['pl3_coapplicant_obligation_tenure'] = loan['pl3_coapplicant_obligation_tenure']
                            if "pl3_coapplicant_obligation_roi" in loan:
                                dct['pl3_coapplicant_obligation_roi'] = loan['pl3_coapplicant_obligation_roi']
                            if "pl3_coapplicant_obligation_type_of_security" in loan:
                                dct['pl3_coapplicant_obligation_type_of_security'] = loan['pl3_coapplicant_obligation_type_of_security']
                            if "pl3_coapplicant_obligation_current_out_standing_amount" in loan:
                                dct['pl3_coapplicant_obligation_current_out_standing_amount'] = loan['pl3_coapplicant_obligation_current_out_standing_amount']
                        # if "loans" in loan_data:
                        #     for loan in loan_data['loans']:
                        #         if 'loan_bank_id' in loan:
                        #             dct['p_coapplicant_obligation_data_is'] = True
                        #             dct['p_coapplicant_obligation_bank_name'] = loan['loan_bank_id']
                        #         if 'loan_type' in loan:
                        #             dct['p_coapplicant_obligation_type_of_loan'] = loan['loan_type']
                        #         if 'loan_account_number' in loan:
                        #             dct['p_coapplicant_obligation_data_is'] = True
                        #             dct['p_coapplicant_obligation_account_number'] = loan['loan_account_number']
                        #         if 'loan_emi' in loan:
                        #             dct['p_coapplicant_obligation_emi'] = loan['loan_emi']
                        #         if 'loan_opening_date' in loan:
                        #             dct['p_coapplicant_obligation_data_is'] = True
                        #             dct['p_coapplicant_obligation_loan_opening_date'] = loan['loan_opening_date']
                        #         if 'loan_tenure_months' in loan:
                        #             dct['p_coapplicant_obligation_tenure'] = loan['loan_tenure_months']
                        #         if 'loan_rate_of_interest' in loan:
                        #             dct['p_coapplicant_obligation_data_is'] = True
                        #             dct['p_coapplicant_obligation_roi'] = loan['loan_rate_of_interest']
                        #         if 'loan_type_of_security' in loan:
                        #             dct['p_coapplicant_obligation_type_of_security'] = loan['loan_type_of_security']
                        #         if 'loan_current_outstanding_amount' in loan:
                        #             dct['p_coapplicant_obligation_data_is'] = True
                        #             dct['p_coapplicant_obligation_current_out_standing_amount'] = loan['loan_current_outstanding_amount']
                        #         if "loan_amount" in loan:
                        #             dct['p_coapplicant_obligation_loan_amount'] = loan['loan_amount'] 

                        #         if "pl2_coapplicant_obligation_data_is" in loan:
                        #             dct['pl2_coapplicant_obligation_data_is'] = loan['pl2_coapplicant_obligation_data_is']
                        #         if "pl2_coapplicant_obligation_bank_name" in loan:
                        #             dct['pl2_coapplicant_obligation_bank_name'] = loan['pl2_coapplicant_obligation_bank_name']
                        #         if "pl2_coapplicant_obligation_type_of_loan" in loan:
                        #             dct['pl2_coapplicant_obligation_type_of_loan'] = loan['pl2_coapplicant_obligation_type_of_loan']
                        #         if "pl2_coapplicant_obligation_account_number" in loan:
                        #             dct['pl2_coapplicant_obligation_account_number'] = loan['pl2_coapplicant_obligation_account_number']
                        #         if "pl2_coapplicant_obligation_loan_amount" in loan:
                        #             dct['pl2_coapplicant_obligation_loan_amount'] = loan['pl2_coapplicant_obligation_loan_amount']    
                        #         if "pl2_coapplicant_obligation_emi" in loan:
                        #             dct['pl2_coapplicant_obligation_emi'] = loan['pl2_coapplicant_obligation_emi']
                        #         if "pl2_coapplicant_obligation_loan_opening_date" in loan:
                        #             dct['pl2_coapplicant_obligation_loan_opening_date'] = loan['pl2_coapplicant_obligation_loan_opening_date']
                        #         if "pl2_coapplicant_obligation_tenure" in loan:
                        #             dct['pl2_coapplicant_obligation_tenure'] = loan['pl2_coapplicant_obligation_tenure']
                        #         if "pl2_coapplicant_obligation_roi" in loan:
                        #             dct['pl2_coapplicant_obligation_roi'] = loan['pl2_coapplicant_obligation_roi']
                        #         if "pl2_coapplicant_obligation_type_of_security" in loan:
                        #             dct['pl2_coapplicant_obligation_type_of_security'] = loan['pl2_coapplicant_obligation_type_of_security']
                        #         if "pl2_coapplicant_obligation_current_out_standing_amount" in loan:
                        #             dct['pl2_coapplicant_obligation_current_out_standing_amount'] = loan['pl2_coapplicant_obligation_current_out_standing_amount']
                        #         if "pl3_coapplicant_obligation_data_is" in loan:
                        #             dct['pl3_coapplicant_obligation_data_is'] = loan['pl3_coapplicant_obligation_data_is']
                        #         if "pl3_coapplicant_obligation_bank_name" in loan:
                        #             dct['pl3_coapplicant_obligation_bank_name'] = loan['pl3_coapplicant_obligation_bank_name']
                        #         if "pl3_coapplicant_obligation_type_of_loan" in loan:
                        #             dct['pl3_coapplicant_obligation_type_of_loan'] = loan['pl3_coapplicant_obligation_type_of_loan']
                        #         if "pl3_coapplicant_obligation_account_number" in loan:
                        #             dct['pl3_coapplicant_obligation_account_number'] = loan['pl3_coapplicant_obligation_account_number']
                        #         if "pl3_coapplicant_obligation_loan_amount" in loan:
                        #             dct['pl3_coapplicant_obligation_loan_amount'] = loan['pl3_coapplicant_obligation_loan_amount']       
                        #         if "pl3_coapplicant_obligation_emi" in loan:
                        #             dct['pl3_coapplicant_obligation_emi'] = loan['pl3_coapplicant_obligation_emi']
                        #         if "pl3_coapplicant_obligation_loan_opening_date" in loan:
                        #             dct['pl3_coapplicant_obligation_loan_opening_date'] = loan['pl3_coapplicant_obligation_loan_opening_date']
                        #         if "pl3_coapplicant_obligation_tenure" in loan:
                        #             dct['pl3_coapplicant_obligation_tenure'] = loan['pl3_coapplicant_obligation_tenure']
                        #         if "pl3_coapplicant_obligation_roi" in loan:
                        #             dct['pl3_coapplicant_obligation_roi'] = loan['pl3_coapplicant_obligation_roi']
                        #         if "pl3_coapplicant_obligation_type_of_security" in loan:
                        #             dct['pl3_coapplicant_obligation_type_of_security'] = loan['pl3_coapplicant_obligation_type_of_security']
                        #         if "pl3_coapplicant_obligation_current_out_standing_amount" in loan:
                        #             dct['pl3_coapplicant_obligation_current_out_standing_amount'] = loan['pl3_coapplicant_obligation_current_out_standing_amount']
                    if "credit_cards" in co_applicant:
                        for credit_card in co_applicant["credit_cards"]: 
                            if "cc_current_outstanding_amount" in credit_card:
                                dct['p3_coapplicant_obligation_credit_card'] = True
                                dct['p3_coapplicant_obligation_current_credit_out_standing_amount'] = credit_card['cc_current_outstanding_amount']
                            if "cc_bank_id" in credit_card:
                                dct['p3_coapplicant_obligation_credit_card'] = True
                                dct['p3_coapplicant_obligation_credit_bank_name'] = credit_card['cc_bank_id']
                            if "cc_credit_limit" in credit_card:
                                dct['p3_coapplicant_obligation_credit_card'] = True
                                dct['p3_coapplicant_obligation_credit_limit'] = credit_card['cc_credit_limit']
                    if isinstance(kw['co_applicant'], list):
                        coapp_bank = 0
                        for bank_detail in co_applicant:
                            if coapp_bank == 0:  
                                if 'account_bank_id' in bank_detail:
                                    dct['p_coapplicant_bank_data_is'] = True
                                    dct['p_coapplicant_bank_select_bank'] = bank_detail['account_bank_id']
                                if 'account_type' in bank_detail:
                                    dct['p_coapplicant_bank_data_is'] = True
                                    dct['p_coapplicant_bank_details_account_type'] = bank_detail['account_type']
                                if 'account_statement_document' in bank_detail:
                                    if 'base64,' in bank_detail['account_statement_document']:
                                        if "pdf" in bank_detail['account_statement_document'].split('base64,')[0]:
                                            dct['p_coapplicant_bank_details_upload_statement_past_month_pdf'] = bank_detail['account_statement_document'].split('base64,')[1].replace(" ", "+")
                                        else:
                                            dct['p_coapplicant_bank_details_upload_statement_past_month'] = bank_detail['account_statement_document'].split('base64,')[1].replace(" ", "+")     
                                if 'account_statement_document_password_protected' in bank_detail:
                                    dct['p_coapplicant_bank_is_bank_statement_is_password_protected'] = bank_detail['account_statement_document_password_protected']
                                if 'account_statement_document_password' in bank_detail:
                                    dct['p_coapplicant_bank_password'] = bank_detail['account_statement_document_password']
                                
                            if coapp_bank == 1:
                                if "account_bank_id" in bank_detail:
                                    dct['pbl2_coapplicant_bank_data_is'] = True
                                    dct['pbl2_coapplicant_bank_select_bank'] = bank_detail['account_bank_id']
                                if "account_type" in bank_detail:
                                    dct['pbl2_coapplicant_bank_data_is'] = True
                                    dct['pbl2_coapplicant_bank_details_account_type'] = bank_detail['account_type']
                                if 'account_statement_document' in bank_detail:
                                    if 'base64,' in bank_detail['account_statement_document']:
                                        if "pdf" in bank_detail['account_statement_document'].split('base64,')[0]:
                                            dct['pbl2_coapplicant_bank_details_upload_statement_past_month_pdf'] = bank_detail['account_statement_document'].split('base64,')[1].replace(" ", "+")
                                        else:
                                            dct['pbl2_coapplicant_bank_details_upload_statement_past_month'] = bank_detail['account_statement_document'].split('base64,')[1].replace(" ", "+")     
                                if "account_statement_document_password_protected" in bank_detail:
                                    dct['pbl2_coapplicant_bank_is_bank_statement_is_password_protected'] = bank_detail['account_statement_document_password_protected']
                                if "account_statement_document_password" in bank_detail:
                                    dct['pbl2_coapplicant_bank_password'] = bank_detail['account_statement_document_password']
                                
                            if coapp_bank == 2:
                                if "account_bank_id" in bank_detail:
                                    dct['pbl3_coapplicant_bank_select_bank'] = bank_detail['account_bank_id']
                                if "account_type" in bank_detail:
                                    dct['pbl3_coapplicant_bank_data_is'] = True
                                    dct['pbl3_coapplicant_bank_details_account_type'] = bank_detail['account_type']
                                if 'account_statement_document' in bank_detail:
                                    if 'base64,' in bank_detail['account_statement_document']:
                                        if "pdf" in bank_detail['account_statement_document'].split('base64,')[0]:
                                            dct['pbl3_coapplicant_bank_details_upload_statement_past_month_pdf'] = bank_detail['account_statement_document'].split('base64,')[1].replace(" ", "+")
                                        else:
                                            dct['pbl3_coapplicant_bank_details_upload_statement_past_month'] = bank_detail['account_statement_document'].split('base64,')[1].replace(" ", "+")         
                                if "account_statement_document_password_protected" in bank_detail:
                                    dct['pbl3_coapplicant_bank_data_is'] = True
                                    dct['pbl3_coapplicant_bank_is_bank_statement_is_password_protected'] = bank_detail['account_statement_document_password_protected']
                                if "account_statement_document_password" in bank_detail:
                                    dct['pbl3_coapplicant_bank_data_is'] = True
                                    dct['pbl3_coapplicant_bank_password'] = bank_detail['account_statement_document_password']  
                            coapp_bank = coapp_bank + 1
            
            if 'p_father_husband_name' in kw:
                dct['p_father_husband_name'] = kw['p_father_husband_name']
            if 'p_educational_qualification' in kw:
                dct['p_educational_qualification'] = kw['p_educational_qualification']
            if 'p_marital_status' in kw:
                dct['p_marital_status'] = kw['p_marital_status']
            if 'p_personal_email_id' in kw:
                dct['p_personal_email_id'] = kw['p_personal_email_id']
            if 'p_mobile_number' in kw:
                dct['p_mobile_number'] = kw['p_mobile_number']
            if 'p_relationship_with_applicant' in kw:
                dct['p_relationship_with_applicant'] = kw['p_relationship_with_applicant']
            if 'p_co_applicant_is' in kw:
                dct['p_co_applicant_is'] = kw['p_co_applicant_is']
            if 'p_co_applicant_gender' in kw:
                dct['p_co_applicant_gender'] = kw['p_co_applicant_gender'].lower()
            if 'p_co_applicant_marital_status' in kw:
                dct['p_co_applicant_marital_status'] = kw['p_co_applicant_marital_status']
            if 'p_co_applicant_father_husband_name' in kw:
                dct['p_co_applicant_father_husband_name'] = kw['p_co_applicant_father_husband_name']
            if 'p_co_applicant_educational_qualification' in kw:
                dct['p_co_applicant_educational_qualification'] = kw['p_co_applicant_educational_qualification']
            if 'p_co_applicant_personal_email_d' in kw:
                dct['p_co_applicant_personal_email_d'] = kw['p_co_applicant_personal_email_d']
            if 'p_co_applicant_mobile_number' in kw:
                dct['p_co_applicant_mobile_number'] = kw['p_co_applicant_mobile_number']
            if 'p_kyc_type_of_document' in kw:
                dct['p_kyc_type_of_document'] = kw['p_kyc_type_of_document']
            if 'p_kyc_current_address_residence_proof_front' in kw:
                dct['p_kyc_current_address_residence_proof_front'] = kw['p_kyc_current_address_residence_proof_front']
            if 'p_kyc_current_address_residence_proof_back' in kw:
                dct['p_kyc_current_address_residence_proof_back'] = kw['p_kyc_current_address_residence_proof_back']
            if 'p_kyc_current_pan_card_photo' in kw:
                dct['p_kyc_current_pan_card_photo'] = kw['p_kyc_current_pan_card_photo']
            if 'p_kyc_current_pan_number' in kw:
                dct['p_kyc_current_pan_number'] = kw['p_kyc_current_pan_number']
            if 'p_kyc_current_date_of_birth' in kw:
                dct['p_kyc_current_date_of_birth'] = kw['p_kyc_current_date_of_birth']
            if 'p_kyc_coapplicant_type_of_document' in kw:
                dct['p_kyc_coapplicant_type_of_document'] = kw['p_kyc_coapplicant_type_of_document']
            if 'p_kyc_coapplicant_current_address_residence_proof_front' in kw:
                dct['p_kyc_coapplicant_current_address_residence_proof_front'] = kw['p_kyc_coapplicant_current_address_residence_proof_front']
            if 'p_kyc_coapplicant_current_address_residence_proof_back' in kw:
                dct['p_kyc_coapplicant_current_address_residence_proof_back'] = kw['p_kyc_coapplicant_current_address_residence_proof_back']
            if 'p_kyc_coapplicant_current_pan_card_photo' in kw:
                dct['p_kyc_coapplicant_current_pan_card_photo'] = kw['p_kyc_coapplicant_current_pan_card_photo']
            if 'p_kyc_coapplicant_current_pan_number' in kw:
                dct['p_kyc_coapplicant_current_pan_number'] = kw['p_kyc_coapplicant_current_pan_number']
            if 'p_kyc_coapplicant_current_date_of_birth' in kw:
                dct['p_kyc_coapplicant_current_date_of_birth'] = kw['p_kyc_coapplicant_current_date_of_birth']
            if 'p_address_residence_owner_rent' in kw:
                dct['p_address_residence_owner_rent'] = kw['p_address_residence_owner_rent']
            if 'p_address_number_of_year_in_current_residence' in kw:
                dct['p_address_number_of_year_in_current_residence'] = kw['p_address_number_of_year_in_current_residence']
            if 'p_address_flat_house' in kw:
                dct['p_address_flat_house'] = kw['p_address_flat_house']
            if 'p_address_street_lane' in kw:
                dct['p_address_street_lane'] = kw['p_address_street_lane']
            if 'p_address_city' in kw:
                dct['p_address_city'] = kw['p_address_city']
            if 'p_address_state' in kw:
                dct['p_address_state'] = kw['p_address_state']
            if 'p_permant_address_proof' in kw:
                dct['p_permant_address_proof'] = kw['p_permant_address_proof']
            if 'p_permant_address_proof_photo' in kw:
                dct['p_permant_address_proof_photo'] = kw['p_permant_address_proof_photo']
            if 'p_permant_pin_code' in kw:
                dct['p_permant_pin_code'] = kw['p_permant_pin_code']
            if 'p_permant_street_lane' in kw:
                dct['p_permant_street_lane'] = kw['p_permant_street_lane']
            if 'p_permant_flat_house' in kw:
                dct['p_permant_flat_house'] = kw['p_permant_flat_house']
            if 'p_permant_state' in kw:
                dct['p_permant_state'] = kw['p_permant_state']
            if 'p_permant_city' in kw:
                dct['p_permant_city'] = kw['p_permant_city']
            if 'p_coapplicant_address_residence_owner_rent' in kw:
                dct['p_coapplicant_address_residence_owner_rent'] = kw['p_coapplicant_address_residence_owner_rent']
            if 'p_coapplicant_address_number_of_year_in_current_residence' in kw:
                dct['p_coapplicant_address_number_of_year_in_current_residence'] = kw['p_coapplicant_address_number_of_year_in_current_residence']
            if 'p_coapplicant_address_flat_house' in kw:
                dct['p_coapplicant_address_flat_house'] = kw['p_coapplicant_address_flat_house']
            if 'p_coapplicant_address_banking_upload_passbookstreet_lane' in kw:
                dct['p_coapplicant_address_street_lane'] = kw['p_coapplicant_address_street_lane']
            if 'p_coapplicant_address_city' in kw:
                dct['p_coapplicant_address_city'] = kw['p_coapplicant_address_city']
            if 'p_coapplicant_address_state' in kw:
                dct['p_coapplicant_address_state'] = kw['p_coapplicant_address_state']
            if 'p_coapplicant_permant_address_proof' in kw:
                dct['p_coapplicant_permant_address_proof'] = kw['p_coapplicant_permant_address_proof']
            if 'p_coapplicant_permant_address_proof_photo' in kw:
                dct['p_coapplicant_permant_address_proof_photo'] = kw['p_coapplicant_permant_address_proof_photo']
            if 'p_coapplicant_permant_pin_code' in kw:
                dct['p_coapplicant_permant_pin_code'] = kw['p_coapplicant_permant_pin_code']
            if 'p_coapplicant_permant_street_lane' in kw:
                dct['p_coapplicant_permant_street_lane'] = kw['p_coapplicant_permant_street_lane']
            if 'p_coapplicant_permant_flat_house' in kw:
                dct['p_coapplicant_permant_flat_house'] = kw['p_coapplicant_permant_flat_house']
            if 'p_coapplicant_permant_state' in kw:
                dct['p_coapplicant_permant_state'] = kw['p_coapplicant_permant_state']
            if 'p_coapplicant_permant_city' in kw:
                dct['p_coapplicant_permant_city'] = kw['p_coapplicant_permant_city']
            if 'p_business_name_of_current_orginization' in kw:
                dct['p_business_name_of_current_orginization'] = kw['p_business_name_of_current_orginization']
            if 'p_busness_orginization_type' in kw:
                dct['p_busness_orginization_type'] = kw['p_busness_orginization_type']
            if 'p_busness_industry_type' in kw:
                dct['p_busness_industry_type'] = kw['p_busness_industry_type']
            if 'applicant_employment_type' in kw:
                dct['p_business_employment_type'] = kw['applicant_employment_type']
            if 'p_business_employeement_id_number' in kw:
                dct['p_business_employeement_id_number'] = kw['p_business_employeement_id_number']
            if 'p_business_officail_email_id' in kw:
                dct['p_business_officail_email_id'] = kw['p_business_officail_email_id']
            if 'applicant_monthly_net_salary' in kw:
                dct['p_business_net_monthly_salary'] = kw['applicant_monthly_net_salary']
            if 'applicant_monthly_gross_salary' in kw:
                dct['p_business_gross_monthly_salary'] = kw['applicant_monthly_gross_salary']
            if 'p_business_designation' in kw:
                dct['p_business_designation'] = kw['p_business_designation']
            if 'p_business_department' in kw:
                dct['p_business_department'] = kw['p_business_department']
            p_business_year_in_current_job_year = 0
            p_business_year_in_current_job_month = 0
            if 'applicant_total_exp_current_role' in kw:
                p_business_year_in_current_job_year = float(kw['applicant_total_exp_current_role'])
            if 'p_business_year_in_current_job_month' in kw:
                p_business_year_in_current_job_month = float(kw['p_business_year_in_current_job_month']) / 12

            if 'applicant_total_exp_current_role' in kw:
                dct['p_business_year_in_current_job'] = p_business_year_in_current_job_year  + p_business_year_in_current_job_month
            
            p_business_total_work_experiance_year = 0
            p_business_total_work_experiance_month = 0

            if 'applicant_total_exp' in kw:
                p_business_total_work_experiance_year = int(kw['applicant_total_exp'])
            if 'p_business_total_work_experiance_month' in kw:
                p_business_total_work_experiance_month = int(kw['p_business_total_work_experiance_month']) / 12

            if 'applicant_total_exp' in kw:
                dct['p_business_total_work_experiance'] = p_business_total_work_experiance_year + p_business_total_work_experiance_month
            if 'p_business_additional_amount' in kw:
                dct['p_business_additional_amount'] = kw['p_business_additional_amount']
            if 'p_business_additional_source' in kw:
                dct['p_business_additional_source'] = kw['p_business_additional_source']

            if 'p2_business_additional_amount' in kw:
                dct['p2_business_additional_amount'] = kw['p2_business_additional_amount']
            if 'p2_business_additional_source' in kw:
                dct['p2_business_additional_source'] = kw['p2_business_additional_source']    
            if 'p_business_office_pin_code' in kw:
                dct['p_business_office_pin_code'] = kw['p_business_office_pin_code']
            if 'p_business_office_building_numbr' in kw:
                dct['p_business_office_building_numbr'] = kw['p_business_office_building_numbr']
            if 'p_business_office_street_lane' in kw:
                dct['p_business_office_street_lane'] = kw['p_business_office_street_lane']
            if 'p_business_office_landmark' in kw:
                dct['p_business_office_landmark'] = kw['p_business_office_landmark']
            if 'p_business_office_city' in kw:
                dct['p_business_office_city'] = kw['p_business_office_city']
            if 'p_business_building_office_state' in kw:
                dct['p_business_building_office_state'] = kw['p_business_building_office_state']
            p_business_co_aaplicant_year_in_current_job_year = 0
            p_business_co_aaplicant_year_in_current_job_month = 0
            if 'p_business_co_aaplicant_year_in_current_job_year' in kw:
                p_business_co_aaplicant_year_in_current_job_year = int(kw['p_business_co_aaplicant_year_in_current_job_year'])
            if 'p_business_co_aaplicant_year_in_current_job_month' in kw:
                p_business_co_aaplicant_year_in_current_job_month = int(kw['p_business_co_aaplicant_year_in_current_job_month']) / 12       
            if 'p_business_co_aaplicant_year_in_current_job_year' in kw:
                dct['p_business_co_aaplicant_year_in_current_job_year_month'] = p_business_co_aaplicant_year_in_current_job_year + p_business_co_aaplicant_year_in_current_job_month
            
            p_busness_co_aaplicant_total_work_experieance_year = 0
            p_busness_co_aaplicant_total_work_experieance_month = 0
            if 'p_busness_co_aaplicant_total_work_experieance_year' in kw:
                p_busness_co_aaplicant_total_work_experieance_year = int(kw['p_busness_co_aaplicant_total_work_experieance_year'])
            if 'p_busness_co_aaplicant_total_work_experieance_month' in kw:
                p_busness_co_aaplicant_total_work_experieance_month = int(kw['p_busness_co_aaplicant_total_work_experieance_month']) / 12

            if 'p_busness_co_aaplicant_total_work_experieance_year' in kw:
                dct['p_busness_co_aaplicant_total_work_experieance'] = p_busness_co_aaplicant_total_work_experieance_year + p_busness_co_aaplicant_total_work_experieance_month
            if 'p_busness_co_aaplicant_net_monthly_salary' in kw:
                dct['p_busness_co_aaplicant_net_monthly_salary'] = kw['p_busness_co_aaplicant_net_monthly_salary']
            if 'p_business_co_aaplicant_gross_monthly_salary' in kw:
                dct['p_business_co_aaplicant_gross_monthly_salary'] = kw['p_business_co_aaplicant_gross_monthly_salary']
            if 'p_business_co_aaplicant_employment_type' in kw:
                dct['p_business_co_aaplicant_employment_type'] = kw['p_business_co_aaplicant_employment_type']
            if 'p_business_co_aaplicant_orginization_name' in kw:
                dct['p_business_co_aaplicant_orginization_name'] = kw['p_business_co_aaplicant_orginization_name']
            if 'p_business_co_aaplicant_designation' in kw:
                dct['p_business_co_aaplicant_designation'] = kw['p_business_co_aaplicant_designation']
            if 'p_business_co_aaplicant_department' in kw:
                dct['p_business_co_aaplicant_department'] = kw['p_business_co_aaplicant_department']

            if "p_obligation_loan" in kw:
                dct['p_obligation_loan'] = kw['p_obligation_loan']    
    

            if 'p_obligation_loan_amount' in kw:
                dct['p_obligation_loan_amount'] = kw['p_obligation_loan_amount'] 

            if 'p_obligation_bank_name' in kw:
                dct['p_obligation_bank_name'] = kw['p_obligation_bank_name']
            if 'p_obligation_type_of_loan' in kw:
                dct['p_obligation_type_of_loan'] = kw['p_obligation_type_of_loan']
            if 'p_obligation_account_number' in kw:
                dct['p_obligation_account_number'] = kw['p_obligation_account_number']
            if 'p_obligation_emi' in kw:
                dct['p_obligation_emi'] = kw['p_obligation_emi']
            if 'p_obligation_loan_opening_date' in kw:
                dct['p_obligation_loan_opening_date'] = kw['p_obligation_loan_opening_date']
            if 'p_obligation_tenure' in kw:
                dct['p_obligation_tenure'] = kw['p_obligation_tenure']
            if 'p_obligation_roi' in kw:
                dct['p_obligation_roi'] = kw['p_obligation_roi']
            if 'p_obligation_type_of_security' in kw:
                dct['p_obligation_type_of_security'] = kw['p_obligation_type_of_security']
            if 'p_obligation_current_out_standing_amount' in kw:
                dct['p_obligation_current_out_standing_amount'] = kw['p_obligation_current_out_standing_amount']
            if 'p_obligation_credit_card' in kw:
                dct['p_obligation_credit_card'] = kw['p_obligation_credit_card']
            if 'p_obligation_current_out_standing_amount' in kw:
                dct['p_obligation_current_out_standing_amount'] = kw['p_obligation_current_out_standing_amount']
            if 'p_obligation_bank_name' in kw:
                dct['p_obligation_bank_name'] = kw['p_obligation_bank_name']
            if 'p_obligation_credit_limit' in kw:
                dct['p_obligation_credit_limit'] = kw['p_obligation_credit_limit']
            if 'p_coapplicant_obligation_bank_name' in kw:
                dct['p_coapplicant_obligation_bank_name'] = kw['p_coapplicant_obligation_bank_name']
            if 'p_coapplicant_obligation_type_of_loan' in kw:
                dct['p_coapplicant_obligation_type_of_loan'] = kw['p_coapplicant_obligation_type_of_loan']
            if 'p_coapplicant_obligation_account_number' in kw:
                dct['p_coapplicant_obligation_account_number'] = kw['p_coapplicant_obligation_account_number']
            if 'p_coapplicant_obligation_emi' in kw:
                dct['p_coapplicant_obligation_emi'] = kw['p_coapplicant_obligation_emi']
            if 'p_coapplicant_obligation_loan_opening_date' in kw:
                dct['p_coapplicant_obligation_loan_opening_date'] = kw['p_coapplicant_obligation_loan_opening_date']
            if 'p_coapplicant_obligation_tenure' in kw:
                dct['p_coapplicant_obligation_tenure'] = kw['p_coapplicant_obligation_tenure']
            if 'p_coapplicant_obligation_roi' in kw:
                dct['p_coapplicant_obligation_roi'] = kw['p_coapplicant_obligation_roi']
            if 'p_coapplicant_obligation_type_of_security' in kw:
                dct['p_coapplicant_obligation_type_of_security'] = kw['p_coapplicant_obligation_type_of_security']
            if 'p_coapplicant_obligation_current_out_standing_amount' in kw:
                dct['p_coapplicant_obligation_current_out_standing_amount'] = kw['p_coapplicant_obligation_current_out_standing_amount']
            if 'p_coapplicant_obligation_credit_card' in kw:
                dct['p_coapplicant_obligation_credit_card'] = kw['p_coapplicant_obligation_credit_card']
            if 'p_coapplicant_obligation_current_out_standing_amount' in kw:
                dct['p_coapplicant_obligation_current_out_standing_amount'] = kw['p_coapplicant_obligation_current_out_standing_amount']
            if 'p_coapplicant_obligation_bank_name' in kw:
                dct['p_coapplicant_obligation_bank_name'] = kw['p_coapplicant_obligation_bank_name']
            if 'p_coapplicant_obligation_credit_limit' in kw:
                dct['p_coapplicant_obligation_credit_limit'] = kw['p_coapplicant_obligation_credit_limit']


            if 'p_bank_select_bank' in kw:
                dct['p_bank_select_bank'] = kw['p_bank_select_bank']
            if 'p_bank_details_account_type' in kw:
                dct['p_bank_details_account_type'] = kw['p_bank_details_account_type']
            if 'p_bank_details_upload_statement_past_month' in kw:
                dct['p_bank_details_upload_statement_past_month'] = kw['p_bank_details_upload_statement_past_month']
            if 'p_bank_is_bank_statement_is_password_protected' in kw:
                dct['p_bank_is_bank_statement_is_password_protected'] = kw['p_bank_is_bank_statement_is_password_protected']
            if 'p_bank_password' in kw:
                dct['p_bank_password'] = kw['p_bank_password']

            if "is_bank_1" in kw:
                dct['is_bank_1'] = kw['is_bank_1']
            if "is_bank_3" in kw:
                dct['is_bank_3'] = kw['is_bank_3']    
            if "p2_bank_select_bank" in kw:
                dct['p2_bank_select_bank'] = kw['p2_bank_select_bank']
            if "p2_bank_details_account_type" in kw:
                dct['p2_bank_details_account_type'] = kw['p2_bank_details_account_type']
            if "p2_bank_details_upload_statement_past_month" in kw:
                dct['p2_bank_details_upload_statement_past_month'] = kw['p2_bank_details_upload_statement_past_month']
            if "p2_bank_is_bank_statement_is_password_protected" in kw:
                dct['p2_bank_is_bank_statement_is_password_protected'] = kw['p2_bank_is_bank_statement_is_password_protected']
            if "p2_bank_password" in kw:
                dct['p2_bank_password'] = kw['p2_bank_password']
            if "is_bank_2" in kw:
                dct['is_bank_2'] = kw['is_bank_2']
            if "p3_bank_select_bank" in kw:
                dct['p3_bank_select_bank'] = kw['p3_bank_select_bank']
            if "p3_bank_details_account_type" in kw:
                dct['p3_bank_details_account_type'] = kw['p3_bank_details_account_type']
            if "p3_bank_details_upload_statement_past_month" in kw:
                dct['p3_bank_details_upload_statement_past_month'] = kw['p3_bank_details_upload_statement_past_month']
            if "p3_bank_is_bank_statement_is_password_protected" in kw:
                dct['p3_bank_is_bank_statement_is_password_protected'] = kw['p3_bank_is_bank_statement_is_password_protected']
            if "p3_bank_password" in kw:
                dct['p3_bank_password'] = kw['p3_bank_password']
            

            if 'p_coapplicant_bank_select_bank' in kw:
                dct['p_coapplicant_bank_select_bank'] = kw['p_coapplicant_bank_select_bank']
            if 'p_coapplicant_bank_details_account_type' in kw:
                dct['p_coapplicant_bank_details_account_type'] = kw['p_coapplicant_bank_details_account_type']
            if 'p_coapplicant_bank_details_upload_statement_past_month' in kw:
                dct['p_coapplicant_bank_details_upload_statement_past_month'] = kw['p_coapplicant_bank_details_upload_statement_past_month']
            if 'p_coapplicant_bank_is_bank_statement_is_password_protected' in kw:
                dct['p_coapplicant_bank_is_bank_statement_is_password_protected'] = kw['p_coapplicant_bank_is_bank_statement_is_password_protected']
            if 'p_coapplicant_bank_password' in kw:
                dct['p_coapplicant_bank_password'] = kw['p_coapplicant_bank_password']

            if "pbl2_coapplicant_bank_select_bank" in kw:
                dct['pbl2_coapplicant_bank_select_bank'] = kw['pbl2_coapplicant_bank_select_bank']
            if "pbl2_coapplicant_bank_details_account_type" in kw:
                dct['pbl2_coapplicant_bank_details_account_type'] = kw['pbl2_coapplicant_bank_details_account_type']
            if "pbl2_coapplicant_bank_details_upload_statement_past_month" in kw:
                dct['pbl2_coapplicant_bank_details_upload_statement_past_month'] = kw['pbl2_coapplicant_bank_details_upload_statement_past_month']
            if "pbl2_coapplicant_bank_is_bank_statement_is_password_protected" in kw:
                dct['pbl2_coapplicant_bank_is_bank_statement_is_password_protected'] = kw['pbl2_coapplicant_bank_is_bank_statement_is_password_protected']
            if "pbl2_coapplicant_bank_password" in kw:
                dct['pbl2_coapplicant_bank_password'] = kw['pbl2_coapplicant_bank_password']
            if "pbl3_coapplicant_bank_select_bank" in kw:
                dct['pbl3_coapplicant_bank_select_bank'] = kw['pbl3_coapplicant_bank_select_bank']
            if "pbl3_coapplicant_bank_details_account_type" in kw:
                dct['pbl3_coapplicant_bank_details_account_type'] = kw['pbl3_coapplicant_bank_details_account_type']
            if "pbl3_coapplicant_bank_details_upload_statement_past_month" in kw:
                dct['pbl3_coapplicant_bank_details_upload_statement_past_month'] = kw['pbl3_coapplicant_bank_details_upload_statement_past_month']
            if "pbl3_coapplicant_bank_is_bank_statement_is_password_protected" in kw:
                dct['pbl3_coapplicant_bank_is_bank_statement_is_password_protected'] = kw['pbl3_coapplicant_bank_is_bank_statement_is_password_protected']
            if "pbl3_coapplicant_bank_password" in kw:
                dct['pbl3_coapplicant_bank_password'] = kw['pbl3_coapplicant_bank_password'] 
            if "pbl2_coapplicant_bank_data_is" in kw:
                dct['pbl2_coapplicant_bank_data_is'] = kw['pbl2_coapplicant_bank_data_is']
            if "pbl3_coapplicant_bank_data_is" in kw:
                dct['pbl3_coapplicant_bank_data_is'] = kw['pbl3_coapplicant_bank_data_is']
        
            if "profession_categories_salaried" in kw:
                dct['profession_categories_salaried'] = kw['profession_categories_salaried']
            if "profession_categories_senp" in kw:
                dct['profession_categories_senp'] = kw['profession_categories_senp']
            if "profession_categories_sep" in kw:
                dct['profession_categories_sep'] = kw['profession_categories_sep']
            if "p_business_business_name" in kw:
                dct['p_business_business_name'] = kw['p_business_business_name']
            if "applicant_profession" in kw:
                dct['p_business_profession'] = kw['applicant_profession']
            if "p_business_registration_number" in kw:
                dct['p_business_registration_number'] = kw['p_business_registration_number']
            if "p_business_gstin" in kw:
                dct['p_business_gstin'] = kw['p_business_gstin']
            if "applicant_total_exp_current_role" in kw:
                dct['p_business_years_in_current_profession'] = kw['applicant_total_exp_current_role']
            if "p_business_gross_professional_receipts_as_per_ITR" in kw:
                dct['p_business_gross_professional_receipts_as_per_ITR'] = kw['p_business_gross_professional_receipts_as_per_ITR']
            if "p2_business_gross_professional_receipts_as_per_ITR" in kw:
                dct['p2_business_gross_professional_receipts_as_per_ITR'] = kw['p2_business_gross_professional_receipts_as_per_ITR']
            if "p3_business_gross_professional_receipts_as_per_ITR" in kw:
                dct['p3_business_gross_professional_receipts_as_per_ITR'] = kw['p3_business_gross_professional_receipts_as_per_ITR']
            if "p_business_email_id" in kw:
                dct['p_business_email_id'] = kw['p_business_email_id']
            if "p_business_phone_number" in kw:
                dct['p_business_phone_number'] = kw['p_business_phone_number']
            if "p_business_register_pin_pincode" in kw:
                dct['p_business_register_pin_pincode'] = kw['p_business_register_pin_pincode']
            if "p_business_register_building_number" in kw:
                dct['p_business_register_building_number'] = kw['p_business_register_building_number']
            if "p_business_register_street" in kw:
                dct['p_business_register_street'] = kw['p_business_register_street']
            if "p_business_register_landmark" in kw:
                dct['p_business_register_landmark'] = kw['p_business_register_landmark']
            if "p_business_register_city" in kw:
                dct['p_business_register_city'] = kw['p_business_register_city']
            if "p_business_register_state" in kw:
                dct['p_business_register_state'] = kw['p_business_register_state']
            if "p_business_corporate_register_pin_pincode" in kw:
                dct['p_business_corporate_register_pin_pincode'] = kw['p_business_corporate_register_pin_pincode']
            if "p_business_corporate_register_building_number" in kw:
                dct['p_business_corporate_register_building_number'] = kw['p_business_corporate_register_building_number']
            if "p_business_corporate_register_street" in kw:
                dct['p_business_corporate_register_street'] = kw['p_business_corporate_register_street']
            if "p_business_corporate_register_landmark" in kw:
                dct['p_business_corporate_register_landmark'] = kw['p_business_corporate_register_landmark']
            if "p_business_corporate_register_city" in kw:
                dct['p_business_corporate_register_city'] = kw['p_business_corporate_register_city']
            if "p_business_corporate_register_state" in kw:
                dct['p_business_corporate_register_state'] = kw['p_business_corporate_register_state']   


            if 'p_business_i_am_a' in kw:
                dct['p_business_i_am_a'] = kw['p_business_i_am_a']
            if 'p_business_business_constitution' in kw:
                dct['p_business_business_constitution'] = kw['p_business_business_constitution']
            if 'p_business_monthly_renumeration' in kw:
                dct['p_business_monthly_renumeration'] = kw['p_business_monthly_renumeration']
            if 'p_business_share_holding' in kw:
                dct['p_business_share_holding'] = kw['p_business_share_holding']
            if 'p_business_annual_income' in kw:
                dct['p_business_annual_income'] = kw['p_business_annual_income']
            if 'p_business_share_in_profit' in kw:
                dct['p_business_share_in_profit'] = kw['p_business_share_in_profit']
            if 'p_business_business_name' in kw:
                dct['p_business_business_name'] = kw['p_business_business_name']
            if 'p_business_industry_type' in kw:
                dct['p_business_industry_type'] = kw['p_business_industry_type']
            if 'p_business_industry_sub_class' in kw:
                dct['p_business_industry_sub_class'] = kw['p_business_industry_sub_class']
            if 'p_business_profit_after_tax' in kw:
                dct['p_business_profit_after_tax'] = kw['p_business_profit_after_tax']
            if 'p_business_previous_profit_after_tax' in kw:
                dct['p_business_previous_profit_after_tax'] = kw['p_business_previous_profit_after_tax']
            if 'p_business_current_year_turnover' in kw:
                dct['p_business_current_year_turnover'] = kw['p_business_current_year_turnover']
            if 'p_business_previous_year_turnover' in kw:
                dct['p_business_previous_year_turnover'] = kw['p_business_previous_year_turnover']
            if 'p_business_Cin_number' in kw:
                dct['p_business_Cin_number'] = kw['p_business_Cin_number']
            if 'p_business_gst_number' in kw:
                dct['p_business_gst_number'] = kw['p_business_gst_number']
            if 'p_business_business_pan' in kw:
                dct['p_business_business_pan'] = kw['p_business_business_pan']
            if 'p_business_tin_number' in kw:
                dct['p_business_tin_number'] = kw['p_business_tin_number']
            if 'p_business_tan_number' in kw:
                dct['p_business_tan_number'] = kw['p_business_tan_number']
            if 'p_business_nio_of_partner_director' in kw:
                dct['p_business_nio_of_partner_director'] = kw['p_business_nio_of_partner_director']
            if 'p_business_date_of_incorportaion' in kw:
                dct['p_business_date_of_incorportaion'] = kw['p_business_date_of_incorportaion']
            if 'p_business_business_vintage' in kw:
                dct['p_business_business_vintage'] = kw['p_business_business_vintage']
            if 'p_business_email_id' in kw:
                dct['p_business_email_id'] = kw['p_business_email_id']
            if 'p_business_phn_number' in kw:
                dct['p_business_phn_number'] = kw['p_business_phn_number']
            if 'p_business_year_of_current_business' in kw:
                dct['p_business_year_of_current_business'] = kw['p_business_year_of_current_business']
            if 'p_business_do_you_have_pos' in kw:
                dct['p_business_do_you_have_pos'] = kw['p_business_do_you_have_pos']
            if 'p_business_if_year_what_is_your_monthly_card_swipe' in kw:
                dct['p_business_if_year_what_is_your_monthly_card_swipe'] = kw['p_business_if_year_what_is_your_monthly_card_swipe']

            if 'p_business_co_aaplicant_gross_professional_receipt' in kw:
                dct['p_business_co_aaplicant_gross_professional_receipt'] = kw['p_business_co_aaplicant_gross_professional_receipt']
            if 'p_busness_co_aaplicant_business_name' in kw:
                dct['p_busness_co_aaplicant_business_name'] = kw['p_busness_co_aaplicant_business_name']
            if 'p_busness_co_aaplicant_coaaplicant_is_a' in kw:
                dct['p_busness_co_aaplicant_coaaplicant_is_a'] = kw['p_busness_co_aaplicant_coaaplicant_is_a']
            if 'p_business_co_aaplicant_constitution' in kw:
                dct['p_business_co_aaplicant_constitution'] = kw['p_business_co_aaplicant_constitution']
            if 'p_busness_co_aaplicant_amount' in kw:
                dct['p_busness_co_aaplicant_amount'] = kw['p_busness_co_aaplicant_amount']
            if 'p_busness_co_aaplicant_share_holding' in kw:
                dct['p_busness_co_aaplicant_share_holding'] = kw['p_busness_co_aaplicant_share_holding']
            if 'p_business_co_aaplicant_monthly_renumeration' in kw:
                dct['p_business_co_aaplicant_monthly_renumeration'] = kw['p_business_co_aaplicant_monthly_renumeration']
            if 'p_busness_co_aaplicant_annual_income' in kw:
                dct['p_busness_co_aaplicant_annual_income'] = kw['p_busness_co_aaplicant_annual_income']
            if 'p_busness_co_aaplicant_profit_after_tax_after_current_year' in kw:
                dct['p_busness_co_aaplicant_profit_after_tax_after_current_year'] = kw['p_busness_co_aaplicant_profit_after_tax_after_current_year']
            if 'p_business_co_aaplicant_current_year_turnover' in kw:
                dct['p_business_co_aaplicant_current_year_turnover'] = kw['p_business_co_aaplicant_current_year_turnover']
            if 'p_busness_co_aaplicant_share_in_profit' in kw:
                dct['p_busness_co_aaplicant_share_in_profit'] = kw['p_busness_co_aaplicant_share_in_profit']
            if 'p_busness_co_aaplicant_profit_after_tax_previous_year' in kw:
                dct['p_busness_co_aaplicant_profit_after_tax_previous_year'] = kw['p_busness_co_aaplicant_profit_after_tax_previous_year']
            if 'p_business_co_aaplicant_previous_year_turn_over' in kw:
                dct['p_business_co_aaplicant_previous_year_turn_over'] = kw['p_business_co_aaplicant_previous_year_turn_over']
            if 'p_business_co_aaplicant_source' in kw:
                dct['p_business_co_aaplicant_source'] = kw['p_business_co_aaplicant_source']
            if 'h_property_identify' in kw:
                dct['h_property_identify'] = kw['h_property_identify']
            if 'h_property_sub_type' in kw:
                dct['h_property_sub_type'] = kw['h_property_sub_type']
            if 'h_property_own_by' in kw:
                dct['h_property_own_by'] = kw['h_property_own_by']
            if 'h_project_building_name' in kw:
                dct['h_project_building_name'] = kw['h_project_building_name']
            if 'h_project_project_name' in kw:
                dct['h_project_project_name'] = kw['h_project_project_name']
            if 'h_project_pin_code' in kw:
                dct['h_project_pin_code'] = kw['h_project_pin_code']
            if 'h_project_building_area' in kw:
                dct['h_project_building_area'] = kw['h_project_building_area']
            if 'h_project_unit_no_building_no_flat_number' in kw:
                dct['h_project_unit_no_building_no_flat_number'] = kw['h_project_unit_no_building_no_flat_number']
            if 'h_project_building_street' in kw:
                dct['h_project_building_street'] = kw['h_project_building_street']
            if 'h_project_building_city' in kw:
                dct['h_project_building_city'] = kw['h_project_building_city']
            if 'h_project_building_state' in kw:
                dct['h_project_building_state'] = kw['h_project_building_state']
            if 'h_project_building_housing_authority' in kw:
                dct['h_project_building_housing_authority'] = kw['h_project_building_housing_authority']
            if 'h_project_tower' in kw:
                dct['h_project_tower'] = kw['h_project_tower']
            if 'h_project_building' in kw:
                dct['h_project_building'] = kw['h_project_building']
            if 'h_project_city' in kw:
                dct['h_project_city'] = kw['h_project_city']
            if 'h_project_state' in kw:
                dct['h_project_state'] = kw['h_project_state']
            if 'h_project_area_of_the_property' in kw:
                dct['h_project_area_of_the_property'] = kw['h_project_area_of_the_property']
            if 'h_project_documented_purchse_cost' in kw:
                dct['h_project_documented_purchse_cost'] = kw['h_project_documented_purchse_cost']
            if 'h_project_extimated_market_value' in kw:
                dct['h_project_extimated_market_value'] = kw['h_project_extimated_market_value']
            if 'h_property_pin_code' in kw:
                dct['h_property_pin_code'] = kw['h_property_pin_code']
            if 'h_property_housing_authority' in kw:
                dct['h_property_housing_authority'] = kw['h_property_housing_authority'] 

            if "pl2_coapplicant_obligation_data_is" in kw:
                dct['pl2_coapplicant_obligation_data_is'] = kw['pl2_coapplicant_obligation_data_is']
            if "pl2_coapplicant_obligation_bank_name" in kw:
                dct['pl2_coapplicant_obligation_bank_name'] = kw['pl2_coapplicant_obligation_bank_name']
            if "pl2_coapplicant_obligation_type_of_loan" in kw:
                dct['pl2_coapplicant_obligation_type_of_loan'] = kw['pl2_coapplicant_obligation_type_of_loan']
            if "pl2_coapplicant_obligation_account_number" in kw:
                dct['pl2_coapplicant_obligation_account_number'] = kw['pl2_coapplicant_obligation_account_number']
            if "pl2_coapplicant_obligation_loan_amount" in kw:
                dct['pl2_coapplicant_obligation_loan_amount'] = kw['pl2_coapplicant_obligation_loan_amount']    
            if "pl2_coapplicant_obligation_emi" in kw:
                dct['pl2_coapplicant_obligation_emi'] = kw['pl2_coapplicant_obligation_emi']
            if "pl2_coapplicant_obligation_loan_opening_date" in kw:
                dct['pl2_coapplicant_obligation_loan_opening_date'] = kw['pl2_coapplicant_obligation_loan_opening_date']
            if "pl2_coapplicant_obligation_tenure" in kw:
                dct['pl2_coapplicant_obligation_tenure'] = kw['pl2_coapplicant_obligation_tenure']
            if "pl2_coapplicant_obligation_roi" in kw:
                dct['pl2_coapplicant_obligation_roi'] = kw['pl2_coapplicant_obligation_roi']
            if "pl2_coapplicant_obligation_type_of_security" in kw:
                dct['pl2_coapplicant_obligation_type_of_security'] = kw['pl2_coapplicant_obligation_type_of_security']
            if "pl2_coapplicant_obligation_current_out_standing_amount" in kw:
                dct['pl2_coapplicant_obligation_current_out_standing_amount'] = kw['pl2_coapplicant_obligation_current_out_standing_amount']
            if "pl3_coapplicant_obligation_data_is" in kw:
                dct['pl3_coapplicant_obligation_data_is'] = kw['pl3_coapplicant_obligation_data_is']
            if "pl3_coapplicant_obligation_bank_name" in kw:
                dct['pl3_coapplicant_obligation_bank_name'] = kw['pl3_coapplicant_obligation_bank_name']
            if "pl3_coapplicant_obligation_type_of_loan" in kw:
                dct['pl3_coapplicant_obligation_type_of_loan'] = kw['pl3_coapplicant_obligation_type_of_loan']
            if "pl3_coapplicant_obligation_account_number" in kw:
                dct['pl3_coapplicant_obligation_account_number'] = kw['pl3_coapplicant_obligation_account_number']
            if "pl3_coapplicant_obligation_loan_amount" in kw:
                dct['pl3_coapplicant_obligation_loan_amount'] = kw['pl3_coapplicant_obligation_loan_amount']       
            if "pl3_coapplicant_obligation_emi" in kw:
                dct['pl3_coapplicant_obligation_emi'] = kw['pl3_coapplicant_obligation_emi']
            if "pl3_coapplicant_obligation_loan_opening_date" in kw:
                dct['pl3_coapplicant_obligation_loan_opening_date'] = kw['pl3_coapplicant_obligation_loan_opening_date']
            if "pl3_coapplicant_obligation_tenure" in kw:
                dct['pl3_coapplicant_obligation_tenure'] = kw['pl3_coapplicant_obligation_tenure']
            if "pl3_coapplicant_obligation_roi" in kw:
                dct['pl3_coapplicant_obligation_roi'] = kw['pl3_coapplicant_obligation_roi']
            if "pl3_coapplicant_obligation_type_of_security" in kw:
                dct['pl3_coapplicant_obligation_type_of_security'] = kw['pl3_coapplicant_obligation_type_of_security']
            if "pl3_coapplicant_obligation_current_out_standing_amount" in kw:
                dct['pl3_coapplicant_obligation_current_out_standing_amount'] = kw['pl3_coapplicant_obligation_current_out_standing_amount']    


            if "p3_co_applicant_data" in kw:
                dct['p3_co_applicant_data'] = kw['p3_co_applicant_data']
            if "p3_relationship_with_applicant" in kw:
                dct['p3_relationship_with_applicant'] = kw['p3_relationship_with_applicant']
            if "p3_co_applicant_is" in kw:
                dct['p3_co_applicant_is'] = kw['p3_co_applicant_is']
            coapplicant3_first = ""
            coapplicant3_last = ""
            if "p3_coapplicant_name_first" in kw:
                coapplicant3_first = kw['p3_coapplicant_name_first']
            if "p3_coapplicant_name_second" in kw:
                coapplicant3_last = kw['p3_coapplicant_name_second']

            if 'p3_coapplicant_name_first' in kw:
                coapplicant3_name = coapplicant3_first + coapplicant3_last
                dct['p3_co_applicant_name'] = coapplicant3_name
            if "p3_co_applicant_gender" in kw:
                dct['p3_co_applicant_gender'] = kw['p3_co_applicant_gender'].lower()
            if "p3_co_applicant_marital_status" in kw:
                dct['p3_co_applicant_marital_status'] = kw['p3_co_applicant_marital_status']
            if "p3_co_applicant_father_husband_name" in kw:
                dct['p3_co_applicant_father_husband_name'] = kw['p3_co_applicant_father_husband_name']
            if "p3_co_applicant_educational_qualification" in kw:
                dct['p3_co_applicant_educational_qualification'] = kw['p3_co_applicant_educational_qualification']
            if "p3_co_applicant_personal_email_d" in kw:
                dct['p3_co_applicant_personal_email_d'] = kw['p3_co_applicant_personal_email_d']
            if "p3_co_applicant_mobile_number" in kw:
                dct['p3_co_applicant_mobile_number'] = kw['p3_co_applicant_mobile_number']
            if "p2_relationship_with_applicant" in kw:
                dct['p2_relationship_with_applicant'] = kw['p2_relationship_with_applicant']
            if "p2_co_applicant_is" in kw:
                dct['p2_co_applicant_is'] = kw['p2_co_applicant_is']
            coapplicant2_first = ""
            coapplicant2_last = ""
            if "p2_coapplicant_name_first" in kw:
                coapplicant2_first = kw['p2_coapplicant_name_first']
            if "p2_coapplicant_name_second" in kw:
                coapplicant2_last = kw['p2_coapplicant_name_second']

            if 'p2_coapplicant_name_first' in kw:
                coapplicant2_name = coapplicant2_first + coapplicant2_last
                dct['p2_co_applicant_name'] = coapplicant2_name  
            if "p2_co_applicant_gender" in kw:
                dct['p2_co_applicant_gender'] = kw['p2_co_applicant_gender'].lower()
            if "p2_co_applicant_marital_status" in kw:
                dct['p2_co_applicant_marital_status'] = kw['p2_co_applicant_marital_status']
            if "p2_co_applicant_father_husband_name" in kw:
                dct['p2_co_applicant_father_husband_name'] = kw['p2_co_applicant_father_husband_name']
            if "p2_co_applicant_educational_qualification" in kw:
                dct['p2_co_applicant_educational_qualification'] = kw['p2_co_applicant_educational_qualification']
            if "p2_co_applicant_personal_email_d" in kw:
                dct['p2_co_applicant_personal_email_d'] = kw['p2_co_applicant_personal_email_d']
            if "p2_co_applicant_mobile_number" in kw:
                dct['p2_co_applicant_mobile_number'] = kw['p2_co_applicant_mobile_number']
            if "p2_kyc_coapplicant_type_of_document" in kw:
                dct['p2_kyc_coapplicant_type_of_document'] = kw['p2_kyc_coapplicant_type_of_document']
            if "p2_kyc_coapplicant_current_address_residence_proof_front" in kw:
                dct['p2_kyc_coapplicant_current_address_residence_proof_front'] = kw['p2_kyc_coapplicant_current_address_residence_proof_front']
            if "p2_kyc_coapplicant_current_address_residence_proof_back" in kw:
                dct['p2_kyc_coapplicant_current_address_residence_proof_back'] = kw['p2_kyc_coapplicant_current_address_residence_proof_back']
            if "p2_kyc_coapplicant_current_pan_card_photo" in kw:
                dct['p2_kyc_coapplicant_current_pan_card_photo'] = kw['p2_kyc_coapplicant_current_pan_card_photo']
            if "p2_kyc_coapplicant_current_pan_number" in kw:
                dct['p2_kyc_coapplicant_current_pan_number'] = kw['p2_kyc_coapplicant_current_pan_number']
            if "p2_kyc_coapplicant_current_date_of_birth" in kw:
                dct['p2_kyc_coapplicant_current_date_of_birth'] = kw['p2_kyc_coapplicant_current_date_of_birth']
            if "p3_kyc_coapplicant_type_of_document" in kw:
                dct['p3_kyc_coapplicant_type_of_document'] = kw['p3_kyc_coapplicant_type_of_document']
            if "p3_kyc_coapplicant_current_address_residence_proof_front" in kw:
                dct['p3_kyc_coapplicant_current_address_residence_proof_front'] = kw['p3_kyc_coapplicant_current_address_residence_proof_front']
            if "p3_kyc_coapplicant_current_address_residence_proof_back" in kw:
                dct['p3_kyc_coapplicant_current_address_residence_proof_back'] = kw['p3_kyc_coapplicant_current_address_residence_proof_back']
            if "p3_kyc_coapplicant_current_pan_card_photo" in kw:
                dct['p3_kyc_coapplicant_current_pan_card_photo'] = kw['p3_kyc_coapplicant_current_pan_card_photo']
            if "p3_kyc_coapplicant_current_pan_number" in kw:
                dct['p3_kyc_coapplicant_current_pan_number'] = kw['p3_kyc_coapplicant_current_pan_number']
            if "p3_kyc_coapplicant_current_date_of_birth" in kw:
                dct['p3_kyc_coapplicant_current_date_of_birth'] = kw['p3_kyc_coapplicant_current_date_of_birth']
            if "p3_coapplicant_address_residence_owner_rent" in kw:
                dct['p3_coapplicant_address_residence_owner_rent'] = kw['p3_coapplicant_address_residence_owner_rent']
            if "p3_coapplicant_address_number_of_year_in_current_residence" in kw:
                dct['p3_coapplicant_address_number_of_year_in_current_residence'] = kw['p3_coapplicant_address_number_of_year_in_current_residence']
            if "p3_coapplicant_address_flat_house" in kw:
                dct['p3_coapplicant_address_flat_house'] = kw['p3_coapplicant_address_flat_house']
            if "p3_coapplicant_address_street_lane" in kw:
                dct['p3_coapplicant_address_street_lane'] = kw['p3_coapplicant_address_street_lane']
            if "p3_coapplicant_address_city" in kw:
                dct['p3_coapplicant_address_city'] = kw['p3_coapplicant_address_city']
            if "p3_coapplicant_address_state" in kw:
                dct['p3_coapplicant_address_state'] = kw['p3_coapplicant_address_state']
            if "p3_coapplicant_permant_address_proof" in kw:
                dct['p3_coapplicant_permant_address_proof'] = kw['p3_coapplicant_permant_address_proof']
            if "p3_coapplicant_permant_address_proof_photo" in kw:
                dct['p3_coapplicant_permant_address_proof_photo'] = kw['p3_coapplicant_permant_address_proof_photo']
            if "p3_coapplicant_permant_pin_code" in kw:
                dct['p3_coapplicant_permant_pin_code'] = kw['p3_coapplicant_permant_pin_code']
            if "p3_coapplicant_permant_street_lane" in kw:
                dct['p3_coapplicant_permant_street_lane'] = kw['p3_coapplicant_permant_street_lane']
            if "p3_coapplicant_permant_flat_house" in kw:
                dct['p3_coapplicant_permant_flat_house'] = kw['p3_coapplicant_permant_flat_house']
            if "p3_coapplicant_permant_state" in kw:
                dct['p3_coapplicant_permant_state'] = kw['p3_coapplicant_permant_state']
            if "p3_coapplicant_permant_city" in kw:
                dct['p3_coapplicant_permant_city'] = kw['p3_coapplicant_permant_city']
            if "p2_coapplicant_address_residence_owner_rent" in kw:
                dct['p2_coapplicant_address_residence_owner_rent'] = kw['p2_coapplicant_address_residence_owner_rent']
            if "p2_coapplicant_address_number_of_year_in_current_residence" in kw:
                dct['p2_coapplicant_address_number_of_year_in_current_residence'] = kw['p2_coapplicant_address_number_of_year_in_current_residence']
            if "p2_coapplicant_address_flat_house" in kw:
                dct['p2_coapplicant_address_flat_house'] = kw['p2_coapplicant_address_flat_house']
            if "p2_coapplicant_address_street_lane" in kw:
                dct['p2_coapplicant_address_street_lane'] = kw['p2_coapplicant_address_street_lane']
            if "p2_coapplicant_address_city" in kw:
                dct['p2_coapplicant_address_city'] = kw['p2_coapplicant_address_city']
            if "p2_coapplicant_address_state" in kw:
                dct['p2_coapplicant_address_state'] = kw['p2_coapplicant_address_state']
            if "p2_coapplicant_permant_address_proof" in kw:
                dct['p2_coapplicant_permant_address_proof'] = kw['p2_coapplicant_permant_address_proof']
            if "p2_coapplicant_permant_address_proof_photo" in kw:
                dct['p2_coapplicant_permant_address_proof_photo'] = kw['p2_coapplicant_permant_address_proof_photo']
            if "p2_coapplicant_permant_pin_code" in kw:
                dct['p2_coapplicant_permant_pin_code'] = kw['p2_coapplicant_permant_pin_code']
            if "p2_coapplicant_permant_street_lane" in kw:
                dct['p2_coapplicant_permant_street_lane'] = kw['p2_coapplicant_permant_street_lane']
            if "p2_coapplicant_permant_flat_house" in kw:
                dct['p2_coapplicant_permant_flat_house'] = kw['p2_coapplicant_permant_flat_house']
            if "p2_coapplicant_permant_state" in kw:
                dct['p2_coapplicant_permant_state'] = kw['p2_coapplicant_permant_state']
            if "p2_coapplicant_permant_city" in kw:
                dct['p2_coapplicant_permant_city'] = kw['p2_coapplicant_permant_city']
            if "p2_business_co_aaplicant_year_in_current_job_year_month" in kw:
                dct['p2_business_co_aaplicant_year_in_current_job_year_month'] = kw['p2_business_co_aaplicant_year_in_current_job_year_month']
            p2_busness_co_aaplicant_total_work_experieance_year = 0
            p2_busness_co_aaplicant_total_work_experieance_month = 0
            if 'p2_busness_co_aaplicant_total_work_experieance_year' in kw:
                p2_busness_co_aaplicant_total_work_experieance_year = int(kw['p2_busness_co_aaplicant_total_work_experieance_year'])
            if 'p2_busness_co_aaplicant_total_work_experieance_month' in kw:
                p2_busness_co_aaplicant_total_work_experieance_month = int(kw['p2_busness_co_aaplicant_total_work_experieance_month']) / 12

            if 'p2_busness_co_aaplicant_total_work_experieance_year' in kw:
                dct['p2_busness_co_aaplicant_total_work_experieance'] = p2_busness_co_aaplicant_total_work_experieance_year + p2_busness_co_aaplicant_total_work_experieance_month

            if "p2_busness_co_aaplicant_net_monthly_salary" in kw:
                dct['p2_busness_co_aaplicant_net_monthly_salary'] = kw['p2_busness_co_aaplicant_net_monthly_salary']
            if "p2_business_co_aaplicant_gross_monthly_salary" in kw:
                dct['p2_business_co_aaplicant_gross_monthly_salary'] = kw['p2_business_co_aaplicant_gross_monthly_salary']
            if "p2_business_co_aaplicant_employment_type" in kw:
                dct['p2_business_co_aaplicant_employment_type'] = kw['p2_business_co_aaplicant_employment_type']
            if "p2_business_co_aaplicant_orginization_name" in kw:
                dct['p2_business_co_aaplicant_orginization_name'] = kw['p2_business_co_aaplicant_orginization_name']
            if "p2_business_co_aaplicant_designation" in kw:
                dct['p2_business_co_aaplicant_designation'] = kw['p2_business_co_aaplicant_designation']
            if "p2_business_co_aaplicant_department" in kw:
                dct['p2_business_co_aaplicant_department'] = kw['p2_business_co_aaplicant_department']
            if "p3_business_co_aaplicant_year_in_current_job_year_month" in kw:
                dct['p3_business_co_aaplicant_year_in_current_job_year_month'] = kw['p3_business_co_aaplicant_year_in_current_job_year_month']
            p3_busness_co_aaplicant_total_work_experieance_year = 0
            p3_busness_co_aaplicant_total_work_experieance_month = 0
            if 'p3_busness_co_aaplicant_total_work_experieance_year' in kw:
                p3_busness_co_aaplicant_total_work_experieance_year = int(kw['p3_busness_co_aaplicant_total_work_experieance_year'])
            if 'p3_busness_co_aaplicant_total_work_experieance_month' in kw:
                p3_busness_co_aaplicant_total_work_experieance_month = int(kw['p3_busness_co_aaplicant_total_work_experieance_month']) / 12

            if 'p3_busness_co_aaplicant_total_work_experieance_year' in kw:
                dct['p3_busness_co_aaplicant_total_work_experieance'] = p3_busness_co_aaplicant_total_work_experieance_year + p3_busness_co_aaplicant_total_work_experieance_month

            if "p3_busness_co_aaplicant_net_monthly_salary" in kw:
                dct['p3_busness_co_aaplicant_net_monthly_salary'] = kw['p3_busness_co_aaplicant_net_monthly_salary']
            if "p3_business_co_aaplicant_gross_monthly_salary" in kw:
                dct['p3_business_co_aaplicant_gross_monthly_salary'] = kw['p3_business_co_aaplicant_gross_monthly_salary']
            if "p3_business_co_aaplicant_employment_type" in kw:
                dct['p3_business_co_aaplicant_employment_type'] = kw['p3_business_co_aaplicant_employment_type']
            if "p3_business_co_aaplicant_orginization_name" in kw:
                dct['p3_business_co_aaplicant_orginization_name'] = kw['p3_business_co_aaplicant_orginization_name']
            if "p3_business_co_aaplicant_designation" in kw:
                dct['p3_business_co_aaplicant_designation'] = kw['p3_business_co_aaplicant_designation']
            if "p3_business_co_aaplicant_department" in kw:
                dct['p3_business_co_aaplicant_department'] = kw['p3_business_co_aaplicant_department']
            if "p2_obligation_loan" in kw:
                dct['p2_obligation_loan'] = kw['p2_obligation_loan']
            if "p2_obligation_bank_name" in kw:
                dct['p2_obligation_bank_name'] = kw['p2_obligation_bank_name']
            if "p2_obligation_type_of_loan" in kw:
                dct['p2_obligation_type_of_loan'] = kw['p2_obligation_type_of_loan']
            if "p2_obligation_loan_amount" in kw:
                dct['p2_obligation_loan_amount'] = kw['p2_obligation_loan_amount']
            if "p2_obligation_account_number" in kw:
                dct['p2_obligation_account_number'] = kw['p2_obligation_account_number']
            if "p2_obligation_emi" in kw:
                dct['p2_obligation_emi'] = kw['p2_obligation_emi']
            if "p2_obligation_loan_opening_date" in kw:
                dct['p2_obligation_loan_opening_date'] = kw['p2_obligation_loan_opening_date']
            if "p2_obligation_tenure" in kw:
                dct['p2_obligation_tenure'] = kw['p2_obligation_tenure']
            if "p2_obligation_roi" in kw:
                dct['p2_obligation_roi'] = kw['p2_obligation_roi']
            if "p2_obligation_type_of_security" in kw:
                dct['p2_obligation_type_of_security'] = kw['p2_obligation_type_of_security']
            if "p2_obligation_current_out_standing_amount" in kw:
                dct['p2_obligation_current_out_standing_amount'] = kw['p2_obligation_current_out_standing_amount']
            if "p3_obligation_loan" in kw:
                dct['p3_obligation_loan'] = kw['p3_obligation_loan']
            if "p3_obligation_bank_name" in kw:
                dct['p3_obligation_bank_name'] = kw['p3_obligation_bank_name']
            if "p3_obligation_loan_amount" in kw:
                dct['p3_obligation_loan_amount'] = kw['p3_obligation_loan_amount']
            if "p3_obligation_type_of_loan" in kw:
                dct['p3_obligation_type_of_loan'] = kw['p3_obligation_type_of_loan']
            if "p3_obligation_account_number" in kw:
                dct['p3_obligation_account_number'] = kw['p3_obligation_account_number']
            if "p3_obligation_emi" in kw:
                dct['p3_obligation_emi'] = kw['p3_obligation_emi']
            if "p3_obligation_loan_opening_date" in kw:
                dct['p3_obligation_loan_opening_date'] = kw['p3_obligation_loan_opening_date']
            if "p3_obligation_tenure" in kw:
                dct['p3_obligation_tenure'] = kw['p3_obligation_tenure']
            if "p3_obligation_roi" in kw:
                dct['p3_obligation_roi'] = kw['p3_obligation_roi']
            if "p3_obligation_type_of_security" in kw:
                dct['p3_obligation_type_of_security'] = kw['p3_obligation_type_of_security']
            if "p3_obligation_current_out_standing_amount" in kw:
                dct['p3_obligation_current_out_standing_amount'] = kw['p3_obligation_current_out_standing_amount']
            if "p3_obligation_credit_card" in kw:
                dct['p3_obligation_credit_card'] = kw['p3_obligation_credit_card']
            if "p3_obligation_current_credit_out_standing_amount" in kw:
                dct['p3_obligation_current_credit_out_standing_amount'] = kw['p3_obligation_current_credit_out_standing_amount']
            if "p3_obligation_credit_bank_name" in kw:
                dct['p3_obligation_credit_bank_name'] = kw['p3_obligation_credit_bank_name']
            if "p3_obligation_credit_limit" in kw:
                dct['p3_obligation_credit_limit'] = kw['p3_obligation_credit_limit']
            if "p3_coapplicant_obligation_credit_card" in kw:
                dct['p3_coapplicant_obligation_credit_card'] = kw['p3_coapplicant_obligation_credit_card']
            if "p3_coapplicant_obligation_current_credit_out_standing_amount" in kw:
                dct['p3_coapplicant_obligation_current_credit_out_standing_amount'] = kw['p3_coapplicant_obligation_current_credit_out_standing_amount']
            if "p3_coapplicant_obligation_credit_bank_name" in kw:
                dct['p3_coapplicant_obligation_credit_bank_name'] = kw['p3_coapplicant_obligation_credit_bank_name']
            if "p3_coapplicant_obligation_credit_limit" in kw:
                dct['p3_coapplicant_obligation_credit_limit'] = kw['p3_coapplicant_obligation_credit_limit']
            if "p3_coapplicant_obligation_bank_name" in kw:
                dct['p3_coapplicant_obligation_bank_name'] = kw['p3_coapplicant_obligation_bank_name']
            if "p3_coapplicant_obligation_type_of_loan" in kw:
                dct['p3_coapplicant_obligation_type_of_loan'] = kw['p3_coapplicant_obligation_type_of_loan']
            if "p3_coapplicant_obligation_account_number" in kw:
                dct['p3_coapplicant_obligation_account_number'] = kw['p3_coapplicant_obligation_account_number']
            if 'p3_coapplicant_obligation_loan_amount' in kw:
                dct['p3_coapplicant_obligation_loan_amount'] = kw['p3_coapplicant_obligation_loan_amount']    
            if "p3_coapplicant_obligation_emi" in kw:
                dct['p3_coapplicant_obligation_emi'] = kw['p3_coapplicant_obligation_emi']
            if "p3_coapplicant_obligation_loan_opening_date" in kw:
                dct['p3_coapplicant_obligation_loan_opening_date'] = kw['p3_coapplicant_obligation_loan_opening_date']
            if "p3_coapplicant_obligation_tenure" in kw:
                dct['p3_coapplicant_obligation_tenure'] = kw['p3_coapplicant_obligation_tenure']
            if "p3_coapplicant_obligation_roi" in kw:
                dct['p3_coapplicant_obligation_roi'] = kw['p3_coapplicant_obligation_roi']
            if "p3_coapplicant_obligation_type_of_security" in kw:
                dct['p3_coapplicant_obligation_type_of_security'] = kw['p3_coapplicant_obligation_type_of_security']
            if "p3_coapplicant_obligation_current_out_standing_amount" in kw:
                dct['p3_coapplicant_obligation_current_out_standing_amount'] = kw['p3_coapplicant_obligation_current_out_standing_amount']
            if "p2_coapplicant_obligation_bank_name" in kw:
                dct['p2_coapplicant_obligation_bank_name'] = kw['p2_coapplicant_obligation_bank_name']
            if "p2_coapplicant_obligation_type_of_loan" in kw:
                dct['p2_coapplicant_obligation_type_of_loan'] = kw['p2_coapplicant_obligation_type_of_loan']
            if "p2_coapplicant_obligation_account_number" in kw:
                dct['p2_coapplicant_obligation_account_number'] = kw['p2_coapplicant_obligation_account_number']
            if 'p2_coapplicant_obligation_loan_amount' in kw:
                dct['p2_coapplicant_obligation_loan_amount'] = kw['p2_coapplicant_obligation_loan_amount']       
            if "p2_coapplicant_obligation_emi" in kw:
                dct['p2_coapplicant_obligation_emi'] = kw['p2_coapplicant_obligation_emi']
            if "p2_coapplicant_obligation_loan_opening_date" in kw:
                dct['p2_coapplicant_obligation_loan_opening_date'] = kw['p2_coapplicant_obligation_loan_opening_date']
            if "p2_coapplicant_obligation_tenure" in kw:
                dct['p2_coapplicant_obligation_tenure'] = kw['p2_coapplicant_obligation_tenure']
            if "p2_coapplicant_obligation_roi" in kw:
                dct['p2_coapplicant_obligation_roi'] = kw['p2_coapplicant_obligation_roi']
            if "p2_coapplicant_obligation_type_of_security" in kw:
                dct['p2_coapplicant_obligation_type_of_security'] = kw['p2_coapplicant_obligation_type_of_security']
            if "p2_coapplicant_obligation_current_out_standing_amount" in kw:
                dct['p2_coapplicant_obligation_current_out_standing_amount'] = kw['p2_coapplicant_obligation_current_out_standing_amount']
            if "p2_coapplicant_bank_select_bank" in kw:
                dct['p2_coapplicant_bank_select_bank'] = kw['p2_coapplicant_bank_select_bank']
            if "p2_coapplicant_bank_details_account_type" in kw:
                dct['p2_coapplicant_bank_details_account_type'] = kw['p2_coapplicant_bank_details_account_type']
            if "p2_coapplicant_bank_details_upload_statement_past_month" in kw:
                dct['p2_coapplicant_bank_details_upload_statement_past_month'] = kw['p2_coapplicant_bank_details_upload_statement_past_month']
            if "p2_coapplicant_bank_is_bank_statement_is_password_protected" in kw:
                dct['p2_coapplicant_bank_is_bank_statement_is_password_protected'] = kw['p2_coapplicant_bank_is_bank_statement_is_password_protected']
            if "p2_coapplicant_bank_password" in kw:
                dct['p2_coapplicant_bank_password'] = kw['p2_coapplicant_bank_password']
            if "p3_coapplicant_bank_select_bank" in kw:
                dct['p3_coapplicant_bank_select_bank'] = kw['p3_coapplicant_bank_select_bank']
            if "p3_coapplicant_bank_details_account_type" in kw:
                dct['p3_coapplicant_bank_details_account_type'] = kw['p3_coapplicant_bank_details_account_type']
            if "p3_coapplicant_bank_details_upload_statement_past_month" in kw:
                dct['p3_coapplicant_bank_details_upload_statement_past_month'] = kw['p3_coapplicant_bank_details_upload_statement_past_month']
            if "p3_coapplicant_bank_is_bank_statement_is_password_protected" in kw:
                dct['p3_coapplicant_bank_is_bank_statement_is_password_protected'] = kw['p3_coapplicant_bank_is_bank_statement_is_password_protected']
            if "p3_coapplicant_bank_password" in kw:
                dct['p3_coapplicant_bank_password'] = kw['p3_coapplicant_bank_password']
            if "p2_business_co_aaplicant_gross_professional_receipt" in kw:
                dct['p2_business_co_aaplicant_gross_professional_receipt'] = kw['p2_business_co_aaplicant_gross_professional_receipt']
            if "p2_busness_co_aaplicant_business_name" in kw:
                dct['p2_busness_co_aaplicant_business_name'] = kw['p2_busness_co_aaplicant_business_name']
            if "p2_busness_co_aaplicant_coaaplicant_is_a" in kw:
                dct['p2_busness_co_aaplicant_coaaplicant_is_a'] = kw['p2_busness_co_aaplicant_coaaplicant_is_a']
            if "p2_business_co_aaplicant_constitution" in kw:
                dct['p2_business_co_aaplicant_constitution'] = kw['p2_business_co_aaplicant_constitution']
            if "p2_busness_co_aaplicant_amount" in kw:
                dct['p2_busness_co_aaplicant_amount'] = kw['p2_busness_co_aaplicant_amount']
            if "p2_busness_co_aaplicant_share_holding" in kw:
                dct['p2_busness_co_aaplicant_share_holding'] = kw['p2_busness_co_aaplicant_share_holding']
            if "p2_business_co_aaplicant_monthly_renumeration" in kw:
                dct['p2_business_co_aaplicant_monthly_renumeration'] = kw['p2_business_co_aaplicant_monthly_renumeration']
            if "p2_busness_co_aaplicant_annual_income" in kw:
                dct['p2_busness_co_aaplicant_annual_income'] = kw['p2_busness_co_aaplicant_annual_income']
            if "p2_busness_co_aaplicant_profit_after_tax_after_current_year" in kw:
                dct['p2_busness_co_aaplicant_profit_after_tax_after_current_year'] = kw['p2_busness_co_aaplicant_profit_after_tax_after_current_year']
            if "p2_business_co_aaplicant_current_year_turnover" in kw:
                dct['p2_business_co_aaplicant_current_year_turnover'] = kw['p2_business_co_aaplicant_current_year_turnover']
            if "p2_busness_co_aaplicant_share_in_profit" in kw:
                dct['p2_busness_co_aaplicant_share_in_profit'] = kw['p2_busness_co_aaplicant_share_in_profit']
            if "p2_busness_co_aaplicant_profit_after_tax_previous_year" in kw:
                dct['p2_busness_co_aaplicant_profit_after_tax_previous_year'] = kw['p2_busness_co_aaplicant_profit_after_tax_previous_year']
            if "p2_business_co_aaplicant_previous_year_turn_over" in kw:
                dct['p2_business_co_aaplicant_previous_year_turn_over'] = kw['p2_business_co_aaplicant_previous_year_turn_over']
            if "p2_business_co_aaplicant_source" in kw:
                dct['p2_business_co_aaplicant_source'] = kw['p2_business_co_aaplicant_source']
            if "p3_business_co_aaplicant_gross_professional_receipt" in kw:
                dct['p3_business_co_aaplicant_gross_professional_receipt'] = kw['p3_business_co_aaplicant_gross_professional_receipt']
            if "p3_busness_co_aaplicant_business_name" in kw:
                dct['p3_busness_co_aaplicant_business_name'] = kw['p3_busness_co_aaplicant_business_name']
            if "p3_busness_co_aaplicant_coaaplicant_is_a" in kw:
                dct['p3_busness_co_aaplicant_coaaplicant_is_a'] = kw['p3_busness_co_aaplicant_coaaplicant_is_a']
            if "p3_business_co_aaplicant_constitution" in kw:
                dct['p3_business_co_aaplicant_constitution'] = kw['p3_business_co_aaplicant_constitution']
            if "p3_busness_co_aaplicant_amount" in kw:
                dct['p3_busness_co_aaplicant_amount'] = kw['p3_busness_co_aaplicant_amount']
            if "p3_busness_co_aaplicant_share_holding" in kw:
                dct['p3_busness_co_aaplicant_share_holding'] = kw['p3_busness_co_aaplicant_share_holding']
            if "p3_business_co_aaplicant_monthly_renumeration" in kw:
                dct['p3_business_co_aaplicant_monthly_renumeration'] = kw['p3_business_co_aaplicant_monthly_renumeration']
            if "p3_busness_co_aaplicant_annual_income" in kw:
                dct['p3_busness_co_aaplicant_annual_income'] = kw['p3_busness_co_aaplicant_annual_income']
            if "p3_busness_co_aaplicant_profit_after_tax_after_current_year" in kw:
                dct['p3_busness_co_aaplicant_profit_after_tax_after_current_year'] = kw['p3_busness_co_aaplicant_profit_after_tax_after_current_year']
            if "p3_business_co_aaplicant_current_year_turnover" in kw:
                dct['p3_business_co_aaplicant_current_year_turnover'] = kw['p3_business_co_aaplicant_current_year_turnover']
            if "p3_busness_co_aaplicant_share_in_profit" in kw:
                dct['p3_busness_co_aaplicant_share_in_profit'] = kw['p3_busness_co_aaplicant_share_in_profit']
            if "p3_busness_co_aaplicant_profit_after_tax_previous_year" in kw:
                dct['p3_busness_co_aaplicant_profit_after_tax_previous_year'] = kw['p3_busness_co_aaplicant_profit_after_tax_previous_year']
            if "p3_business_co_aaplicant_previous_year_turn_over" in kw:
                dct['p3_business_co_aaplicant_previous_year_turn_over'] = kw['p3_business_co_aaplicant_previous_year_turn_over']
            if "p3_business_co_aaplicant_source" in kw:
                dct['p3_business_co_aaplicant_source'] = kw['p3_business_co_aaplicant_source']
            if "p2_coapplicant_pincode" in kw:
                dct['p2_coapplicant_pincode'] = kw['p2_coapplicant_pincode']
            if "p3_coapplicant_pincode" in kw:
                dct['p3_coapplicant_pincode'] = kw['p3_coapplicant_pincode']
            if "p_co_applicant_data" in kw:
                dct['p_co_applicant_data'] = kw['p_co_applicant_data']
            if "p2_co_applicant_data" in kw:
                dct['p2_co_applicant_data'] = kw['p2_co_applicant_data']
            if "p3_co_applicant_data" in kw:
                dct['p3_co_applicant_data'] = kw['p3_co_applicant_data']
            if "p_kyc_coapplicant_data_is" in kw:
                dct['p_kyc_coapplicant_data_is'] = kw['p_kyc_coapplicant_data_is']
            if "p2_kyc_coapplicant_data_is" in kw:
                dct['p2_kyc_coapplicant_data_is'] = kw['p2_kyc_coapplicant_data_is']
            if "p3_kyc_coapplicant_data_is" in kw:
                dct['p3_kyc_coapplicant_data_is'] = kw['p3_kyc_coapplicant_data_is']
            if "p_coapplicant_address_data_is" in kw:
                dct['p_coapplicant_address_data_is'] = kw['p_coapplicant_address_data_is']
            if "p2_coapplicant_address_data_is" in kw:
                dct['p2_coapplicant_address_data_is'] = kw['p2_coapplicant_address_data_is']
            if "p3_coapplicant_address_data_is" in kw:
                dct['p3_coapplicant_address_data_is'] = kw['p3_coapplicant_address_data_is']
            if "p_business_co_aaplicant_data_is" in kw:
                dct['p_business_co_aaplicant_data_is'] = kw['p_business_co_aaplicant_data_is']
            if "p2_business_co_aaplicant_data_is" in kw:
                dct['p2_business_co_aaplicant_data_is'] = kw['p2_business_co_aaplicant_data_is']
            if "p3_business_co_aaplicant_data_is" in kw:
                dct['p3_business_co_aaplicant_data_is'] = kw['p3_business_co_aaplicant_data_is']
            if "p_coapplicant_obligation_data_is" in kw:
                dct['p_coapplicant_obligation_data_is'] = kw['p_coapplicant_obligation_data_is']
            if "p2_coapplicant_obligation_data_is" in kw:
                dct['p2_coapplicant_obligation_data_is'] = kw['p2_coapplicant_obligation_data_is']
            if "p3_coapplicant_obligation_data_is" in kw:
                dct['p3_coapplicant_obligation_data_is'] = kw['p3_coapplicant_obligation_data_is']
            if "p_coapplicant_bank_data_is" in kw:
                dct['p_coapplicant_bank_data_is'] = kw['p_coapplicant_bank_data_is']
            if "p2_coapplicant_bank_data_is" in kw:
                dct['p2_coapplicant_bank_data_is'] = kw['p2_coapplicant_bank_data_is']
            if "p3_coapplicant_bank_data_is" in kw:
                dct['p3_coapplicant_bank_data_is'] = kw['p3_coapplicant_bank_data_is']       

            # if 'email' in kw:
            #     dct['name'] = kw['name']
            #     name = kw['name']
            # if 'phone' in kw:
            #     dct['phone'] = kw['phone']
            #     phone = kw['phone'] 
            # if 'email_from' in kw:
            #     dct['email_from'] = kw['email_from']
            #     email = kw['email_from']         

            customer = request.env['res.partner'].sudo().search([('lead_id','=',lead_id)], limit=1)
            loan_lead = request.env['capwise.lead'].sudo().search([('lead_id','=',lead_id) ,("loan_type", '=',loan_type)], limit=1)
            
            if not loan_lead:
                dsa = request.env['res.partner'].sudo().search([('phone','=',dsa_phone)],limit=1)
                if not dsa:
                    dsa = dsa.create({
                        'name' : dsa_name,
                        'phone': dsa_phone,
                        })
                dct['dsa_id'] = dsa.id 
                crm_obj = request.env['crm.lead'].sudo().search([('phone','=',dsa_phone)], limit=1)
                if crm_obj and crm_obj.user_id:
                    dct['user_id'] = crm_obj.user_id.id
            if not customer:
                customer = customer.create({
                    'name' : customer_name,
                    'phone': customer_phone,
                    'email' : customer_email,
                    "lead_id" : lead_id
                    })
            dct['partner_id'] = customer.id
            loan_lead = request.env['capwise.lead'].sudo().search([('lead_id','=',lead_id),("loan_type", '=',loan_type)], limit=1)
            if not loan_lead:
                loan_lead = loan_lead.create(dct)
            if loan_lead:
                loan_lead.update(dct)

        args = {'success': True, 'message': 'Success', 'ID':loan_lead.id}
        return args             





    @http.route('/capwise/create_loan/home_loan', type="json", auth='public',website=True, method=['GET', 'POST'])
    def loan_lead_home(self, **kw):
        dct = {}
        dsa_name = False
        dsa_email = False
        if request.jsonrequest:
            kw = request.jsonrequest
            _logger.info("dsa_name##@@@@@###########****************%s" %kw)
            if 'partner_mobile' in kw:
                dsa_phone   = kw['partner_mobile']
            if 'dsa_email' in kw:
                dsa_email   = kw['dsa_email']
            if 'loan_type' in kw:
                dct['loan_type'] = kw['loan_type'].lower()
                loan_type = kw['loan_type'].lower()
            if 'lead_id' in kw:
                lead_id = str(kw['lead_id'])
                dct['lead_id'] = kw['lead_id']

            if "lead_loan_amount" in kw:
                dct['expected_revenue'] = kw['lead_loan_amount']
            if "lead_business_constitution" in kw:
                dct['constitution'] = kw['lead_business_constitution']    
            if "lead_profession_type" in kw:
                dct['profession'] = kw['lead_profession_type']
            if "lead_purpose" in kw:
                dct['purpose_of_loan'] = kw['lead_purpose']

            # if "creditScore" in kw:
            #     credit_loop = 0
            #     for credit in kw['creditScore']:
            #         if "vendor_payload_response":
            #             # json_data = json.loads(credit["vendor_payload_response"])
            #             # _logger.info("json_data##@@@@@###########****************%s" %json_data)
            #             if "{" in credit["vendor_payload_response"]:
            #                 print("data")
            #             else:    
            #                 p = check_output(['node', '/opt/odoo/capwise/capwise_crm/static/src/js/node.js', credit["vendor_payload_response"]])
            #                 json_object = json.loads(p)
            #                 if "showHtmlReportForCreditReport" in json_object:
            #                     dct["credit_score"] = json_object.get("showHtmlReportForCreditReport") 
            #         credit_loop = credit_loop + 1       


            if isinstance(kw['lead_data'], list):
                data_line = 0
                for existing_obligation in kw['lead_data']:  
                    if data_line == 0:
                        if "lead_id" in existing_obligation:
                            dct['p_obligation_loan'] = True  
                        if 'loan_amount' in existing_obligation:
                            dct['p_obligation_loan_amount'] = existing_obligation['loan_amount'] 
                        if 'lead_bank_id' in existing_obligation:
                            dct['p_obligation_bank_name'] = existing_obligation['lead_bank_id']
                        if 'lead_type_of_loan' in existing_obligation:
                            dct['p_obligation_type_of_loan'] = existing_obligation['lead_type_of_loan']
                        if 'loan_account_number' in existing_obligation:
                            dct['p_obligation_account_number'] = existing_obligation['loan_account_number']
                        if 'emi' in existing_obligation:
                            dct['p_obligation_emi'] = existing_obligation['emi']
                        if 'lead_loan_opening_date' in existing_obligation:
                            dct['p_obligation_loan_opening_date'] = existing_obligation['lead_loan_opening_date']
                        if 'lead_tenure' in existing_obligation:
                            dct['p_obligation_tenure'] = existing_obligation['lead_tenure']
                        if 'lead_rate_of_interest' in existing_obligation:
                            dct['p_obligation_roi'] = existing_obligation['lead_rate_of_interest']
                        if 'lead_type_of_security' in existing_obligation:
                            dct['p_obligation_type_of_security'] = existing_obligation['lead_type_of_security']
                        if 'lead_current_outstanding_amount' in existing_obligation:
                            dct['p_obligation_current_out_standing_amount'] = existing_obligation['lead_current_outstanding_amount']
                    if data_line == 1:
                        if "lead_id" in existing_obligation:
                            dct['p2_obligation_loan'] = True
                        if "lead_bank_id" in existing_obligation:
                            dct['p2_obligation_bank_name'] = existing_obligation['lead_bank_id']
                        if "lead_type_of_loan" in existing_obligation:
                            dct['p2_obligation_type_of_loan'] = existing_obligation['lead_type_of_loan']
                        if "loan_amount" in existing_obligation:
                            dct['p2_obligation_loan_amount'] = existing_obligation['loan_amount']
                        if "loan_account_number" in existing_obligation:
                            dct['p2_obligation_account_number'] = existing_obligation['loan_account_number']
                        if "emi" in existing_obligation:
                            dct['p2_obligation_emi'] = existing_obligation['emi']
                        if "lead_loan_opening_date" in existing_obligation:
                            dct['p2_obligation_loan_opening_date'] = existing_obligation['lead_loan_opening_date']
                        if "lead_tenure" in existing_obligation:
                            dct['p2_obligation_tenure'] = existing_obligation['lead_tenure']
                        if "lead_rate_of_interest" in existing_obligation:
                            dct['p2_obligation_roi'] = existing_obligation['lead_rate_of_interest']
                        if "lead_type_of_security" in existing_obligation:
                            dct['p2_obligation_type_of_security'] = existing_obligation['lead_type_of_security']
                        if "lead_current_outstanding_amount" in existing_obligation:
                            dct['p2_obligation_current_out_standing_amount'] = existing_obligation['lead_current_outstanding_amount']
                        
                    if data_line == 2:
                        if "lead_id" in existing_obligation:
                            dct['p3_obligation_loan'] = True
                        if "lead_bank_id" in existing_obligation:
                            dct['p3_obligation_bank_name'] = existing_obligation['lead_bank_id']
                        if "loan_amount" in existing_obligation:
                            dct['p3_obligation_loan_amount'] = existing_obligation['loan_amount']
                        if "lead_type_of_loan" in existing_obligation:
                            dct['p3_obligation_type_of_loan'] = existing_obligation['lead_type_of_loan']
                        if "loan_account_number" in existing_obligation:
                            dct['p3_obligation_account_number'] = existing_obligation['loan_account_number']
                        if "emi" in existing_obligation:
                            dct['p3_obligation_emi'] = existing_obligation['emi']
                        if "lead_loan_opening_date" in existing_obligation:
                            dct['p3_obligation_loan_opening_date'] = existing_obligation['lead_loan_opening_date']
                        if "lead_tenure" in existing_obligation:
                            dct['p3_obligation_tenure'] = existing_obligation['lead_tenure']
                        if "lead_rate_of_interest" in existing_obligation:
                            dct['p3_obligation_roi'] = existing_obligation['lead_rate_of_interest']
                        if "lead_type_of_security" in existing_obligation:
                            dct['p3_obligation_type_of_security'] = existing_obligation['lead_type_of_security']
                        if "lead_current_outstanding_amount" in existing_obligation:
                            dct['p3_obligation_current_out_standing_amount'] = existing_obligation['lead_current_outstanding_amount']
                        if "p3_obligation_credit_card" in existing_obligation:
                            dct['p3_obligation_credit_card'] = existing_obligation['p3_obligation_credit_card']
                        if "p3_obligation_current_credit_out_standing_amount" in existing_obligation:
                            dct['p3_obligation_current_credit_out_standing_amount'] = existing_obligation['p3_obligation_current_credit_out_standing_amount']
                        if "p3_obligation_credit_bank_name" in existing_obligation:
                            dct['p3_obligation_credit_bank_name'] = existing_obligation['p3_obligation_credit_bank_name']
                        if "p3_obligation_credit_limit" in existing_obligation:
                            dct['p3_obligation_credit_limit'] = existing_obligation['p3_obligation_credit_limit']
                    data_line = data_line + 1
            if 'lead_data' in kw:
                kw = kw['lead_data']
                if 'h_property_identify' in kw:
                    dct['h_property_identify'] = kw['h_property_identify']
                if 'property_sub_type' in kw:
                    dct['h_property_sub_type'] = kw['property_sub_type']
                if 'property_owned_by' in kw:
                    dct['h_property_own_by'] = kw['property_owned_by']
                if "lead_tenure_in_months" in kw:
                    dct["lead_tenure_in_months"] = kw["lead_tenure_in_months"]

                if "project_details" in kw:
                    project_details = kw['project_details'] 
                    if 'builder_name' in project_details:
                        dct['h_project_building_name'] = project_details['builder_name']
                    if 'project_name' in project_details:
                        dct['h_project_project_name'] = project_details['project_name']
                    if 'project_address_pincode' in project_details:
                        dct['h_project_pin_code'] = project_details['project_address_pincode']
                    if 'project_address_area' in project_details:
                        dct['h_project_building_area'] = project_details['project_address_area']
                    if 'project_unit' in project_details:
                        dct['h_project_unit_no_building_no_flat_number'] = project_details['project_unit']
                    if 'project_address_street' in project_details:
                        dct['h_project_building_street'] = project_details['project_address_street']
                    if 'project_address_city' in project_details:
                        dct['h_project_building_city'] = project_details['project_address_city']
                    if 'project_address_state' in project_details:
                        dct['h_project_building_state'] = project_details['project_address_state']
                    if 'housing_authority' in project_details:
                        dct['h_project_building_housing_authority'] = project_details['housing_authority']
                if "property_details" in kw:
                    property_details = kw["property_details"]       
                    if 'property_tower' in property_details:
                        dct['h_project_tower'] = property_details['property_tower']
                    if 'property_building' in property_details:
                        dct['h_project_building'] = property_details['property_building']
                    if 'property_address_city' in property_details:
                        dct['h_project_city'] = property_details['property_address_city']
                    if 'property_address_state' in property_details:
                        dct['h_project_state'] = property_details['property_address_state']
                    if 'property_address_area' in property_details:
                        dct['h_project_area_of_the_property'] = property_details['property_address_area']
                    if 'property_documented_purchase_cost' in property_details:
                        dct['h_project_documented_purchse_cost'] = property_details['property_documented_purchase_cost']
                    if 'property_estimated_market_value' in property_details:
                        dct['h_project_extimated_market_value'] = property_details['property_estimated_market_value']
                    if 'property_address_pincode' in property_details:
                        dct['h_property_pin_code'] = property_details['property_address_pincode']
                    if 'h_property_housing_authority' in property_details:
                        dct['h_property_housing_authority'] = property_details['h_property_housing_authority']

                if 'lead_id' in kw:
                    lead_id = str(kw['lead_id'])
                    dct['lead_id'] = kw['lead_id']
                if "lead_loan_amount" in kw:
                    dct['expected_revenue'] = kw['lead_loan_amount']
                if "lead_business_constitution" in kw:
                    dct['constitution'] = kw['lead_business_constitution']    
                if "lead_profession_type" in kw:
                    dct['profession'] = kw['lead_profession_type']
                if "lead_purpose" in kw:
                    dct['purpose_of_loan'] = kw['lead_purpose']
                if "lead_gender" in kw:
                    dct['p_gender'] = kw['lead_gender'].lower()    
                last = ""
                first = ""
                coapplicant_first = ""
                coapplicant_last = ""
                if "lead_firstname" in kw:
                    first = kw['lead_firstname']
                if "lead_lastname" in kw:
                    last = kw['lead_lastname']

                if "lead_firstname" in kw:
                    customer_name   = first + last
                    dct['name'] = customer_name
                if 'lead_email' in kw:
                    customer_email   = kw['lead_email']
                    dct['email_from'] = kw['lead_email']
                if 'lead_phone' in kw:
                    customer_phone   = kw['lead_phone']
                    dct['phone1'] = kw['lead_phone']    

                 

                if "p_coapplicant_name_first" in kw:
                    coapplicant_first = kw['p_coapplicant_name_first']
                if "p_coapplicant_name_second" in kw:
                    coapplicant_last = kw['p_coapplicant_name_second']

                if 'p_coapplicant_name_first' in kw:
                    coapplicant_name = coapplicant_first + coapplicant_last
                    dct['p_co_applicant_name'] = coapplicant_name       


                if "p_address_pincode" in kw:
                    dct['p_address_pincode'] = kw['p_address_pincode']
                if "address_pincode" in kw:
                    dct['p_coapplicant_pincode'] = kw['address_pincode']

                if "lap_lease_rental_discount" in kw:
                    dct['lap_lease_rental_discount'] = kw['lap_lease_rental_discount']  
                if "resident_indian_non_resident" in kw:
                    dct['resident_indian_non_resident'] = kw['resident_indian_non_resident']       
                        

                if 'banking_upload_passbook' in kw:
                    if 'base64,' in kw['banking_upload_passbook']:
                        if "pdf" in kw['banking_upload_passbook'].split('base64,')[0]:
                            dct['banking_upload_passbook_pdf'] = kw['banking_upload_passbook'].split('base64,')[1].replace(" ", "+")
                        else:
                            dct['banking_upload_passbook']   = kw['banking_upload_passbook'].split('base64,')[1].replace(" ", "+")
                if 'choose_finacial_instution' in kw:
                    dct['choose_finacial_instution'] = kw['choose_finacial_instution']
                if 'physical_journey' in kw:
                    dct['physical_journey'] = kw['physical_journey']
                if 'lead_aadhaar_number' in kw:
                    dct['b_kyc_document_type'] = kw['lead_aadhaar_number']
                if 'lead_address_document_1' in kw:
                    if 'base64,' in kw['lead_address_document_1']:
                        if "pdf" in kw['lead_address_document_1'].split('base64,')[0]:
                            dct['b_kyc_adhar_front_photo_pdf'] = kw['lead_address_document_1'].split('base64,')[1].replace(" ", "+")
                        else:
                            dct['b_kyc_adhar_front_photo'] = kw['lead_address_document_1'].split('base64,')[1].replace(" ", "+")
                if 'lead_address_document_2' in kw:
                    if 'base64,' in kw['lead_address_document_2']:
                        if "pdf" in kw['lead_address_document_2'].split('base64,')[0]:
                            dct['b_kyc_adhar_back_photo_pdf'] = kw['lead_address_document_2'].split('base64,')[1].replace(" ", "+")
                        else:
                            dct['b_kyc_adhar_back_photo'] = kw['lead_address_document_2'].split('base64,')[1].replace(" ", "+")
                if 'lead_pan_card_proof' in kw:
                    if 'base64,' in kw['lead_pan_card_proof']:
                        if "pdf" in kw['lead_pan_card_proof'].split('base64,')[0]:
                            dct['b_kyc_pan_card_front_pdf'] = kw['lead_pan_card_proof'].split('base64,')[1].replace(" ", "+")
                        else:
                            dct['b_kyc_pan_card_front'] = kw['lead_pan_card_proof'].split('base64,')[1].replace(" ", "+")
                if 'lead_pan_number' in kw:
                    dct['b_kyc_pan_card_number'] = kw['lead_pan_number']
                if 'lead_date_of_birth' in kw:
                    dct['b_kyc_bate_of_birth'] = kw['lead_date_of_birth']
                if "address_type" in kw and kw["address_type"] == "CURRENT":    
                    if 'address_residence_type' in kw:
                        dct['b_address_owned_rented'] = kw['address_residence_type']
                    if 'address_house' in kw:
                        dct['b_address_house'] = kw['address_house']
                    if 'address_pincode' in kw:
                        dct['b_address_pincode'] = kw['address_pincode']
                    if 'address_area' in kw:
                        dct['b_address_street'] = kw['address_area']    
                    if 'address_city' in kw:
                        dct['b_address_city'] = kw['address_city']
                    if 'address_state' in kw:
                        dct['b_address_state'] = kw['address_state']

                if "address_type" in kw and kw["address_type"] != "CURRENT": 
                    if 'b_address_bate_of_birth' in kw:
                        dct['b_address_bate_of_birth'] = kw['b_address_bate_of_birth']
                    if 'is_permanent_address' in kw:
                        dct['is_permanent_address'] = kw['is_permanent_address']

                    if 'address_document_1' in kw:
                        dct['is_permanent_address'] = False
                        if 'base64,' in kw['address_document_1']:
                            if "pdf" in kw['address_document_1'].split('base64,')[0]:
                                dct['b_address_permanent_address_proof_front_pdf'] = kw['address_document_1'].split('base64,')[1].replace(" ", "+")
                            else:
                                dct['b_address_permanent_address_proof_front'] = kw['address_document_1'].split('base64,')[1].replace(" ", "+")

                    if 'address_document_2' in kw:
                        if 'base64,' in kw['address_document_2']:
                            if "pdf" in kw['address_document_2'].split('base64,')[0]:
                                dct['b_address_permanent_address_proof_back_pdf'] = kw['address_document_2'].split('base64,')[1].replace(" ", "+")
                            else:
                                dct['b_address_permanent_address_proof_back'] = kw['address_document_2'].split('base64,')[1].replace(" ", "+")        
                    if 'address_house' in kw:
                        dct['is_permanent_address'] = False
                        dct['b_address_permanent_house'] = kw['address_house']
                    if 'address_area' in kw:
                        dct['b_address_permanent_village'] = kw['address_area']
                    if 'address_pincode' in kw:
                        dct['is_permanent_address'] = False
                        dct['b_address_permanent_pincode'] = kw['address_pincode']
                    if 'address_city' in kw:
                        dct['b_address_permanent_city'] = kw['address_city']
                    if 'address_state' in kw:
                        dct['is_permanent_address'] = False
                        dct['b_address_permanent_state'] = kw['address_state']

                if 'lead_company_identification_number' in kw:
                    dct['b_business_company_identification_number'] = kw['lead_company_identification_number']
                if 'lead_gstin' in kw:
                    dct['b_business_gstin'] = kw['lead_gstin']
                if 'lead_business_name' in kw:
                    dct['b_business_business__name'] = kw['lead_business_name']
                if 'lead_business_constitution' in kw:
                    dct['b_business_business_constitution'] = kw['lead_business_constitution']
                if 'lead_date_of_in_corporation' in kw:
                    dct['b_business_date_of_incorporation'] = kw['lead_date_of_in_corporation']
                if 'lead_business_vintage' in kw:
                    dct['b_business_business_vintage'] = kw['lead_business_vintage']
                if 'lead_business_pan_number' in kw:
                    dct['b_business_business_pan_card'] = kw['lead_business_pan_number']
                if 'lead_tin_number' in kw:
                    dct['b_business_tin_number'] = kw['lead_tin_number']
                if 'lead_tan_number' in kw:
                    dct['b_business_tan_number'] = kw['lead_tan_number']
                if 'lead_current_year_turnover' in kw:
                    dct['b_business_current_year_turnover'] = kw['lead_current_year_turnover']
                if 'lead_previous_year_turnover' in kw:
                    dct['b_business_previous_year_turnover'] = kw['lead_previous_year_turnover']
                if 'lead_current_year_profit_after_tax' in kw:
                    dct['b_business_current_year_profit_after_tax'] = kw['lead_current_year_profit_after_tax']
                if 'lead_previous_year_profit_after_tax' in kw:
                    dct['b_business_previous_year_profit_after_tax'] = kw['lead_previous_year_profit_after_tax']
                if 'business_industry_type' in kw:
                    dct['b_business_industry_type'] = kw['business_industry_type']    

                if 'business_industry_class' in kw:
                    dct['b_business_industry_classs']  = kw['business_industry_class']
                if 'b_business_industry_sub_classs' in kw:
                    dct['b_business_industry_sub_classs'] = kw['b_business_industry_sub_classs']
                
                if 'address' in kw:
                    rit = 0
                    for lead_address in kw['address']:
                        if rit == 0:
                            if 'address_residence_type' in lead_address:
                                dct['b_business_register_owned_rented'] = lead_address['address_residence_type']
                            if 'address_document_type' in lead_address:
                                dct['b_business_register_office_addess_proof'] = lead_address['address_document_type']
                            if 'address_document_1' in lead_address:
                                if 'base64,' in lead_address['address_document_1']:
                                    if "pdf" in lead_address['address_document_1'].split('base64,')[0]:
                                        dct['b_address_permanent_address_proof_front_pdf'] = lead_address['address_document_1'].split('base64,')[1].replace(" ", "+")
                                    else:
                                        dct['b_business_register_document_photo_front'] = lead_address['address_document_1'].split('base64,')[1].replace(" ", "+")
                            if 'address_document_2' in lead_address:
                                if 'base64,' in lead_address['address_document_2']:
                                    if "pdf" in lead_address['address_document_2'].split('base64,')[0]:
                                        dct['b_business_register_document_photo_back_pdf'] = lead_address['address_document_2'].split('base64,')[1].replace(" ", "+")
                                    else:
                                        dct['b_business_register_document_photo_back'] = lead_address['address_document_2'].split('base64,')[1].replace(" ", "+")
                            if 'address_pincode' in lead_address:
                                dct['b_business_register_pin_pincode'] = lead_address['address_pincode']
                            if 'address_house' in lead_address:
                                dct['b_business_register_building_number'] = lead_address['address_house']
                            if 'address_pincode' in lead_address:
                                dct['b_business_register_street'] = lead_address['address_pincode']
                            if 'address_area' in lead_address:
                                dct['b_business_register_city'] = lead_address['address_area'] 
                            if 'address_landmark' in lead_address:
                                dct['b_business_register_landmark'] = lead_address['address_landmark']       
                            if 'address_state' in lead_address:
                                dct['b_business_register_state'] = lead_address['address_state']    
                        if rit == 1:
                            if "address_area" in lead_address:
                                dct['b_business_register_current_office_street'] = lead_address['address_area']   
                            if 'address_city' in lead_address:
                                dct['b_business_register_current_office_city'] = lead_address['address_city'] 
                            if "address_state" in lead_address:
                                dct['b_business_register_current_office_state'] = lead_address['address_state']       
                            if 'b_business_register_current_office_addess_is_same' in lead_address:
                                dct['b_business_register_current_office_addess_is_same'] = lead_address['b_business_register_current_office_addess_is_same']
                            if 'address_document_type' in lead_address:
                                dct['b_business_register_current_office_address_proof'] = lead_address['address_document_type']
                            if 'address_document_1' in lead_address:
                                if 'base64,' in lead_address['address_document_1']:
                                    if "pdf" in lead_address['address_document_1'].split('base64,')[0]:
                                        dct['b_business_register_current_office_address_photo_front_pdf'] = lead_address['address_document_1'].split('base64,')[1].replace(" ", "+")
                                    else:
                                        dct['b_business_register_current_office_address_photo_front'] = lead_address['address_document_1'].split('base64,')[1].replace(" ", "+")
                            if 'address_document_2' in lead_address:
                                if 'base64,' in lead_address['address_document_2']:
                                    if "pdf" in lead_address['address_document_2'].split('base64,')[0]:
                                        dct['b_business_register_current_office_address_photo_back_pdf'] = lead_address['address_document_2'].split('base64,')[1].replace(" ", "+")
                                    else:
                                        dct['b_business_register_current_office_address_photo_back'] = lead_address['address_document_2'].split('base64,')[1].replace(" ", "+")
                            if 'address_house' in lead_address:
                                dct['b_business_register_current_office_building'] = lead_address['address_house']
                            
                            if "address_landmark" in lead_address:
                                dct['b_business_register_current_office_landmark'] = lead_address['address_landmark'] 
                            if "address_pincode" in lead_address:
                                dct['b_business_register_current_office_pincode'] = lead_address['address_pincode'] 
                        rit = rit + 1

                if "existing_obligation" in kw:
                    data_line = 0
                    for existing_obligation in kw['existing_obligation']:  
                        if data_line == 0:
                            if "lead_id" in existing_obligation:
                                dct['p_obligation_loan'] = True  
                            if 'loan_amount' in existing_obligation:
                                dct['p_obligation_loan_amount'] = existing_obligation['loan_amount'] 
                            if 'lead_bank_id' in existing_obligation:
                                dct['p_obligation_bank_name'] = existing_obligation['lead_bank_id']
                            if 'lead_type_of_loan' in existing_obligation:
                                dct['p_obligation_type_of_loan'] = existing_obligation['lead_type_of_loan']
                            if 'loan_account_number' in existing_obligation:
                                dct['p_obligation_account_number'] = existing_obligation['loan_account_number']
                            if 'emi' in existing_obligation:
                                dct['p_obligation_emi'] = existing_obligation['emi']
                            if 'lead_loan_opening_date' in existing_obligation:
                                dct['p_obligation_loan_opening_date'] = existing_obligation['lead_loan_opening_date']
                            if 'lead_tenure' in existing_obligation:
                                dct['p_obligation_tenure'] = existing_obligation['lead_tenure']
                            if 'lead_rate_of_interest' in existing_obligation:
                                dct['p_obligation_roi'] = existing_obligation['lead_rate_of_interest']
                            if 'lead_type_of_security' in existing_obligation:
                                dct['p_obligation_type_of_security'] = existing_obligation['lead_type_of_security']
                            if 'lead_current_outstanding_amount' in existing_obligation:
                                dct['p_obligation_current_out_standing_amount'] = existing_obligation['lead_current_outstanding_amount']
                        if data_line == 1:
                            if "lead_id" in existing_obligation:
                                dct['p2_obligation_loan'] = True
                            if "lead_bank_id" in existing_obligation:
                                dct['p2_obligation_bank_name'] = existing_obligation['lead_bank_id']
                            if "lead_type_of_loan" in existing_obligation:
                                dct['p2_obligation_type_of_loan'] = existing_obligation['lead_type_of_loan']
                            if "loan_amount" in existing_obligation:
                                dct['p2_obligation_loan_amount'] = existing_obligation['loan_amount']
                            if "loan_account_number" in existing_obligation:
                                dct['p2_obligation_account_number'] = existing_obligation['loan_account_number']
                            if "emi" in existing_obligation:
                                dct['p2_obligation_emi'] = existing_obligation['emi']
                            if "lead_loan_opening_date" in existing_obligation:
                                dct['p2_obligation_loan_opening_date'] = existing_obligation['lead_loan_opening_date']
                            if "lead_tenure" in existing_obligation:
                                dct['p2_obligation_tenure'] = existing_obligation['lead_tenure']
                            if "lead_rate_of_interest" in existing_obligation:
                                dct['p2_obligation_roi'] = existing_obligation['lead_rate_of_interest']
                            if "lead_type_of_security" in existing_obligation:
                                dct['p2_obligation_type_of_security'] = existing_obligation['lead_type_of_security']
                            if "lead_current_outstanding_amount" in existing_obligation:
                                dct['p2_obligation_current_out_standing_amount'] = existing_obligation['lead_current_outstanding_amount']
                            if "p3_obligation_loan" in existing_obligation:
                                dct['p3_obligation_loan'] = existing_obligation['p3_obligation_loan']
                            if "p3_obligation_bank_name" in existing_obligation:
                                dct['p3_obligation_bank_name'] = existing_obligation['p3_obligation_bank_name']
                            if "p3_obligation_loan_amount" in existing_obligation:
                                dct['p3_obligation_loan_amount'] = existing_obligation['p3_obligation_loan_amount']
                            if "p3_obligation_type_of_loan" in existing_obligation:
                                dct['p3_obligation_type_of_loan'] = existing_obligation['p3_obligation_type_of_loan']
                            if "p3_obligation_account_number" in existing_obligation:
                                dct['p3_obligation_account_number'] = existing_obligation['p3_obligation_account_number']
                            if "p3_obligation_emi" in existing_obligation:
                                dct['p3_obligation_emi'] = existing_obligation['p3_obligation_emi']
                            if "p3_obligation_loan_opening_date" in existing_obligation:
                                dct['p3_obligation_loan_opening_date'] = existing_obligation['p3_obligation_loan_opening_date']
                            if "p3_obligation_tenure" in existing_obligation:
                                dct['p3_obligation_tenure'] = existing_obligation['p3_obligation_tenure']
                            if "p3_obligation_roi" in existing_obligation:
                                dct['p3_obligation_roi'] = existing_obligation['p3_obligation_roi']
                            if "p3_obligation_type_of_security" in existing_obligation:
                                dct['p3_obligation_type_of_security'] = existing_obligation['p3_obligation_type_of_security']
                            if "p3_obligation_current_out_standing_amount" in existing_obligation:
                                dct['p3_obligation_current_out_standing_amount'] = existing_obligation['p3_obligation_current_out_standing_amount']
                            if "p3_obligation_credit_card" in existing_obligation:
                                dct['p3_obligation_credit_card'] = existing_obligation['p3_obligation_credit_card']
                            if "p3_obligation_current_credit_out_standing_amount" in existing_obligation:
                                dct['p3_obligation_current_credit_out_standing_amount'] = existing_obligation['p3_obligation_current_credit_out_standing_amount']
                            if "p3_obligation_credit_bank_name" in existing_obligation:
                                dct['p3_obligation_credit_bank_name'] = existing_obligation['p3_obligation_credit_bank_name']
                            if "p3_obligation_credit_limit" in existing_obligation:
                                dct['p3_obligation_credit_limit'] = existing_obligation['p3_obligation_credit_limit']
                        data_line = data_line + 1

                if "bank_details" in kw:
                    bank_loop = 0
                    for bank_details  in kw['bank_details']:
                        if bank_loop == 0:
                            if "bank_id" in bank_details:
                                dct['is_bank_1'] = True
                            if 'bank_id' in bank_details:
                                dct['is_bank_1'] = True
                                dct['p_bank_select_bank'] = bank_details['bank_id']
                            if 'lead_bank_account_type' in bank_details:
                                dct['is_bank_1'] = True
                                dct['p_bank_details_account_type'] = bank_details['lead_bank_account_type']
                            if 'lead_bank_statement_file' in bank_details:
                                if "base64," in bank_details['lead_bank_statement_file']:
                                    if "pdf" in bank_details['lead_bank_statement_file'].split('base64,')[0]:
                                        dct['p_bank_details_upload_statement_past_month_pdf'] = bank_details['lead_bank_statement_file'].split('base64,')[1].replace(" ", "+")
                                    else:
                                        dct['p_bank_details_upload_statement_past_month'] = bank_details['lead_bank_statement_file'].split('base64,')[1].replace(" ", "+")
                            if 'p_bank_is_bank_statement_is_password_protected' in bank_details:
                                dct['is_bank_1'] = True
                                dct['p_bank_is_bank_statement_is_password_protected'] = bank_details['p_bank_is_bank_statement_is_password_protected']
                            if 'lead_bank_statement_file_password' in bank_details:
                                dct['p_bank_password'] = bank_details['lead_bank_statement_file_password']

                        
                        if bank_loop == 1:
                            if "bank_id" in bank_details:
                                dct['is_bank_2'] = True
                                dct['p2_bank_select_bank'] = bank_details['bank_id']
                            if "lead_bank_account_type" in bank_details:
                                dct['is_bank_2'] = True
                                dct['p2_bank_details_account_type'] = bank_details['lead_bank_account_type']
                            if "lead_bank_statement_file" in bank_details:
                                if "base64," in bank_details['lead_bank_statement_file']:
                                    dct['is_bank_2'] = True
                                    if "pdf" in bank_details['lead_bank_statement_file'].split('base64,')[0]:
                                        dct['p2_bank_details_upload_statement_past_month_pdf'] = bank_details['lead_bank_statement_file'].split('base64,')[1].replace(" ", "+")
                                    else:
                                        dct['p2_bank_details_upload_statement_past_month'] = bank_details['p2_bank_is_bank_statement_is_password_protected'].split('base64,')[1].replace(" ", "+")
                            if "p2_bank_is_bank_statement_is_password_protected" in bank_details:
                                if "base64," in bank_details['lead_bank_statement_file']:
                                    dct['is_bank_2'] = True
                                    if "pdf" in bank_details['p2_bank_is_bank_statement_is_password_protected'].split('base64,')[0]:
                                        dct['p2_bank_is_bank_statement_is_password_protected_pdf'] = bank_details['p2_bank_is_bank_statement_is_password_protected'].split('base64,')[1].replace(" ", "+")
                                    else:
                                        dct['p2_bank_is_bank_statement_is_password_protected'] = bank_details['p2_bank_is_bank_statement_is_password_protected'].split('base64,')[1].replace(" ", "+")
                            if "lead_bank_statement_file_password" in bank_details:
                                dct['p2_bank_password'] = bank_details['lead_bank_statement_file_password']
                            if "bank_id" in bank_details:
                                dct['is_bank_2'] = True

                        if bank_loop ==2:
                            if "bank_id" in bank_details:
                                dct['is_bank_3'] = True     
                            if "p3_bank_select_bank" in bank_details:
                                dct['is_bank_3'] = True
                                dct['p3_bank_select_bank'] = bank_details['p3_bank_select_bank']
                            if "lead_bank_account_type" in bank_details:
                                dct['p3_bank_details_account_type'] = bank_details['lead_bank_account_type']
                            if "lead_bank_statement_file" in bank_details:
                                if "base64," in bank_details['lead_bank_statement_file']:
                                    dct['is_bank_3'] = True
                                    if "pdf" in bank_details['lead_bank_statement_file'].split('base64,')[0]:
                                        dct['p3_bank_details_upload_statement_past_month_pdf'] = bank_details['lead_bank_statement_file'].split('base64,')[1].replace(" ", "+")
                                    else:
                                        dct['p3_bank_details_upload_statement_past_month'] = bank_details['lead_bank_statement_file'].split('base64,')[1].replace(" ", "+")
                            if "p3_bank_is_bank_statement_is_password_protected" in bank_details:
                                dct['p3_bank_is_bank_statement_is_password_protected'] = bank_details['p3_bank_is_bank_statement_is_password_protected']
                            if "lead_bank_statement_file_password" in bank_details:
                                dct['p3_bank_password'] = bank_details['lead_bank_statement_file_password']  
                        bank_loop = bank_loop + 1          
                if "applicant" in kw:
                    applicant = kw['applicant']
                    if "address" in kw['applicant']:
                        print("kw['applicant']@@@@@@@@@@@@@@@@@@@@@0",kw['applicant']["address"])
                        first_loop = 0
                        for app in kw['applicant']["address"]:
                            if app['address_type'] == "CURRENT":
                                if 'address_residence_type' in app:
                                    dct['p_address_residence_owner_rent'] = app['address_residence_type']
                                if 'p_address_number_of_year_in_current_residence' in app:
                                    dct['p_address_number_of_year_in_current_residence'] = app['p_address_number_of_year_in_current_residence']
                                if 'address_house' in app:
                                    dct['p_address_flat_house'] = app['address_house']
                                if 'address_area' in app:
                                    dct['p_address_street_lane'] = app['address_area']
                                if 'address_city' in app:
                                    dct['p_address_city'] = app['address_city']
                                if 'address_state' in app:
                                    dct['p_address_state'] = app['address_state']  
                                if "address_pincode" in app:
                                    dct['p_address_pincode'] = app['address_pincode'] 
                            if app['address_type'] == "PERMANENT":
                                if 'address_document_type' in app:
                                    dct['p_permant_address_proof'] = app['address_document_type']
                                if 'address_document' in app:
                                    if "base64," in app['address_document']:
                                        if "pdf" in app['address_document'].split('base64,')[0]:
                                            dct['p_permant_address_proof_photo_pdf'] = app['address_document'].split('base64,')[1].replace(" ", "+")
                                        else:
                                            dct['p_permant_address_proof_photo'] = app['address_document'].split('base64,')[1].replace(" ", "+")
                                if 'address_area' in app:
                                    dct['p_permant_street_lane'] = app['address_area']
                                if 'address_house' in app:
                                    dct['p_permant_flat_house'] = app['address_house']
                                if 'address_state' in app:
                                    dct['p_permant_state'] = app['address_state']
                                if 'address_city' in app:
                                    dct['p_permant_city'] = app['address_city']  
                                if 'address_pincode' in app:
                                    dct['p_permant_pin_code'] = app['address_pincode']     
                                        

                    if "applicant_gender" in applicant:
                        dct['p_gender'] = applicant['applicant_gender'].lower()    
                    last = ""
                    first = ""
                    if "applicant_first_name" in applicant:
                        first = applicant['applicant_first_name']
                    if "applicant_last_name" in applicant:
                        last = applicant['applicant_last_name']

                    if "applicant_first_name" in applicant:
                        customer_name   = first + " " + last
                        dct['name'] = customer_name
                    if 'applicant_email_id' in applicant:
                        customer_email   = applicant['applicant_email_id']
                        dct['email_from'] = applicant['applicant_email_id']
                        dct['p_personal_email_id'] = applicant['applicant_email_id']
                    if 'applicant_phone' in applicant:
                        customer_phone   = applicant['applicant_phone']
                        dct['phone1'] = applicant['applicant_phone']  
                    if 'applicant_father_husband_name' in applicant:
                        dct['p_father_husband_name'] = applicant['applicant_father_husband_name']
                    if 'applicant_educational_qualification' in applicant:
                        dct['p_educational_qualification'] = applicant['applicant_educational_qualification']
                    if 'applicant_marital_status' in applicant:
                        dct['p_marital_status'] = applicant['applicant_marital_status']
                    if 'applicant_current_address_document_type' in applicant:
                        dct['p_kyc_type_of_document'] = applicant['applicant_current_address_document_type']
                    if 'applicant_current_address_document_front' in applicant:
                        if 'base64,' in applicant['applicant_current_address_document_front']:
                            if "pdf" in applicant['applicant_current_address_document_front'].split('base64,')[0]:
                                dct['p_kyc_current_address_residence_proof_front_pdf'] = applicant['applicant_current_address_document_front'].split('base64,')[1].replace(" ", "+")
                            else:
                                dct['p_kyc_current_address_residence_proof_front'] = applicant['applicant_current_address_document_front'].split('base64,')[1].replace(" ", "+")
                    if 'applicant_current_address_document_back' in applicant:
                        if 'base64,' in applicant['applicant_current_address_document_back']:
                            dct['p_kyc_current_address_residence_proof_back'] = applicant['applicant_current_address_document_back'].split('base64,')[1].replace(" ", "+")
                    if 'applicant_pan_card_document' in applicant:
                        if 'base64,' in applicant['applicant_pan_card_document']:
                            if "pdf" in applicant['applicant_pan_card_document'].split('base64,')[0]:
                                dct['p_kyc_current_pan_card_photo_pdf'] = applicant['applicant_pan_card_document'].split('base64,')[1].replace(" ", "+")
                            else:
                                dct['p_kyc_current_pan_card_photo'] = applicant['applicant_pan_card_document'].split('base64,')[1].replace(" ", "+")

                    if 'applicant_photo' in applicant:
                        if 'base64,' in applicant['applicant_photo']:
                            if "pdf" in applicant['applicant_photo'].split('base64,')[0]:
                                dct['p_applicant_photo_pdf'] = applicant['applicant_photo'].split('base64,')[1].replace(" ", "+")
                            else:
                                dct['p_applicant_photo'] = applicant['applicant_photo'].split('base64,')[1].replace(" ", "+")             
                    if 'applicant_pan_number' in applicant:
                        dct['p_kyc_current_pan_number'] = applicant['applicant_pan_number']
                    if 'applicant_date_of_birth' in applicant:
                        dct['p_kyc_current_date_of_birth'] = applicant['applicant_date_of_birth']    
                    
                    if 'applicant_current_organization_name' in applicant:
                        dct['p_business_name_of_current_orginization'] = applicant['applicant_current_organization_name']
                    if 'applicant_current_organization_type' in applicant:
                        dct['profession_categories_salaried'] = True
                        dct['p_busness_orginization_type'] = applicant['applicant_current_organization_type']
                    if 'applicant_industry_type' in applicant:
                        dct['p_busness_industry_type'] = applicant['applicant_industry_type']
                    if 'applicant_employment_type' in applicant:
                        dct['profession_categories_salaried'] = True
                        dct['p_business_employment_type'] = applicant['applicant_employment_type']
                    if 'applicant_employment_identification_number' in applicant:
                        dct['p_business_employeement_id_number'] = applicant['applicant_employment_identification_number']
                    if 'p_business_officail_email_id' in applicant:
                        dct['profession_categories_salaried'] = True
                        dct['p_business_officail_email_id'] = applicant['p_business_officail_email_id']
                    if 'applicant_monthly_net_salary' in applicant:
                        dct['profession_categories_salaried'] = True
                        dct['p_business_net_monthly_salary'] = applicant['applicant_monthly_net_salary']
                    if 'applicant_monthly_gross_salary' in applicant:
                        dct['p_business_gross_monthly_salary'] = applicant['applicant_monthly_gross_salary']
                    if 'applicant_designation' in applicant:
                        dct['profession_categories_salaried'] = True
                        dct['p_business_designation'] = applicant['applicant_designation']
                    if 'applicant_department' in applicant:
                        dct['p_business_department'] = applicant['applicant_department']
                    p_business_year_in_current_job_year = 0
                    p_business_year_in_current_job_month = 0
                    if 'applicant_total_exp_current_role' in applicant:
                        p_business_year_in_current_job_year = float(applicant['applicant_total_exp_current_role'])
                    if 'p_business_year_in_current_job_month' in applicant:
                        p_business_year_in_current_job_month = float(applicant['p_business_year_in_current_job_month']) / 12

                    if 'applicant_total_exp_current_role' in applicant:
                        dct['p_business_year_in_current_job'] = p_business_year_in_current_job_year  + p_business_year_in_current_job_month
                    
                    p_business_total_work_experiance_year = 0
                    p_business_total_work_experiance_month = 0

                    if 'applicant_total_exp' in applicant:
                        p_business_total_work_experiance_year = float(applicant['applicant_total_exp'])
                    if 'p_business_total_work_experiance_month' in applicant:
                        p_business_total_work_experiance_month = float(applicant['p_business_total_work_experiance_month']) / 12

                    if 'applicant_total_exp' in applicant:
                        dct['p_business_total_work_experiance'] = p_business_total_work_experiance_year + p_business_total_work_experiance_month    
                    
                    if "applicant_current_organization_name" in applicant:
                        dct['p_business_business_name'] = applicant['applicant_current_organization_name']
                    if "applicant_profession" in applicant:
                        dct['p_business_profession'] = applicant['applicant_profession']
                    if "applicant_highest_professional_qualification" in applicant:
                        dct["applicant_highest_professional_qualification"] = applicant["applicant_highest_professional_qualification"]    
                    if "applicant_registration_number" in applicant:
                        dct['profession_categories_sep'] = True
                        dct['p_business_registration_number'] = applicant['applicant_registration_number']
                    if "applicant_gst_number" in applicant:
                        dct['profession_categories_sep'] = True
                        dct['p_business_gstin'] = applicant['applicant_gst_number']
                    if "applicant_total_exp_current_role" in applicant:
                        dct['p_business_years_in_current_profession'] = applicant['applicant_total_exp_current_role']
                    if "applicant_professional_receipts" in applicant:
                        dct['profession_categories_sep'] = True
                        dct['p_business_gross_professional_receipts_as_per_ITR'] = applicant['applicant_professional_receipts']
                    if "p2_business_gross_professional_receipts_as_per_ITR" in applicant:
                        dct['p2_business_gross_professional_receipts_as_per_ITR'] = applicant['p2_business_gross_professional_receipts_as_per_ITR']
                    if "p3_business_gross_professional_receipts_as_per_ITR" in applicant:
                        dct['p3_business_gross_professional_receipts_as_per_ITR'] = applicant['p3_business_gross_professional_receipts_as_per_ITR']
                    if "applicant_work_email_address" in applicant:
                        dct['p_business_email_id'] = applicant['applicant_work_email_address']
                    if "applicant_work_phone" in applicant:
                        dct['p_business_phone_number'] = applicant['applicant_work_phone']
                    if "profession_categories_salaried" in kw:
                        dct['profession_categories_salaried'] = True
                    if "profession_categories_senp" in kw:
                        dct['profession_categories_senp'] = kw['profession_categories_senp']
                    if "profession_categories_sep" in kw:
                        dct['profession_categories_sep'] = kw['profession_categories_sep']    

                    if 'applicant_role' in applicant:
                        dct['p_business_i_am_a'] = applicant['applicant_role']
                    if 'applicant_constitution' in applicant:
                        dct['p_business_business_constitution'] = applicant['applicant_constitution']
                    if 'applicant_monthly_renumeration' in applicant:
                        dct['p_business_monthly_renumeration'] = applicant['applicant_monthly_renumeration']
                    if 'applicant_share_holding_percentage' in applicant:
                        dct['profession_categories_senp'] = True
                        dct['p_business_share_holding'] = applicant['applicant_share_holding_percentage']
                    if 'applicant_annual_income' in applicant:
                        dct['profession_categories_senp'] = True
                        dct['p_business_annual_income'] = applicant['applicant_annual_income']
                    if 'applicant_profit_percentage' in applicant:
                        dct['profession_categories_senp'] = True
                        dct['p_business_share_in_profit'] = applicant['applicant_profit_percentage']    
                    # if "applicant_business_details" in applicant:
                    #     applicant_business_details  = applicant["applicant_business_details"]
                    if 'applicant_profit_percentage' in applicant:
                        dct['p_business_share_in_profit'] = applicant['applicant_profit_percentage']
                    if 'business_name' in applicant:
                        dct['p_business_business_name'] = applicant['business_name']
                    if 'business_industry_type' in applicant:
                        dct['p_business_industry_type'] = applicant['business_industry_type']    
                    if 'business_industry_subclass' in applicant:
                        dct['p_business_industry_sub_class'] = applicant['business_industry_subclass']
                    if 'business_current_year_profit_after_tax' in applicant:
                        dct['p_business_profit_after_tax'] = applicant['business_current_year_profit_after_tax']
                    if 'business_previous_year_profit_after_tax' in applicant:
                        dct['p_business_previous_profit_after_tax'] = applicant['business_previous_year_profit_after_tax']
                    if 'business_current_year_turnover' in applicant:
                        dct['p_business_current_year_turnover'] = applicant['business_current_year_turnover']
                    if 'business_previous_year_turnover' in applicant:
                        dct['p_business_previous_year_turnover'] = applicant['business_previous_year_turnover']
                    if 'business_tin_number' in applicant:
                        dct['p_business_Cin_number'] = applicant['business_tin_number']
                    if 'business_gst_number' in applicant:
                        dct['p_business_gst_number'] = applicant['business_gst_number']
                    if 'business_pan_number' in applicant:
                        dct['p_business_business_pan'] = applicant['business_pan_number']
                    if 'business_tin_number' in applicant:
                        dct['p_business_tin_number'] = applicant['business_tin_number']
                    if 'business_tan_number' in applicant:
                        dct['p_business_tan_number'] = applicant['business_tan_number']
                    if 'p_business_nio_of_partner_director' in applicant:
                        dct['p_business_nio_of_partner_director'] = applicant['p_business_nio_of_partner_director']
                    if 'business_incorporation_date' in applicant:
                        dct['p_business_date_of_incorportaion'] = applicant['business_incorporation_date']
                    if 'business_vintage' in applicant:
                        dct['p_business_business_vintage'] = applicant['business_vintage']
                    if 'business_email' in applicant:
                        dct['p_business_email_id'] = applicant['business_email']
                    if 'business_phone' in applicant:
                        dct['p_business_phn_number'] = applicant['business_phone']
                    if 'p_business_year_of_current_business' in applicant:
                        dct['p_business_year_of_current_business'] = applicant['p_business_year_of_current_business']
                    if 'business_pos_enabled' in applicant:
                        dct['p_business_do_you_have_pos'] = applicant['business_pos_enabled']
                    if 'business_pos_monthly_sales' in applicant:
                        dct['p_business_if_year_what_is_your_monthly_card_swipe'] = applicant['business_pos_monthly_sales']
                    if 'business_industry_type' in kw:
                        dct['business_industry_type'] = kw['business_industry_type']    

                    if 'business_industry_class' in kw:
                        dct['p_business_industry_sub_class']  = kw['business_industry_class']
                    # if 'industrySubClass' in kw:
                    #     dct['b_business_industry_sub_classs'] = kw['industrySubClass']
                        
                    
                    if "applicant_additional_income" in applicant:
                        data_applicant = 0
                        for applicant_additional_income in applicant['applicant_additional_income']:
                            if data_applicant == 0:
                                if 'income_amount' in applicant_additional_income:
                                    dct['p_business_additional_amount'] = applicant_additional_income['income_amount']
                                if 'income_source' in applicant_additional_income:
                                    dct['p_business_additional_source'] = applicant_additional_income['income_source']
                            if data_applicant == 1:
                                if 'income_amount' in applicant_additional_income:
                                    dct['p2_business_additional_amount'] = applicant_additional_income['income_amount']
                                if 'income_source' in applicant_additional_income:
                                    dct['p2_business_additional_source'] = applicant_additional_income['income_source']
                            data_applicant = data_applicant + 1    
                    if "applicant_business_addresses" in applicant:
                        vvfr = 0
                        for applicant_business_addresses in applicant['applicant_business_addresses']:
                            if "address_type" in applicant_business_addresses and applicant_business_addresses["address_type"] == "OFFICE":
                                if 'address_pincode' in applicant_business_addresses:
                                    dct['p_business_office_pin_code'] = applicant_business_addresses['address_pincode']
                                if 'address_house' in applicant_business_addresses:
                                    dct['p_business_office_building_numbr'] = applicant_business_addresses['address_house']
                                if 'address_area' in applicant_business_addresses:
                                    dct['p_business_office_street_lane'] = applicant_business_addresses['address_area']
                                if 'address_landmark' in applicant_business_addresses:
                                    dct['p_business_office_landmark'] = applicant_business_addresses['address_landmark']
                                if 'address_city' in applicant_business_addresses:
                                    dct['p_business_office_city'] = applicant_business_addresses['address_city']
                                if 'address_state' in applicant_business_addresses:
                                    dct['p_business_building_office_state'] = applicant_business_addresses['address_state']   
                            if "address_type" in applicant_business_addresses and applicant_business_addresses["address_type"] == "REGISTERED_OFFICE":
                                if "address_pincode" in applicant_business_addresses:
                                    dct['p_business_register_pin_pincode'] = applicant_business_addresses['address_pincode']
                                if "address_house" in applicant_business_addresses:
                                    dct['p_business_register_building_number'] = applicant_business_addresses['address_house']
                                if "address_area" in applicant_business_addresses:
                                    dct['p_business_register_street'] = applicant_business_addresses['address_area']
                                if "address_landmark" in applicant_business_addresses:
                                    dct['p_business_register_landmark'] = applicant_business_addresses['address_landmark']
                                if "address_city" in applicant_business_addresses:
                                    dct['p_business_register_city'] = applicant_business_addresses['address_city']
                                if "address_state" in applicant_business_addresses:
                                    dct['p_business_register_state'] = applicant_business_addresses['address_state']
                            if "address_type" in applicant_business_addresses and applicant_business_addresses["address_type"] == "CORPORATE_OFFICE":
                                if "address_pincode" in applicant_business_addresses:
                                    dct['p_business_corporate_register_pin_pincode'] = applicant_business_addresses['address_pincode']
                                if "address_house" in applicant_business_addresses:
                                    dct['p_business_corporate_register_building_number'] = applicant_business_addresses['address_house']
                                if "address_area" in applicant_business_addresses:
                                    dct['p_business_corporate_register_street'] = applicant_business_addresses['address_area']
                                if "address_landmark" in applicant_business_addresses:
                                    dct['p_business_corporate_register_landmark'] = applicant_business_addresses['address_landmark']
                                if "address_city" in applicant_business_addresses:
                                    dct['p_business_corporate_register_city'] = applicant_business_addresses['address_city']
                                if "address_state" in applicant_business_addresses:
                                    dct['p_business_corporate_register_state'] = applicant_business_addresses['address_state']            
                            vvfr = vvfr + 1
                    if 'loans' in applicant:
                        looping = 0
                        for loans in applicant['loans']:
                            if looping == 0:
                                if 'loan_amount' in loans:
                                    dct['p_obligation_loan_amount'] = loans['loan_amount'] 
                                    dct['p_obligation_loan'] = True
                                if 'loan_bank_id' in loans:
                                    dct['p_obligation_loan'] = True
                                    dct['p_obligation_bank_name'] = loans['loan_bank_id']
                                if 'loan_type' in loans:
                                    dct['p_obligation_type_of_loan'] = loans['loan_type']
                                if 'loan_account_number' in loans:
                                    dct['p_obligation_account_number'] = loans['loan_account_number']
                                if 'loan_emi' in loans:
                                    dct['p_obligation_loan'] = True
                                    dct['p_obligation_emi'] = loans['loan_emi']
                                if 'loan_opening_date' in loans:
                                    dct['p_obligation_loan_opening_date'] = loans['loan_opening_date']
                                if 'loan_tenure_months' in loans:
                                    dct['p_obligation_tenure'] = loans['loan_tenure_months']
                                if 'loan_rate_of_interest' in loans:
                                    dct['p_obligation_loan'] = True
                                    dct['p_obligation_roi'] = loans['loan_rate_of_interest']
                                if 'loan_type_of_security' in loans:
                                    dct['p_obligation_type_of_security'] = loans['loan_type_of_security']
                                if 'loan_current_outstanding_amount' in loans:
                                    dct['p_obligation_loan'] = True
                                    dct['p_obligation_current_out_standing_amount'] = loans['loan_current_outstanding_amount'] 
                            
                            if looping == 1:
                                if "loan_bank_id" in loans:
                                    dct['p2_obligation_bank_name'] = loans['loan_bank_id']
                                if "loan_type" in loans:
                                    dct['p2_obligation_type_of_loan'] = loans['loan_type']
                                if "loan_amount" in loans:
                                    dct['p2_obligation_loan'] = True
                                    dct['p2_obligation_loan_amount'] = loans['loan_amount']
                                if "loan_account_number" in loans:
                                    dct['p2_obligation_loan'] = True
                                    dct['p2_obligation_account_number'] = loans['loan_account_number']
                                if "loan_emi" in loans:
                                    dct['p2_obligation_emi'] = loans['loan_emi']
                                if "loan_opening_date" in loans:
                                    dct['p2_obligation_loan'] = True
                                    dct['p2_obligation_loan_opening_date'] = loans['loan_opening_date']
                                if "loan_tenure_months" in loans:
                                    dct['p2_obligation_tenure'] = loans['loan_tenure_months']
                                if "loan_rate_of_interest" in loans:
                                    dct['p2_obligation_loan'] = True
                                    dct['p2_obligation_roi'] = loans['loan_rate_of_interest']
                                if "loan_type_of_security" in loans:
                                    dct['p2_obligation_type_of_security'] = loans['loan_type_of_security']
                                if "loan_current_outstanding_amount" in loans:
                                    dct['p2_obligation_current_out_standing_amount'] = loans['loan_current_outstanding_amount']
                                
                            if looping == 2:
                                if "loan_bank_id" in loans:
                                    dct['p3_obligation_loan'] = True
                                    dct['p3_obligation_bank_name'] = loans['loan_bank_id']
                                if "loan_amount" in loans:
                                    dct['p3_obligation_loan_amount'] = loans['loan_amount']
                                if "loan_type" in loans:
                                    dct['p3_obligation_loan'] =  True
                                    dct['p3_obligation_type_of_loan'] = loans['loan_type']
                                if "loan_account_number" in loans:
                                    dct['p3_obligation_loan'] = True
                                    dct['p3_obligation_account_number'] = loans['loan_account_number']
                                if "loan_emi" in loans:
                                    dct['p3_obligation_emi'] = loans['loan_emi']
                                if "loan_opening_date" in loans:
                                    dct['p3_obligation_loan'] = True
                                    dct['p3_obligation_loan_opening_date'] = loans['loan_opening_date']
                                if "loan_tenure_months" in loans:
                                    dct['p3_obligation_tenure'] = loans['loan_tenure_months']
                                if "loan_rate_of_interest" in loans:
                                    dct['p3_obligation_roi'] = loans['loan_rate_of_interest']
                                if "loan_type_of_security" in loans:
                                    dct['p3_obligation_loan'] = True
                                    dct['p3_obligation_type_of_security'] = loans['loan_type_of_security']
                                if "loan_current_outstanding_amount" in loans:
                                    dct['p3_obligation_current_out_standing_amount'] = loans['loan_current_outstanding_amount']
                            looping = looping + 1    

                                    
                    if "credit_cards" in applicant:
                        for credit_cards in applicant["credit_cards"]: 
                            if "cc_current_outstanding_amount" in credit_cards:
                                dct['p3_obligation_credit_card'] = True
                                dct['p3_obligation_current_credit_out_standing_amount'] = credit_cards['cc_current_outstanding_amount']
                            if "cc_bank_id" in credit_cards:
                                dct['p3_obligation_credit_card'] = True
                                dct['p3_obligation_credit_bank_name'] = credit_cards['cc_bank_id']
                            if "cc_credit_limit" in credit_cards:
                                dct['p3_obligation_credit_limit'] = credit_cards['cc_credit_limit']
                    if "accounts" in applicant:
                        banl_test_loop = 0
                        for bank_details in applicant["accounts"]: 
                            if banl_test_loop == 0:
                                if 'account_bank_id' in bank_details:
                                    dct['is_bank_1'] = True
                                    dct['p_bank_select_bank'] = bank_details['account_bank_id']
                                if 'account_type' in bank_details:
                                    dct['is_bank_1'] = True
                                    dct['p_bank_details_account_type'] = bank_details['account_type']
                                if 'account_statement_document' in bank_details:
                                    dct['is_bank_1'] = True
                                    if 'base64,' in bank_details['account_statement_document']:
                                        if "pdf" in bank_details['account_statement_document'].split('base64,')[0]:
                                            dct['p_bank_details_upload_statement_past_month_pdf'] = bank_details['account_statement_document'].split('base64,')[1].replace(" ", "+")
                                        else:
                                            dct['p_bank_details_upload_statement_past_month'] = bank_details['account_statement_document'].split('base64,')[1].replace(" ", "+")
                                if 'account_statement_document_password_protected' in bank_details:
                                    dct['is_bank_1'] = True
                                    dct['p_bank_is_bank_statement_is_password_protected'] = bank_details['account_statement_document_password_protected']
                                if 'account_statement_document_password' in bank_details:
                                    dct['is_bank_1'] = True
                                    dct['p_bank_password'] = bank_details['account_statement_document_password']   
                            if banl_test_loop == 1:
                                # if "is_bank_3" in bank_details:
                                #     dct['is_bank_3'] = bank_details['is_bank_3']    
                                if "account_bank_id" in bank_details:
                                    dct['is_bank_2'] = True
                                    dct['p2_bank_select_bank'] = bank_details['account_bank_id']
                                if "account_type" in bank_details:
                                    dct['is_bank_2'] = True
                                    dct['p2_bank_details_account_type'] = bank_details['account_type']
                                if 'account_statement_document' in bank_details:
                                    dct['is_bank_2'] = True
                                    if 'base64,' in bank_details['account_statement_document']:
                                        if "pdf" in bank_details['account_statement_document'].split('base64,')[0]:
                                            dct['p2_bank_details_upload_statement_past_month_pdf'] = bank_details['account_statement_document'].split('base64,')[1].replace(" ", "+")
                                        else:
                                            dct['p2_bank_details_upload_statement_past_month'] = bank_details['account_statement_document'].split('base64,')[1].replace(" ", "+")                                            
                                if "account_statement_document_password_protected" in bank_details:
                                    dct['is_bank_2'] = True
                                    dct['p2_bank_is_bank_statement_is_password_protected'] = bank_details['account_statement_document_password_protected']
                                if "account_statement_document_password" in bank_details:
                                    dct['is_bank_2'] = True
                                    dct['p2_bank_password'] = bank_details['account_statement_document_password']
                            if banl_test_loop == 2:
                                if "account_bank_id" in bank_details:
                                    dct['p3_bank_select_bank'] = bank_details['account_bank_id']
                                if "account_type" in bank_details:
                                    dct['p3_bank_details_account_type'] = bank_details['account_type']
                                if 'account_statement_document' in bank_details:
                                    dct['is_bank_3'] = True
                                    if 'base64,' in bank_details['account_statement_document']:
                                        if "pdf" in bank_details['account_statement_document'].split('base64,')[0]:
                                            dct['p3_bank_details_upload_statement_past_month_pdf'] = bank_details['account_statement_document'].split('base64,')[1].replace(" ", "+")
                                        else:
                                            dct['p3_bank_details_upload_statement_past_month'] = bank_details['account_statement_document'].split('base64,')[1].replace(" ", "+")     
                                if "account_statement_document_password_protected" in bank_details:
                                    dct['p3_bank_is_bank_statement_is_password_protected'] = bank_details['account_statement_document_password_protected']
                                if "account_statement_document_password" in bank_details:
                                    dct['p3_bank_password'] = bank_details['account_statement_document_password']
                            banl_test_loop = banl_test_loop + 1

                if "co_applicants" in kw:
                    co_applicant_1 = 0
                    for co_applicant in kw['co_applicants']:
                        if "loans" in co_applicant and co_applicant_1 == 0:
                            loan_loop = 0
                            for loan in co_applicant['loans']:
                                if loan_loop == 0:
                                    print("loan@@@@@@@@@@@@@@@@@@@@222222222222222222222",loan)
                                    if 'loan_bank_id' in loan:
                                        dct['p_coapplicant_obligation_data_is'] = True
                                        dct['p_coapplicant_obligation_bank_name'] = loan['loan_bank_id']
                                    if 'loan_type' in loan:
                                        dct['p_coapplicant_obligation_type_of_loan'] = loan['loan_type']
                                    if 'loan_account_number' in loan:
                                        dct['p_coapplicant_obligation_data_is'] = True
                                        dct['p_coapplicant_obligation_account_number'] = loan['loan_account_number']
                                    if 'loan_emi' in loan:
                                        dct['p_coapplicant_obligation_emi'] = loan['loan_emi']
                                    if 'loan_opening_date' in loan:
                                        dct['p_coapplicant_obligation_data_is'] = True
                                        dct['p_coapplicant_obligation_loan_opening_date'] = loan['loan_opening_date']
                                    if 'loan_tenure_months' in loan:
                                        dct['p_coapplicant_obligation_tenure'] = loan['loan_tenure_months']
                                    if 'loan_rate_of_interest' in loan:
                                        dct['p_coapplicant_obligation_data_is'] = True
                                        dct['p_coapplicant_obligation_roi'] = loan['loan_rate_of_interest']
                                    if 'loan_type_of_security' in loan:
                                        dct['p_coapplicant_obligation_type_of_security'] = loan['loan_type_of_security']
                                    if 'loan_current_outstanding_amount' in loan:
                                        dct['p_coapplicant_obligation_data_is'] = True
                                        dct['p_coapplicant_obligation_current_out_standing_amount'] = loan['loan_current_outstanding_amount']
                                    if "loan_amount" in loan:
                                        dct['p_coapplicant_obligation_loan_amount'] = loan['loan_amount']     
                                        
                                if loan_loop == 1:
                                    print("loan@@@@@@@@@@@@@@@@@@@@1111111111111111111111111111",loan)
                                    if "pl2_coapplicant_obligation_data_is" in loan:
                                        dct['pl2_coapplicant_obligation_data_is'] = loan['pl2_coapplicant_obligation_data_is']
                                    if "loan_bank_id" in loan:
                                        dct['pl2_coapplicant_obligation_data_is'] = True
                                        dct['pl2_coapplicant_obligation_bank_name'] = loan['loan_bank_id']
                                    if "loan_type" in loan:
                                        dct['pl2_coapplicant_obligation_data_is'] = True
                                        dct['pl2_coapplicant_obligation_type_of_loan'] = loan['loan_type']
                                    if "loan_account_number" in loan:
                                        dct['pl2_coapplicant_obligation_data_is'] = True
                                        dct['pl2_coapplicant_obligation_account_number'] = loan['loan_account_number']
                                    if "loan_amount" in loan:
                                        dct['pl2_coapplicant_obligation_loan_amount'] = loan['loan_amount']    
                                    if "loan_emi" in loan:
                                        dct['pl2_coapplicant_obligation_emi'] = loan['loan_emi']
                                    if "loan_opening_date" in loan:
                                        dct['pl2_coapplicant_obligation_data_is'] = True
                                        dct['pl2_coapplicant_obligation_loan_opening_date'] = loan['loan_opening_date']
                                    if "loan_tenure_months" in loan:
                                        dct['pl2_coapplicant_obligation_tenure'] = loan['loan_tenure_months']
                                    if "loan_rate_of_interest" in loan:
                                        dct['pl2_coapplicant_obligation_data_is'] = True
                                        dct['pl2_coapplicant_obligation_roi'] = loan['loan_rate_of_interest']
                                    if "loan_type_of_security" in loan:
                                        dct['pl2_coapplicant_obligation_type_of_security'] = loan['loan_type_of_security']
                                    if "loan_current_outstanding_amount" in loan:
                                        dct['pl2_coapplicant_obligation_current_out_standing_amount'] = loan['loan_current_outstanding_amount']
                                    

                                if loan_loop == 2:
                                    if "pl3_coapplicant_obligation_data_is" in loan:
                                        dct['pl3_coapplicant_obligation_data_is'] = loan['pl3_coapplicant_obligation_data_is']
                                    if "loan_bank_id" in loan:
                                        dct['pl3_coapplicant_obligation_bank_name'] = loan['loan_bank_id']
                                    if "loan_type" in loan:
                                        dct['pl3_coapplicant_obligation_type_of_loan'] = loan['loan_type']
                                    if "loan_account_number" in loan:
                                        dct['pl3_coapplicant_obligation_account_number'] = loan['loan_account_number']
                                    if "loan_amount" in loan:
                                        dct['pl3_coapplicant_obligation_loan_amount'] = loan['loan_amount']       
                                    if "loan_emi" in loan:
                                        dct['pl3_coapplicant_obligation_emi'] = loan['loan_emi']
                                    if "loan_opening_date" in loan:
                                        dct['pl3_coapplicant_obligation_loan_opening_date'] = loan['loan_opening_date']
                                    if "loan_tenure_months" in loan:
                                        dct['pl3_coapplicant_obligation_tenure'] = loan['loan_tenure_months']
                                    if "loan_rate_of_interest" in loan:
                                        dct['pl3_coapplicant_obligation_roi'] = loan['loan_rate_of_interest']
                                    if "loan_type_of_security" in loan:
                                        dct['pl3_coapplicant_obligation_type_of_security'] = loan['loan_type_of_security']
                                    if "loan_current_outstanding_amount" in loan:
                                        dct['pl3_coapplicant_obligation_current_out_standing_amount'] = loan['loan_current_outstanding_amount']    
                                loan_loop = loan_loop + 1

                        if "loans" in co_applicant and co_applicant_1 == 1:
                            loan_loop = 0
                            for loan in co_applicant['loans']:
                                if loan_loop == 0:
                                    print("loan@@@@@@@@@@@@@@@@@@@@222222222222222222222",loan)
                                    if 'loan_bank_id' in loan:
                                        dct['p2_coapplicant_obligation_data_is'] = True
                                        dct['p2_coapplicant_obligation_bank_name'] = loan['loan_bank_id']
                                    if 'loan_type' in loan:
                                        dct['p2_coapplicant_obligation_type_of_loan'] = loan['loan_type']
                                    if 'loan_account_number' in loan:
                                        dct['p2_coapplicant_obligation_data_is'] = True
                                        dct['p2_coapplicant_obligation_account_number'] = loan['loan_account_number']
                                    if 'loan_emi' in loan:
                                        dct['p2_coapplicant_obligation_emi'] = loan['loan_emi']
                                    if 'loan_opening_date' in loan:
                                        dct['p2_coapplicant_obligation_data_is'] = True
                                        dct['p2_coapplicant_obligation_loan_opening_date'] = loan['loan_opening_date']
                                    if 'loan_tenure_months' in loan:
                                        dct['p2_coapplicant_obligation_tenure'] = loan['loan_tenure_months']
                                    if 'loan_rate_of_interest' in loan:
                                        dct['p2_coapplicant_obligation_data_is'] = True
                                        dct['p2_coapplicant_obligation_roi'] = loan['loan_rate_of_interest']
                                    if 'loan_type_of_security' in loan:
                                        dct['p2_coapplicant_obligation_type_of_security'] = loan['loan_type_of_security']
                                    if 'loan_current_outstanding_amount' in loan:
                                        dct['p2_coapplicant_obligation_data_is'] = True
                                        dct['p2_coapplicant_obligation_current_out_standing_amount'] = loan['loan_current_outstanding_amount']
                                    if "loan_amount" in loan:
                                        dct['p2_coapplicant_obligation_loan_amount'] = loan['loan_amount']     
                                        
                                if loan_loop == 1:
                                    print("loan@@@@@@@@@@@@@@@@@@@@1111111111111111111111111111",loan)
                                    if "pl22_coapplicant_obligation_data_is" in loan:
                                        dct['pl22_coapplicant_obligation_data_is'] = loan['pl22_coapplicant_obligation_data_is']
                                    if "loan_bank_id" in loan:
                                        dct['pl22_coapplicant_obligation_data_is'] = True
                                        dct['pl22_coapplicant_obligation_bank_name'] = loan['loan_bank_id']
                                    if "loan_type" in loan:
                                        dct['pl22_coapplicant_obligation_data_is'] = True
                                        dct['pl22_coapplicant_obligation_type_of_loan'] = loan['loan_type']
                                    if "loan_account_number" in loan:
                                        dct['pl2_coapplicant_obligation_data_is'] = True
                                        dct['pl22_coapplicant_obligation_account_number'] = loan['loan_account_number']
                                    if "loan_amount" in loan:
                                        dct['pl22_coapplicant_obligation_loan_amount'] = loan['loan_amount']    
                                    if "loan_emi" in loan:
                                        dct['pl22_coapplicant_obligation_emi'] = loan['loan_emi']
                                    if "loan_opening_date" in loan:
                                        dct['pl22_coapplicant_obligation_data_is'] = True
                                        dct['pl22_coapplicant_obligation_loan_opening_date'] = loan['loan_opening_date']
                                    if "loan_tenure_months" in loan:
                                        dct['pl22_coapplicant_obligation_tenure'] = loan['loan_tenure_months']
                                    if "loan_rate_of_interest" in loan:
                                        dct['pl22_coapplicant_obligation_data_is'] = True
                                        dct['pl22_coapplicant_obligation_roi'] = loan['loan_rate_of_interest']
                                    if "loan_type_of_security" in loan:
                                        dct['pl22_coapplicant_obligation_type_of_security'] = loan['loan_type_of_security']
                                    if "loan_current_outstanding_amount" in loan:
                                        dct['pl22_coapplicant_obligation_current_out_standing_amount'] = loan['loan_current_outstanding_amount']
                                    

                                if loan_loop == 2:
                                    if "pl3_coapplicant_obligation_data_is" in loan:
                                        dct['pl32_coapplicant_obligation_data_is'] = loan['pl32_coapplicant_obligation_data_is']
                                    if "loan_bank_id" in loan:
                                        dct['pl32_coapplicant_obligation_bank_name'] = loan['loan_bank_id']
                                    if "loan_type" in loan:
                                        dct['pl32_coapplicant_obligation_type_of_loan'] = loan['loan_type']
                                    if "loan_account_number" in loan:
                                        dct['pl32_coapplicant_obligation_account_number'] = loan['loan_account_number']
                                    if "loan_amount" in loan:
                                        dct['pl32_coapplicant_obligation_loan_amount'] = loan['loan_amount']       
                                    if "loan_emi" in loan:
                                        dct['pl32_coapplicant_obligation_emi'] = loan['loan_emi']
                                    if "loan_opening_date" in loan:
                                        dct['pl32_coapplicant_obligation_loan_opening_date'] = loan['loan_opening_date']
                                    if "loan_tenure_months" in loan:
                                        dct['pl32_coapplicant_obligation_tenure'] = loan['loan_tenure_months']
                                    if "loan_rate_of_interest" in loan:
                                        dct['pl32_coapplicant_obligation_roi'] = loan['loan_rate_of_interest']
                                    if "loan_type_of_security" in loan:
                                        dct['pl32_coapplicant_obligation_type_of_security'] = loan['loan_type_of_security']
                                    if "loan_current_outstanding_amount" in loan:
                                        dct['pl32_coapplicant_obligation_current_out_standing_amount'] = loan['loan_current_outstanding_amount']    
                                loan_loop = loan_loop + 1
                        if "loans" in co_applicant and co_applicant_1 == 2:
                            loan_loop = 0
                            for loan in co_applicant['loans']:
                                if loan_loop == 0:
                                    print("loan@@@@@@@@@@@@@@@@@@@@222222222222222222222",loan)
                                    if 'loan_bank_id' in loan:
                                        dct['p3_coapplicant_obligation_data_is'] = True
                                        dct['p3_coapplicant_obligation_bank_name'] = loan['loan_bank_id']
                                    if 'loan_type' in loan:
                                        dct['p3_coapplicant_obligation_type_of_loan'] = loan['loan_type']
                                    if 'loan_account_number' in loan:
                                        dct['p3_coapplicant_obligation_data_is'] = True
                                        dct['p3_coapplicant_obligation_account_number'] = loan['loan_account_number']
   
                                    if 'loan_emi' in loan:
                                        dct['p3_coapplicant_obligation_emi'] = loan['loan_emi']
                                    if 'loan_opening_date' in loan:
                                        dct['p3_coapplicant_obligation_data_is'] = True
                                        dct['p3_coapplicant_obligation_loan_opening_date'] = loan['loan_opening_date']
                                    if 'loan_tenure_months' in loan:
                                        dct['p3_coapplicant_obligation_tenure'] = loan['loan_tenure_months']
                                    if 'loan_rate_of_interest' in loan:
                                        dct['p3_coapplicant_obligation_data_is'] = True
                                        dct['p3_coapplicant_obligation_roi'] = loan['loan_rate_of_interest']
                                    if 'loan_type_of_security' in loan:
                                        dct['p3_coapplicant_obligation_type_of_security'] = loan['loan_type_of_security']
                                    if 'loan_current_outstanding_amount' in loan:
                                        dct['p3_coapplicant_obligation_data_is'] = True
                                        dct['p3_coapplicant_obligation_current_out_standing_amount'] = loan['loan_current_outstanding_amount']
                                    if "loan_amount" in loan:
                                        dct['p3_coapplicant_obligation_loan_amount'] = loan['loan_amount']     
                                        
                                if loan_loop == 1:
                                    print("loan@@@@@@@@@@@@@@@@@@@@1111111111111111111111111111",loan)
                                    if "pl23_coapplicant_obligation_data_is" in loan:
                                        dct['pl23_coapplicant_obligation_data_is'] = loan['pl23_coapplicant_obligation_data_is']
                                    if "loan_bank_id" in loan:
                                        dct['pl23_coapplicant_obligation_data_is'] = True
                                        dct['pl23_coapplicant_obligation_bank_name'] = loan['loan_bank_id']
                                    if "loan_type" in loan:
                                        dct['pl23_coapplicant_obligation_data_is'] = True
                                        dct['pl23_coapplicant_obligation_type_of_loan'] = loan['loan_type']
                                    if "loan_account_number" in loan:
                                        dct['pl23_coapplicant_obligation_data_is'] = True
                                        dct['pl23_coapplicant_obligation_account_number'] = loan['loan_account_number']
                                    if "loan_amount" in loan:
                                        dct['pl23_coapplicant_obligation_loan_amount'] = loan['loan_amount']    
                                    if "loan_emi" in loan:
                                        dct['pl23_coapplicant_obligation_emi'] = loan['loan_emi']
                                    if "loan_opening_date" in loan:
                                        dct['pl23_coapplicant_obligation_data_is'] = True
                                        dct['pl23_coapplicant_obligation_loan_opening_date'] = loan['loan_opening_date']
                                    if "loan_tenure_months" in loan:
                                        dct['pl23_coapplicant_obligation_tenure'] = loan['loan_tenure_months']
                                    if "loan_rate_of_interest" in loan:
                                        dct['pl23_coapplicant_obligation_data_is'] = True
                                        dct['pl23_coapplicant_obligation_roi'] = loan['loan_rate_of_interest']
                                    if "loan_type_of_security" in loan:
                                        dct['pl23_coapplicant_obligation_type_of_security'] = loan['loan_type_of_security']
                                    if "loan_current_outstanding_amount" in loan:
                                        dct['pl23_coapplicant_obligation_current_out_standing_amount'] = loan['loan_current_outstanding_amount']
                                    

                                if loan_loop == 2:
                                    if "pl33_coapplicant_obligation_data_is" in loan:
                                        dct['pl33_coapplicant_obligation_data_is'] = loan['pl33_coapplicant_obligation_data_is']
                                    if "loan_bank_id" in loan:
                                        dct['pl33_coapplicant_obligation_bank_name'] = loan['loan_bank_id']
                                    if "loan_type" in loan:
                                        dct['pl33_coapplicant_obligation_type_of_loan'] = loan['loan_type']
                                    if "loan_account_number" in loan:
                                        dct['pl33_coapplicant_obligation_account_number'] = loan['loan_account_number']
                                    if "loan_amount" in loan:
                                        dct['pl33_coapplicant_obligation_loan_amount'] = loan['loan_amount']       
                                    if "loan_emi" in loan:
                                        dct['pl33_coapplicant_obligation_emi'] = loan['loan_emi']
                                    if "loan_opening_date" in loan:
                                        dct['pl33_coapplicant_obligation_loan_opening_date'] = loan['loan_opening_date']
                                    if "loan_tenure_months" in loan:
                                        dct['pl33_coapplicant_obligation_tenure'] = loan['loan_tenure_months']
                                    if "loan_rate_of_interest" in loan:
                                        dct['pl33_coapplicant_obligation_roi'] = loan['loan_rate_of_interest']
                                    if "loan_type_of_security" in loan:
                                        dct['pl33_coapplicant_obligation_type_of_security'] = loan['loan_type_of_security']
                                    if "loan_current_outstanding_amount" in loan:
                                        dct['pl33_coapplicant_obligation_current_out_standing_amount'] = loan['loan_current_outstanding_amount']    
                                loan_loop = loan_loop + 1
                        co_applicant_1 = co_applicant_1 + 1        



                if "co_applicant" in kw:
                    print("kw['co_applicant']@@@@@@@@@@@@@@@@@@@@@@@@",kw['co_applicant'])
                    co_applicant_1 = 0
                    for co_applicant in kw['co_applicant']:
                        print("co_applicant@@@@@@@@@@@@@@@@@@@@@@@@@",co_applicant)
                        coapplicant_first = ""
                        coapplicant_last = ""
                        if co_applicant_1 == 0:
                            if "applicant_first_name" in co_applicant:
                                coapplicant_first = co_applicant['applicant_first_name']
                            if "applicant_last_name" in co_applicant:
                                coapplicant_last = co_applicant['applicant_last_name']
                            if 'applicant_first_name' in co_applicant:
                                coapplicant_name = coapplicant_first + coapplicant_last
                                dct['p_co_applicant_name'] = coapplicant_name   
                                dct['p_co_applicant_data'] = True    

                            if "applicant_additional_income" in co_applicant:
                                dct["p_business_co_aaplicant_data_is"] = True
                                data_co_applicant1 = 0
                                for co_applicant1_additional_income in co_applicant['applicant_additional_income']:
                                    if data_co_applicant1 == 0:
                                        if 'income_amount' in co_applicant1_additional_income:
                                            dct['p1_coapplicant_business_additional_amount'] = co_applicant1_additional_income['income_amount']
                                        if 'income_source' in co_applicant1_additional_income:
                                            dct['p1_coapplicant_business_additional_source'] = co_applicant1_additional_income['income_source']
                                    if data_co_applicant1 == 1:
                                        if 'income_amount' in co_applicant1_additional_income:
                                            dct['p12_coapplicant_business_additional_amount'] = co_applicant1_additional_income['income_amount']
                                        if 'income_source' in co_applicant1_additional_income:
                                            dct['p12_coapplicant_business_additional_source'] = co_applicant1_additional_income['income_source']
                                    data_co_applicant1 = data_co_applicant1 + 1
                            

                            if 'applicant_relation' in co_applicant:
                                dct['p_relationship_with_applicant'] = co_applicant['applicant_relation']
                            if 'applicant_is' in co_applicant:
                                dct['p_co_applicant_is'] = co_applicant['applicant_is']
                            if 'applicant_gender' in co_applicant:
                                dct['p_co_applicant_gender'] = co_applicant['applicant_gender'].lower()
                            if 'applicant_marital_status' in co_applicant:
                                dct['p_co_applicant_marital_status'] = co_applicant['applicant_marital_status']
                            if 'applicant_father_husband_name' in co_applicant:
                                dct['p_co_applicant_father_husband_name'] = co_applicant['applicant_father_husband_name']
                            if 'applicant_educational_qualification' in co_applicant:
                                dct['p_co_applicant_educational_qualification'] = co_applicant['applicant_educational_qualification']
                            if 'applicant_email_id' in co_applicant:
                                dct['p_co_applicant_personal_email_d'] = co_applicant['applicant_email_id']
                            if 'applicant_phone' in co_applicant:
                                dct['p_co_applicant_mobile_number'] = co_applicant['applicant_phone'] 
                            if 'applicant_current_address_document_type' in co_applicant:
                                dct['p_kyc_coapplicant_type_of_document'] = co_applicant['applicant_current_address_document_type']
                                dct['p_kyc_coapplicant_data_is'] = True
                            if 'applicant_current_address_document_front' in co_applicant:
                                if 'base64,' in co_applicant['applicant_current_address_document_front']:
                                    if "pdf" in co_applicant['applicant_current_address_document_front'].split('base64,')[0]:
                                        dct['p_kyc_coapplicant_current_address_residence_proof_front_pdf'] = co_applicant['applicant_current_address_document_front'].split('base64,')[1].replace(" ", "+")
                                    else:
                                        dct['p_kyc_coapplicant_current_address_residence_proof_front'] = co_applicant['applicant_current_address_document_front'].split('base64,')[1].replace(" ", "+")
                            if 'applicant_current_address_document_back' in co_applicant:
                                if 'base64,' in co_applicant['applicant_current_address_document_back']:
                                    dct['p_kyc_coapplicant_current_address_residence_proof_back'] = co_applicant['applicant_current_address_document_back'].split('base64,')[1].replace(" ", "+")
                            if 'applicant_pan_card_document' in co_applicant:
                                if 'base64,' in co_applicant['applicant_pan_card_document']:
                                    if "pdf" in co_applicant['applicant_pan_card_document'].split('base64,')[0]:
                                        dct['p_kyc_coapplicant_current_pan_card_photo_pdf'] = co_applicant['applicant_pan_card_document'].split('base64,')[1].replace(" ", "+")
                                    else:
                                        dct['p_kyc_coapplicant_current_pan_card_photo'] = co_applicant['applicant_pan_card_document'].split('base64,')[1].replace(" ", "+")
                            if 'applicant_pan_number' in co_applicant:
                                dct['p_kyc_coapplicant_current_pan_number'] = co_applicant['applicant_pan_number']
                            if 'applicant_date_of_birth' in co_applicant:
                                dct['p_kyc_coapplicant_data_is'] = True
                                dct['p_kyc_coapplicant_current_date_of_birth'] = co_applicant['applicant_date_of_birth']
                            

                            p_business_co_aaplicant_year_in_current_job_year = 0
                            p_business_co_aaplicant_year_in_current_job_month = 0
                            if 'applicant_total_exp_current_role' in co_applicant:
                                p_business_co_aaplicant_year_in_current_job_year = float(co_applicant['applicant_total_exp_current_role'])
                            if 'p_business_co_aaplicant_year_in_current_job_month' in co_applicant:
                                p_business_co_aaplicant_year_in_current_job_month = float(co_applicant['p_business_co_aaplicant_year_in_current_job_month']) / 12       
                            if 'applicant_total_exp_current_role' in co_applicant:
                                dct['p_business_co_aaplicant_year_in_current_job_year_month'] = p_business_co_aaplicant_year_in_current_job_year + p_business_co_aaplicant_year_in_current_job_month
                            
                            p_busness_co_aaplicant_total_work_experieance_year = 0
                            p_busness_co_aaplicant_total_work_experieance_month = 0
                            if 'applicant_total_exp' in co_applicant:
                                p_busness_co_aaplicant_total_work_experieance_year = float(co_applicant['applicant_total_exp'])
                            if 'p_busness_co_aaplicant_total_work_experieance_month' in co_applicant:
                                p_busness_co_aaplicant_total_work_experieance_month = float(co_applicant['p_busness_co_aaplicant_total_work_experieance_month']) / 12

                            if 'applicant_total_exp' in co_applicant:
                                dct['p_business_co_aaplicant_data_is'] = True
                                dct['p_busness_co_aaplicant_total_work_experieance'] = p_busness_co_aaplicant_total_work_experieance_year + p_busness_co_aaplicant_total_work_experieance_month
                            if 'applicant_monthly_net_salary' in co_applicant:
                                dct['p_business_co_aaplicant_data_is'] = True
                                dct['p_busness_co_aaplicant_net_monthly_salary'] = co_applicant['applicant_monthly_net_salary']
                            if 'applicant_monthly_gross_salary' in co_applicant:
                                dct['p_business_co_aaplicant_gross_monthly_salary'] = co_applicant['applicant_monthly_gross_salary']
                            if "applicant_profession" in co_applicant:
                                dct['p_business_co_aaplicant_applicant_profession'] = co_applicant["applicant_profession"]    
                            if 'applicant_employment_type' in co_applicant:
                                dct['p_business_co_aaplicant_data_is'] = True
                                dct['p_business_co_aaplicant_employment_type'] = co_applicant['applicant_employment_type']
                            if 'applicant_current_organization_name' in co_applicant:
                                dct['p_business_co_aaplicant_orginization_name'] = co_applicant['applicant_current_organization_name']
                            if 'applicant_designation' in co_applicant:
                                dct['p_business_co_aaplicant_data_is'] = True
                                dct['p_business_co_aaplicant_designation'] = co_applicant['applicant_designation']
                            if 'applicant_department' in co_applicant:
                                dct['p_business_co_aaplicant_department'] = co_applicant['applicant_department'] 
                            if 'applicant_professional_receipts' in co_applicant:
                                dct["p_business_co_aaplicant_data_is"] = True
                                dct['p_business_co_aaplicant_gross_professional_receipt'] = co_applicant['applicant_professional_receipts']
                            if 'applicant_employer_name' in co_applicant:
                                dct['p_busness_co_aaplicant_business_name'] = co_applicant['applicant_employer_name']
                            if 'business_name' in co_applicant:
                                dct['p_co_applicant_data'] = True
                                dct['p_busness_co_aaplicant_business_name'] = co_applicant['business_name']    
                            if 'applicant_role' in co_applicant:
                                dct['p_busness_co_aaplicant_coaaplicant_is_a'] = co_applicant['applicant_role']

                            if "applicant_is" in co_applicant:
                                dct["p_business_co_aaplicant_data_is"] = True
                                dct["p_busness_co_aaplicant_coaaplicant_is_a"]  = co_applicant["applicant_is"]   
                            if 'p_business_co_aaplicant_constitution' in co_applicant:
                                dct['p_business_co_aaplicant_constitution'] = co_applicant['p_business_co_aaplicant_constitution']
                            if 'p_busness_co_aaplicant_amount' in co_applicant:
                                dct['p_busness_co_aaplicant_amount'] = co_applicant['p_busness_co_aaplicant_amount']
                            if 'applicant_share_holding_percentage' in co_applicant:
                                dct['p_busness_co_aaplicant_share_holding'] = co_applicant['applicant_share_holding_percentage']
                            if 'applicant_monthly_renumeration' in co_applicant:
                                dct["p_business_co_aaplicant_data_is"] = True
                                dct['p_business_co_aaplicant_monthly_renumeration'] = co_applicant['applicant_monthly_renumeration']
                            if 'applicant_annual_income' in co_applicant:
                                dct["p_business_co_aaplicant_data_is"] = True
                                dct['p_busness_co_aaplicant_annual_income'] = co_applicant['applicant_annual_income']


                            print("co_applicant@@@@@@@@@@@@@@@@@",co_applicant)    

                            if "loans" in co_applicant:
                                loan_loop = 0
                                for loan in co_applicant['loans']:
                                    print("loan@@@@@@@@@@@@@@@@@@@@",loan)
                                    if loan_loop == 0:
                                        if 'loan_bank_id' in loan:
                                            dct['p_coapplicant_obligation_data_is'] = True
                                            dct['p_coapplicant_obligation_bank_name'] = loan['loan_bank_id']
                                        if 'loan_type' in loan:
                                            dct['p_coapplicant_obligation_type_of_loan'] = loan['loan_type']
                                        if 'loan_account_number' in loan:
                                            dct['p_coapplicant_obligation_data_is'] = True
                                            dct['p_coapplicant_obligation_account_number'] = loan['loan_account_number']
                                        if 'loan_emi' in loan:
                                            dct['p_coapplicant_obligation_emi'] = loan['loan_emi']
                                        if 'loan_opening_date' in loan:
                                            dct['p_coapplicant_obligation_data_is'] = True
                                            dct['p_coapplicant_obligation_loan_opening_date'] = loan['loan_opening_date']
                                        if 'loan_tenure_months' in loan:
                                            dct['p_coapplicant_obligation_tenure'] = loan['loan_tenure_months']
                                        if 'loan_rate_of_interest' in loan:
                                            dct['p_coapplicant_obligation_data_is'] = True
                                            dct['p_coapplicant_obligation_roi'] = loan['loan_rate_of_interest']
                                        if 'loan_type_of_security' in loan:
                                            dct['p_coapplicant_obligation_type_of_security'] = loan['loan_type_of_security']
                                        if 'loan_current_outstanding_amount' in loan:
                                            dct['p_coapplicant_obligation_data_is'] = True
                                            dct['p_coapplicant_obligation_current_out_standing_amount'] = loan['loan_current_outstanding_amount']
                                        
                                    if loan_loop == 1:
                                        if "pl2_coapplicant_obligation_data_is" in loan:
                                            dct['pl2_coapplicant_obligation_data_is'] = loan['pl2_coapplicant_obligation_data_is']
                                        if "loan_bank_id" in loan:
                                            dct['pl2_coapplicant_obligation_data_is'] = True
                                            dct['pl2_coapplicant_obligation_bank_name'] = loan['loan_bank_id']
                                        if "loan_type" in loan:
                                            dct['pl2_coapplicant_obligation_data_is'] = True
                                            dct['pl2_coapplicant_obligation_type_of_loan'] = loan['loan_type']
                                        if "loan_account_number" in loan:
                                            dct['pl2_coapplicant_obligation_data_is'] = True
                                            dct['pl2_coapplicant_obligation_account_number'] = loan['loan_account_number']
                                        if "loan_amount" in loan:
                                            dct['pl2_coapplicant_obligation_loan_amount'] = loan['loan_amount']    
                                        if "loan_emi" in loan:
                                            dct['pl2_coapplicant_obligation_emi'] = loan['loan_emi']
                                        if "loan_opening_date" in loan:
                                            dct['pl2_coapplicant_obligation_data_is'] = True
                                            dct['pl2_coapplicant_obligation_loan_opening_date'] = loan['loan_opening_date']
                                        if "loan_tenure_months" in loan:
                                            dct['pl2_coapplicant_obligation_tenure'] = loan['loan_tenure_months']
                                        if "loan_rate_of_interest" in loan:
                                            dct['pl2_coapplicant_obligation_data_is'] = True
                                            dct['pl2_coapplicant_obligation_roi'] = loan['loan_rate_of_interest']
                                        if "loan_type_of_security" in loan:
                                            dct['pl2_coapplicant_obligation_type_of_security'] = loan['loan_type_of_security']
                                        if "loan_current_outstanding_amount" in loan:
                                            dct['pl2_coapplicant_obligation_current_out_standing_amount'] = loan['loan_current_outstanding_amount']
                                        

                                    if loan_loop == 2:
                                        if "pl3_coapplicant_obligation_data_is" in loan:
                                            dct['pl3_coapplicant_obligation_data_is'] = loan['pl3_coapplicant_obligation_data_is']
                                        if "loan_bank_id" in loan:
                                            dct['pl3_coapplicant_obligation_bank_name'] = loan['loan_bank_id']
                                        if "loan_type" in loan:
                                            dct['pl3_coapplicant_obligation_type_of_loan'] = loan['loan_type']
                                        if "loan_account_number" in loan:
                                            dct['pl3_coapplicant_obligation_account_number'] = loan['loan_account_number']
                                        if "loan_amount" in loan:
                                            dct['pl3_coapplicant_obligation_loan_amount'] = loan['loan_amount']       
                                        if "loan_emi" in loan:
                                            dct['pl3_coapplicant_obligation_emi'] = loan['loan_emi']
                                        if "loan_opening_date" in loan:
                                            dct['pl3_coapplicant_obligation_loan_opening_date'] = loan['loan_opening_date']
                                        if "loan_tenure_months" in loan:
                                            dct['pl3_coapplicant_obligation_tenure'] = loan['loan_tenure_months']
                                        if "loan_rate_of_interest" in loan:
                                            dct['pl3_coapplicant_obligation_roi'] = loan['loan_rate_of_interest']
                                        if "loan_type_of_security" in loan:
                                            dct['pl3_coapplicant_obligation_type_of_security'] = loan['loan_type_of_security']
                                        if "loan_current_outstanding_amount" in loan:
                                            dct['pl3_coapplicant_obligation_current_out_standing_amount'] = loan['loan_current_outstanding_amount']    
                                    loan_loop = loan_loop + 1

                            # if "applicant_business_details" in co_applicant:
                            #     applicant_business_detail = co_applicant['applicant_business_details']
                            if 'business_current_year_profit_after_tax' in co_applicant:
                                dct["p_business_co_aaplicant_data_is"] = True
                                dct['p_busness_co_aaplicant_profit_after_tax_after_current_year'] = co_applicant['business_current_year_profit_after_tax']
                            if 'business_current_year_turnover' in co_applicant:
                                dct["p_business_co_aaplicant_data_is"] = True
                                dct['p_business_co_aaplicant_current_year_turnover'] = co_applicant['business_current_year_turnover']
                            if 'applicant_profit_percentage' in co_applicant:
                                dct["p_business_co_aaplicant_data_is"] = True
                                dct['p_busness_co_aaplicant_share_in_profit'] = co_applicant['applicant_profit_percentage']
                            if 'business_previous_year_profit_after_tax' in co_applicant:
                                dct['p_busness_co_aaplicant_profit_after_tax_previous_year'] = co_applicant['business_previous_year_profit_after_tax']
                            if 'business_previous_year_turnover' in co_applicant:
                                dct['p_business_co_aaplicant_previous_year_turn_over'] = co_applicant['business_previous_year_turnover']
                            if 'p_business_co_aaplicant_source' in co_applicant:
                                dct['p_business_co_aaplicant_source'] = co_applicant['p_business_co_aaplicant_source']    
                            if "address" in co_applicant:
                                first_co_loop = 0
                                for coapp in co_applicant['address']:   
                                    if "address_type" in coapp and coapp["address_type"] == "CURRENT":
                                        if 'address_residence_type' in coapp:
                                            dct['p_coapplicant_address_residence_owner_rent'] = coapp['address_residence_type']
                                        if 'p_coapplicant_address_number_of_year_in_current_residence' in coapp:
                                            dct['p_coapplicant_address_data_is'] = True
                                            dct['p_coapplicant_address_number_of_year_in_current_residence'] = coapp['p_coapplicant_address_number_of_year_in_current_residence']
                                        if 'address_house' in coapp:
                                            dct['p_coapplicant_address_flat_house'] = coapp['address_house']
                                        if 'address_area' in coapp:
                                            dct['p_coapplicant_address_street_lane'] = coapp['address_area']
                                        if 'address_city' in coapp:
                                            dct['p_coapplicant_address_data_is'] = True
                                            dct['p_coapplicant_address_city'] = coapp['address_city']
                                        if 'address_state' in coapp:
                                            dct['p_coapplicant_address_data_is'] = True
                                            dct['p_coapplicant_address_state'] = coapp['address_state']
                                        if "address_pincode" in coapp:
                                            dct['p_coapplicant_pincode'] = coapp['address_pincode'] 
                                    if "address_type" in coapp and coapp["address_type"] == "PERMANENT":    
                                        if 'address_type' in coapp:
                                            dct['p_coapplicant_address_data_is'] = True
                                            dct['p_coapplicant_permant_address_proof'] = coapp['address_type']
                                        if 'address_document' in coapp:
                                            if 'base64,' in coapp['address_document']:
                                                if "pdf" in coapp['address_document'].split('base64,')[0]:
                                                    dct['p_coapplicant_permant_address_proof_photo_pdf'] = coapp['address_document'].split('base64,')[1].replace(" ", "+")
                                                else:
                                                    dct['p_coapplicant_permant_address_proof_photo'] = coapp['address_document'].split('base64,')[1].replace(" ", "+")
                                        if 'address_pincode' in coapp:
                                            dct['p_coapplicant_permant_pin_code'] = coapp['address_pincode']
                                        if 'address_area' in coapp:
                                            dct['p_coapplicant_permant_street_lane'] = coapp['address_area']
                                        if 'address_house' in coapp:
                                            dct['p_coapplicant_permant_flat_house'] = coapp['address_house']
                                        if 'address_state' in coapp:
                                            dct['p_coapplicant_permant_state'] = coapp['address_state']
                                        if 'address_city' in coapp:
                                            dct['p_coapplicant_permant_city'] = coapp['address_city']
                                    first_co_loop = first_co_loop + 1


                        if co_applicant_1 == 1:
                            if "applicant_relation" in co_applicant:
                                dct["p2_co_applicant_data"] = True
                                dct['p2_relationship_with_applicant'] = co_applicant['applicant_relation']
                            if "applicant_is" in co_applicant:
                                dct['p2_business_co_aaplicant_data_is'] = True
                                dct['p2_co_applicant_is'] = co_applicant['applicant_is']
                            coapplicant2_first = ""
                            coapplicant2_last = ""
                            if "applicant_first_name" in co_applicant:
                                coapplicant2_first = co_applicant['applicant_first_name']
                            if "applicant_last_name" in co_applicant:
                                coapplicant2_last = co_applicant['applicant_last_name']


                            if "applicant_additional_income" in co_applicant:
                                dct["p2_business_co_aaplicant_data_is"] = True
                                data_co_applicant2 = 0
                                for co_applicant2_additional_income in co_applicant['applicant_additional_income']:
                                    if data_co_applicant2 == 0:
                                        if 'income_amount' in co_applicant2_additional_income:
                                            dct['p2_coapplicant_business_additional_amount'] = co_applicant2_additional_income['income_amount']
                                        if 'income_source' in co_applicant2_additional_income:
                                            dct['p2_coapplicant_business_additional_source'] = co_applicant2_additional_income['income_source']
                                    if data_co_applicant2 == 1:
                                        if 'income_amount' in co_applicant2_additional_income:
                                            dct['p22_coapplicant_business_additional_amount'] = co_applicant2_additional_income['income_amount']
                                        if 'income_source' in co_applicant2_additional_income:
                                            dct['p22_coapplicant_business_additional_source'] = co_applicant2_additional_income['income_source']
                                    data_co_applicant2 = data_co_applicant2 + 1    

                            if 'applicant_first_name' in co_applicant:
                                coapplicant2_name = coapplicant2_first +  " " + coapplicant2_last
                                dct['p2_co_applicant_name'] = coapplicant2_name  
                            if "applicant_gender" in co_applicant:
                                dct['p2_co_applicant_gender'] = co_applicant['applicant_gender'].lower()
                            if "applicant_marital_status" in co_applicant:
                                dct['p2_co_applicant_marital_status'] = co_applicant['applicant_marital_status']
                            if "applicant_father_husband_name" in co_applicant:
                                dct['p2_co_applicant_father_husband_name'] = co_applicant['applicant_father_husband_name']
                            if "applicant_educational_qualification" in co_applicant:
                                dct['p2_co_applicant_educational_qualification'] = co_applicant['applicant_educational_qualification']
                            if "applicant_email_id" in co_applicant:
                                dct['p2_co_applicant_personal_email_d'] = co_applicant['applicant_email_id']
                            if "applicant_phone" in co_applicant:
                                dct['p2_co_applicant_mobile_number'] = co_applicant['applicant_phone'] 

                            if "applicant_profession" in co_applicant:
                                dct['p2_business_co_aaplicant_applicant_profession'] = co_applicant["applicant_profession"]          


                            if "applicant_current_address_document_type" in co_applicant:
                                dct["p2_kyc_coapplicant_data_is"] = True
                                dct['p2_kyc_coapplicant_type_of_document'] = co_applicant['applicant_current_address_document_type']
                            # if "applicant_current_address_document_front" in co_applicant:
                            #     dct[''] = co_applicant['applicant_current_address_document_front']

                            if 'applicant_current_address_document_front' in co_applicant:
                                if 'base64,' in co_applicant['applicant_current_address_document_front']:
                                    if "pdf" in co_applicant['applicant_current_address_document_front'].split('base64,')[0]:
                                        dct['p2_kyc_coapplicant_current_address_residence_proof_front_pdf'] = co_applicant['applicant_current_address_document_front'].split('base64,')[1].replace(" ", "+")
                                    else:
                                        dct['p2_kyc_coapplicant_current_address_residence_proof_front'] = co_applicant['applicant_current_address_document_front'].split('base64,')[1].replace(" ", "+")

                            if 'applicant_current_address_document_front' in co_applicant:
                                if 'base64,' in co_applicant['applicant_current_address_document_front']:
                                    if "pdf" in co_applicant['applicant_current_address_document_front'].split('base64,')[0]:
                                        dct['p2_kyc_coapplicant_current_address_residence_proof_back_pdf'] = co_applicant['applicant_current_address_document_front'].split('base64,')[1].replace(" ", "+")
                                    else:
                                        dct['p2_kyc_coapplicant_current_address_residence_proof_back'] = co_applicant['applicant_current_address_document_front'].split('base64,')[1].replace(" ", "+")
                                        

                            # if 'applicant_current_address_document_back' in co_applicant:
                            #     if 'base64,' in co_applicant['applicant_current_address_document_back']:
                            #         dct['p_kyc_coapplicant_current_address_residence_proof_back'] = co_applicant['applicant_current_address_document_back'].split('base64,')[1].replace(" ", "+")
                                        
                            # if "applicant_current_address_document_back" in co_applicant:
                            #     dct['p2_kyc_coapplicant_current_address_residence_proof_back'] = co_applicant['applicant_current_address_document_back']
                            # if "applicant_pan_card_document" in co_applicant:
                            #     dct['p2_kyc_coapplicant_current_pan_card_photo'] = co_applicant['applicant_pan_card_document']
                            if 'applicant_pan_card_document' in co_applicant:
                                if 'base64,' in co_applicant['applicant_pan_card_document']:
                                    if "pdf" in co_applicant['applicant_pan_card_document'].split('base64,')[0]:
                                        dct['p2_kyc_coapplicant_current_pan_card_photo_pdf'] = co_applicant['applicant_pan_card_document'].split('base64,')[1].replace(" ", "+")
                                    else:
                                        dct['p2_kyc_coapplicant_current_pan_card_photo'] = co_applicant['applicant_pan_card_document'].split('base64,')[1].replace(" ", "+")    
                            if "applicant_pan_number" in co_applicant:
                                dct['p2_kyc_coapplicant_current_pan_number'] = co_applicant['applicant_pan_number']
                            if "applicant_date_of_birth" in co_applicant:
                                dct['p2_kyc_coapplicant_current_date_of_birth'] = co_applicant['applicant_date_of_birth']

                            p_business_co_aaplicant_year_in_current_job_year = 0
                            p_business_co_aaplicant_year_in_current_job_month = 0
                            if 'applicant_total_exp_current_role' in co_applicant:
                                p_business_co_aaplicant_year_in_current_job_year = float(co_applicant['applicant_total_exp_current_role'])
                            if 'p2_business_co_aaplicant_year_in_current_job_month' in co_applicant:
                                p_business_co_aaplicant_year_in_current_job_month = float(co_applicant['p2_business_co_aaplicant_year_in_current_job_month']) / 12       
                            if 'applicant_total_exp_current_role' in co_applicant:
                                dct['p2_business_co_aaplicant_year_in_current_job_year_month'] = p_business_co_aaplicant_year_in_current_job_year + p_business_co_aaplicant_year_in_current_job_month
                            
                            p_busness_co_aaplicant_total_work_experieance_year = 0
                            p_busness_co_aaplicant_total_work_experieance_month = 0
                            if 'applicant_total_exp' in co_applicant:
                                p_busness_co_aaplicant_total_work_experieance_year = float(co_applicant['applicant_total_exp'])
                            if 'p2_busness_co_aaplicant_total_work_experieance_month' in co_applicant:
                                p_busness_co_aaplicant_total_work_experieance_month = float(co_applicant['p2_busness_co_aaplicant_total_work_experieance_month']) / 12

                            if 'applicant_total_exp' in co_applicant:
                                dct['p2_business_co_aaplicant_data_is'] = True
                                dct['p2_busness_co_aaplicant_total_work_experieance'] = p_busness_co_aaplicant_total_work_experieance_year + p_busness_co_aaplicant_total_work_experieance_month
                            if 'applicant_monthly_net_salary' in co_applicant:
                                dct['p2_business_co_aaplicant_data_is'] = True
                                dct['p2_busness_co_aaplicant_net_monthly_salary'] = co_applicant['applicant_monthly_net_salary']
                            if 'applicant_monthly_gross_salary' in co_applicant:
                                dct['p2_business_co_aaplicant_gross_monthly_salary'] = co_applicant['applicant_monthly_gross_salary']
                            if 'applicant_employment_type' in co_applicant:
                                dct['p2_business_co_aaplicant_data_is'] = True
                                dct['p2_business_co_aaplicant_employment_type'] = co_applicant['applicant_employment_type']
                            if 'applicant_current_organization_name' in co_applicant:
                                dct['p2_business_co_aaplicant_orginization_name'] = co_applicant['applicant_current_organization_name']
                            if 'applicant_designation' in co_applicant:
                                dct['p2_business_co_aaplicant_data_is'] = True
                                dct['p2_business_co_aaplicant_designation'] = co_applicant['applicant_designation']
                            if 'applicant_department' in co_applicant:
                                dct['p2_business_co_aaplicant_department'] = co_applicant['applicant_department'] 
                            if 'applicant_professional_receipts' in co_applicant:
                                dct['p2_business_co_aaplicant_gross_professional_receipt'] = co_applicant['applicant_professional_receipts']
                            if 'applicant_employer_name' in co_applicant:
                                dct['p2_busness_co_aaplicant_business_name'] = co_applicant['applicant_employer_name']
                            if 'business_name' in co_applicant:
                                dct['p_co_applicant_data'] = True
                                dct['p2_busness_co_aaplicant_business_name'] = co_applicant['business_name']  
                            if "applicant_is" in co_applicant:
                                dct["p2_busness_co_aaplicant_coaaplicant_is_a"]  = co_applicant["applicant_is"]          
                            if 'applicant_role' in co_applicant:
                                dct['p2_busness_co_aaplicant_coaaplicant_is_a'] = co_applicant['applicant_role']
                            if 'p_business_co_aaplicant_constitution' in co_applicant:
                                dct['p2_business_co_aaplicant_constitution'] = co_applicant['p_business_co_aaplicant_constitution']
                            if 'p_busness_co_aaplicant_amount' in co_applicant:
                                dct['p2_busness_co_aaplicant_amount'] = co_applicant['p2_busness_co_aaplicant_amount']
                            if 'applicant_share_holding_percentage' in co_applicant:
                                dct['p2_business_co_aaplicant_data_is'] = True
                                dct['p2_busness_co_aaplicant_share_holding'] = co_applicant['applicant_share_holding_percentage']
                            if 'applicant_monthly_renumeration' in co_applicant:
                                dct['p2_business_co_aaplicant_monthly_renumeration'] = co_applicant['applicant_monthly_renumeration']
                            if 'applicant_annual_income' in co_applicant:
                                dct['p2_business_co_aaplicant_data_is'] = True
                                dct['p2_busness_co_aaplicant_annual_income'] = co_applicant['applicant_annual_income']
                            
                            # if "applicant_business_details" in co_applicant:
                            #     applicant_business_detail = co_applicant['applicant_business_details']
                            if 'business_current_year_profit_after_tax' in co_applicant:
                                dct['p2_business_co_aaplicant_data_is'] = True
                                dct['p2_busness_co_aaplicant_profit_after_tax_after_current_year'] = co_applicant['business_current_year_profit_after_tax']
                            if 'business_current_year_turnover' in co_applicant:
                                dct['p2_business_co_aaplicant_current_year_turnover'] = co_applicant['business_current_year_turnover']
                            if 'applicant_profit_percentage' in co_applicant:
                                dct['p2_business_co_aaplicant_data_is'] = True
                                dct['p2_busness_co_aaplicant_share_in_profit'] = co_applicant['applicant_profit_percentage']
                            if 'business_previous_year_profit_after_tax' in co_applicant:
                                dct['p2_busness_co_aaplicant_profit_after_tax_previous_year'] = co_applicant['business_previous_year_profit_after_tax']
                            if 'business_previous_year_turnover' in co_applicant:
                                dct['p2_business_co_aaplicant_data_is'] = True
                                dct['p2_business_co_aaplicant_previous_year_turn_over'] = co_applicant['business_previous_year_turnover']
                            if 'p2_business_co_aaplicant_source' in co_applicant:
                                dct['p2_business_co_aaplicant_data_is'] = True
                                dct['p2_business_co_aaplicant_source'] = co_applicant['p2_business_co_aaplicant_source']     
                            if "address" in co_applicant:
                                first_co_loop = 0
                                for coapp in co_applicant['address']:   
                                    if "address_type" in coapp and coapp["address_type"] == "CURRENT": 
                                        if 'address_residence_type' in coapp:
                                            dct['p2_coapplicant_address_residence_owner_rent'] = coapp['address_residence_type']
                                        if 'p_coapplicant_address_number_of_year_in_current_residence' in coapp:
                                            dct['p2_coapplicant_address_data_is'] = True
                                            dct['p2_coapplicant_address_number_of_year_in_current_residence'] = coapp['p_coapplicant_address_number_of_year_in_current_residence']
                                        if 'address_house' in coapp:
                                            dct['p2_coapplicant_address_flat_house'] = coapp['address_house']
                                        if 'address_area' in coapp:
                                            dct['p2_coapplicant_address_street_lane'] = coapp['address_area']
                                        if 'address_city' in coapp:
                                            dct['p2_coapplicant_address_data_is'] = True
                                            dct['p2_coapplicant_address_city'] = coapp['address_city']
                                        if 'address_state' in coapp:
                                            dct['p2_coapplicant_address_data_is'] = True
                                            dct['p2_coapplicant_address_state'] = coapp['address_state']
                                        if "address_pincode" in coapp:
                                            dct['p2_coapplicant_pincode'] = coapp['address_pincode'] 
                                    if "address_type" in coapp and coapp["address_type"] == "PERMANENT":
                                        if 'address_type' in coapp:
                                            dct['p2_coapplicant_address_data_is'] = True
                                            dct['p2_coapplicant_permant_address_proof'] = coapp['address_type']
                                        if 'address_document' in coapp:
                                            if 'base64,' in coapp['address_document']:
                                                if "pdf" in coapp['address_document'].split('base64,')[0]:
                                                    dct['p2_coapplicant_permant_address_proof_photo_pdf'] = coapp['address_document'].split('base64,')[1].replace(" ", "+")
                                                else:
                                                    dct['p2_coapplicant_permant_address_proof_photo'] = coapp['address_document'].split('base64,')[1].replace(" ", "+")
                                        if 'address_pincode' in coapp:
                                            dct['p2_coapplicant_permant_pin_code'] = coapp['address_pincode']
                                        if 'address_area' in coapp:
                                            dct['p2_coapplicant_permant_street_lane'] = coapp['address_area']
                                        if 'address_house' in coapp:
                                            dct['p2_coapplicant_permant_flat_house'] = coapp['address_house']
                                        if 'address_state' in coapp:
                                            dct['p2_coapplicant_permant_state'] = coapp['address_state']
                                        if 'address_city' in coapp:
                                            dct['p2_coapplicant_permant_city'] = coapp['address_city']
                                    first_co_loop = first_co_loop + 1                                   

                        if co_applicant_1 == 2:
                            if "p3_co_applicant_data" in co_applicant:
                                dct["p3_co_applicant_data"] = True
                                dct['p3_co_applicant_data'] = co_applicant['p3_co_applicant_data']
                            if "applicant_relation" in co_applicant:
                                dct['p3_relationship_with_applicant'] = co_applicant['applicant_relation']
                            if "applicant_is" in co_applicant:
                                dct['p3_co_applicant_is'] = co_applicant['applicant_is']
                            coapplicant3_first = ""
                            coapplicant3_last = ""
                            if "applicant_first_name" in co_applicant:
                                coapplicant3_first = co_applicant['applicant_first_name']
                            if "applicant_last_name" in co_applicant:
                                coapplicant3_last = co_applicant['applicant_last_name']

                            if "applicant_additional_income" in co_applicant:
                                _logger.info("webhookbankstatement###########****************%s" %co_applicant["applicant_additional_income"])
                                dct["p3_business_co_aaplicant_data_is"] = True
                                data_co_applicant = 0
                                for co_applicant_additional_income in co_applicant['applicant_additional_income']:
                                    if data_co_applicant == 0:
                                        if 'income_amount' in co_applicant_additional_income:
                                            dct['p_coapplicant_business_additional_amount'] = co_applicant_additional_income['income_amount']
                                        if 'income_source' in co_applicant_additional_income:
                                            dct['p_coapplicant_business_additional_source'] = co_applicant_additional_income['income_source']
                                    if data_co_applicant == 1:
                                        if 'income_amount' in co_applicant_additional_income:
                                            dct['p2_coapplicant_business_additional_amount'] = co_applicant_additional_income['income_amount']
                                        if 'income_source' in co_applicant_additional_income:
                                            dct['p2_coapplicant_business_additional_source'] = co_applicant_additional_income['income_source']
                                    data_co_applicant = data_co_applicant + 1        

                            if 'applicant_first_name' in co_applicant:
                                dct["p3_co_applicant_data"] = True
                                coapplicant3_name = coapplicant3_first + " " + coapplicant3_last
                                dct['p3_co_applicant_name'] = coapplicant3_name
                            if "applicant_gender" in co_applicant:
                                dct["p3_co_applicant_data"] = True
                                dct['p3_co_applicant_gender'] = co_applicant['applicant_gender'].lower()
                            if "applicant_marital_status" in co_applicant:
                                dct['p3_co_applicant_marital_status'] = co_applicant['applicant_marital_status']
                            if "applicant_father_husband_name" in co_applicant:
                                dct['p3_co_applicant_father_husband_name'] = co_applicant['applicant_father_husband_name']
                            if "applicant_educational_qualification" in co_applicant:
                                dct['p3_co_applicant_educational_qualification'] = co_applicant['applicant_educational_qualification']
                            if "applicant_email_id" in co_applicant:
                                dct['p3_co_applicant_personal_email_d'] = co_applicant['applicant_email_id']
                            if "applicant_phone" in co_applicant:
                                dct['p3_co_applicant_mobile_number'] = co_applicant['applicant_phone']

                            if "applicant_current_address_document_type" in co_applicant:
                                dct['p3_kyc_coapplicant_data_is'] = True
                                dct['p3_kyc_coapplicant_type_of_document'] = co_applicant['applicant_current_address_document_type']
                            if 'applicant_current_address_document_front' in co_applicant:
                                dct['p3_kyc_coapplicant_data_is'] = True
                                if 'base64,' in co_applicant['applicant_current_address_document_front']:
                                    if "pdf" in co_applicant['applicant_current_address_document_front'].split('base64,')[0]:
                                        dct['p3_kyc_coapplicant_current_address_residence_proof_front_pdf'] = co_applicant['applicant_current_address_document_front'].split('base64,')[1].replace(" ", "+")
                                    else:
                                        dct['p3_kyc_coapplicant_current_address_residence_proof_front'] = co_applicant['applicant_current_address_document_front'].split('base64,')[1].replace(" ", "+") 
                            if 'applicant_current_address_document_back' in co_applicant:
                                dct['p3_kyc_coapplicant_data_is'] = True
                                if 'base64,' in co_applicant['applicant_current_address_document_back']:
                                    if "pdf" in co_applicant['applicant_current_address_document_back'].split('base64,')[0]:
                                        dct['p3_kyc_coapplicant_current_address_residence_proof_back_pdf'] = co_applicant['applicant_current_address_document_back'].split('base64,')[1].replace(" ", "+")
                                    else:
                                        dct['p3_kyc_coapplicant_current_address_residence_proof_back'] = co_applicant['applicant_current_address_document_back'].split('base64,')[1].replace(" ", "+") 
                            if 'applicant_pan_card_document' in co_applicant:
                                if 'base64,' in co_applicant['applicant_pan_card_document']:
                                    if "pdf" in co_applicant['applicant_pan_card_document'].split('base64,')[0]:
                                        dct['p3_kyc_coapplicant_current_pan_card_photo_pdf'] = co_applicant['applicant_pan_card_document'].split('base64,')[1].replace(" ", "+")
                                    else:
                                        dct['p3_kyc_coapplicant_current_pan_card_photo'] = co_applicant['applicant_pan_card_document'].split('base64,')[1].replace(" ", "+")                
                            # if "applicant_current_address_document_front" in co_applicant:
                            #     dct['p3_kyc_coapplicant_current_address_residence_proof_front'] = co_applicant['applicant_current_address_document_front']
                            # if "applicant_current_address_document_back" in co_applicant:
                            #     dct['p3_kyc_coapplicant_current_address_residence_proof_back'] = co_applicant['applicant_current_address_document_back']
                            # if "applicant_pan_card_document" in co_applicant:
                            #     dct['p3_kyc_coapplicant_current_pan_card_photo'] = co_applicant['applicant_pan_card_document']
                            if "applicant_profession" in co_applicant:
                                dct['p3_business_co_aaplicant_applicant_profession'] = co_applicant["applicant_profession"]   
                            if "applicant_pan_number" in co_applicant:
                                dct['p3_kyc_coapplicant_current_pan_number'] = co_applicant['applicant_pan_number']
                            if "applicant_date_of_birth" in co_applicant:
                                dct['p3_kyc_coapplicant_current_date_of_birth'] = co_applicant['applicant_date_of_birth']
                            p_business_co_aaplicant_year_in_current_job_year = 0
                            p_business_co_aaplicant_year_in_current_job_month = 0
                            if 'applicant_total_exp_current_role' in co_applicant:
                                p_business_co_aaplicant_year_in_current_job_year = float(co_applicant['applicant_total_exp_current_role'])
                            if 'p3_business_co_aaplicant_year_in_current_job_month' in co_applicant:
                                p_business_co_aaplicant_year_in_current_job_month = float(co_applicant['p3_business_co_aaplicant_year_in_current_job_month']) / 12       
                            if 'applicant_total_exp_current_role' in co_applicant:
                                dct['p3_business_co_aaplicant_year_in_current_job_year_month'] = p_business_co_aaplicant_year_in_current_job_year + p_business_co_aaplicant_year_in_current_job_month
                            
                            p_busness_co_aaplicant_total_work_experieance_year = 0
                            p_busness_co_aaplicant_total_work_experieance_month = 0
                            if 'applicant_total_exp' in co_applicant:
                                p_busness_co_aaplicant_total_work_experieance_year = float(co_applicant['applicant_total_exp'])
                            if 'p3_busness_co_aaplicant_total_work_experieance_month' in co_applicant:
                                p_busness_co_aaplicant_total_work_experieance_month = float(co_applicant['p3_busness_co_aaplicant_total_work_experieance_month']) / 12

                            if 'applicant_total_exp' in co_applicant:
                                dct['p3_business_co_aaplicant_data_is'] = True
                                dct['p3_busness_co_aaplicant_total_work_experieance'] = p_busness_co_aaplicant_total_work_experieance_year + p_busness_co_aaplicant_total_work_experieance_month
                            if 'applicant_monthly_net_salary' in co_applicant:
                                dct['p3_business_co_aaplicant_data_is'] = True
                                dct['p3_busness_co_aaplicant_net_monthly_salary'] = co_applicant['applicant_monthly_net_salary']
                            if 'applicant_monthly_gross_salary' in co_applicant:
                                dct['p3_business_co_aaplicant_gross_monthly_salary'] = co_applicant['applicant_monthly_gross_salary']
                            if 'applicant_employment_type' in co_applicant:
                                dct['p3_business_co_aaplicant_data_is'] = True
                                dct['p3_business_co_aaplicant_employment_type'] = co_applicant['applicant_employment_type']
                            if 'applicant_current_organization_name' in co_applicant:
                                dct['p3_business_co_aaplicant_orginization_name'] = co_applicant['applicant_current_organization_name']
                            if 'applicant_designation' in co_applicant:
                                dct['p3_business_co_aaplicant_data_is'] = True
                                dct['p3_business_co_aaplicant_designation'] = co_applicant['applicant_designation']
                            if 'applicant_department' in co_applicant:
                                dct['p3_business_co_aaplicant_department'] = co_applicant['applicant_department'] 
                            if 'applicant_professional_receipts' in co_applicant:
                                dct['p3_business_co_aaplicant_gross_professional_receipt'] = co_applicant['applicant_professional_receipts']
                            if 'applicant_employer_name' in co_applicant:
                                dct['p3_busness_co_aaplicant_business_name'] = co_applicant['applicant_employer_name']
                            if 'business_name' in co_applicant:
                                dct['p3_busness_co_aaplicant_business_name'] = co_applicant['business_name']    
                            if 'applicant_role' in co_applicant:
                                dct['p3_business_co_aaplicant_data_is'] = True
                                dct['p3_busness_co_aaplicant_coaaplicant_is_a'] = co_applicant['applicant_role']
                            if 'applicant_is' in co_applicant:
                                dct['p3_business_co_aaplicant_data_is'] = True
                                dct['p3_busness_co_aaplicant_coaaplicant_is_a'] = co_applicant['applicant_is']    

                                
                            if 'p_business_co_aaplicant_constitution' in co_applicant:
                                dct['p3_business_co_aaplicant_constitution'] = co_applicant['p_business_co_aaplicant_constitution']
                            if 'p_busness_co_aaplicant_amount' in co_applicant:
                                dct['p3_busness_co_aaplicant_amount'] = co_applicant['p3_busness_co_aaplicant_amount']
                            if 'applicant_share_holding_percentage' in co_applicant:
                                dct['p3_busness_co_aaplicant_share_holding'] = co_applicant['applicant_share_holding_percentage']
                            if 'applicant_monthly_renumeration' in co_applicant:
                                dct['p3_business_co_aaplicant_monthly_renumeration'] = co_applicant['applicant_monthly_renumeration']
                            if 'applicant_annual_income' in co_applicant:
                                dct['p3_busness_co_aaplicant_annual_income'] = co_applicant['applicant_annual_income']
                            
                            # if "applicant_business_details" in co_applicant:
                            #     applicant_business_detail = co_applicant['applicant_business_details']
                            if 'business_current_year_profit_after_tax' in co_applicant:
                                dct['p3_business_co_aaplicant_data_is'] = True
                                dct['p3_busness_co_aaplicant_profit_after_tax_after_current_year'] = co_applicant['business_current_year_profit_after_tax']
                            if 'business_current_year_turnover' in co_applicant:
                                dct['p3_business_co_aaplicant_current_year_turnover'] = co_applicant['business_current_year_turnover']
                            if 'applicant_profit_percentage' in co_applicant:
                                dct['p3_business_co_aaplicant_data_is'] = True
                                dct['p3_busness_co_aaplicant_share_in_profit'] = co_applicant['applicant_profit_percentage']
                            if 'business_previous_year_profit_after_tax' in co_applicant:
                                dct['p3_busness_co_aaplicant_profit_after_tax_previous_year'] = co_applicant['business_previous_year_profit_after_tax']
                            if 'business_previous_year_turnover' in co_applicant:
                                dct['p3_business_co_aaplicant_previous_year_turn_over'] = co_applicant['business_previous_year_turnover']
                            if 'p3_business_co_aaplicant_source' in co_applicant:
                                dct['p3_business_co_aaplicant_data_is'] = True
                                dct['p3_business_co_aaplicant_source'] = co_applicant['p3_business_co_aaplicant_source']       
                            if "address" in co_applicant:
                                first_co_loop = 0
                                for coapp in co_applicant['address']:   
                                    if "address_type" in coapp and coapp["address_type"] == "CURRENT": 
                                        if 'address_residence_type' in coapp:
                                            dct['p3_coapplicant_address_residence_owner_rent'] = coapp['address_residence_type']
                                        if 'p_coapplicant_address_number_of_year_in_current_residence' in coapp:
                                            dct['p3_coapplicant_address_data_is'] = True
                                            dct['p3_coapplicant_address_number_of_year_in_current_residence'] = coapp['p_coapplicant_address_number_of_year_in_current_residence']
                                        if 'address_house' in coapp:
                                            dct['p3_coapplicant_address_flat_house'] = coapp['address_house']
                                        if 'address_area' in coapp:
                                            dct['p3_coapplicant_address_street_lane'] = coapp['address_area']
                                        if 'address_city' in coapp:
                                            dct['p3_coapplicant_address_data_is'] = True
                                            dct['p3_coapplicant_address_city'] = coapp['address_city']
                                        if 'address_state' in coapp:
                                            dct['p3_coapplicant_address_data_is'] = True
                                            dct['p3_coapplicant_address_state'] = coapp['address_state']
                                        if "address_pincode" in coapp:
                                            dct['p3_coapplicant_pincode'] = coapp['address_pincode'] 
                                    if "address_type" in coapp and coapp["address_type"] == "PERMANENT":    
                                        if 'address_type' in coapp:
                                            dct['p3_coapplicant_address_data_is'] = True
                                            dct['p3_coapplicant_permant_address_proof'] = coapp['address_type']
                                        if 'address_document' in coapp:
                                            if 'base64,' in coapp['address_document']:
                                                if "pdf" in coapp['address_document'].split('base64,')[0]:
                                                    dct['p3_coapplicant_permant_address_proof_photo_pdf'] = coapp['address_document'].split('base64,')[1].replace(" ", "+")
                                                else:
                                                    dct['p3_coapplicant_permant_address_proof_photo'] = coapp['address_document'].split('base64,')[1].replace(" ", "+")
                                        if 'address_pincode' in coapp:
                                            dct['p3_coapplicant_permant_pin_code'] = coapp['address_pincode']
                                        if 'address_area' in coapp:
                                            dct['p3_coapplicant_permant_street_lane'] = coapp['address_area']
                                        if 'address_house' in coapp:
                                            dct['p3_coapplicant_permant_flat_house'] = coapp['address_house']
                                        if 'address_state' in coapp:
                                            dct['p3_coapplicant_permant_state'] = coapp['address_state']
                                        if 'address_city' in coapp:
                                            dct['p3_coapplicant_permant_city'] = coapp['address_city']
                                    first_co_loop = first_co_loop + 1          
                        co_applicant_1 = co_applicant_1 + 1                    


                            

                        if "p2_business_co_aaplicant_gross_professional_receipt" in co_applicant:
                            dct['p2_business_co_aaplicant_gross_professional_receipt'] = co_applicant['p2_business_co_aaplicant_gross_professional_receipt']
                        if "p2_busness_co_aaplicant_business_name" in co_applicant:
                            dct['p2_busness_co_aaplicant_business_name'] = co_applicant['p2_busness_co_aaplicant_business_name']
                        if "p2_busness_co_aaplicant_coaaplicant_is_a" in co_applicant:
                            dct['p2_busness_co_aaplicant_coaaplicant_is_a'] = co_applicant['p2_busness_co_aaplicant_coaaplicant_is_a']
                        if "p2_business_co_aaplicant_constitution" in co_applicant:
                            dct['p2_business_co_aaplicant_constitution'] = co_applicant['p2_business_co_aaplicant_constitution']
                        if "p2_busness_co_aaplicant_amount" in co_applicant:
                            dct['p2_busness_co_aaplicant_amount'] = co_applicant['p2_busness_co_aaplicant_amount']
                        if "p2_busness_co_aaplicant_share_holding" in co_applicant:
                            dct['p2_busness_co_aaplicant_share_holding'] = co_applicant['p2_busness_co_aaplicant_share_holding']
                        if "p2_business_co_aaplicant_monthly_renumeration" in co_applicant:
                            dct['p2_business_co_aaplicant_monthly_renumeration'] = co_applicant['p2_business_co_aaplicant_monthly_renumeration']
                        if "p2_busness_co_aaplicant_annual_income" in co_applicant:
                            dct['p2_busness_co_aaplicant_annual_income'] = co_applicant['p2_busness_co_aaplicant_annual_income']
                        if "p2_busness_co_aaplicant_profit_after_tax_after_current_year" in co_applicant:
                            dct['p2_busness_co_aaplicant_profit_after_tax_after_current_year'] = co_applicant['p2_busness_co_aaplicant_profit_after_tax_after_current_year']
                        if "p2_business_co_aaplicant_current_year_turnover" in co_applicant:
                            dct['p2_business_co_aaplicant_current_year_turnover'] = co_applicant['p2_business_co_aaplicant_current_year_turnover']
                        if "p2_busness_co_aaplicant_share_in_profit" in co_applicant:
                            dct['p2_busness_co_aaplicant_share_in_profit'] = co_applicant['p2_busness_co_aaplicant_share_in_profit']
                        if "p2_busness_co_aaplicant_profit_after_tax_previous_year" in co_applicant:
                            dct['p2_busness_co_aaplicant_profit_after_tax_previous_year'] = co_applicant['p2_busness_co_aaplicant_profit_after_tax_previous_year']
                        if "p2_business_co_aaplicant_previous_year_turn_over" in co_applicant:
                            dct['p2_business_co_aaplicant_previous_year_turn_over'] = co_applicant['p2_business_co_aaplicant_previous_year_turn_over']
                        if "p2_business_co_aaplicant_source" in co_applicant:
                            dct['p2_business_co_aaplicant_source'] = co_applicant['p2_business_co_aaplicant_source']
                        if "p3_business_co_aaplicant_gross_professional_receipt" in co_applicant:
                            dct['p3_business_co_aaplicant_gross_professional_receipt'] = co_applicant['p3_business_co_aaplicant_gross_professional_receipt']
                        if "p3_busness_co_aaplicant_business_name" in co_applicant:
                            dct['p3_busness_co_aaplicant_business_name'] = co_applicant['p3_busness_co_aaplicant_business_name']
                        if "p3_busness_co_aaplicant_coaaplicant_is_a" in co_applicant:
                            dct['p3_busness_co_aaplicant_coaaplicant_is_a'] = co_applicant['p3_busness_co_aaplicant_coaaplicant_is_a']
                        if "p3_business_co_aaplicant_constitution" in co_applicant:
                            dct['p3_business_co_aaplicant_constitution'] = co_applicant['p3_business_co_aaplicant_constitution']
                        if "p3_busness_co_aaplicant_amount" in co_applicant:
                            dct['p3_busness_co_aaplicant_amount'] = co_applicant['p3_busness_co_aaplicant_amount']
                        if "p3_busness_co_aaplicant_share_holding" in co_applicant:
                            dct['p3_busness_co_aaplicant_share_holding'] = co_applicant['p3_busness_co_aaplicant_share_holding']
                        if "p3_business_co_aaplicant_monthly_renumeration" in co_applicant:
                            dct['p3_business_co_aaplicant_monthly_renumeration'] = co_applicant['p3_business_co_aaplicant_monthly_renumeration']
                        if "p3_busness_co_aaplicant_annual_income" in co_applicant:
                            dct['p3_busness_co_aaplicant_annual_income'] = co_applicant['p3_busness_co_aaplicant_annual_income']
                        if "p3_busness_co_aaplicant_profit_after_tax_after_current_year" in co_applicant:
                            dct['p3_busness_co_aaplicant_profit_after_tax_after_current_year'] = co_applicant['p3_busness_co_aaplicant_profit_after_tax_after_current_year']
                        if "p3_business_co_aaplicant_current_year_turnover" in co_applicant:
                            dct['p3_business_co_aaplicant_current_year_turnover'] = co_applicant['p3_business_co_aaplicant_current_year_turnover']
                        if "p3_busness_co_aaplicant_share_in_profit" in co_applicant:
                            dct['p3_busness_co_aaplicant_share_in_profit'] = co_applicant['p3_busness_co_aaplicant_share_in_profit']
                        if "p3_busness_co_aaplicant_profit_after_tax_previous_year" in co_applicant:
                            dct['p3_busness_co_aaplicant_profit_after_tax_previous_year'] = co_applicant['p3_busness_co_aaplicant_profit_after_tax_previous_year']
                        if "p3_business_co_aaplicant_previous_year_turn_over" in co_applicant:
                            dct['p3_business_co_aaplicant_previous_year_turn_over'] = co_applicant['p3_business_co_aaplicant_previous_year_turn_over']
                        if "p3_business_co_aaplicant_source" in co_applicant:
                            dct['p3_business_co_aaplicant_source'] = co_applicant['p3_business_co_aaplicant_source']           
                        



                        if "credit_cards" in co_applicant:
                            for credit_card in co_applicant["credit_cards"]: 
                                if "cc_current_outstanding_amount" in credit_card:
                                    dct['p3_coapplicant_obligation_credit_card'] = True
                                    dct['p3_coapplicant_obligation_current_credit_out_standing_amount'] = credit_card['cc_current_outstanding_amount']
                                if "cc_bank_id" in credit_card:
                                    dct['p3_coapplicant_obligation_credit_card'] = True
                                    dct['p3_coapplicant_obligation_credit_bank_name'] = credit_card['cc_bank_id']
                                if "cc_credit_limit" in credit_card:
                                    dct['p3_coapplicant_obligation_credit_card'] = True
                                    dct['p3_coapplicant_obligation_credit_limit'] = credit_card['cc_credit_limit']
                if "co_applicant" in kw:
                    looppings = 0
                    for co_applicant in kw['co_applicant']:
                        if "accounts" in co_applicant and looppings == 0:
                            coapp_bank = 0
                            for bank_detail in co_applicant["accounts"]:
                                if coapp_bank == 0:  
                                    if 'account_bank_id' in bank_detail:
                                        dct['p_coapplicant_bank_data_is'] = True
                                        dct['p_coapplicant_bank_select_bank'] = bank_detail['account_bank_id']
                                    if 'account_type' in bank_detail:
                                        dct['p_coapplicant_bank_data_is'] = True
                                        dct['p_coapplicant_bank_details_account_type'] = bank_detail['account_type']
                                    # if 'account_statement_document' in bank_detail:
                                    #     dct['p_coapplicant_bank_data_is'] = True
                                    #     dct['p_coapplicant_bank_details_upload_statement_past_month'] = bank_detail['account_statement_document']
                                    if 'account_statement_document' in bank_details:
                                        dct['p_coapplicant_bank_data_is'] = True
                                        if 'base64,' in bank_details['account_statement_document']:
                                            if "pdf" in bank_details['account_statement_document'].split('base64,')[0]:
                                                dct['p_coapplicant_bank_details_upload_statement_past_month_pdf'] = bank_details['account_statement_document'].split('base64,')[1].replace(" ", "+")
                                            else:
                                                dct['p_coapplicant_bank_details_upload_statement_past_month'] = bank_details['account_statement_document'].split('base64,')[1].replace(" ", "+")       
                                    if 'account_statement_document_password_protected' in bank_detail:
                                        dct['p_coapplicant_bank_is_bank_statement_is_password_protected'] = bank_detail['account_statement_document_password_protected']
                                    if 'account_statement_document_password' in bank_detail:
                                        dct['p_coapplicant_bank_password'] = bank_detail['account_statement_document_password']
                                    
                                if coapp_bank == 1:
                                    if "account_bank_id" in bank_detail:
                                        dct['pbl2_coapplicant_bank_data_is'] = True
                                        dct['pbl2_coapplicant_bank_select_bank'] = bank_detail['account_bank_id']
                                    if "account_type" in bank_detail:
                                        dct['pbl2_coapplicant_bank_data_is'] = True
                                        dct['pbl2_coapplicant_bank_details_account_type'] = bank_detail['account_type']
                                    # if "account_statement_document" in bank_detail:
                                    #     dct['pbl2_coapplicant_bank_data_is'] = True
                                    #     dct['pbl2_coapplicant_bank_details_upload_statement_past_month'] = bank_detail['account_statement_document']

                                    if 'account_statement_document' in bank_details:
                                        dct['pbl2_coapplicant_bank_data_is'] = True
                                        if 'base64,' in bank_details['account_statement_document']:
                                            if "pdf" in bank_details['account_statement_document'].split('base64,')[0]:
                                                dct['pbl2_coapplicant_bank_details_upload_statement_past_month_pdf'] = bank_details['account_statement_document'].split('base64,')[1].replace(" ", "+")
                                            else:
                                                dct['pbl2_coapplicant_bank_details_upload_statement_past_month'] = bank_details['account_statement_document'].split('base64,')[1].replace(" ", "+") 
                                                    
                                    if "account_statement_document_password_protected" in bank_detail:
                                        dct['pbl2_coapplicant_bank_is_bank_statement_is_password_protected'] = bank_detail['account_statement_document_password_protected']
                                    if "account_statement_document_password" in bank_detail:
                                        dct['pbl2_coapplicant_bank_password'] = bank_detail['account_statement_document_password']
                                    
                                if coapp_bank == 2:
                                    if "account_bank_id" in bank_detail:
                                        dct['pbl3_coapplicant_bank_select_bank'] = bank_detail['account_bank_id']
                                    if "account_type" in bank_detail:
                                        dct['pbl3_coapplicant_bank_data_is'] = True
                                        dct['pbl3_coapplicant_bank_details_account_type'] = bank_detail['account_type']
                                    # if "account_statement_document" in bank_detail:
                                    #     dct['pbl3_coapplicant_bank_data_is'] = True
                                    #     dct['pbl3_coapplicant_bank_details_upload_statement_past_month'] = bank_detail['account_statement_document']
                                    if 'account_statement_document' in bank_details:
                                        dct['pbl3_coapplicant_bank_data_is'] = True
                                        if 'base64,' in bank_details['account_statement_document']:
                                            if "pdf" in bank_details['account_statement_document'].split('base64,')[0]:
                                                dct['pbl3_coapplicant_bank_details_upload_statement_past_month_pdf'] = bank_details['account_statement_document'].split('base64,')[1].replace(" ", "+")
                                            else:
                                                dct['pbl3_coapplicant_bank_details_upload_statement_past_month'] = bank_details['account_statement_document'].split('base64,')[1].replace(" ", "+") 
                                                        
                                    if "account_statement_document_password_protected" in bank_detail:
                                        dct['pbl3_coapplicant_bank_data_is'] = True
                                        dct['pbl3_coapplicant_bank_is_bank_statement_is_password_protected'] = bank_detail['account_statement_document_password_protected']
                                    if "account_statement_document_password" in bank_detail:
                                        dct['pbl3_coapplicant_bank_data_is'] = True
                                        dct['pbl3_coapplicant_bank_password'] = bank_detail['account_statement_document_password']  
                                coapp_bank = coapp_bank + 1
                        if "accounts" in co_applicant and  looppings == 1: 
                            coapp_bank = 0      
                            for bank_detail in co_applicant["accounts"]:
                                if coapp_bank == 0:  
                                    if 'account_bank_id' in bank_detail:
                                        dct['p2_coapplicant_bank_data_is'] = True
                                        dct['p2_coapplicant_bank_select_bank'] = bank_detail['account_bank_id']
                                    if 'account_type' in bank_detail:
                                        dct['p2_coapplicant_bank_data_is'] = True
                                        dct['p2_coapplicant_bank_details_account_type'] = bank_detail['account_type']
                                    # if 'account_statement_document' in bank_detail:
                                    #     dct['p_coapplicant_bank_data_is'] = True
                                    #     dct['p_coapplicant_bank_details_upload_statement_past_month'] = bank_detail['account_statement_document']
                                    if 'account_statement_document' in bank_details:
                                        dct['p2_coapplicant_bank_data_is'] = True
                                        if 'base64,' in bank_details['account_statement_document']:
                                            if "pdf" in bank_details['account_statement_document'].split('base64,')[0]:
                                                dct['p2_coapplicant_bank_details_upload_statement_past_month_pdf'] = bank_details['account_statement_document'].split('base64,')[1].replace(" ", "+")
                                            else:
                                                dct['p2_coapplicant_bank_details_upload_statement_past_month'] = bank_details['account_statement_document'].split('base64,')[1].replace(" ", "+")       
                                    if 'account_statement_document_password_protected' in bank_detail:
                                        dct['p2_coapplicant_bank_is_bank_statement_is_password_protected'] = bank_detail['account_statement_document_password_protected']
                                    if 'account_statement_document_password' in bank_detail:
                                        dct['p2_coapplicant_bank_password'] = bank_detail['account_statement_document_password']
                                    
                                if coapp_bank == 1:
                                    if "account_bank_id" in bank_detail:
                                        dct['pbl22_coapplicant_bank_data_is'] = True
                                        dct['pbl22_coapplicant_bank_select_bank'] = bank_detail['account_bank_id']
                                    if "account_type" in bank_detail:
                                        dct['pbl22_coapplicant_bank_data_is'] = True
                                        dct['pbl22_coapplicant_bank_details_account_type'] = bank_detail['account_type']
                                    # if "account_statement_document" in bank_detail:
                                    #     dct['pbl2_coapplicant_bank_data_is'] = True
                                    #     dct['pbl2_coapplicant_bank_details_upload_statement_past_month'] = bank_detail['account_statement_document']

                                    if 'account_statement_document' in bank_details:
                                        dct['pbl22_coapplicant_bank_data_is'] = True
                                        if 'base64,' in bank_details['account_statement_document']:
                                            if "pdf" in bank_details['account_statement_document'].split('base64,')[0]:
                                                dct['pbl22_coapplicant_bank_details_upload_statement_past_month_pdf'] = bank_details['account_statement_document'].split('base64,')[1].replace(" ", "+")
                                            else:
                                                dct['pbl22_coapplicant_bank_details_upload_statement_past_month'] = bank_details['account_statement_document'].split('base64,')[1].replace(" ", "+") 
                                                    
                                    if "account_statement_document_password_protected" in bank_detail:
                                        dct['pbl22_coapplicant_bank_is_bank_statement_is_password_protected'] = bank_detail['account_statement_document_password_protected']
                                    if "account_statement_document_password" in bank_detail:
                                        dct['pbl22_coapplicant_bank_password'] = bank_detail['account_statement_document_password']
                                    
                                if coapp_bank == 2:
                                    if "account_bank_id" in bank_detail:
                                        dct['pbl32_coapplicant_bank_select_bank'] = bank_detail['account_bank_id']
                                    if "account_type" in bank_detail:
                                        dct['pbl32_coapplicant_bank_data_is'] = True
                                        dct['pbl3_coapplicant_bank_details_account_type'] = bank_detail['account_type']
                                    # if "account_statement_document" in bank_detail:
                                    #     dct['pbl3_coapplicant_bank_data_is'] = True
                                    #     dct['pbl3_coapplicant_bank_details_upload_statement_past_month'] = bank_detail['account_statement_document']
                                    if 'account_statement_document' in bank_details:
                                        dct['pbl32_coapplicant_bank_data_is'] = True
                                        if 'base64,' in bank_details['account_statement_document']:
                                            if "pdf" in bank_details['account_statement_document'].split('base64,')[0]:
                                                dct['pbl32_coapplicant_bank_details_upload_statement_past_month_pdf'] = bank_details['account_statement_document'].split('base64,')[1].replace(" ", "+")
                                            else:
                                                dct['pbl32_coapplicant_bank_details_upload_statement_past_month'] = bank_details['account_statement_document'].split('base64,')[1].replace(" ", "+") 
                                                        
                                    if "account_statement_document_password_protected" in bank_detail:
                                        dct['pbl32_coapplicant_bank_data_is'] = True
                                        dct['pbl32_coapplicant_bank_is_bank_statement_is_password_protected'] = bank_detail['account_statement_document_password_protected']
                                    if "account_statement_document_password" in bank_detail:
                                        dct['pbl32_coapplicant_bank_data_is'] = True
                                        dct['pbl32_coapplicant_bank_password'] = bank_detail['account_statement_document_password']  
                                coapp_bank = coapp_bank + 1
                        if "accounts" in co_applicant and  looppings == 2: 
                            coapp_bank = 0   
                            for bank_detail in co_applicant["accounts"]:
                                if coapp_bank == 0:  
                                    if 'account_bank_id' in bank_detail:
                                        dct['p3_coapplicant_bank_data_is'] = True
                                        dct['p3_coapplicant_bank_select_bank'] = bank_detail['account_bank_id']
                                    if 'account_type' in bank_detail:
                                        dct['p3_coapplicant_bank_data_is'] = True
                                        dct['p3_coapplicant_bank_details_account_type'] = bank_detail['account_type']
                                    # if 'account_statement_document' in bank_detail:
                                    #     dct['p_coapplicant_bank_data_is'] = True
                                    #     dct['p_coapplicant_bank_details_upload_statement_past_month'] = bank_detail['account_statement_document']
                                    if 'account_statement_document' in bank_details:
                                        dct['p3_coapplicant_bank_data_is'] = True
                                        if 'base64,' in bank_details['account_statement_document']:
                                            if "pdf" in bank_details['account_statement_document'].split('base64,')[0]:
                                                dct['p3_coapplicant_bank_details_upload_statement_past_month_pdf'] = bank_details['account_statement_document'].split('base64,')[1].replace(" ", "+")
                                            else:
                                                dct['p3_coapplicant_bank_details_upload_statement_past_month'] = bank_details['account_statement_document'].split('base64,')[1].replace(" ", "+")       
                                    if 'account_statement_document_password_protected' in bank_detail:
                                        dct['p3_coapplicant_bank_is_bank_statement_is_password_protected'] = bank_detail['account_statement_document_password_protected']
                                    if 'account_statement_document_password' in bank_detail:
                                        dct['p3_coapplicant_bank_password'] = bank_detail['account_statement_document_password']
                                    
                                if coapp_bank == 1:
                                    if "account_bank_id" in bank_detail:
                                        dct['pbl23_coapplicant_bank_data_is'] = True
                                        dct['pbl23_coapplicant_bank_select_bank'] = bank_detail['account_bank_id']
                                    if "account_type" in bank_detail:
                                        dct['pbl23_coapplicant_bank_data_is'] = True
                                        dct['pbl23_coapplicant_bank_details_account_type'] = bank_detail['account_type']
                                    # if "account_statement_document" in bank_detail:
                                    #     dct['pbl2_coapplicant_bank_data_is'] = True
                                    #     dct['pbl2_coapplicant_bank_details_upload_statement_past_month'] = bank_detail['account_statement_document']

                                    if 'account_statement_document' in bank_details:
                                        dct['pbl23_coapplicant_bank_data_is'] = True
                                        if 'base64,' in bank_details['account_statement_document']:
                                            if "pdf" in bank_details['account_statement_document'].split('base64,')[0]:
                                                dct['pbl23_coapplicant_bank_details_upload_statement_past_month_pdf'] = bank_details['account_statement_document'].split('base64,')[1].replace(" ", "+")
                                            else:
                                                dct['pbl23_coapplicant_bank_details_upload_statement_past_month'] = bank_details['account_statement_document'].split('base64,')[1].replace(" ", "+") 
                                                    
                                    if "account_statement_document_password_protected" in bank_detail:
                                        dct['pbl23_coapplicant_bank_is_bank_statement_is_password_protected'] = bank_detail['account_statement_document_password_protected']
                                    if "account_statement_document_password" in bank_detail:
                                        dct['pbl23_coapplicant_bank_password'] = bank_detail['account_statement_document_password']
                                    
                                if coapp_bank == 2:
                                    if "account_bank_id" in bank_detail:
                                        dct['pbl33_coapplicant_bank_select_bank'] = bank_detail['account_bank_id']
                                    if "account_type" in bank_detail:
                                        dct['pbl33_coapplicant_bank_data_is'] = True
                                        dct['pbl33_coapplicant_bank_details_account_type'] = bank_detail['account_type']
                                    # if "account_statement_document" in bank_detail:
                                    #     dct['pbl3_coapplicant_bank_data_is'] = True
                                    #     dct['pbl3_coapplicant_bank_details_upload_statement_past_month'] = bank_detail['account_statement_document']
                                    if 'account_statement_document' in bank_details:
                                        dct['pbl33_coapplicant_bank_data_is'] = True
                                        if 'base64,' in bank_details['account_statement_document']:
                                            if "pdf" in bank_details['account_statement_document'].split('base64,')[0]:
                                                dct['pbl33_coapplicant_bank_details_upload_statement_past_month_pdf'] = bank_details['account_statement_document'].split('base64,')[1].replace(" ", "+")
                                            else:
                                                dct['pbl33_coapplicant_bank_details_upload_statement_past_month'] = bank_details['account_statement_document'].split('base64,')[1].replace(" ", "+") 
                                                        
                                    if "account_statement_document_password_protected" in bank_detail:
                                        dct['pbl33_coapplicant_bank_data_is'] = True
                                        dct['pbl33_coapplicant_bank_is_bank_statement_is_password_protected'] = bank_detail['account_statement_document_password_protected']
                                    if "account_statement_document_password" in bank_detail:
                                        dct['pbl33_coapplicant_bank_data_is'] = True
                                        dct['pbl33_coapplicant_bank_password'] = bank_detail['account_statement_document_password']  
                                coapp_bank = coapp_bank + 1
                        looppings = looppings + 1

            
            if 'p_father_husband_name' in kw:
                dct['p_father_husband_name'] = kw['p_father_husband_name']
            if 'p_educational_qualification' in kw:
                dct['p_educational_qualification'] = kw['p_educational_qualification']
            if 'p_marital_status' in kw:
                dct['p_marital_status'] = kw['p_marital_status']
            if 'p_personal_email_id' in kw:
                dct['p_personal_email_id'] = kw['p_personal_email_id']
            if 'p_mobile_number' in kw:
                dct['p_mobile_number'] = kw['p_mobile_number']
            if 'p_relationship_with_applicant' in kw:
                dct['p_relationship_with_applicant'] = kw['p_relationship_with_applicant']
            if 'p_co_applicant_is' in kw:
                dct['p_co_applicant_is'] = kw['p_co_applicant_is']
            if 'p_co_applicant_gender' in kw:
                dct['p_co_applicant_gender'] = kw['p_co_applicant_gender'].lower()
            if 'p_co_applicant_marital_status' in kw:
                dct['p_co_applicant_marital_status'] = kw['p_co_applicant_marital_status']
            if 'p_co_applicant_father_husband_name' in kw:
                dct['p_co_applicant_father_husband_name'] = kw['p_co_applicant_father_husband_name']
            if 'p_co_applicant_educational_qualification' in kw:
                dct['p_co_applicant_educational_qualification'] = kw['p_co_applicant_educational_qualification']
            if 'p_co_applicant_personal_email_d' in kw:
                dct['p_co_applicant_personal_email_d'] = kw['p_co_applicant_personal_email_d']
            if 'p_co_applicant_mobile_number' in kw:
                dct['p_co_applicant_mobile_number'] = kw['p_co_applicant_mobile_number']
            if 'p_kyc_type_of_document' in kw:
                dct['p_kyc_type_of_document'] = kw['p_kyc_type_of_document']
            if 'p_kyc_current_address_residence_proof_front' in kw:
                dct['p_kyc_current_address_residence_proof_front'] = kw['p_kyc_current_address_residence_proof_front']
            if 'p_kyc_current_address_residence_proof_back' in kw:
                dct['p_kyc_current_address_residence_proof_back'] = kw['p_kyc_current_address_residence_proof_back']
            if 'p_kyc_current_pan_card_photo' in kw:
                dct['p_kyc_current_pan_card_photo'] = kw['p_kyc_current_pan_card_photo']
            if 'p_kyc_current_pan_number' in kw:
                dct['p_kyc_current_pan_number'] = kw['p_kyc_current_pan_number']
            if 'p_kyc_current_date_of_birth' in kw:
                dct['p_kyc_current_date_of_birth'] = kw['p_kyc_current_date_of_birth']
            if 'p_kyc_coapplicant_type_of_document' in kw:
                dct['p_kyc_coapplicant_type_of_document'] = kw['p_kyc_coapplicant_type_of_document']
            if 'p_kyc_coapplicant_current_address_residence_proof_front' in kw:
                dct['p_kyc_coapplicant_current_address_residence_proof_front'] = kw['p_kyc_coapplicant_current_address_residence_proof_front']
            if 'p_kyc_coapplicant_current_address_residence_proof_back' in kw:
                dct['p_kyc_coapplicant_current_address_residence_proof_back'] = kw['p_kyc_coapplicant_current_address_residence_proof_back']
            if 'p_kyc_coapplicant_current_pan_card_photo' in kw:
                dct['p_kyc_coapplicant_current_pan_card_photo'] = kw['p_kyc_coapplicant_current_pan_card_photo']
            if 'p_kyc_coapplicant_current_pan_number' in kw:
                dct['p_kyc_coapplicant_current_pan_number'] = kw['p_kyc_coapplicant_current_pan_number']
            if 'p_kyc_coapplicant_current_date_of_birth' in kw:
                dct['p_kyc_coapplicant_current_date_of_birth'] = kw['p_kyc_coapplicant_current_date_of_birth']
            if 'p_address_residence_owner_rent' in kw:
                dct['p_address_residence_owner_rent'] = kw['p_address_residence_owner_rent']
            if 'p_address_number_of_year_in_current_residence' in kw:
                dct['p_address_number_of_year_in_current_residence'] = kw['p_address_number_of_year_in_current_residence']
            if 'p_address_flat_house' in kw:
                dct['p_address_flat_house'] = kw['p_address_flat_house']
            if 'p_address_street_lane' in kw:
                dct['p_address_street_lane'] = kw['p_address_street_lane']
            if 'p_address_city' in kw:
                dct['p_address_city'] = kw['p_address_city']
            if 'p_address_state' in kw:
                dct['p_address_state'] = kw['p_address_state']
            if 'p_permant_address_proof' in kw:
                dct['p_permant_address_proof'] = kw['p_permant_address_proof']
            if 'p_permant_address_proof_photo' in kw:
                dct['p_permant_address_proof_photo'] = kw['p_permant_address_proof_photo']
            if 'p_permant_pin_code' in kw:
                dct['p_permant_pin_code'] = kw['p_permant_pin_code']
            if 'p_permant_street_lane' in kw:
                dct['p_permant_street_lane'] = kw['p_permant_street_lane']
            if 'p_permant_flat_house' in kw:
                dct['p_permant_flat_house'] = kw['p_permant_flat_house']
            if 'p_permant_state' in kw:
                dct['p_permant_state'] = kw['p_permant_state']
            if 'p_permant_city' in kw:
                dct['p_permant_city'] = kw['p_permant_city']
            if 'p_coapplicant_address_residence_owner_rent' in kw:
                dct['p_coapplicant_address_residence_owner_rent'] = kw['p_coapplicant_address_residence_owner_rent']
            if 'p_coapplicant_address_number_of_year_in_current_residence' in kw:
                dct['p_coapplicant_address_number_of_year_in_current_residence'] = kw['p_coapplicant_address_number_of_year_in_current_residence']
            if 'p_coapplicant_address_flat_house' in kw:
                dct['p_coapplicant_address_flat_house'] = kw['p_coapplicant_address_flat_house']
            if 'p_coapplicant_address_banking_upload_passbookstreet_lane' in kw:
                dct['p_coapplicant_address_street_lane'] = kw['p_coapplicant_address_street_lane']
            if 'p_coapplicant_address_city' in kw:
                dct['p_coapplicant_address_city'] = kw['p_coapplicant_address_city']
            if 'p_coapplicant_address_state' in kw:
                dct['p_coapplicant_address_state'] = kw['p_coapplicant_address_state']
            if 'p_coapplicant_permant_address_proof' in kw:
                dct['p_coapplicant_permant_address_proof'] = kw['p_coapplicant_permant_address_proof']
            if 'p_coapplicant_permant_address_proof_photo' in kw:
                dct['p_coapplicant_permant_address_proof_photo'] = kw['p_coapplicant_permant_address_proof_photo']
            if 'p_coapplicant_permant_pin_code' in kw:
                dct['p_coapplicant_permant_pin_code'] = kw['p_coapplicant_permant_pin_code']
            if 'p_coapplicant_permant_street_lane' in kw:
                dct['p_coapplicant_permant_street_lane'] = kw['p_coapplicant_permant_street_lane']
            if 'p_coapplicant_permant_flat_house' in kw:
                dct['p_coapplicant_permant_flat_house'] = kw['p_coapplicant_permant_flat_house']
            if 'p_coapplicant_permant_state' in kw:
                dct['p_coapplicant_permant_state'] = kw['p_coapplicant_permant_state']
            if 'p_coapplicant_permant_city' in kw:
                dct['p_coapplicant_permant_city'] = kw['p_coapplicant_permant_city']
            if 'p_business_name_of_current_orginization' in kw:
                dct['p_business_name_of_current_orginization'] = kw['p_business_name_of_current_orginization']
            if 'p_busness_orginization_type' in kw:
                dct['p_busness_orginization_type'] = kw['p_busness_orginization_type']
            if 'p_busness_industry_type' in kw:
                dct['p_busness_industry_type'] = kw['p_busness_industry_type']
            if 'applicant_employment_type' in kw:
                dct['p_business_employment_type'] = kw['applicant_employment_type']
            if 'p_business_employeement_id_number' in kw:
                dct['p_business_employeement_id_number'] = kw['p_business_employeement_id_number']
            if 'p_business_officail_email_id' in kw:
                dct['p_business_officail_email_id'] = kw['p_business_officail_email_id']
            if 'applicant_monthly_net_salary' in kw:
                dct['p_business_net_monthly_salary'] = kw['applicant_monthly_net_salary']
            if 'applicant_monthly_gross_salary' in kw:
                dct['p_business_gross_monthly_salary'] = kw['applicant_monthly_gross_salary']
            if 'p_business_designation' in kw:
                dct['p_business_designation'] = kw['p_business_designation']
            if 'p_business_department' in kw:
                dct['p_business_department'] = kw['p_business_department']
            p_business_year_in_current_job_year = 0
            p_business_year_in_current_job_month = 0
            if 'applicant_total_exp_current_role' in kw:
                p_business_year_in_current_job_year = float(kw['applicant_total_exp_current_role'])
            if 'p_business_year_in_current_job_month' in kw:
                p_business_year_in_current_job_month = float(kw['p_business_year_in_current_job_month']) / 12

            if 'applicant_total_exp_current_role' in kw:
                dct['p_business_year_in_current_job'] = p_business_year_in_current_job_year  + p_business_year_in_current_job_month
            
            p_business_total_work_experiance_year = 0
            p_business_total_work_experiance_month = 0

            if 'applicant_total_exp' in kw:
                p_business_total_work_experiance_year = float(kw['applicant_total_exp'])
            if 'p_business_total_work_experiance_month' in kw:
                p_business_total_work_experiance_month = float(kw['p_business_total_work_experiance_month']) / 12

            if 'applicant_total_exp' in kw:
                dct['p_business_total_work_experiance'] = p_business_total_work_experiance_year + p_business_total_work_experiance_month
            if 'p_business_additional_amount' in kw:
                dct['p_business_additional_amount'] = kw['p_business_additional_amount']
            if 'p_business_additional_source' in kw:
                dct['p_business_additional_source'] = kw['p_business_additional_source']

            if 'p2_business_additional_amount' in kw:
                dct['p2_business_additional_amount'] = kw['p2_business_additional_amount']
            if 'p2_business_additional_source' in kw:
                dct['p2_business_additional_source'] = kw['p2_business_additional_source']    
            if 'p_business_office_pin_code' in kw:
                dct['p_business_office_pin_code'] = kw['p_business_office_pin_code']
            if 'p_business_office_building_numbr' in kw:
                dct['p_business_office_building_numbr'] = kw['p_business_office_building_numbr']
            if 'p_business_office_street_lane' in kw:
                dct['p_business_office_street_lane'] = kw['p_business_office_street_lane']
            if 'p_business_office_landmark' in kw:
                dct['p_business_office_landmark'] = kw['p_business_office_landmark']
            if 'p_business_office_city' in kw:
                dct['p_business_office_city'] = kw['p_business_office_city']
            if 'p_business_building_office_state' in kw:
                dct['p_business_building_office_state'] = kw['p_business_building_office_state']
            p_business_co_aaplicant_year_in_current_job_year = 0
            p_business_co_aaplicant_year_in_current_job_month = 0
            if 'p_business_co_aaplicant_year_in_current_job_year' in kw:
                p_business_co_aaplicant_year_in_current_job_year = float(kw['p_business_co_aaplicant_year_in_current_job_year'])
            if 'p_business_co_aaplicant_year_in_current_job_month' in kw:
                p_business_co_aaplicant_year_in_current_job_month = float(kw['p_business_co_aaplicant_year_in_current_job_month']) / 12       
            if 'p_business_co_aaplicant_year_in_current_job_year' in kw:
                dct['p_business_co_aaplicant_year_in_current_job_year_month'] = p_business_co_aaplicant_year_in_current_job_year + p_business_co_aaplicant_year_in_current_job_month
            
            p_busness_co_aaplicant_total_work_experieance_year = 0
            p_busness_co_aaplicant_total_work_experieance_month = 0
            if 'p_busness_co_aaplicant_total_work_experieance_year' in kw:
                p_busness_co_aaplicant_total_work_experieance_year = float(kw['p_busness_co_aaplicant_total_work_experieance_year'])
            if 'p_busness_co_aaplicant_total_work_experieance_month' in kw:
                p_busness_co_aaplicant_total_work_experieance_month = float(kw['p_busness_co_aaplicant_total_work_experieance_month']) / 12

            if 'p_busness_co_aaplicant_total_work_experieance_year' in kw:
                dct['p_busness_co_aaplicant_total_work_experieance'] = p_busness_co_aaplicant_total_work_experieance_year + p_busness_co_aaplicant_total_work_experieance_month
            if 'p_busness_co_aaplicant_net_monthly_salary' in kw:
                dct['p_busness_co_aaplicant_net_monthly_salary'] = kw['p_busness_co_aaplicant_net_monthly_salary']
            if 'p_business_co_aaplicant_gross_monthly_salary' in kw:
                dct['p_business_co_aaplicant_gross_monthly_salary'] = kw['p_business_co_aaplicant_gross_monthly_salary']
            if 'p_business_co_aaplicant_employment_type' in kw:
                dct['p_business_co_aaplicant_employment_type'] = kw['p_business_co_aaplicant_employment_type']
            if 'p_business_co_aaplicant_orginization_name' in kw:
                dct['p_business_co_aaplicant_orginization_name'] = kw['p_business_co_aaplicant_orginization_name']
            if 'p_business_co_aaplicant_designation' in kw:
                dct['p_business_co_aaplicant_designation'] = kw['p_business_co_aaplicant_designation']
            if 'p_business_co_aaplicant_department' in kw:
                dct['p_business_co_aaplicant_department'] = kw['p_business_co_aaplicant_department']

            if "p_obligation_loan" in kw:
                dct['p_obligation_loan'] = kw['p_obligation_loan']    
    

            if 'loan_amount' in kw:
                dct['p_obligation_loan_amount'] = kw['loan_amount'] 

            if 'p_obligation_bank_name' in kw:
                dct['p_obligation_bank_name'] = kw['p_obligation_bank_name']
            if 'p_obligation_type_of_loan' in kw:
                dct['p_obligation_type_of_loan'] = kw['p_obligation_type_of_loan']
            if 'p_obligation_account_number' in kw:
                dct['p_obligation_account_number'] = kw['p_obligation_account_number']
            if 'p_obligation_emi' in kw:
                dct['p_obligation_emi'] = kw['p_obligation_emi']
            if 'p_obligation_loan_opening_date' in kw:
                dct['p_obligation_loan_opening_date'] = kw['p_obligation_loan_opening_date']
            if 'p_obligation_tenure' in kw:
                dct['p_obligation_tenure'] = kw['p_obligation_tenure']
            if 'p_obligation_roi' in kw:
                dct['p_obligation_roi'] = kw['p_obligation_roi']
            if 'p_obligation_type_of_security' in kw:
                dct['p_obligation_type_of_security'] = kw['p_obligation_type_of_security']
            if 'p_obligation_current_out_standing_amount' in kw:
                dct['p_obligation_current_out_standing_amount'] = kw['p_obligation_current_out_standing_amount']
            if 'p_obligation_credit_card' in kw:
                dct['p_obligation_credit_card'] = kw['p_obligation_credit_card']
            if 'p_obligation_current_out_standing_amount' in kw:
                dct['p_obligation_current_out_standing_amount'] = kw['p_obligation_current_out_standing_amount']
            if 'p_obligation_bank_name' in kw:
                dct['p_obligation_bank_name'] = kw['p_obligation_bank_name']
            if 'p_obligation_credit_limit' in kw:
                dct['p_obligation_credit_limit'] = kw['p_obligation_credit_limit']
            if 'p_coapplicant_obligation_bank_name' in kw:
                dct['p_coapplicant_obligation_bank_name'] = kw['p_coapplicant_obligation_bank_name']
            if 'p_coapplicant_obligation_type_of_loan' in kw:
                dct['p_coapplicant_obligation_type_of_loan'] = kw['p_coapplicant_obligation_type_of_loan']
            if 'p_coapplicant_obligation_account_number' in kw:
                dct['p_coapplicant_obligation_account_number'] = kw['p_coapplicant_obligation_account_number']
            if 'p_coapplicant_obligation_emi' in kw:
                dct['p_coapplicant_obligation_emi'] = kw['p_coapplicant_obligation_emi']
            if 'p_coapplicant_obligation_loan_opening_date' in kw:
                dct['p_coapplicant_obligation_loan_opening_date'] = kw['p_coapplicant_obligation_loan_opening_date']
            if 'p_coapplicant_obligation_tenure' in kw:
                dct['p_coapplicant_obligation_tenure'] = kw['p_coapplicant_obligation_tenure']
            if 'p_coapplicant_obligation_roi' in kw:
                dct['p_coapplicant_obligation_roi'] = kw['p_coapplicant_obligation_roi']
            if 'p_coapplicant_obligation_type_of_security' in kw:
                dct['p_coapplicant_obligation_type_of_security'] = kw['p_coapplicant_obligation_type_of_security']
            if 'p_coapplicant_obligation_current_out_standing_amount' in kw:
                dct['p_coapplicant_obligation_current_out_standing_amount'] = kw['p_coapplicant_obligation_current_out_standing_amount']
            if 'p_coapplicant_obligation_credit_card' in kw:
                dct['p_coapplicant_obligation_credit_card'] = kw['p_coapplicant_obligation_credit_card']
            if 'p_coapplicant_obligation_current_out_standing_amount' in kw:
                dct['p_coapplicant_obligation_current_out_standing_amount'] = kw['p_coapplicant_obligation_current_out_standing_amount']
            if 'p_coapplicant_obligation_bank_name' in kw:
                dct['p_coapplicant_obligation_bank_name'] = kw['p_coapplicant_obligation_bank_name']
            if 'p_coapplicant_obligation_credit_limit' in kw:
                dct['p_coapplicant_obligation_credit_limit'] = kw['p_coapplicant_obligation_credit_limit']


            if 'p_bank_select_bank' in kw:
                dct['p_bank_select_bank'] = kw['p_bank_select_bank']
            if 'p_bank_details_account_type' in kw:
                dct['p_bank_details_account_type'] = kw['p_bank_details_account_type']
            if 'p_bank_details_upload_statement_past_month' in kw:
                dct['p_bank_details_upload_statement_past_month'] = kw['p_bank_details_upload_statement_past_month']
            if 'p_bank_is_bank_statement_is_password_protected' in kw:
                dct['p_bank_is_bank_statement_is_password_protected'] = kw['p_bank_is_bank_statement_is_password_protected']
            if 'p_bank_password' in kw:
                dct['p_bank_password'] = kw['p_bank_password']

            if "is_bank_1" in kw:
                dct['is_bank_1'] = kw['is_bank_1']
            if "is_bank_3" in kw:
                dct['is_bank_3'] = kw['is_bank_3']    
            if "p2_bank_select_bank" in kw:
                dct['p2_bank_select_bank'] = kw['p2_bank_select_bank']
            if "p2_bank_details_account_type" in kw:
                dct['p2_bank_details_account_type'] = kw['p2_bank_details_account_type']
            if "p2_bank_details_upload_statement_past_month" in kw:
                dct['p2_bank_details_upload_statement_past_month'] = kw['p2_bank_details_upload_statement_past_month']
            if "p2_bank_is_bank_statement_is_password_protected" in kw:
                dct['p2_bank_is_bank_statement_is_password_protected'] = kw['p2_bank_is_bank_statement_is_password_protected']
            if "p2_bank_password" in kw:
                dct['p2_bank_password'] = kw['p2_bank_password']
            if "is_bank_2" in kw:
                dct['is_bank_2'] = kw['is_bank_2']
            if "p3_bank_select_bank" in kw:
                dct['p3_bank_select_bank'] = kw['p3_bank_select_bank']
            if "p3_bank_details_account_type" in kw:
                dct['p3_bank_details_account_type'] = kw['p3_bank_details_account_type']
            if "p3_bank_details_upload_statement_past_month" in kw:
                dct['p3_bank_details_upload_statement_past_month'] = kw['p3_bank_details_upload_statement_past_month']
            if "p3_bank_is_bank_statement_is_password_protected" in kw:
                dct['p3_bank_is_bank_statement_is_password_protected'] = kw['p3_bank_is_bank_statement_is_password_protected']
            if "p3_bank_password" in kw:
                dct['p3_bank_password'] = kw['p3_bank_password']
            

            if 'p_coapplicant_bank_select_bank' in kw:
                dct['p_coapplicant_bank_select_bank'] = kw['p_coapplicant_bank_select_bank']
            if 'p_coapplicant_bank_details_account_type' in kw:
                dct['p_coapplicant_bank_details_account_type'] = kw['p_coapplicant_bank_details_account_type']
            if 'p_coapplicant_bank_details_upload_statement_past_month' in kw:
                dct['p_coapplicant_bank_details_upload_statement_past_month'] = kw['p_coapplicant_bank_details_upload_statement_past_month']
            if 'p_coapplicant_bank_is_bank_statement_is_password_protected' in kw:
                dct['p_coapplicant_bank_is_bank_statement_is_password_protected'] = kw['p_coapplicant_bank_is_bank_statement_is_password_protected']
            if 'p_coapplicant_bank_password' in kw:
                dct['p_coapplicant_bank_password'] = kw['p_coapplicant_bank_password']

            if "pbl2_coapplicant_bank_select_bank" in kw:
                dct['pbl2_coapplicant_bank_select_bank'] = kw['pbl2_coapplicant_bank_select_bank']
            if "pbl2_coapplicant_bank_details_account_type" in kw:
                dct['pbl2_coapplicant_bank_details_account_type'] = kw['pbl2_coapplicant_bank_details_account_type']
            if "pbl2_coapplicant_bank_details_upload_statement_past_month" in kw:
                dct['pbl2_coapplicant_bank_details_upload_statement_past_month'] = kw['pbl2_coapplicant_bank_details_upload_statement_past_month']
            if "pbl2_coapplicant_bank_is_bank_statement_is_password_protected" in kw:
                dct['pbl2_coapplicant_bank_is_bank_statement_is_password_protected'] = kw['pbl2_coapplicant_bank_is_bank_statement_is_password_protected']
            if "pbl2_coapplicant_bank_password" in kw:
                dct['pbl2_coapplicant_bank_password'] = kw['pbl2_coapplicant_bank_password']
            if "pbl3_coapplicant_bank_select_bank" in kw:
                dct['pbl3_coapplicant_bank_select_bank'] = kw['pbl3_coapplicant_bank_select_bank']
            if "pbl3_coapplicant_bank_details_account_type" in kw:
                dct['pbl3_coapplicant_bank_details_account_type'] = kw['pbl3_coapplicant_bank_details_account_type']
            if "pbl3_coapplicant_bank_details_upload_statement_past_month" in kw:
                dct['pbl3_coapplicant_bank_details_upload_statement_past_month'] = kw['pbl3_coapplicant_bank_details_upload_statement_past_month']
            if "pbl3_coapplicant_bank_is_bank_statement_is_password_protected" in kw:
                dct['pbl3_coapplicant_bank_is_bank_statement_is_password_protected'] = kw['pbl3_coapplicant_bank_is_bank_statement_is_password_protected']
            if "pbl3_coapplicant_bank_password" in kw:
                dct['pbl3_coapplicant_bank_password'] = kw['pbl3_coapplicant_bank_password'] 
            if "pbl2_coapplicant_bank_data_is" in kw:
                dct['pbl2_coapplicant_bank_data_is'] = kw['pbl2_coapplicant_bank_data_is']
            if "pbl3_coapplicant_bank_data_is" in kw:
                dct['pbl3_coapplicant_bank_data_is'] = kw['pbl3_coapplicant_bank_data_is']
        
            if "profession_categories_salaried" in kw:
                dct['profession_categories_salaried'] = kw['profession_categories_salaried']
            if "profession_categories_senp" in kw:
                dct['profession_categories_senp'] = kw['profession_categories_senp']
            if "profession_categories_sep" in kw:
                dct['profession_categories_sep'] = kw['profession_categories_sep']
            if "p_business_business_name" in kw:
                dct['p_business_business_name'] = kw['p_business_business_name']
            if "applicant_profession" in kw:
                dct['p_business_profession'] = kw['applicant_profession']
            if "p_business_registration_number" in kw:
                dct['p_business_registration_number'] = kw['p_business_registration_number']
            if "p_business_gstin" in kw:
                dct['p_business_gstin'] = kw['p_business_gstin']
            if "applicant_total_exp_current_role" in kw:
                dct['p_business_years_in_current_profession'] = kw['applicant_total_exp_current_role']
            if "p_business_gross_professional_receipts_as_per_ITR" in kw:
                dct['p_business_gross_professional_receipts_as_per_ITR'] = kw['p_business_gross_professional_receipts_as_per_ITR']
            if "p2_business_gross_professional_receipts_as_per_ITR" in kw:
                dct['p2_business_gross_professional_receipts_as_per_ITR'] = kw['p2_business_gross_professional_receipts_as_per_ITR']
            if "p3_business_gross_professional_receipts_as_per_ITR" in kw:
                dct['p3_business_gross_professional_receipts_as_per_ITR'] = kw['p3_business_gross_professional_receipts_as_per_ITR']
            if "p_business_email_id" in kw:
                dct['p_business_email_id'] = kw['p_business_email_id']
            if "p_business_phone_number" in kw:
                dct['p_business_phone_number'] = kw['p_business_phone_number']
            if "p_business_register_pin_pincode" in kw:
                dct['p_business_register_pin_pincode'] = kw['p_business_register_pin_pincode']
            if "p_business_register_building_number" in kw:
                dct['p_business_register_building_number'] = kw['p_business_register_building_number']
            if "p_business_register_street" in kw:
                dct['p_business_register_street'] = kw['p_business_register_street']
            if "p_business_register_landmark" in kw:
                dct['p_business_register_landmark'] = kw['p_business_register_landmark']
            if "p_business_register_city" in kw:
                dct['p_business_register_city'] = kw['p_business_register_city']
            if "p_business_register_state" in kw:
                dct['p_business_register_state'] = kw['p_business_register_state']
            if "p_business_corporate_register_pin_pincode" in kw:
                dct['p_business_corporate_register_pin_pincode'] = kw['p_business_corporate_register_pin_pincode']
            if "p_business_corporate_register_building_number" in kw:
                dct['p_business_corporate_register_building_number'] = kw['p_business_corporate_register_building_number']
            if "p_business_corporate_register_street" in kw:
                dct['p_business_corporate_register_street'] = kw['p_business_corporate_register_street']
            if "p_business_corporate_register_landmark" in kw:
                dct['p_business_corporate_register_landmark'] = kw['p_business_corporate_register_landmark']
            if "p_business_corporate_register_city" in kw:
                dct['p_business_corporate_register_city'] = kw['p_business_corporate_register_city']
            if "p_business_corporate_register_state" in kw:
                dct['p_business_corporate_register_state'] = kw['p_business_corporate_register_state']   


            if 'p_business_i_am_a' in kw:
                dct['p_business_i_am_a'] = kw['p_business_i_am_a']
            if 'p_business_business_constitution' in kw:
                dct['p_business_business_constitution'] = kw['p_business_business_constitution']
            if 'p_business_monthly_renumeration' in kw:
                dct['p_business_monthly_renumeration'] = kw['p_business_monthly_renumeration']
            if 'p_business_share_holding' in kw:
                dct['p_business_share_holding'] = kw['p_business_share_holding']
            if 'p_business_annual_income' in kw:
                dct['p_business_annual_income'] = kw['p_business_annual_income']
            if 'p_business_share_in_profit' in kw:
                dct['p_business_share_in_profit'] = kw['p_business_share_in_profit']
            if 'p_business_business_name' in kw:
                dct['p_business_business_name'] = kw['p_business_business_name']
            if 'p_business_industry_type' in kw:
                dct['p_business_industry_type'] = kw['p_business_industry_type']
            if 'p_business_industry_sub_class' in kw:
                dct['p_business_industry_sub_class'] = kw['p_business_industry_sub_class']
            if 'p_business_profit_after_tax' in kw:
                dct['p_business_profit_after_tax'] = kw['p_business_profit_after_tax']
            if 'p_business_previous_profit_after_tax' in kw:
                dct['p_business_previous_profit_after_tax'] = kw['p_business_previous_profit_after_tax']
            if 'p_business_current_year_turnover' in kw:
                dct['p_business_current_year_turnover'] = kw['p_business_current_year_turnover']
            if 'p_business_previous_year_turnover' in kw:
                dct['p_business_previous_year_turnover'] = kw['p_business_previous_year_turnover']
            if 'p_business_Cin_number' in kw:
                dct['p_business_Cin_number'] = kw['p_business_Cin_number']
            if 'p_business_gst_number' in kw:
                dct['p_business_gst_number'] = kw['p_business_gst_number']
            if 'p_business_business_pan' in kw:
                dct['p_business_business_pan'] = kw['p_business_business_pan']
            if 'p_business_tin_number' in kw:
                dct['p_business_tin_number'] = kw['p_business_tin_number']
            if 'p_business_tan_number' in kw:
                dct['p_business_tan_number'] = kw['p_business_tan_number']
            if 'p_business_nio_of_partner_director' in kw:
                dct['p_business_nio_of_partner_director'] = kw['p_business_nio_of_partner_director']
            if 'p_business_date_of_incorportaion' in kw:
                dct['p_business_date_of_incorportaion'] = kw['p_business_date_of_incorportaion']
            if 'p_business_business_vintage' in kw:
                dct['p_business_business_vintage'] = kw['p_business_business_vintage']
            if 'p_business_email_id' in kw:
                dct['p_business_email_id'] = kw['p_business_email_id']
            if 'p_business_phn_number' in kw:
                dct['p_business_phn_number'] = kw['p_business_phn_number']
            if 'p_business_year_of_current_business' in kw:
                dct['p_business_year_of_current_business'] = kw['p_business_year_of_current_business']
            if 'p_business_do_you_have_pos' in kw:
                dct['p_business_do_you_have_pos'] = kw['p_business_do_you_have_pos']
            if 'p_business_if_year_what_is_your_monthly_card_swipe' in kw:
                dct['p_business_if_year_what_is_your_monthly_card_swipe'] = kw['p_business_if_year_what_is_your_monthly_card_swipe']

            if 'p_business_co_aaplicant_gross_professional_receipt' in kw:
                dct['p_business_co_aaplicant_gross_professional_receipt'] = kw['p_business_co_aaplicant_gross_professional_receipt']
            if 'p_busness_co_aaplicant_business_name' in kw:
                dct['p_busness_co_aaplicant_business_name'] = kw['p_busness_co_aaplicant_business_name']
            if 'p_busness_co_aaplicant_coaaplicant_is_a' in kw:
                dct['p_busness_co_aaplicant_coaaplicant_is_a'] = kw['p_busness_co_aaplicant_coaaplicant_is_a']
            if 'p_business_co_aaplicant_constitution' in kw:
                dct['p_business_co_aaplicant_constitution'] = kw['p_business_co_aaplicant_constitution']
            if 'p_busness_co_aaplicant_amount' in kw:
                dct['p_busness_co_aaplicant_amount'] = kw['p_busness_co_aaplicant_amount']
            if 'p_busness_co_aaplicant_share_holding' in kw:
                dct['p_busness_co_aaplicant_share_holding'] = kw['p_busness_co_aaplicant_share_holding']
            if 'p_business_co_aaplicant_monthly_renumeration' in kw:
                dct['p_business_co_aaplicant_monthly_renumeration'] = kw['p_business_co_aaplicant_monthly_renumeration']
            if 'p_busness_co_aaplicant_annual_income' in kw:
                dct['p_busness_co_aaplicant_annual_income'] = kw['p_busness_co_aaplicant_annual_income']
            if 'p_busness_co_aaplicant_profit_after_tax_after_current_year' in kw:
                dct['p_busness_co_aaplicant_profit_after_tax_after_current_year'] = kw['p_busness_co_aaplicant_profit_after_tax_after_current_year']
            if 'p_business_co_aaplicant_current_year_turnover' in kw:
                dct['p_business_co_aaplicant_current_year_turnover'] = kw['p_business_co_aaplicant_current_year_turnover']
            if 'p_busness_co_aaplicant_share_in_profit' in kw:
                dct['p_busness_co_aaplicant_share_in_profit'] = kw['p_busness_co_aaplicant_share_in_profit']
            if 'p_busness_co_aaplicant_profit_after_tax_previous_year' in kw:
                dct['p_busness_co_aaplicant_profit_after_tax_previous_year'] = kw['p_busness_co_aaplicant_profit_after_tax_previous_year']
            if 'p_business_co_aaplicant_previous_year_turn_over' in kw:
                dct['p_business_co_aaplicant_previous_year_turn_over'] = kw['p_business_co_aaplicant_previous_year_turn_over']
            if 'p_business_co_aaplicant_source' in kw:
                dct['p_business_co_aaplicant_source'] = kw['p_business_co_aaplicant_source']
            

            if "pl2_coapplicant_obligation_data_is" in kw:
                dct['pl2_coapplicant_obligation_data_is'] = kw['pl2_coapplicant_obligation_data_is']
            if "pl2_coapplicant_obligation_bank_name" in kw:
                dct['pl2_coapplicant_obligation_bank_name'] = kw['pl2_coapplicant_obligation_bank_name']
            if "pl2_coapplicant_obligation_type_of_loan" in kw:
                dct['pl2_coapplicant_obligation_type_of_loan'] = kw['pl2_coapplicant_obligation_type_of_loan']
            if "pl2_coapplicant_obligation_account_number" in kw:
                dct['pl2_coapplicant_obligation_account_number'] = kw['pl2_coapplicant_obligation_account_number']
            if "loan_amount" in kw:
                dct['pl2_coapplicant_obligation_loan_amount'] = kw['loan_amount']    
            if "pl2_coapplicant_obligation_emi" in kw:
                dct['pl2_coapplicant_obligation_emi'] = kw['pl2_coapplicant_obligation_emi']
            if "pl2_coapplicant_obligation_loan_opening_date" in kw:
                dct['pl2_coapplicant_obligation_loan_opening_date'] = kw['pl2_coapplicant_obligation_loan_opening_date']
            if "pl2_coapplicant_obligation_tenure" in kw:
                dct['pl2_coapplicant_obligation_tenure'] = kw['pl2_coapplicant_obligation_tenure']
            if "pl2_coapplicant_obligation_roi" in kw:
                dct['pl2_coapplicant_obligation_roi'] = kw['pl2_coapplicant_obligation_roi']
            if "pl2_coapplicant_obligation_type_of_security" in kw:
                dct['pl2_coapplicant_obligation_type_of_security'] = kw['pl2_coapplicant_obligation_type_of_security']
            if "pl2_coapplicant_obligation_current_out_standing_amount" in kw:
                dct['pl2_coapplicant_obligation_current_out_standing_amount'] = kw['pl2_coapplicant_obligation_current_out_standing_amount']
            if "pl3_coapplicant_obligation_data_is" in kw:
                dct['pl3_coapplicant_obligation_data_is'] = kw['pl3_coapplicant_obligation_data_is']
            if "pl3_coapplicant_obligation_bank_name" in kw:
                dct['pl3_coapplicant_obligation_bank_name'] = kw['pl3_coapplicant_obligation_bank_name']
            if "pl3_coapplicant_obligation_type_of_loan" in kw:
                dct['pl3_coapplicant_obligation_type_of_loan'] = kw['pl3_coapplicant_obligation_type_of_loan']
            if "pl3_coapplicant_obligation_account_number" in kw:
                dct['pl3_coapplicant_obligation_account_number'] = kw['pl3_coapplicant_obligation_account_number']
            if "pl3_coapplicant_obligation_loan_amount" in kw:
                dct['pl3_coapplicant_obligation_loan_amount'] = kw['pl3_coapplicant_obligation_loan_amount']       
            if "pl3_coapplicant_obligation_emi" in kw:
                dct['pl3_coapplicant_obligation_emi'] = kw['pl3_coapplicant_obligation_emi']
            if "pl3_coapplicant_obligation_loan_opening_date" in kw:
                dct['pl3_coapplicant_obligation_loan_opening_date'] = kw['pl3_coapplicant_obligation_loan_opening_date']
            if "pl3_coapplicant_obligation_tenure" in kw:
                dct['pl3_coapplicant_obligation_tenure'] = kw['pl3_coapplicant_obligation_tenure']
            if "pl3_coapplicant_obligation_roi" in kw:
                dct['pl3_coapplicant_obligation_roi'] = kw['pl3_coapplicant_obligation_roi']
            if "pl3_coapplicant_obligation_type_of_security" in kw:
                dct['pl3_coapplicant_obligation_type_of_security'] = kw['pl3_coapplicant_obligation_type_of_security']
            if "pl3_coapplicant_obligation_current_out_standing_amount" in kw:
                dct['pl3_coapplicant_obligation_current_out_standing_amount'] = kw['pl3_coapplicant_obligation_current_out_standing_amount']    


            
            

            if "p3_coapplicant_address_residence_owner_rent" in kw:
                dct['p3_coapplicant_address_residence_owner_rent'] = kw['p3_coapplicant_address_residence_owner_rent']
            if "p3_coapplicant_address_number_of_year_in_current_residence" in kw:
                dct['p3_coapplicant_address_number_of_year_in_current_residence'] = kw['p3_coapplicant_address_number_of_year_in_current_residence']
            if "p3_coapplicant_address_flat_house" in kw:
                dct['p3_coapplicant_address_flat_house'] = kw['p3_coapplicant_address_flat_house']
            if "p3_coapplicant_address_street_lane" in kw:
                dct['p3_coapplicant_address_street_lane'] = kw['p3_coapplicant_address_street_lane']
            if "p3_coapplicant_address_city" in kw:
                dct['p3_coapplicant_address_city'] = kw['p3_coapplicant_address_city']
            if "p3_coapplicant_address_state" in kw:
                dct['p3_coapplicant_address_state'] = kw['p3_coapplicant_address_state']
            if "p3_coapplicant_permant_address_proof" in kw:
                dct['p3_coapplicant_permant_address_proof'] = kw['p3_coapplicant_permant_address_proof']
            if "p3_coapplicant_permant_address_proof_photo" in kw:
                dct['p3_coapplicant_permant_address_proof_photo'] = kw['p3_coapplicant_permant_address_proof_photo']
            if "p3_coapplicant_permant_pin_code" in kw:
                dct['p3_coapplicant_permant_pin_code'] = kw['p3_coapplicant_permant_pin_code']
            if "p3_coapplicant_permant_street_lane" in kw:
                dct['p3_coapplicant_permant_street_lane'] = kw['p3_coapplicant_permant_street_lane']
            if "p3_coapplicant_permant_flat_house" in kw:
                dct['p3_coapplicant_permant_flat_house'] = kw['p3_coapplicant_permant_flat_house']
            if "p3_coapplicant_permant_state" in kw:
                dct['p3_coapplicant_permant_state'] = kw['p3_coapplicant_permant_state']
            if "p3_coapplicant_permant_city" in kw:
                dct['p3_coapplicant_permant_city'] = kw['p3_coapplicant_permant_city']




            if "p2_business_co_aaplicant_year_in_current_job_year_month" in kw:
                dct['p2_business_co_aaplicant_year_in_current_job_year_month'] = kw['p2_business_co_aaplicant_year_in_current_job_year_month']
            p2_busness_co_aaplicant_total_work_experieance_year = 0
            p2_busness_co_aaplicant_total_work_experieance_month = 0
            if 'p2_busness_co_aaplicant_total_work_experieance_year' in kw:
                p2_busness_co_aaplicant_total_work_experieance_year = float(kw['p2_busness_co_aaplicant_total_work_experieance_year'])
            if 'p2_busness_co_aaplicant_total_work_experieance_month' in kw:
                p2_busness_co_aaplicant_total_work_experieance_month = float(kw['p2_busness_co_aaplicant_total_work_experieance_month']) / 12

            if 'p2_busness_co_aaplicant_total_work_experieance_year' in kw:
                dct['p2_busness_co_aaplicant_total_work_experieance'] = p2_busness_co_aaplicant_total_work_experieance_year + p2_busness_co_aaplicant_total_work_experieance_month

            if "p2_busness_co_aaplicant_net_monthly_salary" in kw:
                dct['p2_busness_co_aaplicant_net_monthly_salary'] = kw['p2_busness_co_aaplicant_net_monthly_salary']
            if "p2_business_co_aaplicant_gross_monthly_salary" in kw:
                dct['p2_business_co_aaplicant_gross_monthly_salary'] = kw['p2_business_co_aaplicant_gross_monthly_salary']
            if "p2_business_co_aaplicant_employment_type" in kw:
                dct['p2_business_co_aaplicant_employment_type'] = kw['p2_business_co_aaplicant_employment_type']
            if "p2_business_co_aaplicant_orginization_name" in kw:
                dct['p2_business_co_aaplicant_orginization_name'] = kw['p2_business_co_aaplicant_orginization_name']
            if "p2_business_co_aaplicant_designation" in kw:
                dct['p2_business_co_aaplicant_designation'] = kw['p2_business_co_aaplicant_designation']
            if "p2_business_co_aaplicant_department" in kw:
                dct['p2_business_co_aaplicant_department'] = kw['p2_business_co_aaplicant_department']


            if "p3_business_co_aaplicant_year_in_current_job_year_month" in kw:
                dct['p3_business_co_aaplicant_year_in_current_job_year_month'] = kw['p3_business_co_aaplicant_year_in_current_job_year_month']
            p3_busness_co_aaplicant_total_work_experieance_year = 0
            p3_busness_co_aaplicant_total_work_experieance_month = 0
            if 'p3_busness_co_aaplicant_total_work_experieance_year' in kw:
                p3_busness_co_aaplicant_total_work_experieance_year = float(kw['p3_busness_co_aaplicant_total_work_experieance_year'])
            if 'p3_busness_co_aaplicant_total_work_experieance_month' in kw:
                p3_busness_co_aaplicant_total_work_experieance_month = float(kw['p3_busness_co_aaplicant_total_work_experieance_month']) / 12

            if 'p3_busness_co_aaplicant_total_work_experieance_year' in kw:
                dct['p3_busness_co_aaplicant_total_work_experieance'] = p3_busness_co_aaplicant_total_work_experieance_year + p3_busness_co_aaplicant_total_work_experieance_month

            if "p3_busness_co_aaplicant_net_monthly_salary" in kw:
                dct['p3_busness_co_aaplicant_net_monthly_salary'] = kw['p3_busness_co_aaplicant_net_monthly_salary']
            if "p3_business_co_aaplicant_gross_monthly_salary" in kw:
                dct['p3_business_co_aaplicant_gross_monthly_salary'] = kw['p3_business_co_aaplicant_gross_monthly_salary']
            if "p3_business_co_aaplicant_employment_type" in kw:
                dct['p3_business_co_aaplicant_employment_type'] = kw['p3_business_co_aaplicant_employment_type']
            if "p3_business_co_aaplicant_orginization_name" in kw:
                dct['p3_business_co_aaplicant_orginization_name'] = kw['p3_business_co_aaplicant_orginization_name']
            if "p3_business_co_aaplicant_designation" in kw:
                dct['p3_business_co_aaplicant_designation'] = kw['p3_business_co_aaplicant_designation']
            if "p3_business_co_aaplicant_department" in kw:
                dct['p3_business_co_aaplicant_department'] = kw['p3_business_co_aaplicant_department']


            if "p2_obligation_loan" in kw:
                dct['p2_obligation_loan'] = kw['p2_obligation_loan']
            if "p2_obligation_bank_name" in kw:
                dct['p2_obligation_bank_name'] = kw['p2_obligation_bank_name']
            if "p2_obligation_type_of_loan" in kw:
                dct['p2_obligation_type_of_loan'] = kw['p2_obligation_type_of_loan']
            if "p2_obligation_loan_amount" in kw:
                dct['p2_obligation_loan_amount'] = kw['p2_obligation_loan_amount']
            if "p2_obligation_account_number" in kw:
                dct['p2_obligation_account_number'] = kw['p2_obligation_account_number']
            if "p2_obligation_emi" in kw:
                dct['p2_obligation_emi'] = kw['p2_obligation_emi']
            if "p2_obligation_loan_opening_date" in kw:
                dct['p2_obligation_loan_opening_date'] = kw['p2_obligation_loan_opening_date']
            if "p2_obligation_tenure" in kw:
                dct['p2_obligation_tenure'] = kw['p2_obligation_tenure']
            if "p2_obligation_roi" in kw:
                dct['p2_obligation_roi'] = kw['p2_obligation_roi']
            if "p2_obligation_type_of_security" in kw:
                dct['p2_obligation_type_of_security'] = kw['p2_obligation_type_of_security']
            if "p2_obligation_current_out_standing_amount" in kw:
                dct['p2_obligation_current_out_standing_amount'] = kw['p2_obligation_current_out_standing_amount']
            if "p3_obligation_loan" in kw:
                dct['p3_obligation_loan'] = kw['p3_obligation_loan']
            if "p3_obligation_bank_name" in kw:
                dct['p3_obligation_bank_name'] = kw['p3_obligation_bank_name']
            if "p3_obligation_loan_amount" in kw:
                dct['p3_obligation_loan_amount'] = kw['p3_obligation_loan_amount']
            if "p3_obligation_type_of_loan" in kw:
                dct['p3_obligation_type_of_loan'] = kw['p3_obligation_type_of_loan']
            if "p3_obligation_account_number" in kw:
                dct['p3_obligation_account_number'] = kw['p3_obligation_account_number']
            if "p3_obligation_emi" in kw:
                dct['p3_obligation_emi'] = kw['p3_obligation_emi']
            if "p3_obligation_loan_opening_date" in kw:
                dct['p3_obligation_loan_opening_date'] = kw['p3_obligation_loan_opening_date']
            if "p3_obligation_tenure" in kw:
                dct['p3_obligation_tenure'] = kw['p3_obligation_tenure']
            if "p3_obligation_roi" in kw:
                dct['p3_obligation_roi'] = kw['p3_obligation_roi']
            if "p3_obligation_type_of_security" in kw:
                dct['p3_obligation_type_of_security'] = kw['p3_obligation_type_of_security']
            if "p3_obligation_current_out_standing_amount" in kw:
                dct['p3_obligation_current_out_standing_amount'] = kw['p3_obligation_current_out_standing_amount']
            if "p3_obligation_credit_card" in kw:
                dct['p3_obligation_credit_card'] = kw['p3_obligation_credit_card']
            if "p3_obligation_current_credit_out_standing_amount" in kw:
                dct['p3_obligation_current_credit_out_standing_amount'] = kw['p3_obligation_current_credit_out_standing_amount']
            if "p3_obligation_credit_bank_name" in kw:
                dct['p3_obligation_credit_bank_name'] = kw['p3_obligation_credit_bank_name']
            if "p3_obligation_credit_limit" in kw:
                dct['p3_obligation_credit_limit'] = kw['p3_obligation_credit_limit']
            if "p3_coapplicant_obligation_credit_card" in kw:
                dct['p3_coapplicant_obligation_credit_card'] = kw['p3_coapplicant_obligation_credit_card']
            if "p3_coapplicant_obligation_current_credit_out_standing_amount" in kw:
                dct['p3_coapplicant_obligation_current_credit_out_standing_amount'] = kw['p3_coapplicant_obligation_current_credit_out_standing_amount']
            if "p3_coapplicant_obligation_credit_bank_name" in kw:
                dct['p3_coapplicant_obligation_credit_bank_name'] = kw['p3_coapplicant_obligation_credit_bank_name']
            if "p3_coapplicant_obligation_credit_limit" in kw:
                dct['p3_coapplicant_obligation_credit_limit'] = kw['p3_coapplicant_obligation_credit_limit']
            if "p3_coapplicant_obligation_bank_name" in kw:
                dct['p3_coapplicant_obligation_bank_name'] = kw['p3_coapplicant_obligation_bank_name']
            if "p3_coapplicant_obligation_type_of_loan" in kw:
                dct['p3_coapplicant_obligation_type_of_loan'] = kw['p3_coapplicant_obligation_type_of_loan']
            if "p3_coapplicant_obligation_account_number" in kw:
                dct['p3_coapplicant_obligation_account_number'] = kw['p3_coapplicant_obligation_account_number']
            if 'p3_coapplicant_obligation_loan_amount' in kw:
                dct['p3_coapplicant_obligation_loan_amount'] = kw['p3_coapplicant_obligation_loan_amount']    
            if "p3_coapplicant_obligation_emi" in kw:
                dct['p3_coapplicant_obligation_emi'] = kw['p3_coapplicant_obligation_emi']
            if "p3_coapplicant_obligation_loan_opening_date" in kw:
                dct['p3_coapplicant_obligation_loan_opening_date'] = kw['p3_coapplicant_obligation_loan_opening_date']
            if "p3_coapplicant_obligation_tenure" in kw:
                dct['p3_coapplicant_obligation_tenure'] = kw['p3_coapplicant_obligation_tenure']
            if "p3_coapplicant_obligation_roi" in kw:
                dct['p3_coapplicant_obligation_roi'] = kw['p3_coapplicant_obligation_roi']
            if "p3_coapplicant_obligation_type_of_security" in kw:
                dct['p3_coapplicant_obligation_type_of_security'] = kw['p3_coapplicant_obligation_type_of_security']
            if "p3_coapplicant_obligation_current_out_standing_amount" in kw:
                dct['p3_coapplicant_obligation_current_out_standing_amount'] = kw['p3_coapplicant_obligation_current_out_standing_amount']
            if "p2_coapplicant_obligation_bank_name" in kw:
                dct['p2_coapplicant_obligation_bank_name'] = kw['p2_coapplicant_obligation_bank_name']
            if "p2_coapplicant_obligation_type_of_loan" in kw:
                dct['p2_coapplicant_obligation_type_of_loan'] = kw['p2_coapplicant_obligation_type_of_loan']
            if "p2_coapplicant_obligation_account_number" in kw:
                dct['p2_coapplicant_obligation_account_number'] = kw['p2_coapplicant_obligation_account_number']
            if 'p2_coapplicant_obligation_loan_amount' in kw:
                dct['p2_coapplicant_obligation_loan_amount'] = kw['p2_coapplicant_obligation_loan_amount']       
            if "p2_coapplicant_obligation_emi" in kw:
                dct['p2_coapplicant_obligation_emi'] = kw['p2_coapplicant_obligation_emi']
            if "p2_coapplicant_obligation_loan_opening_date" in kw:
                dct['p2_coapplicant_obligation_loan_opening_date'] = kw['p2_coapplicant_obligation_loan_opening_date']
            if "p2_coapplicant_obligation_tenure" in kw:
                dct['p2_coapplicant_obligation_tenure'] = kw['p2_coapplicant_obligation_tenure']
            if "p2_coapplicant_obligation_roi" in kw:
                dct['p2_coapplicant_obligation_roi'] = kw['p2_coapplicant_obligation_roi']
            if "p2_coapplicant_obligation_type_of_security" in kw:
                dct['p2_coapplicant_obligation_type_of_security'] = kw['p2_coapplicant_obligation_type_of_security']
            if "p2_coapplicant_obligation_current_out_standing_amount" in kw:
                dct['p2_coapplicant_obligation_current_out_standing_amount'] = kw['p2_coapplicant_obligation_current_out_standing_amount']
            if "p2_coapplicant_bank_select_bank" in kw:
                dct['p2_coapplicant_bank_select_bank'] = kw['p2_coapplicant_bank_select_bank']
            if "p2_coapplicant_bank_details_account_type" in kw:
                dct['p2_coapplicant_bank_details_account_type'] = kw['p2_coapplicant_bank_details_account_type']
            if "p2_coapplicant_bank_details_upload_statement_past_month" in kw:
                dct['p2_coapplicant_bank_details_upload_statement_past_month'] = kw['p2_coapplicant_bank_details_upload_statement_past_month']
            if "p2_coapplicant_bank_is_bank_statement_is_password_protected" in kw:
                dct['p2_coapplicant_bank_is_bank_statement_is_password_protected'] = kw['p2_coapplicant_bank_is_bank_statement_is_password_protected']
            if "p2_coapplicant_bank_password" in kw:
                dct['p2_coapplicant_bank_password'] = kw['p2_coapplicant_bank_password']
            if "p3_coapplicant_bank_select_bank" in kw:
                dct['p3_coapplicant_bank_select_bank'] = kw['p3_coapplicant_bank_select_bank']
            if "p3_coapplicant_bank_details_account_type" in kw:
                dct['p3_coapplicant_bank_details_account_type'] = kw['p3_coapplicant_bank_details_account_type']
            if "p3_coapplicant_bank_details_upload_statement_past_month" in kw:
                dct['p3_coapplicant_bank_details_upload_statement_past_month'] = kw['p3_coapplicant_bank_details_upload_statement_past_month']
            if "p3_coapplicant_bank_is_bank_statement_is_password_protected" in kw:
                dct['p3_coapplicant_bank_is_bank_statement_is_password_protected'] = kw['p3_coapplicant_bank_is_bank_statement_is_password_protected']
            if "p3_coapplicant_bank_password" in kw:
                dct['p3_coapplicant_bank_password'] = kw['p3_coapplicant_bank_password']
            if "p2_business_co_aaplicant_gross_professional_receipt" in kw:
                dct['p2_business_co_aaplicant_gross_professional_receipt'] = kw['p2_business_co_aaplicant_gross_professional_receipt']
            if "p2_busness_co_aaplicant_business_name" in kw:
                dct['p2_busness_co_aaplicant_business_name'] = kw['p2_busness_co_aaplicant_business_name']
            if "p2_busness_co_aaplicant_coaaplicant_is_a" in kw:
                dct['p2_busness_co_aaplicant_coaaplicant_is_a'] = kw['p2_busness_co_aaplicant_coaaplicant_is_a']
            if "p2_business_co_aaplicant_constitution" in kw:
                dct['p2_business_co_aaplicant_constitution'] = kw['p2_business_co_aaplicant_constitution']
            if "p2_busness_co_aaplicant_amount" in kw:
                dct['p2_busness_co_aaplicant_amount'] = kw['p2_busness_co_aaplicant_amount']
            if "p2_busness_co_aaplicant_share_holding" in kw:
                dct['p2_busness_co_aaplicant_share_holding'] = kw['p2_busness_co_aaplicant_share_holding']
            if "p2_business_co_aaplicant_monthly_renumeration" in kw:
                dct['p2_business_co_aaplicant_monthly_renumeration'] = kw['p2_business_co_aaplicant_monthly_renumeration']
            if "p2_busness_co_aaplicant_annual_income" in kw:
                dct['p2_busness_co_aaplicant_annual_income'] = kw['p2_busness_co_aaplicant_annual_income']
            if "p2_busness_co_aaplicant_profit_after_tax_after_current_year" in kw:
                dct['p2_busness_co_aaplicant_profit_after_tax_after_current_year'] = kw['p2_busness_co_aaplicant_profit_after_tax_after_current_year']
            if "p2_business_co_aaplicant_current_year_turnover" in kw:
                dct['p2_business_co_aaplicant_current_year_turnover'] = kw['p2_business_co_aaplicant_current_year_turnover']
            if "p2_busness_co_aaplicant_share_in_profit" in kw:
                dct['p2_busness_co_aaplicant_share_in_profit'] = kw['p2_busness_co_aaplicant_share_in_profit']
            if "p2_busness_co_aaplicant_profit_after_tax_previous_year" in kw:
                dct['p2_busness_co_aaplicant_profit_after_tax_previous_year'] = kw['p2_busness_co_aaplicant_profit_after_tax_previous_year']
            if "p2_business_co_aaplicant_previous_year_turn_over" in kw:
                dct['p2_business_co_aaplicant_previous_year_turn_over'] = kw['p2_business_co_aaplicant_previous_year_turn_over']
            if "p2_business_co_aaplicant_source" in kw:
                dct['p2_business_co_aaplicant_source'] = kw['p2_business_co_aaplicant_source']
            if "p3_business_co_aaplicant_gross_professional_receipt" in kw:
                dct['p3_business_co_aaplicant_gross_professional_receipt'] = kw['p3_business_co_aaplicant_gross_professional_receipt']
            if "p3_busness_co_aaplicant_business_name" in kw:
                dct['p3_busness_co_aaplicant_business_name'] = kw['p3_busness_co_aaplicant_business_name']
            if "p3_busness_co_aaplicant_coaaplicant_is_a" in kw:
                dct['p3_busness_co_aaplicant_coaaplicant_is_a'] = kw['p3_busness_co_aaplicant_coaaplicant_is_a']
            if "p3_business_co_aaplicant_constitution" in kw:
                dct['p3_business_co_aaplicant_constitution'] = kw['p3_business_co_aaplicant_constitution']
            if "p3_busness_co_aaplicant_amount" in kw:
                dct['p3_busness_co_aaplicant_amount'] = kw['p3_busness_co_aaplicant_amount']
            if "p3_busness_co_aaplicant_share_holding" in kw:
                dct['p3_busness_co_aaplicant_share_holding'] = kw['p3_busness_co_aaplicant_share_holding']
            if "p3_business_co_aaplicant_monthly_renumeration" in kw:
                dct['p3_business_co_aaplicant_monthly_renumeration'] = kw['p3_business_co_aaplicant_monthly_renumeration']
            if "p3_busness_co_aaplicant_annual_income" in kw:
                dct['p3_busness_co_aaplicant_annual_income'] = kw['p3_busness_co_aaplicant_annual_income']
            if "p3_busness_co_aaplicant_profit_after_tax_after_current_year" in kw:
                dct['p3_busness_co_aaplicant_profit_after_tax_after_current_year'] = kw['p3_busness_co_aaplicant_profit_after_tax_after_current_year']
            if "p3_business_co_aaplicant_current_year_turnover" in kw:
                dct['p3_business_co_aaplicant_current_year_turnover'] = kw['p3_business_co_aaplicant_current_year_turnover']
            if "p3_busness_co_aaplicant_share_in_profit" in kw:
                dct['p3_busness_co_aaplicant_share_in_profit'] = kw['p3_busness_co_aaplicant_share_in_profit']
            if "p3_busness_co_aaplicant_profit_after_tax_previous_year" in kw:
                dct['p3_busness_co_aaplicant_profit_after_tax_previous_year'] = kw['p3_busness_co_aaplicant_profit_after_tax_previous_year']
            if "p3_business_co_aaplicant_previous_year_turn_over" in kw:
                dct['p3_business_co_aaplicant_previous_year_turn_over'] = kw['p3_business_co_aaplicant_previous_year_turn_over']
            if "p3_business_co_aaplicant_source" in kw:
                dct['p3_business_co_aaplicant_source'] = kw['p3_business_co_aaplicant_source']
            if "p2_coapplicant_pincode" in kw:
                dct['p2_coapplicant_pincode'] = kw['p2_coapplicant_pincode']
            if "p3_coapplicant_pincode" in kw:
                dct['p3_coapplicant_pincode'] = kw['p3_coapplicant_pincode']
            if "p_co_applicant_data" in kw:
                dct['p_co_applicant_data'] = kw['p_co_applicant_data']
            if "p2_co_applicant_data" in kw:
                dct['p2_co_applicant_data'] = kw['p2_co_applicant_data']
            if "p3_co_applicant_data" in kw:
                dct['p3_co_applicant_data'] = kw['p3_co_applicant_data']
            if "p_kyc_coapplicant_data_is" in kw:
                dct['p_kyc_coapplicant_data_is'] = kw['p_kyc_coapplicant_data_is']
            if "p2_kyc_coapplicant_data_is" in kw:
                dct['p2_kyc_coapplicant_data_is'] = kw['p2_kyc_coapplicant_data_is']
            if "p3_kyc_coapplicant_data_is" in kw:
                dct['p3_kyc_coapplicant_data_is'] = kw['p3_kyc_coapplicant_data_is']
            if "p_coapplicant_address_data_is" in kw:
                dct['p_coapplicant_address_data_is'] = kw['p_coapplicant_address_data_is']
            if "p2_coapplicant_address_data_is" in kw:
                dct['p2_coapplicant_address_data_is'] = kw['p2_coapplicant_address_data_is']
            if "p3_coapplicant_address_data_is" in kw:
                dct['p3_coapplicant_address_data_is'] = kw['p3_coapplicant_address_data_is']
            if "p_business_co_aaplicant_data_is" in kw:
                dct['p_business_co_aaplicant_data_is'] = kw['p_business_co_aaplicant_data_is']
            if "p2_business_co_aaplicant_data_is" in kw:
                dct['p2_business_co_aaplicant_data_is'] = kw['p2_business_co_aaplicant_data_is']
            if "p3_business_co_aaplicant_data_is" in kw:
                dct['p3_business_co_aaplicant_data_is'] = kw['p3_business_co_aaplicant_data_is']
            if "p_coapplicant_obligation_data_is" in kw:
                dct['p_coapplicant_obligation_data_is'] = kw['p_coapplicant_obligation_data_is']
            if "p2_coapplicant_obligation_data_is" in kw:
                dct['p2_coapplicant_obligation_data_is'] = kw['p2_coapplicant_obligation_data_is']
            if "p3_coapplicant_obligation_data_is" in kw:
                dct['p3_coapplicant_obligation_data_is'] = kw['p3_coapplicant_obligation_data_is']
            if "p_coapplicant_bank_data_is" in kw:
                dct['p_coapplicant_bank_data_is'] = kw['p_coapplicant_bank_data_is']
            if "p2_coapplicant_bank_data_is" in kw:
                dct['p2_coapplicant_bank_data_is'] = kw['p2_coapplicant_bank_data_is']
            if "p3_coapplicant_bank_data_is" in kw:
                dct['p3_coapplicant_bank_data_is'] = kw['p3_coapplicant_bank_data_is']       

            # if 'email' in kw:
            #     dct['name'] = kw['name']
            #     name = kw['name']
            # if 'phone' in kw:
            #     dct['phone'] = kw['phone']
            #     phone = kw['phone'] 
            # if 'email_from' in kw:
            #     dct['email_from'] = kw['email_from']
            #     email = kw['email_from']         

            customer = request.env['res.partner'].sudo().search([('lead_id','=',lead_id)], limit=1)
            loan_lead = request.env['capwise.lead'].sudo().search([('lead_id','=',lead_id),("loan_type", '=',loan_type) ], limit=1)
            
            if not loan_lead:
                dsa = request.env['res.partner'].sudo().search([('phone','=',dsa_phone)],limit=1)
                if not dsa:
                    dsa = dsa.create({
                        'name' : dsa_name,
                        'phone': dsa_phone,
                        })
                dct['dsa_id'] = dsa.id 
                crm_obj = request.env['crm.lead'].sudo().search([('phone','=',dsa_phone)], limit=1)
                if crm_obj and crm_obj.user_id:
                    dct['user_id'] = crm_obj.user_id.id
            if not customer:
                customer = customer.create({
                    'name' : customer_name,
                    'phone': customer_phone,
                    'email' : customer_email,
                    "lead_id" : lead_id
                    })
            dct['partner_id'] = customer.id
            loan_lead = request.env['capwise.lead'].sudo().search([('lead_id','=',lead_id),("loan_type", '=',loan_type)], limit=1)
            if not loan_lead:
                loan_lead = loan_lead.create(dct)
            if loan_lead:
                loan_lead.update(dct)

        args = {'success': True, 'message': 'Success', 'ID':loan_lead.id}
        return args             

            #     if owner_id:
            #         vals['owner'] = owner_id.id
            #     if not crm_obj.classes:
            #         if kw['class']:
            #             if kw['class'] == 'adult':
            #                 vals['classes'] = "Adult"
            #             else:
            #                 vals['classes'] = str(kw['class'])    
            # elif not crm_obj:
            #     if kw['class']:
            #         if kw['class'] == 'adult':
            #             vals['classes'] = "Adult"
            #         else:
            #             vals['classes'] = str(kw['class'])
            #     if owner_id:
            #         vals['owner'] = owner_id.id
            # if user_id:
            #     vals['user_id'] = user_id.id
            # vals['type'] = 'lead'
            # vals['source_id'] = source_id.id
            # if crm_obj:
            #     crm_obj.update(vals)
            #     new_lead = crm_obj
            # else:
            #     new_lead = request.env['crm.lead'].sudo().create(vals)
            # msg = "User Downloaded the Application"
            # new_lead.sudo().message_post(body=msg)
        # args = {'success': True, 'message': 'Success', 'ID':crm_obj.id}
        # return json.dumps(args)

    # @http.route('/capwise_crm/capwise_crm/objects', auth='public')
    # def list(self, **kw):
    #     return http.request.render('capwise_crm.listing', {
    #         'root': '/capwise_crm/capwise_crm',
    #         'objects': http.request.env['capwise_crm.capwise_crm'].search([]),
    #     })

    # @http.route('/capwise_crm/capwise_crm/objects/<model("capwise_crm.capwise_crm"):obj>', auth='public')
    # def object(self, obj, **kw):
    #     return http.request.render('capwise_crm.object', {
    #         'object': obj
    #     })


    @http.route('/capwise/webhook_bank_statement', type="json", auth='public',website=True, method=['GET', 'POST'])
    def webhoook_bank_statement(self, **kw):
        _logger.info("webhookbankstatement###########****************%s" %request.jsonrequest)
        kw = request.jsonrequest
        lead_id = ""
        loanType = ""
        if "loanType" in kw:
            loanType = kw['loanType'].lower()
        if "leadId" in kw:
            lead_id = kw['leadId']
        vals = {}    
        for_data = request.env['capwise.lead'].sudo().search([("lead_id","=",lead_id),("loan_type","=",loanType)])
        if for_data:
            if "docId" in kw:
                url = "https://cartbi.com/api/downloadFileAsExcel"
                payload = str(kw["docId"])
                headers = {
                  'auth-token': 'API://Rw/2P28PI8L3vaPt0BXsWstRSNR5o8dDnVjDKhQMWd3OwQsisIK2MUPi7shTMn4c',
                  'Content-Type': 'text/plain'
                }

                conn = requests.request("POST", url, headers=headers, data=payload)
                _logger.info("conn.content###########****************%s" %conn.content)

                file_added = "/opt/odoo/demofile_%s_%s.xlsx" % (lead_id, loanType)
                with open(file_added, "wb") as binary_file:
                    binary_file.write(conn.content)

                def open_target_file(target_path):
                    with open(target_path,"rb") as excel_file:
                        return excel_file.read()

                def encode_file(excel_file):
                    return base64.b64encode(excel_file)

                def decode_file():
                    return base64.b64decode(excel_file)

                your_excel_path = file_added
                _logger.info("your_excel_path****************%s" %your_excel_path)
                destiny_path = ""

                excel_file = open_target_file(your_excel_path)
                encoded_excel = encode_file(excel_file)
                print("encoded_excel##########################",encoded_excel)
                
                attachment = {
                           'name': "BSA.xlsx",
                           'display_name': "BSA.xls",
                           'datas': encoded_excel,
                           'type': 'binary'
                       }
                ir_id = request.env['ir.attachment'].sudo().create(attachment)
                print("ir_id$$$$$$$$$$$$$$$$$$$$$$$$4",ir_id)
                _logger.info("ir_idir_id###########****************%s" %ir_id)
            for_data.update({
                "bsa_attachment" : [(4, ir_id.id)]
                })
        args = {'success': True, 'message': 'Success', 'ID':for_data.id}
        return args    



    def _get_credit_repot(self, lead_id, loan_type):
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
        print("token######################",token)
        if lead_id:
            lead_status = {
                "lead_id" : lead_id,
                "loan_type" : loan_type,
            }
            response = requests.post("https://api.dev.finbii.com/crm/get-experian",headers={'Authorization': "Bearer %s" % token}, json=lead_status)
            _logger.info("Mobile APP create lead data****************%s" %request.jsonrequest)
            json_object = json.loads(response.content)[0]
            if "showHtmlReportForCreditReport" in json_object:
                root = json.loads(json_object).get("showHtmlReportForCreditReport")    
                soup = BeautifulSoup(root, 'html.parser')
                for data in soup:
                    tag_first = "First_Name"
                    reg_str_First_Name = "<" + tag_first + ">(.*?)</" + tag_first + ">"
                    res_First_Name = re.findall(reg_str_First_Name, data)
                    First_Name = res_First_Name
                    if First_Name:
                        dct['first_name'] = First_Name[0]
                        print("First_Name##############",First_Name)
                                

                    tag_last = "Last_Name"
                    reg_str = "<" + tag_last + ">(.*?)</" + tag_last + ">"
                    res_Last_name = re.findall(reg_str, data)
                    Last_name = res_Last_name
                    if Last_name:
                        dct['Last_Name'] = Last_name[0]
                        print("Last_name##################",Last_name)


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
                    if ReportDate:
                        dct['ReportDate'] = ReportDate[0]
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
                    reg_str = "<" + tag_rptnum + ">(.*?)</" + tag_rptnum + ">"
                    res_ReportNumber = re.findall (reg_str,data)
                    ReportNumber = res_ReportNumber
                    if ReportNumber:
                        dct['ReportNumber'] = ReportNumber[0]
                        print("ReportNumber#########",ReportNumber)

                    tag_subname = "Subscriber_Name"
                    reg_str ="<" + tag_subname + ">(.*?)</" + tag_subname + ">"
                    res_Subscriber_Name = re.findall (reg_str,data)
                    Subscriber_Name = res_Subscriber_Name
                    if Subscriber_Name:
                        dct['Subscriber_Name'] = Subscriber_Name[0]
                        print("Subscriber_Name#########",Subscriber_Name)

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
                    if Gender_Code:
                        dct['Gender_Code'] = Gender_Code[0]
                        print("Gender_Code#########",Gender_Code)


                    tag_pan = "IncomeTaxPan"
                    reg_str = "<" + tag_pan + ">(.*?)</" + tag_pan + ">"
                    res_IncomeTaxPan = re.findall(reg_str,data)
                    IncomeTaxPan = res_IncomeTaxPan
                    if IncomeTaxPan:
                        dct['IncomeTaxPan'] = IncomeTaxPan[0]
                        print("IncomeTaxPan#########",IncomeTaxPan)

                    tag_pandt = "PAN_Issue_Date"
                    reg_str = "<" + tag_pandt + ">(.*?)</" + tag_pandt + ">"
                    res_PAN_Issue_Date = re.findall(reg_str,data)
                    PAN_Issue_Date = res_PAN_Issue_Date
                    if PAN_Issue_Date:
                        dct['PAN_Issue_Date'] = PAN_Issue_Date[0]
                        print("PAN_Issue_Date#########",PAN_Issue_Date)

                    tag_expdt = "PAN_Expiration_Date"
                    reg_str = "<" +tag_expdt + ">(.*?)</" + tag_expdt + ">"
                    res_PAN_Expiration_Date = re.findall(reg_str,data)
                    PAN_Expiration_Date = res_PAN_Expiration_Date
                    if PAN_Expiration_Date:
                        dct['PAN_Expiration_Date'] = PAN_Expiration_Date[0]
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
                        dct['Passport_Issue_Date'] = Passport_Issue_Date[0]
                        print("Passport_Issue_Date#########",Passport_Issue_Date)

                    tag_pxpdt = "Passport_Expiration_Date"
                    reg_str = "<" +tag_pxpdt + ">(.*?)</" + tag_pxpdt + ">"
                    res_Passport_Expiration_Date = re.findall(reg_str,data)
                    Passport_Expiration_Date = res_Passport_Expiration_Date
                    if Passport_Expiration_Date:
                        dct['Passport_Expiration_Date'] = Passport_Expiration_Date[0]
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
                        dct['Voter_ID_Issue_Date'] = Voter_ID_Issue_Date[0]
                        print("Voter_ID_Issue_Date#########",Voter_ID_Issue_Date)

                    tag_videxp = "Voter_ID_Expiration_Date"
                    reg_str = "<" + tag_videxp + ">(.*?)</" + tag_videxp + ">"
                    res_Voter_ID_Expiration_Date = re.findall(reg_str,data)
                    Voter_ID_Expiration_Date = res_Voter_ID_Expiration_Date
                    if Voter_ID_Expiration_Date:
                        dct['Voter_ID_Expiration_Date'] = Voter_ID_Expiration_Date[0]
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
                        dct['Driver_License_Issue_Date'] = Driver_License_Issue_Date[0]
                        print("Driver_License_Issue_Date#########",Driver_License_Issue_Date)

                    tag_dlexpdt = "Driver_License_Expiration_Date"
                    reg_str = "<" + tag_dlexpdt + ">(.*?)</" + tag_dlexpdt + ">"
                    res_Driver_License_Expiration_Date = re.findall(reg_str,data)
                    Driver_License_Expiration_Date = res_Driver_License_Expiration_Date
                    if Driver_License_Expiration_Date:
                        dct['Driver_License_Expiration_Date'] = Driver_License_Expiration_Date[0]
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
                        dct['Ration_Card_Issue_Date'] = Ration_Card_Issue_Date[0]
                        print("Ration_Card_Issue_Date#########",Ration_Card_Issue_Date)

                    tag_rtncrdexp = "Ration_Card_Expiration_Date"
                    reg_str = "<" + tag_rtncrdexp + ">(.*?)</" + tag_rtncrdexp + ">"
                    res_Ration_Card_Expiration_Date = re.findall(reg_str,data)
                    Ration_Card_Expiration_Date = res_Ration_Card_Expiration_Date
                    if Ration_Card_Expiration_Date:
                        dct['Ration_Card_Expiration_Date'] = Ration_Card_Expiration_Date[0]
                        print("Ration_Card_Expiration_Date#########",Ration_Card_Expiration_Date)

                    tag_unividno = "Universal_ID_Number"
                    reg_str = "<" + tag_unividno + ">(.*?)</" + tag_unividno + ">"
                    res_Universal_ID_Number = re.findall(reg_str,data)
                    Universal_ID_Number = res_Universal_ID_Number
                    if Universal_ID_Number:
                        dct['Universal_ID_Number'] = Universal_ID_Number[0]
                        print("Universal_ID_Number#########",Universal_ID_Number)

                    tag_unividdet = "Universal_ID_Issue_Date"
                    reg_str ="<" + tag_unividdet + ">(.*?)</" + tag_unividdet + ">"
                    res_Universal_ID_Issue_Date = re.findall(reg_str,data)
                    Universal_ID_Issue_Date = res_Universal_ID_Issue_Date
                    if Universal_ID_Issue_Date:
                        dct['Universal_ID_Issue_Date'] = Universal_ID_Issue_Date[0]
                        print("Universal_ID_Issue_Date#########",Universal_ID_Issue_Date)


                    tag_univexp ="Universal_ID_Expiration_Date"
                    reg_str = "<" + tag_univexp + ">(.*?)</" + tag_univexp + ">"
                    res_Universal_ID_Expiration_Date = re.findall(reg_str,data)
                    Universal_ID_Expiration_Date = res_Universal_ID_Expiration_Date
                    if Universal_ID_Expiration_Date:
                        dct['Universal_ID_Expiration_Date'] = Universal_ID_Expiration_Date[0]
                        print("Universal_ID_Expiration_Date#########",Universal_ID_Expiration_Date)

                    tag_dobap ="Date_Of_Birth_Applicant"
                    reg_str = "<" + tag_dobap + ">(.*?)</" + tag_dobap + ">"
                    res_Date_Of_Birth_Applicant = re.findall(reg_str,data)
                    Date_Of_Birth_Applicant = res_Date_Of_Birth_Applicant
                    if Date_Of_Birth_Applicant:
                        dct['Date_Of_Birth_Applicant'] = Date_Of_Birth_Applicant[0]
                        print("Date_Of_Birth_Applicant#########",Date_Of_Birth_Applicant)

                    tag_tna1 = "Telephone_Number_Applicant_1st"
                    reg_str = "<" + tag_tna1 + ">(.*?)</" + tag_tna1 + ">"
                    res_Telephone_Number_Applicant_1st = re.findall(reg_str,data)
                    Telephone_Number_Applicant_1st = res_Telephone_Number_Applicant_1st
                    if Telephone_Number_Applicant_1st:
                        dct['Telephone_Number_Applicant_1st'] = Telephone_Number_Applicant_1st[0]
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

                    tag_mphno = "MobilePhone"
                    reg_str = "<" + tag_mphno + ">(.*?)</" + tag_mphno + ">"
                    res_MobilePhone = re.findall(reg_str,data)
                    MobilePhone = res_MobilePhone
                    if MobilePhone:
                        dct['MobilePhone'] = MobilePhone[0]
                        print("MobilePhone#########",MobilePhone)

                    tag_mailid = "EMailId"
                    reg_str = "<" + tag_mailid + ">(.*?)</" + tag_mailid + ">"
                    res_EMailId = re.findall(reg_str,data)
                    EMailId = res_EMailId
                    if EMailId:
                        dct['EMailId'] = EMailId[0]
                        print("EMailId#########",EMailId)

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
                    dct['Outstanding_Balance_Secured_Percentage'] = Outstanding_Balance_Secured_Percentage[0]
                    print("Outstanding_Balance_Secured_Percentage#########",Outstanding_Balance_Secured_Percentage)
                    
                    tag_outbaluns = "Outstanding_Balance_UnSecured"
                    reg_str = "<" + tag_outbaluns + ">(.*?)</" + tag_outbaluns + ">"
                    res_Outstanding_Balance_UnSecured = re.findall(reg_str,data)
                    Outstanding_Balance_UnSecured = res_Outstanding_Balance_UnSecured
                    dct['Outstanding_Balance_UnSecured'] = Outstanding_Balance_UnSecured[0]
                    print("Outstanding_Balance_UnSecured#########",Outstanding_Balance_UnSecured)

                    tag_obup = "Outstanding_Balance_UnSecured_Percentage"
                    reg_str = "<" + tag_obup + ">(.*?)</" + tag_obup + ">"
                    res_Outstanding_Balance_UnSecured_Percentage = re.findall(reg_str,data)
                    Outstanding_Balance_UnSecured_Percentage = res_Outstanding_Balance_UnSecured_Percentage
                    dct['Outstanding_Balance_UnSecured_Percentage'] = Outstanding_Balance_UnSecured_Percentage[0]
                    print("Outstanding_Balance_UnSecured_Percentage#########",Outstanding_Balance_UnSecured_Percentage)


                    tag_oball = "Outstanding_Balance_All"
                    reg_str = "<" + tag_oball + ">(.*?)</" + tag_oball + ">"
                    res_Outstanding_Balance_All = re.findall(reg_str,data)
                    Outstanding_Balance_All=res_Outstanding_Balance_All
                    dct['Outstanding_Balance_All'] = Outstanding_Balance_All[0]
                    print("Outstanding_Balance_All#########",Outstanding_Balance_All)

                    tag_idno = "Identification_Number"
                    reg_str = "<" + tag_oball + ">(.*?)</" + tag_oball + ">"
                    res_Identification_Number = re.findall(reg_str,data)
                    Identification_Number = res_Identification_Number
                    dct['Identification_Number'] = Identification_Number[0]
                    print("Identification_Number#########",Identification_Number)

                    tag_sbsnme="Subscriber_Name"
                    reg_str = "<" + tag_sbsnme + ">(.*?)</" + tag_sbsnme + ">"
                    res_Subscriber_Name = re.findall(reg_str,data)
                    Subscriber_Name = res_Subscriber_Name
                    dct['Subscriber_Name'] = Subscriber_Name[0]
                    print("Subscriber_Name#########",Subscriber_Name)

                    tag_acno = "Account_Number"
                    reg_str = "<" + tag_acno + ">(.*?)</" + tag_acno + ">"
                    res_Account_Number = re.findall(reg_str,data)
                    Account_Number = res_Account_Number
                    dct['Account_Number'] = Account_Number[0]
                    print("Account_Number#########",Account_Number)


                    tag_ptype = "Portfolio_Type"
                    res_str = "<" + tag_ptype + ">(.*?)</" + tag_ptype + ">"
                    res_Portfolio_Type = re.findall(res_str,data)
                    Portfolio_Type = res_Portfolio_Type
                    dct['Portfolio_Type'] = Portfolio_Type[0]
                    print("Portfolio_Type#########",Portfolio_Type)

                    tag_acctype = "Account_Type"
                    reg_str = "<" + tag_acctype + ">(.*?)</" + tag_acctype + ">"
                    res_Account_Type = re.findall(reg_str,data)
                    Account_Type = res_Account_Type
                    dct['Account_Type'] = Account_Type[0]
                    print("Account_Type#########",Account_Type)
                    

                    tag_hcoalt = "Highest_Credit_or_Original_Loan_Amount"
                    reg_str ="<" + tag_hcoalt + ">(.*?)</" + tag_hcoalt + ">"
                    res_Highest_Credit_or_Original_Loan_Amount = re.findall(reg_str,data)
                    Highest_Credit_or_Original_Loan_Amount = res_Highest_Credit_or_Original_Loan_Amount
                    dct['Highest_Credit_or_Original_Loan_Amount'] = Highest_Credit_or_Original_Loan_Amount[0]
                    print("Highest_Credit_or_Original_Loan_Amount#########",Highest_Credit_or_Original_Loan_Amount)

                    tag_opdt = "Open_Date"
                    reg_str = "<" + tag_opdt + ">(.*?)</" + tag_opdt + ">"
                    res_Open_Date = re.findall(reg_str,data)
                    Open_Date = res_Open_Date
                    dct['Open_Date'] = Open_Date[0]
                    print("Open_Date#########",Open_Date)

                    tag_clam = "Credit_Limit_Amount"
                    reg_str = "<"+ tag_clam + ">(.*?)</" + tag_clam + ">"
                    res_Credit_Limit_Amount = re.findall(reg_str,data)
                    Credit_Limit_Amount = res_Credit_Limit_Amount
                    dct['Credit_Limit_Amount'] = Credit_Limit_Amount[0]
                    print("Credit_Limit_Amount#########",Credit_Limit_Amount)

                    
                    tag_hcoalt = "Highest_Credit_or_Original_Loan_Amount"
                    reg_str ="<" + tag_hcoalt + ">(.*?)</" + tag_hcoalt + ">"
                    res_Highest_Credit_or_Original_Loan_Amount = re.findall(reg_str,data)
                    Highest_Credit_or_Original_Loan_Amount = res_Highest_Credit_or_Original_Loan_Amount
                    dct['Highest_Credit_or_Original_Loan_Amount'] = Highest_Credit_or_Original_Loan_Amount[0]
                    print("Highest_Credit_or_Original_Loan_Amount#########",Highest_Credit_or_Original_Loan_Amount)

                    tag_trmdur = "Terms_Duration"
                    reg_str = "<" + tag_trmdur + ">(.*?)</" + tag_trmdur + ">"
                    res_Terms_Duration = re.findall(reg_str,data)
                    Terms_Duration = res_Terms_Duration
                    dct['Terms_Duration'] = Terms_Duration[0]
                    print("Terms_Duration#########",Terms_Duration)

                    tag_trmfrq = "Terms_Frequency"
                    reg_str = "<" + tag_trmfrq + ">(.*?)</" + tag_trmfrq + ">"
                    res_Terms_Frequency = re.findall(reg_str,data)
                    Terms_Frequency = res_Terms_Frequency
                    dct['Terms_Frequency'] = Terms_Frequency[0]
                    print("Terms_Frequency#########",Terms_Frequency)

                    tag_smpm = "Scheduled_Monthly_Payment_Amount"
                    reg_str = "<" + tag_smpm + ">(.*?)</" + tag_smpm + ">"
                    res_Scheduled_Monthly_Payment_Amount = re.findall(reg_str,data)
                    Scheduled_Monthly_Payment_Amount = res_Scheduled_Monthly_Payment_Amount
                    dct['Scheduled_Monthly_Payment_Amount'] = Scheduled_Monthly_Payment_Amount[0]
                    print("Scheduled_Monthly_Payment_Amount#########",Scheduled_Monthly_Payment_Amount)

                    tag_acstatus = "Account_Status"
                    reg_str = "<" + tag_acstatus + ">(.*?)</" + tag_acstatus + ">"
                    res_Account_Status = re.findall(reg_str,data)
                    Account_Status = res_Account_Status
                    dct['Account_Status'] = Account_Status[0]
                    print("Account_Status#########",Account_Status)

                    tag_pmtrt = "Payment_Rating"
                    reg_str = "<" + tag_pmtrt + ">(.*?)</" + tag_pmtrt + ">"
                    res_Payment_Rating = re.findall(reg_str,data)
                    Payment_Rating = res_Payment_Rating
                    dct['Payment_Rating'] = Payment_Rating[0]
                    print("Payment_Rating#########",Payment_Rating)

                    tag_pmthisp ="Payment_History_Profile"
                    reg_str =  "<" + tag_pmthisp + ">(.*?)</" + tag_pmthisp + ">"
                    res_Payment_History_Profile = re.findall(reg_str,data)
                    Payment_History_Profile = res_Payment_History_Profile
                    dct['Payment_History_Profile'] = Payment_History_Profile[0]
                    print("Payment_History_Profile#########",Payment_History_Profile)

                    tag_spcmt = "Special_Comment"
                    reg_str = "<" + tag_spcmt + ">(.*?)</" + tag_spcmt + ">"
                    res_Special_Comment = re.findall(reg_str,data)
                    Special_Comment = res_Special_Comment
                    dct['Special_Comment'] = Special_Comment[0]
                    print("Special_Comment#########",Special_Comment)


                    tag_crbal = "Current_Balance"
                    reg_str = "<" + tag_crbal + ">(.*?)</" + tag_crbal + ">"
                    res_Current_Balance = re.findall(reg_str,data)
                    Current_Balance = res_Current_Balance
                    dct['Current_Balance'] = Current_Balance[0]
                    print("Current_Balance#########",Current_Balance)

                    tag_amtpdue = "Amount_Past_Due"
                    reg_str = "<" + tag_amtpdue + ">(.*?)</" + tag_amtpdue + ">"
                    res_Amount_Past_Due = re.findall(reg_str,data)
                    Amount_Past_Due = res_Amount_Past_Due
                    dct['Amount_Past_Due'] = Amount_Past_Due[0]
                    print("Amount_Past_Due#########",Amount_Past_Due)

                    tag_ocoa = "Original_Charge_Off_Amount"
                    reg_str = "<" + tag_ocoa + ">(.*?)</" + tag_ocoa + ">"
                    res_Original_Charge_Off_Amount = re.findall(reg_str,data)
                    Original_Charge_Off_Amount = res_Original_Charge_Off_Amount
                    dct['Original_Charge_Off_Amount'] = Original_Charge_Off_Amount[0]
                    print("Original_Charge_Off_Amount#########",Original_Charge_Off_Amount)

                    tag_dtrpt="Date_Reported"
                    reg_str = "<" + tag_dtrpt + ">(.*?)</" + tag_dtrpt + ">"
                    res_Date_Reported = re.findall(reg_str,data)
                    Date_Reported = res_Date_Reported
                    dct['Date_Reported'] = Date_Reported[0]
                    print("Date_Reported#########",Date_Reported)

                    tag_dofd = "Date_of_First_Delinquency"
                    reg_str = "<" + tag_dofd + ">(.*?)</" + tag_dofd + ">"
                    res_Date_of_First_Delinquency = re.findall(reg_str,data)
                    Date_of_First_Delinquency = res_Date_of_First_Delinquency
                    dct['Date_of_First_Delinquency'] = Date_of_First_Delinquency[0]
                    print("Date_of_First_Delinquency#########",Date_of_First_Delinquency)

                    tag_dtcd = "Date_Closed"
                    reg_str = "<" + tag_dtcd + ">(.*?)</" + tag_dtcd + ">"
                    res_Date_Closed = re.findall(reg_str,data)
                    Date_Closed = res_Date_Closed
                    dct['Date_Closed'] = Date_Closed[0]
                    print("Date_Closed#########",Date_Closed)

                    tag_dolp = "Date_of_Last_Payment"
                    reg_str = "<" + tag_dolp + ">(.*?)</" + tag_dolp + ">"
                    res_Date_of_Last_Payment = re.findall(reg_str,data)
                    Date_of_Last_Payment = res_Date_of_Last_Payment
                    dct['Date_of_Last_Payment'] = Date_of_Last_Payment[0]
                    print("Date_of_Last_Payment#########",Date_of_Last_Payment)

                    tag_suitf="SuitFiledWillfulDefaultWrittenOffStatus"
                    reg_str = "<" + tag_suitf + ">(.*?)</" + tag_suitf + ">"
                    res_SuitFiledWillfulDefaultWrittenOffStatus = re.findall(reg_str,data)
                    SuitFiledWillfulDefaultWrittenOffStatus = res_SuitFiledWillfulDefaultWrittenOffStatus
                    dct['SuitFiledWillfulDefaultWrittenOffStatus'] = SuitFiledWillfulDefaultWrittenOffStatus[0]
                    print("SuitFiledWillfulDefaultWrittenOffStatus#########",SuitFiledWillfulDefaultWrittenOffStatus)

                    tag_suitwd = "SuitFiled_WilfulDefault"
                    reg_str = "<" + tag_suitwd + ">(.*?)</" + tag_suitwd + ">"
                    res_SuitFiled_WilfulDefault = re.findall(reg_str, data)
                    SuitFiled_WilfulDefault = res_SuitFiled_WilfulDefault
                    dct['SuitFiled_WilfulDefault'] = SuitFiled_WilfulDefault[0]
                    print("SuitFiled_WilfulDefault#########",SuitFiled_WilfulDefault)

                    tag_woss = "Written_off_Settled_Status"
                    reg_str = "<" + tag_woss + ">(.*?)</" + tag_woss + ">"
                    res_Written_off_Settled_Status = re.findall(reg_str,data)
                    Written_off_Settled_Status = res_Written_off_Settled_Status
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
                    dct['Occupation_Code'] = Occupation_Code[0]
                    print("Occupation_Code#########",Occupation_Code)

                    tag_smamt = "Settlement_Amount"
                    reg_str = "<" + tag_smamt + ">(.*?)</" + tag_smamt + ">" 
                    res_Settlement_Amount = re.findall(reg_str, data)
                    Settlement_Amount = res_Settlement_Amount
                    dct['Settlement_Amount'] = Settlement_Amount[0]
                    print("Settlement_Amount#########",Settlement_Amount)

                    tag_vocol = "Value_of_Collateral"
                    reg_str = "<" + tag_vocol + ">(.*?)</" + tag_vocol + ">" 
                    res_Value_of_Collateral = re.findall(reg_str, data)
                    Value_of_Collateral = res_Value_of_Collateral
                    dct['Value_of_Collateral'] = Value_of_Collateral[0]
                    print("Value_of_Collateral#########",Value_of_Collateral)

                    tag_tocl = "Type_of_Collateral"
                    reg_str = "<" + tag_tocl + ">(.*?)</" + tag_tocl + ">" 
                    res_Type_of_Collateral = re.findall(reg_str, data)
                    Type_of_Collateral = res_Type_of_Collateral
                    dct['Type_of_Collateral'] = Type_of_Collateral[0]
                    print("Type_of_Collateral#########",Type_of_Collateral)

                    tag_woat = "Written_Off_Amt_Total"
                    reg_str = "<" + tag_woat + ">(.*?)</" + tag_woat + ">" 
                    res_Written_Off_Amt_Total = re.findall(reg_str,data)
                    Written_Off_Amt_Total = res_Written_Off_Amt_Total
                    dct['Written_Off_Amt_Total'] = Written_Off_Amt_Total[0]
                    print("Written_Off_Amt_Total#########",Written_Off_Amt_Total)

                    tag_woap = "Written_Off_Amt_Principal"
                    reg_str = "<" + tag_woap + ">(.*?)</" + tag_woap + ">"
                    res_Written_Off_Amt_Principal = re.findall(reg_str,data)
                    Written_Off_Amt_Principal = res_Written_Off_Amt_Principal
                    dct['Written_Off_Amt_Principal'] = Written_Off_Amt_Principal[0]
                    print("Written_Off_Amt_Principal#########",Written_Off_Amt_Principal)

                    tag_roi ="Rate_of_Interest"
                    reg_str = "<" + tag_roi + ">(.*?)</" + tag_roi + ">"
                    res_Rate_of_Interest = re.findall(reg_str,data)
                    Rate_of_Interest = res_Rate_of_Interest
                    dct['Rate_of_Interest'] = Rate_of_Interest[0]
                    print("Rate_of_Interest#########",Rate_of_Interest)

                    tag_rptenure = "Repayment_Tenure"
                    reg_str = "<" + tag_rptenure + ">(.*?)</" + tag_rptenure + ">"
                    res_Repayment_Tenure = re.findall(reg_str, data)
                    Repayment_Tenure = res_Repayment_Tenure
                    dct['Repayment_Tenure'] = Repayment_Tenure[0]
                    print("Repayment_Tenure#########",Repayment_Tenure)

                    tag_prrf = "Promotional_Rate_Flag"
                    reg_str = "<" + tag_prrf + ">(.*?)</" + tag_prrf + ">"
                    res_Promotional_Rate_Flag = re.findall(reg_str, data)
                    Promotional_Rate_Flag = res_Promotional_Rate_Flag
                    dct['Promotional_Rate_Flag'] = Promotional_Rate_Flag[0]
                    print("Promotional_Rate_Flag#########",Promotional_Rate_Flag)

                    tag_incind = "Income_Indicator"
                    reg_str = "<" + tag_incind + ">(.*?)</" + tag_incind + ">"
                    res_Income_Indicator = re.findall(reg_str, data)
                    Income_Indicator = res_Income_Indicator
                    dct['Income_Indicator'] = Income_Indicator[0]
                    print("Income_Indicator#########",Income_Indicator)

                    tag_infrin = "Income_Frequency_Indicator"
                    reg_str = "<" + tag_infrin + ">(.*?)</" + tag_infrin + ">"
                    res_Income_Frequency_Indicator = re.findall(reg_str, data)
                    Income_Frequency_Indicator = res_Income_Frequency_Indicator
                    dct['Income_Frequency_Indicator'] = Income_Frequency_Indicator[0]
                    print("Income_Frequency_Indicator#########",Income_Frequency_Indicator)

                    tag_defstdt = "DefaultStatusDate"
                    reg_str = "<" + tag_defstdt + ">(.*?)</" + tag_defstdt + ">"
                    res_DefaultStatusDate = re.findall(reg_str, data)
                    DefaultStatusDate = res_DefaultStatusDate
                    dct['DefaultStatusDate'] = DefaultStatusDate[0]
                    print("DefaultStatusDate#########",DefaultStatusDate)

                    tag_litstdt = "LitigationStatusDate"
                    reg_str = "<" + tag_litstdt + ">(.*?)</" + tag_litstdt + ">"
                    res_LitigationStatusDate = re.findall(reg_str, data)
                    LitigationStatusDate = res_LitigationStatusDate
                    dct['LitigationStatusDate'] = LitigationStatusDate[0]
                    print("LitigationStatusDate#########",LitigationStatusDate)

                    tag_wosdt = "WriteOffStatusDate"
                    reg_str = "<" + tag_wosdt + ">(.*?)</" + tag_wosdt + ">"
                    res_WriteOffStatusDate=re.findall(reg_str, data)
                    WriteOffStatusDate = res_WriteOffStatusDate
                    dct['WriteOffStatusDate'] = WriteOffStatusDate[0]
                    print("WriteOffStatusDate#########",WriteOffStatusDate)

                    tag_dtoad = "DateOfAddition"
                    reg_str = "<" + tag_dtoad + ">(.*?)</" + tag_dtoad + ">"
                    res_DateOfAddition = re.findall(reg_str, data)
                    DateOfAddition = res_DateOfAddition
                    dct['DateOfAddition'] = DateOfAddition[0]
                    print("DateOfAddition#########",DateOfAddition)

                    tag_ccod = "CurrencyCode"
                    reg_str = "<" + tag_ccod + ">(.*?)</" + tag_ccod + ">"
                    res_CurrencyCode = re.findall(reg_str, data)
                    CurrencyCode = res_CurrencyCode
                    dct['CurrencyCode'] = CurrencyCode[0]
                    print("CurrencyCode#########",CurrencyCode)

                    tag_sbscmt = "Subscriber_comments"
                    reg_str = "<" + tag_sbscmt + ">(.*?)</" + tag_sbscmt + ">"
                    res_Subscriber_comments = re.findall(reg_str, data)
                    Subscriber_comments = res_Subscriber_comments
                    dct['Subscriber_comments'] = Subscriber_comments[0]
                    print("Subscriber_comments#########",Subscriber_comments)

                    tag_cncmm = "Consumer_comments"
                    reg_str = "<" + tag_cncmm + ">(.*?)</" + tag_cncmm + ">"
                    res_Consumer_comments = re.findall(reg_str, data)
                    Consumer_comments = res_Consumer_comments
                    dct['Consumer_comments'] = Consumer_comments[0]
                    print("Consumer_comments#########",Consumer_comments)

                    tag_ahtc = "AccountHoldertypeCode"
                    reg_str = "<" + tag_ahtc + ">(.*?)</" + tag_ahtc + ">"
                    res_AccountHoldertypeCode = re.findall(reg_str, data)
                    AccountHoldertypeCode = res_AccountHoldertypeCode
                    dct['AccountHoldertypeCode'] = AccountHoldertypeCode[0]
                    print("AccountHoldertypeCode#########",AccountHoldertypeCode)
                    
                    tag_yr = "Year"
                    reg_str = "<" + tag_yr + ">(.*?)</" + tag_yr + ">"
                    res_Year = re.findall(reg_str, data)
                    Year = res_Year
                    dct['Year'] = Year[0]
                    print("Year#########",Year)

                    tag_mnt = "Month"
                    reg_str = "<" + tag_mnt + ">(.*?)</" + tag_mnt + ">"
                    res_Month = re.findall(reg_str, data)
                    Month = res_Month
                    dct['Month'] = Month
                    print("Month#########", Month)

                    tag_dypd = "Days_Past_Due"
                    reg_str = "<" + tag_dypd + ">(.*?)</" + tag_dypd + ">"
                    res_Days_Past_Due = re.findall(reg_str, data)
                    Days_Past_Due = res_Days_Past_Due
                    dct['Days_Past_Due'] = Days_Past_Due[0]
                    print("Days_Past_Due#########",Days_Past_Due)

                    tag_snmnm = "Surname_Non_Normalized"
                    reg_str = "<" + tag_snmnm + ">(.*?)</" + tag_snmnm + ">"
                    res_Surname_Non_Normalized = re.findall(reg_str, data)
                    Surname_Non_Normalized =res_Surname_Non_Normalized
                    dct['Surname_Non_Normalized'] = Surname_Non_Normalized[0]
                    print("Surname_Non_Normalized#########",Surname_Non_Normalized)

                    tag_fnnnn = "First_Name_Non_Normalized"
                    reg_str = "<" + tag_fnnnn + ">(.*?)</" + tag_fnnnn + ">"
                    res_First_Name_Non_Normalized = re.findall(reg_str,data)
                    First_Name_Non_Normalized = res_First_Name_Non_Normalized
                    dct['First_Name_Non_Normalized'] = First_Name_Non_Normalized[0]
                    print("First_Name_Non_Normalized#########",First_Name_Non_Normalized)

                    tag_mn1n = "Middle_Name_1_Non_Normalized"
                    reg_str = "<" + tag_snmnm + ">(.*?)</" + tag_snmnm + ">"
                    res_Middle_Name_1_Non_Normalized = re.findall(reg_str,data)
                    Middle_Name_1_Non_Normalized = res_Middle_Name_1_Non_Normalized
                    dct['Middle_Name_1_Non_Normalized'] = Middle_Name_1_Non_Normalized[0]
                    print("Middle_Name_1_Non_Normalized#########",Middle_Name_1_Non_Normalized)

                    tag_mn2n = "Middle_Name_2_Non_Normalized"
                    reg_str = "<" + tag_mn2n + ">(.*?)</" + tag_mn2n + ">"
                    res_Middle_Name_2_Non_Normalized = re.findall(reg_str,data)
                    Middle_Name_2_Non_Normalized = res_Middle_Name_2_Non_Normalized
                    dct['Middle_Name_2_Non_Normalized'] = Middle_Name_2_Non_Normalized[0]
                    print("Middle_Name_2_Non_Normalized#########",Middle_Name_2_Non_Normalized)

                    tag_mn3n = "Middle_Name_3_Non_Normalized"
                    reg_str = "<" + tag_mn3n + ">(.*?)</" + tag_mn3n + ">"
                    res_Middle_Name_3_Non_Normalized = re.findall(reg_str,data)
                    Middle_Name_3_Non_Normalized = res_Middle_Name_3_Non_Normalized
                    dct['Middle_Name_3_Non_Normalized'] = Middle_Name_3_Non_Normalized[0]
                    print("Middle_Name_3_Non_Normalized#########",Middle_Name_3_Non_Normalized)

                    tag_als = "Alias"
                    reg_str = "<" + tag_als + ">(.*?)</" + tag_als + ">"
                    res_Alias = re.findall(reg_str,data)
                    Alias = res_Alias
                    dct['Alias'] = Alias[0]
                    print("Alias#########",Alias)

                    tag_intxpn = "Income_TAX_PAN"
                    reg_str ="<" + tag_intxpn + ">(.*?)</" + tag_intxpn + ">"
                    res_Income_TAX_PAN = re.findall(reg_str,data)
                    Income_TAX_PAN = res_Income_TAX_PAN
                    dct['Income_TAX_PAN'] = Income_TAX_PAN
                    dct['Income_TAX_PAN'] = Income_TAX_PAN[0]
                    print("Income_TAX_PAN#########",Income_TAX_PAN)

                    tag_pssno = "Passport_Number"
                    reg_str = "<" + tag_pssno + ">(.*?)</" + tag_pssno + ">"
                    res_Passport_Number = re.findall(reg_str,data)
                    Passport_Number = res_Passport_Number
                    dct['Passport_Number'] = Passport_Number[0]
                    print("Passport_Number#########",Passport_Number)

                    tag_vidno = "Voter_ID_Number"
                    res_str = "<" + tag_vidno + ">(.*?)</" + tag_vidno + ">"
                    res_Voter_ID_Number = re.findall(res_str,data)
                    Voter_ID_Number = res_Voter_ID_Number
                    dct['Voter_ID_Number'] = Voter_ID_Number[0]
                    print("Voter_ID_Number#########",Voter_ID_Number)

                    tag_dob = "Date_of_birth"
                    reg_str = "<" + tag_dob + ">(.*?)</" + tag_dob + ">"
                    res_Date_of_birth = re.findall(reg_str,data)
                    Date_of_birth = res_Date_of_birth
                    dct['Date_of_birth'] = Date_of_birth[0]
                    print("Date_of_birth#########",Date_of_birth)

                    tag_flann = "First_Line_Of_Address_non_normalized"
                    reg_str = "<" + tag_flann + ">(.*?)</" + tag_flann + ">"
                    res_First_Line_Of_Address_non_normalized = re.findall(reg_str,data)
                    First_Line_Of_Address_non_normalized = res_First_Line_Of_Address_non_normalized
                    dct['First_Line_Of_Address_non_normalized'] = First_Line_Of_Address_non_normalized[0]
                    print("First_Line_Of_Address_non_normalized#########",First_Line_Of_Address_non_normalized)

                    tag_slann = "Second_Line_Of_Address_non_normalized"
                    reg_str = "<" + tag_slann + ">(.*?)</" + tag_slann + ">"
                    res_Second_Line_Of_Address_non_normalized = re.findall(reg_str,data)
                    Second_Line_Of_Address_non_normalized = res_Second_Line_Of_Address_non_normalized
                    dct['Second_Line_Of_Address_non_normalized'] = Second_Line_Of_Address_non_normalized[0]
                    print("Second_Line_Of_Address_non_normalized#########",Second_Line_Of_Address_non_normalized)

                    tag_tlann = "Third_Line_Of_Address_non_normalized"
                    reg_str = "<" + tag_tlann + ">(.*?)</" + tag_tlann + ">"
                    res_Third_Line_Of_Address_non_normalized = re.findall(reg_str,data)
                    Third_Line_Of_Address_non_normalized = res_Third_Line_Of_Address_non_normalized
                    dct['Third_Line_Of_Address_non_normalized'] = Third_Line_Of_Address_non_normalized[0]
                    print("Third_Line_Of_Address_non_normalized#########",Third_Line_Of_Address_non_normalized)

                    tag_ctynnorm = "City_non_normalized"
                    reg_str = "<" + tag_ctynnorm + ">(.*?)</" + tag_ctynnorm + ">"
                    res_City_non_normalized = re.findall(reg_str,data)
                    City_non_normalized = res_City_non_normalized
                    dct['City_non_normalized'] = City_non_normalized[0]
                    print("City_non_normalized#########",City_non_normalized)


                    tag_floann = "Fifth_Line_Of_Address_non_normalized"
                    reg_str = "<" + tag_floann + ">(.*?)</" + tag_floann + ">"
                    res_Fifth_Line_Of_Address_non_normalized = re.findall(reg_str,data)
                    Fifth_Line_Of_Address_non_normalized = res_Fifth_Line_Of_Address_non_normalized
                    dct['Fifth_Line_Of_Address_non_normalized'] = Fifth_Line_Of_Address_non_normalized[0]
                    print("Fifth_Line_Of_Address_non_normalized#########",Fifth_Line_Of_Address_non_normalized)


                    tag_stnn = "State_non_normalized"
                    reg_str = "<" + tag_stnn + ">(.*?)</" + tag_stnn + ">"
                    res_State_non_normalized = re.findall(reg_str,data)
                    State_non_normalized = res_State_non_normalized
                    dct['State_non_normalized'] = State_non_normalized[0]
                    print("State_non_normalized#########",State_non_normalized)

                    tag_zippnn = "ZIP_Postal_Code_non_normalized"
                    reg_str = "<" + tag_zippnn + ">(.*?)</" + tag_zippnn + ">"
                    res_ZIP_Postal_Code_non_normalized = re.findall(reg_str,data)
                    ZIP_Postal_Code_non_normalized = res_ZIP_Postal_Code_non_normalized
                    dct['ZIP_Postal_Code_non_normalized'] = ZIP_Postal_Code_non_normalized[0]
                    print("ZIP_Postal_Code_non_normalized#########",ZIP_Postal_Code_non_normalized)

                    tag_cntnn = "CountryCode_non_normalized"
                    reg_str = "<" + tag_cntnn + ">(.*?)</" + tag_cntnn + ">"
                    res_CountryCode_non_normalized = re.findall(reg_str,data)
                    CountryCode_non_normalized = res_CountryCode_non_normalized
                    dct['CountryCode_non_normalized'] = CountryCode_non_normalized[0]
                    print("CountryCode_non_normalized#########",CountryCode_non_normalized)

                    tag_aiinn = "Address_indicator_non_normalized"
                    reg_str = "<" + tag_aiinn + ">(.*?)</" + tag_aiinn + ">"
                    res_Address_indicator_non_normalized = re.findall(reg_str,data)
                    Address_indicator_non_normalized = res_Address_indicator_non_normalized
                    dct['Address_indicator_non_normalized'] = Address_indicator_non_normalized[0]
                    print("Address_indicator_non_normalized#########",Address_indicator_non_normalized)

                    tag_recnon = "Residence_code_non_normalized"
                    reg_str = "<" + tag_recnon + ">(.*?)</" + tag_recnon + ">"
                    res_Residence_code_non_normalized = re.findall(reg_str,data)
                    Residence_code_non_normalized = res_Residence_code_non_normalized
                    dct['Residence_code_non_normalized'] = Residence_code_non_normalized[0]
                    print("Residence_code_non_normalized#########",Residence_code_non_normalized)


                    tag_telno = "Telephone_Number"
                    reg_str = "<" + tag_telno + ">(.*?)</" + tag_telno + ">"
                    res_Telephone_Number = re.findall(reg_str,data)
                    Telephone_Number = res_Telephone_Number
                    dct['Telephone_Number'] = Telephone_Number[0]
                    print("Telephone_Number#########",Telephone_Number)



                    tag_ttypp  = "Telephone_Type"
                    reg_str = "<" + tag_ttypp + ">(.*?)</" + tag_ttypp + ">"
                    res_Telephone_Type = re.findall(reg_str,data)
                    Telephone_Type = res_Telephone_Type
                    dct['Telephone_Type'] = Telephone_Type[0]
                    print("Telephone_Type#########",Telephone_Type)

                    tag_texttt  = "Telephone_Extension"
                    reg_str = "<" + tag_texttt + ">(.*?)</" + tag_texttt + ">"
                    res_Telephone_Extension = re.findall(reg_str,data)
                    Telephone_Extension = res_Telephone_Extension
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



                    tag_exmtch = "Exact_match"
                    reg_str = "<" + tag_exmtch + ">(.*?)</" + tag_exmtch + ">"
                    res_Exact_match = re.findall(reg_str,data)
                    Exact_match = res_Exact_match
                    if Exact_match:
                        dct['Exact_match'] = Exact_match[0]
                        print("Exact_match#########",Exact_match)

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

                    loan_lead = request.env['capwise.lead'].sudo().search([('lead_id','=',lead_id),("loan_type", '=',loan_type) ], limit=1)  
                    loan_lead.update(dct)  

                    print_report = request.env.ref('capwise_crm.Credit_report').sudo()._render_qweb_pdf(loan_lead.ids)
                    print("print_report#############",print_report)
                    loan_lead.pdf_credit_score = base64.b64encode(print_report[0]) 


    @http.route('/crm/lenders_status', type="json", auth='public',website=True, method=['GET', 'POST'])
    def leader_status_data(self, **kw):
        # _logger.info("iiiiiiiiiiiiii###########****************%s" %request.jsonrequest)
        lead_id = ""
        loanType = ""
        if request.jsonrequest:
            kw = request.jsonrequest
        if "loanType" in kw:
            loanType = kw['loanType'].lower()
        if "leadId" in kw:
            lead_id = kw['leadId']
        vals = []
        dicts = {} 
        for_data = request.env['capwise.lead'].sudo().search([("lead_id","=",lead_id),("loan_type","=",loanType)])
        if for_data:
            for lender in for_data.multiple_lender:
                dicts = {
                'Bank_FI' : lender.Bank_FI.vendor_name.name,
                'state_id' : lender.state_id,
                'login_date' : lender.login_date,
                'login_amount' : lender.login_amount,
                'sanction_date' : lender.sanction_date,
                'sanction_amount' : lender.sanction_amount,
                'disb_Date' : lender.disb_Date,
                'dis_amount' : lender.dis_amount,
                }
                vals.append(dicts)
            print("vals@@@@@@@@@@@@@@@@@",vals)    
            return vals     