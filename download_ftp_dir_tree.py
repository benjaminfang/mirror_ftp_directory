#! /usr/bin/env python3

import os
import sys
import ftplib
import argparse
import re

def get_args():
    args=argparse.ArgumentParser(description='This is a ultily to mirror a directory of a ftp site.\nExample: ./download_ftp_dir_tree.py -ftp ftp.ncbi.nlm.nih.gov -remote_dir /blast/documents',epilog='any problem please contect benjaminfang.ol@outlook.com.')
    args.add_argument('-ftp',type=str,help='ftp site name or ip address.(required)',required=True)
    args.add_argument('-remote_dir',type=str,help='abselutly directory name.(required)',required=True)
    args.add_argument('-local_dir',default='./',type=str,help='directory put download files. Default is present directroy.(optional)')
    args.add_argument('-filter_re',default='.',type=str,help='a regular expression to filter file name to download.(optional)')
    args.add_argument('-download_hide',default='Y',choices=['F','T'],type=str,help='Y, download hiden file, F donnt download.default is T.(optional)')
    args.add_argument('-test',default='F',choices=['F','T'],type=str,help='if F, all file will be download, if T, all file will not be download, and just construct\ndirectory struction on local.Default is F.(optional)')

    args_in=args.parse_args()
    ftpsite=args_in.ftp
    remote_dir=args_in.remote_dir
    local_dir=args_in.local_dir
    filter_re=args_in.filter_re
    d_hide=args_in.download_hide
    test_if=args_in.test
    #print(args_in)
    return ftpsite,remote_dir,local_dir,filter_re,d_hide,test_if


def get_link_type(ftpob,link):
    link_type='dir'
    fptpwd=ftpob.pwd()
    try:
        ftpob.cwd(link)
    except:
        link_type='file'

    ftpob.cwd(fptpwd)

    return link_type


def download_dir_tree(ftpob,parent_node,dir_local,re_tmp,d_hide):
    if not os.path.exists(dir_local): os.mkdir(dir_local)
    all_child_nodes_info=ftpob.mlsd(parent_node)
    for child_node_info in all_child_nodes_info:
        child_node=child_node_info[0]
        node_type=child_node_info[1]['type']
        if child_node != '.' and child_node !='..':
            #print(child_node)
            if d_hide=='F' and child_node[0]=='.': continue
            if node_type=='OS.unix=symlink':
                node_type=get_link_type(ftpob,os.path.join(parent_node,child_node))
            if node_type=='file':
                if re_tmp.match(child_node):
                    f_out=open(os.path.join(dir_local,child_node),'wb')
                    if test_if == 'T':
                        print(os.path.join(parent_node,child_node))
                        pass
                    else:
                        print(os.path.join(parent_node,child_node))
                        ftpob.retrbinary('RETR '+os.path.join(parent_node,child_node),f_out.write)
            elif node_type=='dir':
                new_parent_node=os.path.join(parent_node,child_node)
                new_dir_local=os.path.join(dir_local,child_node)
                download_dir_tree(ftpob,new_parent_node,new_dir_local,re_tmp,d_hide)

            else:
                print('>Oh no,exception happend:',os.path.join(parent_node,child_node),file_name,file_type)
                exit()

    
def mirror_directroy(ftpob,remote_dir,local_dir,filter_re,d_hide,test_if):
    dirname=os.path.dirname(remote_dir)
    basename=os.path.basename(remote_dir)

    init_file_type=[item[1]['type'] for item in ftpob.mlsd(dirname) if item[0]==basename][0]
    #print(init_file_type)
    if init_file_type == 'OS.unix=symlink':
        init_file_type=get_link_type(ftpob,remote_dir)

    if init_file_type == 'file':
        f_out=open(os.path.join(local_dir,basename),'wb')
        ftpob.retrbinary('RETR '+remote_dir,f_out.write)
    else:
        dir_local=os.path.join(local_dir,basename)
        re_tmp=re.compile(filter_re)
        download_dir_tree(ftpob,remote_dir,dir_local,re_tmp,d_hide)
        



#------------------------------------------------------------------
ftpsite,remote_dir,local_dir,filter_re,d_hide,test_if=get_args()
with ftplib.FTP() as ftpob:
    ftpob.connect(ftpsite)
    ftpob.login()
    mirror_directroy(ftpob,remote_dir,local_dir,filter_re,d_hide,test_if)
    ftpob.quit()
    print('All done, byby...')






