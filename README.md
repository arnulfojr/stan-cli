# STAN CLI tool


Finally! A proper NATS CLI Tool that does not *completly* suck!

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
$ cat data.json | docker-compose run cli request subject-name --data -
# or simply (but keep in mind the volumes mounting!)
$ docker-compose run cli request subject-name --data data.json

```

```bash
# publishing an event through stan
$ cat data.json | docker-compose run cli publish subject-name cluster-name --data -
```

# Contact

Arnulfo Solis
arnulfojr94@gmail.com
