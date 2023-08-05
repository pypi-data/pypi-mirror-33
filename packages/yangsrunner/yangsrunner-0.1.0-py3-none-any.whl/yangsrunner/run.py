from argparse import ArgumentParser
from yangsutil import FileUtil
import os


def make_folder(path):
    if os.path.isdir(path) is False:
        os.makedirs(path)


def make_file(path, contents=None):
    if os.path.isfile(path) is False:
        f = open(path, 'w')

        if contents is not None:
            for content in contents:
                f.write(content + '\n')
        f.close()


def make_init_project(project_name):
    # project folder
    FileUtil.make_folder(file_path='%s/test.txt' % os.path.join(project_name, 'apps'))

    # main.py
    FileUtil.save_file(
        file_path=os.path.join(project_name, 'main.py'),
        string_contents="""from yangsrunner import SimpleExecutor


class Main(SimpleExecutor):

    def __init__(self):
        SimpleExecutor.__init__(self, setting_file='setting.yml')
        

if __name__ == '__main__':
    Main().start()
""",
    )

    # setting.yml
    FileUtil.save_file(
        file_path=os.path.join(project_name, 'setting.yml'),
        string_contents="""#######
# app #
#######
app_root: apps
app_name: %s
""" % project_name
    )

    # .gitignore
    FileUtil.save_file(
        file_path=os.path.join(project_name, '.gitignore'),
        string_contents="""# directories
venv.dir/
.idea/
log/
csv/
credentials/

# files
*.pyc
*.whl
client_secret.json
setting.yml        
"""
    )

    # requirements.txt
    FileUtil.save_file(
        file_path=os.path.join(project_name, 'requirements.txt'),
        string_contents=''
    )

    # README.md
    FileUtil.save_file(
        file_path=os.path.join(project_name, 'README.md'),
        string_contents="# %s" % project_name.capitalize()
    )


# starter
def main():
    parser = ArgumentParser()
    parser.add_argument('instruction', help='"startproject" [name]', nargs=2)
    user_input = parser.parse_args()

    # parsing
    inst_list = user_input.instruction
    if inst_list[0].lower() == 'startproject':
        project_name = inst_list[1]
        make_init_project(project_name=project_name)

    else:
        print("Not found instruction ...")
