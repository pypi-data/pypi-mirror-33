#!/bin/bash

# Copyright (C) 2018 David Valle Delisle <dvd@redhat.com>
# Copyright (C) 2017 Lars Kellogg-Stedman <lars@redhat.com>
# Copyright (C) 2017, 2018 Robin Černín <cerninr@gmail.com>
# Copyright (C) 2017, 2018 Pablo Iranzo Gómez <Pablo.Iranzo@gmail.com>
# Copyright (C) 2018 Mikel Olasagasti Uranga <mikel@olasagasti.info>


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

# Load common functions
[[ -f "${CITELLUS_BASE}/common-functions.sh" ]] && . "${CITELLUS_BASE}/common-functions.sh"

# long_name: SELinux persistent status
# description: Determines SELinux status on configuration
# priority: 100
# selinux enforcing

if [[ ${CITELLUS_LIVE} = 0 ]];  then
    is_required_file "${CITELLUS_ROOT}/sos_commands/selinux/sestatus_-b"
    sestatus="${CITELLUS_ROOT}/sos_commands/selinux/sestatus_-b"
else
    is_required_command "sestatus"
    sestatus=$(mktemp)
    trap "rm ${sestatus}" EXIT
    sestatus -b > ${sestatus}
fi

status=$(awk '/^SELinux status:/ {print $3}' ${sestatus})
if [[ "x$status" == "xenabled" ]]; then
    file_mode=$(awk '/^Mode from config file:/ {print $5}' "$sestatus")

    if [[ "x$file_mode" == "xenforcing" ]]; then
        exit ${RC_OKAY}
    else
        echo "persistent selinux mode is not enforcing (found $file_mode)" >&2
        exit ${RC_FAILED}
    fi
elif [[ "x$status" == "xdisabled" ]]; then
    echo "SELinux is disabled" >&2
    exit ${RC_FAILED}
else
    echo "failed to determined persistent selinux mode" >&2
    exit ${RC_FAILED}
fi

