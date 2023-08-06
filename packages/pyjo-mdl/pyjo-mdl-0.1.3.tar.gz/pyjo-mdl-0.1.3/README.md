# pyjo-mdl
Model definition language for Pyjo


This package will allow you to dynamically create pyjo models with a
domain specific language created ad-hoc.

# Model definition language

We can define the structure of the model with a json format.
 Heres a basic example:

```
{
  "url": {
    "type": "url",
    "required": false
  },
  "name": {
    "type": "string"
  },
  "rounds": {
    "type": "array",
    "element": {
      "type": "embedded",
      "model": {
        "foo": {
          "type": "string"
        },
        "bar": {
          "type": "integer",
          "min_value": 100
        }
      }
    }
  }
}
```

This allows to define models as a set of properties with some type
 and validation.

As you can see, there are many possible properties in this DSL.
 We want to keep it as simple as possible to start with,
  so heres a very basic list of stuff that we plan to add
   from the beginning.
    More stuff will come in the future as needs arise.

# Available properties and options

### Some generally available options:
- `required`: true if the property must be always filled when providing content. Defaults to true
- `type`: type of the property, see below for a proposal of the initial set of properties available


### string
Basic string field, may contain any set of UTF-8 characters.
Extra options:

- `validation`: a regular expression the string must satisfy
- `min_length`: Min number of chars in the string, defaults to 0
- `max_length`: Max number of chars in the string, defaults to infinite!
- `values`: array of all and only possible values for this field

Example:

```
{
    "tag_version": {
        "type": "string",
        "validation": "^.*-[0-9]\.[0-9]\.[0-9]build[0-9]+$"
        "max_length": 256
    }
}
```

Example (enum):

```
{
    "meal_category": {
        "type": "string",
        "values": [
            "smoothie",
            "main dish",
            "dessert",
        ]
    }
}
```


### integer
Integer number. Extras:

- `min_value`: min value allowed
- `max_value`: max value allowed

```
{
    "calories": {
        "type": "integer",
        "min_value": 0
    }
}
```


### float
Floating point number. Extras:

- `min_value`: min value allowed
- `max_value`: max value allowed

```
{
    "price": {
        "type": "float",
        "min_value": 0,
        "max_value": 99.99
    }
}
```


### boolean
Flag, true or false. Cant be easier than this.

```
{
    "hidden": {
        "type": "boolean"
    }
}
```

Booleans will automatically consider values in
 `yes, true, t, y, 1` to be truthy (ignoring case),
 values in `no, false, f, n, 0` to be falsy. Other string values will
 raise an exception.

### url:
URLs are validated with the following regex:
`http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+`

```
{
    "cover_image": {
        "type": "url"
    }
}
```

### embedded
Represents an embedded model that may have no meaning outside of the
 main model. Its useful to represent some nested data structure.
  May contain all the properties of a full model. Must contain:

- `model`: the model structure being embedded

Example

```
{
    "pet": {
        "type": "embedded",
        "model": {
            "name": {
                "type": "string",
            },
            "age": {
                "type": "integer",
                "min_value": 0
            }
        }
    }
}
```

### array
Represents a list of fields of any kind, including embedded. Extras:

- `element`: defines the kind of element in this array property. It may be of any kind, including embedded

Examples (primitive content):

```
{
    "lucky_numbers": {
        "type": "array",
        "element": {
            "type": "integer"
        }
    }
}
```

Example 2 (embedded complex models):

```
{
    "pets": {
        "type": "array",
        "element": {
            "type": "embedded",
            "model": {
                "name": {
                    "type": "string"
                },
                "age": {
                    "type": "integer",
                    "min_value": 0
                }
            }
        }
    }
}
```
