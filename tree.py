import os

def print_tree(root_dir, prefix=''):
    # ดึงรายการไฟล์และโฟลเดอร์
    entries = sorted(os.listdir(root_dir))
    for index, entry in enumerate(entries):
        path = os.path.join(root_dir, entry)
        connector = '└── ' if index == len(entries) - 1 else '├── '
        print(prefix + connector + entry)
        if os.path.isdir(path):
            extension = '    ' if index == len(entries) - 1 else '│   '
            print_tree(path, prefix + extension)

if __name__ == '__main__':
    folder_path = 'https://github.com/royrover/NUtv'  # เปลี่ยนเป็น path ที่ต้องการ
    print(folder_path)
    print_tree(folder_path)
