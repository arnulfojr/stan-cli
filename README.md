# STAN CLI tool


Finally! A proper NATS CLI Tool that does not *completly* suck!

Uses Click to expose a good and standarized CLI interface and uses Pygments to colorize JSON content!

> This repository is still in alpha version

## Requirements

* Python >= 3.7

## Docker set up

Included in stan-cli there's a Dockerfile and a docker-compose file that specifies everything that is needed to run the cli.
This can be adjusted to your needs.

## Commands

* request
* publish
* subscribe

```bash
# requesting something through nats
$ cat data.json | docker-compose run cli request subject-name -
# or simply (but keep in mind the volumes mounting!)
$ docker-compose run cli request subject-name data.json
# if you prefer docker cli
$ cat data.json | docker run --interactive --rm --env-file $PWD/local.env stan-cli:latest request subject -
```

Piping is as easy as:

```bash
$ cat data.json | docker-compose run cli request --raw subject-name - | jq -s .
# if you expect JSON then simply ignore the raw
$ cat data.json | docker-compose run cli request subject-name -
# or
$ cat data.json | docker run --interactive --rm --env-file $PWD/local.env stan-cli:latest request subject - | jq .
```

```bash
# publishing an event through stan
$ cat data.json | docker-compose run cli publish --cluster myCluster subject-name -
```


To get the content of a channel the stancli supports

```bash
$ docker run --rm --env-file $PWD/local.env stan-cli:latest subscribe subject
# if you expect JSON content, the lucky you (for ANSI add the --tty flag to docker run)
$ docker run --rm -t --env-file $PWD/local.env stan-cli:latest subscribe subject --pretty-json
```

# Contact

Arnulfo Solis
arnulfojr94@gmail.com
