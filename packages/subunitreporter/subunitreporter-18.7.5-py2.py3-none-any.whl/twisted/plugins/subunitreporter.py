# Copyright Least Authority TFA GmbH
# See LICENSE for details.

from __future__ import (
    division,
    absolute_import,
    print_function,
    unicode_literals,
)

from zope.interface import implementer

from twisted.trial.itrial import IReporter
from twisted.plugin import IPlugin

@implementer(IPlugin, IReporter)
class _Reporter(object):
    def __init__(self, name, module, description, longOpt, shortOpt, klass):
        self.name = name
        self.module = module
        self.description = description
        self.longOpt = longOpt
        self.shortOpt = shortOpt
        self.klass = klass


subunitv2 = _Reporter(
    "Subunit v2 Reporter",
    "subunitreporter",
    description="subunit v2 stream output",
    longOpt="subunitv2",
    shortOpt=None,
    klass="reporter",
)

subunitv2_b64 = _Reporter(
    "Subunit v2 (Base64 encoded) Reporter",
    "subunitreporter",
    description="base64-encoded subunit v2 stream output",
    longOpt="subunitv2-b64",
    shortOpt=None,
    klass="reporter_b64",
)

subunitv2_file = _Reporter(
    "Subunit v2 Reporter",
    "subunitreporter",
    description="subunit v2 output to $SUBUNITREPORTER_OUTPUT_PATH",
    longOpt="subunitv2-file",
    shortOpt=None,
    klass="reporter_file",
)
