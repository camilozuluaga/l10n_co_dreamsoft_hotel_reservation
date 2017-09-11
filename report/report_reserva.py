# -*- encoding: utf-8 -*-

from openerp.report import report_sxw
from openerp.osv import osv


class reporte_reserva(report_sxw.rml_parse):
	def __init__(self,cr,uid,name,context):
		super(reporte_reserva,self).__init__(cr,uid,name,context)
		self.localcontext.update({
			#'get_data_reserva': self.get_data_reserva
			})
