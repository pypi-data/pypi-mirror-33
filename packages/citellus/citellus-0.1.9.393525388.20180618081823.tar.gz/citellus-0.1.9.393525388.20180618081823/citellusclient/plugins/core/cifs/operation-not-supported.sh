#!/bin/bash

# Copyright (C) 2018 Robin Černín <rcernin@redhat.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# we can run this against fs snapshot or live system

# long_name: Finds matches of kernel.*cifs_mount failed w/return code = -95
# description: Finds matches of error kernel.*cifs_mount failed w/return code = -95

REGEXP="kernel.*cifs_mount failed w/return code = -95"

# priority: 700

# Load common functions
[[ -f "${CITELLUS_BASE}/common-functions.sh" ]] && . "${CITELLUS_BASE}/common-functions.sh"

if [[ "x$CITELLUS_LIVE" = "x0" ]]; then
    journal="$journalctl_file"
else
    journal="$(mktemp)"
    trap "/bin/rm ${journal}" EXIT
    journalctl -t systemd --no-pager --boot > ${journal}
fi

if is_lineinfile "${REGEXP}" ${journal} ${CITELLUS_ROOT}/var/log/messages ; then
    echo $"CIFS: mount error(95): Operation not supported." >&2
    echo $"$REGEXP found in logs" >&2
    exit ${RC_FAILED}
else
    exit ${RC_OKAY}
fi

