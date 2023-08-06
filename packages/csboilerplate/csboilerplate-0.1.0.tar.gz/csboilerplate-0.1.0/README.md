console script boilerplate
==

some boilerplate stuff for console scripts. inspired by now unmaintained `pyCLI`.

decorate your main function and register it in your `setup.py` as `console_scripts`
entry_point [1]. the function will receive an app object as argument.

you get:
- pythons `ArgumentParser`
- `KeyboardInterrupt` is catched
- `SIGTERM` is handled, so that context managers will exit properly
- logging helper

`exit_handler` and `sigterm_handler` may be customized.

[1] <https://setuptools.readthedocs.io/en/latest/setuptools.html#automatic-script-creation>


example
--

```python
from csboilerplate import cli_app


@cli_app(name=__name__)
def main(app):
    app.logging_config(log_level=app.args.debug)
    # do your stuff


main.argparser.add_argument('-d', '--debug', action='count', default=0,
                            help='lower logging threshold, may be used twice')
```


dev env
==

checkout git and:

```commandline
virtualenv .env -p python3
. .env/bin/activate
pip install -e .[dev]
```
