from process.cell_agg import AGGPrePost
from process.cell_sum import SUMPrePost
from process.node_agg import AGGNodePrePost
from process.node_sum import SUMNodePrePost
from eenum.sheet import ResultSheetNaming
from utils.printtofile import PrintToFile
from utils.toget import ToGet
from datetime import datetime
from eenum.enumflag import Flag
from eenum.enumlist import gsmrawkpiIndex, gsmrawkpiindex_daily, baseline
import shutil
import time
import os
import traceback


class ProcessKPI:
    def __init__(self):
        self.project_dir = os.path.dirname(os.path.abspath(__file__))
        self.source_folder = os.path.join(self.project_dir, "input")
        self.source_kpi = os.path.join(self.project_dir, "csv_input")
        self.kpihourly = ToGet.get_listfile_with_prefix(self.source_kpi, "HOURLY")
        self.kpidaily = ToGet.get_listfile_with_prefix(self.source_kpi, "DAILY")
        self.sheet_naming = ResultSheetNaming()
        self.final_path = self._generate_final_path()

    def init(self) -> None:
        try:
            cellbase_ok = self._cellbase()
            nodebase_ok = self._nodebase()

            print("Cellbase", cellbase_ok)
            print("Nodebase", nodebase_ok)

        except Exception:
            errors = traceback.format_exc()
            print(errors)

    def _cellbase(self):
        try:
            kpi_process_result = []

            hourly_raw = [
                os.path.join(self.source_kpi, filename) for filename in self.kpihourly
            ]
            daily_raw = [
                os.path.join(self.source_kpi, filename) for filename in self.kpidaily
            ]

            bh_txt = os.path.join(self.source_folder, "busyhour_data.csv")
            cell_txt = os.path.join(self.source_folder, "cell_data.csv")
            date_csv = os.path.join(self.source_folder, "date_data.csv")

            bh_data = ToGet.txtfile_to_list(txtpath=bh_txt)
            cell_data = ToGet.txtfile_to_list(txtpath=cell_txt)
            date_data = ToGet.csv_to_list(csv_file=date_csv, delimiter=",")
            rawhourly_data = ToGet.csv_files_to_list(
                csv_files=hourly_raw, delimiter=","
            )
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

            is_ok_cellbase = PrintToFile.to_xlsx_offside_noheader_color(
                file_to_save=self.final_path,
                ws_name=self.sheet_naming.cell,
                list_of_contents=kpi_process_result,
                list_of_red=["Fail", "Degrade"],
                list_of_yellow=["Maintain"],
                list_of_green=["Improve", "Pass"],
                col_offside=0,
                starting_row=5,
            )

            return is_ok_cellbase

        except Exception:
            errors = traceback.format_exc()
            print(errors)
            return False

    def _nodebase(self):
        try:
            kpi_node_result = []

            hourly_raw = [
                os.path.join(self.source_kpi, filename) for filename in self.kpihourly
            ]
            daily_raw = [
                os.path.join(self.source_kpi, filename) for filename in self.kpidaily
            ]

            bh_txt = os.path.join(self.source_folder, "busyhour_data.csv")
            date_csv = os.path.join(self.source_folder, "date_data.csv")
            bh_data = ToGet.txtfile_to_list(txtpath=bh_txt)

            date_data = ToGet.csv_to_list(csv_file=date_csv, delimiter=",")
            rawhourly_data = ToGet.csv_files_to_list(
                csv_files=hourly_raw, delimiter=","
            )
            rawdaily_data = ToGet.csv_files_to_list(csv_files=daily_raw, delimiter=",")

            mockpi_agg_list = Flag.mockpi_agg_list()
            mockpi_sum_list = Flag.mockpi_sum_list()

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

            is_ok_nodebase = PrintToFile.to_xlsx_offside_noheader_color(
                file_to_save=self.final_path,
                ws_name=self.sheet_naming.node,
                list_of_contents=kpi_node_result,
                list_of_red=["Fail", "Degrade"],
                list_of_yellow=["Maintain"],
                list_of_green=["Improve", "Pass"],
                col_offside=0,
                starting_row=5,
            )

            return is_ok_nodebase

        except Exception:
            errors = traceback.format_exc()
            print(errors)
            return False

    def _generate_final_path(self):
        try:
            ori_path = "templates/TEMPLATE.xlsx"
            final_folder = "output_result"
            datetime_today = ToGet.get_current_datetime()
            week = ToGet.get_current_week()
            weeknum = int(week) - 1
            weeknum2 = int(weeknum - 1)
            final_filenaming = (
                f"KPI_W{weeknum2}_to_W{weeknum}_GSM_{datetime_today}.xlsx"
            )
            final_path = os.path.join(final_folder, final_filenaming)

            shutil.copyfile(ori_path, final_path)

            print("Final Path:", final_path)

            return final_path

        except Exception:
            errors = traceback.format_exc()
            print(errors)
            return ""

    def process_data(self):
        startTime = time.time()
        print(
            "StartTime: ",
            datetime.fromtimestamp(startTime).strftime("%Y-%m-%d %H:%M:%S"),
        )

        self.init()

        print("Processing data...")

        print("Ending process...")

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
    process_kpi = ProcessKPI()
    process_kpi.process_data()
