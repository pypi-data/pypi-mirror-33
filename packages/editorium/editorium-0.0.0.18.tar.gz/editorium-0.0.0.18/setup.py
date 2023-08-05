from distutils.core import setup


setup( name = "editorium",
       url = "https://bitbucket.org/mjr129/editorium",
       version = "0.0.0.18",
       description = "Creates a Qt Editor for arbitrary Python Objects using Reflection.",
       author = "Martin Rusilowicz",
       license = "https://www.gnu.org/licenses/agpl-3.0.html",
       packages = ["editorium",
                   "editorium.controls"],
       python_requires = ">=3.6",
       install_requires = ["py-flags",
                           "sip",
                           "PyQt5",
                           "mhelper",
                           "stringcoercion"],
       )
