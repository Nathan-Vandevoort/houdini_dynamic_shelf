import os
import logging
from dynamic_shelf import core
from dynamic_shelf import constants

logger = logging.getLogger(__name__)

raw_paths = (
    'data/item01/item_01.shelf',
    'data/item02/item_02.shelf',
    'data/item03/item_03.shelf',
    'data/item04/item_04.shelf',
)

dirname = os.path.dirname(__file__)
paths = [os.path.normpath(os.path.join(dirname, path)) for path in raw_paths]


def get_tools_from_shelf_file():

    for path in paths:
        core.get_tool_elements_from_shelf_file(path)


def test_xml_to_tool():
    tools = []
    for path in paths:
        elements = core.get_tool_elements_from_shelf_file(path)
        tools.extend(core.elements_to_tools(elements))

    logger.debug(tools)


def test_build_shelf():

    os.environ[constants.SEARCH_VAR] = os.pathsep.join(
        (os.path.dirname(paths[1]), os.path.dirname(paths[2]))
    )

    logger.info(f'{os.getenv(constants.SEARCH_VAR)}')

    manager = core.ShelfManager()
    manager.register_shelf_file(paths[0])
    manager.register_shelf_file(paths[3])
    manager._build_shelf()


def test_write_shelf():

    # os.environ[constants.SEARCH_VAR] = os.pathsep.join(
    #     (os.path.dirname(paths[1]), os.path.dirname(paths[2]))
    # )

    logger.info(f'{os.getenv(constants.SEARCH_VAR)}')

    manager = core.ShelfManager()
    manager.register_shelf_file(paths[0])
    manager.register_shelf_file(paths[3])
    shelf_path = manager.write_shelf()
    logger.debug(f'{shelf_path.replace('\\', '/')=}')

    test_shelf_path = os.path.join(
        os.path.dirname(__file__), 'reference_files', 'reference.shelf'
    )

    with open(shelf_path, 'r') as w:
        written_data = w.read()

    with open(test_shelf_path, 'r') as w:
        reference_data = w.read()

    assert written_data == reference_data, logger.error(written_data)

    logger.info(f'{shelf_path=}')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    test_write_shelf()
