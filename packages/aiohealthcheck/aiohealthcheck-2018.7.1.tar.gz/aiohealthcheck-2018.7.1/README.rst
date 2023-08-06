.. image:: https://travis-ci.org/cjrh/aiohealthcheck.svg?branch=master
    :target: https://travis-ci.org/cjrh/aiohealthcheck

.. image:: https://coveralls.io/repos/github/cjrh/aiohealthcheck/badge.svg?branch=master
    :target: https://coveralls.io/github/cjrh/aiohealthcheck?branch=master

.. image:: https://img.shields.io/pypi/pyversions/aiohealthcheck.svg
    :target: https://pypi.python.org/pypi/aiohealthcheck

.. image:: https://img.shields.io/github/tag/cjrh/aiohealthcheck.svg
    :target: https://img.shields.io/github/tag/cjrh/aiohealthcheck.svg

.. image:: https://img.shields.io/badge/install-pip%20install%20aiohealthcheck-ff69b4.svg
    :target: https://img.shields.io/badge/install-pip%20install%20aiohealthcheck-ff69b4.svg

.. image:: https://img.shields.io/pypi/v/aiohealthcheck.svg
    :target: https://img.shields.io/pypi/v/aiohealthcheck.svg

.. image:: https://img.shields.io/badge/calver-YYYY.MM.MINOR-22bfda.svg
    :target: http://calver.org/


aiohealthcheck
======================

This tiny module provides a simple TCP endpoint, suitable for a healthcheck
in your microservice application. All it provides is a simple TCP endpoint
on a port to allow a container orchestration service to connect to, to
verify that the application is up.

Demo
----

Pretty much just start up a long-lived task with the provided
``tcp_health_endpoint()`` coroutine function:

.. code-block:: python

    loop.create_task(aiohealthcheck.tcp_health_endpoint(port=5000))

The internal TCP server will be shut down when the task is cancelled, e.g.,
during your app's shutdown sequence.

Kubernetes Example Configuration
--------------------------------

.. code-block::

	ports:
	- name: liveness-port
	  containerPort: 5000
	livenessProbe:
	  tcpSocket:
	    port: liveness-port
	  initialDelaySeconds: 15
	  periodSeconds: 20

