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

You do want to record the `username`, `timestamp` fields, but what about `some-changing-key` field? What about fields inside `tags`? You want to keep the `tags` key as it will always be included in response, but do not want to keep `some-changing-key` as it may or maynot appear in responses.

**Something you may want the values of a key to ignore, while something you want the key value pair to be ignored alltogether**

For such cases, you may not want to document them. For such purpose, **Ignore file** is used.

In ignore file, you can document the fields you want the swagman to ignore. It uses the [jsonpath-rw](https://pypi.org/project/jsonpath-rw/) library and uses its syntax (which is quite easy to learn).

**To ignore only values but keep the keys**, simple use the `jsonpath-rw` syntax that points to the key. For ex- `$.result.tags.[*]` will find everything inside `tags` field in `result` object.

**To ignore both key and values**, simply use the above method, i.e. write your `jsonpath-rw` regex that matches the path, and *append* `:a` to it. For example, if you want to delete everything inside tag *including* tag field itself, you can do so by: `$.result.tags.[*]:a`


Taking above example, you want to ignore following fields:

- everything inside `tags` (ignore value but NOT the key `tags`)
- `some-changing-key` field (ignore both key and value)

You can define them in a file `ignore.yaml` as such:

```yaml
schema:
   /user:
     post:
       200:
         - '$.result.tags.[*]' //Ignore everything inside tags field
         - '$.result.some-changing-key:a' //Ignore 'some-changing-field'. Note the leading :a 
```

and then you can convert your postman collection to swagger definition without these fields:

```sh
python run.py -i ignore.yaml postman-export.json swagger.yaml
```

PS: Leading `:a` in jsonpath-rw syntax with ignore both the key and values, otherwise only values are ignored.

## Change swagger format

The default output conversion format is `yaml`. However, you can easily change the format to json by:

```sh
python run.py -f json postman-export.json swagger.json
```