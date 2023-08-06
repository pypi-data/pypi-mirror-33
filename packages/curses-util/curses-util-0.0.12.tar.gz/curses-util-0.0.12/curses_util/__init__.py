import pkgutil, inspect

# Makes the package a 'meta module' which includes all classes defined in all modules
# contained within. There is probably a more pythonic way to do this :/.

for loader, name,_ in pkgutil.walk_packages(__path__):
    for name, obj in vars(loader.find_module(name).load_module(name)).items():
        if inspect.isclass(obj):
            globals().update({name: obj})
