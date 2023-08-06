Thither.Direct library for python
============================

Installation
------------
    pip install libthither

##  THE LIBRARY
+ APIs are:
  + Flow Metrics Statistics Client
    + push_single
    + push_list
    + push_csv_data
    + get_definitions
    + get_stats
  + (more to come)
+ Utils: 
  + (still to come)


Creating a Flow Metrics Statistics Client
------------------------

.. code-block:: python

    from libthither.api.fms import FlowMetricsStatisticsClient

    client = FlowMetricsStatisticsClient(
        'YourFlowID',
        pass_phrase='YourPassPhrase',
        keep_alive=True,
        # https=False,
        # cipher='AES',
        # json=False,
		# version='v201807',
        # requests_args={},
        )
    # after initiated, client can be called with:
    client.push_single(YourMetricId, DateAndTime, Value)
    client.push_list([[Metric ID, DateTime, Value],])
    client.push_csv_data("mid,dt,v\nYourMetricId,DateAndTime,Value")

More information at:
	https://thither.direct/information/services/commercial/index
	https://github.com/thither/Thither.Direct-client-libraries/tree/master/python
