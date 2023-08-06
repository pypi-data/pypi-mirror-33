#!/usr/bin/env python3

import argparse
import asyncio
import gettext
import logging
import pdb
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, FileType
from datetime import datetime, time, timedelta
from functools import partial

import colorama as ca

from impetuous import __version__ as version
from impetuous.cli import parse_friendly_datetime
from impetuous.cli.actions import (FUNCTION_DEST, Cli, DryRun, im_a,
                                   im_config_edit, im_decode, im_doing,
                                   im_edit, im_encode, im_export, im_import,
                                   im_import_legacy, im_post, im_repl, im_show,
                                   im_summary, im_suggest)
from impetuous.im import Impetuous
from impetuous.interaction import OperationError, RequestError
from impetuous.sheet import localtz, utcnow

logger = logging.getLogger('impetuous')


def main():
    # Localization? Maybe?
    import os.path
    ld = os.path.join(os.path.dirname(__file__), '..', 'locale')
    gettext.install('impetuous', ld)

    today = utcnow().astimezone(localtz).date()
    since = datetime.combine(today, time(0))
    until = since + timedelta(days=1)

    # Some arguments we want to know earlier, but we don't want
    # parse_known_args to throw up if it sees '-h', so we create a parser with
    # add_help=False, then add help later on after parsing early arguments.
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter, add_help=False)
    parser.add_argument('--version', action='version', version=f'%(prog)s {version}')
    parser.add_argument('--dbecho', action='store_true', default=False,
                        help='Show everything that sqlalchemy is doing. You almost never want to do this.')
    parser.add_argument('--log', help='Logging level',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                        default='WARNING')
    parser.add_argument('--since', help='Operate on entries starting after ...',
                        type=parse_friendly_datetime, default=since)
    parser.add_argument('--until', help='Operate on entries ending before ...',
                        type=parse_friendly_datetime, default=until)
    parser.add_argument('-y', '--yesterday', help='Operate on yesterday. Can be repeated.',
                        action='count', default=0)
    parser.add_argument('-d', '--debug', action='store_true', default=False)
    args, _ = parser.parse_known_args()

    # Initialize colorama stuff
    ca.init()

    logging.basicConfig(level=getattr(logging, args.log))
    utcnow_ish = utcnow() - timedelta(days=args.yesterday)
    datetime_arg = partial(parse_friendly_datetime, default=utcnow_ish)
    datetime_arg.__name__ = 'nice looking datetime'

    try:
        impetuous = Impetuous(dbecho=args.dbecho)
        cli = Cli(impetuous)
    except BrokenPipeError:
        pass
    except KeyboardInterrupt:
        logger.info("Bye!")
    except SystemExit:
        raise
    except Exception as e:
        if args.debug:
            logger.exception(e)
            pdb.post_mortem()
        raise

    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS)

    subparser = parser.add_subparsers(title='action')
    subparser.required = True
    subparser.dest = FUNCTION_DEST

    show_help = '''Show a list things done, startings, endings, and durations
    for the current sheet.'''
    show_args = subparser.add_parser('show', help=show_help, aliases=['s', 'l'], formatter_class=ArgumentDefaultsHelpFormatter)
    show_args.add_argument('--reverse', '-r', action='store_true', default=False)
    show_args.add_argument('--verbose', '-v', action='store_true', default=False)
    show_args.add_argument('-l', '--limit', type=int, default=None)
    show_args.set_defaults(action=im_show)

    summary_help = '''Show summary organized.'''
    summary_args = subparser.add_parser('summary', help=summary_help, aliases=['ss', 'll'], formatter_class=ArgumentDefaultsHelpFormatter)
    summary_args .add_argument('--verbose', '-v', action='store_true', default=False)
    summary_args.set_defaults(action=im_summary)

    doing_help = '''Try to stop the thing running soonest before the given
    stopping time (now by default) and then start something new if you give me
    "blah".'''
    doing_args = subparser.add_parser('doing', help=doing_help, aliases=['d', 'doing'], formatter_class=ArgumentDefaultsHelpFormatter)
    doing_args.add_argument('blah', type=str, nargs='*')
    doing_args.add_argument('--when', '-w', type=datetime_arg, default='now', help='Start of period')
    doing_args.add_argument('--comment', '-c', type=str)
    doing_args.add_argument('-n', '--dry-run', action='store_true', default=False, help="Don't commit changes to the database. Just talk about them.")
    doing_args.set_defaults(action=im_doing)

    edit_help = '''Opens a YAML representation of a bunch of time entries in a
    temporary file to be modified in EDITOR.'''
    edit_args = subparser.add_parser('edit', help=edit_help, formatter_class=ArgumentDefaultsHelpFormatter)
    edit_args.add_argument('-n', '--dry-run', action='store_true', default=False, help="Don't commit changes to the database. Just talk about them.")
    edit_args.set_defaults(action=im_edit)

    suggest_help = '''Suggest something to do, like if you're bored.'''
    suggest_args = subparser.add_parser('suggest', help=suggest_help, formatter_class=ArgumentDefaultsHelpFormatter)
    suggest_args.add_argument('-l', '--limit', type=int, default=20, help="How many suggestions.")
    suggest_args.set_defaults(action=im_suggest)

    import_legacy_help = '''Import legacy/v1 time sheet. Run im -l=INFO for
    more output. Run import-legacy -q for less. Nine out of ten cat herders
    recommend running this with ~/.config/impetuous/sheets/*
    ~/.local/share/impetuous/* and then making your local impetuous maintainer
    a pot of coffee.
    This does not respect --since or --until.'''
    import_legacy_args = subparser.add_parser('import-legacy', help=import_legacy_help, formatter_class=ArgumentDefaultsHelpFormatter)
    import_legacy_args.add_argument('-n', '--dry-run', action='store_true', default=False, help="Don't commit changes to the database. Just talk about them.")
    import_legacy_args.add_argument('-q', '--quiet', action='store_true', default=False, help="Don't output the entries as they are imported.")
    import_legacy_args.add_argument('--ignore-errors', action='store_true', default=False, help="Commit partial data, even if some stuff couldn't be inserted.")
    import_legacy_args.add_argument('files', default='-', nargs='+', type=argparse.FileType('r'))
    import_legacy_args.set_defaults(action=im_import_legacy)

    config_help = '''Opens the config in EDITOR.'''
    config_args = subparser.add_parser('config-edit', help=config_help, formatter_class=ArgumentDefaultsHelpFormatter)
    config_args.set_defaults(action=im_config_edit)

    post_help = '''Submits workshows to JIRA and Freshdesk.'''
    post_args = subparser.add_parser('post', help=post_help, formatter_class=ArgumentDefaultsHelpFormatter)
    post_args.add_argument('-n', '--dry-run', action='store_true', default=False, help="Do not actually send submissions. Just talk about them.")
    post_args.set_defaults(action=im_post)

    encode_help = '''Encodes passwords/secrets in the config using a given
    codec. The config parser is very rude and will does not preserve comments
    anything in your config file when this modifies it.'''
    encode_args = subparser.add_parser('encode', help=encode_help, formatter_class=ArgumentDefaultsHelpFormatter)
    encode_args.add_argument('codec', choices=['base64', 'bz2', 'hex', 'quotedprintable', 'uu', 'zlib'])
    encode_args.set_defaults(action=im_encode)

    decode_help = '''Decodes passwords in the config using a given codec. The
    config parser is very rude and will does not preserve comments anything in
    your config file when this modifies it.'''
    decode_args = subparser.add_parser('decode', help=decode_help, formatter_class=ArgumentDefaultsHelpFormatter)
    decode_args.set_defaults(action=im_decode)

    a_help = '''What are you?'''
    a_args = subparser.add_parser('a', aliases=['an'], help=a_help, formatter_class=ArgumentDefaultsHelpFormatter)
    a_args.add_argument('?', type=str, nargs='+')
    a_args.set_defaults(action=im_a)

    repl_args = subparser.add_parser('repl', formatter_class=ArgumentDefaultsHelpFormatter)
    repl_args.set_defaults(action=im_repl)

    try:
        args = parser.parse_args()
    except BrokenPipeError:
        pass
    except KeyboardInterrupt:
        logger.info("Bye!")
    except SystemExit:
        raise
    except Exception as e:
        if args.debug:
            logger.exception(e)
            pdb.post_mortem()
        raise
    args.since -= timedelta(days=args.yesterday)
    args.until -= timedelta(days=args.yesterday)
    action = args.action

    logger.debug("Arguments are %s", args)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(action(cli, args))
    except DryRun as e:
        logger.info("Exited because dry run!")
    except RequestError as e:
        logger.error(e)
        logger.error("Tried executing: %s", e.orig.statement)
        logger.error("With: %r", e.orig.params)
        raise SystemExit(1)
    except (ValueError, OperationError) as e:
        if args.debug:
            logger.exception(e)
            pdb.post_mortem()
        else:
            logger.error(e)
        raise SystemExit(1)
    except NotImplementedError as e:
        if args.debug:
            logger.exception(e)
            pdb.post_mortem()
        else:
            logger.error("This isn't implemented: %s", e)
        raise SystemExit(1)
    except BrokenPipeError:
        pass
    except KeyboardInterrupt:
        logger.info("Bye!")
    except SystemExit:
        raise
    except Exception as e:
        if args.debug:
            logger.exception(e)
            pdb.post_mortem()
        raise
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()


if __name__ == '__main__':
    main()
