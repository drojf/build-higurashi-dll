import os
import pathlib
import shutil
import subprocess

# Parameters which are the same for every chapter
class Config:
    def __init__(self, higurashi_assembly_repo_path, output_folder_base):
        self.higurashi_assembly_repo_path = higurashi_assembly_repo_path
        self.output_folder_base = output_folder_base
        self.built_dll_path = os.path.join(self.higurashi_assembly_repo_path, 'bin', 'Release', 'Assembly-CSharp.dll')

# Parameters which are different for every chapter
class ChapterInformation:
    def __init__(self, config: Config, branch_name, data_folder_name, archive_name):
        if os.path.splitext(archive_name)[1] == '':
            raise Exception(f'No file extension specified for archive "{archive_name}"')

        self.branch_name = branch_name
        self.data_folder_name = data_folder_name
        self.archive_name = archive_name

        self.output_chapter_folder = os.path.join(config.output_folder_base, self.branch_name, self.data_folder_name)
        self.output_dll_folder = os.path.join(self.output_chapter_folder, 'Managed')
        self.output_dll_path = os.path.join(self.output_dll_folder, 'Assembly-CSharp.dll')
        self.output_archive_path = os.path.join('archive_output', self.archive_name)



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
    config = Config(higurashi_assembly_repo_path='C:\\drojf\\large_projects\\umineko\\higurashi-assembly',
                    output_folder_base=r'output')

    msbuild_path = 'C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\Community\\MSBuild\\Current\\Bin\\MSBuild.exe'
    sln_path = os.path.join(config.higurashi_assembly_repo_path, 'Assembly-CSharp.sln')


    chapters = [
        ChapterInformation(config, 'oni-mod',      'HigurashiEp01_Data', 'experimental-drojf-dll-ep1.7z'),
        ChapterInformation(config, 'wata-mod',     'HigurashiEp02_Data', 'experimental-drojf-dll-ep2.7z'),
        ChapterInformation(config, 'tata-mod',     'HigurashiEp03_Data', 'experimental-drojf-dll-ep3.7z'),
        ChapterInformation(config, 'hima-mod',     'HigurashiEp04_Data', 'experimental-drojf-dll-ep4.7z'),
        ChapterInformation(config, 'mea-mod',      'HigurashiEp05_Data', 'experimental-drojf-dll-ep5.7z'),
        ChapterInformation(config, 'tsumi-mod',    'HigurashiEp06_Data', 'experimental-drojf-dll-ep6.7z'),
        ChapterInformation(config, 'mina-mod',     'HigurashiEp07_Data', 'experimental-drojf-dll-ep7.7z'),
        ChapterInformation(config, 'matsuri-mod',  'HigurashiEp08_Data', 'experimental-drojf-dll-ep8.7z'),
        ChapterInformation(config, 'console-arcs', 'HigurashiEp04_Data', 'experimental-drojf-dll-console.7z'),
    ]

    if not os.path.exists(msbuild_path):
        raise Exception("msbuild path doesn't exist! Please set the 'msbuild_path' variable. There's some instructions in the "
              "Readme.md in https://github.com/07th-mod/higurashi-assembly. You should use the one that comes with "
              "your Visual Studio install - check the default path for an example.")

    if not os.path.exists(config.higurashi_assembly_repo_path):
        raise Exception("higurashi repo path doesn't exist! Please set the 'higurashi_assembly_repo_path' variable to a clone "
              "or fork of the https://github.com/07th-mod/higurashi-assembly repo")


    # Remove built DLLs, to prevent accidentally thinking a build was successful
    # when it's actually the leftover DLL from the previous build
    if os.path.exists(config.built_dll_path):
        print(f"Removing {config.built_dll_path}")
        os.remove(config.built_dll_path)

    for chapter in chapters:
        if os.path.exists(chapter.output_dll_path):
            print(f"Removing {chapter.output_dll_path}")
            os.remove(chapter.output_dll_path)

        if os.path.exists(chapter.output_archive_path):
            print(f"Removing {chapter.output_archive_path}")
            os.remove(chapter.output_archive_path)


    for chapter in chapters:
        print(f">>>> Building {chapter.branch_name}")

        # Switch to the branch we want to build
        subprocess.run(['git', 'checkout', chapter.branch_name], cwd=config.higurashi_assembly_repo_path, check=True)

        # Build Release using the sln, forcing rebuild
        subprocess.run([msbuild_path, sln_path, '/p:Configuration=Release', '/t:Rebuild'], check=True)

        # Create output folder structure if not exist, then copy DLL there
        pathlib.Path(chapter.output_dll_folder).mkdir(parents=True, exist_ok=True)
        shutil.copy(config.built_dll_path, chapter.output_dll_folder)

        # Archive the entire Higurashi_Ep0X folder
        # Need the '.\\' to ensure the rest of the relative path is not included in the archive
        zip('.\\' + chapter.output_chapter_folder, chapter.output_archive_path)

    print("Program Finished")


if __name__ == '__main__':
    main()

