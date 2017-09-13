# -*- encoding: utf-8 -*-

from openerp.report import report_sxw
from openerp.osv import osv
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
import pytz
from datetime import datetime


class reporte_reserva(report_sxw.rml_parse):
	def __init__(self,cr,uid,name,context):
		super(reporte_reserva,self).__init__(cr,uid,name,context)
		self.localcontext.update({
			'time':time,
			})


class reporte_alumnos(osv.AbstractModel):
	_name="report.hotel.reservation"
	_inherit="report.abstract_report"
	_template="hotel.reservation"
	_wrapped_report_class=reporte_reserva