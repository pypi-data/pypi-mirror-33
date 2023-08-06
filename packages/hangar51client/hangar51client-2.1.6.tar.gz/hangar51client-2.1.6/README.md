# Hangar51 client

**hangar51client** is a Python client for working with the
[Hangar51](https://git.getme.co.uk/getme/hangar51) API.

## Install

Use pip to install the hangar51client:

`pip install git+ssh://git@git.getme.co.uk/getme/hangar51client.git`

## Developing

- Clone the library from git
- `cd` into the library directory
- Set up a virtual environment
- Run `pip install -e .` to install library dependencies

## Testing

If you're contributing to the hangar51client package you'll need to run tests.
We're using pytest for the project and of course you'll need to have access to
a Hangar51 instance (it's **strongly recommended** that you set up an instance
of Hangar51 on your local development environment).

You'll also need to update the value of the `api_key` and `url` in
`tests/init.py` file to match your local set up.