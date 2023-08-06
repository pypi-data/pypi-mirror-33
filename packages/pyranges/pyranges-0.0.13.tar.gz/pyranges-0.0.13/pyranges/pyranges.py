import pandas as pd
import numpy as np
from collections import defaultdict

from tabulate import tabulate

from pyranges.methods import (_overlap, _cluster, _tile, _intersection,
                              _coverage, _overlap_write_both,
                              _set_intersection, _set_union, _subtraction, _nearest)


from ncls import NCLS


def create_ncls(cdf):

    return NCLS(cdf.Start.values,
                cdf.End.values,
                cdf.index.values)


def create_ncls_dict(df, strand):

    if not strand:
        grpby = df.groupby("Chromosome")
    else:
        grpby = df.groupby("Chromosome Strand".split())

    nclses = {key: create_ncls(cdf) for (key, cdf) in grpby}
    dd = defaultdict(NCLS)
    dd.update(nclses)

    return dd


def create_pyranges_df(seqnames, starts, ends, strands=None):


    if isinstance(seqnames, str):
        seqnames = pd.Series([seqnames] * len(starts), dtype="category")

    if strands != None and strands != False:

        if isinstance(strands, str):
            strands = pd.Series([strands] * len(starts), dtype="category")

        columns = [seqnames, starts, ends, strands]
        lengths = list(str(len(s)) for s in columns)
        assert len(set(lengths)) == 1, "seqnames, starts, ends and strands must be of equal length. But are {}".format(", ".join(lengths))
        colnames = "Chromosome Start End Strand".split()
    else:
        columns = [seqnames, starts, ends]
        lengths = list(str(len(s)) for s in columns)
        assert len(set(lengths)) == 1, "seqnames, starts and ends must be of equal length. But are {}".format(", ".join(lengths))
        colnames = "Chromosome Start End".split()

    idx = range(len(starts))
    series_to_concat = []
    for s in columns:
        s = pd.Series(s, index=idx)
        series_to_concat.append(s)

    df = pd.concat(series_to_concat, axis=1)
    df.columns = colnames

    return df


def return_empty_if_one_empty(func):

    def extended_func(self, other, **kwargs):

        if len(self) == 0 or len(other) == 0:
            df = pd.DataFrame(columns="Chromosome Start End Strand".split())
        else:
            df = func(self, other, **kwargs)

        return df

    return extended_func


def return_empty_if_both_empty(func):

    def extended_func(self, other, **kwargs):

        if len(self) == 0 and len(other) == 0:
            df = pd.DataFrame(columns="Chromosome Start End Strand".split())
        else:
            df = func(self, other, **kwargs)

        return df

    return extended_func


def pyrange_or_df(func):

    def extension(self, other, **kwargs):
        df = func(self, other, **kwargs)

        if kwargs.get("df_only"):
            return df

        return PyRanges(df)

    return extension


def pyrange_or_df_single(func):

    def extension(self, **kwargs):
        df = func(self, **kwargs)

        if kwargs.get("df_only"):
            return df

        return PyRanges(df)

    return extension


class PyRanges():

    df = None

    def __init__(self, df=None, seqnames=None, starts=None, ends=None, strands=None, copy_df=True):

        df_given = True if not df is None else False

        if df is False or df is None:
            df = create_pyranges_df(seqnames, starts, ends, strands)
        else:
            assert "Chromosome" in df and "Start" in df and "End" in df
            df.index = range(len(df))

        # using __dict__ to avoid invoking setattr
        if "Strand" not in df:
            self.__dict__["stranded"] = False
        else:
            self.__dict__["stranded"] = True

        if copy_df and df_given:
            df = df.copy()
            df.Chromosome = df.Chromosome.astype("category")
            if "Strand" in df:
                df.Strand = df.Strand.astype("category")

        self.__dict__["df"] = df

        self.__dict__["__ncls__"] = create_ncls_dict(df, self.stranded)


    def __len__(self):
        return self.df.shape[0]

    def __setattr__(self, column_name, column):

        if column_name in "Chromosome Start End Strand".split():
            raise Exception("The columns Chromosome, Start, End or Strand can not be reset.")
        if column_name == "stranded":
            raise Exception("The stranded attribute is read-only. Create a new PyRanges object instead.")
        if not isinstance(column, str):
            if not len(self.df) == len(column):
                raise Exception("DataFrame and column must be same length.")

            column_to_insert = pd.Series(column, index=self.df.index)
        else:
            column_to_insert = pd.Series(column, index=self.df.index)

        pos = self.df.shape[1]
        if column_name in self.df:
            pos = list(self.df.columns).index(column_name)
            self.df.drop(column_name, inplace=True, axis=1)

        self.df.insert(pos, column_name, column_to_insert)


    def __getattr__(self, name):

        if name in self.df:
            return self.df[name]
        else:
            self.__dict__[name]

    def __eq__(self, other):

        return self.df.equals(other.df)

    def __getitem__(self, val):

        pd.options.mode.chained_assignment = None
        if isinstance(val, str):
            if val in set(self.df.Chromosome):
                return PyRanges(self.df.loc[self.df.Chromosome == val])
            elif val in "+ -".split():
                return PyRanges(self.df.loc[self.df.Strand == val])
            else:
                raise Exception("Invalid choice for string subsetting PyRanges: {}. Must be either strand or chromosome".format(val))

        elif isinstance(val, tuple):

            # "chr1", 5:10
            if len(val) == 2 and val[0] in self.df.Chromosome.values and isinstance(val[1], slice):
                chromosome, loc = val
                start = loc.start or 0
                stop = loc.stop or max(self.df.loc[self.df.Chromosome == chromosome].End.max(), start)
                idxes = [r[2] for r in self.__ncls__[chromosome, "+"].find_overlap(start, stop)] + \
                        [r[2] for r in self.__ncls__[chromosome, "-"].find_overlap(start, stop)]

                return PyRanges(self.df.loc[idxes])

            # "+", 5:10
            if len(val) == 2 and val[0] in "+ -".split() and isinstance(val[1], slice):
                strand, loc = val
                start = loc.start or 0
                stop = loc.stop or max(self.df.loc[self.df.Chromosome == chromosome].End.max(), start)
                idxes = []
                for chromosome in self.df.Chromosome.drop_duplicates():
                    idxes.extend([r[2] for r in self.__ncls__[chromosome, strand].find_overlap(start, stop)])

                return PyRanges(self.df.loc[idxes])

            # "chr1", "+"
            if len(val) == 2 and val[1] in "+ -".split():

                chromosome, strand = val

                return PyRanges(self.df.loc[(self.df.Chromosome == chromosome) & (self.df.Strand == strand)])

            # "chr1", "+", 5:10
            elif len(val) == 3 and val[0] in self.df.Chromosome.values and val[1] in "+ -".split():

                chromosome, strand, loc = val
                start = loc.start or 0
                stop = loc.stop or max(self.df.loc[self.df.Chromosome == chromosome].End.max(), start)
                idxes = [r[2] for r in self.__ncls__[chromosome, strand].find_overlap(start, stop)]

                return PyRanges(self.df.loc[idxes])

        # 100:999
        elif isinstance(val, slice):

            start = val.start or 0
            stop = val.stop or max(self.df.End.max(), start)

            idxes = []
            for it in self.__ncls__.values():
                idxes.extend([r[2] for r in it.find_overlap(start, stop)])

            return PyRanges(self.df.loc[idxes])

        pd.options.mode.chained_assignment = "warn"


    def __str__(self):

        if len(self.df) > 6:
            h = self.df.head(3).astype(object)
            t = self.df.tail(3).astype(object)
            m = self.df.head(1).astype(object)
            m.loc[:,:] = "..."
            m.index = ["..."]
            s = pd.concat([h, m, t])
        else:
            s = self.df

        str_repr = tabulate(s, headers='keys', tablefmt='psql', showindex=False) + \
                                        "\nPyRanges object has {} sequences from {} chromosomes.".format(self.df.shape[0], len(set(self.df.Chromosome)))
        return str_repr


    def __repr__(self):

        return str(self)


    @pyrange_or_df
    @return_empty_if_one_empty
    def overlap(self, other, strandedness=False, invert=False, how=None, **kwargs):

        "Want all intervals in self that overlap with other."

        df = _overlap(self, other, strandedness, invert, how)

        return df

    @pyrange_or_df
    @return_empty_if_one_empty
    def nearest(self, other, strandedness=False, suffix="_b", how=None, overlap=True, **kwargs):

        "Find the nearest feature in other."

        df = _nearest(self, other, strandedness, suffix, how, overlap)

        return df

    @pyrange_or_df
    @return_empty_if_one_empty
    def intersection(self, other, strandedness=False, how=None):

        "Want the parts of the intervals in self that overlap with other."

        df = _intersection(self, other, strandedness, how)

        return df

    @pyrange_or_df
    @return_empty_if_one_empty
    def set_intersection(self, other, strandedness=False, how=None):

        si = _set_intersection(self, other, strandedness, how)

        return si

    @pyrange_or_df
    @return_empty_if_both_empty
    def set_union(self, other, strand=False):

        si = _set_union(self, other, strand)

        return si


    @pyrange_or_df
    def subtraction(self, other, strandedness=False):

        return _subtraction(self, other, strandedness)


    @pyrange_or_df
    @return_empty_if_one_empty
    def join(self, other, strandedness=False, new_pos=None, suffixes=["_a", "_b"], how=None):

        df = _overlap_write_both(self, other, strandedness, new_pos, suffixes, how)

        return df


    @pyrange_or_df_single
    def cluster(self, strand=None, df_only=False, max_dist=0, min_nb=1):

        df = _cluster(self, strand, max_dist, min_nb)

        return df

    @pyrange_or_df_single
    def tile(self, tile_size=50):

        df = _tile(self, tile_size)
        return df


    def coverage(self, value_col=None, stranded=False):

        return _coverage(self, value_col, stranded=stranded)
