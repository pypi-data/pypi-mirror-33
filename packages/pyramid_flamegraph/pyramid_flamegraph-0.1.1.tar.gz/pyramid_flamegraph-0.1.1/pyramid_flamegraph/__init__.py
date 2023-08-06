# -*- coding: utf-8 -*-
import collections
import logging
import signal

from . import flamegraphwrap

log = logging.getLogger(__name__)


def flamegraph_config_from_settings(settings, prefix='flamegraph.'):
    config = {}
    config['interval'] = settings.pop('flamegraph.interval', 0.001)
    config['color'] = settings.pop('flamegraph.color', 'hot')
    return config


class Tween(object):

    def __init__(self, handler, settings):
        self.handler = handler
        self.config = flamegraph_config_from_settings(settings)

    def __call__(self, request):
        with Sampler(request, self.config):
            return self.handler(request)


class Sampler(object):

    def __init__(self, request, config):
        self.svg_filename = './flamegraph{}.svg'.format(request.path.replace('/', '.'))
        title = "request: {} [{}]".format(request.url, request.method)
        self.stack_counts = collections.defaultdict(int)
        self.interval = config['interval']
        self.flamegraph_option = {'color': config['color'], 'title': title}

    def _sample(self, signum, frame):
        stack = []
        while frame is not None:
            formatted_frame = '{}({})'.format(frame.f_code.co_name,
                                              frame.f_globals.get('__name__'))
            stack.append(formatted_frame)
            frame = frame.f_back

        formatted_stack = ';'.join(reversed(stack))
        self.stack_counts[formatted_stack] += 1

    def get_stats(self):
        return '\n'.join('%s %d' % (key, value) for key, value in sorted(self.stack_counts.items()))

    def __enter__(self):
        signal.signal(signal.SIGALRM, self._sample)
        signal.setitimer(signal.ITIMER_REAL, self.interval, self.interval)

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            return True
        signal.setitimer(signal.ITIMER_REAL, 0, 0)
        with open(self.svg_filename, 'w') as svg:
            svg.write(flamegraphwrap.stats_to_svg(self.get_stats(), self.flamegraph_option))


def tween_factory(handler, registry):
    return Tween(handler, registry.settings.copy())


def includeme(config):
    config.add_tween('pyramid_flamegraph.tween_factory')
