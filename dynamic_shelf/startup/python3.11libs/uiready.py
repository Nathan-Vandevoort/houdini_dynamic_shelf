import logging

from dynamic_shelf import ShelfManager
import hou


logger = logging.getLogger(__name__)


def create_shelves() -> None:
    manager = ShelfManager()
    shelf_file = manager.write_shelf()
    hou.shelves.loadFile(shelf_file)


create_shelves()
