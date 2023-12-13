# The first four lines implement the core functionality, the fifth limits the number of results,
# while the last two lines provide the nice human-readable output that looks like this:
#     ...
#     0d99bb931299  530KiB path/to/some-image.jpg
#     2ba44098e28f   12MiB path/to/hires-image.png
#     bd1741ddce0d   63MiB path/to/some-video-1080p.mp4

# pipe it through tac command to sort the answer reverse
git rev-list --objects --all |
  git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' |
  sed -n 's/^blob //p' |
  sort --numeric-sort --key=2 |
  tail -n 10 |
  cut -c 1-12,41- |
  $(command -v gnumfmt || echo numfmt) --field=2 --to=iec-i --suffix=B --padding=7 --round=nearest

# To exclude files that are present in HEAD, insert the following line:
grep -vF --file=<(git ls-tree -r HEAD | awk '{print $3}') |

# To show only files exceeding given size (e.g. 1 MiB = 220 B), insert the following line:
awk '$2 >= 2^20' |

# Understanding the meaning of the displayed file size
# What this script displays is the size each file would have in the working directory.
# If you want to see how much space a file occupies if not checked out,
# you can use %(objectsize:disk) instead of %(objectsize).
# However, mind that this metric also has its caveats, as is mentioned in the documentation.

git rev-list --objects --all |
  git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' |
  awk '/^blob/ {print substr($0,6)}' |
  awk '$2 >= 100*1024^2' |
  sort --numeric-sort --key=2 --reverse |
  cut --complement --characters=13-40 |
  numfmt --field=2 --to=iec-i --suffix=B --padding=7 --round=nearest

git ls-tree -r -t -l --full-name HEAD | sort -n -k 4 | tail -n 10

