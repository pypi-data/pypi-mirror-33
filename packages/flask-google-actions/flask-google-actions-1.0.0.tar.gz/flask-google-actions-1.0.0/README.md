# Actions on Google Client Python Library

This client library makes it easy to create Actions for the Google Assistant.

This library parses AppRequest objects from Google Actions Dialogflow webhooks and is able to create AppResponse objects.

Use the following libraries for creating webhooks in dialogflow with google actions for python.

* [Flask Actions]()
* ~Django Actions~ Coming soon

[![PyPI](https://img.shields.io/pypi/v/nine.svg)](https://pypi.org/project/google-actions/1.0.0/)


## Installation

```
pip install googleactions
```

## Basic Usage

```python
from googleactions import AppRequest, AppResponse
import json

request = "{...}" # Json request payload from dialogflow
app_request = AppRequest(request)
app_response = AppResponse('Hello world!')
print(app_request.json())
print(app_response.json())
```