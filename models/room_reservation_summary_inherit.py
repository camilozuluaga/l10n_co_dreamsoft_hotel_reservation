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
import pytz
import logging
_logger = logging.getLogger(__name__)
from datetime import datetime as dtime
from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as dt
from odoo.exceptions import except_orm, ValidationError

class room_reservation_summary_inherit(models.Model):

	_name = 'room.reservation.summary'

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
		self.date_from = self.env['dreamsofft.hotel_config'].fecha_UTC(fecha_desde)
			
	@api.onchange('fecha_hasta')
	def on_change_fecha_hasta(self):
		fecha_hasta = self.fecha_hasta +' '+ self.consultar_registro_horario()[1]+':00'
		self.date_to = self.env['dreamsofft.hotel_config'].fecha_UTC(fecha_hasta)
			


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

	@api.onchange('date_from', 'date_to')
	def get_room_summary(self):
			'''
			@param self: object pointer
			 '''
			datos = []
			res = {}
			all_detail = []
			room_obj = self.env['hotel.room']
			reservation_line_obj = self.env['hotel.room.reservation.line']
			folio_room_line_obj = self.env['folio.room.line']
			user_obj = self.env['res.users']
			date_range_list = []
			main_header = []
			summary_header_list = ['Rooms']
			if self.date_from and self.date_to:
					if self.date_from > self.date_to:
							raise except_orm(_('User Error!'),
															 _('Please Check Time period Date \
															 From can\'t be greater than Date To !'))
					timezone = pytz.timezone(self._context.get('tz', False))
					d_frm_obj = dtime.strptime(self.date_from, dt)\
							.replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone)
					d_to_obj = dtime.strptime(self.date_to, dt)\
							.replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone)
					temp_date = d_frm_obj
					while(temp_date <= d_to_obj):
							val = ''
							val = (str(temp_date.strftime("%a")) + ' ' +
										 str(temp_date.strftime("%b")) + ' ' +
										 str(temp_date.strftime("%d")))
							summary_header_list.append(val)
							date_range_list.append(temp_date.strftime
																		 (dt))
							temp_date = temp_date + datetime.timedelta(days=1)
					all_detail.append(summary_header_list)
					room_ids = room_obj.search([])
					all_room_detail = []
					for room in room_ids:
							room_detail = {}
							room_list_stats = []
							room_detail.update({'name': room.name or ''})
							if not room.room_reservation_line_ids and \
								 not room.room_line_ids:
									for chk_date in date_range_list:
											room_list_stats.append({'state': 'Disponible',
																							'date': chk_date,
																							'room_id': room.id})
							else:
									for chk_date in date_range_list:
											ch_dt = chk_date[:10] + ' 23:59:59'
											ttime = dtime.strptime(ch_dt, dt)
											c = ttime.replace(tzinfo=timezone).\
													astimezone(pytz.timezone('UTC'))
											chk_date = c.strftime(dt)
											reserline_ids = room.room_reservation_line_ids.ids
											reservline_ids = (reservation_line_obj.search
																				([('id', 'in', reserline_ids),
																					('check_in', '<=', chk_date),
																					('check_out', '>=', chk_date),
																					('state', '=', 'assigned')
																					]))
											if not reservline_ids:
													sdt = dt
													chk_date = datetime.datetime.strptime(chk_date,
																																sdt)
													chk_date = datetime.datetime\
															.strftime(chk_date - datetime
																				.timedelta(days=1),
																				sdt)
													reservline_ids = (reservation_line_obj.search
																						([('id', 'in', reserline_ids),
																							('check_in', '<=', chk_date),
																							('check_out', '>=', chk_date),
																							('state', '=', 'assigned')]))
													for res_room in reservline_ids:
															rrci = res_room.check_in
															rrco = res_room.check_out
															cid = datetime.datetime.strptime(rrci, dt)
															cod = datetime.datetime.strptime(rrco, dt)
															dur = cod - cid
															if room_list_stats:
																	count = 0
																	for rlist in room_list_stats:
																			cidst = datetime.datetime.strftime(cid,
																																				 dt)
																			codst = datetime.datetime.strftime(cod,
																																				 dt)
																			rm_id = res_room.room_id.id
																			ci = rlist.get('date') >= cidst
																			co = rlist.get('date') <= codst
																			rm = rlist.get('room_id') == rm_id
																			st = rlist.get('state') == 'Reserved'
																			if ci and co and rm and st:
																					count += 1
																	if count - dur.days == 0:
																			c_id1 = user_obj.browse(self._uid)
																			c_id = c_id1.company_id
																			con_add = 0
																			amin = 0.0
																			if c_id:
																					con_add = c_id.additional_hours
#                                        When configured_addition_hours is
#                                        greater than zero then we calculate
#                                        additional minutes
																			if con_add > 0:
																					amin = abs(con_add * 60)
																			hr_dur = abs((dur.seconds / 60))
#                                        When additional minutes is greater
#                                        than zero then check duration with
#                                        extra minutes and give the room
#                                        reservation status is reserved or
#                                        free
																			if amin > 0:
																					if hr_dur >= amin:
																							reservline_ids = True
																					else:
																							reservline_ids = False
																			else:
																					if hr_dur > 0:
																							reservline_ids = True
																					else:
																							reservline_ids = False
																	else:
																			reservline_ids = False
											fol_room_line_ids = room.room_line_ids.ids
											chk_state = ['cancel']
											folio_resrv_ids = (folio_room_line_obj.search
																				 ([('id', 'in', fol_room_line_ids),
																					 ('check_in', '<=', chk_date),
																					 ('check_out', '>=', chk_date),
																					 ('status', 'not in', chk_state)
																					 ]))

											if reservline_ids or folio_resrv_ids:

												room_list_stats.append({'state': 'Reservado',
																									'date': chk_date,
																									'room_id': room.id,
																									'is_draft': 'No',
																									'data_model': '',
																									'data_id': 0})
											else:

												room_list_stats.append({'state': 'Disponible',
																									'date': chk_date,
																									'room_id': room.id})


							room_detail.update({'value': room_list_stats})

							all_room_detail.append(room_detail)

					main_header.append({'header': summary_header_list})

					name_room_draft= []
					date_checkin= []
					date_checkout= []
					#es donde van las posiciones donde encontraron cada habitacion
					posicion_all_room_detail= []
					room_draft = self.env['hotel.reservation'].search([('state', '=', 'draft')])
					if room_draft:
						for x in room_draft:
							room_reservation_line_ids = self.env['hotel_reservation.line'].search([('line_id', '=', x.id)])
							name_room_draft.append(room_reservation_line_ids.name)
							date_checkin.append(x.checkin)
							date_checkout.append(x.checkout)


					nuevo = {'is_draft': 'Yes', 'state' : 'Prereserva'}
					#all_room_detail[3]['value'][1].update(nuevo)

					quantity_room_draft= len(name_room_draft)
					contador=0
					iterador=0

					while (contador < quantity_room_draft)  :
						if name_room_draft[contador] ==  all_room_detail[iterador]['name']:

							for x in range(0, len(all_room_detail[iterador]['value']), 1):

								if (date_checkin[contador][0:10] == all_room_detail[iterador]['value'][x]['date'][0:10]):

									all_room_detail[iterador]['value'][x].update(nuevo)
							iterador= 0
							contador=contador +1
							posicion_all_room_detail.append(iterador)
						else:
							iterador= iterador + 1

						if iterador == len(all_room_detail):
							iterador=0
							contador=contador +1

					self.summary_header = str(main_header)
					self.room_summary = str(all_room_detail)

			return res