# Dashbase Tools [![CircleCI](https://circleci.com/gh/dashbase/dashbase-tools.svg?style=svg)](https://circleci.com/gh/dashbase/dashbase-tools)

**To see the full documentation, please view *[dashbase-tools wiki](https://github.com/dashbase/dashbase-tools/wiki)*.**

## Introduction

`dashbase-tools` contains three components: `dash`, `dtail` and `dashbase_mnt`. These tools are used to access dashbase data in terminal.

`dashbase-tools` is written in `python 2.7.14`, and is now not competiable with `python 3.x`.

## Install

### Using docker

We also support docker to run our tools.

**Note: Because `dashbase_mnt` depends on `fuse`, so need `--privileged` to run!**

If you don't want to use `dashbase_mnt`:

```shell
docker run -it dashbase/dashbase-tools:latest bash
```

If you want to use `dashbase_mnt`:

```shell
docker run -it --privileged dashbase/dashbase-tools:latest bash
```

#### What does tags on docker hub mean

There are three kinds of tags on docker hub:

1. `latest`: image which contains the latest released version. Automatically built every time `master` is updated.
2. `dev`: image which contains the latest develop version. Automatically built every time `develop` is updated.
3. Version tags like `1.0.0rc1`: image which contains the specified version. Automatically built every time a new release branch is pushed.

### For development

For contributors or developers, please view **[Contributor's Guide](https://github.com/dashbase/dashbase-tools/wiki/Contributor's-Guide)**.

## dash

SQL command console for querying a dashbase service.

This tool is a terminal version of dashbase-web.

You can use this tool to execute sql query or get table schema and infomation.

Sample:

[![asciicast](https://asciinema.org/a/ps1NjUJIyCYqpAedvUDX0HCnA.png)](https://asciinema.org/a/ps1NjUJIyCYqpAedvUDX0HCnA)

For more detailed usage, please view **[How to use dash](https://github.com/dashbase/dashbase-tools/wiki/How-to-use-dash)**.

## dtail

This tool is used to get the latest dashbase data from terminal.

It's function is like `tail -f your_dashbase_log`.

Mimics a unix `tail` + `grep` combination and queries a dashbase service endpoint for aggregated logs.

Sample:

[![asciicast](https://asciinema.org/a/pWMZ96F5yeKv8syRskaZRpEoi.png)](https://asciinema.org/a/pWMZ96F5yeKv8syRskaZRpEoi)

For more detailed usage, please view **[How to use dtail](https://github.com/dashbase/dashbase-tools/wiki/How-to-use-dtail)**.

## dashbase_mnt

Fuse implementation for Dashbase.

Sample:

[![asciicast](https://asciinema.org/a/3MVv89jhiTA62lLHzNeyjsfNL.png)](https://asciinema.org/a/3MVv89jhiTA62lLHzNeyjsfNL)

For more detailed usage, please view **[How to use dashbase_mnt](https://github.com/dashbase/dashbase-tools/wiki/How-to-use-dashbase_mnt)**.