from pandas import read_table
from time import gmtime, strftime

print("\n")
print(strftime("%Y-%m-%d %H:%M:%S", gmtime()))

nrows = int(1e5)
chip = read_table("/mnt/scratch/endrebak/pyranges_benchmark/data/download/chip.bed.gz", nrows=nrows)
bg = read_table("/mnt/scratch/endrebak/pyranges_benchmark/data/download/input.bed.gz", nrows=nrows)
