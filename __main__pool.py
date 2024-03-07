from process.bhprocess import PrePostProc
from process.bhprocessmin import PrePostProcdrop

from utils.toget import ToGet
from datetime import datetime
from enumlist import gsmrawkpiIndex
import time
import os
import sys
import multiprocessing


class MyKPIProcess:
    def __init__(self, mockpi_list, cell_data, raw_data_csv, date_data, bh_data):
        self.mockpi_list = mockpi_list
        self.cell_data = cell_data
        self.raw_data_csv = raw_data_csv
        self.date_data = date_data
        self.bh_data = bh_data

    def process_kpi(self, mockpi):
        if mockpi in [
            "Interference_UL_ICM_Band4_Band5",
            "SDCCH_Drop_Rate",
            "Call_Drop_Rate",
            "TbfDrop_Rate",
        ]:
            prepostcompare = PrePostProcdrop(
                cell_data=self.cell_data,
                rawkpi_data=self.raw_data_csv,
                rawkpi_col=gsmrawkpiIndex(),
                date_data=self.date_data,
                busyhour_data=self.bh_data,
                mockpi=mockpi,
            )
        else:
            prepostcompare = PrePostProc(
                cell_data=self.cell_data,
                rawkpi_data=self.raw_data_csv,
                rawkpi_col=gsmrawkpiIndex(),
                date_data=self.date_data,
                busyhour_data=self.bh_data,
                mockpi=mockpi,
            )

        return prepostcompare.process_kpi()


def main():
    startTime = time.time()
    print(
        "StartTime: ", datetime.fromtimestamp(startTime).strftime("%Y-%m-%d %H:%M:%S")
    )

    project_dir = os.path.dirname(os.path.abspath(__file__))
    source_folder = os.path.join(project_dir, "input")
    rawkpi = sys.argv[1]

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

    my_kpi_process = MyKPIProcess(
        mockpi_list, cell_data, raw_data_csv, date_data, bh_data
    )
    pool = multiprocessing.Pool(processes=len(mockpi_list))
    kpi_results = pool.map(my_kpi_process.process_kpi, mockpi_list)
    pool.close()
    pool.join()

    kpi_process_result = [result for sublist in kpi_results for result in sublist]

    print(kpi_process_result)
    endTime = time.time()
    print("endTime: ", datetime.fromtimestamp(endTime).strftime("%Y-%m-%d %H:%M:%S"))

    elapsedTime = endTime - startTime

    if elapsedTime < 60:
        print("Total Run Time (secs): ", round(elapsedTime, 2))
    else:
        elapsedTimeInMins = round(elapsedTime / 60, 2)
        print("Total Run Time (mins): ", elapsedTimeInMins)


if __name__ == "__main__":
    main()
