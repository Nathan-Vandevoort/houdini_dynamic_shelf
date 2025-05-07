# Houdini Dynamic Shelves

Dynamic shelf creation tool. Intended to be used as a standalone module or rez package.


## Usage

### Standalone Package:

```
from dynamic_shelf import ShelfManager
import hou

shelf_manager = ShelfManager()

shelf_manager.register_shelf_item('/path/to/shelf/file/01')
shelf_manager.register_shelf_item('/path/to/shelf/file/02')
shelf_manager.register_shelf_item('/path/to/shelf/file/03')

# Writes the shelf file to the users temp directory
shelf_path = shelf_manager.write_shelf()

# Write the shelf file to a specified location
shelf_path = shelf_manager.write_shelf(save_path='/path/to/write/shelf/file.shelf')

hou.shelves.loadFile(shelf_path)

```

### Rez Package:

The ShelfManager will look through every directory on the HOUDINI_DYNAMIC_SHELVES_PATH for .shelf files and attempt
to composite them into a single .shelf file. This happens when ShelfManager.write_shelf() is called. 

The dynamic_shelf/startup/python.x.ylibs/uiready.py file  


## Installation

To build locally:
```shell
rez-build -i
```

To release:
```shell
semantic-release version && rez-release
```
