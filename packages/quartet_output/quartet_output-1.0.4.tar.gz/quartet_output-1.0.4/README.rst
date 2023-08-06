=============================
quartet_output
=============================

.. image:: https://gitlab.com/serial-lab/quartet_output/badges/master/coverage.svg
   :target: https://gitlab.com/serial-lab/quartet_output/pipelines
.. image:: https://gitlab.com/serial-lab/quartet_output/badges/master/build.svg
   :target: https://gitlab.com/serial-lab/quartet_output/commits/master
.. image:: https://badge.fury.io/py/quartet_output.svg
    :target: https://badge.fury.io/py/quartet_output

Output Rules and logic for QU4RTET supply chain and trading-partner messaging.

Intro
-----
The `quartet_output` module is responsible for inspecting inbound messages
and, based on criteria defined by users, singling out some of those messages
for further processing.  Once a message has been filtered, it is typically
used to create a new message from some existing EPCIS data or to simply
create a new message using the same data with the intent of sending that
message to another system.

Criteria
--------
The `quartet_output` module allows users to define *EPCIS Output Criteria*
definitions.  These definitions allow users to instruct the module to look
at inbound EPCIS events and look for events that meet certain selection
criteria.  For example, users can define criteria that would inspect all
inbound *Transaction Events* of action *ADD* from a specific *bizLocation*
with a *Purchase Order* business transaction attached.  Once an event
arrives meeting these criteria, the system allows a user to use that event
to trigger the generation of a shipping event along with all of the serial
numbers for the epcs specified in the triggering event.  Other scenarios are
possible as well and, of course, users can implement *Rules* and *Steps* of
their own that do just about anything once an inbound event has been filtered.

Transport
---------
`quartet_output` allows users to configure transport configurations using
both `EndPoint` and `AuthenticationInfo` database models.  These models are
attached to the criteria that filter EPCIS events and allow the user to
specify where messages should be sent once an event has been filtered and
has triggered any outbound processing logic.

Documentation
-------------

The full documentation is located here:

https://serial-lab.gitlab.io/quartet_output

Quickstart
----------

Install quartet_output

.. code-block:: text

    pip install quartet_output

Add it to your `INSTALLED_APPS`:

.. code-block:: text

    INSTALLED_APPS = (
        ...
        'quartet_output.apps.QuartetOutputConfig',
        ...
    )

Add quartet_output's URL patterns:

.. code-block:: text

    from quartet_output import urls as quartet_output_urls


    urlpatterns = [
        ...
        url(r'^', include(quartet_output_urls)),
        ...
    ]

Features
--------

* Output determination allows you to create filters on inbound EPCIS data
  and determine which inbound EPCIS events trigger outbound business messaging.

* Define HTTP and HTTPS end points for trading partners.

* Define various authentication schemes for external end points.

* Outbound messages take advantage of the `quartet_capture` rule engine by
  creating a new outbound task for every message.  This puts every outbound
  task on the Celery Task Queue- allowing you to scale your outbound messaging
  to your liking.


Running The Unit Tests
----------------------

.. code-block:: text

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox

