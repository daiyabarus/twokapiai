from process.cell_agg import AGGPrePost
from process.cell_sum import SUMPrePost

from utils.toget import ToGet
from datetime import datetime

import enumlist
import time
import os
# import sys


def main():
    startTime = time.time()
    print(
        "StartTime: ",
        datetime.fromtimestamp(startTime).strftime("%Y-%m-%d %H:%M:%S"),
    )

    project_dir = os.path.dirname(os.path.abspath(__file__))
    source_folder = os.path.join(project_dir, "input")
    source_kpi = os.path.join(project_dir, "csv_input")
    kpihourly = ToGet.get_listfile_with_prefix(source_kpi, "HOURLY")
    kpidaily = ToGet.get_listfile_with_prefix(source_kpi, "DAILY")

    kpi_process_result = []
    hourly_raw = [os.path.join(source_kpi, filename) for filename in kpihourly]
    daily_raw = [os.path.join(source_kpi, filename) for filename in kpidaily]
    print(f"{hourly_raw}")
    print(f"{daily_raw}")
    print(f"{kpihourly}")
    bh_txt = os.path.join(source_folder, "busyhour_data.csv")
    cell_txt = os.path.join(source_folder, "cell_data.csv")
    date_csv = os.path.join(source_folder, "date_data.csv")

    bh_data = ToGet.txtfile_to_list(txtpath=bh_txt)
    cell_data = ToGet.txtfile_to_list(txtpath=cell_txt)
    date_data = ToGet.csv_to_list(csv_file=date_csv, delimiter=",")
    rawhourly_data = ToGet.csv_files_to_list(csv_files=hourly_raw, delimiter=",")
    rawdaily_data = ToGet.csv_files_to_list(csv_files=daily_raw, delimiter=",")

    mockpi_agg_list = [
        "Availability",
        "Call_Setup_Success_Rate",
        "HO_Success_Rate",
        "HO_UTRAN_Success_Rate",
        "DL_EGRPS_Throughput",
        "UL_EGRPS_Throughput",
        "Random_Access_Success_Rate",
        "Interference_UL_ICM_Band4_Band5",
        "SDCCH_Drop_Rate",
        "Call_Drop_Rate",
        "TbfDrop_Rate",
    ]

    mockpi_sum_list = [
        "HO_attempts",
        "HO_Utran_Attempts",
        "Voice_Traffic",
        "Traffic_Mb",
    ]

    for mockpi in mockpi_agg_list:
        aggprepost_compare = AGGPrePost(
            cell_data=cell_data,
            rawhourly_data=rawhourly_data,
            rawhourly_col=enumlist.gsmrawkpiIndex(),
            rawdaily_data=rawdaily_data,
            rawdaily_col=enumlist.gsmrawkpiindex_daily(),
            date_data=date_data,
            busyhour_data=bh_data,
            baseline_data=enumlist.baseline(),
            mockpi=mockpi,
        )

        kpi_result_avail = aggprepost_compare.process_kpi()
        kpi_process_result.extend(kpi_result_avail)

    for mockpi in mockpi_sum_list:
        sumprepost_compare = SUMPrePost(
            cell_data=cell_data,
            rawhourly_data=rawhourly_data,
            rawhourly_col=enumlist.gsmrawkpiIndex(),
            rawdaily_data=rawdaily_data,
            rawdaily_col=enumlist.gsmrawkpiindex_daily(),
            date_data=date_data,
            busyhour_data=bh_data,
            baseline_data=enumlist.baseline(),
            mockpi=mockpi,
        )

        kpi_result_avail = sumprepost_compare.process_kpi()
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
