import abc
import dataclasses


class Base(abc.ABC): ...


@dataclasses.dataclass
class Script(Base):
    scriptType: str = 'python'
    body: str = ''


@dataclasses.dataclass
class HelpText(Base):
    body: str = ''


@dataclasses.dataclass
class HelpURL(Base):
    body: str = ''


@dataclasses.dataclass
class Tool(Base):
    name: str
    label: str
    icon: str
    helpText: HelpText = None
    helpURL: HelpURL = None
    script: Script = None
