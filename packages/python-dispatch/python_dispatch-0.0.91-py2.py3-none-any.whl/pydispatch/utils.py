import sys
import weakref
from _weakref import ref
try:
    from _weakref import _remove_dead_weakref
except ImportError:
    def _remove_dead_weakref(o, key):
        del o[key]
import types

PY2 = sys.version_info.major == 2
if not PY2:
    basestring = str

AIO_AVAILABLE = sys.version_info >= (3, 5)

def get_method_vars(m):
    if PY2:
        f = m.im_func
        obj = m.im_self
    else:
        f = m.__func__
        obj = m.__self__
    return f, obj

class WeakMethodContainer(weakref.WeakValueDictionary):
    def keys(self):
        if PY2:
            return self.iterkeys()
        return super(WeakMethodContainer, self).keys()
    def add_method(self, m):
        if isinstance(m, types.FunctionType):
            self['function', id(m)] = m
        else:
            f, obj = get_method_vars(m)
            wrkey = (f, id(obj))
            self[wrkey] = obj
    def del_method(self, m):
        if isinstance(m, types.FunctionType):
            wrkey = ('function', id(m))
        else:
            f, obj = get_method_vars(m)
            wrkey = (f, id(obj))
        if wrkey in self:
            del self[wrkey]
    def del_instance(self, obj):
        to_remove = set()
        for wrkey, _obj in self.iter_instances():
            if obj is _obj:
                to_remove.add(wrkey)
        for wrkey in to_remove:
            del self[wrkey]
    def iter_instances(self):
        for wrkey in set(self.keys()):
            obj = self.get(wrkey)
            if obj is None:
                continue
            yield wrkey, obj
    def iter_methods(self):
        for wrkey, obj in self.iter_instances():
            f, obj_id = wrkey
            if f == 'function':
                yield self[wrkey]
            else:
                yield getattr(obj, f.__name__)

class InformativeDict(dict):
    def __delitem__(self, key):
        super(InformativeDict, self).__delitem__(key)
        self.del_callback(key)

class InformativeWVDict(weakref.WeakValueDictionary):
    def __init__(self, **kwargs):
        self.del_callback = kwargs.get('del_callback')
        weakref.WeakValueDictionary.__init__(self)
        def remove(wr, selfref=ref(self)):
            self = selfref()
            if self is not None:
                if self._iterating:
                    self._pending_removals.append(wr.key)
                else:
                    # Atomic removal is necessary since this function
                    # can be called asynchronously by the GC
                    _remove_dead_weakref(self.data, wr.key)
                    self._data_del_callback(wr.key)
        self._remove = remove
        self.data = InformativeDict()
        self.data.del_callback = self._data_del_callback
    def _data_del_callback(self, key):
        self.del_callback(key)

class EmissionHoldLock_(object):
    def __init__(self, event_instance):
        self.event_instance = event_instance
        self.last_event = None
        self.held = False
    def acquire(self):
        if self.held:
            return
        self.held = True
        self.last_event = None
    def release(self):
        if not self.held:
            return
        if self.last_event is not None:
            args, kwargs = self.last_event
            self.last_event = None
            self.held = False
            self.event_instance(*args, **kwargs)
    def __enter__(self):
        self.acquire()
        return self
    def __exit__(self, *args):
        self.release()

if AIO_AVAILABLE:
    from pydispatch.aioutils import AioEmissionHoldLock
    class EmissionHoldLock(EmissionHoldLock_, AioEmissionHoldLock):
        pass
else:
    EmissionHoldLock = EmissionHoldLock_
