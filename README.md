# FARtools
A python script to *easily* edit and read .far archives from Guitar Hero Live

## Arguments

`-h`    or  `--help`        to show the help text

`--cap` or  `--easy`        to enable cap mode, intended to be used for people who aren't familiar with the command prompt

`-a`    or  `--add`         to add a new file to the archive

`-rn`   or  `--rename`      to rename an already existing file in the archive

`-rp`   or  `--replace`     to replace an already existing file in the archive

`-ls`   or  `--listfiles`   to list the files in the archive

`-c`    or  `--compress`    to compress the file

`-x`    or  `--extract`     to extract a file from the archive

`-xa`   or  `--extractAll`  to extract all files from the archive

`--FAR archive.far`          Archive to modify (Keep backups in case something goes wrong!!!)

`-p FilePath` or `--path FilePath` Has multiple uses depending on the other arguments
- The path of the new file in the case of `-a`
- The path to the file to replace in the case of `-rp`
- The path to the file to rename in the case of `-rn`
- The path to the file to extract in the case of `-x`

`-f FILE` or `--file FILE`  Has multiple uses depending on the other arguments
- The file to add in the archive in the case of `-a`
- The file to replace in the archive in the case of `-rp`
- The new name of the file in the case of `-rn` (Hello consistency issues 😅)
- The file to extract the data to in the case of `-x`
- The output folder in the case of `-xa`

`-o outfile` or `--output outfile` Virtually the same as `-f`, but intended to be used with `-x` and `-xa`