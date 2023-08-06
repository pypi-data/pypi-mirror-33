import click
import os
import sys
import notetxt
import arrow
import subprocess
from configparser import SafeConfigParser
from typing import Optional, List
import re


CFG_PATH = os.path.expanduser('~/.ntr.ini')


class Context(click.Context):
        def __init__(self):
            self.cfg = None
            self.obj = None


class AliasedGroup(click.Group):

    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        matches = [x for x in self.list_commands(ctx)
                   if x.startswith(cmd_name)]
        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail('Too many matches: %s' % ', '.join(sorted(matches)))


def load_config(path: str=CFG_PATH) -> Optional[SafeConfigParser]:
    cfg_parser = SafeConfigParser()
    if CFG_PATH not in cfg_parser.read(path):
        return None
    return cfg_parser


def check_cfg(cfg):
    if cfg is None:
        click.echo('There seems to be a problem with the configuration.')
        click.echo(f'Please check whether {click.style(CFG_PATH, bold=True)} '
                   'exists.')
        click.echo('If it does not, feel free to run "' +
                   click.style('ntr config --init ', bold=True) +
                   '" which will create a config file for you.')
        sys.exit(-1)


def get_notedir(cfg: dict) -> str:
    check_cfg(cfg)
    return cfg.get('general', 'notedir')


def load_notes(cfg: dict):
    return notetxt.load_from_dir(get_notedir(cfg))

def find_note_by_grep(grep: str, ignore_case: bool,
                      notes: List[notetxt.Note],
                      ctx: click.Context) -> notetxt.Note:

    flags = re.I if ignore_case else 0
    filtered_notes = list(filter(lambda x: re.search(grep, x.title, flags), notes))

    if len(filtered_notes) > 1:
        click.secho('We found more than one note with the provided grep:',
                    fg='yellow')
        ctx.invoke(list_, grep=grep, ignore_case=ignore_case)
        sys.exit(-1)

    return filtered_notes[0]



def find_note_by_id(note_id: str, notes: List[notetxt.Note],
                    ctx: click.Context) -> notetxt.Note:
    filtered_notes = list(filter(lambda x: x.id.startswith(note_id), notes))

    if len(filtered_notes) > 1:
        click.secho('We found more than one note with the provided note_id:',
                    fg='yellow')
        ctx.invoke(list_, id=note_id)
        sys.exit(-1)

    return filtered_notes[0]

pass_context = click.make_pass_decorator(Context, ensure=True)


@click.command(cls=AliasedGroup)
@pass_context
@click.option('--cfg', help='Config file path', required=False,
              default=CFG_PATH)
def ntr(ctx, cfg):
    ctx.cfg = load_config(cfg)


@ntr.command(name='list')
@pass_context
@click.option('--time', '-t', help='Sort by age (descending)', is_flag=True,
              default=True)
@click.option('--reverse', '-r', help='Reverse ordering', is_flag=True,
              default=False)
@click.option('--id', help='ID (prefix) of a given note')
@click.option('--grep', '-g',
              help='A regular expression to "grep" through the notes list',
              default=None)
@click.option('--ignore-case', '-i',
              help='Ignore case of characters when grepping', is_flag=True)
@click.option('--max-results', '-n', help='Maximum number of results',
              type=int, default=None)
def list_(ctx, time, reverse, id, grep, ignore_case, max_results):
    cfg = ctx.cfg
    notes = load_notes(cfg)

    if id:
        notes = list(filter(lambda x: x.id.startswith(id), notes))

    if grep:
        flags = re.I if ignore_case else 0
        notes = list(filter(lambda x: re.search(grep, x.title, flags), notes))

    for note in notes:
        note.last_modified = note.path.stat().st_mtime
        note.readable_last_modified = arrow.get(note.last_modified).humanize()

    sorting_mapping = {
        't': lambda x: -x.last_modified,
    }

    sorting_fn = None
    if time:
        sorting_fn = sorting_mapping['t']

    max_results = len(notes) if max_results is None else max_results

    for i, note in enumerate(sorted(notes, key=sorting_fn, reverse=reverse),
                             start=1):
        fmt = f"{note.id[:4]}\t{note.readable_last_modified}\t{note.title}"
        click.echo(fmt)
        if i >= max_results:
            break


@ntr.command()
@pass_context
@click.argument('note_id')
@click.option('--grep', '-g',
              help='Find a note by "grepping" through their titles',
              is_flag=True)
@click.option('--ignore-case', '-i',
              help='Ignore case of characters when grepping', is_flag=True)
def edit(ctx, note_id, grep, ignore_case):
    cfg = ctx.cfg
    notes = load_notes(cfg)

    if grep:
        note = find_note_by_grep(note_id, ignore_case, notes, ctx)
    else:
        note = find_note_by_id(note_id, notes, ctx)

    editor = os.environ.get('EDITOR', 'vim')
    subprocess.run([editor, note.path])


@ntr.command()
@pass_context
@click.argument('title', required=True)
def new(ctx, title):
    cfg = ctx.cfg

    now = arrow.now()

    tag = now.format('YYYY/MM')
    notedir = get_notedir(cfg)
    note = notetxt.new_note(title, tag, notedir)

    ctx.invoke(edit, note_id=note.id)


@ntr.command()
@pass_context
@click.argument('note_id')
@click.option('--add', '-a', help='Add a tag')
@click.option('--rm', '-r', help='Remove a tag')
def tag(ctx, note_id, add, rm):
    cfg = ctx.cfg
    notes = load_notes(cfg)

    note = find_note_by_id(note_id, notes, ctx)
    if add:
        note.add_tag(add)
    elif rm:
        note.remove_tag(rm)
    else:
        for tag in note.tags:
            click.echo(tag)

    note.save_tags()


@ntr.command()
@pass_context
@click.option('--init', is_flag=True)
@click.argument('key', required=False, default=None)
@click.argument('value', required=False, default=None)
def config(ctx, init, key, value):
    cfg = ctx.cfg
    if init:
        if cfg is None:
            cfg = SafeConfigParser()
            cfg.add_section('general')

            click.echo(f'The config file located at {CFG_PATH} has '
                       'been created.')
            click.echo('In order to set the notes dir, please run')
            click.secho('ntr config notedir PATH', bold=True)
            cfg.write(open(CFG_PATH, 'w'))
            return
        else:
            click.echo('It seems the config file located at' +
                       click.style(f' {CFG_PATH} ', bold=True) +
                       click.style('already exists', bold=True, fg='red') +
                       '.')
            click.echo('We are therefore not performing any action '
                       'at this point.')
            sys.exit(-1)

    if key is not None and value is not None:
        cfg.set('general', key, value)
        cfg.write(open(CFG_PATH, 'w'))

    if key is not None and value is None:
        click.echo(cfg.get('general', key))

    if key is None and value is None:
        for section_name in cfg.sections():
            click.echo(f'[{section_name}]')
            for name, value in cfg.items(section_name):
                click.echo(f'{name}={value}')


if __name__ == "__main__":
    ntr()
