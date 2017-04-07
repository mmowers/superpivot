import gams
import os
import pandas as pd
import gdxcc

def get_df(file_name, param_name):
    ws = gams.GamsWorkspace()

    gdxFile = os.path.join(os.getcwd(), file_name)

    gdxHandle = gdxcc.new_gdxHandle_tp()
    rc =  gdxcc.gdxCreate(gdxHandle, gdxcc.GMS_SSSIZE)
    assert rc[0],rc[1]
    assert gdxcc.gdxOpenRead(gdxHandle, gdxFile)[0]
    nrUels = gdxcc.gdxUMUelInfo(gdxHandle)[1]
    uelMap = []

    for i in range(nrUels+1):
        uelMap.append(gdxcc.gdxUMUelGet(gdxHandle, i)[1])
    ret, symNr = gdxcc.gdxFindSymbol(gdxHandle, param_name)
    assert ret, param_name + " parameter not found"
    ret, nrRecs = gdxcc.gdxDataReadRawStart(gdxHandle, symNr)
    assert ret, "Error in gdxDataReadRawStart: " + gdxcc.gdxErrorStr(gdxHandle, gdxcc.gdxGetLastError(gdxHandle))[1]

    ls = []
    for i in range(nrRecs):
        ret = gdxcc.gdxDataReadRaw(gdxHandle)
        sets = [uelMap[x] for x in ret[1]]
        val = ret[2][gdxcc.GMS_VAL_LEVEL]
        if val == 5e300:
            val = 0
        ls.append(sets+[val])

    assert not gdxcc.gdxClose(gdxHandle)
    assert gdxcc.gdxFree(gdxHandle)
    df = pd.DataFrame(ls)
    return df

if __name__ == "__main__":
    import sys
    df = get_df(sys.argv[1], sys.argv[2])
    print(df)