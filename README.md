# sonsu-marketplace

[![Validate Marketplace](https://github.com/sonsu-lee/sonsu-marketplace/actions/workflows/validate-marketplace.yml/badge.svg)](https://github.com/sonsu-lee/sonsu-marketplace/actions/workflows/validate-marketplace.yml)
[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg)](https://github.com/RichardLitt/standard-readme)

Personal plugin marketplace for omp.

This repository is a plugin catalog for
[omp](https://github.com/can1357/oh-my-pi). omp reads the catalog at
`.omp-plugin/marketplace.json` and installs plugins from the `plugins/`
directory. No plugins are published yet.

## Install

You need the omp CLI.

```sh
omp plugin marketplace add sonsu-lee/sonsu-marketplace
```

### Updating

Fetch the latest catalog:

```sh
omp plugin marketplace update sonsu-marketplace
```

## Usage

List the plugins in the catalog and install one:

```sh
omp plugin discover sonsu-marketplace
omp plugin install <plugin>@sonsu-marketplace
```

Add `--scope project` to install a plugin for the current project only. In an
omp session, `/marketplace` opens the same catalog in the plugin browser.

## Maintainers

[@sonsu-lee](https://github.com/sonsu-lee)

## Contributing

Ask questions and report problems in
[GitHub issues](https://github.com/sonsu-lee/sonsu-marketplace/issues). Pull
requests are accepted. Read [CONTRIBUTING.md](CONTRIBUTING.md) first. It covers
reporting problems, making changes, adding plugins, and the checks to run.

## License

[MIT](LICENSE) © sonsu-lee
