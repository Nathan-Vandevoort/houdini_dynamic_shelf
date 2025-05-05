import dataclasses
import inspect
import logging
import os
import tempfile

from lxml import etree as ET

from .data import Tool, Base
from .constants import SEARCH_VAR, TEMP_DIR_NAME

logger = logging.getLogger(__name__)


class ShelfManager:

    def __init__(self) -> None:
        self.shelf_file_paths = self._get_shelf_files_from_env()
        self.tool_shelves: dict[str, dict[str, Tool]] = {}
        self.shelf_labels: dict[str, str] = {}

    def register_item(self, path: str) -> None:
        if not os.path.isfile(path):
            logger.warning(f'Shelf file does not exist.')
            logger.debug(f'{path=}')
            return

        if not path.endswith('.shelf'):
            logger.warning(f'File is not a .shelf file.')
            logger.debug(f'{path=}')
            return

        self.shelf_file_paths.append(path)

    def write_shelf(self, save_path: str | None = None) -> str:
        self._build_shelf()

        if not save_path:
            temp_dir = tempfile.gettempdir()
            tempfile.tempdir = os.path.join(temp_dir, TEMP_DIR_NAME)

            if not os.path.isdir(tempfile.tempdir):
                os.makedirs(tempfile.tempdir)

            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.shelf')
            save_path = temp_file.name
            temp_file.close()

        root = ET.Element('shelfDocument')
        created_tool_names = []
        for shelf_name in self.tool_shelves:

            # Create tools.
            for tool_name in self.tool_shelves[shelf_name]:

                # Skip already created tools.
                if tool_name in created_tool_names:
                    continue

                tool = self.tool_shelves[shelf_name][tool_name]
                attributes = {
                    'name': tool.name,
                    'label': tool.label,
                    'icon': tool.icon,
                }
                new_tool = ET.SubElement(root, 'tool', attrib=attributes)

                script_attributes = {'scriptType': tool.script.scriptType}
                new_script = ET.SubElement(new_tool, 'script', attrib=script_attributes)
                new_script.text = ET.CDATA(tool.script.body)

                created_tool_names.append(tool_name)

            # Create shelf.
            shelf_label = self.shelf_labels.get(shelf_name)
            if not shelf_label:
                shelf_label = shelf_name.title()
            shelf_attributes = {'name': shelf_name, 'label': shelf_label}
            tool_shelf = ET.SubElement(root, 'toolshelf', attrib=shelf_attributes)
            for shelf_tool_name in tuple(self.tool_shelves[shelf_name]):
                ET.SubElement(
                    tool_shelf, 'memberTool', attrib={'name': shelf_tool_name}
                )

        tree = ET.ElementTree(root)
        tree.write(save_path, encoding='utf-8', xml_declaration=True, pretty_print=True)

        return save_path

    def _build_shelf(self) -> None:
        logger.debug(f'building shelf...')
        for path in self.shelf_file_paths:
            # HACK: the way shelf_labels are implemented here is really gross. Maybe do it better?
            tool_elements, shelf_labels = get_tool_elements_from_shelf_file(path)
            new_tools = elements_to_tools(tool_elements)

            for tool_shelf in new_tools:
                if existing_tools := self.tool_shelves.get(tool_shelf):
                    existing_tools.update(new_tools[tool_shelf])
                else:
                    self.tool_shelves[tool_shelf] = new_tools[tool_shelf]
            self.shelf_labels.update(shelf_labels)

    @staticmethod
    def _get_shelf_files_from_env() -> list[str]:
        """
        Get every file which ends in .shelf in the SEARCH_VAR path environment variable.
        """

        search_paths = os.getenv(SEARCH_VAR)
        if not search_paths:
            return []

        paths = search_paths.split(os.pathsep)
        shelf_file_paths = []
        for path in paths:
            shelf_files = [
                os.path.join(path, file)
                for file in os.listdir(path)
                if file.endswith('.shelf')
            ]
            shelf_file_paths.extend(shelf_files)

        return shelf_file_paths


def get_tool_elements_from_shelf_file(
    path: str,
) -> tuple[dict[str, dict[str, ET.Element]], dict[str, str]]:
    """
    Gets all the tools from a .shelf file as xml elements.
    Automatically ensures ensures all returned tools are memberTools.

    Returns:
        {shelf_name (str): {tool_name (str): tool (ET.Element)}}
    """

    logger.info(f'Gettings tools from {path}')

    if not os.path.isfile(path):
        logger.warning(f'Failed to find .shelf file at {path}')
        return {}, {}

    if not path.endswith('.shelf'):
        logger.warning(f'Input file is not a .shelf file.')
        return {}, {}

    try:
        tree = ET.parse(path)
    except ET.ParseError as e:
        logger.warning(f'Invalid XML format in {path}')
        logger.debug(e)
        return {}, {}

    tools = tree.findall('tool')

    # Get all the member tools.
    tool_shelves = tree.findall('toolshelf')
    member_tool_data: dict[str, list[str]] = {}
    shelf_labels: dict[str, str] = {}
    for tool_shelf in tool_shelves:
        shelf_name = tool_shelf.attrib.get('name')
        if not shelf_name:
            continue

        shelf_label = tool_shelf.attrib.get('label')
        if not shelf_label:
            shelf_label = shelf_name.title()

        member_tools = tool_shelf.findall('memberTool')
        if not member_tools:
            continue

        member_tool_names = [
            name
            for member_tool in member_tools
            if (name := member_tool.attrib.get('name'))
        ]
        if existing_member_tool_names := member_tool_data.get('shelf_name'):
            existing_member_tool_names.extend(member_tool_names)
        else:
            member_tool_data[shelf_name] = member_tool_names
        shelf_labels[shelf_name] = shelf_label

    # Ensure all tools are member tools.
    filtered_tools = {}
    for tool in tools:
        tool_name = tool.attrib.get('name')
        if not tool_name:
            continue

        for tool_shelf_name in member_tool_data:
            if tool_name in member_tool_data[tool_shelf_name]:
                if existing_tools := filtered_tools.get(tool_shelf_name):
                    existing_tools[tool_name] = tool
                else:
                    filtered_tools[tool_shelf_name] = {tool_name: tool}

    return filtered_tools, shelf_labels


def elements_to_tools(
    tool_elements: dict[str, dict[str, ET.Element]],
) -> dict[str, dict[str, Tool]]:
    """
    Converts XML tool elements to a dataclass representation.

    Return:
        {shelf_name: {tool_name: Tool}}
    """

    shelves = {}
    for shelf_name in tool_elements:
        tools = {}
        for tool_name in tool_elements[shelf_name]:
            elem = tool_elements[shelf_name][tool_name]

            # Mandatory attributes
            name = elem.attrib.get('name')
            label = elem.attrib.get('label')
            icon = elem.attrib.get('icon')
            if None in (name, label, icon):
                logger.warning(f'Malformed tool.')
                logger.debug(f'{elem.attrib=}')
                continue

            logger.debug(f'Converting: {name}')
            new_tool = Tool(name, label, icon)

            # Data items.
            for item in elem:
                if hasattr(Tool, item.tag):
                    annotation = Tool.__annotations__[item.tag]

                    if inspect.isclass(annotation) and issubclass(annotation, Base):
                        new_data = annotation()
                        for field in dataclasses.fields(annotation):

                            # Get text from element.
                            if field.name == 'body':
                                setattr(new_data, 'body', item.text)
                                continue

                            data = item.attrib.get(field.name)
                            setattr(new_data, field.name, data)

                        setattr(new_tool, item.tag, new_data)
                        continue

                    data = elem.attrib.get(item.tag)
                    setattr(new_tool, item.tag, data)

            tools[tool_name] = new_tool

        if tools:
            shelves[shelf_name] = tools

    return shelves
