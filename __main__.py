from process.bhprocess import PrePostProc
from process.bhprocessmin import PrePostProcdrop

from utils.toget import ToGet
from datetime import datetime

# from enumlist import gsmrawkpiIndex
# from enumlist import baseline
import enumlist
import time
import os
import sys


def main():
    startTime = time.time()
    print(
        "StartTime: ",
        datetime.fromtimestamp(startTime).strftime("%Y-%m-%d %H:%M:%S"),
    )

    project_dir = os.path.dirname(os.path.abspath(__file__))
    source_folder = os.path.join(project_dir, "input")
    rawkpi = sys.argv[1]

    kpi_process_result = []
    bh_txt = os.path.join(source_folder, "busyhour_data.csv")
    cell_txt = os.path.join(source_folder, "cell_data.csv")
    date_csv = os.path.join(source_folder, "date_data.csv")

    bh_data = ToGet.txtfile_to_list(txtpath=bh_txt)
    cell_data = ToGet.txtfile_to_list(txtpath=cell_txt)
    date_data = ToGet.csv_to_list(csv_file=date_csv, delimiter=",")
    raw_data_csv = ToGet.csv_to_list(csv_file=rawkpi, delimiter=",")

    mockpi_list = [
        "Availability",
        "Call_Setup_Success_Rate",
        "HO_Success_Rate",
        "HO_attempts",
        "HO_UTRAN_Success_Rate",
        "HO_Utran_Attempts",
        "HO_Utran_Success",
        "Voice_Traffic",
        "Traffic_Mb",
        "DL_EGRPS_Throughput",
        "UL_EGRPS_Throughput",
        "Random_Access_Success_Rate",
    ]

    mockpi_list_drop = [
        "Interference_UL_ICM_Band4_Band5",
        "SDCCH_Drop_Rate",
        "Call_Drop_Rate",
        "TbfDrop_Rate",
    ]

    for mockpi in mockpi_list:
        prepostcompare = PrePostProc(
            cell_data=cell_data,
            rawkpi_data=raw_data_csv,
            rawkpi_col=enumlist.gsmrawkpiIndex(),
            date_data=date_data,
            busyhour_data=bh_data,
            baseline_data=enumlist.baseline(),
            mockpi=mockpi,
        )

        kpi_result_avail = prepostcompare.process_kpi()
        kpi_process_result.extend(kpi_result_avail)

    for mockpi in mockpi_list_drop:
        prepostcomparedrop = PrePostProcdrop(
            cell_data=cell_data,
            rawkpi_data=raw_data_csv,
            rawkpi_col=enumlist.gsmrawkpiIndex(),
            date_data=date_data,
            busyhour_data=bh_data,
            baseline_data=enumlist.baseline(),
            mockpi=mockpi,
        )

        kpi_result_avail = prepostcomparedrop.process_kpi()
        kpi_process_result.extend(kpi_result_avail)

    print(kpi_process_result)
    endTime = time.time()
    print(
        "endTime: ",
        datetime.fromtimestamp(endTime).strftime("%Y-%m-%d %H:%M:%S"),
    )

    elapsedTime = endTime - startTime

    if elapsedTime < 60:
        print("Total Run Time (secs): ", round(elapsedTime, 2))
    else:
        elapsedTimeInMins = round(elapsedTime / 60, 2)
        print("Total Run Time (mins): ", elapsedTimeInMins)


if __name__ == "__main__":
    main()
