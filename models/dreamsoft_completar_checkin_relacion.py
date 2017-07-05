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

class hotel_completar_checkin_relacion(models.Model):

	_name = 'dreamsoft.completar_checkin_relacion'

	relacion_completar_checkin_id = fields.Many2one('dreamsoft.completar_checkin', u'Acompañante')
	name = fields.Many2one('res.partner', u'Acompañante')
	reservation_id = fields.Many2one('hotel.reservation', 'Reservacion')

	@api.model
	def create(self, vals, check=True):
		"""
		sobreescribimos el metodo create para que los 
		usuarios no puedan sino crear un solo registro 
		para la configuracion de los horarios.
		
		@param self: The object pointer
		@param vals: dictionary of fields value.
		@return: new record set for hotel folio.
		"""
		if self._context:
			keys = self._context.keys()
			if 'reserva_id' in keys:
				vals['reservation_id'] = self._context['reserva_id']
		return  super(hotel_completar_checkin_relacion, self).create(vals)

