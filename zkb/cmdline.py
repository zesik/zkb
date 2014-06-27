# -*- coding: utf-8 -*-
"""
zkb.cmdline
~~~~~~~~~~~

Command line processor for ZKB.

:Copyright: Copyright 2014 Yang LIU <zesikliu@gmail.com>
:License: BSD, see LICENSE for details.
"""

import os
import datetime
import argparse
import subprocess
import SocketServer
import SimpleHTTPServer
import webbrowser
import pkg_resources

from zkb.readers import HeaderedContentReader
from zkb.builder import SiteBuilder
from zkb.builder import FileProcessor
from zkb.config import SiteConfig
from zkb.log import logger


_DEFAULT_CONFIG_FILE = '_config.yml'
_ADDRESS = 'localhost'
_PORT = 8900


def _load_config(filename):
    """Load site config from config file.

    :param filename: file name
    :type filename: str
    :rtype: SiteConfig
    """
    extension = os.path.splitext(filename)[1].lower()
    reader = HeaderedContentReader.from_extension(extension)
    logger.info('Loading config...')
    with open(filename, 'r') as stream:
        config, _, _ = reader.read(stream)
    return SiteConfig(config)


def init(args):
    filename = _DEFAULT_CONFIG_FILE
    if os.path.isfile(filename):
        logger.error('Config file already exist.')
        return 1
    lines = SiteConfig.default_config()
    with open(filename, 'w+') as f:
        f.writelines(lines)
    logger.info('Config file generated (%s). Please make changes to it to '
                'include correct blog information.' % args.config)


def init_git(args):
    config = _load_config(args.config)
    src_dir = os.path.realpath(config.article_dir)
    out_dir = os.path.realpath(config.output_dir)
    # Initialize git repository for source
    subprocess.call('git init', shell=True, cwd=src_dir)
    if out_dir.startswith(src_dir):
        echo_command = 'echo %s > %s' % (config.output_dir, '.gitignore')
        subprocess.call(echo_command, shell=True, cwd=src_dir)
    echo_command = 'echo Hello world > %s' % 'README'
    subprocess.call(echo_command, shell=True, cwd=src_dir)
    subprocess.call('git add --all', shell=True, cwd=src_dir)
    subprocess.call('git commit -m \"Initial commit\"',
                    shell=True, cwd=src_dir)
    subprocess.call('git branch -m source', shell=True, cwd=src_dir)
    subprocess.call('git remote add origin %s' % config.git_remote,
                    shell=True, cwd=src_dir)
    # Initialize git repository for output
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    subprocess.call('git init', shell=True, cwd=out_dir)
    echo_command = 'echo Hello world > %s' % 'index.html'
    subprocess.call(echo_command, shell=True, cwd=out_dir)
    subprocess.call('git add --all', shell=True, cwd=out_dir)
    subprocess.call('git commit -m \"Initial commit\"',
                    shell=True, cwd=out_dir)
    subprocess.call('git remote add origin %s' % config.git_remote,
                    shell=True, cwd=out_dir)
    logger.info('Git repository initialized.')


def customize(args):
    config = _load_config(args.config)
    template_dir = os.path.realpath(config.template_dir)
    template_files = [
        'archive.html',
        'article.html',
        'footer.html',
        'header.html',
        'index.html',
        'tags.html',
        'images/header-1.jpg',
        'images/header-2.jpg',
        'stylesheets/style.css',
        'stylesheets/codeblock.css']
    logger.info('Writing templates...')
    fileproc = FileProcessor()
    for file in template_files:
        stream = pkg_resources.resource_stream(
            'zkb', 'templates/default/' + file)
        fileproc.write_stream(
            os.path.join(template_dir, *file.split('/')), stream)
    logger.info('All done.')


def build(args):
    config = _load_config(args.config)
    result = SiteBuilder.from_config(config).build()
    if result == 0:
        logger.info('All done.')
    else:
        logger.error('Failed to generate partial or all content.')


def test(args):
    config = _load_config(args.config)
    os.chdir(config.output_dir)
    httpd = SocketServer.TCPServer((_ADDRESS, _PORT),
                                   SimpleHTTPServer.SimpleHTTPRequestHandler)
    webbrowser.open('http://%s:%d%s' % (_ADDRESS, _PORT, config.url))
    logger.info('Serving at port %d...' % _PORT)
    httpd.serve_forever()


def deploy(args):
    config = _load_config(args.config)
    src_dir = os.path.realpath(config.article_dir)
    out_dir = os.path.realpath(config.output_dir)
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if args.force:
        push_command = 'git push -u --force origin %s'
    else:
        push_command = 'git push -u origin %s'
    subprocess.call('git add --all', shell=True, cwd=src_dir)
    subprocess.call('git commit -m \"Commit of %s\"' % date,
                    shell=True, cwd=src_dir)
    subprocess.call('git add --all', shell=True, cwd=out_dir)
    subprocess.call('git commit -m \"Commit of %s\"' % date,
                    shell=True, cwd=out_dir)
    subprocess.call(push_command % "source", shell=True, cwd=src_dir)
    subprocess.call(push_command % "master", shell=True, cwd=out_dir)
    logger.info('All done.')


def main():
    config_param = {'nargs': '?',
                    'metavar': 'CONFIG',
                    'default': _DEFAULT_CONFIG_FILE,
                    'help': 'config file.'}
    arg_parser = argparse.ArgumentParser(
        prog='zkb', description='ZKB, a static blog generator')
    subparsers = arg_parser.add_subparsers(title='commands:')
    # `init' command
    init_parser = subparsers.add_parser(
        'init', help='initialize blog')
    init_parser.add_argument('config', **config_param)
    init_parser.set_defaults(func=init)
    # `init-git' command
    init_git_parser = subparsers.add_parser(
        'init-git', help='initialize git repository for the blog')
    init_git_parser.add_argument('config', **config_param)
    init_git_parser.set_defaults(func=init_git)
    # `customize' command
    customize_parser = subparsers.add_parser(
        'customize', help='write templates for customization')
    customize_parser.add_argument('config', **config_param)
    customize_parser.set_defaults(func=customize)
    # `build' command
    build_parser = subparsers.add_parser(
        'build', help='build blog')
    build_parser.add_argument('config', **config_param)
    build_parser.set_defaults(func=build)
    # `test' command
    test_parser = subparsers.add_parser(
        'test', help='start a local server to test blog')
    test_parser.add_argument('config', **config_param)
    test_parser.set_defaults(func=test)
    # `deploy' command
    deploy_parser = subparsers.add_parser(
        'deploy', help='deploy the blog to remote git repository')
    deploy_parser.add_argument('config', **config_param)
    deploy_parser.add_argument('-f', '--force',
                               help='add \'--force\' when pushing',
                               action='store_true')
    deploy_parser.set_defaults(func=deploy)
    # Parse args
    args = arg_parser.parse_args()
    return args.func(args)


