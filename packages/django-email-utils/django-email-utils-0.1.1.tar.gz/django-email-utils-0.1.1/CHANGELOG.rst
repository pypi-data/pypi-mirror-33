#########
Changelog
#########


******
v0.1.1
******

Fix automatic deployment with Travis CI.


******
v0.1.0
******

Initial release. Functionality at this point is as follows:

* If both templates can be rendered, the email is sent with both plain text and HTML content.
* If only the HTML template can be rendered, the plain text email is empty.
* If no template can be rendered, an exception is thrown.
