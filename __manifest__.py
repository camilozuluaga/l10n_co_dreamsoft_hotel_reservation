# -*- coding: utf-8 -*-
{
    'name': 'Colombia - Reservacion',
    'category': 'Localization',
    'version': '1.0.0',
    'author': 'DREAMSOFT',
    'license': 'AGPL-3',
    'maintainer': '',
    'website': '',
    'summary': 'Colombia Reservacion: Extended hotel_reservation'
               'Contact Module - Odoo 10.0',
    'images': [],
    'depends': ['l10n_co_dreamsoft_hotel', 'hotel_reservation'],
    'data': [
        'views/configuracion_reserva_periodo_resumido_view.xml',
        'views/room_reservation_summary_view.xml',
        'views/quick_room_reservation_view.xml',
        'views/hotel_reservation_view.xml',
        'views/dreamsoft_completar_checkin_relacion_view.xml',
        'views/dreamsoft_completar_checkin_view.xml',
        'data/data_tareas_programadas.xml',
    ],
    'qweb': [],
    'installable': True,
}
