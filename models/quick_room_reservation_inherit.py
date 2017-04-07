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

class quick_room_reservation_inherit(models.TransientModel):

	_name = 'quick.room.reservation'

	_inherit = 'quick.room.reservation'


	fecha_entrada = fields.Date('Fecha Entrada', required=True)
	fecha_salida = fields.Date('Fecha Salida', required=True)



	@api.onchange('fecha_entrada')
	def on_change_fecha_entrada(self):
		dt_value = datetime.datetime.strptime(self.fecha_entrada, '%Y-%M-%d') + datetime.timedelta(days=1)
		self.fecha_salida = dt_value
		self.check_in = self.fecha_entrada+' '+self.env['room.reservation.summary'].consultar_registro_horario()[0]+':00'

	@api.onchange('fecha_salida')
	def on_change_fecha_salida(self):
		if self.fecha_salida:
			self.check_out = self.fecha_salida+' '+self.env['room.reservation.summary'].consultar_registro_horario()[0]+':00'


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
		res = super(quick_room_reservation_inherit, self).default_get(fields)
		if self._context:
			keys = self._context.keys()
			if 'date' in keys:
				res.update({'fecha_entrada': self._context['date'][0:10]})
		return res