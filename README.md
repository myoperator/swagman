# Swagman

This tool converts your postman collection to OpenAPISpec v3 definition. You can easily
import it in your swagger UI and hence the name **Swagman**

## Installation

*NOTE* - You must have Python 3.5+ installed

To install, simply clone the repo and do a `pip install`:

```sh
git clone https://github.com/myoperator/swagman

pip install -r requirements.txt
```

## Quick Start

### Create postman examples
Create a postman collection with some examples. Make sure you **add some responses in your examples**. Swagman will use the responses from examples and that is essential to form the
response schema.

Export your postman collection/request into a json file

### Running the swagman

Now, you can simply point the swagman to your exported postman file and give it a output filename to export schema to.

```sh
python run.py postman-export.json swagger-schema.yaml
```

This will convert your `postman-export.json` file to `swagger-schema.yaml` file.

## Options

Available options are:

```sh
Usage: run.py [OPTIONS] POSTMANFILE OUTFILE

Options:
  -f, --format TEXT  Format to output. One of json or yaml. Default is yaml
  -i, --ignore TEXT  Ignore file in yaml or json
  --help             Show this message and exit.
```

## Ignoring partial API Responses

Sometimes, your api responses have some data which varies. For instance, consider this response for the api `POST /user`:

```json
{
    "result": {
        "timestamp": 1572696732,
        "username": "abc",
        "tags": {
            "tag1" : "something",
            "tag3": "somethig else"
        },
        "some-changing-key": "whatever"
    }
}
```

You do want to record the `username`, `timestamp` fields, but what about `some-changing-key` field? What about fields inside `tags`? It may appear sometimes and can vary with request parameters.

For such cases, you may not want to document them. For such purpose, **Ignore file** is used.

In ignore file, you can document the fields you want the swagman to ignore. It uses the [jsonpath-rw](https://pypi.org/project/jsonpath-rw/) library and uses its syntax (which is quite easy to learn).

Taking above example, you want to ignore following fields:

- everything inside `tags`
- `some-changing-key`

You can define them in a file `ignore.yaml` as such:

```yaml
schema:
   /user:
     post:
       200:
         - '$.result.tags.[*]' //Ignore everything inside tags field
         - '$.result.some-changing-key' //Ignore 'some-changing-field'
```

and then you can convert your postman collection to swagger definition without these fields:

```sh
python run.py -i ignore.yaml postman-export.json swagger.yaml
```

## Change swagger format

The default output conversion format is `yaml`. However, you can easily change the format to json by:

```sh
python run.py -f json postman-export.json swagger.json
```