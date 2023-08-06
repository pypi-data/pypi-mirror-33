Editorium
=========

Eᴅɪᴛᴏʀɪᴜᴍ creates Qᴛ editors for objects or functions via reflection.

Object fields or method parameters are reflected and an editor generated for each field or parameter.
For instance an `int` field is generated as a `QSpinBox` editor.

Please see the SᴛʀɪɴɢCᴏᴇʀᴄɪᴏɴ project for the command-line equivalent.

Features
--------

* Generate editor for field/type
* Generate editors for object
* Generate editors for function call
* Read fields from object to editors
* Write fields from editors into object
* Supports custom editors and extensions

Default editors
---------------

* `int` --> `QSpinBox`
* `float` --> `QLineEdit`
* `str` --> `QLineEdit`
* `Optional` --> `QCheckBox`
* `bool` --> `QCheckBox` 
* `Enum` --> `QComboBox` (includes enum-like objects registered with SᴛʀɪɴɢCᴏᴇʀᴄɪᴏɴ)
* `Flags` --> `QCheckBox` array
* `List[T]` --> appropriate array of `T`
* `Filename` --> `QLineEdit` + `QToolButton`

### Notes

* `Optional[T]` is a _PEP-484_ annotation supplied by Pʏᴛʜᴏɴ's Tʏᴩɪɴɢ library and indicates that a value may be `None`.
* `Filename` is a _PEP-484_-style annotation provided by the MHᴇʟᴩᴇʀ library and provides hints on an acceptable filename e.g. `Filename[".txt", EMode.SAVE]`.
* The SᴛʀɪɴɢCᴏᴇʀᴄɪᴏɴ library is queried to obtain the list of options for types such as `Enum`s, so if you have registered your list providers with SᴛʀɪɴɢCᴏᴇʀᴄɪᴏɴ you will not need to do so again for Eᴅɪᴛᴏʀɪᴜᴍ.

Meta
----

```ini
language=python,python3
type=lib
host=bitbucket,pypi
```