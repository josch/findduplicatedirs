Description
-----------

Give a directory, find all transitive subdirectories of which two or more
duplicates exist.

Two directories are considered a duplicate of each other if their sha256
checksums are equal. A directory's sha256 checksum is calculated from the
concatenation of the following content of the directory:

 - all file names
 - all file contents
 - the targets of all symlinks (links are not followed)
 - all direct subdirectory names
 - the sha256 of its direct subdirectories

To avoid clutter, only those duplicate directories are printed for which at
least one parent directory has a different hash from the others. This avoids
printing duplicate directories for which their parents are also all the exact
duplicate of each other.

The output format has 4 or more columns separated by tabs. The first column
lists the diskusage as it would be returned by `du -b`. The second column lists
the amount of elements in this sub directory tree as it would be returned by
`find | wc -l`. All subsequent columns list the duplicate directories with the
same content.
