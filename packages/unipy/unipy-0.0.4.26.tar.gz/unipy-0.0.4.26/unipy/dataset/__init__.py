"""Datasets.

This module offers you well-known datasets.

api
---
- `init` -- Unzip datasets.
- `reset` -- Re-unzip datasets.
- `ls` -- List-up datasets.
- `load` -- Load a dataset.

"""


from unipy.dataset import api

from unipy.dataset.api import *

__all__ = []
__all__ += api.__all__
