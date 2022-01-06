import re

import pandas as pd


def validate(infile, outfile):
    if not infile.exists():
        raise FileNotFoundError("No input file")
    if outfile.exists():
        raise FileExistsError("Cowardly refusing to overwrite existing file")


def load(infile):
    return InputDataFrame(pd.read_excel(infile))


def main(wrapdf, outfile):
    wrapdf.drop_empty_rows()
    wrapdf.drop_id1()
    wrapdf.diagnosis_split_question()
    wrapdf.diagnosis_normalize()
    wrapdf.save(outfile)


class InputDataFrame:
    def __init__(self, df):
        self.df = df

    def drop_empty_rows(self):
        self.df.dropna(how="all", inplace=True)

    def drop_id1(self):
        df = self.df
        if "Patient ID.1" in df:
            assert all(
                (df["Patient ID"] == df["Patient ID.1"])
                | ((df["Patient ID"].isna()) & df["Patient ID.1"].isna())
            )
            self.df.drop(columns=["Patient ID.1"], inplace=True)

    def diagnosis_split_question(self):
        """New field is not only true/false, but also which one, since multiple
        diagnosis allowed, and not all of them have to be uncertain if one
        is.
        """
        pass

    def diagnosis_normalize(self):
        diagnosis = self.df["Diagnosis"].apply(
            lambda s: [
                re.sub(r"\s+", " ", f.strip()).replace(" ", "_")
                for f in s.lower().strip().split("_x001d_")
            ]
            if isinstance(s, str)
            else []
            if s != s
            else (1 / 0, s)  # raise an error
        )
        self.df["Diagnosis"] = diagnosis.apply(lambda l: " ".join(l))

    def save(self, out):
        writer = pd.ExcelWriter(out)
        self.df.to_excel(writer, "case log")
        writer.save()
