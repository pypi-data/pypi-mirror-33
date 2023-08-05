from datetime import datetime
import click
import os
import string
import subprocess
import sys
import yaml


def load_config():
    homedir = os.path.expanduser("~")
    tasks = {}
    default_vars = {}
    def update(cfgfile):
        if os.path.exists(cfgfile):
            config = yaml.load(open(cfgfile))
            tasks.update(config.get("tasks", {}))
            default_vars.update(config.get("vars", {}))

    update(os.path.join(homedir, ".bud.yml"))
    update(os.path.join(os.getcwd(), "bud.yml"))

    return {"tasks": tasks, "vars": default_vars}

def log(name, command):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cwd = os.getcwd()
    bud = " ".join(sys.argv)
    if "\n" in command:
        cmd = command.encode("unicode_escape").decode("utf-8")
    else:
        cmd = command
    d = {"ts": ts, "cwd": cwd, "cmd": cmd, "bud": bud}
    print("{ts} {cwd}$ {cmd} #{bud}".format(**d))


def execute(name, command):
    subprocess.call(command, shell=True, executable="/bin/bash")


def get_params(s):
    formatter = string.Formatter()
    return [fname for _, fname, _, _ in formatter.parse(s) if fname]


class BudCLI(click.MultiCommand):

    def list_commands(self, ctx):
        config = load_config()
        return list(config.get("tasks", {}).keys())

    def get_command(self, ctx, name):
        ns = {}
        config = load_config()
        task =  config.get("tasks", {})[name]
        params = []
        for p in get_params(task):
            default = config.get("vars", {}).get(p, None)
            if default:
                params.append(click.Option(("--{}".format(p),), envvar=p.upper(), default=default, help="default: {}".format(default)))
            else:
                params.append(click.Option(("--{}".format(p),), envvar=p.upper(), required=True))

        def callback(*args, **kwargs):
            log=ctx.obj["log"]
            command = task.format(**kwargs) 
            if not ctx.obj["quiet"]:
                click.echo("> "+click.style(command, fg='green'))
            sys.exit(execute(name, command))

        ret = click.Command(name, help=task, short_help=task, params=params, callback=callback)
        return ret


@click.command(cls=BudCLI, invoke_without_command=True)
@click.option('--quiet', is_flag=True, default=False, help='hide output')
@click.pass_context
def cli(ctx, quiet):
    """simple command executor"""
    ctx.obj["log"] = log
    ctx.obj["quiet"] = quiet 

def main():
    cli(obj={})


if __name__ == '__main__':
    main() 

