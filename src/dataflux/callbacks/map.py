# Copyright (C) 2026 Hector van der Aa <hector@h3cx.dev>
# Copyright (C) 2026 Association Exergie <association.exergie@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from dataflux.state import AppState


def live_map_recenter(sender, app_data, user_data: AppState) -> None:
    user_data.live_map_pending_recenter = True


def live_map_zoom_in(sender, app_data, user_data: AppState) -> None:
    user_data.live_map_pending_zoom_in = True


def live_map_zoom_out(sender, app_data, user_data: AppState) -> None:
    user_data.live_map_pending_zoom_out = True
