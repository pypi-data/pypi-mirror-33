# -*- coding: UTF-8 -*-

import click
import sys, os

p = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if p not in sys.path:
    sys.path.insert(0, p)

from .lib import jp_dict
from .lib import pixiv_daily
from .lib import nikkei_top

@click.group()
def faya():
    pass


@click.command()
@click.argument('word')
def jp(word):
    print(word)
    msg = jp_dict.get(word)
    click.echo(msg)


# @click.command()
# @click.argument('word')
# def ox(word):
#    print(word)
#    msg = main_lib.get('?ox')(word)
#    click.echo(msg)


@click.command()
def pixiv():
    msg = pixiv_daily.get()
    click.echo(msg)

@click.command()
def nikkei():
    msg = nikkei_top.get()
    click.echo(msg)


faya.add_command(jp)
# faya.add_command(ox)
faya.add_command(pixiv)
faya.add_command(nikkei)

if __name__ == '__main__':
    jp('眠い')
