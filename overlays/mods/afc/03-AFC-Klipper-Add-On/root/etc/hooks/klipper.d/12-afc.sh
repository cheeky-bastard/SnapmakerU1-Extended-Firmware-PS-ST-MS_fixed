#!/bin/sh
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: Copyright (c) 2026 cheeky-bastard
case "${1:-}" in
    start|restart)
        if ! /usr/local/sbin/afc-restore-modules; then
            echo "Enabled AFC could not restore its module links; refusing to start Klipper." >&2
            exit 1
        fi
        ;;
esac
