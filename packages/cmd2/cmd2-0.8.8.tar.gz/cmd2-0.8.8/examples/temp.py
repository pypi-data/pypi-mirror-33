#!/usr/bin/env python3
# coding=utf-8
"""
Unit/functional testing for argparse completer in cmd2

Copyright 2018 Eric Lin <anselor@gmail.com>
Released under MIT license, see LICENSE file
"""
import os
from cmd2.cmd2 import Cmd, with_argparser
from cmd2 import argparse_completer

class PyscriptExample(Cmd):
    ratings_types = ['G', 'PG', 'PG-13', 'R', 'NC-17']

    def _do_media_movies(self, args) -> None:
        if not args.command:
            self.do_help('media movies')
        else:
            print('media movies ' + str(args.__dict__))

    def _do_media_shows(self, args) -> None:
        if not args.command:
            self.do_help('media shows')

        if not args.command:
            self.do_help('media shows')
        else:
            print('media shows ' + str(args.__dict__))

    media_parser = argparse_completer.ACArgumentParser(prog='media')

    media_types_subparsers = media_parser.add_subparsers(title='Media Types', dest='type')

    movies_parser = media_types_subparsers.add_parser('movies')
    movies_parser.set_defaults(func=_do_media_movies)

    movies_commands_subparsers = movies_parser.add_subparsers(title='Commands', dest='command')

    movies_list_parser = movies_commands_subparsers.add_parser('list')

    movies_list_parser.add_argument('-t', '--title', help='Title Filter')
    movies_list_parser.add_argument('-r', '--rating', help='Rating Filter', nargs='+',
                                    choices=ratings_types)
    movies_list_parser.add_argument('-d', '--director', help='Director Filter')
    movies_list_parser.add_argument('-a', '--actor', help='Actor Filter', action='append')

    movies_add_parser = movies_commands_subparsers.add_parser('add')
    movies_add_parser.add_argument('title', help='Movie Title')
    movies_add_parser.add_argument('rating', help='Movie Rating', choices=ratings_types)
    movies_add_parser.add_argument('-d', '--director', help='Director', nargs=(1, 2), required=True)
    movies_add_parser.add_argument('actor', help='Actors', nargs='*')

    movies_delete_parser = movies_commands_subparsers.add_parser('delete')

    shows_parser = media_types_subparsers.add_parser('shows')
    shows_parser.set_defaults(func=_do_media_shows)

    shows_commands_subparsers = shows_parser.add_subparsers(title='Commands', dest='command')

    shows_list_parser = shows_commands_subparsers.add_parser('list')

    @with_argparser(media_parser)
    def do_media(self, args):
        """Media management command demonstrates multiple layers of subcommands being handled by AutoCompleter"""
        func = getattr(args, 'func', None)
        if func is not None:
            # Call whatever subcommand function was selected
            func(self, args)
        else:
            # No subcommand was provided, so call help
            self.do_help('media')


if __name__ == '__main__':
    app = PyscriptExample()
    app.cmdloop()
