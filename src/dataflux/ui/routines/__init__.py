# Copyright (C) 2026 Hector van der Aa <hector@h3cx.dev>
# Copyright (C) 2026 Association Exergie <association.exergie@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

import dearpygui.dearpygui as dpg
import dataflux.ui.routines.menu
import dataflux.ui.routines.status

from dataflux.state import AppState


def update_global_connection_status(state: AppState):
    dataflux.ui.routines.menu.update_menu_file_connection_status(state)
    dataflux.ui.routines.status.update_status_connection_status(state)
