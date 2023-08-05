# Copyright (c) 2018 Ben Maddison. All rights reserved.
#
# The contents of this file are licensed under the MIT License
# (the "License"); you may not use this file except in compliance with the
# License.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
"""pynamedotcom CLI module."""

from __future__ import print_function

import click
import json
import logging
import os

from argparse import Namespace

from pynamedotcom import API


logger = logging.getLogger(__name__)


def _default_auth_path():  # pragma: no cover
    """Try and find the default auth-file, if it exists."""
    if "XDG_CONFIG_HOME" in os.environ:
        base_path = os.environ.get("XDG_CONFIG_HOME")
    elif "HOME" in os.environ:
        base_path = os.path.join(os.environ.get("HOME"), ".config")
    else:
        return None
    path = os.path.join(base_path, "pynamedotcom", "auth.json")
    if os.path.exists(path):
        return path
    return None


def _set_log_level(ctx, param, value):
    """Set logging level according to the --debug flag."""
    if value:
        log_level = logging.DEBUG
    else:
        log_level = logging.WARNING
    logging.basicConfig(level=log_level)
    return value


@click.group()
@click.pass_context
@click.option("-d", "--debug", is_flag=True,
              callback=_set_log_level, is_eager=True, expose_value=False,
              help="Enable debug logging.")
@click.option("-h", "--host", default="api.name.com",
              help="Server hostname.", show_default=True)
@click.option("-u", "--username",
              help="name.com username. Overides --auth-file.")
@click.option('-t', "--token",
              help="name.com API token. Overides --auth-file")
@click.option("-f", "--auth-file", type=click.Path(exists=True),
              default=_default_auth_path(), show_default=True,
              help="Read credentials from file.")
@click.version_option()
def main(ctx, host, auth_file, username, token):
    """CLI tool for interacting with the name.com API."""
    # Get credentials from file or CLI options
    auth = {"user": None, "token": None}
    # Try reading from file
    if auth_file:
        logger.debug("reading auth parameters from {}".format(auth_file))
        with open(auth_file) as f:
            auth = json.load(f)
    # Overide values based on -u/-t options
    if username:
        auth["user"] = username
    if token:
        auth["token"] = token
    logger.debug("connecting to {} as {}".format(host, auth["user"]))

    # Declare helper function
    def api():
        """Helper function to return configured pynamedotcom.API instance."""
        return API(host=host, **auth)

    ctx.obj = Namespace()
    # Add helper to click Context.obj to pass to command functions
    ctx.obj.api = api


@main.command()
@click.pass_context
def ping(ctx):
    """Check for successful authentication."""
    # Use provided helper to instantiate pynamedotcom.API object
    with ctx.obj.api() as api:
        try:
            # Execute method and print a success message
            api.ping()
            click.echo(click.style("OK", fg="green"))
        except Exception as e:  # pragma: no cover
            # fail cleanly
            ctx.fail(message="{}".format(e))


@main.command()
@click.pass_context
def domains(ctx):
    """Get list of domain names."""
    # Use provided helper to instantiate pynamedotcom.API object
    with ctx.obj.api() as api:
        try:
            # Execute method and print a success message
            for domain in api.domains:
                click.echo(domain)
        except Exception as e:  # pragma: no cover
            # fail cleanly
            ctx.fail(message="{}".format(e))


@main.group(invoke_without_command=True)
@click.pass_context
@click.argument("name")
def domain(ctx, name):
    """Get domain details."""
    # Record args in Context
    ctx.obj.name = name
    # Only execute if no subcommand is provided
    if ctx.invoked_subcommand is None:
        # Use provided helper to instantiate pynamedotcom.API object
        with ctx.obj.api() as api:
            try:
                # Execute method and print the domain details
                domain = api.domain(name=name)
                click.echo("{}".format(domain.name))
                click.echo("  nameservers:")
                for ns in domain.nameservers:
                    click.echo("    {}".format(ns))
                click.echo("  contacts:")
                for role, contact in domain.contacts.items():
                    click.echo("    {}: {}".format(role, contact))
                click.echo("  privacy: {}".format(domain.privacy))
                click.echo("  locked: {}".format(domain.locked))
                click.echo("  autorenew: {}".format(domain.autorenew))
                click.echo("  expiry: {}".format(domain.expiry))
                click.echo("  created: {}".format(domain.created))
                click.echo("  renewal price: ${}".format(domain.renewal_price))
            except Exception as e:  # pragma: no cover
                # fail cleanly
                ctx.fail(message="{}".format(e))


@domain.command()
@click.pass_context
def name(ctx):
    """Get domain name."""
    # Use provided helper to instantiate pynamedotcom.API object
    with ctx.obj.api() as api:
        try:
            # Execute method and print the domain details
            domain = api.domain(name=ctx.obj.name)
            click.echo("{}".format(domain.name))
        except Exception as e:  # pragma: no cover
            # fail cleanly
            ctx.fail(message="{}".format(e))


@domain.command()
@click.pass_context
@click.argument("nameservers", nargs=-1, required=False)
def nameservers(ctx, nameservers):
    """Get or set domain nameservers."""
    # Coerce nameservers argument to list type
    nameservers = list(nameservers)
    # Use provided helper to instantiate pynamedotcom.API object
    with ctx.obj.api() as api:
        try:
            # Execute method and print the domain details
            domain = api.domain(name=ctx.obj.name)
            if nameservers:
                domain.nameservers = nameservers
                click.echo(click.style("OK", fg="green"))
            else:
                for nameserver in domain.nameservers:
                    click.echo("{}".format(nameserver))
        except Exception as e:  # pragma: no cover
            # fail cleanly
            ctx.fail(message="{}".format(e))


@domain.command()
@click.pass_context
def contacts(ctx):
    """Get domain contacts."""
    # Use provided helper to instantiate pynamedotcom.API object
    with ctx.obj.api() as api:
        try:
            # Execute method and print the domain details
            domain = api.domain(name=ctx.obj.name)
            for role, contact in domain.contacts.items():
                click.echo("{}: {}".format(role, contact))
        except Exception as e:  # pragma: no cover
            # fail cleanly
            ctx.fail(message="{}".format(e))


@domain.command()
@click.pass_context
def privacy(ctx):
    """Get domain privacy status."""
    # Use provided helper to instantiate pynamedotcom.API object
    with ctx.obj.api() as api:
        try:
            # Execute method and print the domain details
            domain = api.domain(name=ctx.obj.name)
            click.echo("{}".format(domain.privacy))
        except Exception as e:  # pragma: no cover
            # fail cleanly
            ctx.fail(message="{}".format(e))


@domain.command()
@click.pass_context
@click.argument("state", type=bool, required=False)
def locked(ctx, state):
    """Get or set domain lock status."""
    # Use provided helper to instantiate pynamedotcom.API object
    with ctx.obj.api() as api:
        try:
            # Execute method and print the domain details
            domain = api.domain(name=ctx.obj.name)
            if state is not None:
                domain.locked = state
                click.echo(click.style("OK", fg="green"))
            else:
                click.echo("{}".format(domain.locked))
        except Exception as e:  # pragma: no cover
            # fail cleanly
            ctx.fail(message="{}".format(e))


@domain.command()
@click.pass_context
@click.argument("state", type=bool, required=False)
def autorenew(ctx, state):
    """Get or set domain autorenew status."""
    # Use provided helper to instantiate pynamedotcom.API object
    with ctx.obj.api() as api:
        try:
            # Execute method and print the domain details
            domain = api.domain(name=ctx.obj.name)
            if state is not None:
                domain.autorenew = state
                click.echo(click.style("OK", fg="green"))
            else:
                click.echo("{}".format(domain.autorenew))
        except Exception as e:  # pragma: no cover
            # fail cleanly
            ctx.fail(message="{}".format(e))


@domain.command()
@click.pass_context
def expiry(ctx):
    """Get domain expiry date/time."""
    # Use provided helper to instantiate pynamedotcom.API object
    with ctx.obj.api() as api:
        try:
            # Execute method and print the domain details
            domain = api.domain(name=ctx.obj.name)
            click.echo("{}".format(domain.expiry))
        except Exception as e:  # pragma: no cover
            # fail cleanly
            ctx.fail(message="{}".format(e))


@domain.command()
@click.pass_context
def created(ctx):
    """Get domain creation date/time."""
    # Use provided helper to instantiate pynamedotcom.API object
    with ctx.obj.api() as api:
        try:
            # Execute method and print the domain details
            domain = api.domain(name=ctx.obj.name)
            click.echo("{}".format(domain.created))
        except Exception as e:  # pragma: no cover
            # fail cleanly
            ctx.fail(message="{}".format(e))


@domain.command()
@click.pass_context
def renewal_price(ctx):
    """Get domain renewal price."""
    # Use provided helper to instantiate pynamedotcom.API object
    with ctx.obj.api() as api:
        try:
            # Execute method and print the domain details
            domain = api.domain(name=ctx.obj.name)
            click.echo("${}".format(domain.renewal_price))
        except Exception as e:  # pragma: no cover
            # fail cleanly
            ctx.fail(message="{}".format(e))


@main.command()
@click.pass_context
@click.argument("name")
def search(ctx, name):
    """Search for domain availablility."""
    # Use provided helper to instantiate pynamedotcom.API object
    with ctx.obj.api() as api:
        try:
            # Execute method and print the results
            result = api.check_availability(name=name)
            if result.purchasable:
                click.echo(click.style("{} is available:".format(result.name),
                                       fg="green"))
                click.echo("  premium: {}".format(result.premium))
                click.echo("  type: {}".format(result.purchase_type))
                click.echo("  purchase price: ${}".format(result.purchase_price))  # noqa
                click.echo("  renewal price: ${}".format(result.renewal_price))
            else:
                click.echo(click.style("{} is not available".format(result.name),  # noqa
                                       fg="red"))
                ctx.exit(code=1)
        except Exception as e:  # pragma: no cover
            # fail cleanly
            ctx.fail(message="{}".format(e))
