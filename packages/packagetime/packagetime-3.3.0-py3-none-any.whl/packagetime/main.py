import re
import pathlib
import sys
import logging
import subprocess
import logging
import argparse
import yaml
import os

PYTHON = sys.executable

logging.basicConfig( format = '%(asctime)s %(levelname)s: %(message)s', level = logging.INFO )

def loadConfiguration( path ):
    if path.exists():
        config = yaml.load( path.open() )
        logging.warning( 'loaded configuration from {}: {}'.format( path, config ) )
        return config
    else:
        NULL_CONFIGURATION = { 'publishTo': 'pypi' }
        return NULL_CONFIGURATION

def run( command ):
    global arguments
    logging.info( command )
    if arguments.dryRun:
        return
    subprocess.run( command, shell = True, check = True )

def gitStuff( version ):
    run( 'git pull' )
    run( 'git commit -m "version {}"'.format( version ) )
    run( 'git tag {}'.format( version ) )
    run( 'git push' )
    run( 'git push --tags' )

def package( name ):
    run( 'rm -fr build/ {name}.egg-info/ && {python} setup.py bdist_wheel'.format( name = name, python = PYTHON ) )

def publishToPyPI():
    run( '{python} setup.py bdist_wheel upload'.format( python = PYTHON ) )

def main():
    CONFIG_FILE = pathlib.Path.home() / '.packagetime'
    configuration = loadConfiguration( CONFIG_FILE )
    parser = argparse.ArgumentParser()
    parser.add_argument( '--dry-run', action='store_true', dest='dryRun' )
    parser.add_argument( '--publish-to', dest='publishTo', default=configuration[ 'publishTo' ], metavar='DESTINATION', help='user@host:~/destination or "pypi"' )
    parser.add_argument( '--no-publish', action='store_true', dest='noPublish', help = 'do not publish, just package' )
    parser.add_argument( '--no-git', action='store_true', dest='noGIT', help = 'skip commits and tagging' )
    parser.add_argument( '-y', '--yes', action='store_true', help = 'skip confirmation from user' )
    global arguments
    arguments = parser.parse_args()

    logging.basicConfig( format = '%(levelname)s: %(message)s', level = logging.INFO )

    setupContent = open( 'setup.py' ).read()
    VERSION_PATTERN = re.compile(  "version\s*=\s*.(?P<version>[0-9.a-z]+).", re.MULTILINE )
    version = VERSION_PATTERN.search( setupContent ).groupdict()[ 'version' ]
    NAME_PATTERN = re.compile( 'name\s*=\s*.(?P<name>.+).,$', re.MULTILINE )
    name = NAME_PATTERN.search( setupContent ).groupdict()[ 'name' ]
    if arguments.dryRun or arguments.yes:
        answer = 'yes'
    else:
        answer = input( 'will commit and publish {}. continue? (yes/no): '.format( version ) )
    if answer != 'yes':
        print( 'bye.' )
        quit()
    if not arguments.noGIT:
        gitStuff( version )
    package( name )
    if arguments.noPublish:
        return
    if arguments.publishTo == 'pypi':
        publishToPyPI()
    else:
        scpPattern = 'scp dist/*{version}*whl ' + arguments.publishTo
        run( scpPattern.format( version = version, publishTo = arguments.publishTo, name = name ) )
