class PaiFlow:
    @staticmethod
    def deploy(name: str,
               model: object,
               **kwargs):
        '''发布模型
        参数:
            name: 任务名称，预测api调用时需要传入该名称
            model: 训练好的模型
        动态列表参数:
            additional_info: dict, 额外的模型信息，例如score之类的，存储到map的额外信息中，可在界面查看，默认{}
        '''
        pass
