# Program Google Assistant Apps with Python & Flask

This client library makes it easy to create Actions for the Google Assistant.

This library uses the [google-actions-on-python](https://github.com/caycewilliams/actions-on-google-python/) and [flask](https://github.com/pallets/flask) to make building applications for google assistant fast and easy.

[![PyPI](https://img.shields.io/pypi/v/nine.svg)](https://pypi.org/project/flask-google-actions/1.0.1/)


## Installation

```
pip install flask-google-actions
```

## Basic Usage

```python
from googleactions import Intent
from flaskactions import api

@api.intent(Intent.MAIN)
def hook_main(app_request):
    return 'Hello world!'
    
if __name__ == "__main__":
    api.start(username='username', password='password')
```