Automaton Tools module
======================

The automaton tools module provide an abstraction of the selenium web driver through a "BrowserServer" object.

System requirements
===================

This module has been developed with Python 3.7 and uses selenium version 3.14.

BronwserServer object
=====================

The BrowserServer object uses the selenium webdrivers executables in order to communicate with a browser.

Currently the module is wrapped with

-   ChromeDriver2.43 for chrome version 69-71
-   geckodriver-v0.23.0 for firefox 32 and 64 bits
-   MicrosoftWebDriver release 17134 for edge 17.17134
-   IEDriverServer version 3.14.0 for Internet Explorer

The mapping is as following:

{  
"chrome": { "32": "chrome/chromedriver.exe"}, "firefox":{ "32": "firefox/32/geckodriver.exe", "64": "firefox/64/geckodriver.exe"}, "ie":{ "32":"ie/32/IEDriverServer.exe", "64":"ie/64/IEDriverServer.exe"}, "edge":{ "32":"edge/MicrosoftWebDriver.exe"}}

Mapping update
--------------

You can update the mapping setting by using "update\_webdriver\_mapping(new\_mapping)" method.

The mapping indicate where the webdriver executable could be found.

{\<browser\>:{\<version\>:\<full path location\>,...}}

**Please mind** the browser list is "ie", "firefox","chrome", "edge" and "safari" in lower case, and the versions are "32" or "64" only.

Choosing a webdriver
--------------------

Before using the BrowserServer, you must select a webdriver defined in the mapping by using  
"set\_browser\_type(name, version)" or "set\_browser\_type(browser\_type)" where browser\_type is {"name":\<browser name\>, "version":\<version\>} dictionary.

Serve the webdriver
-------------------

When everything is set you can call "serve()" method which open the browser of the specified type.

You can stop the webdriver by invoking the "close()" method.

Interacting with the browser
============================

The main feature is unifying the way you choose to interact with the browser.

An element is described by a dictionary in which we give a type and a value.

The **type** is one of the following:

-   id: the element identifier,
-   name: the element name,
-   class\_name: the element class name,
-   css: the element css path,
-   link\_text: the link full text,
-   partial\_link\_text: the link partial text,
-   tag\_name: the element tag name
-   xpath: the element xpath

The **value** contains the actual value for the **type**. For example an element with the "id" type must have  
the id's value to be correctly defined. In the same way an element with the "tag\_name" type and a value "div" may return all div on the web page.

To avoid, as much as possible, this multi-definition you can add a **text** dictionary entry which try to locate the element with this exact text. **You may find an element with an empty text so use it with care.**

Although the BrowserServer class is a must have, you can use the module spaces separately. I will quickly present here only the BrowserServer class method but the module spaces functions only add a "driver" attribute which hold the selemium web driver to use.

finders
-------

This module space is about finding and returning web element.

-   find\_element(field): return the first element which match the criteria
-   find\_elements(field): return all elements which match the criteria in a list
-   find\_from\_elements(field,text): return the first element which match the criteria and has the text.

information
-----------

This module space is about retrieving data from the web page or the browser.

-   is\_field\_exist(field,until): return the first element which match the criteria within "until" second. Return None otherwise.
-   is\_field\_contains\_text(field,text): return true if the field contains the text even in the value, false otherwise.
-   is\_alert\_present(until): return true if an alert is present within "until" second.
-   element\_text(field): return the field text.
-   how\_many\_windows(): return the number of opened windows.
-   is\_field\_displayed(field): return true if the field is displayed.
-   is\_field\_enabled(field): return true if the field is enabled.

navigators
----------

This module space is about browsing tag and web browsing.

-   go\_to\_url(url): return 0 if successful and go to the specified url.
-   enter\_frame(field): return 0 if successful and enter the page frame/iframe.
-   go\_to\_window(handle,title): return 0 if successful and gain focus on the window defined by its handle ot its title.

alerts
------

This module space is about the alert popups.

- intercept\_alert(messages, accept, value): return 0 if successful. You can specify a list of message which one must be displayed on the alert, accept or reject the alert (Ok or dimiss) and enter a value where the alert prompt for a user input. - alert\_message(): return the alert message if an alert is displayed.

actions
-------

This module space is about filling, selecting and clicking on web element.

-   fill\_element(field,value): return 0 if successful, fill the field with the value

- fill\_elements(fields, data): return 0 if successful, fill each field in the fields dictionary with the value hold in the data dictionary. You can have a larger fields dictionary than the data but each data entry must be found in the fields dictionary. - select\_in\_dropdown(field,visible\_text,value): return 0 if successful, select in the field dropdown the element either described by its visible text or its hidden value. - click\_element(field): return 0 if successful, perform a left click on the field. - set\_checked(field,is\_checked): return 0 if successful, set the check box field so that the is\_checked value is always true i.e. checked if is\_checked set to true and not checked if is\_checked set to false.

Other documentation
===================

Please find in the test folder doctest files which describe almost all methods here.

Moreover don't hesitate to use the python help(method/class) directly from the python console in order to access the docstring.

To Do
=====

-   Add a multi-selection for dropdown
-   Add a drag & drop functionality
-   Add a get handles functionality

Release Notes
=============

-   version 0.1: first release

