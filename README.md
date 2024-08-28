# Soluble

![Made with POP](https://img.shields.io/badge/made%20with-pop-teal)
![Made with Python](https://img.shields.io/badge/made%20with-python-yellow)

**Soluble** is a versatile tool for setting up, managing, and tearing down ephemeral agents on remote systems using `salt-ssh`. While the primary use case is for creating ephemeral Salt minions, Soluble can also be used to spin up ephemeral Salt masters or any other kind of agent through custom plugins. This makes it an ideal tool for transient infrastructure needs.

## About

Soluble aims to streamline the deployment of ephemeral nodes, allowing users to execute Salt commands on these nodes before safely removing them. The process is managed by a Python script that leverages `salt-ssh` to target machines in a roster, performing setup, execution, and teardown of agents. Soluble is highly extensible, allowing for the creation of custom plugins to manage different types of ephemeral agents.

### What is POP?

This project is built with [POP](https://pop.readthedocs.io/), a Python-based implementation of *Plugin Oriented Programming (POP)*. POP seeks to bring together concepts and wisdom from the history of computing in new ways to solve modern computing problems.

For more information:

- [Intro to Plugin Oriented Programming (POP)](https://pop-book.readthedocs.io/en/latest/)
- [pop-awesome](https://gitlab.com/vmware/pop/pop-awesome)
- [pop-create](https://gitlab.com/vmware/pop/pop-create/)

## Getting Started

### Prerequisites

- Python 3.10+
- Git (if installing from source or contributing to the project)
- SaltStack installed on the master node
- `salt` and `salt-key` commands available

### Installation

You can install `soluble` either from [PyPI](https://pypi.org/project/soluble/) or from source on [GitHub](https://github.com/saltstack/soluble).

#### Install from PyPI

```bash
pip install soluble
```

#### Install from Source

```bash
# Clone the repository
git clone https://github.com/saltstack/soluble.git
cd soluble

# Setup a virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

Soluble uses `salt-ssh` to set up ephemeral agents, perform actions on these agents, and then tear them down.

### Plugins

A soluble plugin contains a `conf.py` and a `soluble` directory containing the Python file for the plugin. Each plugin must contain three functions: `setup`, `run`, and `teardown`.

- **`setup`:** Prepares the soluble agent. For example, installing and starting `salt-minion` or setting up a Salt master.
- **`run`:** Executes the primary function of the plugin. This is the only function that should print to stdout.
- **`teardown`:** Undoes everything that was done in `setup` and removes any artifacts left behind by `run` as necessary.

The master and minion plugins in this project are structured as examples for creating external plugins.

### Python Code Examples

Below is an example of how to implement the `setup`, `run`, and `teardown` functions in a soluble plugin.
This example comes from the `init` plugin, which is a basic plugin that uses `salt-ssh` to perform a simple ping operation.

```python
# project_root/<my_plugin>/soluble/<my_plugin>.py


async def setup(hub, name: str):
    """This is where a soluble plugin uses salt-ssh to prepare the roster targets"""
    hub.log.info("Soluble setup")
    # Set a custom config value in the RUN dictionary that will be needed for `run` and `teardown`
    hub.soluble.RUN[name].my_key = "my value"
    await hub.salt.ssh.run_command(
        name,
        f"test.ping",
    )


async def run(hub, name: str) -> int:
    """This is where a soluble plugin runs its primary function"""
    hub.log.info("Soluble run")
    await hub.salt.ssh.run_command(name, f"test.ping", capture_output=False)
    return 0


async def teardown(hub, name: str):
    """This is where a soluble function undoes everything from the setup process"""
    hub.log.info("Soluble teardown")
    await hub.salt.ssh.run_command(
        name,
        f"test.ping",
    )
```

### CLI and Configuration

The `name` argument is passed to all the functions. `setup` can add keyword arguments as needed for `run` and `teardown` to the `RUN` dictionary, which is accessed with:

```python
hub.soluble.RUN[name]
```

Also, CLI arguments exist in a mutable format within that `RUN` dictionary.

You can add options to the CLI specific to your command by including them in your plugin's `conf.py`:

```python
# project_root/<my_plugin>/conf.py

# Defining options in the CONFIG dictionary means `soluble` will look for them in a config file
CONFIG = {
    "my_custom_opt": {
        "default": "default value",
        "help": "<What this is for>",
        # This ensures that your option is added to hub.soluble.RUN[name]
        "dyne": "soluble",
    },
}

# Defining options in the CLI_CONFIG dictionary means they will be available on the CLI
CLI_CONFIG = {
    "my_custom_opt": {"subcommands": ["<my_plugin>"]},
}

DYNE = {"soluble": ["soluble"]}
```

### Examples

Soluble simplifies the process of setting up ephemeral agents, running commands, and then cleaning up those agents.
Plain `salt-ssh` gives you a small subset of the full capability of salt.  `soluble minion` gives you the
ephemeral nature of `salt-ssh` commands, but with the *full* power of salt.

Here’s a basic usage example:

```bash
soluble -R /path/to/roster minion '*' test.ping
```

In this example:
- The `-R` flag specifies the path to the roster file for `salt-ssh`.
- The first positional argument (`test.ping`) is the Salt command to be executed on the ephemeral minions.

#### Basic Soluble Plugins

There are three basic soluble plugins: `init`, `minion`, and `master`.

- **Init Plugin Example:**

  The init plugin just does a "test.ping" with `salt-ssh`.

  ```bash
  soluble -R /path/to/roster init '*'
  ```

- **Soluble Minion Examples:**

  ```bash
  # Install a package on ephemeral nodes
  soluble minion '*' pkg.install vim

  # Apply a state file
  soluble minion '*' state.apply my_state

  # Ping minions
  soluble minion '*' test.ping
  ```

- **Soluble Master Example:**

  This will spin up a master on the roster targets until you hit CTRL-C.

  ```bash
  soluble -R /path/to/roster master --master-config=/path/to/config '*'
  ```

  To leave the master running indefinitely, add the `--bootstrap` flag.

  ```bash
  soluble -R /path/to/roster master --master-config=/path/to/config '*' --bootstrap
  ```

## Roadmap

Refer to the [open issues](https://github.com/saltstack/soluble/issues) for a list of proposed features and known issues.

The project roadmap includes:
- Expanding support for additional Salt modules and functions.
- Enhancing error handling and logging for more robust operation.
- Integration with other infrastructure management tools.

## Acknowledgements

- [Img Shields](https://shields.io) for making repository badges easy.

---

### Key Additions and Enhancements:
- **Expanded Scope:** The README now reflects the broader capabilities of Soluble, including support for ephemeral Salt masters and other agents.
- **Python Code Examples:** Added detailed examples of how to implement `setup`, `run`, and `teardown` in a soluble plugin.
- **Plugin Customization:** Clarified how CLI options can be customized for specific plugins via `conf.py`.
