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


	fecha_entrada = fields.Date('Fecha prevista de llegada', required=True, store=True)
	fecha_salida = fields.Date('Fecha prevista de salida', required=True, store=True)
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
							Hola'))


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
		self._create_folio()
		ctx = dict(self.env.context).copy()	
		ctx.update({'reserva_id': self.ids[0]})
		ctx.update({'partner_id': self.partner_id.id})
		_logger.info(self.partner_id.id)
		return {
			'name': 'Registro detallado',
			'res_model': 'dreamsoft.completar_checkin',
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



	@api.constrains('checkin', 'checkout')
	def check_in_out_dates(self):
		"""
		When date_order is less then checkin date or
		Checkout date should be greater than the checkin date.
		"""
		if self.checkout and self.checkin:
			if self.checkin[0:10] < self.date_order[0:10]:
				raise except_orm(_('Warning'), _('Checkin date should be \
				greater than the current date.'))
			if self.checkout < self.checkin:
				raise except_orm(_('Warning'), _('Checkout date \
				should be greater than Checkin date.'))


	@api.model
	def create(self, vals):
		"""
		Overrides orm create method.
		@param self: The object pointer
		@param vals: dictionary of fields value.
		"""
		if not vals:
			vals = {}
		if self._context is None:
			self._context = {}
			
		vals['fecha_entrada'] = vals['checkin']
		vals['fecha_salida'] = vals['checkout']

		return super(hotel_reservation_inherit, self).create(vals)


	def name_room(self, list_reserva):
		name_room=''
		if list_reserva:
			if len(list_reserva) == 1:
				_logger.info('vamos bien')
				hotel_room_ids = self.env['hotel.room'].search([('id', '=', list_reserva[0])])
				product_id= hotel_room_ids.product_id
				for room in product_id:
					for room_name in product_id:
						name_room=room_name.name
						_logger.info(name_room)
						return name_room

		return name_room


class HotelReservationLine_inherit(models.Model):

	_name = "hotel_reservation.line"
	_inherit = 'hotel_reservation.line'
	
	@api.onchange('categ_id')
	def on_change_categ(self):

		hotel_room_obj = self.env['hotel.room']
		hotel_room_ids = hotel_room_obj.search([('categ_id', '=', self.categ_id.id)])

		hotel_reservation= self.env['hotel_reservation.line']
		hotel_reservation_ids= hotel_room_obj.search([('categ_id', '=', self.categ_id.id)])
		for room in hotel_room_ids:
			_logger.info(room.product_id)

		hotel_room_obj = self.env['hotel.room']
		hotel_room_ids = hotel_room_obj.search([('categ_id', '=',
												 self.categ_id.id)])
		room_ids = []

		for room in hotel_room_ids:
			
			assigned = False
			for line in room.room_reservation_line_ids:
				if line.status != 'cancel':
					if (line.check_in <= self.line_id.checkin <=
						line.check_out) or (line.check_in <=
											self.line_id.checkout <=
											line.check_out):
						assigned = True
			for rm_line in room.room_line_ids:
				if rm_line.status != 'cancel':
					if (rm_line.check_in <= self.line_id.checkin <=
						rm_line.check_out) or (rm_line.check_in <=
											   self.line_id.checkout <=
											   rm_line.check_out):
						assigned = True
			if not assigned:
				_logger.info(room.id)
				room_ids.append(room.id)

		_logger.info('Empezando modificacion')
		date_chekin = self.line_id.checkin
		date_checkout = self.line_id.checkout
		#donde van a ir las habitaciones
		name_room=[]

		#buscamos las reservas que contengan esta fecha
		room_reservation_ids = self.env['hotel.reservation'].search([('checkin', '>=', date_chekin), ('checkout', '<=', date_checkout), ('state', '=', 'draft')])
		_logger.info(room_reservation_ids)

		if self.reserve:
			_logger.info('estamos de una que estamos editando')
		else:
			#Condicion si hay una reserva en draft con las mismas fechas
			if room_reservation_ids:
				#buscamos la relacion en reservation line para obtener el nombre de la habitacion
				for x in room_reservation_ids:
					room_reservation_line_ids = self.env['hotel_reservation.line'].search([('line_id', '=', x.id)])
					_logger.info(room_reservation_line_ids)

					name_room.append(room_reservation_line_ids.name)

				room_reservation_id = self.retornar_room_id(name_room)

				for x in room_reservation_id:
					if x.id in room_ids:
						room_ids.remove(x.id)

		domain = {'reserve': [('id', 'in', room_ids)]}
		return {'domain': domain}

	#retonar el room de acuerdo al nombre de la habitacion
	def retornar_room_id(self, name_list):
		room_ids=''
		_logger.info('entramos al metodo')
		if name_list:
			if len(name_list) > 0:
				for x in range(len(name_list)):
					_logger.info(name_list[x])
					template_ids= self.env['product.template'].search([('name', '=', str(name_list[x]))])
					_logger.info(template_ids)
					for i in template_ids:
						product_id = self.env['product.product'].search([('product_tmpl_id', '=', i.id)])
						_logger.info(product_id)
						for z in product_id:
							room_ids =self.env['hotel.room'].search([('product_id', '=', z.id)])

		return room_ids





	@api.multi
	def write(self, vals):
		_logger.info(vals)
		reservation_reserve_id =vals['reserve']
		reserver_id= reservation_reserve_id[0]
		reserver_ids= reserver_id[2]
	
		name_room = self.env['hotel.reservation'].name_room(reserver_ids)
		vals['name']=name_room

		return super(HotelReservationLine_inherit, self).write(vals)

	@api.model
	def create(self, vals):
		_logger.info(vals)
		reservation_reserve_id =vals['reserve']
		reserver_id= reservation_reserve_id[0]
		reserver_ids= reserver_id[2]
	
		name_room = self.env['hotel.reservation'].name_room(reserver_ids)
		vals['name']=name_room

		return super(HotelReservationLine_inherit, self).create(vals)