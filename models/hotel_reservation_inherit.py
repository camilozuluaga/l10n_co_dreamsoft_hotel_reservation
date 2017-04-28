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

class hotel_reservation_inherit(models.Model):

	_name = 'hotel.reservation'

	_inherit = 'hotel.reservation'

	def _obtener_arriban_hoy(self):
		fecha_hoy = datetime.date.today()
		fecha_hoy = fecha_hoy.strftime(DEFAULT_SERVER_DATE_FORMAT)
		for record in self:
			if record.fecha_entrada == fecha_hoy:
				record.arriban_hoy = True


	fecha_entrada = fields.Date('Fecha prevista de llegada', required=True)
	fecha_salida = fields.Date('Fecha prevista de salida', required=True)
	arriban_hoy = fields.Boolean(compute='_obtener_arriban_hoy', store=True, default=False)
	adults=fields.Integer('Adultos',default=1)

	@api.onchange('fecha_entrada')
	def on_change_fecha_entrada(self):
		fecha_hoy = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
		if self.fecha_entrada:
			fecha_entrada = self.fecha_entrada+' '+self.env['room.reservation.summary'].consultar_registro_horario()[0]+':00' 
			self.checkin = self.env['dreamsofft.hotel_config'].fecha_UTC(fecha_entrada)

			if self.checkin < fecha_hoy:
				raise except_orm(_('Warning'), _('Fecha de Check In \
					No puede ser menor a la fecha de hoy.'))


	@api.onchange('fecha_salida')
	def on_change_fecha_salida(self):

		fecha_hoy = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
		if self.fecha_salida:
			fecha_salida = self.fecha_salida+' '+self.env['room.reservation.summary'].consultar_registro_horario()[1]+':00'
			self.checkout = self.env['dreamsofft.hotel_config'].fecha_UTC(fecha_salida)

			if self.checkout < fecha_hoy:
				raise except_orm(_('Warning'), _('Fecha de Check Out \
					No puede ser menor a la fecha de hoy.'))

			if self.checkout and self.checkin:
				if self.checkout < self.checkin:
					raise except_orm(_('Warning'), _('Checkout date \
							should be greater than Checkin date.'))


	@api.model
	def actualizar_arriban_hoy(self, ids=None):
		"""
			tarea programada que lo que hace es actualizar el estado 
			del campo arriban hoy que es un booleano que lo que 
			hace es que el boton de crear folio no aparezca si esta e falso
			y este campo se crea por defecto en falso para que no se visible 
			el boton aun.
		"""
		fecha_hoy = datetime.date.today()
		fecha_hoy = fecha_hoy.strftime(DEFAULT_SERVER_DATE_FORMAT)
		if not ids:
			entradas_hoy_ids = self.search([('fecha_entrada', '=', fecha_hoy)])
		return entradas_hoy_ids.write({'arriban_hoy': True})



	@api.multi
	def done(self):

		"""
			Funcion para llamar al modelo donde se va hacer el registro de las personas cuando llegan al hotel, 
			este funcion funciona cuando se da click en el boton Crear Folio.
		"""
		#self._create_folio()
		ctx = dict(self.env.context).copy()
		ctx.update({'reserva_id': self.ids[0]})
		return {
			'name': 'Registro detallado',
			'res_model': 'dreamsoft.reserva_acompanantes',
			'type': 'ir.actions.act_window',
			'context': ctx,
			'view_id': False,
			'view_mode': 'form',
			'view_type': 'form',
			'target': 'new'
		}	


	@api.constrains('adults')
	def verificar_adultos(self):

		if self.adults<=0:
			raise except_orm(_('Warning'), _('Debe de haber como minimo un adulto'))
