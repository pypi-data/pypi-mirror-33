import os
import warnings
try:
    from vstutils.environment import prepare_environment, cmd_execution
except ImportError:
    warnings.warn('"vstutils" was not installed', ImportWarning)
    prepare_environment = lambda *args, **kwargs: ()
    cmd_execution = prepare_environment

default_settings = {
    # ansible specific environment variables
    "ANSIBLE_HOST_KEY_CHECKING": 'False',
    "ANSIBLE_FORCE_COLOR": "true",
    # celery specific
    "C_FORCE_ROOT": "true",
    # django settings module
    "DJANGO_SETTINGS_MODULE": os.getenv(
        "DJANGO_SETTINGS_MODULE", 'polemarch.main.settings'
    ),
    # VSTUTILS settings
    "VST_PROJECT": os.getenv("VST_PROJECT", 'polemarch'),
}

__version__ = "0.1.12"

prepare_environment(**default_settings)
