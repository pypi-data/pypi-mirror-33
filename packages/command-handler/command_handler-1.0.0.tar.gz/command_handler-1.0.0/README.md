# Command Handler

Command Handler is a library for [Flask framework](https://github.com/pallets/flask)
which provides:
- API method for posting new commands,
- tools for easy command handlers management.

## Installation

```sh
pip install command_handler
```

## Usage

To use `command_handler` import `CommandHandler` object and call it with your `flask` application passed.

```py
from command_handler import CommandHandler
from flask import Flask

app = Flask(__name__)
ch = CommandHandler(app)
```

This will add a new endpoint to your API: `/command` which is specified in [_Command input_ section](#command-input).

Handlers can be added by `addHandler` method of the returned object as described in [_Defining handlers_ section](#defining-handlers).

### Configuration

The way `CommandHandler` is designed allows to pass config parameters to the initializer.

#### Command input endpoint URL

It is possible to prefix default `/command` route with any string accepted by Flask's routing
by defining `rulePrefix` parameter.

Following code sets URL to `/foo/bar/command`:

```py
ch = CommandHandler(app, rulePrefix="/foo/bar")
```

#### Request validators

It is possible to define command request validators.
`CommandHandler` by default sets `command` and `json` validators and it is not possible to remove them.

Validators can be defined by setting `validators` parameter which accepts list of strings.

```py
ch = CommandHandler(app, validators=["command", "json"])
```

List of possible validators can be found in [_Validators_ section](#validators)

### Command input

By default route to the command input endpoint is `/command`.
It can be configured as described in [_Configuration_ section](#command-input-endpoint-url).

Command input endpoint accepts only `POST` requests
with the content matching following [JSON schema](http://json-schema.org):

```json
{
    "type": "object",
    "properties": {
        "command": {
            "type": "string",
            "description": "Name of the sent command",
            "examples": [
                "foo",
                "foo.bar",
                "foo.bar.baz"
            ]
        },
        "payload": {
            "type": "object",
            "description": "Payload of the sent command",
        }
    },
    "required": [
        "command",
        "payload"
    ]
}
```

It is also required to send `Content-Type` header which value matches `^application/.*json$` regular expression.

Additional validators can be defined as specified in [_Validators_ section](#validators).

### Defining handlers

Command handlers can be defined by calling `addHandler` method of `CommandHandler` instance.

```py
ch = CommandHandler(app)

ch.addHandler(lambda payload, command: None, "foo.*", {})
```

The following parameters are accepted by `addHandler` method:

##### `handler`

Invokable object which is called when matching command has been posted.

`handler` function has to accept two parameters:
1. command's payload,
2. command's name.

##### `command`

String which command's name is matched against.

Command matching is described in [_Command matching_ section](#command-matching).

##### `schema`

[JSON schema](http://json-schema.org) object used to validate command's payload.

##### `transformer = lambda x: x`

`transformer` parameter can be used to transform command's payload before passing it to the handler.

It gets command's payload as only parameter and returns object passed to the handler as payload.

By default it is a function which returns parameter without any changes.

##### `postProcessor = None`

Invokable object which is called when handler processing is done.

It has to accept same parameters as [handler](#handler).

#### Raising exceptions

There is no possibility of changing response of a [command input endpoint](#command-input)
except raising an exception.

When `command_handler.request.exceptions.InvalidRequestException` is raised
[command input endpoint](#command-input) returns response with HTTP code
specified during `InvalidRequestEndpoint` creation (by default it is `400: Bad Request`)
and message which matches following [JSON schema](http://json-schema.org):

```json
{
    "type": "object",
    "properties": {
        "type": "string",
        "description": "Message passed to the `InvalidRequestException` during creation",
        "default": ""
    },
    "required": [
        "error"
    ]
}
```

It is preferred to use `4xx` codes with `InvalidRequestException`.

Following snippet will respond with `418: I'm a teapot` HTTP code and
`{"error": "I'm a teapot handler"}` when `foo.bar` command is sent:

```py
def fooHandler(payload, command):
    raise InvalidRequestException("I'm a teapot handler", code=418)

ch = CommandHandler(app)
ch.addHandler(fooHandler, "foo.bar", {})
```

When any other exception is raised [command input endpoint](#command-input)
returns response with HTTP code `500: Internal server error`.

### Command matching

Each command name sent to [command input endpoint](#command-input)
has to be a list of words delimited by dots.

Command name passed to [`addHandler`](#defining-handlers) method must also be
in the same form. There are two special words for command name assigned to the handler:
- `*` can substitute exactly one word,
- `#` can substitute zero or more words.

Command handler invoker will call handler which matches command name of handler
passed to [`addHandler`](#defining-handlers) method. If there is no matching
handler [command input endpoint](#command-input) will respond with `500: Internal server error`.

If there is more than one match the handler which was added first will be called.
However handler's registry is not allowing to add handler which is assigned to the already covered name.
It means that order of adding handler matters.

For example following snippet will work properly but adding those handlers in reverse order will cause
in raising an exception.

```py
ch.addHandler(lambda payload, command: None, "foo.bar", {})
ch.addHandler(lambda payload, command: None, "foo.#", {})
```

### Validators

Command Handler contains following predefined request validators:

##### `command`

Validator which verifies if:
- request contains `payload` and `command` fields,
- `command` field value is a string,
- `payload` field value is a dictionary,
- value of `command` field is matchable to defined handlers,
- value of `payload` field matches schema which had been assigned to the handler,

##### `json`

Validator which verifies if:
- request contains `Content-Type` header with value matching to `^application/.*json$` regex,
- request content is json-parseable.

##### `privateIp`

Validator which verifies if remote IP address of the request
is [private](https://tools.ietf.org/html/rfc1918).
