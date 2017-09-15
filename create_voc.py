import PIL
from PIL import Image
from bs4 import BeautifulSoup
from datetime import date
from icrawler.builtin import GoogleImageCrawler
import progressbar
import os
import errno
import shutil
import glob
import re


bar = progressbar.ProgressBar()


def crawl_images():
    cigaretes = ['chesterfield blue', 'chesterfield red']

    for pack in cigaretes:
        google_crawler = GoogleImageCrawler(
          parser_threads=2, 
          downloader_threads=4,
          storage={ 'root_dir': re.sub(r' ', '_', pack) })

        google_crawler.crawl(
            keyword=pack,
            max_num=650,
            date_min=None,
            date_max=None)


def create_tree(path):
    for folder in ('VOCdevkit', 'VOCdevkit/VOC2012', 'VOCdevkit/VOC2012/Annotations', 'VOCdevkit/VOC2012/ImageSets',
                   'VOCdevkit/VOC2012/JPEGImages', 'VOCdevkit/VOC2012/SegmentationClass',
                   'VOCdevkit/VOC2012/SegmentationObject', 'VOCdevkit/VOC2012/ImageSets/Action',
                   'VOCdevkit/VOC2012/ImageSets/Layout', 'VOCdevkit/VOC2012/ImageSets/Main',
                   'VOCdevkit/VOC2012/ImageSets/Segmentation'):
        try:
            os.makedirs(path + folder)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
            else:
                delete_prompt = input('Directories structure already exist. Do you want to delete it? [y/n]: ')
                if delete_prompt == 'y':
                    shutil.rmtree(path + folder)
                    os.makedirs(path+folder)
                elif delete_prompt == 'n':
                    break
                else:
                    raise ValueError('Possible choices are yes-\'y\' or no-\'n\'')

##create_tree('')


def remove_non_jpegs_and_resize_and_rename():
    dir = 'VOCdevkit/VOC2012/JPEGImages/'
    for folder in os.listdir(dir):
        index = 1
        for img in os.listdir(dir + folder):
            try:    
                if img.endswith(('.jpg', '.jpeg', '.JPG')):
                    image_name = folder + '-' + str(index) + '.jpg'
                    image = Image.open(dir + folder + '/' + img)
                    if image.width > 1024 or image.height > 1024:
                        if image.height > image.width:
                            factor = 1024 / image.height
                        else:
                            factor = 1024 / image.width
                        new = image.resize((int(image.width * factor), int(image.height * factor)), PIL.Image.ANTIALIAS)
                        new.save(dir + folder + '/' + image_name)
                        os.remove(dir + folder + '/' + img)
                    elif image.width < 600 or image.height < 600:
                        if image.height < image.width:
                            factor = 600 / image.height
                        else:
                            factor = 600 / image.width
                        new = image.resize((int(image.width * factor), int(image.height * factor)), PIL.Image.ANTIALIAS)
                        new.save(dir + folder + '/' + image_name)
                        os.remove(dir + folder + '/' + img)
                    else:
                        image.save(dir + folder + '/' + image_name)
                        os.remove(dir + folder + '/' + img)
                    index += 1
                else:
                    os.remove(dir + folder + '/' + img)
            except Exception as e:
                print(img, folder, e)
                os.remove(dir + folder + '/' + img)
                                        

##remove_non_jpegs_and_resize_and_rename()


def create_imagesets(path):
    JPEGImages, ImageSets = path + 'VOCdevkit/VOC2012/JPEGImages/', path + 'VOCdevkit/VOC2012/ImageSets/Main/'
    train_set, val_set = [],[]
    
    for folder in next(os.walk(JPEGImages))[1]:
        images = glob.glob(JPEGImages + folder + '/*.jpg')
        point = round(len(images)/5*4)
        train_set += images[:point]
        val_set += images[point:]

    with open(ImageSets + 'train.txt', 'w') as train_f:
        with open(ImageSets + 'trainval.txt', 'w') as trainval_f:
            for image in sorted(train_set):
                line = os.path.basename(image)[0:-4] + '\n'
                train_f.write(line)
                trainval_f.write(line)
    with open(ImageSets + 'val.txt', 'w') as val_f:
        with open(ImageSets + 'trainval.txt', 'a') as trainval_f:
            for image in sorted(val_set):
                line = os.path.basename(image)[0:-4] + '\n'
                val_f.write(line)
                trainval_f.write(line)
    
    for folder in next(os.walk(JPEGImages))[1]:
        with open(ImageSets + folder + '_train.txt', 'w') as train_f:
            with open(ImageSets + folder + '_trainval.txt', 'w') as trainval_f:
                for image in sorted(train_set):
                    if os.path.basename(image) in os.listdir(JPEGImages + folder):
                        line = os.path.basename(image)[0:-4] + ' 1\n'
                    else:
                        line = os.path.basename(image)[0:-4] + ' -1\n'
                    train_f.write(line)
                    trainval_f.write(line)
        with open(ImageSets + folder + '_val.txt', 'w') as val_f:
            with open(ImageSets + folder + '_trainval.txt', 'a') as trainval_f:
                for image in sorted(val_set):
                    if os.path.basename(image) in os.listdir(JPEGImages + folder):
                        line = os.path.basename(image)[0:-4] + ' 1\n'
                    else:
                        line = os.path.basename(image)[0:-4] + ' -1\n'
                    val_f.write(line)
                    trainval_f.write(line)

    path_to_images = glob.iglob(JPEGImages + '*/*.jpg')
    list(map(lambda image: os.rename(image, JPEGImages + os.path.basename(image)), path_to_images))
    list(map(lambda folder: shutil.rmtree(JPEGImages + folder), next(os.walk(JPEGImages))[1]))
            

create_imagesets('')


def change_folder_in_xml(path):
    anotations_path = path + 'VOCdevkit/VOC2012/Annotations/'
    files = glob.glob(anotations_path + '*.xml')

    for file in bar(files):
        with open(file, 'r+') as f:
            soup = BeautifulSoup(f, 'xml')
            folder, database = soup.folder, soup.database
            folder.string, database.string = 'VOC2012', 'The VOC2012 Database'
            if soup.path:
                soup.path.decompose()
            f.seek(0)
            f.truncate()
            f.write(str(soup))

##change_folder_in_xml('')
