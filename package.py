name = "dynamic_shelf"

version = "0.0.0"

requires = [
    "houdini-19.5+",
    "python-3.9+",
    "lxml-5.0+",
]

build_command = "bash {root}/build.sh {install}"

uuid = "4541732180ac434fa55e228ac7817f14"


def commands():
    env.PYTHONPATH.append("{root}/python")

    if 'houdini' in resolve:
        env.HOUDINI_PATH.prepend('{root}/python/dynamic_shelf/startup')
