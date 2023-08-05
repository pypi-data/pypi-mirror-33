# coding=utf-8
"""
Manages the test suite
"""
import os
import webbrowser
from pathlib import Path
import shutil

import click

import epab.utils
from epab.core import CONFIG, CTX

PYTEST_OPTIONS = ' '.join([
    '--cov={package}',
    '--cov-report xml',
    '--cov-report html',
    '--cov-branch',
    # f'--cov-fail-under={CONFIG.test__coverage__fail_under}',
    '--durations={test_duration}',
    # '--hypothesis-show-statistics',
    '--tb=short',
    '--cov-config .coveragerc',
    # '--dead-fixtures',
    # '--dup-fixtures',
    # '-x',
])

# noinspection SpellCheckingInspection
COVERAGE_CONFIG = r"""
## http://coverage.readthedocs.io/en/latest/config.html
[run]
# timid = True
branch = True
source = epab
# omit =

[report]
# Regexes for lines to exclude from consideration
exclude_lines =
    # Have to re-enable the standard pragma
    pragma: no cover

    # Don't complain about missing debug-only code:
    def __repr__
    if self\.debug

    # Don't complain if tests don't hit defensive assertion code:
    raise AssertionError
    raise NotImplementedError
    pass

    # Ignore abstract definitions:
    @abc.abstractmethod
    @abc.abstractproperty

    # Ignore click commands
    # @click.command()

    # Don't complain if non-runnable code isn't run:
    if 0:
    if __name__ == .__main__.:

[html]
directory = ./htmlcov
title = Coverage report

[paths]
source=
    ./epab
"""


class _Coverage:
    @staticmethod
    def install():
        """
        Installs coverage config file
        """
        Path('.coveragerc').write_text(COVERAGE_CONFIG.format(package_name=CONFIG.package))

    @staticmethod
    def upload_coverage_to_codacy():
        """
        Uploads the coverage to Codacy
        """
        if Path('coverage.xml').exists():
            epab.utils.AV.info('Uploading coverage to Codacy')
            epab.utils.run('pip install --upgrade codacy-coverage')
            epab.utils.run('python-codacy-coverage -r coverage.xml')
            epab.utils.AV.info('Codacy coverage OK')
        else:
            epab.utils.AV.error('"coverage.xml" not found, skipping codacy coverage')

    # Disabled for the time being
    # @staticmethod
    # def upload_coverage_to_scrutinizer():
    #     """
    #     Uploads the coverage to Scrutinizer
    #     """
    #     if os.getenv('SCRUT_TOK', False):
    #         if Path('coverage.xml').exists():
    #             epab.utils.AV.info('Uploading coverage to Scrutinizer')
    #             epab.utils.run('pip install git+https://github.com/etcher-vault/ocular.py.git#egg=ocular')
    #             token = os.getenv('SCRUT_TOK')
    #             epab.utils.run(
    #                 f'ocular --access-token "{token}" --data-file "coverage.xml" --config-file ".coveragerc"'
    #             )
    #             epab.utils.AV.info('Scrutinizer coverage OK')
    #         else:
    #             epab.utils.AV.error('"coverage.xml" not found, skipping ocular coverage')
    #     else:
    #         epab.utils.AV.error('no "SCRUT_TOK" in environment, skipping ocular coverage')

    @staticmethod
    def remove_config_file():
        """
        Removes coverage config file
        """
        Path('.coveragerc').unlink()


def upload_coverage():
    """
    Sends coverage result to Codacy and Scrutinizer if running on AV
    """
    if CTX.appveyor:
        # _Coverage.upload_coverage_to_scrutinizer()
        _Coverage.upload_coverage_to_codacy()
    else:
        epab.utils.info('skipping coverage upload')


def pytest_options():
    """
    Returns: PyTest standard command line options
    """
    return PYTEST_OPTIONS.format(
        package=CONFIG.package,
        test_duration=CONFIG.test__duration,
    )


@epab.utils.run_once
def _pytest(test, *, long, show, exitfirst, last_failed, failed_first):
    epab.utils.info('Running test suite')
    os.environ['PYTEST_QT_API'] = 'pyqt5'
    _Coverage.install()
    cmd = f'python -m pytest {test}'

    if CTX.appveyor and CONFIG.test__av_runner_options:
        cmd = f'{cmd} {CONFIG.test__av_runner_options}'
    elif CONFIG.test__runner_options:
        cmd = f'{cmd} {CONFIG.test__runner_options}'

    long = ' --long' if long else ''
    exitfirst = ' --exitfirst' if exitfirst else ''
    last_failed = ' --last-failed' if last_failed else ''
    failed_first = ' --failed-first' if failed_first else ''

    if Path('./htmlcov').exists():
        shutil.rmtree('./htmlcov')
    cmd = f'{cmd} {pytest_options()}{long}{exitfirst}{last_failed}{failed_first}'

    try:
        epab.utils.run(cmd)
    finally:
        upload_coverage()
        _Coverage.remove_config_file()
    if show:
        # noinspection SpellCheckingInspection
        path = Path('./htmlcov/index.html').absolute()
        webbrowser.open(f'file://{path}')


@click.command(context_settings=dict(ignore_unknown_options=True))
@click.option('-l', '--long', is_flag=True, default=False, help='Long tests')
@click.option('-s', '--show', is_flag=True, default=False, help='Show coverage in browser')
@click.option('-x', '--exitfirst', is_flag=True, default=False, help='Exit instantly on first error')
@click.option('--lf', '--last-failed', is_flag=True, default=False, help='Rerun only the tests that failed')
@click.option('--ff', '--failed-first', is_flag=True, default=False,
              help='Run all tests but run the last failures first')
@click.option('-t', '--test', default=CONFIG.test__target, help='Select which tests to run')
def pytest(test, long, show, exitfirst, last_failed, failed_first):
    """
    Runs Pytest (https://docs.pytest.org/en/latest/)
    """
    _pytest(
        test,
        long=long,
        show=show,
        exitfirst=exitfirst,
        last_failed=last_failed,
        failed_first=failed_first,
    )
