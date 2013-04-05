# Dynamic Charting Page Spec
	Author: James Webster
	Client: Croftsware Ltd
	Date: 2013-04-05
	Version: 1.0

*This repo contains example code sufficient to scope, cost and deliver a specific project. It should only be read in that context.*

## Skills Required
* Python / Django
* jQuery
* HTML & CSS
* MongoDB (ability to install) and familiarity with python library


## Summary
To render data from a mongo db collection as a flot chart. The chart should be dynamically built with parameters set by the user.

An example Django project is included, it has code to read from MongoDB and to render a simple graph. The purpose of this piece of work is to provide user control of that graph.

The user should be able to add and remove series, change the series parameters and generally explore the data in chart form.


## Requirements
*The following requirements are listed in priority order using the [MoSCoW](http://en.wikipedia.org/wiki/MoSCoW_Method) method*

### Must Have
* Page loads with an initial default configuration
* Series can be removed (trigger redraw)
* Add series
	* Can choose colour of series to be added (from defined colour palette)
	* Can choose between bar and line for new series
	* Can choose to display point or not
	* Can specify the labels for the series (defaulting to field names)
	* Can optionally specify a filter
	* Can choose the resolution (e.g. Hourly, Daily, Monthly), it only needs to work with time series data
	* (Series options (e.g. list of filters) can be hard coded, see could haves)
* 'Bookmark': user defined graphs should have a permanent URL so that the chart can be saved.
* User defined start and end points for x-axis

### Should Have
* Reset button to take page back to initial state
* Charting data sets with different time periods x-axis (e.g a timeseries and a numeric series)
* The chart controls should be in keeping with the theme look and feel (additional css should be added in separate files)

### Could Have
* Filters built from the datasets (i.e. scanning the full datasets and collecting the filter & period options)

### Won’t Have
* Charting data sets with different x-axis (e.g a timeseries and a numeric series)
* menus, navigation are out of scope, this page will fit into an existing application



## Notes
Unless specified please use judgement to decide if page / chart should automatically re-draw after a change or if a submit button should be used.



## Constraints
* Use the Flot Library
* Use jQuery
* HTML, CSS & javascript must be independent of the data (i.e. same templates must render both example)
* Files within the theme folder (e.g. css & js) should not be modified, please extract and edit in the root of the static folder.




## The Data
Data is held in MongoDB collections.

	"mapreduce_%s__%s__%s__%s" % (period,
                                  reduce_function,
                                  resource_type,
                                  field_name)

where:
* period might be hourly, daily, weekly, monthly.
* reduce_function might be sumof or average
* resource_type is the 'table' the dataset comes from
* field_name is 'column' within the resource_type or 'table'

The example data is from two different resource type 'time_record' and 'other_time_record' both have a field name of 'hours'. The raw data has been reduced into daily, weekly and monthly collections. For context: the data represents time keeping records for employees. 'time_record' has time logged against clients and 'other_time_record' has time logged against holiday, training admin etc. Both collections refer to URIs rather than specific values (those URIs resolve to real objects in the Sheep namespace).

	mapreduce_daily__sumof__other_time_record__hours
	mapreduce_daily__sumof__time_record__hours
	mapreduce_monthly__sumof__other_time_record__hours
	mapreduce_monthly__sumof__time_record__hours
	mapreduce_weekly__sumof__other_time_record__hours
	mapreduce_weekly__sumof__time_record__hours

Example data from the daily time records collection:

	{ "_id" : "1325376000000:all", "value" : 2 }
	{ "_id" : "1325376000000:employee:client=/example/employee/500ff1b8e147f74f7000000d/:/example/client/5045cc4ce147f79b41000036/", "value" : 2 }
	{ "_id" : "1325376000000:employee=/example/employee/500ff1b8e147f74f7000000d/", "value" : 2 }
	{ "_id" : "1325376000000:client:employee=/example/client/5045cc4ce147f79b41000036/:/example/employee/500ff1b8e147f74f7000000d/", "value" : 2 }
	{ "_id" : "1325376000000:client=/example/client/5045cc4ce147f79b41000036/", "value" : 2 }
	{ "_id" : "1328486400000:all", "value" : 4 }
	{ "_id" : "1328486400000:employee:client=/example/employee/500ff1b8e147f74f7000000c/:/example/client/5045cc4ce147f79b4100001f/", "value" : 4 }
	{ "_id" : "1328486400000:employee=/example/employee/500ff1b8e147f74f7000000c/", "value" : 4 }
	{ "_id" : "1328486400000:client:employee=/example/client/5045cc4ce147f79b4100001f/:/example/employee/500ff1b8e147f74f7000000c/", "value" : 4 }
	{ "_id" : "1328486400000:client=/example/client/5045cc4ce147f79b4100001f/", "value" : 4 }


The Map-Reduce process pre-computes all the values needed to build the charts so that we can load the charts very quickly. This means that all the possible facets must be expanded. In this simple (and typical) example the '_id' key is always a time in milliseconds followed by a query string.

	:all - no filtering
	:employee=X - filtering for employee = X
	:client=Y - filtering for client = Y
	:client:employee=Y:X - filtering for client=Y and employee = X

The MongoDB queries.

After a point in time and with one filter:
	{'$and': [{'_id': {'$regex': 'employee=/example/employee/500ff1b8e147f74f70000001/'}}, {'_id': {'$gt': '1333375507000'}}]}

After a point in time and with two filters:
	{'$and': [{'_id': {'$regex': 'employee:client=/example/employee/500ff1b8e147f74f70000008/:/example/client/5045cc4be147f79b41000002/'}}, {'_id': {'$gt': '1333375590000'}}]}


## Import the test data
These commands will load the json files into the charts database:

	mongoimport --db charts --collection mapreduce_daily__sumof__other_time_record__hours --file mapreduce_daily__sumof__other_time_record__hours.json
	mongoimport --db charts --collection mapreduce_daily__sumof__time_record__hours --file mapreduce_daily__sumof__time_record__hours.json
	mongoimport --db charts --collection mapreduce_monthly__sumof__other_time_record__hours --file mapreduce_monthly__sumof__other_time_record__hours.json
	mongoimport --db charts --collection mapreduce_monthly__sumof__time_record__hours --file mapreduce_monthly__sumof__time_record__hours.json
	mongoimport --db charts --collection mapreduce_weekly__sumof__other_time_record__hours --file mapreduce_weekly__sumof__other_time_record__hours.json
	mongoimport --db charts --collection mapreduce_weekly__sumof__time_record__hours --file mapreduce_weekly__sumof__time_record__hours.json




## Contact
	James Webster james@croftsware.com
	+44 (0) 7526 558 900