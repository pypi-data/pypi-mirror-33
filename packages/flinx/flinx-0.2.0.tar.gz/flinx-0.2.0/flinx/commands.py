import inspect
import subprocess
import sys
import webbrowser
from functools import wraps
from pathlib import Path

import click

from sphinx.cmd.build import main as sphinx_build

from .generation import write_template_files


def generation_options(verbose=True):
    """Add generation options."""
    def inner(f):
        @click.option('--force', is_flag=True,
                      help="Overwrite conf.py and index.rst")
        @click.option('--unless-exists', is_flag=True,
                      help="Skip conf.py and index.rst generation without error, "
                      "if non-generated files exists.")
        @click.option('--verbose', is_flag=True, default=verbose)
        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)

        return wrapper
    return inner


@click.group()
def cli():
    """Configuration-free Sphinx builder."""
    pass


@cli.command()
@generation_options(verbose=True)
def generate(force=False, unless_exists=False, verbose=False):
    """Write the generated files."""
    docs_dir = Path('./docs')
    write_template_files(docs_dir, force=force, unless_exists=unless_exists,
                         verbose=verbose)


@cli.command()
@generation_options(verbose=True)
def eject(force=False, unless_exists=False, verbose=False):
    """Write the generated files, without header warnings."""
    docs_dir = Path('./docs')
    write_template_files(docs_dir, force=force, include_generated_warning=False,
                         unless_exists=unless_exists, verbose=verbose)


def build_sphinx_args(all_files=False,
                      force=False,
                      fmt='html',
                      unless_exists=False,
                      verbose=False,
                      **args):
    """Translate shared options into a new set of options, and write templates."""
    docs_dir = Path('./docs')
    build_dir = docs_dir / '_build' / fmt
    write_template_files(docs_dir, force=force, unless_exists=unless_exists,
                         verbose=verbose)
    args = [
        '-b', fmt,
        '-c', str(docs_dir),  # config file directory
        '-j', 'auto',  # processors
    ]
    if not verbose:
        args += ['-q']
    if all_files:
        args += ['-a']
    args += [str(docs_dir), str(build_dir), ]
    return dict(build_args=args, build_dir=build_dir, docs_dir=docs_dir)


def with_sphinx_build_args(f):
    """Decorate a function to consume a common set of options."""
    @click.option('-a', '--all-files', is_flag=True,
                  help='Rebuild all the docs, regardless of what has changed.')
    @click.option('-o', '--open-url', is_flag=True,
                  help='Open the HTML index in a browser.')
    @click.option('--format', 'fmt', default='html',
                  help='The output format.')
    @generation_options(verbose=False)
    @wraps(f)
    def wrapper(**kwargs):
        build_args = build_sphinx_args(**kwargs)
        kwargs = {k: v for k, v in kwargs.items() if k not in consumed_args}
        for k, v in build_args.items():
            if k in wrapped_args:
                kwargs[k] = v
        return f(**kwargs)

    def non_variadic_param_names(f):
        """Return a set of names of f's non-variadic parameters."""
        var_parameter_kinds = (inspect.Parameter.VAR_POSITIONAL,
                               inspect.Parameter.VAR_KEYWORD)
        return {p.name for p in inspect.signature(f).parameters.values()
                if p.kind not in var_parameter_kinds}

    # names of parameters to the wrapped function
    wrapped_args = non_variadic_param_names(f)
    # names of parameters that shouldn't be passed to the wrapped function
    consumed_args = non_variadic_param_names(build_sphinx_args) - wrapped_args
    return wrapper


@cli.command()
@with_sphinx_build_args
def build(build_args=None, docs_dir=None, build_dir=None, fmt=None, open_url=False):
    """Use sphinx-build to build the documentation."""
    status = sphinx_build(build_args)
    if status:
        sys.exit(status)
    if open_url and fmt == 'html':
        webbrowser.open(str(build_dir / 'index.html'))


@cli.command()
@with_sphinx_build_args
def serve(build_args=None, open_url=False):
    """Use sphinx-autobuild to build and serve the documentation."""
    if open_url:
        build_args += ['-B']
    process = subprocess.run(['sphinx-autobuild'] + build_args)
    if process.returncode:
        sys.exit(process.returncode)


if __name__ == '__main__':
    sys.exit(cli() or 0)
