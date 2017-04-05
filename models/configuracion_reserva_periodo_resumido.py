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

class configuracion_reserva_periodo(models.Model):

	_name = 'dreamsoft.configuracion.periodo_reserva'

	hora_entrada = fields.Char('Hora Checkin', size=5, default='00:00')
	hora_salida = fields.Char('Hora Checkout', size=5, default='00:00')



	def verificar_horas(self, hora):
		'''
		metodo que se usa para identificar si la hora de entrada es correcta
		es correcta si es hasta el numero 23 empezando desde las 00 hasta las
		23 que serian horas y al igual que los minutos.
		-------------------------------------------------------------------
		@param self: object pointer
		@param hora: el valor del campo modificado
		@return: raise warning depending on the validation
		'''
		cadena = str(hora).strip()
		if cadena:
			dos_puntos = cadena[2:3]

			_logger.info(((not cadena[0:2].isdigit()) or (not cadena[3:5].isdigit())))


			if dos_puntos != ':':
				if cadena[1:2] != ':':
					raise ValidationError(_('La hora debe de tener dos puntos para separar horas y minutos'))
				else:
					cadena = '0'+cadena

			if (not cadena[0:2].isdigit() or not cadena[3:5].isdigit()):
				raise ValidationError(_('La hora no debe contener letras ni caracteres'))

			if len(cadena[0:2]) > 2:
				raise ValidationError(_('La hora debe ser entre las 00 y las 23'))

			if int(cadena[0:2]) >= 0:
				if int(cadena[0:2]) > 23:
					raise ValidationError(_('La hora debe ser entre las 00 y las 23'))

			if int(cadena[3:5]) >= 0:
				if int(cadena[3:5]) >= 0:
					if int(cadena[3:5]) > 59:
						raise ValidationError(_('Los minutos deben de estar entre 00 y 59'))
				else:
					raise ValidationError(_('Los minutos deben de ser mayor a 0 '))

	@api.constrains('hora_entrada', 'hora_salida')
	def chequear_hora(self):
		self.verificar_horas(self.hora_entrada)
		self.verificar_horas(self.hora_salida)
