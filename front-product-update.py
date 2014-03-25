'''
Created on 2013-7-22
'''
#/usr/bin/python
import xml.etree.ElementTree
import http.client
import os 
import time
import re
import sys

#该值用来标识更新文件
current_build_id = sys.argv[1]
front_resource_path = '/opt/playsnail/app/front-resource'
files_to_be_updated = []
files_to_be_removed= []

#解析svn提交记录
def parse_path(buildId):
    conn = http.client.HTTPConnection("ip:port")
    conn.request('get', '/hudson/job/frontend-QA/'+ buildId +'/api/xml?wrapper=changes&xpath=//changeSet')  
    xmlStr = conn.getresponse().read()  
    root = xml.etree.ElementTree.fromstring(xmlStr)
    path_nodes=root.getiterator("path")
    for node in path_nodes:
     type_node_child=node.getchildren()[0] 
     file_node_child=node.getchildren()[1] 
     type = type_node_child.text
     file = file_node_child.text
     if 'delete' == type:
       files_to_be_removed.append(file)
     else:
       files_to_be_updated.append(file) 
    



#替换svn路径为物理路径
def add_prefix_path_to_files(items):
    source = []
    itemUpdated = ''
    for item in items:
        p = re.compile(r'/[^/]*/[^/]*/[^/]*/PlaySnail-frontend-app')        
        if(p.match(item) is not None):
           itemUpdated = p.sub('/opt/playsnail/resource/frontend/static/app',item)
        
        p = re.compile(r'/[^/]*/[^/]*/[^/]*/PlaySnail-frontend-dynamic')
        if(p.match(item) is not None):                
           itemUpdated = p.sub('/opt/playsnail/resource/backend/dynamic',item)
            
        p = re.compile(r'/[^/]*/[^/]*/[^/]*/PlaySnail-frontend-jsp')
        if(p.match(item) is not None):
           itemUpdated = p.sub('/opt/playsnail/resource/backend/jsp',item)
            
        p = re.compile(r'/[^/]*/[^/]*/[^/]*/PlaySnail-frontend-pages')
        if(p.match(item) is not None):
            itemUpdated = p.sub('/opt/playsnail/resource/frontend/static/pages',item)
             
        p = re.compile(r'/[^/]*/[^/]*/[^/]*/PlaySnail-frontend-style')
        if(p.match(item) is not None):
            itemUpdated = p.sub('/opt/playsnail/resource/frontend/static/style',item)
             
        p = re.compile(r'/[^/]*/[^/]*/[^/]*/PlaySnail-frontend-swf')
        if(p.match(item) is not None):
            itemUpdated = p.sub('/opt/playsnail/resource/frontend/static/other/swf',item)
             
        if itemUpdated not in source:
            source.append(itemUpdated)
            print(itemUpdated)
           
    print('-----------------')
    return source
        
   
   
#压缩打包需要更新的文件 
def compress_files(files):   
   target_dir = 'front-res-product-' + current_build_id + '-'
   target = target_dir + time.strftime('%Y%m%d%H%M%S') + '.tar.gz'
   scp_command = "ssh -tt -p 443 ip /opt/playsnail/app/script/front_compress_product_files.sh %s %s" % (' '.join(files), target)
   if os.system(scp_command) == 0:
       print('scp file to remote success')
   else:
       print('scp file to remote fail')
   return target
       
       
       
#遍历budild id
def for_each_build(start,end):
    for id in range(start,end):
        parse_path(str(id))
    
    
#备份并更新文件  
def backp_and_update(allFiles,tarFile): 
     backup_update_command = "ssh -tt -p 443 ip /opt/playsnail/app/script/front_product_update.sh '%s' %s" % (' '.join(allFiles) , tarFile)
     if os.system(backup_update_command) == 0:
         print("update file success!")
     else:
         print("update file failed")
    

#遍历build id
if len(sys.argv) < 4:
    parse_path(sys.argv[2])
else:
    for_each_build(int(sys.argv[2]),int(sys.argv[3]) + 1)

#解析需要更新的文件物理路径
updateFiles = add_prefix_path_to_files(files_to_be_updated)
#解析需要删除的文件物理路径
removeFiles = add_prefix_path_to_files(files_to_be_removed)
#将需要更新的文件打包并上传到公网正式机器
if updateFiles:
    tar_file = compress_files(updateFiles)
    #先将需要更新与删除的文件在公网机器上做备份，然后删除需更新的文件，解压更新包
    if removeFiles:
        updateFiles.extend(removeFiles)
    backp_and_update(updateFiles, tar_file)




