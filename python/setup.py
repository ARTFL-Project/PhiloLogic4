
from distutils.core import setup

setup(name = "philologic",
      version = "4.6",
      author = "The ARTFL Project",
      author_email = "artfl@artfl.uchicago.edu",
      packages = ["philologic", "philologic.runtime", "philologic.utils", "philologic.runtime.reports"],
      scripts=["scripts/philoload4"]
     )
