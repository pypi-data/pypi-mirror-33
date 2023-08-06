# copyright 2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""Mappers with "jsonschema.object" regid."""

import abc

from six import (
    add_metaclass,
    text_type,
)

from logilab.common.decorators import classproperty

from cubicweb_jsonschema.views import jsonschema_section

from .base import (
    JSONSchemaMapper,
    JSONSchemaDeserializer,
    JSONSchemaSerializer,
    add_descriptive_metadata,
    object_schema,
    ProtectedDict,
)
from .predicates import (
    partial_yams_match,
)

__all__ = [
    'CompoundMapper',
]


@JSONSchemaDeserializer.register
@JSONSchemaSerializer.register
@add_metaclass(abc.ABCMeta)
class CompoundMapper(JSONSchemaMapper):
    """Mapper for a "compound" field gathering Yams relations into a
    dedicated JSON "object" to be inserted in "definitions" key of the JSON
    Schema document.

    The compound "object" will appear in the main JSON Schema document's
    properties under the `name` class attribute (defaults to class name).
    """
    __regid__ = 'jsonschema.object'
    __abstract__ = True
    __select__ = partial_yams_match()

    @abc.abstractproperty
    def etype(self):
        """entity type holding this compound field"""

    @abc.abstractproperty
    def relations(self):
        """sequence of relations gathered in this compound field"""

    @abc.abstractproperty
    def title(self):
        """title of the field"""

    # sequence of 'relation/role' computed from 'relations'
    _relations = ()

    @classproperty
    def name(cls):
        """name of the property to be inserted in the main JSON Schema
        document (defaults to class name).
        """
        return text_type(cls.__name__)

    @classmethod
    def __registered__(cls, reg):
        if not cls.relations:
            raise ValueError(
                '{} is missing a "relations" class attribute'.format(cls))
        # Compute relation/role pairs from relations
        relations = []
        for relinfo in cls.relations:
            try:
                rtype, role = relinfo
            except ValueError:
                rtype = relinfo
                role = 'subject'
            relations.append((rtype, role))
        cls._relations = tuple(relations)
        # Check for name or relation duplication
        for obj in reg[cls.__regid__]:
            if obj == cls:
                continue
            if obj.etype == cls.etype:
                if obj.name == cls.name:
                    # Make sure 'name' is unique amongst objects with
                    # 'jsonschema.object' regid.
                    raise ValueError('a class with name "{}" is already '
                                     'registered for {} entity type'.format(
                                         cls.name, cls.etype))
                # Prevent duplicate mapping of the same etype/rtype.
                common_rtypes = set(obj._relations) & set(cls._relations)
                if common_rtypes:
                    raise ValueError(
                        'duplicate relation mapping for "{}": {}'.format(
                            cls.etype,
                            ', '.join('-'.join(rel) for rel in common_rtypes),
                        )
                    )
        # Hide relations mapped to this document from etype JSON Schema.
        for rtype, role in cls._relations:
            if role == 'object':
                jsonschema_section.tag_object_of(
                    ('*', rtype, cls.etype), 'hidden')
            else:
                jsonschema_section.tag_subject_of(
                    (cls.etype, rtype, '*'), 'hidden')
        return super(CompoundMapper, cls).__registered__(reg)

    def required(self, schema_role):
        """Return False by default."""
        return False

    def schema_and_definitions(self, schema_role=None):
        properties = {}
        required = []
        definitions = ProtectedDict()
        for rtype, role in self._relations:
            rschema = self._cw.vreg.schema[rtype]
            target_types = {
                t.type for t in rschema.targets(self.etype, role)}
            mapper = self.select_mapper(
                'jsonschema.relation',
                etype=self.etype, rtype=rtype, role=role,
                target_types=target_types,
            )
            subschema, defs = mapper.schema_and_definitions(schema_role)
            if subschema is None:
                continue
            properties[mapper.orm_rtype] = subschema
            if mapper.required(schema_role):
                required.append(mapper.orm_rtype)
            if defs:
                definitions.update(defs)
        schema = {
            '$ref': '#/definitions/{}'.format(self.title),
        }
        definitions[self.title] = add_descriptive_metadata(
            object_schema(properties, required),
            self,
        )
        return schema, definitions

    def values(self, entity, instance):
        assert entity is None or entity.cw_etype == self.etype, \
            'cannot get "values" for {} with {}'.format(entity, self)
        try:
            values = instance.pop(self.name)
        except KeyError:
            if entity is None:
                return {}
            # Continue with an empty "value" that would get filled by compound
            # relation mappers with default or None values.
            values = {}
        for rtype, role in self._relations:
            mapper = self._relation_mapper(rtype, role)
            values.update(
                mapper.values(entity, values))
        return values

    def serialize(self, entity):
        assert entity.cw_etype == self.etype, \
            'cannot serialize {} with {}'.format(entity, self)
        data = {}
        for rtype, role in self._relations:
            mapper = self._relation_mapper(rtype, role)
            value = mapper.serialize(entity)
            if value is not None:
                data[mapper.orm_rtype] = value
        return data

    def _relation_mapper(self, rtype, role):
        rschema = self._cw.vreg.schema[rtype]
        target_types = {t.type for t in rschema.targets(self.etype, role)}
        return self.select_mapper(
            'jsonschema.relation', etype=self.etype,
            rtype=rtype, role=role, target_types=target_types,
        )
