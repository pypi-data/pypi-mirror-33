# {# pkglts, base
{% if base.namespace_method == 'P3.3>' -%}
__path__ = __import__('pkgutil').extend_path(__path__, __name__)
{%- endif -%}
{% if base.namespace_method == 'pkg_util' -%}
__path__ = __import__('pkgutil').extend_path(__path__, __name__)
{%- endif -%}
{% if base.namespace_method == 'setuptools' -%}
__import__('pkg_resources').declare_namespace(__name__)
{%- endif %}
# #}
