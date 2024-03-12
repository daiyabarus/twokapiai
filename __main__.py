from process.cell_agg import AGGPrePost
from process.cell_sum import SUMPrePost
from process.node_agg import AGGNodePrePost
from process.node_sum import SUMNodePrePost

from utils.toget import ToGet
from datetime import datetime
from eenum.enumflag import Flag

from eenum.enumlist import gsmrawkpiIndex, gsmrawkpiindex_daily, baseline

import time
import os


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
    kpi_node_result = []

    hourly_raw = [os.path.join(source_kpi, filename) for filename in kpihourly]
    daily_raw = [os.path.join(source_kpi, filename) for filename in kpidaily]

    bh_txt = os.path.join(source_folder, "busyhour_data.csv")
    cell_txt = os.path.join(source_folder, "cell_data.csv")
    date_csv = os.path.join(source_folder, "date_data.csv")

    bh_data = ToGet.txtfile_to_list(txtpath=bh_txt)
    cell_data = ToGet.txtfile_to_list(txtpath=cell_txt)
    date_data = ToGet.csv_to_list(csv_file=date_csv, delimiter=",")
    rawhourly_data = ToGet.csv_files_to_list(csv_files=hourly_raw, delimiter=",")
    rawdaily_data = ToGet.csv_files_to_list(csv_files=daily_raw, delimiter=",")

    mockpi_agg_list = Flag.mockpi_agg_list()
    mockpi_sum_list = Flag.mockpi_sum_list()

    for mockpi in mockpi_agg_list:
        aggprepost_compare = AGGPrePost(
            cell_data=cell_data,
            rawhourly_data=rawhourly_data,
            rawhourly_col=gsmrawkpiIndex(),
            rawdaily_data=rawdaily_data,
            rawdaily_col=gsmrawkpiindex_daily(),
            date_data=date_data,
            busyhour_data=bh_data,
            baseline_data=baseline(),
            mockpi=mockpi,
        )

        kpi_result = aggprepost_compare.process_kpi()
        kpi_process_result.extend(kpi_result)

    for mockpi in mockpi_sum_list:
        sumprepost_compare = SUMPrePost(
            cell_data=cell_data,
            rawhourly_data=rawhourly_data,
            rawhourly_col=gsmrawkpiIndex(),
            rawdaily_data=rawdaily_data,
            rawdaily_col=gsmrawkpiindex_daily(),
            date_data=date_data,
            busyhour_data=bh_data,
            baseline_data=baseline(),
            mockpi=mockpi,
        )

        kpi_result = sumprepost_compare.process_kpi()
        kpi_process_result.extend(kpi_result)

    for mockpi in mockpi_agg_list:
        aggprepost_node_compare = AGGNodePrePost(
            rawhourly_data=rawhourly_data,
            rawhourly_col=gsmrawkpiIndex(),
            rawdaily_data=rawdaily_data,
            rawdaily_col=gsmrawkpiindex_daily(),
            date_data=date_data,
            busyhour_data=bh_data,
            baseline_data=baseline(),
            mockpi=mockpi,
        )

        kpi_result = aggprepost_node_compare.process_kpi()
        kpi_node_result.extend(kpi_result)

    for mockpi in mockpi_sum_list:
        sumprepost_node_compare = SUMNodePrePost(
            rawhourly_data=rawhourly_data,
            rawhourly_col=gsmrawkpiIndex(),
            rawdaily_data=rawdaily_data,
            rawdaily_col=gsmrawkpiindex_daily(),
            date_data=date_data,
            busyhour_data=bh_data,
            baseline_data=baseline(),
            mockpi=mockpi,
        )

        kpi_result = sumprepost_node_compare.process_kpi()
        kpi_node_result.extend(kpi_result)

    print(kpi_process_result)
    print(kpi_node_result)

    endTime = time.time()
    print(
        "EndTime: ",
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

