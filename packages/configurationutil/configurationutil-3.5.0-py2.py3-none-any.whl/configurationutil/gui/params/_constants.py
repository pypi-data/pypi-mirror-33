# encoding: utf-8

import attr


@attr.s(frozen=True)
class _ParamsUITypesConstant(object):
    dict = attr.ib(default=u'dict', init=False)
    list = attr.ib(default=u'list', init=False)


ParamsUITypesConstant = _ParamsUITypesConstant()
