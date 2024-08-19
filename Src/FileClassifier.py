import json
import os
import shutil

class FileClassifier:
    def __init__(self, folder_path):

        self.will_folder = folder_path 

        #打开文件并导入json数据
        with open("Src/postfix_map.json",'r',encoding='utf8') as fp:
            self.postfix_library = json.load(fp)


    def postfix_matching(self,postfix_name,postfix_library):
        classname=list()
        # 根据后缀名判断类型
        for postfix_key in postfix_library.keys():
            #如果数据类型还是字典,利用递归逐层获取分类名
            if isinstance(postfix_library[postfix_key],dict):
                ret,ret_classname=self.postfix_matching(postfix_name,postfix_library[postfix_key])
                if ret:
                    classname.append(postfix_key)
                    classname.extend(ret_classname)
                    return True,classname
            #如果数据类型为列表,即为后缀表,直接判断后缀是否在该表中,并返回分类名
            elif isinstance(postfix_library[postfix_key],list):
                if postfix_name in postfix_library[postfix_key]:
                    classname.append(postfix_key)
                    return True,classname
        #没匹配到返回分类名为其他
        else:
            return False,["其他"]      


    def run(self):

        file = os.listdir(self.will_folder+ "/")  # 读取要分类文件夹内的文件

        for f in file:
            will_file = self.will_folder + "/" + f
            if os.path.isfile(will_file):  # 判断是否为文件
                postfix_name = will_file.split(".")[-1]  # 获取文件后缀

                #后缀名不在白名单才执行分类操作
                if postfix_name not in self.postfix_library["White list"]:
                    
                    ret,classname=self.postfix_matching(postfix_name,self.postfix_library["Postfix"])

                    new_path = self.will_folder
                    for name in classname:
                            new_path += "/"+ name

                    if not os.path.exists(new_path):  # 判断的分类文件夹是否存在
                        os.makedirs(new_path)# 创建分类文件夹

                    if not os.path.exists(new_path + "/" + f):
                        shutil.move(will_file, new_path)  # 移动文件到新路径

if __name__ == "__main__":
    will_folder = input("请输入要分类的文件夹位置:")
    FC=FileClassifier(will_folder)
    FC.run()
