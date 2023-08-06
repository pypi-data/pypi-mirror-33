from pyranges import PyRanges, read_bed
from time import gmtime, strftime

import psutil

def mem():
	print(str(round(psutil.Process().memory_info().rss/1024./1024., 2)) + ' MB')

for i in range(0, int(1e6)):
    print("")
    print(mem())
    print(i)
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    chip = read_bed("/mnt/scratch/endrebak/pyranges_benchmark/data/download/chip_5000000.bed.gz")
    bg = read_bed("/mnt/scratch/endrebak/pyranges_benchmark/data/download/input_5000000.bed.gz")

    result = chip.set_intersection(bg)
