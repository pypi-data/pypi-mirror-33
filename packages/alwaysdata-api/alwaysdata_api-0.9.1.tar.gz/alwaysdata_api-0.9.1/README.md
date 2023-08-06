alwaysdata_api
==============

A dead simple Python interface to the [Alwaysdata][AD] [API][API]


Installation
------------

```sh
pip install alwaysdata_api
```

or

```sh
git clone https://gitlab.com/wpk-/alwaysdata-api.git
cd alwaysdata-api
python setup.py install
```


Usage
-----

If you store your API key and account name in the `ALWAYSDATA_API_KEY` and
`ALWAYSDATA_ACCOUNT` environment variables, the following example works out of
the box:

```python
from alwaysdata_api import Domain
Domain.list(name='paul')[0].name
# 'paulkoppen.com'
```

Alternatively, you can provide the authentication via code. The above example
then needs to be expanded to include the extra configuration:

```python
from alwaysdata_api import Config, Domain
config = Config(('MY_API_KEY account=MY_ACCOUNT', ''))
Domain.list(name='paul', config=config)[0].name
# 'paulkoppen.com'
```

See [demo.py][DEMO] for more examples.


Licence
-------

[MIT](LICENCE)



[AD]: //alwaysdata.com/
[API]: //api.alwaysdata.com/doc/
[DEMO]: demo.py
