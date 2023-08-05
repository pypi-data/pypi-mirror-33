from yangsrunner.common.utils import is_file_exist
from yangsutil import FileUtil, LogUtil, ObjectUtil


class SimpleExecutor:

    def __init__(self, setting_file):
        self.setting_file = setting_file

    def _arguments(self):
        raise NotImplementedError('if empty "return {}" ...')

    def start(self):
        # setting
        if is_file_exist(self.setting_file) is False:
            exit(1)

        setting = FileUtil.read_yml_file(self.setting_file)

        # logger
        logger = LogUtil.get_logger(app_name=setting['app_name'])

        # arg
        args = self._arguments()

        # app
        ObjectUtil.get_class('%s.%s' % (setting['app_root'], args['app'].lower()), 'APP')(
            args=args,
            logger=logger,
            setting=setting
        ).start()
