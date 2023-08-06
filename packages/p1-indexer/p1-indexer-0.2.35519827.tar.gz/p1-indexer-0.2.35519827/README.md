# Installation #
Install base indexer using pip:
`pip install --upgrade p1-indexer`

# API Documentation #

## Settings ##
you must set `APP_ID` and `API_KEY` in your `settings.py` project file. Don't forget setting your `django_rq` too for using `async` option.
```
#!python
# settings.py

import os

'''
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
   Algolia
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
'''
ALGOLIA = {
    'APPLICATION_ID': '<APP_ID>',
    'API_KEY': '<API_KEY>'
}

'''
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
   RQ
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
'''
RQ_QUEUES = {
    'default': {
        'URL': os.getenv('REDISCLOUD_URL', 'redis://localhost:6379'), # If you're on Heroku
        'DEFAULT_TIMEOUT': 3600,
    },
    # 'high': {
    #     'URL': os.getenv('REDIS_URL', 'redis://localhost:6379/'), # If you're on Heroku
    #     'DEFAULT_TIMEOUT': 500,
    #     # 'EXCEPTION_HANDLERS': ['path.to.my.handler'], # If you need custom exception handlers
    # },
    # 'low': {
    #     'URL': os.getenv('REDIS_URL', 'redis://localhost:6379/'), # If you're on Heroku
    #     'DEFAULT_TIMEOUT': 500,
    # }
}
RQ_SHOW_ADMIN_LINK = True

```



## Example Usage ##
`BaseIndexer` is an abstract class, you must inherit `BaseIndexer` and set the required attributes, such as `serializer_class`, `index_name`, and `model`
```
#!python

from indexer.base_indexer import BaseIndexer
from django.conf import settings
from galactus.apps.product.serializers import ProductOptionSerializer
from galactus.apps.product.models import Product

INDEX_NAME = 'master_product_options' if settings.IS_RUN_IN_PROD_ENV else 'staging_product_options'

class ProductOptionIndexer(BaseIndexer):
    serializer_class = ProductOptionSerializer
    index_name = INDEX_NAME
    model = Product

    def get_index_setting_dict(self):
        return {
            "attributesToRetrieve": [
                "options",
                "addOns",
            ],
            "attributesToHighlight": [],
        }

    def get_property_for_objectID(self): #default is id
        return 'upc'
```

---
## Attributes ##
---
###- **serializer_class** (required)
`serializer` is part of [Rest Framework](http://www.django-rest-framework.org/api-guide/serializers/). Indexer will index the document according with the output of the serializer.

###- **index_name** (required)
`index_name` will be the index_name in your algolia apps. Don't forget to make difference index_name between **development environment** and **production_environment**. The convention is `[environment]_[plural_entity_name]` ex: `master_product_options` and `staging_product_options`

###- **model** (required)
`model` will be passed to serializer during indexing.

---
## Methods ##
---
###- **get_property_for_objectID(self)** ###
`get_property_for_objectID` return the string `attribute` of the model object. default: `id`

### -**get_index_setting_dict(self)**##
`get_index_setting_dict` return object of the settings. Read more in [setting object](https://www.algolia.com/doc/api-client/python/settings/#index-settings-parameters)
default:

```
#!python
    def get_index_setting_dict(self):
        return {
            "attributesToIndex": [],
            "attributesForFaceting": [],
            "attributesToRetrieve": [],
            "customRanking": [],
            "attributesToHighlight": [],
            "synonyms": []
        }
```
### -**reindex_one(self, objectID, wait_task=False)**##
`reindex_one` accept two parameters, 
- the first one is the `objectID` that will be passed to the `model`.
- the second one is `wait_task` that accept `Boolean` value. If `wait_task` value is `True` then the process of indexing will by **synchronize**.

### -**reindex_partial(self, list_of_objectID, batch_size=150, wait_task=False):**##
`reindex_partial` accept three parameters, 
- the first one is `list` of `objectID` that will be passed to the `model`. ex: `[1, 2, 3]`
- the second one is `batch_size` is the size of batch in process of indexing.
- the third one is `wait_task` that accept `Boolean` value. If `wait_task` value is `True` then the process of indexing will by **synchronize**.

### -**reindex_all(self, batch_size=150, async=False):**##
`reindex_all` accept two parameters, 
- the first one is `batch_size` is the size of batch in process of indexing.
- the second one is `async` that accept `Boolean` value. If `async` value is `True` then the process of will be put in `django_rq`.

### -**reindex_delete_one(self, objectID):**##
`reindex_delete_one` accept one parameter, 
- the `objectID` that registered in `index` on algolia.

### -**reindex_delete_partial(self, list_of_objectID, batch_size=150):**##
`reindex_delete_partial` accept two parameters, 
- the first one is `list` of `objectID` that registered in `index` on algolia. ex: `[1, 2, 3]`
- the second one is `batch_size` is the size of batch in process of indexing.

### -**update_settings(self):**##
`update_settings` will override the setting of index on algolia.

---
## Example ##
---

suppose we have books that wanted to be indexed.

```
#!python
# book/models.py

from django.db import models
from django.utils.translation import ugettext_lazy as _

class Book(models.Model):
    title = models.CharField(_("Book Title"), max_length=255)
    year = models.IntegerField(_("Book Year"))

    class Meta:
        app_label = 'book'

```

We make the serializers of the book model.

```
#!python
# book/serializers.py
from rest_framework import serializers
from book.model import BookModel

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookModel
        fields = ('id', 'title', 'year')

```

this is the example of the output serializer
```
book = Book(title='Lullabies', year=2014)
BookSerializer(book)
"""
output:
{
    id: 1,
    title: 'Lullabies',
    year: 2014,
}
"""
```