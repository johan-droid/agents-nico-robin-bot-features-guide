#!/bin/bash
set -e

rm -rf test_repo
mkdir test_repo
cd test_repo
git init
git config user.email "test@example.com"
git config user.name "Test User"
git checkout -b main

# 1. Both modified same line
echo "base" > same_line.txt

# 2. One deleted, other modified
echo "base" > deleted_modified.txt

# 3. Binary file conflict
dd if=/dev/urandom of=binary.bin bs=1024 count=1 2>/dev/null

# 4. Large file (>5 MB)
dd if=/dev/urandom of=large.bin bs=1024 count=5120 2>/dev/null

# 5. Rename vs modify
echo "base" > rename_modify.txt

# 6. Encoding mismatch (UTF-8 vs ISO-8859-1)
printf "base\n" | iconv -f UTF-8 -t ISO-8859-1 > encoding.txt

git add .
git commit -m "Base commit"

# Branch 'theirs'
git checkout -b theirs
echo "theirs" > same_line.txt
echo "modified by theirs" > deleted_modified.txt
dd if=/dev/urandom of=binary.bin bs=1024 count=1 2>/dev/null
dd if=/dev/urandom of=large.bin bs=1024 count=5120 2>/dev/null
git rm rename_modify.txt
echo "theirs" > renamed_theirs.txt
printf "theirs\n" | iconv -f UTF-8 -t ISO-8859-1 > encoding.txt

git add .
git commit -m "Theirs commit"

# Branch 'ours'
git checkout main
git checkout -b ours
echo "ours" > same_line.txt
git rm deleted_modified.txt
dd if=/dev/urandom of=binary.bin bs=1024 count=1 2>/dev/null
dd if=/dev/urandom of=large.bin bs=1024 count=5120 2>/dev/null
echo "ours modify" > rename_modify.txt
printf "ours\n" > encoding.txt

git add .
git commit -m "Ours commit"

# Create conflict
set +e
git merge theirs
set -e

echo "Conflicts created. Running dry-run..."
../src/merge/resolver.py --dry-run

echo "Running backup..."
../src/merge/resolver.py --backup --dry-run

echo "Resolving with ours..."
../src/merge/resolver.py --strategy ours

echo "Status after resolution:"
git status

echo "Rolling back..."
../src/merge/resolver.py --rollback

echo "Status after rollback:"
git status

cd ..
