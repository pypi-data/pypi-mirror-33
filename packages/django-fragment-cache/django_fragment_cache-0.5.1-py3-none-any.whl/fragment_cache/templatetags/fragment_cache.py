from django import template
from django.template import (
    Library, Node, TemplateSyntaxError, VariableDoesNotExist,
)
from django.core.cache import cache
from django.templatetags.cache import CacheNode
from django.core.cache import InvalidCacheBackendError, caches
from django.core.cache.utils import make_template_fragment_key

register = template.Library()


class UserCacheNode(Node):
    """
    Elegant custom template fragment caching
    """
    def __init__(self, nodelist, expire_time_var, fragment_name, vary_on, cache_name):
        self.nodelist = nodelist
        self.expire_time_var = expire_time_var
        self.fragment_name = fragment_name
        self.vary_on = vary_on
        self.cache_name = cache_name

    def render(self, context:dict):
        try:
            expire_time = self.expire_time_var.resolve(context)
        except VariableDoesNotExist:
            raise TemplateSyntaxError('"cache" tag got an unknown variable: %r' % self.expire_time_var.var)
        if expire_time is not None:
            try:
                expire_time = int(expire_time)
            except (ValueError, TypeError):
                raise TemplateSyntaxError('"cache" tag got a non-integer timeout value: %r' % expire_time)
        if self.cache_name:
            try:
                cache_name = self.cache_name.resolve(context)
            except VariableDoesNotExist:
                raise TemplateSyntaxError('"cache" tag got an unknown variable: %r' % self.cache_name.var)
            try:
                fragment_cache = caches[cache_name]
            except InvalidCacheBackendError:
                raise TemplateSyntaxError('Invalid cache name specified for cache tag: %r' % cache_name)
        else:
            try:
                fragment_cache = caches['template_fragments']
            except InvalidCacheBackendError:
                fragment_cache = caches['default']

        vary_on = [var.resolve(context) for var in self.vary_on]
        cache_key = make_template_fragment_key(self.fragment_name, vary_on)
        value = fragment_cache.get(cache_key)
        if value is None:
            fragment_var = context.get(self.fragment_name)
            if callable(fragment_var):
                extra = fragment_var(*vary_on)
                if type(extra) is dict:
                    context.update(extra)
            value = self.nodelist.render(context)
            fragment_cache.set(cache_key, value, expire_time)
        return value

@register.tag('fragment_cache')
def fragment_cache(parser, token):
    nodelist = parser.parse(('endfragment_cache',))
    parser.delete_first_token()
    tokens = token.split_contents()
    if len(tokens) < 3:
        raise TemplateSyntaxError("'%r' tag requires at least 2 arguments." % tokens[0])
    if len(tokens) > 3 and tokens[-1].startswith('using='):
        cache_name = parser.compile_filter(tokens[-1][len('using='):])
        tokens = tokens[:-1]
    else:
        cache_name = None

    return UserCacheNode(
        nodelist, parser.compile_filter(tokens[1]),
        tokens[2],  # fragment_name can't be a variable.
        [parser.compile_filter(t) for t in tokens[3:]],
        cache_name,
    )




