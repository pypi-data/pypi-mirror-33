# Configuration file for the Sphinx documentation builder.
#
{% if generated_text -%}
# {{ generated_text }}
# Make changes to ``project.toml``, and run ``flinx generate``.
{%- else -%}
# This file contains only the most common options. For a full list
# see the `Sphinx documentation <http://www.sphinx-doc.org/en/master/config>`.
{%- endif %}

import sys
{% if '.md' in source_suffix %}
from recommonmark.parser import CommonMarkParser
{% endif %}

sys.path.insert(0, '{{ module_path }}')

project = '{{ project }}'
copyright = {{ copyright | repr }}
author = '{{ author }}'
version = '{{ version }}'
release = '{{ version }}'

master_doc = '{{ master_basename }}'
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
source_suffix = {{ source_suffix }}

{% if '.md' in source_suffix %}
source_parsers = { '.md': CommonMarkParser }
{% endif %}

{%- if 'sphinx.ext.intersphinx' in extensions %}
intersphinx_mapping = {'https://docs.python.org/': None}
{%- endif %}

{% for k, v in config %}
{{ k }} = {{ v | repr }}
{% endfor %}
