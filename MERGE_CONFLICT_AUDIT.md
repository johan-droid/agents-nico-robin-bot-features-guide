# Git Merge Resolver Audit

## Overview
The resolver handles unmerged files via `git ls-files -u` by extracting the unique conflicting files. It identifies `stage 2` (ours) and `stage 3` (theirs). Based on the chosen strategy (`ours` or `theirs`), it either executes `git checkout --ours/theirs -- <file>` followed by `git add` for modifications, or `git rm <file>` if the file was deleted in the chosen branch.

## Test Cases Covered

1. **Both modified same line**
   - **Command**: `echo "base" > same_line.txt` (base) -> `echo "theirs" > same_line.txt` (theirs) -> `echo "ours" > same_line.txt` (ours)
   - **Output**: `Resolving same_line.txt using strategy 'ours'` -> `git checkout --ours -- same_line.txt`

2. **One deleted, other modified**
   - **Command**: `echo "base" > deleted_modified.txt` (base) -> `echo "modified by theirs" > deleted_modified.txt` (theirs) -> `git rm deleted_modified.txt` (ours)
   - **Output**: `Resolving deleted_modified.txt using strategy 'ours'` -> `git rm deleted_modified.txt` (because it's missing in stage 2).

3. **Binary file conflict**
   - **Command**: `dd if=/dev/urandom of=binary.bin`
   - **Output**: `Resolving binary.bin using strategy 'ours'` -> `git checkout --ours -- binary.bin`

4. **Large file (>5 MB)**
   - **Command**: `dd if=/dev/urandom of=large.bin bs=1024 count=5120`
   - **Output**: `Resolving large.bin using strategy 'ours'` -> `git checkout --ours -- large.bin`

5. **Rename vs modify**
   - **Command**: `echo "base" > rename_modify.txt` -> `git rm rename_modify.txt` (theirs) -> `echo "ours modify" > rename_modify.txt` (ours)
   - **Output**: `Resolving rename_modify.txt using strategy 'ours'` -> `git checkout --ours -- rename_modify.txt` (Note: the rename itself is automatically staged as a new file by git).

6. **Encoding mismatch (UTF-8 vs ISO-8859-1)**
   - **Command**: `printf "base\n" | iconv -f UTF-8 -t ISO-8859-1 > encoding.txt`
   - **Output**: `Resolving encoding.txt using strategy 'ours'` -> `git checkout --ours -- encoding.txt`

## Preventive Improvements Added

1. **`--backup` flag**: Copies `.git/MERGE_MSG` and `.git/index` to `.bak` files before starting resolution.
2. **`--dry-run` flag**: Prints out actions and logs them without executing git commands.
3. **Logging**: All actions are logged to `.merge_resolver.log` with an ISO timestamp, file name, and resolution choice.
4. **`--rollback` command**: Restores `.git/MERGE_MSG` and `.git/index` from the `.bak` backups created by `--backup`.

## Example Log Entry (Dry-Run)
```
[2026-05-15T09:15:22.873557] [DRY-RUN] Resolving deleted_modified.txt using strategy 'ours'
[2026-05-15T09:15:22.873749] [DRY-RUN] Resolving binary.bin using strategy 'ours'
[2026-05-15T09:15:22.873802] [DRY-RUN] Resolving same_line.txt using strategy 'ours'
```
