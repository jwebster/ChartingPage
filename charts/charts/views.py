from django.shortcuts import render_to_response, Http404
from django.conf import settings
from django.template import Context, loader, defaultfilters, Library, \
    TemplateDoesNotExist, RequestContext

import pymongo
import json
import time

import datetime
from dateutil.parser import parse


def smart_date(value):

    if type(value) == datetime.datetime:
        return value

    if value == 'today':
        return datetime.datetime.now()
    elif value == 'yesterday':
        return datetime.datetime.now() - datetime.timedelta(days=1)
    elif value == 'tomorrow':
        return datetime.datetime.now() + datetime.timedelta(days=1)
    elif value == 'year_ago':
        return datetime.datetime.now() - datetime.timedelta(days=365)
    elif value == 'start_of_month':
        today = datetime.datetime.today()
        return datetime.datetime(today.year, today.month, 1)
    elif value == 'start_of_year':
        today = datetime.datetime.today()
        return datetime.datetime(today.year, 1, 1)
    else:
        return parse(value, dayfirst=True)


def build_timeseries_chart(period,
                           series,
                           start=None,
                           end=None):

    DB_HOST = ["localhost"]
    DB_PORT = 27017

    db = pymongo.Connection(DB_HOST, DB_PORT)['charts']

    datasets = []
    for s in series:
        resource_type = s['resource']
        field_name = s['field']
        query_filter = s['filter']
        mapreduce_function = s['mapreduce_function']

        query = {}

        if start is not None:
            ts = int(time.mktime(smart_date(start).timetuple())) * 1000
            query = {'_id': {'$gt': '%s' % ts}}

        if end is not None:
            ts = int(time.mktime(smart_date(end).timetuple())) * 1000
            if query == {}:
                query = {'_id': {'$lt': '%s' % ts}}
            else:
                query = {'$and': [{'_id': {'$lt': '%s' % ts}}, query]}

        if query_filter is not None:
            query = {'$and': [{'_id': {'$regex': query_filter}}, query]}
        else:
            query = {'$and': [{'_id': {'$regex': 'all'}}, query]}

        collection = "mapreduce_%s__%s__%s__%s" % (period,
                                                   mapreduce_function,
                                                   resource_type,
                                                   field_name)
        print collection, query
        new_series = []
        for rec in db[collection].find(query):
            key_timestamp = int(rec['_id'].split(':')[0])
            new_series.append([key_timestamp, rec['value']])

        datasets.append({'data': json.dumps(new_series),
                         'label': field_name})
        print field_name, len(new_series)

    return datasets


def home(request):

    period = 'weekly'
    start = 'year_ago'
    end = None

    series = [
        {'resource': 'time_record',
         'field': 'hours',
         'filter': 'employee=/example/employee/500ff1b8e147f74f7000000c/',
         'mapreduce_function': 'sumof'},

        {'resource': 'other_time_record',
         'field': 'hours',
         'filter': 'employee=/example/employee/500ff1b8e147f74f7000000c/',
         'mapreduce_function': 'sumof'}]

    data = build_timeseries_chart(period=period,
                                  series=series,
                                  start=start,
                                  end=end)

    return render_to_response("chart.html",
                              {'datasets': data,

                               },
                              context_instance=RequestContext(request))
