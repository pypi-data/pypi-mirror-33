import cProfile, inspect, io, pstats, random
import django.core.exceptions
import os.path

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object

from operator import attrgetter
from pathlib import Path
from .config import MindsightConfig
from .store import SampleStore


class Middleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        self._profile = None
        self._config = MindsightConfig()

        if self._config.MINDSIGHT_AGENT_URL is None:
            raise django.core.exceptions.MiddleWareNotUsed

        if self._config.MINDSIGHT_PROJECT is None:
            raise django.core.exceptions.MiddleWareNotUsed

        if self._config.MINDSIGHT_SAMPLE_PROBABILITY < 0.0:
            raise django.core.exceptions.MiddleWareNotUsed

        self._store = SampleStore(
            self._config.MINDSIGHT_AGENT_URL,
            self._config.MINDSIGHT_PROJECT,
            self._config.MINDSIGHT_ENVIRONMENT,
            send_after=self._config.MINDSIGHT_SEND_AFTER,
            send_timeout=self._config.MINDSIGHT_SEND_TIMEOUT)

        if MiddlewareMixin is not object:
            super(Middleware, self).__init__(get_response)


    def _must_profile(self):
        if self._config.MINDSIGHT_SAMPLE_PROBABILITY >= 1.0:
            return True
        elif random.random() < self._config.MINDSIGHT_SAMPLE_PROBABILITY:
            return True

        return False

    
    def _in_project(self, root, stat):
        return inspect.iscode(stat.code) and \
            root in Path(stat.code.co_filename).absolute().parents


    def _full_fn_name(self, stat):
        p = Path(stat.code.co_filename).absolute()
        rel = p.relative_to(self._config.MINDSIGHT_ROOT)
        rel_no_ext = os.path.splitext(str(rel))[0]
        return rel_no_ext.replace('/', '.') + '.' + stat.code.co_name


    def _process_profile(self, profile):
        root = Path(self._config.MINDSIGHT_ROOT)

        all_stats = sorted(profile.getstats(), key=attrgetter('totaltime'), reverse=True)
        stats = [s for s in all_stats if self._in_project(root, s)]

        for stat in stats:
            fn_name = self._full_fn_name(stat)
            ncalls = int(stat.totaltime / self._config.MINDSIGHT_SAMPLE_INTERVAL)

            if ncalls <= 0:
                ncalls = 1

            self._store.record(fn_name, ncalls=ncalls)


    def process_request(self, request):
        if not self._must_profile():
            return None

        self._profile = cProfile.Profile()
        self._profile.enable()
        return None


    def process_response(self, request, response):
        if self._profile is None:
            return response

        self._profile.disable()
        prof = self._profile
        self._profile = None
        self._process_profile(prof)
        return response
