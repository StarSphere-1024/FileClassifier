import json
import os
import shutil
import argparse
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FileClassifier:
    def __init__(self, folder_path=None, default_paths=None):
        self.will_folder = folder_path
        self.default_paths = default_paths or []  # 如果没有提供默认路径，则使用空列表

        # 获取当前脚本的目录
        script_dir = Path(__file__).resolve().parent

        # 构建配置文件的绝对路径
        config_path = script_dir / "postfix_map.json"

        # 打开文件并导入json数据
        try:
            with open(config_path, 'r', encoding='utf8') as fp:
                self.postfix_library = json.load(fp)
        except FileNotFoundError:
            logging.error(f"配置文件 {config_path} 未找到")
            raise
        except json.JSONDecodeError:
            logging.error(f"配置文件 {config_path} 格式错误")
            raise

    def postfix_matching(self, postfix_name, postfix_library):
        classname = []
        # 根据后缀名判断类型
        for postfix_key in postfix_library.keys():
            # 如果数据类型还是字典,利用递归逐层获取分类名
            if isinstance(postfix_library[postfix_key], dict):
                ret, ret_classname = self.postfix_matching(postfix_name, postfix_library[postfix_key])
                if ret:
                    classname.append(postfix_key)
                    classname.extend(ret_classname)
                    return True, classname
            # 如果数据类型为列表,即为后缀表,直接判断后缀是否在该表中,并返回分类名
            elif isinstance(postfix_library[postfix_key], list):
                if postfix_name in postfix_library[postfix_key]:
                    classname.append(postfix_key)
                    return True, classname
        # 没匹配到返回分类名为其他
        else:
            return False, ["其他"]

    def process_file(self, file_path, base_path):
        try:
            if os.path.isfile(file_path):  # 判断是否为文件
                postfix_name = file_path.suffix[1:]  # 获取文件后缀

                # 后缀名不在白名单才执行分类操作
                if postfix_name not in self.postfix_library["White list"]:
                    ret, classname = self.postfix_matching(postfix_name, self.postfix_library["Postfix"])

                    new_path = base_path
                    for name in classname:
                        new_path = new_path / name

                    if not new_path.exists():  # 判断的分类文件夹是否存在
                        new_path.mkdir(parents=True, exist_ok=True)  # 创建分类文件夹

                    if not (new_path / file_path.name).exists():
                        shutil.move(str(file_path), str(new_path))  # 移动文件到新路径
                        logging.info(f"文件 {file_path} 已移动到 {new_path}")
                    else:
                        logging.warning(f"文件 {file_path} 已存在于目标文件夹 {new_path}")
            else:
                logging.warning(f"路径 {file_path} 不是文件")
        except Exception as e:
            logging.error(f"处理文件 {file_path} 时发生错误: {e}")

    def run(self):
        if self.will_folder:
            paths_to_process = [Path(self.will_folder)] + [Path(p) for p in self.default_paths]
        else:
            paths_to_process = [Path(p) for p in self.default_paths]

        for path in paths_to_process:
            if path.is_dir():  # 检查路径是否为有效的文件夹
                file_list = os.listdir(path)  # 读取要分类文件夹内的文件
                for f in file_list:
                    file_path = path / f
                    self.process_file(file_path, path)
            else:
                logging.warning(f"路径 {path} 不是有效的文件夹")

if __name__ == "__main__":
    # 默认要分类的路径列表
    default_paths = [
        'D:/Resourses/Downloads'
    ]

    parser = argparse.ArgumentParser(description="文件分类器")
    parser.add_argument("-f", "--folder_path", type=str, help="要分类的文件夹的位置", default=None)
    parser.add_argument("-d", "--default_paths", type=str, nargs='+', help="默认要分类的文件夹路径列表", default=default_paths)
    args = parser.parse_args()

    # 如果用户没有提供文件夹路径，则使用默认路径列表
    if args.folder_path is None and not args.default_paths:
        logging.error("没有提供文件夹路径或默认路径，请确保至少提供一个路径。")
        exit(1)

    FC = FileClassifier(args.folder_path, default_paths=args.default_paths)
    FC.run()