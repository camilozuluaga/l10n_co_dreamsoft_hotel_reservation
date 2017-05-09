# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-Today Serpent Consulting Services PVT. LTD.
#    (<http://www.serpentcs.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
# ---------------------------------------------------------------------------

import time
import datetime
import urllib2
from odoo.exceptions import except_orm, ValidationError
from odoo.tools import misc, DEFAULT_SERVER_DATETIME_FORMAT
from odoo import models, fields, api, _
from odoo import workflow
from decimal import Decimal
import logging
_logger = logging.getLogger(__name__)


class reserva_acompanantes_checkin(models.Model):


	_name = 'dreamsoft.reserva_acompanantes'
	_rec_name_ = 'checkin_ids'

	checkin_ids = fields.One2many('dreamsoft.acompanantes_reserva','id_res_partner', string=u'Acompañantes')
	


	@api.model
	def default_get(self, fields):
		"""
		To get default values for the object.
		@param self: The object pointer.
		@param fields: List of fields for which we want default values
		@return: A dictionary which of fields with values.
		"""
		if self._context is None:
			self._context = {}
		res = super(reserva_acompanantes_checkin, self).default_get(fields)
		_logger.info(self._context)
		usuario_principal=[]
		if self._context:
			keys = self._context.keys()
			if 'partner_id' in keys:
				usuario_principal.append({'id_res_partner' : self._context['partner_id']}))
			product_obj = self.pool.get('res.partner')
			product_id = product_obj.search(cr, uid, [('id','=',self._context['partner_id'])])
			_logger.info(product_id)
			res['checkin_ids'] = usuario_principal[0]
		return res

