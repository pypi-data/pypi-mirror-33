# copyright 2018 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
"""Utilities for Yams to JSON Schema mappers."""


def relation_target_types(schema, rtype, role, preset_types=None):
    """Yield target entity types for (rtype, role) relation, possibly filtered
    out from values not in `preset_types`.
    """
    rschema = schema[rtype]
    for target_eschema in sorted(rschema.targets(role=role)):
        if target_eschema.final:
            continue
        target_type = target_eschema.type
        if preset_types is not None and target_type not in preset_types:
            continue
        yield target_type
