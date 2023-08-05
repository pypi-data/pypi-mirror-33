from .files import (file_Core,
                    file_Tsv,
                    file_Json,
                    )
from .directories import (dir_Root,
                          dir_Subject,
                          )
from .objects import (Task,
                      Electrodes,
                      iEEG,
                      )
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'VERSION')) as f:
    __version__ = f.read().strip()
