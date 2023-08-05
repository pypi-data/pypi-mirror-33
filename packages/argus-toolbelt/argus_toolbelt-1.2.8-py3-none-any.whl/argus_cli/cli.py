from colorama import init, deinit
from pprint import pprint

from api_generator import load
from argus_cli.settings import settings, update_settings  # Settings has to be before the logger!
from argus_cli.helpers.log import log
from argus_cli import plugin
from argus_cli.arguments import get_command_arguments, get_plugin_arguments
from argus_cli.plugin import run_command, load_plugin_module, get_plugin_modules, register_command_metadata


def setup() -> None:
    """Does setup of the API and loads plugins"""
    plugin.api = load(settings["api"]["api_url"], settings["api"]["definitions"])

    plugins = get_plugin_modules(settings["cli"]["plugins"])
    log.info("Loading plugins...")
    for plug in plugins:
        load_plugin_module(plug)


def run() -> None:
    """Parses command and runs the application"""
    plugin_name, command_name = get_plugin_arguments()
    register_command_metadata(plugin_name, command_name)

    arguments = get_command_arguments()

    # FIXME: This isn't the cleanest solution. Should look for a better one for program wide args
    user_api_key = arguments.get("apikey")
    if user_api_key:
        update_settings(["api", "api_key"], user_api_key)
    # Remove debug and api_key arguments
    arguments.pop("debug")
    arguments.pop("apikey")

    result = run_command(plugin_name, command_name, arguments)

    if result:
        pprint(result)


def main() -> None:
    """Used to launch the application"""
    # Initialize colorama to enable Windows color support
    init()

    # Initialize and run argus cli
    setup()
    run()

    # Deinitialize colorama
    deinit()
