
from .encoders import DATE_FORMAT
from .utils import recursive_dict_update

FILTER_OPS = {
    'eq': '$eq',
    'is': '$eq',
    'ne': '$ne',
    'isnt': '$ne',
    'gt': '$gt',
    'gte': '$gte',
    'lt': '$lt',
    'lte': '$lte',
    'in': '$in',
    'nin': '$nin',
}

class QueryParser:

    @staticmethod
    def _get_query(key, opval, coerce_fn):
        """Parses token and returns subquery based on operator inside token

        :param key      - name of the field
        :param opval   - string in format operator.value, operator is optional, defaults to eq

        Supported operators vs Mongo equivalent:
            eq  - $eq, default
                filter=animal:eq.cat
                filter=animal:cat - alternative notation
            ne  - $ne - complementary operator for eq
            gte - $gte
            lte - $lte
                filter=_created:gte.2018-02-12T14:26:09.666000Z
            gt  - $gt
            lt  - $lt
                filter=_created:lt.2018-02-12T14:26:09.666000Z
            is  - $eq - in this case 'null' is converted to None, 'false' to False, 'true' to True
                filter=backup:is.null
            isnt- $ne - complementary operator for is
            in  - $in - use '|' as separator
                filter=status:in.running|canceled
            nin  - $nin - complementary operator for in
                filter=status:nin.running|pending

        """
        if not isinstance(opval, str):
            return opval

        tokens = opval.split('.', 1)
        # Ve have value only - use default eq operator
        if len(tokens) == 1:
            return {key: coerce_fn(opval)}

        operator, val = tokens

        if operator in ('in', 'nin',):
            val = [coerce_fn(value) for value in val.split('|')]
        elif operator in ('is', 'isnt'):
            lval = val.lower()
            # Value transformation
            if lval in ('true', 'false'):
                val = lval == 'true'  # Hipster transformation to bool
            elif lval in ('null', 'none'):
                val = None
            else:
                raise ValueError('Query: {}.{} is invalid - invalid value for such operation'.format(operator, val))
        else:
            val = coerce_fn(val)

        return {key: {FILTER_OPS[operator]: val}}

    @classmethod
    def parse_filter(cls, query_str, coerce_fn):
        """Parses ?filter=. Raises ValueError"""
        query = {}
        if query_str:
            tokens = query_str.split(';')  # Use ; as separator

            for token in tokens:
                key, opval = token.split(':', 1)
                subquery = cls._get_query(key, opval, coerce_fn(key))
                if not subquery:
                    raise ValueError('Invalid query: {}'.format(token))
                recursive_dict_update(query, subquery)
        return query

    @staticmethod
    def parse_limit(query_str):
        """Parses ?limit=. Raises ValueError"""
        query_str = query_str or 0
        return int(query_str) or None

    @staticmethod
    def parse_sort(query_str):
        """Parses ?sort=. Raises ValueError"""
        if query_str:
            return query_str.replace(';', ',')  # Allow both (;,) as separator

    @staticmethod
    def parse_projection(query_str):
        """Parses ?fields=. Raises ValueError"""
        if query_str:
            return query_str.replace(';', ',').split(',')  # Allow both (;,) as separator
