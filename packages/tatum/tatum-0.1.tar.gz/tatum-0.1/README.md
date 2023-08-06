Tatum - A Simple PyMongo Chaining Wrapper
--------

Usage:

# Example 1 - find by field's value and project that field. limit to 10 results:
>>> query = Chaining(<Collection Object>).select('<field_name>') \
                                         .find(<field_name>, <field_value>) \
                                         .limit(10)

>>> for docs in query.all():
>>>    # iterate docs

# Example 2 - find by field's value, project 2 fields and sort by field:
>>> query = Chaining(<Collection Object>).select('<field_name>') \
                                         .select('<field_name2>') \
                                         .find('<field_name>', '<field_value>') \
                                         .sort(<field_name>, <order>)

>>> count = query.count()
>>> #   => {"count": <documents count>}

# Example 3 - find all. group by 2 fields and project these fields:
>>> query = Chaining(<Collection Object>).select('<field_name>') \
                                         .select('<field_name2>') \
                                         .group(<field_name>) \
                                         .group(<field_name2>) \

>>> for docs in query.all():
>>>    for doc in docs['items']:
>>>        # perform actions on doc
