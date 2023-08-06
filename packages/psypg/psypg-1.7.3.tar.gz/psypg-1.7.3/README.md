# Psycopg2 Wrapper

By [Gary Chambers](https://gitlab.com/amos_moses).


## Installation

    pip install psypg

or

    python ./setup.py install

## Usage
### In Flask
```python
from psypg import PgConfig, pg_query

app = Flask(__name__)
app.config.from_object('config')
d = PgConfig(app.config['DBSCHEMA'], app.config['DBINIFILES'])

@app.before_request
def before_request():
    try:
        g.db = d.get_handle()
    except Exception as e:
        app.logger.exception(e)
        abort(503)

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/user/<int:userid>')
def index(userid):
    query = 'select * from table where id = %s'
    rows = pg_query(g.db, query, [userid], fetch_one=True)
```

## Configuration


## Information

1. I don't like ORMs
2. I don't like ad hoc queries in my application code
3. Unless it's a really simple SQL query, I obtain all data through database functions
4. So far, so good

### Known Issues

If you discover any bugs, feel free to create an issue on GitHub fork and
send us a pull request.

[Issues List](https://gitlab.com/amos_moses/psypg/issues).

## Authors

* Gary Chambers (https://gitlab.com/amos_moses)

## Contributing

1. Fork it
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create new Pull Request


## License

The MIT License (MIT)

Copyright (c) 2015-2018 Gary Chambers

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
