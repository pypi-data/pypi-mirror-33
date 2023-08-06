import typing

from star_builder import Component
from apistar.http import QueryParams, RequestData

Model = typing.NewType("model", dict)


class ModelComponent(Component):
    """
    聚合参数的基类
    """

    def resolve(self, *args, **kwargs) -> object:
        return super(ModelComponent, self).resolve()

    @staticmethod
    def gather(params: QueryParams, form: RequestData) -> Model:
        total_params = dict()
        if params:
            total_params.update(params)
        if form:
            total_params.update(form)
        return Model(total_params)
