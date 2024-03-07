from utils.aggr import Aggr
from datetime import datetime


class PrePostProc:
    def __init__(
        self,
        cell_data,
        rawkpi_data,
        rawkpi_col,
        date_data,
        busyhour_data,
        baseline_data,
        mockpi,
    ):
        self.cell_data = cell_data
        self.rawkpi_data = rawkpi_data
        self.rawkpi_col = rawkpi_col
        self.date_data = date_data
        self.busyhour_data = busyhour_data
        self.baseline_data = baseline_data
        self.mockpi = mockpi

    def _parse_date(self, date_str):
        return datetime.strptime(date_str, "%m/%d/%Y").date()

    def _get_bsc(self, raw_data):
        return raw_data[self.rawkpi_col.get("BSC", 3)]

    def _extract_kpi_values(self):
        pre_values = {cell: [] for cell in self.cell_data}
        post_values = {cell: [] for cell in self.cell_data}

        pre_date = self._parse_date(self.date_data[0][0])
        post_date = self._parse_date(self.date_data[0][1])

        for raw_data in self.rawkpi_data[1:]:
            cell, date_str, hour = [
                raw_data[self.rawkpi_col.get(key, idx)]
                for key, idx in [
                    ("CELL_NAME", 2),
                    ("DATE_ID", 0),
                    ("HOUR_ID", 1),
                ]
            ]
            date = self._parse_date(date_str)

            if cell in self.cell_data and hour in self.busyhour_data:
                kpi_str = raw_data[self.rawkpi_col.get(self.mockpi, None)]
                if kpi_str:
                    kpi_value = float(kpi_str)
                else:
                    kpi_value = 0

                if date == pre_date:
                    pre_values[cell].append(kpi_value)

                elif date == post_date:
                    post_values[cell].append(kpi_value)

        return pre_values, post_values

    def process_kpi(self):
        pre_values, post_values = self._extract_kpi_values()
        kpi_result = []
        baseline_dict = dict(self.baseline_data)

        for cell in self.cell_data:
            pre_avg = (
                round(sum(pre_values[cell]) / len(pre_values[cell]), 2)
                if pre_values[cell]
                else 0
            )
            post_avg = (
                round(sum(post_values[cell]) / len(post_values[cell]), 2)
                if post_values[cell]
                else 0
            )

            prepost_calc = Aggr(pre_avg, post_avg)
            bsc = self._get_bsc(self.rawkpi_data[1])

            flag_to_use = "flag"
            if baseline_dict.get(self.mockpi) == "SUFFIX":
                baseline_value = post_avg
                baseline_calc = Aggr(pre_avg, post_avg)
                flag_to_use = "flag10"
            else:
                baseline_value = float(baseline_dict.get(self.mockpi, 0))
                baseline_calc = Aggr(post_avg, baseline_value)
                flag_to_use = "flagdrop10"

            kpi_data = [
                bsc,
                cell,
                self.mockpi,
                pre_avg,
                post_avg,
                prepost_calc.delta,
                prepost_calc.delta_percent,
                prepost_calc.flag,
                baseline_calc.delta,
                baseline_calc.delta_percent,
                getattr(baseline_calc, flag_to_use),
            ]
            kpi_result.append(kpi_data)

        return kpi_result

