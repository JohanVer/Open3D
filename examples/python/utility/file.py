# Open3D: www.open3d.org
# The MIT License (MIT)
# See license file or visit www.open3d.org for details

# examples/python/utility/file.py

from os import listdir, makedirs
from os.path import exists, isfile, join, splitext
import shutil
import re
from pathlib import Path
import transformations as tf
import json

def readFiles(path):
    with open(path) as file:
        content = file.readlines()
        content = [x.strip() for x in content]
    return content

def readPoses(path, calibration=''):
    if (calibration != ''):
        print('Loading extrinsic calibration from: %s' % calibration)
        with open(calibration,
                  "r") as read_file:
            camera_calibration_dict = json.load(read_file)
        init_T_camera = camera_calibration_dict['transformation']
    else:
        init_T_camera = tf.identity_matrix()

    with open(path) as file:
        content = file.readlines()
        content = [x.strip() for x in content]
    poses = []
    for c in content:
        s = c.split(' ')
        trans = [s[0], s[1], s[2]]
        quat = [s[3], s[4], s[5], s[6]]

        t_m = tf.quaternion_matrix(quat)
        t_m[0:3, 3] = trans

        # Apply calibration
        t_m = (t_m.dot(init_T_camera))

        poses.append(t_m)
    return poses

def searchForFiles(name, search_path):
    paths = []
    for path in Path(search_path).rglob(name):
        paths.append(path)
    return paths

def sorted_alphanum(file_list_ordered):
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(file_list_ordered, key=alphanum_key)


def get_file_list(path, extension=None):
    if extension is None:
        file_list = [path + f for f in listdir(path) if isfile(join(path, f))]
    else:
        file_list = [
            path + f
            for f in listdir(path)
            if isfile(join(path, f)) and splitext(f)[1] == extension
        ]
    file_list = sorted_alphanum(file_list)
    return file_list


def add_if_exists(path_dataset, folder_names):
    for folder_name in folder_names:
        if exists(join(path_dataset, folder_name)):
            path = join(path_dataset, folder_name)
    return path


def get_rgbd_folders(path_dataset):
    path_color = add_if_exists(path_dataset, ["image/", "rgb/", "color/"])
    path_depth = join(path_dataset, "depth/")
    return path_color, path_depth


def get_rgbd_file_lists(path_dataset, ext_calibration_path):

    rgb_path_files = searchForFiles('rgb_drive.txt', path_dataset + '/raw_full/')
    vehicle_file = searchForFiles('rgb_drive_vehicle_0.0800.txt', path_dataset + '/raw_full/vehicle/')[0]

    rgb_names = readFiles(str(rgb_path_files[0]))
    rgb_list = []
    depth_list = []

    poses = readPoses(vehicle_file, ext_calibration_path)

    for n_idx, n in enumerate(rgb_names):
            rgb_list.append(path_dataset + '/raw_full/rgb/' + n)
            depth_list.append(path_dataset + '/raw_full/depth/' + n)

    # path_color, path_depth = get_rgbd_folders(path_dataset)
    # color_files = get_file_list(path_color, ".jpg") + \
    #         get_file_list(path_color, ".png")
    # depth_files = get_file_list(path_depth, ".png")
    return rgb_list, depth_list, poses


def make_clean_folder(path_folder):
    if not exists(path_folder):
        makedirs(path_folder)
    else:
        shutil.rmtree(path_folder)
        makedirs(path_folder)


def check_folder_structure(path_dataset):
    path_color, path_depth = get_rgbd_folders(path_dataset)
    assert exists(path_depth), \
            "Path %s is not exist!" % path_depth
    assert exists(path_color), \
            "Path %s is not exist!" % path_color


def write_poses_to_log(filename, poses):
    with open(filename, 'w') as f:
        for i, pose in enumerate(poses):
            f.write('{} {} {}\n'.format(i, i, i + 1))
            f.write('{0:.8f} {1:.8f} {2:.8f} {3:.8f}\n'.format(
                pose[0, 0], pose[0, 1], pose[0, 2], pose[0, 3]))
            f.write('{0:.8f} {1:.8f} {2:.8f} {3:.8f}\n'.format(
                pose[1, 0], pose[1, 1], pose[1, 2], pose[1, 3]))
            f.write('{0:.8f} {1:.8f} {2:.8f} {3:.8f}\n'.format(
                pose[2, 0], pose[2, 1], pose[2, 2], pose[2, 3]))
            f.write('{0:.8f} {1:.8f} {2:.8f} {3:.8f}\n'.format(
                pose[3, 0], pose[3, 1], pose[3, 2], pose[3, 3]))
