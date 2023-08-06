# mara-cli: Mara commandline app

A 'mara' command which exposes contributed click commands. Contributed click 
commands are exposed as subcommands. It automatically finds the 
`compose_mara_app()` function of your app, executes it, and then calls the 
appropriate subcommand.


## Contributed MARA_* functionality in this package

* A click command which iterates the known set config items 
  (directly added, not via `MARA_CLICK_COMMANDS`).

## Consumed MARA_* functionality

This consumes the `MARA_CLICK_COMMANDS` functionality.  `MARA_CLICK_COMMANDS` 
must be an iterable which yields `@click.command()` decorated functions 
(either an iterator or a functions which returns a list or a list of such 
functions).
