==========
txdocumint
==========

Twisted Python client for `clj-documint <https://github.com/fusionapp/clj-documint>`.


Usage
-----

.. code-block:: python

   from StringIO import StringIO
   # inlineCallbacks affords the opportunity to be concise.
   from twisted.internet.defer import inlineCallbacks, returnValue
   from txdocumint import actions, create_session

   @inlineCallbacks
   def render_some_html(html_string):
       session = yield create_session(DOCUMINT_ENDPOINT_URI)
       html_uri = yield session.store_content(StringIO(html_string), 'text/plain')
       pdf_uri = yield session.perform_action(actions.render_html(html_uri))
       returnValue(pdf_uri)


Contribute
----------

See <https://github.com/fusionapp/txdocumint> for details.


