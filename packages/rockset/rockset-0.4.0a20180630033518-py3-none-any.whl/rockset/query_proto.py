""" This is an internal module that will NOT be shipped as part of client SDK.
It adds a proto() method to all Query classes defined in query.py
Import this class to "extend" all Query classes with a new proto() method,
but continue to use classes defined in query.py directly for building queries.

Usage:

    from rockset import Q, F
    import rockset.query_proto

    q = ((F.last_name == "Gray") && (F.age < 40))
    print(q.proto())
    print(q.sexpression())

"""
from rockset import query_pb2, query_field_path_pb2, \
    field_query_pb2, value_pb2, regex_pb2
from rockset.query import *
from rockset.value import encode, decode


class _QueryProto(Query):
    def proto(self):
        """ Returns the Rockset protobuf representation of the query

        Returns:
            rockset.query_pb2.Query: query's protobuf representation
        """
        return NotImplementedError(
            'Class {} does not implement proto()', type(self)
        )


Query.proto = _QueryProto.proto


class _QueryStringSexprProto(Query):
    def proto(self):
        if self._sexpr == '(all)':
            return _AllQueryProto().proto()
        raise ValueError('cannot generate proto for arbitrary s-expressions')


QueryStringSexpr.proto = _QueryStringSexprProto.proto


class _QueryStringResourceProto(Query):
    def proto(self):
        return _AllQueryProto().proto()


QueryStringResource.proto = _QueryStringResourceProto.proto


class _MultiTermQueryProto(MultiTermQuery):
    def _proto_mt(self, field):
        p = query_pb2.Query()
        getattr(p, field).children.extend(c.proto() for c in self.children)
        return p


MultiTermQuery._proto_mt = _MultiTermQueryProto._proto_mt


class _AndQueryProto(AndQuery):
    def proto(self):
        return self._proto_mt('and_query')


AndQuery.proto = _AndQueryProto.proto


class _OrQueryProto(OrQuery):
    def proto(self):
        return self._proto_mt('or_query')


OrQuery.proto = _OrQueryProto.proto


class _NotQueryProto(NotQuery):
    def proto(self):
        p = query_pb2.Query()
        nq = p.not_query
        nq.child.CopyFrom(self.negated.proto())
        return p


NotQuery.proto = _NotQueryProto.proto


class _DifferenceQueryProto(DifferenceQuery):
    def proto(self):
        p = query_pb2.Query()
        dq = p.difference_query
        dq.base.CopyFrom(self.base.proto())
        dq.diminisher.CopyFrom(self.diminisher.proto())
        return p


DifferenceQuery.proto = _DifferenceQueryProto.proto


class _FieldEqQueryProto(FieldEqQuery):
    def proto(self):
        p = query_pb2.Query()
        fq = p.field_query
        fq.field.CopyFrom(self.field.proto())
        fq.binary.code = field_query_pb2.BinaryOp.EQ
        fq.binary.other.CopyFrom(encode(self.value))
        return p


FieldEqQuery.proto = _FieldEqQueryProto.proto


class _FieldOpQueryProto(FieldOpQuery):
    def proto(self):
        p = query_pb2.Query()
        fq = p.field_query
        fq.field.CopyFrom(self.field.proto())
        if self.op == 'lt':
            fq.binary.code = field_query_pb2.BinaryOp.LT
            fq.binary.other.CopyFrom(encode(self.value))
        elif self.op == 'le':
            fq.binary.code = field_query_pb2.BinaryOp.LE
            fq.binary.other.CopyFrom(encode(self.value))
        elif self.op == 'gt':
            fq.binary.code = field_query_pb2.BinaryOp.GT
            fq.binary.other.CopyFrom(encode(self.value))
        elif self.op == 'ge':
            fq.binary.code = field_query_pb2.BinaryOp.GE
            fq.binary.other.CopyFrom(encode(self.value))
        elif self.op == 'prefix':
            fq.string_prefix = decode(self.value)
        elif self.op == 'regex':
            regex = regex_pb2.Regex()
            regex.pattern = decode(self.value)
            fq.string_regex.CopyFrom(regex)
        else:
            raise NotImplementedError('dont support %s yet' % self.op)
        return p


FieldOpQuery.proto = _FieldOpQueryProto.proto


class _FieldIsDefinedQueryProto(FieldIsDefinedQuery):
    def proto(self):
        p = query_pb2.Query()
        fq = p.field_query
        fq.unary = field_query_pb2.FieldQuery.IS_DEFINED
        fq.field.CopyFrom(self.field.proto())
        return p


FieldIsDefinedQuery.proto = _FieldIsDefinedQueryProto.proto


class _FieldIsNotNullQueryProto(FieldIsNotNullQuery):
    def proto(self):
        p = query_pb2.Query()
        fq = p.field_query
        fq.unary = field_query_pb2.FieldQuery.IS_NOT_NULL
        fq.field.CopyFrom(self.field.proto())
        return p


FieldIsNotNullQuery.proto = _FieldIsNotNullQueryProto.proto


class _ApplyQueryProto(ApplyQuery):
    def proto(self):
        p = query_pb2.Query()
        aq = p.apply_query
        aq.to_field.CopyFrom(self.to_field.proto())
        aq.child.CopyFrom(self.child.proto())
        return p


ApplyQuery.proto = _ApplyQueryProto.proto


class _AllQueryProto(AllQuery):
    def proto(self):
        p = query_pb2.Query()
        p.all_query.SetInParent()
        return p


AllQuery.proto = _AllQueryProto.proto


class _AggregateQueryProto(AggregateQuery):
    def proto(self):
        p = query_pb2.Query()
        aggq = p.aggregate_query
        aggq.dimension_fields.extend(
            [df.proto() for df in self.dimension_fields]
        )
        aggq.aggregate_fields.extend(
            [af.proto() for af in self.aggregate_fields]
        )
        aggq.child.CopyFrom(self.child.proto())
        return p


AggregateQuery.proto = _AggregateQueryProto.proto


class _SortQueryProto(SortQuery):
    def proto(self):
        p = query_pb2.Query()
        sq = p.sort_query
        if self.mode == 'asc':
            sq.mode = query_pb2.ASC
        elif self.mode == 'desc':
            sq.mode = query_pb2.DESC
        else:
            raise NotImplementedError("only asc & desc are supported")
        sq.fields.extend([f.proto() for f in self.fields])
        sq.child.CopyFrom(self.child.proto())
        return p


SortQuery.proto = _SortQueryProto.proto


class _LimitQueryProto(LimitQuery):
    def proto(self):
        p = query_pb2.Query()
        lq = p.limit_query
        lq.max_results = self.max_results
        lq.skip = self.skip_results
        lq.child.CopyFrom(self.child.proto())
        return p


LimitQuery.proto = _LimitQueryProto.proto


class _SubQueryProto(SubQuery):
    def proto(self):
        p = query_pb2.Query()
        p.CopyFrom(self.child.proto())
        return p


SubQuery.proto = _SubQueryProto.proto


class _SelectQueryProto(SelectQuery):
    def proto(self):
        p = query_pb2.Query()
        sq = p.select_query
        for f in self.fields:
            sq.fields.add().name.CopyFrom(f.proto())
        sq.child.CopyFrom(self.child.proto())
        return p


SelectQuery.proto = _SelectQueryProto.proto


class _WhereQueryProto(WhereQuery):
    def proto(self):
        return (self.pred & self.child).proto()


WhereQuery.proto = _WhereQueryProto.proto


class _FieldRefProto(FieldRef):
    def proto(self):
        fp = query_field_path_pb2.QueryFieldPath()
        for p in self._path():
            c = fp.components.add()
            if isinstance(p, slice):
                assert p.start is None and p.stop is None and p.step is None, \
                    'Invalid slice'
                c.all_indexes.SetInParent()
            elif isinstance(p, str):
                c.key = p
            elif isinstance(p, int):
                c.index = p
            else:
                assert False, 'Invalid path type ' + type(p)
        return fp


FieldRef.proto = _FieldRefProto.proto


class _AggFieldRefProto(AggFieldRef):
    def proto(self):
        self._check_valid_alias()
        af = query_pb2.AggregateField()
        if self._aggregate_op == 'min':
            af.function = query_pb2.MIN
        elif self._aggregate_op == 'max':
            af.function = query_pb2.MAX
        elif self._aggregate_op == 'avg':
            af.function = query_pb2.AVG
        elif self._aggregate_op == 'sum':
            af.function = query_pb2.SUM
        elif self._aggregate_op == 'count':
            af.function = query_pb2.COUNT
        elif self._aggregate_op == 'countdistinct':
            af.function = query_pb2.COUNTDISTINCT
        elif self._aggregate_op == 'approximatecountdistinct':
            af.function = query_pb2.APPROXIMATECOUNTDISTINCT
        elif self._aggregate_op == 'collect':
            af.function = query_pb2.COLLECT
        else:
            raise NotImplementedError(
                'dont support agg %s yet!' % self._aggregate_op
            )
        af.field.CopyFrom(self._field.proto())
        af.alias = self._alias
        return af


AggFieldRef.proto = _AggFieldRefProto.proto
