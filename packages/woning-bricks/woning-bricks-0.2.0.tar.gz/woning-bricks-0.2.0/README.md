# Bricks - putting all the pieces together

This is a tool for having an easier and more consistent development workflow.

## Installation

```
    pip install git+https://gitlab.com/woning-group/libs/bricks.git
```

## Configuration

Each project must have a ``bricks.yml``. If you plan to use docker-compose,
you must also have a ``docker-compose.yml`` where the service has the same
name as the project.

Example ``bricks.yml`` structure

```
metadata:
  name: test
  version: 0.0.1
  description: Testing this
  tags:
  - hello
  - world

plugins:
  - name: pythonlib-kit
    params:
      hello: there
      setup_py: yes

commands:
  - name: say_hello
    driver: local
    commands:
    - echo "hello there $message"
```

## Commands

To list project details:

```
bricks help
```

To run certain commands, run

```
bricks run command_name [-p param1=value1][-p param2=value2][...]
```

Eg.

```
bricks run test
bricks run test -p use_ansible=1
bricks run build -p root_url=https://example.com
```