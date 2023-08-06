DEFAULT_FILTERS = {
    'name': ['*'],
    'architecture': ['x86_64'],
    'hypervisor': ['xen'],
    'virtualization-type': ['hvm'],
    'root-device-type': ['ebs'],
    'image-type': ['machine'],
    'state': ['available'],
    'description': ['*'],
}

DISTRO_OWNER_IDS = {
    'ubuntu': '099720109477',
    'debian': '379101102735',
}
