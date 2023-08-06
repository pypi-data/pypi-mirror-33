# OCMVisualization

import os


def run_Rscript(data_path, tag, path):
    if not os.path.exists(tag):
        os.mkdir(tag)
    print(os.getcwd())
    Rscript_path = os.path.join(path, 'Rscript', 'OCM_feature.r');print(Rscript_path)
    # 运行R程序，给文件路径加上双引号，解决文件夹名含空格的问题
    os.system("""Rscript "%s" %s %s""" % (Rscript_path, data_path, tag))

