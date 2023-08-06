__author__ = 'Dmitry Gerasimenko'
__version__ = '0.0.1'


def _jupyter_nbextension_paths():
    return [dict(
        section="notebook",
        src=".",
        dest="gradelabel",
        require="gradelabel/main"
    )]
