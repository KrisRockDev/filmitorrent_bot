import os
import difflib
import shutil

from icecream import ic


def find_similar_files(base_directory, target_filename, threshold=0.7):
    matching_files = []
    target_name_without_extension, target_extension = os.path.splitext(target_filename)

    for root, dirs, files in os.walk(base_directory):
        for filename in files:
            name_without_extension, extension = os.path.splitext(filename)
            similarity = difflib.SequenceMatcher(None, name_without_extension, target_name_without_extension).ratio()
            if similarity >= threshold and extension != target_extension:
                matching_files.append(os.path.join(root, filename))

    return matching_files


def main():
    DIR = r'd:\filmtorrent'

    base_directory = r'd:\filmtorrent'  # путь_к_директории
    # target_filename = 'The.Out.Laws.2023.1080p_RHS_[scarfilm.org].mkv'  # название_целевого_файла.расширение
    for filename in os.listdir(base_directory):
        if os.path.isfile(os.path.join(DIR, filename)):
            if filename.lower()[-3:] == 'mkv':
                target_filename = os.path.join(DIR, filename)

                similar_files = find_similar_files(base_directory, target_filename, threshold=0.55)
                if similar_files:
                    print("Похожие файлы найдены:")
                    for file in similar_files:
                        print(target_filename)
                        print(file)
                        shutil.move(os.path.join(DIR, target_filename), os.path.join(os.path.split(file)[0], os.path.split(os.path.split(file)[0])[1][17:] + '.mkv'))
                else:
                    print(f"Похожие файлы не найдены для: {target_filename}")


if __name__ == '__main__':
    main()
