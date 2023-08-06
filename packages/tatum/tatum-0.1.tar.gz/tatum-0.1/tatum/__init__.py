from utils import *

class Chaining(object):
    """ Basic ActiveRecord-like wrapper for PyMongo queries

    Usage:

    # Example 1
    query = Chaining(<Collection Object>).select('<field_name>') \
                                         .find(<field_name>, <field_value>) \
                                         .limit(10)

     for docs in query.all():
        # iterate docs

    # Example 2
    query = Chaining(<Collection Object>).select('<field_name>') \
                                         .select('<field_name2>') \
                                         .find('<field_name>', '<field_value>') \
                                         .sort(<field_name>, <order>)

     count = query.count()
        => {"count": <documents count>}

    # Example 3
    query = Chaining(<Collection Object>).select('<field_name>') \
                                         .select('<field_name2>') \
                                         .group(<field_name>) \
                                         .group(<field_name2>) \

     for docs in query.all():
        for doc in docs['items']:
            # perform actions on doc

    Instance Methods:
    select  --  'SELECT' operator
    find    --  'WHERE' operator
    sort    --  'ORDER BY' operator
    group   --  'GROUP' operator
    limit   --  'LIMIT' operator
    skip    --  'OFFSET' operator
    count   --  'COUNT' operator. executes the query.
    all     --  prepare and execute query
    """
    __dict__ = {}

    @accepts(object, object)
    def __init__(self, collection):
        """ Set collection to be queried

        Arguments:
        collection    -- a MongoDB Collection object
        """
        self.collection = collection

    @accepts(object, str, (str, object, dict))
    def find(self, field, value):
        """Return self.

        add a condition to the query. does not support $or conditions at the moment.

        Keyword arguments:
        field         -- name of the field
        value         -- field value. can contain strings, regex or dictionaries
        """
        self.__add_missing('$match')

        self.__dict__['$match'][field] = value

        return self

    @accepts(object, str, (int, dict))
    def select(self, field, specification=1):
        """Return self.

        add a field to be retrieved by the query.

        Keyword arguments:
        field         -- name of the field
        specification -- projection specification (default 1)
        """
        self.__add_missing('$project')

        self.__dict__['$project'][field] = specification

        return self

    @accepts(object, str, int)
    def sort(self, field, order=1):
        """Return self.

        add a field to sort the results by.

        Keyword arguments:
        field         -- name of the field
        order         -- accepts 1 (pymongo.ASCENDING) or -1 (pymongo.DESCENDING)
        """
        self.__add_missing('$sort')

        self.__dict__['$sort'][field] = order

        return self

    @accepts(object, str, str, str, dict)
    def group(self, field, items_key="items", items="$$ROOT", kw_fields={}):
        """Return self.

        add a field to group the results by.

        Keyword arguments:
        field         -- name of the field to group by
        items_key     -- name given to the array of aggregated
                         fields or documents (default "items")
        items         -- items to be retrieved in the array
                         (default "$$ROOT". retrieves whole document.)
        kw_fields     -- arbitrary (k,v) pairs to be added to $group query
        """
        self.__add_missing('$group', [])

        # https://docs.mongodb.com/manual/reference/operator/aggregation/group/
        # see MongoDB $group documentation on how to $push single fields instead
        # of the whole document
        query = {
            '_id': "${}".format(field),
            items_key: {'$push': items}
        }

        # add arbitrary fields into the $group query. notice 'count' can also
        # be added via the public 'count' method.
        for k,v in kw_fields.iteritems():
            query[k] = v

        self.__dict__['$group'].append(query)

        return self

    @accepts(object, str)
    def count(self, k="count"):
        """Return self.

        count results. when combined with $group - returns results and their respective counters.

        Keyword arguments:
        k             -- name of the retrieved field (default "count")

        Notes:
        count triggers the retrieval of the documents.
        """
        if self.__dict__.has_key('$group'):
            for group in self.__dict__['$group']:
                group["count"] = {'$sum': 1}
        else:
            self.__add_missing("$count")
            self.__dict__["$count"] = k

        return self.all()

    @accepts(object, int)
    def limit(self, v):
        """Return self.

        limit retrieved results.

        Keyword arguments:
        v             -- amount of results to be retrieved
        """
        self.__add_missing('$limit', int())

        self.__dict__['$limit'] = v

        return self

    @accepts(object, int)
    def skip(self, v):
        """Return self.

        set results offset.

        Keyword arguments:
        v             -- offset to skip results by

        Notes:
        doesn't work with $groups.
        """
        self.__add_missing('$skip', int())

        self.__dict__['$skip'] = v

        return self

    @accepts(object, int)
    def sample(self, v):
        """Return self.

        sample random results.

        Keyword arguments:
        v             -- amount of results to be retrieved
        """
        self.__add_missing('$sample', int())

        self.__dict__['$sample'] = v

        return self

    def all(self):
        """Return a query Cursor.

        query the db and return a cursor of the results.
        """
        # an aggregation query must have a $match field, even if it's empty
        self.__add_missing("$match")

        # prepare query
        query = self.__prepare()

        return self.collection.aggregate(query)

    def __add_missing(self, agg_name, agg_type=None):
        """ Add query condition if it doesn't already exist """
        # NOTE: supplying 'agg_type={}' as a parameter caused some
        # unexpected behaviour, so we perform it here instead.
        agg_type = {} if agg_type is None else agg_type

        if not self.__dict__.has_key(agg_name):
            self.__dict__[agg_name] = agg_type

    def __prepare(self):
        """Return query

        prepare query before execution
        """
        query = []

        # iterate query fields and values
        for k, v in self.__dict__.iteritems():
            # when field value is a list (as with $group), we need to
            # append each condition to the query by itself
            if isinstance(v, list):
                [query.append({k: item}) for item in v]
            else:
                query.append({k: v})

        return query

name = "tatum"