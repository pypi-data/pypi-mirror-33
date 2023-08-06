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
"""Mappers with "jsonschema.relation" regid."""

import abc

import iso8601
from six import (
    add_metaclass,
    text_type,
)

from logilab.common.decorators import cachedproperty

from yams import BadSchemaDefinition, ValidationError
from yams.constraints import StaticVocabularyConstraint
from cubicweb import (
    Binary,
    Unauthorized,
    neg_role,
    _,
)
from cubicweb.predicates import (
    match_kwargs,
)

from cubicweb_jsonschema import (
    CREATION_ROLE,
    EDITION_ROLE,
    VIEW_ROLE,
    orm_rtype,
)

from .base import (
    JSONSchemaMapper,
    JSONSchemaDeserializer,
    JSONSchemaSerializer,
    add_descriptive_metadata,
    add_links,
    object_schema,
)
from .predicates import (
    _etype_from_context,
    yams_component_target,
    yams_final_rtype,
    yams_match,
)
from . import _utils


__all__ = [
    'BaseRelationMapper',
    'AttributeMapper',
    'StringMapper',
    'FloatMapper',
    'IntMapper',
    'BooleanMapper',
    'PasswordMapper',
    'DateMapper',
    'DatetimeMapper',
    'BytesMapper',
    'InlinedRelationMapper',
    'RelationMapper',
    'ETypeRelationItemMapper',
    'EntityRelationItemMapper',
]


class BaseRelationMapper(JSONSchemaMapper):
    """Base abstract class to fill the gap between a yams relation and it's json
    schema mapping.

    They should be selected depending on the relation (`etype`, `rtype`, `role`
    and optionaly `target_types`).
    """
    __regid__ = 'jsonschema.relation'
    __select__ = match_kwargs('rtype', 'role')
    __abstract__ = True

    @property
    def etype(self):
        """The entity type bound to this mapper."""
        return _etype_from_context(self.cw_extra_kwargs)

    def __init__(self, _cw, **kwargs):
        #: relation type name
        self.rtype = kwargs.pop('rtype')
        #: role of `etype` in relation
        self.role = kwargs.pop('role')
        #: possible target types of the relation (empty for attribute relations)
        self.target_types = list(_utils.relation_target_types(
            _cw.vreg.schema, self.rtype, self.role,
            kwargs.pop('target_types', None)))
        super(BaseRelationMapper, self).__init__(_cw, **kwargs)

    def __repr__(self):
        return ('<{0.__class__.__name__} etype={0.etype} rtype={0.rtype} '
                'role={0.role} target_types={0.target_types}>'.format(self))

    @cachedproperty
    def description(self):
        ntargets = len(self.target_types)
        if ntargets > 1:
            return None
        elif ntargets == 1:
            targettype = self.target_types[0]
        else:
            targettype = None
        eschema = self._cw.vreg.schema[self.etype]
        rdef = eschema.rdef(self.rtype, role=self.role,
                            targettype=targettype)
        if rdef.description:
            return self._cw._(rdef.description)

    @cachedproperty
    def title(self):
        if self.role == 'object':
            return self._cw._(self.rtype + '_object')
        return self._cw._(self.rtype)

    @cachedproperty
    def orm_rtype(self):
        return orm_rtype(self.rtype, self.role)

    def links(self, schema_role=None, **kwargs):
        """Yield Link appobjects matching regid and selection context of this
        mapper if schema_role is None.
        """
        if schema_role is not None:
            return
        for link in super(BaseRelationMapper, self).links(
                schema_role=schema_role, **kwargs):
            yield link


@JSONSchemaDeserializer.register
@JSONSchemaSerializer.register
@add_metaclass(abc.ABCMeta)
class AttributeMapper(BaseRelationMapper):
    """Abstract base abstract class to map attribute relation.

    Concrete class should implement the `json_type` property.
    """
    __abstract__ = True
    __select__ = yams_final_rtype() & match_kwargs('etype')

    @abc.abstractproperty
    def json_type(self):
        """JSON primitive type (e.g. "string", "number", etc.)"""

    #: JSON Schema "format" keyword for semantic validation.
    format = None

    @property
    def attr(self):
        """Relation definition for bound attribute."""
        return self._cw.vreg.schema[self.etype].rdef(self.rtype)

    def _constraint_mapper(self, cstr):
        mapper = self._cw.vreg['mappers'].select_or_none(
            'jsonschema.constraint', self._cw.vreg, self._cw._,
            self.etype, self.rtype, cstr)
        if mapper is not None:
            return mapper
        elif not isinstance(cstr, StaticVocabularyConstraint):
            self.warning('ignored %s on %s', cstr.type(), self.attr)
        return None

    def required(self, schema_role):
        """Return True if mapped property is *required*."""
        if schema_role in (CREATION_ROLE, EDITION_ROLE):
            return self.attr.cardinality[0] == '1'
        return False

    @add_links
    def schema_and_definitions(self, schema_role=None):
        schema = {
            'type': self.json_type,
        }
        if self.format is not None:
            schema['format'] = self.format
        if schema_role in (CREATION_ROLE, EDITION_ROLE):
            vocabulary_constraint = next(
                (cstr for cstr in self.attr.constraints
                 if isinstance(cstr, StaticVocabularyConstraint)), None)
            if vocabulary_constraint:
                # In presence of a vocabulary constraint, we wrap the field
                # into a oneOf field with a single-value 'enum', ignoring
                # other constraints.
                oneof_items = []
                for v in sorted(vocabulary_constraint.vocabulary()):
                    item_schema = schema.copy()
                    item_schema.update({
                        'enum': [v],
                        'title': self._cw._(v),
                    })
                    oneof_items.append(item_schema)
                schema = {
                    'oneOf': oneof_items,
                }
            else:
                for constraint in self.attr.constraints:
                    cstr_mapper = self._constraint_mapper(constraint)
                    if cstr_mapper is not None:
                        schema.update(cstr_mapper.json_schema(schema_role))
            if self.attr.default is not None:
                schema['default'] = self.attr.default

        return add_descriptive_metadata(schema, self), None

    def values(self, entity, instance):
        """Return a dictionary holding deserialized value for mapped attribute.

        If mapped attribute is absent from `instance` and `entity` is not
        None, the default value for attribute is returned as value of the
        dictionnary.
        """
        try:
            value = instance.pop(self.rtype)
        except KeyError:
            if entity is None:
                return {}
            rschema = entity.e_schema.rdef(self.rtype, self.role)
            value = rschema.default
        else:
            value = self._type(value)
            if entity is not None and getattr(entity, self.orm_rtype) == value:
                # Do not trigger update, if the value has not changed.
                # This is useful for PUT requests for which all fields should
                # be present even if they are not changed. By skipping
                # unchanged value, we avoid possible security check that would
                # be meaningless since the value is not changed.
                return {}
        return {self.orm_rtype: value}

    @staticmethod
    def _type(json_value):
        """Return properly typed value for use within a cubicweb's entity from
        given JSON value.

        Nothing to do by default.
        """
        return json_value

    def serialize(self, entity):
        value = getattr(entity, self.orm_rtype)
        if value is not None:
            return self._value(value)

    @staticmethod
    def _value(value):
        """Return the serializable value from attribute `value`."""
        return value


class StringMapper(AttributeMapper):
    """Attribute mapper for Yams' String type."""
    __select__ = yams_match(target_types='String')
    #:
    json_type = 'string'
    _type = text_type


class FloatMapper(AttributeMapper):
    """Attribute mapper for Yams' Float type."""
    __select__ = yams_match(target_types='Float')
    #:
    json_type = 'number'


class IntMapper(AttributeMapper):
    """Attribute mapper for Yams' Int and BigInt types."""
    __select__ = yams_match(target_types={'Int', 'BigInt'})
    #:
    json_type = 'integer'


class BooleanMapper(AttributeMapper):
    """Attribute mapper for Yams' Boolean type."""
    __select__ = yams_match(target_types='Boolean')
    #:
    json_type = 'boolean'


class PasswordMapper(AttributeMapper):
    """Attribute mapper for Yams' Password type."""
    __select__ = yams_match(target_types='Password')
    #:
    json_type = 'string'
    #:
    format = 'password'

    def required(self, schema_role):
        """Possibly return True unless in *edition* role."""
        if schema_role == EDITION_ROLE:
            return False
        return super(PasswordMapper, self).required(schema_role)

    def values(self, entity, instance):
        password_changed = self.orm_rtype in instance
        values = super(PasswordMapper, self).values(entity, instance)
        if entity is not None and not password_changed:
            # We don't want the Password value to be reset if it has not
            # changed.
            del values[self.orm_rtype]
        return values

    def serialize(self, entity):
        return None

    @staticmethod
    def _type(json_value):
        """Return an encoded string suitable for Password type."""
        return json_value.encode('utf-8')


class DateMapper(StringMapper):
    """Attribute mapper for Yams' Date type."""
    __select__ = yams_match(target_types=('Date'))
    #:
    format = 'date'

    @staticmethod
    def _type(value):
        """Return a datetime object parsed from ISO8601 `value` string."""
        return iso8601.parse_date(value)


class DatetimeMapper(DateMapper):
    """Attribute mapper for Yams' (TZ)Datetime type."""
    __select__ = yams_match(target_types=('Datetime', 'TZDatetime'))
    #:
    format = 'date-time'


class BytesMapper(StringMapper):
    """Attribute mapper for Yams' Bytes type."""
    __select__ = yams_match(target_types='Bytes')

    @staticmethod
    def _type(value):
        """Return a Binary containing `value`."""
        return Binary(value.encode('utf-8'))

    @staticmethod
    def _value(value):
        """Return a unicode string from Binary `value`."""
        return value.getvalue().decode('utf-8')


class _RelationMapper(BaseRelationMapper):
    """Abstract class for true relation (as opposed to attribute) mapper.
    """
    __abstract__ = True
    __select__ = ~yams_final_rtype()

    @add_links
    def schema_and_definitions(self, schema_role=None):
        item_mapper = self.select_mapper(
            'jsonschema.item',
            rtype=self.rtype, role=self.role,
            target_types=set(self.target_types),
            **self.cw_extra_kwargs)
        items_schema, defs = item_mapper.schema_and_definitions(schema_role)
        schema = {
            'type': 'array',
            'items': items_schema,
        }
        if schema_role in (CREATION_ROLE, EDITION_ROLE):
            cardinality = self._cardinality()
            if cardinality in '+1':
                schema['minItems'] = 1
            if cardinality in '?1':
                schema['maxItems'] = 1
        return add_descriptive_metadata(schema, self), defs

    def required(self, schema_role):
        if schema_role in (CREATION_ROLE, EDITION_ROLE):
            return self._cardinality() in '1+'
        return False

    def _cardinality(self):
        """Return role-cardinality if schema definition is consistent and
        raise BadSchemaDefinition otherwise.
        """
        rschema = self._cw.vreg.schema[self.rtype]
        cardinality = None
        for target_type in self.target_types:
            rdef = rschema.role_rdef(self.etype, target_type, self.role)
            card = rdef.role_cardinality(self.role)
            if cardinality is None:
                cardinality = card
            elif card != cardinality:
                raise BadSchemaDefinition(
                    'inconsistent {} cardinalities within {} relation '
                    'definitions'.format(self.role, self.rtype))
        return cardinality


@JSONSchemaDeserializer.register
@JSONSchemaSerializer.register
class InlinedRelationMapper(_RelationMapper):
    """Map relation as 'inlined', i.e. the target of the relation is
    created/edited along with its original entity.
    """
    __select__ = (_RelationMapper.__select__
                  & yams_component_target()
                  & (match_kwargs('etype') | match_kwargs('entity')))

    def values(self, entity, instance):
        # Would require knownledge of the target type from "instance",
        # but the generated JSON schema does not expose this yet.
        assert len(self.target_types) == 1, \
            'cannot handle multiple target types yet: {}'.format(
                self.target_types)
        target_type = self.target_types[0]
        try:
            values = instance.pop(self.rtype)
        except KeyError:
            if entity is None:
                return {}
            values = []
        if not isinstance(values, list):
            raise ValidationError(entity,
                                  {self.rtype: _('value should be an array')})
        if entity is not None:
            # if entity already exists, delete entities related through
            # this mapped relation
            for linked_entity in getattr(entity, self.orm_rtype):
                if linked_entity.cw_etype in self.target_types:
                    linked_entity.cw_delete()
        target_mapper = self.select_mapper(
            'jsonschema.entity', etype=target_type,
            rtype=self.rtype, role=neg_role(self.role),
            target_types={self.etype},
        )
        result = []
        for subinstance in values:
            subvalues = target_mapper.values(subinstance)
            result.append(self._cw.create_entity(target_type, **subvalues))
        return {self.orm_rtype: result}

    def serialize(self, related_entities):
        def serialize(entity):
            mapper = self.select_mapper(
                'jsonschema.entity', entity=entity,
                rtype=self.rtype, role=neg_role(self.role),
                target_types={self.etype},
            )
            return mapper.serialize()

        return [serialize(related) for related in related_entities]


@JSONSchemaDeserializer.register
@JSONSchemaSerializer.register
class RelationMapper(_RelationMapper):
    """Map relation as 'generic', i.e. the target of the relation may be
    selected in preexisting possible targets.
    """
    __select__ = (_RelationMapper.__select__
                  & ~yams_component_target()
                  & (match_kwargs('etype') | match_kwargs('entity')))

    def values(self, entity, instance):
        try:
            values = instance.pop(self.rtype)
        except KeyError:
            return {}
        if entity is not None:
            entity.cw_set(**{self.orm_rtype: None})
        try:
            values = [int(x['id']) for x in values]
        except (TypeError, ValueError):
            msg = _('value should be an array of string-encoded integers')
            raise ValidationError(entity, {self.rtype: msg})
        return {self.orm_rtype: values}

    def serialize(self, related_entities):
        item_mapper = self.select_mapper(
            'jsonschema.item',
            rtype=self.rtype, role=self.role, **self.cw_extra_kwargs)
        return [item_mapper.serialize(entity) for entity in related_entities]


class ETypeRelationItemMapper(BaseRelationMapper):
    """Map items of a 'generic' relation for an non-existant entity."""
    __regid__ = 'jsonschema.item'
    __select__ = (_RelationMapper.__select__
                  & ~yams_component_target()
                  & match_kwargs('etype', 'rtype', 'role'))

    def relation_targets(self, schema_role):
        entity = self._cw.vreg['etypes'].etype_class(self.etype)(self._cw)
        potential_targets = []
        for target_type in self.target_types:
            try:
                potential_targets.extend(entity.unrelated(
                    self.rtype, target_type, self.role).entities())
            except Unauthorized:
                continue
        return potential_targets

    @add_links
    def schema_and_definitions(self, schema_role=None):
        ids = [
            {
                'type': 'string',
                'enum': [text_type(target.eid)],
                'title': target.dc_title(),
            }
            for target in self.relation_targets(schema_role)
        ]
        if not ids:
            return False, None
        properties = {
            'id': {
                'oneOf': ids,
            },
        }
        required = []
        if schema_role in (CREATION_ROLE, EDITION_ROLE):
            required.append('id')
        return object_schema(properties, required), None

    # XXX copy of CollectionItemMapper's method
    def links(self, schema_role=None, **kwargs):
        kwargs['anchor'] = '#'
        return super(ETypeRelationItemMapper, self).links(
            schema_role=schema_role, **kwargs)


@JSONSchemaSerializer.register
class EntityRelationItemMapper(ETypeRelationItemMapper):
    """Map items of a 'generic' relation for an existing entity."""
    __select__ = (_RelationMapper.__select__
                  & ~yams_component_target()
                  & match_kwargs('entity', 'rtype', 'role'))

    @property
    def entity(self):
        return self.cw_extra_kwargs['entity']

    def relation_targets(self, schema_role):
        if schema_role == VIEW_ROLE:
            return self.entity.related(
                self.rtype, self.role,
                targettypes=tuple(self.target_types)).entities()
        if schema_role == CREATION_ROLE:
            assert len(self.target_types) == 1, \
                'cannot handle multiple target types in {} for {}'.format(
                    self, schema_role)
            targettype = self.target_types[0]
            return self.entity.unrelated(
                self.rtype, targettype, role=self.role,
            ).entities()
        return super(EntityRelationItemMapper, self).relation_targets(
            schema_role)

    def serialize(self, entity):
        return {'id': str(entity.eid)}
