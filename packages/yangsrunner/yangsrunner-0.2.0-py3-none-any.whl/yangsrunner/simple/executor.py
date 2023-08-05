from yangsrunner.common.utils import is_file_exist
from yangsutil import FileUtil, LogUtil, ObjectUtil


class SimpleExecutor:

    def __init__(self, setting_file):
        self.setting_file = setting_file

    def _arguments(self):
        raise NotImplementedError('IF empty "return {}", ELSE recommendation argparse ...')

    def start(self):
        # setting
        if is_file_exist(self.setting_file) is False:
            exit(1)

        setting = FileUtil.read_yml_file(self.setting_file)

        # arg
        args = self._arguments()

        # app
        try:
            app = ObjectUtil.get_class(
                module_name='%s.%s' % (setting['app_root'].replace('/', '.'), args['app'].lower()),
                class_name='APP'
            )
        except KeyError:
            print('setting.yml[app_root] or arguments[app] is missing ...')
            app = None

        # validation
        if app is None:
            app_name = '%s-none' % setting['app_name']

            logger = LogUtil.get_logger(app_name=app_name)

            logger.info('Not found "%s" application ... ' % args['app'])

        else:
            app_name = '%s-%s' % (setting['app_name'], args['app'])

            logger = LogUtil.get_logger(app_name=app_name)

            logger.info('Execute "%s" application ... ' % args['app'])

            app(args=args, logger=logger, setting=setting).start()
