# -*- coding: utf-8 -*-
from odoo import http
from odoo import http
from odoo.http import request
import re
from datetime import datetime, time, date, timedelta
from subprocess import Popen, PIPE, STDOUT
import requests
import json
from bs4 import BeautifulSoup
import numpy_financial as npf
from subprocess import check_output
import pandas as pd
import html
import xlrd as xl 
import logging
import base64


_logger = logging.getLogger(__name__)

class CapwiseCrm(http.Controller):

    @http.route('/capwise/business_rule_engine', type="json", auth='public',website=True, method=['GET', 'POST'])
    def rule_engine_lead(self, **kw):
        dct = {}
        profile_loan_proprietor = ""
        profile_loan_partnership = ""
        profile_loan_pvt_ltd = ""
        profile_loan_ltd = ""
        profile_unsecured_loan_salaried = ""
        lender_unsecured = ""
        lead_vintage = ""
        owned_rent = ""
        ages_data = ""
        loan_lender = ""
        credit_lender = ""
        lender_unsecure_loan = [] 
        tenure_lender = ""
        tenore = 0
        if request.jsonrequest:
            print("request.jsonrequest@@@@@@@@@@@@@@@@",request.jsonrequest)
            data = request.jsonrequest
            # data["applicant_date_of_birth"]
            # data["lead_business_constitution"]
            # data["applicant_constitution"]
            # data["constitution_id"]
            # if "loan_type" in data and data[""]:

            if "loan_type" in data:
                data_loan_type = data["loan_type"].lower()
            if "lead_id" in data:
                data_lead_id = data["lead_id"]  
            lender_loantype = request.env["business_rules.business_rules"].sudo().search([("loan_type","=",data_loan_type)])
            lender=[]
            
            # for i in lender_loantype:  
            #     lender.append(i.fincial_institutions.vendor_name.name)
            # print(lender)

            print("lender_loantype@@@@@@@@@@@@@@@@@@@",lender_loantype)

            lead_records = request.env["capwise.lead"].sudo().search([("loan_type","=",data_loan_type),("lead_id","=",data_lead_id)])
            lead_records.lenders_data = [(6, 0, lender_loantype.ids)]

            if "servicable_pincode" in data:
                for pincode_service in lead_records.lenders_data:
                    for pin in pincode_service.fincial_institutions.location_pin_Code:
                        print("pin########################",pin)
                        if pin.name == str(data["servicable_pincode"]):
                            print("pincode_service@@@@@@@@@@@@@@@@@@@@",pincode_service)
                            lead_records.lenders_data = [(4, pincode_service.id)]

            if "lead_business_constitution" in data:
                if data["lead_business_constitution"] == 1:
                    profile_loan_proprietor = True
                    lender_unsecured = request.env["business_rules.business_rules"].sudo().search([("loan_type","=",data_loan_type),("profile_loan_proprietor","=",profile_loan_proprietor)])
                if data["lead_business_constitution"] == 2:
                    profile_loan_partnership = True
                    lender_unsecured = request.env["business_rules.business_rules"].sudo().search([("loan_type","=",data_loan_type),("profile_loan_partnership","=",profile_loan_partnership)])
                    print("lender_unsecured@@@@@@@@@@@@@@@@@@@@@@@",lender_unsecured)
                if data["lead_business_constitution"] == 3:
                    profile_loan_pvt_ltd = True
                    lender_unsecured = request.env["business_rules.business_rules"].sudo().search([("loan_type","=",data_loan_type),("profile_loan_pvt_ltd","=",profile_loan_pvt_ltd)])
                if data["lead_business_constitution"] == 4:
                    profile_loan_ltd  = True
                    lender_unsecured = request.env["business_rules.business_rules"].sudo().search([("loan_type","=",data_loan_type),("profile_loan_ltd","=",profile_loan_ltd)])
                if data["lead_business_constitution"] == 5:
                    profile_loan_salaried = True
                    lender_unsecured = request.env["business_rules.business_rules"].sudo().search([("loan_type","=",data_loan_type),("profile_loan_salaried","=",profile_loan_salaried)])
                # if lender_unsecured:
                # print("lead_records.lenders_data@@@@@@@@@@@@@@@@@@ttyyyyyyyyyyyyyyyy",lender_unsecured.ids)
                lead_records.lenders_data = [(6, 0, lender_unsecured.ids)]
                print("lead_records.lenders_data@@@@@@@@@@@@@@@@@@@@@@3333333333",lead_records.lenders_data)


            lead_sst = lead_records.lenders_data
            if "business_vintage" in data:
                print("lead_sst@@@@@@@@@@@@@@@@@@@",lead_sst)
                if "vintage_in_work_business_loan_from" in data:
                    lead_vintage = lead_sst.filtered(lambda d: d.vintage_in_work_business_loan == True and d.vintage_in_work_business_loan_from < data["vintage_in_work_business_loan_from"])
                    print("lead_vintage@###################111111111111111",lead_vintage)
                if "vintage_in_work_personal_loan_from" in data:
                    lead_vintage = lead_sst.filtered(lambda d: d.vintage_in_work_personal_loan == True and d.vintage_in_work_personal_loan_from < data["vintage_in_work_personal_loan_from"])
                    print("lead_vintage@###################222222222222",lead_vintage)
                if "vintage_in_work_business_home_loan_senp_from" in data:
                    lead_vintage = lead_sst.filtered(lambda d: d.vintage_in_work_business_home_loan_senp == True and d.vintage_in_work_business_home_loan_senp_from < data["vintage_in_work_business_home_loan_senp_from"])
                    # lead_vintage = lead_sst.search([("vintage_in_work_business_home_loan_senp","=",True),("vintage_in_work_business_home_loan_senp_from","<",data["vintage_in_work_business_home_loan_senp_from"])])
                    print("lead_vintage@###################3333333333",lead_vintage)
                if "vintage_in_work_business_home_loan_salaried_from" in data:
                    lead_vintage = lead_sst.filtered(lambda d: d.vintage_in_work_business_home_loan_salaried == True and d.vintage_in_work_business_home_loan_salaried_from < data["vintage_in_work_business_home_loan_salaried_from"])
                    # lead_vintage = lead_sst.search([("vintage_in_work_business_home_loan_salaried","=",True),("vintage_in_work_business_home_loan_salaried_from","<",data["vintage_in_work_business_home_loan_salaried_from"])])
                    print("lead_vintage@###################444444444",lead_vintage)
                if "vintage_in_work_business_lap_senp_from" in data:
                    lead_vintage = lead_sst.filtered(lambda d: d.vintage_in_work_business_lap_senp == True and d.vintage_in_work_business_lap_senp_from < data["vintage_in_work_business_lap_senp_from"])
                    # lead_vintage = lead_sst.search([("vintage_in_work_business_lap_senp","=",True),("vintage_in_work_business_lap_senp_from","<",data["vintage_in_work_business_lap_senp_from"])])
                    print("lead_vintage@#################555555555",lead_vintage)
                if "vintage_in_work_business_lap_salaried_from" in data:
                    lead_vintage = lead_sst.filtered(lambda d: d.vintage_in_work_business_lap_salaried == True and d.vintage_in_work_business_lap_salaried_from < data["vintage_in_work_business_lap_salaried_from"])
                    # lead_vintage = lead_sst.search([("vintage_in_work_business_lap_salaried","=",True),("vintage_in_work_business_lap_salaried_from","<",data["vintage_in_work_business_lap_salaried_from"])])    
                    print("lead_vintage@###################6666666666666666666666",lead_vintage)
                # if lead_vintage:
                print("lead_lead_vintage@@@@@@@@@@@@@@@@@@dddddddddddddd",lead_vintage)
                lead_records.lenders_data = [(6, 0, lead_vintage.ids)]    
            
            print("lead_lead_vintage@@@@@@@@@@@@@@@@@@777777777777777777",lead_records.lenders_data)


            owned_rented = lead_records.lenders_data
            if "address_residence_type_pl" in data:   
                owned_rent = owned_rented.filtered(lambda l: l.applicable_for_unsecured_loan_personal_loan == data["address_residence_type_pl"])
                print("owned_rent@@@@@@@@@@@@@@@@@@@1111111111111",owned_rent) 
            if "address_residence_type_bl" in data: 
                owned_rent = owned_rented.filtered(lambda l: l.applicable_for_unsecured_loan_business_loan == data["address_residence_type_bl"])
                print("owned_rent@@@@@@@@@@@@@@@@@@@2222222222222222",owned_rent) 
            if owned_rent:
                print("owned_rent@@@@@@@@@@@@@@@@@@@3333333333333333",owned_rent)   
                lead_records.lenders_data = [(6, 0, owned_rent.ids)]        
                print("owned_rent@@@@@@@@@@@@@@@@@@@4444444444444444",lead_records.lenders_data)


                # today = date.today()
                # age = today.year - birthDate.year - ((today.month, today.day) < (birthDate.month, birthDate.day))
                # return 60 > age > 26
                # print(calculateAge(date(1987, 2, 3))) (edited)
            ages = lead_records.lenders_data   
            print("ages@@@@@@@@@@@@@@ddddddddddddddd",ages)
            if "age" in data:
                today = date.today()
                print("today^^^^^^^^^^^^^^^^^^^^^",today)
                birthDate = data["age"]
                birthDate = datetime.strptime(birthDate, '%Y-%M-%d')
                print("birthDate########################",birthDate)

                age = today.year - birthDate.year - ((today.month, today.day) < (birthDate.month, birthDate.day))
                print("age####################",age)
                ages_data = ages.filtered(lambda m: m.age_from < age < m.age_to)

                # search([("age_unsecured_loan_customer_age_SENP_from", "<", age),("age_unsecured_loan_customer_age_SENP_to",">",age)])               
                print("ages_data#############1111111111111111",ages_data)

            if ages_data:
                print("owned_rent@@@@@@@@@@@@@@@@@@@999999999999999",ages_data)   
                lead_records.lenders_data = [(6, 0, ages_data.ids)]        
                print("owned_rent@@@@@@@@@@@@@@@@@@@kkkkkkkkkkkkkkkk",lead_records.lenders_data)


            tenture = lead_records.lenders_data
            if "tenor" in data:
                tenore = data["tenor"]
                tenure_lender = tenture.filtered(lambda k: k.tenor_from  <  tenore < k.tenor_to)
            if tenure_lender:
                print("tenure_lender@@@@@@@@@@@@@@@@@@@999999999999999",tenure_lender)   
                lead_records.lenders_data = [(6, 0, tenure_lender.ids)]

            loan = lead_records.lenders_data
            if "loan_amount" in data:
                loan_data = data["loan_amount"]
                loan_lender = loan.filtered(lambda y: y.loan_amount_from < loan_data < y.loan_amount_to)

            if loan_lender:
                lead_records.lenders_data = [(6, 0, loan_lender.ids)]

            credit = lead_records.lenders_data   
            if "bureau_score" in data:
                credit_data = data["bureau_score"]
                credit_lender = credit.filtered(lambda g: g.bureau_from < credit_data <  g.bureau_to)
            if credit_lender:
                print("loan_lender@@@@@@@@@@@@@@@@@@@999999999999999",credit_lender)   
                lead_records.lenders_data = [(6, 0, credit_lender.ids)]

            # for equip in lead_records.lender_data:
            #     if equip.Account_Status == "ACTIVE":
            #         if data_loan_type == "BL" and equip.Account_Type == "61":



            # enqui = lead_records.lenders_data
            # enqui_lender = enqui.filtered(lambda g: g.enquiry == True and g.enquiry_from > lead_records.enquire)


            if "pan_card" in data:
                if data["pan_card"] != lead_records.IncomeTaxPan:
                    lead_records.pan_card_verify = True
            if "aadhar_card" in data:
                if data["aadhar_card"] != lead_records.Universal_ID_Number:
                    lead_records.aadhar_card_verify = True        

            if "date_of_birth" in data:
                if data["date_of_birth"] != lead_records.Date_Of_Birth_Applicant:
                    lead_records.Date_Of_Birth_verify = True

            if "mobile_number" in data:
                if data["mobile_number"] != lead_records.MobilePhoneNumber:
                    lead_records.mobile_phone_verify = True  

            if "email_id" in data:
                if data["email_id"] != lead_records.EMailId:
                    lead_records.email_verify = True

            for lenders in lead_records.lender_data:
                for payment in lenders.payment_hist:
                    if int(payment.Days_Past_Due) >= 0 and int(payment.Days_Past_Due) <= 30:
                        lead_records.dps_one = True
                    if int(payment.Days_Past_Due) >= 31 and int(payment.Days_Past_Due) <= 60:
                        lead_records.dps_two = True
                    if int(payment.Days_Past_Due) >= 61 and int(payment.Days_Past_Due) <= 90:
                        lead_records.dps_three = True
                    if int(payment.Days_Past_Due) >= 91 and int(payment.Days_Past_Due) <= 10000:
                        lead_records.dps_four = True 

            emi_total = 0
            amount_over_due = 0 
            settlement_amonunt = 0
            for lend in lead_records.lender_data:
                print("lend.Account_Status@@@@@@@@@@@@@",lend.Account_Status)
                if lend.Account_Status in ['11','71','78','80','82','83','84','21','22','23','24','25']:
                    if lend.Scheduled_Monthly_Payment_Amount:
                        emi_total = emi_total + int(lend.Scheduled_Monthly_Payment_Amount)
                    if lend.Amount_Past_Due:    
                        amount_over_due = amount_over_due + int(lend.Amount_Past_Due)
                    if lend.Settlement_Amount:    
                        settlement_amonunt = settlement_amonunt + int(lend.Settlement_Amount)
                lead_records.emi_total_emi = emi_total 
                lead_records.total_amount_overdue = amount_over_due
                lead_records.total_settlement_amount = settlement_amonunt



            if not lead_records.lender_data:
                lead_records.ntc_notify = True

            for subdbt in lead_records.lender_data:
                for susss in subdbt.payment_hist:
                    if susss.Days_Past_Due == "sub":
                        lead_records.sub_notify = True
                    if susss.Days_Past_Due == "dbt":
                        lead_records.doubtful = True 
                    if susss.Days_Past_Due == "lss":
                        lead_records.lss = True        
                if subdbt.Account_Status in ['53','54','55','56','57','58','59','60','61','62','63','76','77','79','85','81','86','87','88','94','90','91']:
                    lead_records.suitfilled = True
                if subdbt.Account_Status in ['89','93','97','64','65','66','67','68','69','70','72','73','74','75','76','77','79','85','81','86','87','88','94','90','91']:
                    lead_records.Willful = True  




            # abb_data = lead_records.lenders_data
            # print("jjjjjjjjjjjjjjjjjjjjjjjjj",abb_data.abb_business_loan_dates.split(','))
            # dates_abb = abb_data.abb_business_loan_dates.split(',')
                       

            fi_loop = lead_records.lenders_data.mapped("id")
            for hhss in lead_records.lenders_data:
                print("bbbbbbbbbbbbbbbbbbbbbb",fi_loop)
                if hhss.id in fi_loop:
                    print("hhssmmmmmmmmmmmmmmmmmm",hhss)
                    print("hhsshhss.abb_business_loan_dates$$$$$$$$$$$$$$$$$$$$$4",hhss.abb_business_loan_dates)
                    dates_abb = hhss.abb_business_loan_dates.split(',')
                    # df = pd.read_excel("", )    
                    # print("df######################",df.shape)
                    # loc = ("/home/anuj/Desktop/workspace15/BSA_7.xlsx")          #Giving the location of the file 
                    loc = ("/opt/odoo/demofile_%s_%s.xlsx" % (data_lead_id, data_loan_type))
                      
                    wb = xl.open_workbook(loc)                    #opening & reading the excel file
                    s1 = wb.sheet_by_name("Daily Balances")                     #extracting the worksheet
                      
                    print("No. of rows:", s1.nrows)               #Counting & Printing thenumber of rows & columns respectively
                    print("No. of columns:", s1.ncols)
                    ddgt = [] 
                    for ddt in range(s1.ncols - 1):
                        total_per_month = 0
                        print("ddtEEEEEEEEEEEEEEEEEE",int(ddt) + 1)
                        for dat in dates_abb:
                            print("datmmmmmmmmmmmmmmmmmmm",int(dat) + 4)
                            print("cellvalueuuuuuuuuuuuuuuuuuuuu",s1.cell_value(int(dat) + 3,int(ddt) + 1))
                            value_per_day = s1.cell_value(int(dat) + 3,int(ddt) + 1)
                            if value_per_day: 
                                total_per_month = total_per_month + float(value_per_day) 
                        if total_per_month:
                            total_per_month = total_per_month /  len(dates_abb) 
                            print("average_abbb_per_monthiiiiiiiiiiiiiiiiiiii",total_per_month)
                        ddgt.append(total_per_month) 
                    print("ddgt@@@@@@@@@@@@@@",ddgt)
                    total_abb_sixmonth = 0 
                    for overall in ddgt[-6:]:
                        print("overall$$$$$$$$$$$$$$$$$$$$",overall)
                        total_abb_sixmonth = total_abb_sixmonth + overall
                    average_abb_six_month = total_abb_sixmonth / 6
                    print("average_abb_six_month################",average_abb_six_month)

                    s2 = wb.sheet_by_name("Cheque Bounce") 
                    print("No2222222222222. of rows:", s2.nrows)               #Counting & Printing thenumber of rows & columns respectively
                    print("No222222222222. of columns:", s2.ncols)
                    cheque_count = 0
                    for chequecol in range(3, s2.nrows):
                        print("chequecol##############",chequecol)
                        cheque_data = s2.cell_value(chequecol,5)
                        print("cheque_data#1,5,10,15,20,25################",cheque_data)
                        if cheque_data:
                            cheque_count = cheque_count + 1
                    print("cheque_count##################",cheque_count) 

                    s3 = wb.sheet_by_name("CAM Analysis") 
                    print("No333333333. of rows:", s3.nrows)
                    print("No333333333333. of columns:", s3.ncols)

                    debit_transaction = s3.cell_value(s3.nrows - 1, 6)
                    print("debit_transaction###################",debit_transaction)

                    credit_transaction = s3.cell_value(s3.nrows - 1,1)
                    print("credit_transaction##################",credit_transaction)

                    credit_submission = s3.cell_value(s3.nrows - 1,2)
                    print("credit_submission##################",credit_submission)


                    salary_list = []
                    average_salary = 0
                    salary_data = 0
                    s4 = wb.sheet_by_name("Salary")
                    print("No444444444444. of rows:", s4.nrows)
                    print("No44444444444444. of columns:", s4.ncols)
                    for data in range(4, s4.nrows):
                        print("data@@@@@@@@@@@@@@@@@",data)
                        salary = s4.cell_value(data, 1)
                        print("salary#################",salary)
                        if not salary:
                            print("ccccccccccccccccccccccc",s4.cell_value(data, 0))
                            salary_list.append(s4.cell_value(data, 0))
                        average_salary = s4.cell_value(data, 2)
                        print("average_salary#################3",average_salary)
                    if average_salary:
                        salary_data = average_salary
                        print("salary_listRRRRRRRRRRRRRRRRRRRRRR",salary_list)

                    s5 = wb.sheet_by_name("Fraud Indicators") 
                    print("No555555555555555. of rows:", s5.nrows)
                    print("No555555555555. of columns:", s5.ncols)
                    fraud_indicate = s5.cell_value(s3.nrows - 3,3)
                    print("fraud_indicate@@@@@@@@@@@@@@",fraud_indicate)
                    if fraud_indicate == "Y":
                        print("fraud in BSAyyyyyyyyyyyyyyyyyy",fraud_indicate)


                    ROI = []
                    ROI.append(hhss.rate_of_interest_from)
                    ROI.append(hhss.rate_of_interest_to)
                    emil_range = []
                    elegible_loan = [] 
                    live_obligation = 0

                    for alls in ROI:
                        print("alls##################kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk",alls)
                        foir = hhss.foir_from
                        print("salary_data$$$$$$$$$$$$$$$$$$$$",salary_data)
                        net_elegible_income = float(foir) * float(salary_data)
                        # max_emi = data["max_emi"]
                        print("net_elegible_income$$$$$$$$$$$$$$$$$$iiiiiiiiiiiiiiii$$$",net_elegible_income)
                        # Solution = np.pmt(0.10 / 12, 12 * 12,  10, 000) 
                        # tenure = data["tenor_unsecured_loan_min_tenor_bl"]
                        print("tenure$$$$$$$$$$$$$$$$$$$$$",tenore)
                        Solution = npf.pmt(alls/12, tenore ,-100000)
                        print("Solution#####32222222222222222222",Solution)
                        emil_range.append(Solution)

                        # print("Solution####################",net_elegible_income/Solution)
                        elegible_loan_amount = net_elegible_income/Solution
                        elegible_loan.append(elegible_loan_amount)
                    financial_bre = request.env["financial.finbii"].sudo().create({
                        "financial_institue" : hhss.fincial_institutions.id,
                        "loan_type" : data_loan_type,
                        "average_abb_six_month" : average_abb_six_month,
                        "cheque_count" : cheque_count,
                        "debit_transaction" : debit_transaction,
                        "credit_transaction" : credit_transaction,
                        "credit_submission" : credit_submission,
                        "roi_range" : ROI,
                        "average_salary" : average_salary,
                        "fraud_indicate" : fraud_indicate,
                        "Solution" : emil_range,
                        "elegible_loan_amount" : elegible_loan,
                    })
                    
                    lead_records.finance_for_bre = [(4, financial_bre.id)]

            # tmp = df == 'X' # boolean mask
            # tmp = tmp[list(tmp.columns[-1]) + tmp.columns.tolist()[:-1]] # shift the order of columns to 1 ahead
            # tmp.columns = df.columns # restore names order in the mask
            # df[tmp] = 'S' # setting the s value to the cell right after the 'X'


                 

            # for amot in lead_records.lender_data:
            #     amount_over_due = amount_over_due + amot.Amount_Past_Due



            # pan_card = ""
            # Aadhar
            # Date Of birth
            # Telephone Number
            # Email Id
            # Address(Residence,Office)
            # DPD
            # DPD 2
            # DPD 3
            # DPD 4
            # EMI(Live Loans)
            # Amount Overdue
            # Write Off
            # Setteled
            # Restructured
            # Enquiries    

            args = {'success': True, 'message': 'Success', 'Lender':lead_records.lenders_data.mapped("fincial_institutions")}
            return args
