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

class room_reservation_summary_inherit(models.Model):

	name = 'room.reservation.summary'

	_inherit = 'room.reservation.summary'


	fecha_desde = fields.Date('Fecha de', default=(lambda *a: time.strftime(DEFAULT_SERVER_DATE_FORMAT)))
	fecha_hasta = fields.Date('Fecha hasta', default=(lambda *a: time.strftime(DEFAULT_SERVER_DATE_FORMAT)))



	def consultar_registro_horario(self):
		confi_horario_id = self.env['dreamsoft.configuracion.periodo_reserva'].search([]).id
		horarios_confi = []
		if confi_horario_id:
			for horarios in self.env['dreamsoft.configuracion.periodo_reserva'].browse(confi_horario_id):
				horarios_confi.append(horarios.hora_entrada)
				horarios_confi.append(horarios.hora_salida)
			return horarios_confi
		horarios_confi.append('00:00')
		horarios_confi.append('00:00')
		return horarios_confi


	@api.onchange('fecha_desde')
	def on_change_fecha_desde(self):
		fecha_desde = self.fecha_desde +' '+ self.consultar_registro_horario()[0]+':00'
		self.date_from = fecha_desde
			
	@api.onchange('fecha_hasta')
	def on_change_fecha_hasta(self):
		fecha_hasta = self.fecha_hasta +' '+ self.consultar_registro_horario()[1]+':00'
		_logger.info(fecha_hasta)
		self.date_to = fecha_hasta
			


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
		res = super(room_reservation_summary_inherit, self).default_get(fields)
		# Added default datetime as today and date to as today + 30.
		from_dt = datetime.date.today()
		dt_from = from_dt.strftime(DEFAULT_SERVER_DATE_FORMAT)
		to_dt = from_dt + relativedelta(days=30)
		dt_to = to_dt.strftime(DEFAULT_SERVER_DATE_FORMAT)
		res.update({'fecha_desde': dt_from, 'fecha_hasta': dt_to})

		if not self.date_from and self.date_to:
			date_today = datetime.datetime.today()
			first_day = datetime.datetime(date_today.year,
										  date_today.month)
			first_temp_day = first_day + relativedelta(months=1)
			last_temp_day = first_temp_day - relativedelta(days=1)
			last_day = datetime.datetime(last_temp_day.year,
										 last_temp_day.month,
										 last_temp_day.day)
			date_froms = first_day.strftime(DEFAULT_SERVER_DATE_FORMAT)
			date_ends = last_day.strftime(DEFAULT_SERVER_DATE_FORMAT)
			res.update({'fecha_desde': date_froms, 'fecha_hasta': date_ends})
		return res
