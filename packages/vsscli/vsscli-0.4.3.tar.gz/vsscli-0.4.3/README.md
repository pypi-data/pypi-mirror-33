# ITS Private Cloud Command Line Interface

[![CI][build-img]](https://gitlab-ee.eis.utoronto.ca/vss/vsscli/commits/master)
[![Coverage][coverage-img]](https://gitlab-ee.eis.utoronto.ca/vss/vsscli/commits/master)
[![PyPI][pypi-img]](https://pypi.python.org/pypi/vsscli)
[![PyPI version][pyver-img]](https://pypi.python.org/pypi/vsscli)
[![Docker Image Pulls][docker-pulls-img]][docker-image]
[![Docker Image Layers][docker-layer-img]][docker-image]
[![Docker Image Version][docker-version-img]][docker-image]

This package provides a unified command line interface to the ITS Private Cloud.

## Documentation

Package documentation is now available at [docs][docs].

## Installation

> Windows users, download and install [Python Releases for Windows][Python Releases for Windows] prior running [pip][pip].

The fastest way to install VSS CLI is to use [pip][pip]:

```bash
pip install vsscli
```

If you have the VSS CLI installed and want to upgrade to the latest version
you can run:

```bash
pip install --upgrade vsscli
```

This will install VSS CLI as well as all dependencies. You can also just [download the tarball][download the tarball].
Once you have the `vsscli` directory structure on your workstation, you can just run:

```bash
cd <path_to_vsscli>
python setup.py install
```


## CLI Releases

The release notes for the VSS CLI can be found [CHANGELOG](CHANGELOG.md) in the gitlab repo.

## Getting Started

Before using VSS CLI, you need setup your VSS credentials. You can do this in a couple of ways:

* Environment variables
* Configuration file

The quickest way to get started is to run the ``vss configure`` command:

```bash
vss configure
Username []:
Endpoint [https://vss-api.eis.utoronto.ca]:
Passw
Repeat for confirmation:
```

To use environment variables, set ``VSS_API_USER`` and ``VSS_API_USER_PASS`` or ``VSS_API_TOKEN``:

```bash
export VSS_API_USER=<vss_user>
export VSS_API_USER_PASS=<vss_user_pass>
# or
export VSS_API_TOKEN=<vss_api_token>
```

To use a config file, create a configuration as follows:

```javascript
{
"https://vss-api.eis.utoronto.ca": {
    "auth": "<encoded_creds>",
    "token": "<access_token"
    }
}
```

Place it in ``~/.vss/config.json`` (or in ``%UserProfile%\.vss\config.json`` on Windows).
If you place the config file in a different location than ``~/.vss/config.json``
you need to inform VSS CLI the full path. Do this by setting
the appropriate environment variable:

```bash
export VSS_CONFIG_FILE=/path/to/config_file.json
```

Or use the ``-c/--config`` option in the ``vss`` command as follows:

```bash
vss -c ~/.secret/vss-config.json
```

By default VSS CLI output is text, and this can be configured either by ``-o/--output``
option or the ``VSS_DEFAULT_OUTPUT`` environment variable as follows:

```bash
$ export VSS_DEFAULT_OUTPUT=json
# or
$ export VSS_DEFAULT_OUTPUT=text
```

## JSON Parameter Input

VSS CLI options vary from simple string, boolean or numeric values to
JSON data structures as input parameters on the command line.

For example, consider the following command to deploy a new virtual
machine from a given template and provide a guest operating system
specification to reconfigure hostname, domain, dns, ip, subnet
and gateway:

```bash
vss compute vm mk from-template --source $TEMPLATE_UUID \
      --description 'New virtual machine' \
      --custom-spec '{"hostname": "fe1", "domain": "eis.utoronto.ca", "interfaces": [{"dhcp": true}]}'
```

Where ``$TEMPLATE_UUID`` is an environment variable storing the UUID of
the source template.


## Bash completion

Bash completion support is provided by [Click][Click] and will complete
sub commands and parameters. Subcommands are always listed whereas parameters
only if at least a dash has been provided. Example:

```bash
vss compute <TAB><TAB>
account    compute    configure  request    stor       token

vss -<TAB><TAB>
--config      --no-verbose  --output      --verbose     --version     -c            -o
```

Activating Bash completion can be done by executing the following command:

```bash
eval "$(_VSS_COMPLETE=source vss)"
```

The above activation example will always invoke your application on startup
and may slow down the shell activation. VSS-CLI ships with a Bash completion
activation script named ``vss_bash_completer`` which can be either loaded manually
or added to your ``basrc``:

```bash
. $(dirname `which vss`)/vss_bash_completer
```    

## VSS Shell


The VSS CLI provides a REPL interactive shell with tab-completion, suggestions and
command history.

```bash
Usage: vss shell [OPTIONS]

  REPL interactive shell.

Options:
  -i, --history TEXT  File path to save history
  --help              Show this message and exit.

```

To enter the shell just execute ``vss shell`` and you will get the following welcome message:
 
<a href="https://asciinema.org/a/9TTqzGUvakj2vZ2ZfaDt2RTKa"><img src="https://asciinema.org/a/9TTqzGUvakj2vZ2ZfaDt2RTKa.png" width="450"/></a>

## Getting Help

We use GitLab issues for tracking bugs, enhancements and feature requests.
If it turns out that you may have found a bug, please [open a new issue][open a new issue].

## Versioning

The API versions are tagged based on [Semantic Versioning](https://semver.org/). Versions available in the 
[tags section](https://gitlab-ee.eis.utoronto.ca/vss/vsscli/tags).

## Contributing

Refer to the [Contributing Guide](CONTRIBUTING.md) for details on our code of conduct and the process of 
submitting code to the repository.


[docs]: https://eis.utoronto.ca/~vss/vsscli/
[download the tarball]: https://pypi.python.org/pypi/vsscli
[Click]: http://click.pocoo.org/6/
[Python Releases for Windows]: https://www.python.org/downloads/windows/
[pip]: http://www.pip-installer.org/en/latest/
[open a new issue]: https://gitlab-ee.eis.utoronto.ca/vss/vsscli/issues/new>
[build-img]: https://gitlab-ee.eis.utoronto.ca/vss/vsscli/badges/master/build.svg
[coverage-img]: https://gitlab-ee.eis.utoronto.ca/vss/vsscli/badges/master/coverage.svg
[pypi-img]: https://img.shields.io/pypi/v/vsscli.svg
[pyver-img]: https://img.shields.io/pypi/pyversions/vsscli.svg
[docker-pulls-img]:  https://img.shields.io/docker/pulls/uofteis/vsscli.svg
[docker-layer-img]: https://images.microbadger.com/badges/image/uofteis/vsscli.svg
[docker-version-img]: https://images.microbadger.com/badges/version/uofteis/vsscli.svg
[docker-image]: https://hub.docker.com/r/uofteis/vsscli/
