import os
import pathlib
import shutil
import subprocess


class ChapterInformation:
    def __init__(self, branch_name, data_folder_name, archive_name):
        self.branch_name = branch_name
        self.data_folder_name = data_folder_name
        self.archive_name = archive_name


def try_remove_tree(path):
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
    except FileNotFoundError:
        pass


def zip(input_path, output_filename):
    try_remove_tree(output_filename)
    command = ["7z", "a", output_filename, input_path, '-mx=9', '-md256m']
    print(f">>>> Creating Archive: {command}")
    subprocess.run(command, check=True)


def main():
    msbuild_path = 'C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\Community\\MSBuild\\Current\\Bin\\MSBuild.exe'
    higurashi_assembly_repo_path = 'C:\\drojf\\large_projects\\umineko\\higurashi-assembly-test-merge-3'
    sln_path = os.path.join(higurashi_assembly_repo_path, 'Assembly-CSharp.sln')
    output_folder_base = r'output'

    chapters = [
        ChapterInformation('oni-mod',    'HigurashiEp01_Data', 'experimental-drojf-dll-ep1'),
        ChapterInformation('wata-mod',   'HigurashiEp02_Data', 'experimental-drojf-dll-ep2'),
        ChapterInformation('tata-mod',   'HigurashiEp03_Data', 'experimental-drojf-dll-ep3'),
        ChapterInformation('hima-mod',   'HigurashiEp04_Data', 'experimental-drojf-dll-ep4'),
        ChapterInformation('mea-mod',    'HigurashiEp05_Data', 'experimental-drojf-dll-ep5'),
        ChapterInformation('tsumi-mod',  'HigurashiEp06_Data', 'experimental-drojf-dll-ep6'),
        ChapterInformation('mina-mod',   'HigurashiEp07_Data', 'experimental-drojf-dll-ep7'),
        ChapterInformation('matsuri-mod','HigurashiEp08_Data', 'experimental-drojf-dll-ep8'),
        ChapterInformation('console-arcs', 'HigurashiEp04_Data', 'experimental-drojf-dll-console'),
    ]

    if not os.path.exists(msbuild_path):
        raise Exception("msbuild path doesn't exist! Please set the 'msbuild_path' variable. There's some instructions in the "
              "Readme.md in https://github.com/07th-mod/higurashi-assembly. You should use the one that comes with "
              "your Visual Studio install - check the default path for an example.")

    if not os.path.exists(higurashi_assembly_repo_path):
        raise Exception("higurashi repo path doesn't exist! Please set the 'higurashi_assembly_repo_path' variable to a clone "
              "or fork of the https://github.com/07th-mod/higurashi-assembly repo")

    for chapter in chapters:
        print(f">>>> Building {chapter.branch_name}")
        built_dll_path = os.path.join(higurashi_assembly_repo_path, 'bin', 'Release', 'Assembly-CSharp.dll')
        output_chapter_folder = os.path.join(output_folder_base, chapter.branch_name, chapter.data_folder_name)
        output_dll_folder = os.path.join(output_chapter_folder, 'Managed')
        output_dll_path = os.path.join(output_dll_folder, 'Assembly-CSharp.dll')
        output_archive_path = os.path.join('archive_output', chapter.archive_name)

        # Remove built DLLs, to prevent accidentally thinking a build was successful
        # when it's actually the leftover DLL from the previous build
        if os.path.exists(built_dll_path):
            os.remove(built_dll_path)

        if os.path.exists(output_dll_path):
            os.remove(output_dll_path)

        if os.path.exists(output_archive_path):
            os.remove(output_archive_path)

        # Switch to the branch we want to build
        subprocess.run(['git', 'checkout', chapter.branch_name], cwd=higurashi_assembly_repo_path, check=True)

        # Build Release using the sln, forcing rebuild
        subprocess.run([msbuild_path, sln_path, '/p:Configuration=Release', '/t:Rebuild'], check=True)

        # Create output folder structure if not exist, then copy DLL there
        pathlib.Path(output_dll_folder).mkdir(parents=True, exist_ok=True)
        shutil.copy(built_dll_path, output_dll_folder)

        # Archive the entire Higurashi_Ep0X folder
        # Need the '.\\' to ensure the rest of the relative path is not included in the archive
        zip('.\\' + output_chapter_folder, output_archive_path)

    print("Program Finished")


if __name__ == '__main__':
    main()

