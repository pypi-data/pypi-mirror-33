# -*- coding: utf8 -*-
from self_update.sdk_version import get_version

package = 'mali'


def get_mali_version():
    return get_version(package)


def get_mali_package():
    return package
