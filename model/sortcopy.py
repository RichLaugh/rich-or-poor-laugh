import os
import csv
import shutil

CSV_PATH = 'audio.csv'
SRC_FOLDER = '/mnt/d/data_44k/laughter'
DEST_FOLDER = './audio'


def main():
    os.makedirs(DEST_FOLDER, exist_ok=True)

    with open(CSV_PATH, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            filename = row['name']
            category = row['category']

            src_path = os.path.join(SRC_FOLDER, filename)
            dst_dir = os.path.join(DEST_FOLDER, category)
            dst_path = os.path.join(dst_dir, filename)

            os.makedirs(dst_dir, exist_ok=True)

            if os.path.exists(src_path):
                shutil.copy2(src_path, dst_path)
                print(f"Скопирован: {src_path} -> {dst_path}")
            else:
                print(f"Файл не найден: {src_path}")


if __name__ == '__main__':
    main()