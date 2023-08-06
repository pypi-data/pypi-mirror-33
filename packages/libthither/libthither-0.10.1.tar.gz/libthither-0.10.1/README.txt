Thither.Direct library for python
============================

Check out the `documentation`__ for more complete examples.

.. __: https://thither.direct/information/services/commercial/index


Installation
------------

Install python libthither:

.. code-block:: console

    pip install libthither
    


Creating a Flow Metrics Statistics Client
------------------------

.. code-block:: python

    from libthither.api.fms import FlowMetricsStatisticsClient

    client = FlowMetricsStatisticsClient(
        'YourFlowID',
        pass_phrase='YourPassPhrase',
        https=True,
        cipher='',
        keep_alive=True,
        json=False
        requests_args={},
        )
    # after initiated, client can be called with:
    client.push_single(YourMetricId, DateAndTime, Value)
    client.push_list([[Metric ID, DateTime, Value],])
    client.push_csv_data("mid,dt,v\nYourMetricId,DateAndTime,Value")

