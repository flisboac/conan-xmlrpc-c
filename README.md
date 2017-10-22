
# conan-xmlrpc-c

[Conan.io](https://conan.io) package for [XMLRPC-C](http://xmlrpc-c.sourceforge.net/), a lightweight RPC library based on XML and HTTP.

Currently, this package can be found in [conan-transit](https://bintray.com/conan/conan-transit).

## Usage

```shell
# If needed, Substitute the version (1.39.12) by the version of the
# library you want to depend on
$ conan install xmlrpc-c/1.39.12@flisboac/testing
```

The rest is usual Conan business. [Check out the documentation](http://conanio.readthedocs.io/en/latest/getting_started.html) for more details on how to get started with Conan.

### Available options

- `shared`: `True` or `False`, to specify whether to use the static or shared version of the library. If `True`, t's advised to ensure other packages are also `shared=True`

