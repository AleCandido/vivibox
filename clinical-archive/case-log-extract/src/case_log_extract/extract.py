import pandas as pd


def main(infile, outfile):
    print(f"Input {infile}")
    print(f"Output {outfile}")

    pd.read_excel(infile)

    print("ciao")
