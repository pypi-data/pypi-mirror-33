import os
import urllib.request as rq
import zipfile

def create_my_world():
    url = 'https://www.yuanfudao.com/tutor-ybc-course-api/res.zip'
    filename = 'res.zip'
    rq.urlretrieve(url,filename)
    zip_file = zipfile.ZipFile(filename)
    for files in zip_file.namelist():
        zip_file.extract(files,'./')
    zip_file.close()
    os.remove(filename)

def create_my_world_l2():
    url = 'https://www.yuanfudao.com/tutor-ybc-course-api/res2.zip'
    filename = 'res2.zip'
    rq.urlretrieve(url,filename)
    zip_file = zipfile.ZipFile(filename)
    for files in zip_file.namelist():
        zip_file.extract(files,'./')
    zip_file.close()
    os.remove(filename)

def create_my_world_l2_bak():
    url = 'https://www.yuanfudao.com/tutor-ybc-course-api/res2.zip'
    filename = 'res2.zip'
    rq.urlretrieve(url,filename)
    zip_file = zipfile.ZipFile(filename)
    for files in zip_file.namelist():
        filename = files.encode('cp437').decode('gbk')
        zip_file.extract(files,'./')
        os.rename(files,filename)
    zip_file.close()
    os.remove(filename)

def main():
    create_my_world()
    create_my_world_l2()

if __name__ == '__main__':
    main()
