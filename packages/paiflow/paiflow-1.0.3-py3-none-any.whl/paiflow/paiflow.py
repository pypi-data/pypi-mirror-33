class PaiFlow:
    @staticmethod
    def deploy(name: str,
               model: object,
               predict_type: str,
               predict_function: object,
               **kwargs):
        '''发布模型
        参数:
            name: 任务名称，预测api调用时需要传入该名称
            model: 训练好的模型
            predict_type: 预测类型，选用哪种预置容器承载预测，例如python36-20180621
            predict_function: 预测函数，请使用predict_type中包含的模块写，如果没有，要新写一种类型
                格式: def do_predict(trained_model, to_predict):
                to_predict是一个list的list列表
        动态列表参数:
            additional_info: dict, 额外的模型信息，例如score之类的，存储到map的额外信息中，可在界面查看，默认{}
            update_now: bool, 是否立刻更新预测服务中的模型，默认True
        '''
        pass
