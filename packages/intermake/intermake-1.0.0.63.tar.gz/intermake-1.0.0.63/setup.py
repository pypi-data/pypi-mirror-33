"""
Intermake setup.
"""
from distutils.core import setup


setup( name = "intermake",
       version = "1.0.0.63",
       description = "Automated run-time generation of user interfaces from Python code - command-line-args, CLI, python-interactive, python-scripted, graphical (Qt GUI)",
       author = "Martin Rusilowicz",
       license = "https://www.gnu.org/licenses/agpl-3.0.html",
       url = "https://bitbucket.org/mjr129/intermake",
       python_requires = ">=3.6",
       package_data = { "": ["*.css"] },
       packages = ["intermake",
                   "intermake.datastore",
                   "intermake.engine",
                   "intermake.helpers",
                   "intermake.hosts",
                   "intermake.hosts.frontends",
                   "intermake.commands",
                   "intermake.visualisables",
                   "intermake_qt",
                   "intermake_qt.host",
                   "intermake_qt.forms",
                   "intermake_qt.forms",
                   "intermake_qt.forms.designer",
                   "intermake_qt.forms.designer.resource_files",
                   "intermake_qt.utilities",
                   "intermake_qt.views"
                   ],
       install_requires = ["colorama",
                           "stringcoercion",
                           "editorium",
                           "py-flags",
                           "mhelper",
                           "PyQt5"],
       entry_points = { "console_scripts": ["intermake = intermake.__main__:main"] },
       )
