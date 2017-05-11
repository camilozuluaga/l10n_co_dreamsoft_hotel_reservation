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
from dateutil.relativedelta import relativedelta
import urllib2
from odoo.exceptions import except_orm, ValidationError
from odoo.tools import misc, DEFAULT_SERVER_DATE_FORMAT,DEFAULT_SERVER_DATETIME_FORMAT
from odoo import models, fields, api, _
from odoo import workflow
from decimal import Decimal
import logging
_logger = logging.getLogger(__name__)

class hotel_completar_checkin(models.Model):

	_name = 'dreamsoft.completar_checkin'


	acompanantes_ids = fields.One2many('dreamsoft.completar_checkin_relacion', 'relacion_completar_checkin_id', u'Acompañantes')






	@api.model
	def default_get(self, fields):

		if self._context is None:
			self._context = {}

		res = super(hotel_completar_checkin, self).default_get(fields)
		usuario_principal=[]

		if self._context:
			keys = self._context.keys()
			if 'partner_id' in keys:

				usuario_principal.append((0,0,{'name' : self._context['partner_id'], 'reservation_id': self._context['reserva_id']}))
			res['acompanantes_ids'] = usuario_principal
		return res