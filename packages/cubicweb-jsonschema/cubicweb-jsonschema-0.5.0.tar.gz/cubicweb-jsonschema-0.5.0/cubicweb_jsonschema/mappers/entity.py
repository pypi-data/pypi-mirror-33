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
"""Mappers with "jsonschema.entity" regid."""

from cubicweb import (
    _,
    ValidationError,
)
from cubicweb.predicates import (
    match_kwargs,
    relation_possible,
)

from cubicweb_jsonschema import (
    CREATION_ROLE,
    EDITION_ROLE,
    VIEW_ROLE,
)

from .base import (
    JSONSchemaMapper,
    JSONSchemaDeserializer,
    JSONSchemaSerializer,
    ProtectedDict,
    add_descriptive_metadata,
    add_links,
    object_schema,
)
from .predicates import (
    _for_workflowable_entity,
)


__all__ = [
    'ETypeMapper',
    'TargetETypeMapper',
    'EntityMapper',
    'TargetEntityMapper',
    'WorkflowableEntityMapper',
]


@JSONSchemaDeserializer.register
class ETypeMapper(JSONSchemaMapper):
    """JSON Schema mapper for entity types."""
    __regid__ = 'jsonschema.entity'
    __select__ = match_kwargs('etype')

    @property
    def etype(self):
        return self.cw_extra_kwargs['etype']

    @property
    def entity(self):
        """Entity bound to this mapper, None for ETypeMapper."""
        return None

    @property
    def title(self):
        return self._cw._(self.etype)

    @add_links
    def schema_and_definitions(self, schema_role=None):
        properties = {}
        required = []
        definitions = ProtectedDict()

        def insert_property(name, subschema, defs, mapper):
            if subschema is None:
                return
            properties[name] = subschema
            if defs:
                definitions.update(defs)
            if mapper.required(schema_role):
                required.append(name)

        for mapper in self._object_mappers():
            subschema, defs = mapper.schema_and_definitions(schema_role)
            insert_property(mapper.name, subschema, defs, mapper)

        for rtype, role, target_types in self.relations(schema_role):
            if target_types is None:
                target_types = self._rtype_target_types(rtype, role)
            assert isinstance(target_types, set), target_types
            mapper = self._relation_mapper(rtype, role, target_types)
            subschema, defs = mapper.schema_and_definitions(schema_role)
            insert_property(rtype, subschema, defs, mapper)

        schema = object_schema(properties, required)
        return add_descriptive_metadata(schema, self), definitions

    def links(self, schema_role=None):
        """Yield Link appobjects matching regid and selection context of this
        entity mapper along with selectable "jsonschema.relation" links for
        "subject" relations.
        """
        if schema_role is not None:
            return
        for linkcls in super(ETypeMapper, self).links():
            yield linkcls
        links_registry = self._cw.vreg['links']
        for rtype, role, __ in self.relations(VIEW_ROLE, section='related'):
            if role != 'subject':
                continue
            yield links_registry.select(
                'jsonschema.relation', self._cw,
                entity=self.entity, rtype=rtype, role=role,
            )

    def values(self, instance):
        """Return a dict with deserialized data from `instance` suitable for
        insertion in CubicWeb database.
        """
        entity = self.entity
        values = {}
        # Deserialize "jsonschema.object" mappers first.
        for mapper in self._object_mappers():
            values.update(mapper.values(entity, instance))
        # Then Yams relations.
        if entity is None:
            schema_role = CREATION_ROLE
        else:
            schema_role = EDITION_ROLE
        for rtype, role, target_types in self.relations(schema_role):
            mapper = self._relation_mapper(rtype, role, target_types)
            values.update(mapper.values(entity, instance))
        if instance:
            # All properties in "instance" should have been consumed at this
            # point.
            eid = entity.eid if entity is not None else None
            msg = _('unexpected properties: {}').format(', '.join(instance))
            raise ValidationError(eid, {None: msg})
        return values

    def relations(self, schema_role, section='inlined'):
        """Yield relation information tuple (rtype, role, targettypes)
        for given schema role in the context of bound entity type.

        Keyword argument `section` controls uicfg section to select relations
        in.
        """
        try:
            permission = {
                None: 'read',
                VIEW_ROLE: 'read',
                CREATION_ROLE: 'add',
                EDITION_ROLE: 'update',
            }[schema_role]
        except KeyError:
            raise ValueError('unhandled schema role "{0}" in {1}'.format(
                schema_role, self))
        entity = self.entity
        if entity is None:
            entity = self._cw.vreg['etypes'].etype_class(self.etype)(self._cw)
        rsection = self._cw.vreg['uicfg'].select(
            'jsonschema', self._cw, entity=entity)
        return rsection.relations_by_section(entity, section, permission)

    def _object_mappers(self):
        """Yield 'jsonschema.object' mapper instance selectable for entity
        bound to this mapper.
        """
        if 'jsonschema.object' not in self._cw.vreg['mappers']:
            return
        for mappercls in self._cw.vreg['mappers']['jsonschema.object']:
            if mappercls.__select__(mappercls, self._cw, etype=self.etype) > 0:
                yield mappercls(self._cw)

    def _rtype_target_types(self, rtype, role):
        rschema = self._cw.vreg.schema[rtype]
        return {t.type for t in rschema.targets(self.etype, role)}

    def _relation_mapper(self, rtype, role, target_types=None):
        return self.select_mapper(
            'jsonschema.relation',
            etype=self.etype, rtype=rtype, role=role, target_types=target_types)


class TargetETypeMapper(ETypeMapper):
    """Specialized version of :class:`ETypeMapper` selectable for an entity
    type as target of (`rtype`, `role`) relation.
    """
    __select__ = match_kwargs('etype', 'rtype', 'role')

    @property
    def rtype(self):
        return self.cw_extra_kwargs['rtype']

    @property
    def role(self):
        return self.cw_extra_kwargs['role']

    def relations(self, schema_role, section='inlined'):
        relations = super(TargetETypeMapper, self).relations(
            schema_role, section=section)
        for rtype, role, target_types in relations:
            if (rtype, role) == (self.rtype, self.role):
                continue
            yield rtype, role, target_types


@JSONSchemaSerializer.register
class EntityMapper(ETypeMapper):
    """JSON Schema mapper for an entity."""
    __select__ = match_kwargs('entity')

    @property
    def entity(self):
        """Live entity from selection context."""
        return self.cw_extra_kwargs['entity']

    @property
    def etype(self):
        return self.entity.cw_etype

    def _relation_mapper(self, rtype, role, target_types=None):
        return self.select_mapper(
            'jsonschema.relation',
            entity=self.entity, rtype=rtype,
            role=role, target_types=target_types,
            resource=None,
        )

    def serialize(self):
        """Return the serialized value entity bound to this mapper."""
        entity = self.entity
        entity.complete()
        data = {}
        for mapper in self._object_mappers():
            data[mapper.name] = mapper.serialize(entity)
        eschema = entity.e_schema
        for rtype, role, target_types in self.relations(VIEW_ROLE):
            relation_mapper = self._relation_mapper(rtype, role, target_types)
            if eschema.rdef(rtype, role=role, takefirst=True).final:
                value = relation_mapper.serialize(entity)
                if value is None:
                    continue
            else:
                rset = entity.related(
                    rtype, role, targettypes=tuple(target_types))
                if not rset:
                    continue
                value = relation_mapper.serialize(rset.entities())
            data[relation_mapper.orm_rtype] = value
        return data


class WorkflowableEntityMapper(EntityMapper):
    """Mapper for workflowable entity."""
    __select__ = (
        EntityMapper.__select__
        & relation_possible('in_state')
    )

    def schema_and_definitions(self, schema_role=None):
        schema, defns = super(
            WorkflowableEntityMapper, self).schema_and_definitions(
                schema_role=schema_role)
        properties = schema['properties']
        assert 'in_state' not in properties, schema
        properties['in_state'] = {
            'type': 'string',
            'title': self._cw._('state'),
            'readOnly': True,
        }
        return schema, defns

    def serialize(self):
        data = super(WorkflowableEntityMapper, self).serialize()
        wfentity = self.entity.cw_adapt_to('IWorkflowable')
        data['in_state'] = wfentity.state
        return data


class TargetEntityMapper(EntityMapper, TargetETypeMapper):
    """Specialized version of :class:`TargetETypeMapper` and
    :class:`EntityMapper` selectable for an *entity* as target of (`rtype`,
    `role`) relation.
    """
    __select__ = match_kwargs('entity', 'rtype', 'role')


class TrInfoEntityMapper(ETypeMapper):
    """Mapper for TrInfo entity types associated with an entity."""
    __select__ = (
        match_kwargs({'etype': 'TrInfo'})
        & _for_workflowable_entity()
    )

    @add_links
    def schema_and_definitions(self, schema_role=None):
        # For creation role, we return a custom schema (which is quite
        # unrelated to Yams schema) so that the end user sees a document with
        # the name of the transition (and a comment) instead of getting
        # exposed to the implementation details of CubicWeb workflows data
        # model.
        if schema_role != CREATION_ROLE:
            return super(TrInfoEntityMapper, self).schema_and_definitions(
                schema_role=schema_role)
        entity = self.cw_extra_kwargs['for_entity']
        wfobj = entity.cw_adapt_to('IWorkflowable')
        _ = self._cw._
        transitions_choice = [{'enum': [tr.name], 'title': _(tr.name)}
                              for tr in wfobj.possible_transitions()]
        if not transitions_choice:
            return False, None
        schema = {
            'type': 'object',
            'properties': {
                'name': {
                    'type': 'string',
                    'oneOf': transitions_choice,
                },
                'comment': {
                    'type': 'string'
                },
            },
            'required': ['name'],
        }
        return add_descriptive_metadata(schema, self), None
