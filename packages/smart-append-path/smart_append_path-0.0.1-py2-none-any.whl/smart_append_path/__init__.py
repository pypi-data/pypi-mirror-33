name = "smart_append_path"

def join_path(source_file,ref_path):
    from os.path import dirname, abspath
    project_root = (dirname(abspath(source_file))) + '/' + ref_path
    return abspath(project_root)

def append(source_path,ref_path):
    path = join_path(source_path,ref_path)
    from sys import path as syspath
    from os.path import abspath
    for v in syspath:
        if abspath(v) == path:
            return
    syspath.insert(0,path)

def append_top1(source_path):
    return append(source_path,'..')

def append_top2(source_path):
    return append(source_path,'../..')

def append_top3(source_path):
    return append(source_path,'../../..')