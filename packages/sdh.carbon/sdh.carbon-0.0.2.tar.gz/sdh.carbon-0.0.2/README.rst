Tools for serving statistic data to carbon/graphite server.

To install package into django need:

* add 'ua2.carbon.middleware.MeasureMiddleware' at the top of MIDDLEWARE_CLASSES list
* into settings.py add next lines:

.. code-block:: python

	from sdh.carbon.loaders import django_loader
	django_loader()


***************
Usage examples
***************

Measure function execution time
-------------------------------

.. code-block:: python

	from sdh import carbon

	@carbon.measure('myapp')
	def test():
		print "Hello World!"


Measure arbitrary block execution time
--------------------------------------

.. code-block:: python

	from sdh import carbon

	def test():
		with carbon.Profiler('myapp'):
			for i in range(1,100):
				print "Hello World!"


Send raw value to carbon
------------------------

.. code-block:: python

	from sdh import carbon

	def test():
		for i in range(1,100):
			print "Hello World!"
			carbon.send('metric.hello.world', 1)

