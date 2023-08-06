from pyranges import PyRanges, read_bed
from time import gmtime, strftime
from pandas import read_table

#pandas import only
# ==20560== LEAK SUMMARY:
# ==20560==    definitely lost: 164,417 bytes in 87 blocks
# ==20560==    indirectly lost: 0 bytes in 0 blocks
# ==20560==      possibly lost: 197,339 bytes in 150 blocks
# ==20560==    still reachable: 4,537,321 bytes in 6,064 blocks
# ==20560==         suppressed: 0 bytes in 0 blocks


# pandas only
# ==20507== LEAK SUMMARY:
# ==20507==    definitely lost: 164,417 bytes in 87 blocks
# ==20507==    indirectly lost: 0 bytes in 0 blocks
# ==20507==      possibly lost: 209,147 bytes in 170 blocks
# ==20507==    still reachable: 4,545,787 bytes in 6,095 blocks
# ==20507==         suppressed: 0 bytes in 0 blocks


#nopandas
# ==20541== LEAK SUMMARY:
# ==20541==    definitely lost: 0 bytes in 0 blocks
# ==20541==    indirectly lost: 0 bytes in 0 blocks
# ==20541==      possibly lost: 7,288 bytes in 13 blocks
# ==20541==    still reachable: 336,456 bytes in 177 blocks
# ==20541==         suppressed: 0 bytes in 0 blocks
# ==20541==
# ==20541== For counts of detected and suppressed errors, rerun with: -v
# ==20541== Use --track-origins=yes to see where uninitialised values come from
# ==20541== ERROR SUMMARY: 1459 errors from 154 contexts (suppressed: 0 from 0)


# with PyRanges
# ==20422== LEAK SUMMARY:
# ==20422==    definitely lost: 164,417 bytes in 87 blocks
# ==20422==    indirectly lost: 0 bytes in 0 blocks
# ==20422==      possibly lost: 211,275 bytes in 174 blocks
# ==20422==    still reachable: 4,576,651 bytes in 6,173 blocks
# ==20422==         suppressed: 0 bytes in 0 blocks
# ==20422== Reachable blocks (those to which a pointer was found) are not shown.
# ==20422== To see them, rerun with: --leak-check=full --show-leak-kinds=all



# with intersection
# ==20398== LEAK SUMMARY:
# ==20398==    definitely lost: 164,417 bytes in 87 blocks
# ==20398==    indirectly lost: 0 bytes in 0 blocks
# ==20398==      possibly lost: 211,995 bytes in 175 blocks
# ==20398==    still reachable: 4,575,931 bytes in 6,172 blocks
# ==20398==         suppressed: 0 bytes in 0 blocks

# intersection
# ==20893== LEAK SUMMARY:
# ==20893==    definitely lost: 643,025 bytes in 10,058 blocks
# ==20893==    indirectly lost: 0 bytes in 0 blocks
# ==20893==      possibly lost: 232,691 bytes in 229 blocks
# ==20893==    still reachable: 4,585,078 bytes in 6,192 blocks
# ==20893==         suppressed: 0 bytes in 0 blocks
# ==20893==
# ==20893== For counts of detected and suppressed errors, rerun with: -v
# ==20893== Use --track-origins=yes to see where uninitialised values come from
# ==20893== ERROR SUMMARY: 51395 errors from 441 contexts (suppressed: 0 from 0)

nrows = int(1e5)

chip = read_table("/mnt/scratch/endrebak/pyranges_benchmark/data/download/chip.bed.gz", nrows=nrows, names="Chromosome Start End Strand".split(), usecols=[0, 1, 2, 5])
bg = read_table("/mnt/scratch/endrebak/pyranges_benchmark/data/download/input.bed.gz", nrows=nrows, names="Chromosome Start End Strand".split(), usecols=[0, 1, 2, 5])

c = PyRanges(chip)
b = PyRanges(bg)

c.intersection(b)
