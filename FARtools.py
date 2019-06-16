#    FARtools, a python script to edit and read .far archives from Guitar Hero Live
#    Copyright (C) 2019  Olivia Ducharme
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import sys
import struct
import argparse
import zlib
import pathlib

args = argparse.ArgumentParser(description='Tools to easily add, replace and rename files in FAR archives.')

args.add_argument('--easy', '--cap', action="store_true", default=False, dest="cap", help="Noob friendly mode that helps them do what they want (this one's for you, Cap!)")
args.add_argument('-a', '--add', action="store_true", default=False, dest="add", help="Add a new file to the archive")
args.add_argument('-rn', '--rename', action="store_true", default=False, dest="rename", help="Rename an already existing file in the archive")
args.add_argument('-rp', '--replace', action="store_true", default=False, dest="replace", help="Replace an already existing file in the archine")
args.add_argument('-ls', '--listfiles', action="store_true", default=False, dest="listf", help="Prints the list of all the paths in the archive")
args.add_argument('-c', '--compress', action="store_true", default=False, dest="compress", help="Compresses files added through -a")
args.add_argument('-x', '--extract', action="store_true", default=False, dest="Xtract", help="Extract a file from the FAR archive")

args.add_argument('--FAR', action="store", dest="FAR", type=str, help="Path to the archive you want to modify")
args.add_argument('-p', '--path', action="store", dest="FilePath", type=str, help="Path of the file you want to extract/add/rename/replace in the archive")
args.add_argument('-f', '--file', action="store", dest="Replace", type=str, help="Path to the new file (Or the new path if your are renaming)")
args.add_argument('-o', '--output', action="store", dest="Replace", type=str, help="Path to output the extracted file")

if len(sys.argv) < 2:
    args.print_help()
    exit(0)
parsed = args.parse_args()

def ExtractFile(OutPath, HeaderPosition: int):
    os.lseek(FAR, HeaderPosition + 0x100, os.SEEK_SET)

    size_decompressed = int.from_bytes(os.read(FAR, 0x08), "big")
    size_compressed = int.from_bytes(os.read(FAR, 0x08), "big")
    DataPos = DataStart + int.from_bytes(os.read(FAR, 0x08), "big")
    Compressed = True if int.from_bytes(os.read(FAR, 0x08), "big") == 0x200000000 else False

    if Compressed:
        os.lseek(FAR, DataPos + 2, os.SEEK_SET)
        FileData = os.read(FAR, size_compressed - 2)
        FileData = zlib.decompress(FileData, -15, size_decompressed)
    else:
        os.lseek(FAR, DataPos, os.SEEK_SET)
        FileData = os.read(FAR, size_compressed)
    
    os.write(Replace, FileData)
    


def AddFile(FileData: bytes):
    os.lseek(FAR, DataStart, os.SEEK_SET)
    DataKeep = os.read(FAR, (FAR_Size - DataStart))

    os.lseek(FAR, DataStart, os.SEEK_SET)

    os.write(FAR, bytes(FilePath, "UTF-8"))
    i = len(FilePath)
    while i < 0x100:
        os.write(FAR, b'\x00')
        i+=1

    Compressed_Flag = 0x200000000 if compressed else 0x100000000
    FileData = b'\x00\x00' + zlibcomp.compress(FileData) + zlibcomp.flush() if compressed else FileData
    ReplaceCompSize = len(FileData) + 2 if compressed else len(FileData)

    os.write(FAR, Replace_Size.to_bytes(0x08, 'big')) # Decompressed size
    os.write(FAR, ReplaceCompSize.to_bytes(0x08, 'big')) # Compressed size

    os.write(FAR, (FAR_Size - DataStart).to_bytes(0x08, 'big')) # Offset
    os.write(FAR, Compressed_Flag.to_bytes(0x08, 'big')) # Decompressed flag
    os.write(FAR, DataKeep) # Writes back the already existing files
    os.write(FAR, FileData)
    
    #Moving DataStart 0x120 bytes further
    os.lseek(FAR, 0x08, os.SEEK_SET)
    os.write(FAR, (DataStart + 0x120).to_bytes(0x04, 'big'))
    
    #Adding 1 to the file count
    os.write(FAR, (FileTable_Objects + 1).to_bytes(0x04, 'big'))


def ReplaceFile(FileData: bytes, HeaderPos: int):
    os.lseek(FAR, HeaderPos + 0x100, os.SEEK_SET)

    FileData = b'\x00\x00' + zlibcomp.compress(FileData) + zlibcomp.flush() if compressed else FileData
    ReplaceCompSize = len(FileData) + 2 if compressed else len(FileData)
    
    os.write(FAR, Replace_Size.to_bytes(8, 'big'))              # Decompressed size
    os.write(FAR, ReplaceCompSize.to_bytes(8, 'big'))              # Compressed size
    os.write(FAR, (FAR_Size - DataStart).to_bytes(8, 'big'))    # File data offset 
    os.lseek(FAR, 0x03, os.SEEK_CUR)                            
    os.write(FAR, b'\x02' if compressed else b'\x01')           # Compressed flag
    os.lseek(FAR, 0, os.SEEK_END)
    os.write(FAR, FileData)
    print("Injection Done successfully")

def FindFile(Filename):
    i = 0
    while i < FileTable_Objects:
        CurFile = FileNames[i]
        if CurFile == Filename:
            print("File Exists in FAR")
            break
        elif i+1 == FileTable_Objects:
            if add == False:
                print("Invalid File path")
            else:
                print("Path available")
            return [False, 0]
        i+=1

    HeaderPos = i * 0x120 + FileTable_Start
    print("The header of the specified file is located at " + hex(HeaderPos))
    return [True, HeaderPos]

def RenFile(HeaderPos):
    os.lseek(FAR, HeaderPos, os.SEEK_SET)
    os.write(FAR, str(pathlib.PureWindowsPath(Replace)).encode('utf-8'))

def FARInit():
    os.lseek(FAR, 0x00, os.SEEK_SET)
    MagicWord = os.read(FAR, 0x04).decode('utf-8')
    if MagicWord != "FSAR":
        print("Error: The file specified with the --FAR argument isn't a far file, exitting")
        exit(0)
    os.lseek(FAR, 0x08, os.SEEK_SET)
    DataStart = int.from_bytes(os.read(FAR, 0x04), 'big')
    FileTable_Size = DataStart - FileTable_Start
    FileTable_Objects = FileTable_Size // 0x120

    os.lseek(FAR, FileTable_Start, os.SEEK_SET)

    FileNames = [None] * FileTable_Objects
    i = 0
    while i < FileTable_Objects: 
        FileNames[i] = os.read(FAR, 0x100).decode('utf-8')  # Read the filename into the filenames list
        while FileNames[i].find('\x00') != -1:
            FileNames[i] = FileNames[i].strip('\x00')       # Remove all the 0x00 padding (cuz 0x00 is a valid unicode character 😡)
        os.lseek(FAR, 0x20, os.SEEK_CUR)
        i+=1
    return [FileNames, FileTable_Objects, DataStart]

def CapMode():
    print("Welcome to Cap mode!")
    parsed.FAR = input("What's path to your far archive: ")
    mode = input("Enter what you want to do with the archive [add/rename/replace/list files/extract]: ")
    
    if mode.lower() == "add":
        parsed.Replace = input("Good! you want to add a file. Now tell me, what is the path of the file you " + 
                               "want to add: ")
        parsed.FilePath = input("And where do you want to add this file in the archive: ")
        Compress = input("Do you want the newly added file to be compressed [Y/N]: ")
        parsed.compress = True if Compress.lower() == "y" else False
        parsed.add = True

    elif mode.lower() == "replace":
        parsed.FilePath = input("Good! you want to replace a file. Now tell me, what is the path in the " +
                               "archive of the file you want to replace: ")
        parsed.Replace = input("And where is the new file: ")
        Compress = input("Do you want the new file to be compressed [Y/N]: ")
        parsed.compress = True if Compress.lower() == "y" else False
        parsed.replace = True

    elif mode.lower() == "rename":
        parsed.FilePath = str(pathlib.PureWindowsPath(
                            input("Good! you want to rename a file. Now tell me, what is the path in the " + 
                                  "archive of the file you want to rename: ")
                             ))
        tempPath = parsed.FilePath.rsplit('\\', 1)[1] if parsed.FilePath.find('\\') != -1 else parsed.FilePath
        parsed.Replace = input(f"And what is the new filename for {tempPath} (With the extension): ")
        parsed.rename = True

    elif mode.lower() == "extract":
        parsed.FilePath = input("Good! you want to extract a file. Now tell me, what is the path " + 
                               "in the archive of the file you want to extract: ")
        parsed.Replace = input("And where do you want to extract this file: ")
        parsed.Xtract = True

    elif mode.lower() == "list files":
        parsed.listf = True
        
    
if parsed.cap:
    CapMode()

add = parsed.add
rename = parsed.rename
replace = parsed.replace
listf = parsed.listf
compressed = parsed.compress
Xtract = parsed.Xtract

FAR = parsed.FAR
if listf == False:
    FilePath = str(pathlib.PureWindowsPath(parsed.FilePath))
    Replace = parsed.Replace

if rename:
    tempPath = FilePath.rsplit('\\', 1)[0]
    Replace = tempPath + '\\' + Replace if FilePath.find('\\') == -1 else Replace

if compressed:
    zlibcomp = zlib.compressobj(zlib.Z_BEST_COMPRESSION, zlib.DEFLATED, -15)

FileTable_Start = 0x20

FAR_Size = os.path.getsize(FAR)
FAR = os.open(FAR, os.O_RDWR | os.O_BINARY)

if listf == False and rename == False:
    if Xtract == True:   
        Replace = os.open("Extracted_" + Replace if pathlib.Path(Replace).exists() else Replace,
                         os.O_CREAT | os.O_BINARY | os.O_WRONLY)
    else:
        Replace_Size = os.path.getsize(Replace)
        Replace = os.open(Replace, os.O_RDONLY | os.O_BINARY)
        if add or replace:
            Replace_data = os.read(Replace, Replace_Size)

# Gather data from the FAR file
[FileNames, FileTable_Objects, DataStart] = FARInit()

if listf == True:
    for Filename in FileNames:
        print(Filename)
    exit(0)

FoundFile = FindFile(FilePath)

if Xtract == True:
    if FoundFile[0]:
        ExtractFile(Replace, FoundFile[1])
        print("File Successfully extracted")
        exit(0)
    else:
        print(f"Error: File not found in archive, use '{sys.argv[0]} -FAR {parsed.FAR} -ls' to list the files in " +
              "the archive")
        exit(0)

if add == True:
    if FoundFile[0] == True:
        Replace = True
        print("File already exists, replacing instead")
    else:
        AddFile(Replace_data)
        os.fsync(FAR)
        [FileNames, FileTable_Objects, DataStart] = FARInit()
        if FindFile(FilePath)[0]:
            print("File added successfully")
        else:
            print(FileTable_Objects)
            print("oopsies")
        exit(0)

if replace == True:
    ReplaceFile(Replace_data, FoundFile[1])
    print("File successfully replaced")

if rename == True:
    RenFile(FoundFile[1])
    print("File successfully renamed")