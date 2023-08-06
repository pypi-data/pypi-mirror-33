# OrderedNamespace

Namespaces are a great idea and this one is mine.

What's the big deal?  Python dicts are just fine, but in the Jupyter/IPython interactive environment I hate having to deal with brackets and quotes when using tab-based auto-completion to get a quick glance at the contents of an object.

OrderedNamespace has been especially designed to have a minimal number of things that bug me.  More specifically, I wanted my namespace implementation to support the following functionality:

- Access data contents as dot-style attributes _or_ as dict keys
- Predictable ordering of attributes/keys
- Automatic support for tab-completion (especially within Jupyter Notebooks)
- Nesting: auto-convert supplied dict data to OrderedNamespace instances
- Nice pretty printing within Jupyter environment

Ultimately I decided to write a class from scratch and using an OrderedDict instance in place of the class' built-in `__dict__`.  This meant writing my own methods for `__setitem__`, `__getitem__`, `__getattr__` and `__setattr__`.  I also had to learn about automatic tab completion as used in Jupyter/IPython.  Overall it was more work than I originally anticipated, but it was all fun and I'm glade I did it.

Install this package with:

```bash
pip install ordered-nanmespace
```

And then use it like this:

```py
import ordered_namespace as ons
import numpy as np

data = ons.Struct()

data.X = [1, 2, 3]

data['Y'] = {'hello': 'I am not a robot',
             'yikes': 75.4}

data.Z = np.arange(35).reshape(7,5)
```

Notice above that both dict key and attribute-style techniques were used to add new information to the namespace structure.  Printing out the data contents shows nicely-formatted pretty text:

```py
>>> data

[{X: [1, 2, 3],
  Y: [{hello: 'I am not a robot', yikes: 75.4}],
  Z: array([[ 0,  1,  2,  3,  4],
         [ 5,  6,  7,  8,  9],
         [10, 11, 12, 13, 14],
         [15, 16, 17, 18, 19],
         [20, 21, 22, 23, 24],
         [25, 26, 27, 28, 29],
         [30, 31, 32, 33, 34]])}]
```


Inspiration for this class came from parts of the following projects:
- https://docs.python.org/3.6/library/types.html#types.SimpleNamespace
- https://github.com/srevenant/dictobj
- https://github.com/pcattori/namespaces
- https://github.com/pcattori/maps
- https://stackoverflow.com/questions/27941581/replacing-default-dict-for-object-with-ordereddict
- https://stackoverflow.com/questions/455059/using-an-ordered-dict-as-object-dictionary-in-python

I learned about IPython's tab-completion at this link:
- http://ipython.readthedocs.io/en/stable/config/integrating.html#tab-completion

The follwing were extremely helpful in sorting through IPython's rich-text display framework:
- http://ipython.readthedocs.io/en/stable/config/integrating.html
- https://github.com/ipython/ipython/blob/master/IPython/lib/pretty.py
- https://docs.python.org/3/library/functions.html#dir

