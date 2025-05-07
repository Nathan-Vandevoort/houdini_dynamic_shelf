name = "dynamic_shelf"

version = "0.0.0"

requires = [
    "houdini-19.5+",
    "python-3.9+",
    "lxml-5.0+",
]

build_command = "bash {root}/build.sh {install}"

uuid = "e8b2373a44bd44d1b331fe6fcb30a64c"


def commands():
    env.PYTHONPATH.append("{root}/python")

    if 'houdini' in resolve:
        env.HOUDINI_PATH.prepend('{root}/python/dynamic_shelf/startup')
