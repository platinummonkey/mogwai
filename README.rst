mogwai
======

mogwai in an object-graph mapper (OGM) designed specifically for use with Titan
(http://thinkaurelius.github.io/titan/) via RexPro (https://github.com/tinkerpop/rexster/wiki/RexPro).
Mogwai supports easily integrating Gremlin graph-traversals with vertex and edge models. For those
already familiar with Blueprints (https://github.com/tinkerpop/blueprints/wiki) there is is a
simple example.

.. image:: https://app.wercker.com/status/767e3cb41d7c6866fd88712bda8fede2/m/master
   :alt: Build Status
   :align: center
   :target: https://app.wercker.com/project/bykey/767e3cb41d7c6866fd88712bda8fede2


Documentation
=============

mogwai documentation can be found at http://mogwai.readthedocs.org/

Installation
============

``$ pip install mogwai``

Testing
=======

To get mogwai unit tests running you'll need a titan installation with rexster server configured with a mogwai graph::

    <graph>
        <graph-name>mogwai</graph-name>
        <graph-type>com.thinkaurelius.titan.tinkerpop.rexster.TitanGraphConfiguration</graph-type>
        <graph-read-only>false</graph-read-only>
        <graph-location>/tmp/mogwai</graph-location>
        <properties>
              <storage.backend>local</storage.backend>
              <storage.directory>/tmp/mogwai</storage.directory>
              <buffer-size>100</buffer-size>
        </properties>

        <extensions>
          <allows>
            <allow>tp:gremlin</allow>
          </allows>
        </extensions>
    </graph>



Pull Requests
=============

General Rules:
  - All Tests must pass
  - Coverage shouldn't decrease
  - All Pull Requests should be rebased against master **before** submitting the PR.


