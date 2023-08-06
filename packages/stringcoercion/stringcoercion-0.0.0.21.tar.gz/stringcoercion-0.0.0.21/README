String Coercion
===============

SᴛʀɪɴɢCᴏᴇʀᴄɪᴏɴ interprets values typed into the console (or similar text-input) as fields for objects or parameters for functions via [PEP-484](https://www.python.org/dev/peps/pep-0484/) style reflection.

Object fields or method parameters are reflected and an interpreter generated for each field or parameter.
For instance an `int` field is simply interpreted using `int(text)`.

Please see the Eᴅɪᴛᴏʀɪᴜᴍ project for the GUI equivalent. 

Default interpreters
--------------------

* `int`
* `str`
* `Optional`
* `bool` 
* `Enum`
* `Flags`
* `List` or `Tuple`
* `Password`

### Notes

* `Optional[T]` is a _PEP-484_ annotation supplied by Pʏᴛʜᴏɴ's Tʏᴩɪɴɢ library and indicates that a value may be `None`.
* `Filename` is a _PEP-484_-style annotation provided by the MHᴇʟᴩᴇʀ library and provides hints on an acceptable filename e.g. `Filename[".txt", EMode.SAVE]`.

Meta
----

```ini
type=library
language=python3
host=bitbucket,pypi
```