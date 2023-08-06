Flea - WSGI testing
===================

Flea helps you write functional tests for WSGI applications.

Flea uses CSS selectors and XPath to give you a powerful tool to
drive and test the output of your WSGI web applications.
Here's an example of how easy it is to test a WSGI application::

	>>> from flea import Agent
	>>> r = Agent(my_wsgi_app).get('/')
	>>> print r.body
	<html>
		<body>
			<a href="/sign-in">sign in</a>
		</body>
	</html>
	>>> r = r.click('sign in')
	>>> r = r("form#login-form").fill(
	... 	username = 'root',
	... 	password = 'secret',
	... ).submit()
	>>> assert 'login successful' in r.body

