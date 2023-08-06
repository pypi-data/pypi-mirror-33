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
"""Mappers with "jsonschema.collection" regid."""

from six import text_type

from logilab.common.registry import yes
from cubicweb import (
    neg_role,
    Unauthorized,
)
from cubicweb.predicates import (
    match_kwargs,
)

from cubicweb_jsonschema import (
    CREATION_ROLE,
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
    yams_component_target,
    yams_final_rtype,
)
from . import _utils


__all__ = [
    'CollectionMapper',
    'EntityCollectionMapper',
    'RelatedCollectionMapper',
    'CollectionItemMapper',
    'CompositeRelationItemMapper',
]


@JSONSchemaSerializer.register
class CollectionMapper(JSONSchemaMapper):
    """Mapper for a collection of entities."""
    __regid__ = 'jsonschema.collection'

    def __repr__(self):
        return '<{0.__class__.__name__}>'.format(self)

    @add_links
    def schema_and_definitions(self, schema_role=None):
        if schema_role == CREATION_ROLE:
            return self._submission_schema_and_definitions()
        return self._array_schema(schema_role=schema_role)

    def _submission_schema_and_definitions(self):
        # Disallow submission as we have no knowledge of target entity type in
        # this mapper.
        return False, {}

    def _array_schema(self, schema_role=None):
        item_mapper = self.select_mapper(
            'jsonschema.item', **self.cw_extra_kwargs)
        items_schema, items_defs = item_mapper.schema_and_definitions(
            schema_role)
        schema = {
            'type': 'array',
            'items': items_schema,
        }
        return add_descriptive_metadata(schema, self), items_defs

    def links(self, schema_role=None):
        """Yield Link appobjects matching regid and selection context of this
        mapper if schema_role is None.
        """
        if schema_role is not None:
            return
        for link in super(CollectionMapper, self).links(
                schema_role=schema_role):
            yield link

    def serialize(self, entities):
        """Return a list of collection item representing each entity in
        `entities`.
        """
        def mapper(entity):
            """Select jsonschema.item mapper using entity's type."""
            return self.select_mapper(
                'jsonschema.item',
                etype=entity.cw_etype, **self.cw_extra_kwargs)

        return [mapper(entity).serialize(entity) for entity in entities]


@JSONSchemaDeserializer.register
class EntityCollectionMapper(CollectionMapper):
    """Mapper for a collection of entities of a given type."""
    __regid__ = 'jsonschema.collection'
    __select__ = CollectionMapper.__select__ & match_kwargs('etype')

    def __repr__(self):
        return '<{0.__class__.__name__} etype={0.etype}>'.format(self)

    @property
    def etype(self):
        return self.cw_extra_kwargs['etype']

    @property
    def title(self):
        """Title of the collection, plural form of entity type."""
        return self._cw._('{}_plural').format(self.etype)

    def _submission_schema_and_definitions(self):
        """Delegate generation of schema and definitions to the "entity"
        mapper corresponding to the entity type in this collection.
        """
        mapper = self.select_mapper(
            'jsonschema.entity', **self.cw_extra_kwargs)
        return mapper.schema_and_definitions(schema_role=CREATION_ROLE)

    def values(self, instance):
        mapper = self.select_mapper(
            'jsonschema.entity', **self.cw_extra_kwargs)
        return mapper.values(instance)

    def serialize(self, entities):
        """Return a list of collection item representing each entity in
        `entities`.
        """
        mapper = self.select_mapper('jsonschema.item', **self.cw_extra_kwargs)
        return [mapper.serialize(entity) for entity in entities]


class RelatedCollectionMapper(EntityCollectionMapper):
    """Mapper for a collection of entities through an *inlined* relation."""
    __select__ = (
        match_kwargs('entity', 'rtype', 'role')
        & yams_component_target()
    )

    def __repr__(self):
        return ('<{0.__class__.__name__}'
                ' rtype={0.rtype} role={0.role}>'.format(self))

    @property
    def role(self):
        return self.cw_extra_kwargs['role']

    @property
    def rtype(self):
        return self.cw_extra_kwargs['rtype']

    @property
    def title(self):
        """Title of the collection, name of the relation."""
        return self._cw._(self.rtype if self.role == 'subject'
                          else self.rtype + '-object')

    def _submission_schema_and_definitions(self):
        """Delegate generation of schema and definitions to the "entity"
        mapper selected with possible target of `rtype`, `role` bound to this
        mapper.
        """
        rschema = self._cw.vreg.schema[self.rtype]
        target_types = rschema.targets(role=self.role)
        assert len(target_types) == 1, \
            'cannot handle multiple target types in {}'.format(self)
        target_type = target_types[0]
        entity = self.cw_extra_kwargs['entity']
        mapper = self.select_mapper(
            'jsonschema.entity', etype=target_type,
            rtype=self.rtype, role=neg_role(self.role),
            target_types={entity.cw_etype},
        )
        return mapper.schema_and_definitions(schema_role=CREATION_ROLE)


class NonInlinedRelatedCollectionMapper(RelatedCollectionMapper):
    """Mapper for a collection of entities through a non-*inlined* relation."""
    __select__ = (
        match_kwargs('entity', 'rtype', 'role')
        & ~yams_component_target()
    )

    def _submission_schema_and_definitions(self):
        """Return schema and definitions accounting for constraints on
        possible targets of `rtype`, `role` relation information for `entity`
        bound to this mapper.
        """
        entity = self.cw_extra_kwargs['entity']
        rschema = self._cw.vreg.schema[self.rtype]
        # XXX similar loop in ETypeRelationItemMapper.relation_targets().
        ids = []
        for target_type in rschema.targets(role=self.role):
            try:
                rset = entity.unrelated(
                    self.rtype, target_type, role=self.role)
            except Unauthorized:
                continue
            for target in rset.entities():
                ids.append({
                    'type': 'string',
                    'enum': [text_type(target.eid)],
                    'title': target.dc_title(),
                })
        if not ids:
            return False, None
        properties = {
            'id': {
                'oneOf': ids,
            },
        }
        schema = object_schema(properties, required=['id'])
        return add_descriptive_metadata(schema, self), None


@JSONSchemaSerializer.register
class CollectionItemMapper(JSONSchemaMapper):
    """Mapper for an item of a collection."""
    __regid__ = 'jsonschema.item'
    __select__ = yes()

    @add_links
    def schema_and_definitions(self, schema_role=None):
        """Return either a string schema or an object with "type", "id and
        "title" properties.
        """
        if schema_role == CREATION_ROLE:
            raise ValueError(
                '{} is not appropriate for submission role'.format(self))
        schema = {
            'type': 'object',
            'properties': {
                'type': {
                    'type': 'string',
                },
                'id': {
                    'type': 'string',
                },
                'title': {
                    'type': 'string',
                },
            },
        }
        return add_descriptive_metadata(schema, self), {}

    def links(self, schema_role=None, **kwargs):
        kwargs['anchor'] = '#'
        return super(CollectionItemMapper, self).links(
            schema_role=schema_role, **kwargs)

    @staticmethod
    def serialize(entity):
        """Return a dictionary with entity represented as a collection item."""
        return {
            'type': entity.cw_etype.lower(),
            'id': text_type(entity.eid),
            'title': entity.dc_title(),
        }


class TrInfoCollectionMapper(EntityCollectionMapper):
    """Mapper for a collection of TrInfo associated with an entity."""
    __select__ = (
        match_kwargs({'etype': 'TrInfo'})
        & _for_workflowable_entity()
    )

    def values(self, *args):
        # This is handled by the view.
        raise NotImplementedError()

    def serialize(self):
        entity = self.cw_extra_kwargs['for_entity']
        wfobj = entity.cw_adapt_to('IWorkflowable')
        entities = wfobj.workflow_history
        return super(TrInfoCollectionMapper, self).serialize(entities)


class CompositeRelationItemMapper(CollectionItemMapper):
    """Mapper for items target of a composite relation."""
    __select__ = (
        ~yams_final_rtype()
        & yams_component_target()
        & (match_kwargs('etype') | match_kwargs('entity'))
        & match_kwargs('target_types')
    )

    # Per yams_component_target selector, 'rtype' and 'role' kwargs should be
    # present but 'target_types' is optional.
    def __init__(self, _cw, rtype, role, target_types=None,
                 etype=None, entity=None, **kwargs):
        super(CompositeRelationItemMapper, self).__init__(_cw, **kwargs)
        self.rtype = rtype
        self.role = role
        self.target_types = list(_utils.relation_target_types(
            _cw.vreg.schema, rtype, role, target_types))
        if etype is not None:
            self.etype = etype
        elif entity is not None:
            self.etype = entity.cw_etype

    def _inlined_relation(self):
        """Return True if relation from selection context is "inlined" per
        jsonschema uicfg.
        """
        rsection = self._cw.vreg['uicfg'].select('jsonschema', self._cw)
        tags = set([
            rsection.get(
                self.etype, self.rtype, target_type, self.role)
            for target_type in self.target_types
        ])
        if len(tags) != 1:
            raise ValueError(
                'inconsistent rtag for {} with {} as {} (targets: {})'.format(
                    self.rtype, self.etype, self.role, self.target_types)
            )
        # We actually check for both "inlined" and "hidden", since a
        # CompoundMapper may set a relation to "hidden" while we'll still want
        # it to be considered as "inlined" in this context. XXX
        return tags.pop() in ('inlined', 'hidden')

    def schema_and_definitions(self, schema_role=None):
        """Return schema and definitions for an item of a relation collection.

        In "creation" role, schema a oneOf with possible target types entity
        JSON schema. Otherwise, depending on wether the relation in "inlined"
        per jsonschema uicfg, either a full entity JSON Schema is returned or
        a genertic collection item JSON Schema.
        """
        if schema_role != CREATION_ROLE and not self._inlined_relation():
            return super(CompositeRelationItemMapper,
                         self).schema_and_definitions(schema_role=schema_role)
        items, definitions = [], ProtectedDict()
        for target_type in self.target_types:
            mapper = self.select_mapper(
                'jsonschema.entity', etype=target_type,
                rtype=self.rtype, role=neg_role(self.role),
                target_types={self.etype},
            )
            subschema, defs = mapper.schema_and_definitions(schema_role)
            items.append({
                '$ref': '#/definitions/{}'.format(target_type),
            })
            definitions[target_type] = subschema
            if defs:
                definitions.update(defs)
        nitems = len(items)
        if nitems == 0:
            return None, None
        elif nitems == 1:
            return items[0], definitions
        else:
            schema = {
                'oneOf': items,
            }
            return schema, definitions
