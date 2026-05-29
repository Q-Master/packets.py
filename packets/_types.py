# -*- coding:utf-8 -*-
from typing import Union, Dict, TypeAlias, Any


DiffKeys: TypeAlias = Dict[str, Union[str, 'DiffKeys']]
#UpdateData: TypeAlias = Dict[str, Union[Any, 'UpdateData']]

class UpdateData(Dict[str, Union[Any, 'UpdateData']]):
    pass