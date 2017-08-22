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
from datetime import datetime
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
	reservation_id = fields.Many2one('hotel.reservation', 'Reservacion')
	name = fields.Many2one('res.partner', 'Huesped', readonly=True)
	street_partner = fields.Char(string='Direccion', related='name.street', readonly=True, store=False)
	telefono_partner = fields.Char(string='Telefono', related='name.phone', readonly=True, store=False)
	email_partner = fields.Char(string='Email', related='name.email', readonly=True, store=False)
	pais_partner = fields.Char(string='Pais', related='name.country_id.name', readonly=True, store=False)
	state_partner = fields.Char(string='Estado', related='name.state_id.name', readonly=True, store=False)
	city_partner = fields.Char(string='Ciudad', related='name.xcity.name', readonly=True, store=False)
	date_partner = fields.Date(string='Fecha de Nacimiento', related='name.xbirthday', readonly=True, store=False)
	reservation_checkin = fields.Datetime(string='Fecha de Entrada', related='reservation_id.checkin', readonly=True, store=False)
	reservation_checkout = fields.Datetime(string='Fecha de Salida', related='reservation_id.checkout', readonly=True, store=False)
	dias_hospedado= fields.Integer(u'Días Hospedado', readonly=True, store=False)
	si_envio_correo = fields.Boolean('Si')
	no_envio_correo = fields.Boolean('No')
	reservation_room = fields.Char('Room', readonly=True, store=False)
	es_menor= fields.Boolean('Menor de Edad', default=False)

	@api.model
	def create(self, vals):
		partner_id=''
		if not vals:
			vals = {}

		if self._context:
			keys = self._context.keys()
			if 'partner_id' in keys:
				_logger.info('el paciente')
				_logger.info(self._context['partner_id'])
				partner_id = self._context['partner_id']


		keys = vals.keys()

		partner_name_id = self.env['res.partner'].search([('id', '=', partner_id)]).es_menor
			
		vals['es_menor'] = partner_name_id
		if 'reservation_id' in keys:

			room_reservation_line_id = self.env['hotel_reservation.line'].search([('line_id', '=', vals['reservation_id'])])
			
			if room_reservation_line_id:

				producto_id = self.env['product.template'].search([('name', '=', room_reservation_line_id.name)])

				if producto_id:

					room = self.env['hotel.room'].search([('product_id', '=', producto_id.id)])  

					if room:

						if ((len(vals['acompanantes_ids']) + 1) > room.capacity):

							if room.additional_people:

								if ((len(vals['acompanantes_ids']) + 1) > (room.capacity + room.quantity_people)):

									raise ValidationError(_('La capacidad no concuerda con la de la habitacion hay mas personas'))	
							else:
									raise ValidationError(_('La capacidad no concuerda con la de la habitacion hay mas personas'))

		return super(hotel_completar_checkin, self).create(vals)


	@api.model
	def default_get(self, fields):
		if self._context is None:
			self._context = {}
		res = super(hotel_completar_checkin, self).default_get(fields)

		name_room=''

		if self._context:
			keys = self._context.keys()
			if 'partner_id' in keys:
				res['name'] = self._context['partner_id']
				res['reservation_id'] = self._context['reserva_id']
				room_reservation_id = self.env['hotel.reservation'].search([('id', '=', self._context['reserva_id'])])
				
				for x in room_reservation_id:
					room_reservation_line_id = self.env['hotel_reservation.line'].search([('line_id', '=', x.id)])
					name_room= room_reservation_line_id.name
				res['reservation_room']= str(name_room)
				date_checkin=None
				date_checkout=None
				for x in room_reservation_id:
					date_checkin= x.checkin
					date_checkout= x.checkout
				res['dias_hospedado'] = self.calcular_dias(date_checkin[0:10], date_checkout[0:10])
				
		return res



	#Funcion para calcular la diferencia entre dos fechas en dias
	def calcular_dias(self, date_checkin, date_checkout):
		dia_calculado=0
		if date_checkin and date_checkout:
			fecha_entrada = datetime.strptime(str(date_checkin), '%Y-%m-%d')
			fecha_salida = datetime.strptime(str(date_checkout), '%Y-%m-%d')
			dias = fecha_salida - fecha_entrada
			dias_calculados = str(dias)
			dias_calculados= dias_calculados.split(' ')
			dia_calculado= int(dias_calculados[0])
			
		return dia_calculado


	def refresh(self):
		#raise NotImplementedError("Ids is just there by convention! Please don't use it.")		self._cr.execute("SELECT * FROM hotel_reservation")
		return self.env.cr.execute('SELECT * FROM hotel_reservation')

	