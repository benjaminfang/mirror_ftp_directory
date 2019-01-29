#! /usr/bin/env python3

import os
import ftplib
import argparse
import re
#-------------------------------------------------------------------------------
def get_args():
    args=argparse.ArgumentParser(description='This is a ultily to mirror a directory of a ftp site.\nExample: ./download_ftp_dir_tree.py -ftp ftp.ncbi.nlm.nih.gov -remote_dir /blast/documents',epilog='any problem please contect benjaminfang.ol@outlook.com.')
    args.add_argument('-ftp',type=str,help='ftp site name or ip address.(required)',required=True)
    args.add_argument('-remote_node',type=str,help='abselutly directory name.(required)',required=True)
    args.add_argument('-local_dir',default='./',type=str,help='directory put download files. Default is present directroy.(optional)')
    args.add_argument('-filter_re',default=None,type=str,help='a regular expression to filter file name to download.(optional)')
    args.add_argument('-filter_dp',default=0,type=int,help='directory depth to be filted with regular expression.(optional)')
    args.add_argument('-download_hide',default='F',choices=['F','T'],type=str,help='T, download hiden file, F donnt download.default is F.(optional)')
    args.add_argument('-test',default='F',choices=['F','T'],type=str,help='if F, all file will be download, if T, all file will not be download, and just construct\ndirectory struction on local.Default is F.(optional)')

    args_in=args.parse_args()
    ftpsite=args_in.ftp
    remote_node=args_in.remote_node
    local_dir=args_in.local_dir
    filter_re=args_in.filter_re
    filter_dp=args_in.filter_dp
    d_hide=args_in.download_hide
    test_if=args_in.test
    #print(args_in)
    return ftpsite,remote_node,local_dir,filter_re,filter_dp,d_hide,test_if
#-------------------------------------------------------------------------------
def get_link_type(ftpob,link):
    link_type='dir'
    fptpwd=ftpob.pwd()
    try:
        ftpob.cwd(link)
    except:
        link_type='file'

    ftpob.cwd(fptpwd)

    return link_type
#-------------------------------------------------------------------------------
def judge_root_node_type(ftpob,remote_dir):
    dirname=os.path.dirname(remote_dir)
    basename=os.path.basename(remote_dir)

    root_node_type=[item[1]['type'] for item in ftpob.mlsd(dirname) if item[0]==basename][0]
    #print(init_file_type)
    if root_node_type == 'OS.unix=symlink':
        root_node_type=get_link_type(ftpob,remote_dir)

    return root_node_type
#-------------------------------------------------------------------------------
def download_dir_tree(ftpob,node_path,local_dir,filter_re,filter_dp,d_hide,test_if,current_dp,node_type='dir'):
    if not os.path.exists(local_dir): os.mkdir(local_dir)
    node_name=os.path.basename(node_path)
    if node_type == 'file':
        if filter_re and filter_dp==current_dp:
            re_tmp=re.compile(filter_re)
            if re_tmp.search(node_name):
                if d_hide =='F' and node_name[0]!='.':
                    local_file=os.path.join(local_dir,node_name)
                    print(node_path)
                    if test_if == 'T':
                        f_out=open(local_file,'wb')
                    elif test_if == 'F':
                        f_out=open(local_file,'wb')
                        ftpob.retrbinary('RETR '+node_path,f_out.write)
                elif d_hide == 'T':
                    local_file=os.path.join(local_dir,node_name)
                    print(node_path)
                    if test_if == 'T':
                        f_out=open(local_file,'wb')
                    elif test_if == 'F':
                        f_out=open(local_file,'wb')
                        ftpob.retrbinary('RETR '+node_path,f_out.write)
        else:
            if d_hide =='F' and node_name[0]!='.':
                local_file=os.path.join(local_dir,node_name)
                #print(local_file)
                print(node_path)
                if test_if == 'T':
                    f_out=open(local_file,'wb')
                elif test_if == 'F':
                    f_out=open(local_file,'wb')
                    ftpob.retrbinary('RETR '+node_path,f_out.write)
            elif d_hide == 'T':
                local_file=os.path.join(local_dir,node_name)
                print(node_path)
                if test_if == 'T':
                    f_out=open(local_file,'wb')
                elif test_if == 'F':
                    f_out=open(local_file,'wb')
                    ftpob.retrbinary('RETR '+node_path,f_out.write)
    elif node_type == 'dir':
        if filter_re and filter_dp==current_dp:
            re_tmp=re.compile(filter_re)
            if re_tmp.search(node_name):
                if d_hide=='F' and node_name[0]!='.':
                    local_dir=os.path.join(local_dir,node_name)
                    if not os.path.exists(local_dir): os.mkdir(local_dir)
                    if current_dp==1:
                        print(node_path)
                    current_dp+=1
                    parent_node_path=node_path
                    all_child_nodes_info=ftpob.mlsd(parent_node_path)

                    for child_node_info in all_child_nodes_info:
                        child_node_name=child_node_info[0]
                        child_node_type=child_node_info[1]['type']
                        if child_node_name=='.' or child_node_name=='..': continue
                        child_node_path=os.path.join(parent_node_path,child_node_name)
                        if child_node_type=='OS.unix=symlink':
                            child_node_type=get_link_type(ftpob,child_node_path)

                        if child_node_type=='file':
                            if filter_re and filter_dp==current_dp:
                                re_tmp=re.compile(filter_re)
                                if re_tmp.search(child_node_name):
                                    if d_hide=='F' and child_node_name[0]!='.':
                                        local_file=os.path.join(local_dir,child_node_name)
                                        if current_dp==1:
                                            print(child_node_path)
                                        if test_if=='T':
                                            f_out=open(local_file,'wb')
                                        elif test_if=='F':
                                            f_out=open(local_file,'wb')
                                            ftpob.retrbinary('RETR '+child_node_path,f_out.write)
                                    if d_hide=='T':
                                        local_file=os.path.join(local_dir,child_node_name)
                                        if current_dp==1:
                                            print(child_node_path)
                                        if test_if=='T':
                                            f_out=open(local_file,'wb')
                                        elif test_if:
                                            f_out=open(local_file,'wb')
                                            ftpob.retrbinary('RETR '+child_node_path,f_out.write)
                            else:
                                if d_hide=='F' and child_node_name[0]!='.':
                                    local_file=os.path.join(local_dir,child_node_name)
                                    if current_dp==1:
                                        print(child_node_path)
                                    if test_if=='T':
                                        f_out=open(local_file,'wb')
                                    elif test_if=='F':
                                        f_out=open(local_file,'wb')
                                        ftpob.retrbinary('RETR '+child_node_path,f_out.write)
                                if d_hide=='T':
                                    local_file=os.path.join(local_dir,child_node_name)
                                    if current_dp==1:
                                        print(child_node_path)
                                    if test_if=='T':
                                        f_out=open(local_file,'wb')
                                    elif test_if:
                                        f_out=open(local_file,'wb')
                                        ftpob.retrbinary('RETR '+child_node_path,f_out.write)
                        elif child_node_type=='dir':
                            download_dir_tree(ftpob,child_node_path,local_dir,filter_re,filter_dp,d_hide,test_if,current_dp,node_type='dir')
        else:
            if d_hide=='F' and node_name[0]!='.':
                local_dir=os.path.join(local_dir,node_name)
                if not os.path.exists(local_dir): os.mkdir(local_dir)
                if current_dp==1:
                    print(node_path)
                current_dp+=1
                parent_node_path=node_path
                all_child_nodes_info=list(ftpob.mlsd(parent_node_path))
                for child_node_info in all_child_nodes_info:
                    child_node_name=child_node_info[0]
                    child_node_type=child_node_info[1]['type']
                    if child_node_name=='.' or child_node_name=='..': continue
                    child_node_path=os.path.join(parent_node_path,child_node_name)
                    if child_node_type=='OS.unix=symlink':
                        child_node_type=get_link_type(ftpob,child_node_path)

                    if child_node_type=='file':
                        if filter_re and filter_dp==current_dp:
                            re_tmp=re.compile(filter_re)
                            if re_tmp.search(child_node_name):
                                if d_hide=='F' and child_node_name[0]!='.':
                                    local_file=os.path.join(local_dir,child_node_name)
                                    if current_dp==1:
                                        print(child_node_path)
                                    if test_if=='T':
                                        f_out=open(local_file,'wb')
                                    elif test_if=='F':
                                        f_out=open(local_file,'wb')
                                        ftpob.retrbinary('RETR '+child_node_path,f_out.write)
                                if d_hide=='T':
                                    local_file=os.path.join(local_dir,child_node_name)
                                    if current_dp==1:
                                        print(child_node_path)
                                    if test_if=='T':
                                        f_out=open(local_file,'wb')
                                    elif test_if:
                                        f_out=open(local_file,'wb')
                                        ftpob.retrbinary('RETR '+child_node_path,f_out.write)
                        else:
                            if d_hide=='F' and child_node_name[0]!='.':
                                local_file=os.path.join(local_dir,child_node_name)
                                if current_dp==1:
                                    print(child_node_path)
                                if test_if=='T':
                                    f_out=open(local_file,'wb')
                                elif test_if=='F':
                                    f_out=open(local_file,'wb')
                                    ftpob.retrbinary('RETR '+child_node_path,f_out.write)
                            if d_hide=='T':
                                local_file=os.path.join(local_dir,child_node_name)
                                if current_dp==1:
                                    print(child_node_path)
                                if test_if=='T':
                                    f_out=open(local_file,'wb')
                                elif test_if:
                                    f_out=open(local_file,'wb')
                                    ftpob.retrbinary('RETR '+child_node_path,f_out.write)
                    elif child_node_type=='dir':
                        download_dir_tree(ftpob,child_node_path,local_dir,filter_re,filter_dp,d_hide,test_if,current_dp,node_type='dir')
#-------------------------------------------------------------------------------
def mirror_directroy(ftpob,remote_node,local_dir,filter_re,filter_dp,d_hide,test_if):
    root_node=remote_node
    current_dp=0
    root_node_type=judge_root_node_type(ftpob,remote_node)

    download_dir_tree(ftpob,root_node,local_dir,filter_re,filter_dp,d_hide,test_if,current_dp,node_type=root_node_type)
    #print(ftpob,root_node,local_dir,filter_re,filter_dp,d_hide,test_if,current_dp,root_node_type)
#===============================================================================
ftpsite,remote_node,local_dir,filter_re,filter_dp,d_hide,test_if=get_args()
with ftplib.FTP() as ftpob:
    ftpob.connect(ftpsite)
    ftpob.login()
    mirror_directroy(ftpob,remote_node,local_dir,filter_re,filter_dp,d_hide,test_if)
    ftpob.quit()
    print('All done, byby now...')
