
# conan-xmlrpc-c

[Conan.io](https://conan.io) package for [XMLRPC-C](http://xmlrpc-c.sourceforge.net/), a lightweight RPC library based on XML and HTTP.

Currently, this package can be found in [flisboac's Conan repository at Bintray](https://bintray.com/flisboac/conan).

## Usage

First, add a new remote repository. Open a terminal and type:

```shell
# Substitute <REMOTE> by whatever name you want to give to the new remote
$ conan remote add <REMOTE> https://api.bintray.com/conan/flisboac/conan 
```

After that, add the dependency to your project. A sample `conanfile.txt`:

```ini
[requires]
# If needed, Substitute the version (1.39.12) by the version of the
# library you want to depend on
xmlrpc-c/1.39.12@flisboac/testing

[generators]
cmake
```

And then:

```shell
$ conan install
```

[Check out the documentation](http://conanio.readthedocs.io/en/latest/getting_started.html) for more details on how to get started with Conan.

### Available options

- `shared`: `True` or `False`, to specify whether to use the static or shared version of the library. If `True`, t's advised to ensure other packages are also `shared=True`

