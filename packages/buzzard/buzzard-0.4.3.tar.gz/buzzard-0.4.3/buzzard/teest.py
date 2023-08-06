
import buzzard as buzz
import shapely.geometry as sg
import numpy as np
from pprint import pprint
import cloudpickle
import weakref
import functools

# def ensure_activated_iteration(f):
#     @functools.wraps(f)
#     def g(that, *args, **kwargs):
#         that.activate()
#         activated = True

#         def _cb(_):
#             if activated:
#                 that.deactivate()

#         it = f(that, *args, **kwargs)
#         weak_it = weakref.ref(it, _cb)

#         for v in it:
#             yield v

#         that.deactivate()
#         activated = False
#     return g

def ensure_activated_iteration(f):
    @functools.wraps(f)
    def g(that, *args, **kwargs):
        that.activate()
        try:
            it = f(that, *args, **kwargs)
            for v in it:
                yield v
        finally:
            that.deactivate()
    return g

class TheClass(object):

    def activate(self):
        print('Activate!!!')

    def deactivate(self):
        print('Deactivate!!!')

    @ensure_activated_iteration
    def awesome_generator(self):
        for i in range(1, 5):
            yield i * 42

inst = TheClass()

print('Test 1 **************************************************')
for i in inst.awesome_generator():
    print(i)
print('/////////////////////////////////////////////////////////')

print('Test 2 **************************************************')
for i in inst.awesome_generator():
    print(i)
    if i == 42:
        break
print('/////////////////////////////////////////////////////////')

def h():
    print('Test 3 **************************************************')
    it = inst.awesome_generator()
    print(next(it))
    print(next(it))
    print('/////////////////////////////////////////////////////////')
h()

def h():
    print('Test 4 **************************************************')
    it1 = inst.awesome_generator()
    print(next(it1))
    it2 = inst.awesome_generator()
    print(next(it2))
    print('/////////////////////////////////////////////////////////')
h()



exit()

ds = buzz.DataSource()
print(ds)


# p = '/media/ngoguey/Donnees/ngoguey/evaluations/Budillon_Rabatel-Izeaux-20170622/recrefine1_epoch194_overlap0/top1.tif'
# r = ds.open_araster(p)

p = '/media/ngoguey/4b16cd43-a81f-4aef-b59e-6de3120df13b/more_quarry/Calcaire_biterrois-Galiberte-20170628/data_bounds.shp'
r = ds.open_avector(p)


print()
print('Constructions 1 ******************************************************************************************************************************************************')
c = r.__class__._Constants(
    ds,
    open_options=[],
    mode=r.mode,
    gdal_ds=r._gdal_ds,
    lyr=r._lyr,
)

print(c)
print('deactivable', c.deactivable)
pprint(c.__dict__)
d1 = c.__dict__

print()
print('Constructions 2 ******************************************************************************************************************************************************')
c = cloudpickle.dumps(c)
c = cloudpickle.loads(c)

c = r.__class__._Constants(
    ds,
    **c.__dict__,
)
print(c)
print('deactivable', c.deactivable)
pprint(c.__dict__)
d2 = c.__dict__

print('**********************************************************************************************************************************')
assert d1 == d2
