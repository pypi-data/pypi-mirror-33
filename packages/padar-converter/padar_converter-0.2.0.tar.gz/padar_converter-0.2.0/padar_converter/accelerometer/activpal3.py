import pandas as pd


def convert_activpal3_csv(data):
    output = data.copy(deep=True)
    output = output.iloc[:,0:4]
    output.columns = ['HEADER_TIME_STAMP', 'X', 'Y', 'Z']
    output["HEADER_TIME_STAMP"] = pd.to_datetime(output["HEADER_TIME_STAMP"] * 60 * 60 * 24, origin=pd.Timestamp('1899-12-30'), unit='s').astype('datetime64[ms]')
    output.iloc[:,1:4] = (output.iloc[:,1:4] - 127) / 2**8 * 4
    return output


if __name__ == '__main__':
    import sys
    d = pd.read_csv(sys.argv[1],header=None)
    o = convert_activpal3_csv(d)
    print(o.head())