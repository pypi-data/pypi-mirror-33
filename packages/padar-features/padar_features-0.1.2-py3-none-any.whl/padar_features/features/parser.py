import os


def get_file_type(file_path):
    return os.path.basename(file_path).split('.')[-2].lower().strip()


def get_sensor_id(file_path):
    base_name = os.path.basename(file_path)
    return base_name.split('.')[1].split('-')[0].upper().strip()


def get_sensor_type(file_path):
    if get_file_type(file_path) == 'sensor' and 'accel' in file_path.lower():
        return 'accelerometer'


def get_data_type(file_path):
    if len(os.path.basename(file_path).split('.')[0].split('-')) < 2:
        return ""
    return os.path.basename(file_path).split('.')[0].split('-')[1]


def get_pid(file_path):
    if file_path is None:
        return None
    if "MasterSynced" in file_path:
        return os.path.basename(
            os.path.dirname(file_path.split('MasterSynced')[0])
        )
    elif "Derived" in file_path:
        return os.path.basename(
            os.path.dirname(file_path.split('Derived')[0])
        )
    else:
        return os.path.basename(os.path.dirname(file_path))



