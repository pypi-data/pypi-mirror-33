class InfoModel:
    def __init__(self, uid: str):
        '''任务ID，预测api调用时需要传入该ID'''
        self.uid = uid
        '''显示的标题'''
        self.title = self.uid
        '''显示的描述'''
        self.description = self.title
        '''搜索的关键词，逗号分隔'''
        self.keyword = self.uid
        '''模型版本'''
        self.version = '1.0.0'
        '''额外的模型信息，例如score之类的，存储到map的额外信息中，可在界面查看'''
        self.additional_info = {}
