# Url generator

UrlGenerator is a simple library that allows you to generate URLs from a single JSON configuration for different programming languages. 

## Other programming languages
+There is also [UrlGenerator for PHP](https://github.com/heureka/php-url-generator), which accepts the same configuration,
+so you can combine multiple projects in Python and PHP using same configuration file.

#### Basic usage:
Main entrypoint to this library is function `url_generator.get_url` which accepts the following parameters:

###### pathString
*Path string* defines path through route configuration using dot notation (see the #configuration section bellow).

example: `heureka.category.index`

##### parameter kwargs
*Params* is dictionary of route parameters. Params dict should contain mixed `GET` parameters and template parameters as defined in configuration.

example: `lang="sk", productId=12345`

#### Example call: 
```python
from url_generator import UrlGenerator

ug = UrlGenerator('path/to/your/config.json', env="dev", lang="sk")
ug.get_url("heureka.category.index", productId=12345)
```

## Configuration
Path to configuration file must be passed trough the constructor to the UrlGenerator instance (as a first parameter).
Check `tests/test.json` for better understanding.

Structure is plain Json (planning support for comments in future).

Simple configuration file can look like this:
```
{
    "some_example_site": {
        "@scheme": "https",
        "@host": "example.com",
        "@path": "/{category_id}/search",
        "@params": {
            "query": "q"
        }  
    }
}
```

### Keywords
Keys in configuration that are prefixed by `@` symbol are considered as *keyword*.
Each route is defined by keyword. Note that `@scheme` and `@host` *keywords* are mandatory.

*Keywords* are prefixed by `@` symbol to distinguish them from *path nodes*.

#### `@scheme`
This represents URL scheme by [RFC1738](https://tools.ietf.org/html/rfc1738), usually `http` or `https`

example: `"@scheme": "https"`

#### `@host`
This represents host (and can contain port if necessary)

example: `"@host": "www.heureka.cz"`

#### `@path`
This represents URL path by [RFC1738](https://tools.ietf.org/html/rfc1738) like `/` for index or `/iphone-7/recenze` for product detail

example: `"@path": "/obchody/czc-cz/recenze"`

#### `@query`
This represents list of allowed query parameters with their internal and external representation.

For example if configuration contains `"@query": {"index": "i"}` then `index` parameter in 
call `ug.get_url('example_site', index=10)` will be compiled according to configuration into `i=10`
and returned url should looks like `https://www.example.com/?i=10`.

Note that **query parameters are not mandatory**, and cannot be set as mandatory.

#### `@fragment`
This represents fragment (anchor identifier) by [RFC1738](https://tools.ietf.org/html/rfc1738) like `#section`
example: `"@fragment": "section"`

### Path nodes
Every key in configuration, which is **not prefixed by `@` or `{`** symbol, is considered as *path node*.

Path nodes **should use** `underscore_case` naming convention.

*Path string* is dot joined *Path nodes* like `heureka.category.index`.

For example, in following configuration `some_site` or `index` are path nodes.
On the other hand `@host` and `@path` are keywords.
```
{
    "@scheme": "https",
    "some_site": {
        "index": {
            "@host": "example.com",
            "@path": "/index.php"
        }
    }
}
```

With the precending configuration we can call `get_url('some_site.index')` and generated url will be `https://example.com/index.php`. 

### Inheritance
Using *path string* we define which URL we want to receive.
The *URL Generator* parses the config file and gets *keywords* from given *path node* and all its parents.

At the example bellow, we can call `get_url('example.russian')` and the response will be `https://www.example.ru/information`.

Note that *URL Generator* uses the `@host` *keyword* in `example.russian` *path node*, but `@path` *keyword* is from `example`. At least `@scheme` *keyword* is defined in global space (root path).
```
{
    "@scheme": "https",
    "example": {
        "@host": "www.example.com",
        "@path": "/information"
 
        "russian": {
            "@host": "www.example.ru"
        }
    }
}
```

At this example you can also see *keywords* overloading, as the `host` *keyword* is defined in `example` *path node* and it is overloaded in `example.russian` *path node*.

This way we can build complex structures like `heureka.product.detail.reviews.only_certified` without too many repating definitions in the configuration.

### Template parameters
In the configuration we can define *template parameters* using `{parameter}` syntax.
Those parameters will be expected in `get_url(path, params)` function call (in params array).

Template parameters can be also defined globally as first parameter of *URL Generator* constructor and those will be shared for all `get_url` function calls.

It is **not recommended** to use template parameters in values for `@scheme` and `@query` *keywords*.

At the example bellow we define top level domain using `language` parameter.
So we can call `get_url(path, language='cz', page=1])` and the result will be `https://www.example.cz?p=1`.
```
{
    "@scheme": "https",
    "example": {
        "@host": "www.example.{language}",
        "@params": { "page": "p" }
    }
}
```

Note that *query parametes* and *template parameters* are mixed in `get_url(.., **kwargs)` second parameter together.

### Template conditions
We can define *template conditions* in configuration to separate configuration for given parameter value.

This way we can define configuration only for given language/environment/etc..

*Template conditions* uses `{parameter}=expected_value` syntax and can contain same rules as *path nodes*.

Rules defined inside template condition are processed only if given parameter equals expected value.

At the example bellow we define `{lang}=spanish` condition, so if we call `get_url("example", lang="spanish")` it returns `https://www.ejemplar.es`.  

```
{
    "@scheme": "https",
    "example": {
        "@host": "www.example.cz",
       
        "{lang}=spanish": {
            "@host": "www.ejemplar.es"
        }
    }
}
```

Note that rules are processed from top to bottom in file. Latter rule has priority so *template condition* must be
placed after overloaded values to have effect.

## Contributing rules
The main advantage of the URLGenerator is that it can share the configuration through multiple programming languages.
Therefore, it is necessary to keep the individual language versions compatible with each other.

So, when you create a pull-request into this repository, please concider contributing the same functionality to the other repositories listed in [Other programming languages](#other-programming-languages) section. 

Project owners should never merge code which breaks compatibility with other language versions.

## Author
The author of the first idea is [Pavel Škoda](https://github.com/skooda). 

## So ...
Happy URLing ;)
