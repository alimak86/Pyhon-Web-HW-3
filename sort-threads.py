from pathlib import Path  # use for the iteration over the folders
import datetime  # for working with date
import os  # for working with files and folders
import re  # for working with the strings
import shutil  # working with the files and folders
import sys  # use for the program arguments

from threading import Thread, Condition,Barrier,Event
import threading

import logging
from time import sleep

# define variables requred for the main folders used for the arrangement
VIDEO = "video"
AUDIO = "audio"
DOCS = "documents"
IMAGES = "images"
ARCHIVES = "archives"
OTHER = "other"


WIDTH = 16  # tried to use for the format output, but did nit succeded


# main extentions of the files
images = ["jpeg", "png", "jpg", "svg"]
video = ["avi", "mp4", "mov", "mkv"]
audio = ["mp3", "ogg", "wav", "amr"]
documents = ["doc", "docx", "txt", "pdf", "xlsx", "pptx", "dat", "odt", "djvu"]
archieves = ["zip", "tar", "gz"]

# cyrilic symbols ued for the ranslations
CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")

TRANS = {}

# create a dictionary requred for the translation


def create_dictionary():
    dict = {}  # empty dictionary
    for ch, l in zip(CYRILLIC_SYMBOLS, TRANSLATION):  # read symbol from the alphabet
        dict[ord(ch)] = l  # add to dictionary
        dict[ord(ch.upper())] = l.upper()  # add to dictionary
    return dict


TRANS = create_dictionary()  # create dictionary TRANS

# responsible for the translation of name. convert cyrilic into latin alphabet


def translate(name):
    return name.translate(TRANS)

# sanitize latin word name
# substitute non digits and latin symbols with _


def sanitize_transl(name):
    return re.sub(r"[^0-9a-zA-Z]", "_", name)

# split filanem into name and extantion
# return name before dot
# return extantion - everything after the dot
# it is assumed that a first right point separate name from the extantion


def split_filename(filename):  # split filename into two words name and extention
    dot_index = filename.rfind(".")
    if dot_index > 0:
        return [filename[0:dot_index], filename[dot_index+1:len(filename)]]
    else:
        return [filename, "noext"]

# create main folders video, audio etc in case if nothing in the folder dir_name


def create_main_folders(dir_name, condition: Condition):
    logging.debug(f"is creating main folders")
   # responsible for the creation of the folders required for the cleaning and return list of created folders
   # in the dir_name folder
    list = []  # empty list of created folders
    main_folders = [VIDEO, AUDIO, IMAGES,
                    DOCS, ARCHIVES, OTHER]
    os.chdir(dir_name)  # make folder current
    print(
        "-----------------------------------------------------------------------")
    print("List of the existing main folders folders:")
    print(
        "-----------------------------------------------------------------------")

    for folder in main_folders:
        # check if a main folder is in the current directory
        if not os.path.isdir(folder):
            os.mkdir(folder)  # if not then create
            # append to the list in ordet to know what was added
            list.append(folder)
        else:
            print("{:<16}".format(folder))

    print(
        "-----------------------------------------------------------------------")
    print("List of created main folders:")
    print(
        "-----------------------------------------------------------------------")
    for folder in list:
        print("{:<16}".format(folder))
    print(
        "-----------------------------------------------------------------------")
    with condition:
        logging.debug(f"done with creatin main folders now you may sort your files out")
        condition.notify_all()

    return list

# output files from the file list corresponding type NAME


def output_files(file_list, NAME):
    # print("-----------------------------------------------------------------------")
    print(NAME)
    print(
        "-----------------------------------------------------------------------")
    for file in file_list:
        print("{:<16}".format(file))
    print(
        "-----------------------------------------------------------------------")

# create a list of folders and files in the directory dir_name


def list_folder(dir_name):  #
    # returns list of list of files and folders
    p = Path(dir_name)  # p points out to a folder dir_name
    video_files = []  # empty list of video files
    audio_files = []  # empty list of audio files
    images_files = []  # empty list of images files
    archieves_files = []  # empty list of archives files
    docs_files = []  # empty list of doc files
    other_files = []  # empty list of other files
    folders = []  # empty list of folders in the directory dir_name

    count_files = {IMAGES: 0, AUDIO: 0, VIDEO: 0,
                   DOCS: 0, ARCHIVES: 0, OTHER: 0}

    for obj in p.iterdir():  # lets review the folder
        if obj.is_dir():  # check if the object is a folder
            # we get every folder except main folders
            if obj.name not in (VIDEO, AUDIO, DOCS, IMAGES, ARCHIVES, OTHER):
                # append only folders which are not main folders
                folders.append(obj.name)
        else:  # go here if object is a file
            # read extension second part of the name
            filename = split_filename(obj.name)
            # word after the latest dot
            ext = filename[1]  # read extention
            # check which file extantion it belongs to
            if ext in images:
                # calculate amount of that file, same for the rest
                count_files[IMAGES] += 1
                images_files.append(obj.name)
            elif ext in video:
                count_files[VIDEO] += 1
                video_files.append(obj.name)
            elif ext in audio:
                count_files[AUDIO] += 1
                audio_files.append(obj.name)
            elif ext in documents:
                count_files[DOCS] += 1
                docs_files.append(obj.name)
            elif ext in archieves:
                count_files[ARCHIVES] += 1
                archieves_files.append(obj.name)
            else:
                count_files[OTHER] += 1
                other_files.append(obj.name)
    # create a dictionary file type : list of files corresponding to this type
    dict_files = {VIDEO: video_files, AUDIO: audio_files, IMAGES: images_files,
                  DOCS: docs_files, ARCHIVES: archieves_files, OTHER: other_files}

    # print date
    print("\n\nDate:" + str(datetime.date.today()))
    print("current folder:", dir_name)
    print(
        "-----------------------------------------------------------------------\n")
    print("List of files:")
    print(
        "-----------------------------------------------------------------------")
    for NAME in dict_files:
        # output all files found coresponding type NAME
        output_files(dict_files[NAME], NAME)
    print("Total files")
    print(
        "-----------------------------------------------------------------------")
    for ext in count_files:
        print("{:<16}{:<16}".format(ext, count_files[ext]))

    print(
        "-----------------------------------------------------------------------")
    print("List of folders:")
    print(
        "-----------------------------------------------------------------------")
    for folder in folders:
        print("{:<16}".format(folder))
    return [{VIDEO: video_files, AUDIO: audio_files, IMAGES: images_files, DOCS: docs_files, ARCHIVES: archieves_files, OTHER: other_files}, folders]

# normilize name
# translate into latin letters
# substitute unknown symbols to _


def normilize(name):
    # normilize filename
    name = translate(name)
    name = sanitize_transl(name)
    return name

# move files to folder


def move_files(files, folder):
    count = 0  # calculate how many were renamed
    for file in files:
        name = split_filename(file)[0]
        ext = split_filename(file)[1]
        filename = normilize(name) + "." + ext
        try:
            if filename != file:
                count += 1
            shutil.copy2(file, folder + "\\" + filename)
            os.remove(file)
        except PermissionError:  # if something happens during the moving then will tell
            print(f"can not move file:{file}")

    return count


def move_files_in_folder(dir_name, files_dict):
    os.chdir(dir_name)  # set up current directory for work
    print("Start moving files...")
    print("Working directory:", os.getcwd())
    for NAME in files_dict:
        # for each type of files copy them into the corresponding folder
        if NAME != ARCHIVES:  # archives will work later
            print(
                "-----------------------------------------------------------------------")
            print("move files ", NAME, " to the folder ", NAME, "...")
            renamed = move_files(files_dict[NAME], NAME)
            print("Total files moved:", len(files_dict[NAME]))
            print("Renamed:{:<16}\n".format(renamed))

# calculate number of all files and folders contained
# in the current folder including all subfolders


def files_in_the_folder(folder):  # not required
    p = Path(folder)
    list = []  # list of folders in the current folder
    count = 0
    for obj in p.iterdir():
        if obj.is_dir():
            list.append(obj.name)  # append all the subfolders of the folder
            count += 1
        else:
            count += 1  # if not directory, so file count
 # return [count, list]
    if list == []:  # if list is empty means no subfolders so return number of files
        return count
    else:
        for dir in list:
            # else calculate files in the subfolders
            count += files_in_the_folder(folder + "\\" + dir)
        return count


def destroy_empty_folders(dir_name, folders):  # not required
    os.chdir(dir_name)  # set up current directory for work
    destroyed = []
    for folder in folders:
        count = files_in_the_folder(folder)
        if count == 0:  # means there is no files in the folder
            try:
                os.rmdir(folder)
                destroyed.append(folder)
            except OSError:  # if something happens during destruction of the folder will tell
                print(f"can not destroy folder {folder}")
    return destroyed


def rename_folders(dir_name, folders):  # is not required at all
    os.chdir(dir_name)  # set up current directory for work
    count = 0  # folders renamed
    for folder in folders:
        new_folder = normilize(folder)
        if new_folder != folder:
            try:
                os.rename(folder, new_folder)
                count += 1
            finally:  # if something happens
                print(f"can not rename {folder}")
    return count


def unpack_archives(dir_name, archive_list):
    os.chdir(dir_name)
    print("Start unpacking archives...")
    print("Working directory:", os.getcwd())

    for archive in archive_list:
        list = split_filename(archive)
        name = list[0]
        ext = list[1]
        new_name = normilize(name)
        try:
            shutil.unpack_archive(archive, ARCHIVES + "\\" + new_name)
            os.remove(archive)
        except shutil.ReadError:  # if something happens during the moving the archive
            print(f"problem with the moving of {archive}")
        except PermissionError:
            print(f"problem with the moving of {archive}")

    print("Total unpacked:{:<16}".format(len(archive_list)))


def create_filelist(folder):
    # create file list of all subfolders
    logging.debug(f"is creating list of ll files in {folder}")
    p = Path(folder)
    folderlist = []  # list of folders in the current folder
    filelist = []  # list of file names in the current folder + subfolders

    for obj in p.iterdir():
        if obj.is_dir():
            # append all the subfolders of the folder
            folderlist.append(obj.name)

    for subfolder in folderlist:
        # else calculate files in the subfolders
        filelist += filelist_in_the_folder(folder + "\\" + subfolder)
    logging.debug(f"completed to create the list of the files in the {folder}")
    return filelist


def filelist_in_the_folder(folder):
    p = Path(folder)
    folderlist = []  # list of folders in the current folder
    filelist = []  # list of file names in the current folder + subfolders

    for obj in p.iterdir():
        if obj.is_dir():
            # append all the subfolders of the folder
            folderlist.append(obj.name)
        else:
            # if not directory, so filename count
            filelist.append(folder + "\\" + obj.name)
 # return [count, list]
    if folderlist == []:  # if list is empty means no subfolders so return list of files
        return filelist
    else:
        for dir in folderlist:
            # else calculate files in the subfolders
            filelist += filelist_in_the_folder(folder + "\\" + dir)
        return filelist


def copy_filelist_to_directory(dir_name, filelist):
    # move all files from the filelist to directory
    os.chdir(dir_name)  # dir_name make current
    for file in filelist:
        split = file.split("\\")
        name = split[len(split)-1]
        try:
            shutil.copy2(file, name)
            # os.remove(file)
        except PermissionError:  # if something happens during the moving then will tell
            print(f"can not copy file:{file}")
        except shutil.SameFileError:  # if something happens during the moving then will tell
            print(f"same filename:{file}")


def clean(folder):
    # remove all files and subfolders in the current folder
    folderlist = []

    p = Path(folder)
    for obj in p.iterdir():
        if obj.is_dir():
            # append all the subfolders of the folder
            folderlist.append(obj.name)
        else:
            try:
                os.remove(folder + "\\" + obj.name)  # remove files
            except PermissionError:
                print(f"can not remove {obj.name}")
            except FileNotFoundError:
                print(f"can not find {obj.name}")

    if folderlist == []:  # if list is empty means no subfolders so return list of files
        return 0
    else:
        for dir in folderlist:
            clean(folder + "\\" + dir)
            try:
                os.rmdir(folder + "\\" + dir)  # remove after cleaning
            except OSError:
                print(f"{folder} is not empty")


def dir(dir_name):  # sort all file in the dir_name into main folders - all other folders already trashed
    # list out all the files and folders of the folder
    logging.debug(f"accumulating all the files in the {dir_name}")
    list = list_folder(dir_name)
    files_dict = list[0]  # get files dictionary
    logging.debug(f"accumulating all the folders in the {dir_name}")
    folders = list[1]  # get list of folders
    # create folder if needed for the arrangement

    logging.debug(f"moving all the files in the main folders")
    move_files_in_folder(dir_name, files_dict)

    logging.debug(f"destroying empty folders")
    destroyed = destroy_empty_folders(dir_name, folders)
    print(
        "-----------------------------------------------------------------------")
    print("Folders destroyed: {:<16}".format(len(destroyed)))
    print(
        "-----------------------------------------------------------------------")
    
    logging.debug(f"unpacking archives")
    unpack_archives(dir_name, files_dict[ARCHIVES])  # unpack archive


def clean_folders(dir_name,event:Event):  # delete all subfolders of the folder dir_name
    event.wait()
    logging.debug(f"is removing all the folders and subfolders in {dir_name}")
    p = Path(dir_name)
    for obj in p.iterdir():  # arrange the rest of the folders
        if obj.is_dir():  # check if the object is a folder
            clean(dir_name + "\\" + obj.name)

    logging.debug(f"completed removing all the folders and subfolders in {dir_name}")

def copy_file(dir_name, file):
    global THR_PASSED
    logging.debug(f"is moving...")
    # move all files from the filelist to directory
    os.chdir(dir_name)  # dir_name make current
    split = file.split("\\")
    name = split[len(split)-1]
    try:
        shutil.copy2(file, name)
        
        try:
            os.remove(file)  # remove files
        except PermissionError:
            print(f"can not remove {file}")
        except FileNotFoundError:
            print(f"can not find {file}")

    except PermissionError:  # if something happens during the moving then will tell
        print(f"can not copy file:{file}")
    except shutil.SameFileError:  # if something happens during the moving then will tell
        print(f"same filename:{file}")
    THR_PASSED+=1
    logging.debug(f"is done {THR_PASSED}")


def control_threads(num, event:Event):
    global THR_PASSED
    while True:
        logging.debug("is controlling the THR_PASS")
        if THR_PASSED == num:
            event.set()
            break
 
THR_PASSED = 0


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG, format='%(threadName)s %(message)s')
    main_directory = sys.argv[1]

    ready_to_sort = Condition()
    create_folders_thread = Thread(target = create_main_folders,args=(main_directory,ready_to_sort),name = "create_folder_thread")
    create_folders_thread.start()

    filelist = create_filelist(main_directory)
    num_threads = len(filelist)## include creation folders
    
    for element in filelist:
        print(element)
        move_thread = Thread(target = copy_file,args=(main_directory,element),name = element)
        move_thread.start()

    thr_terminated = Event()
    control_thread = Thread(target = control_threads,args=(num_threads,thr_terminated),name = "control_thread")
    control_thread.start()

    cleaner_thread = Thread(target = clean_folders,args=(main_directory,thr_terminated),name = "cleaner_thread")
    cleaner_thread.start()

    thr_terminated.wait()
    dir(main_directory)

