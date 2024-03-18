from utils.diff import Diff
from datetime import datetime, timedelta
# from enumflag import Flag


class SUMPrePost:
    def __init__(
        self,
        cell_data,
        rawhourly_data,
        rawhourly_col,
        rawdaily_data,
        rawdaily_col,
        date_data,
        busyhour_data,
        baseline_data,
        mockpi,
    ):
        self.cell_data = cell_data
        self.rawhourly_data = rawhourly_data
        self.rawhourly_col = rawhourly_col
        self.rawdaily_data = rawdaily_data
        self.rawdaily_col = rawdaily_col
        self.date_data = date_data
        self.busyhour_data = busyhour_data
        self.baseline_data = baseline_data
        self.mockpi = mockpi

    def _parse_date(self, date_str):
        return datetime.strptime(date_str, "%m/%d/%Y").date()

    def _get_bsc(self, cell_name):
        for raw_data in self.rawdaily_data[1:]:
            if raw_data[self.rawdaily_col.get("CELL_NAME", 1)] == cell_name:
                return raw_data[self.rawdaily_col.get("BSC", 2)]
        return "UNDEFINED"

    def _extract_kpi_values(self, include_busy_hour=True):
        pre_values = {cell: [] for cell in self.cell_data}
        post_values = {cell: [] for cell in self.cell_data}

        pre_date = self._parse_date(self.date_data[0][0])
        post_date = self._parse_date(self.date_data[0][1])

        for raw_data in self.rawhourly_data[1:]:
            cell, date_str, hour = [
                raw_data[self.rawhourly_col.get(key, idx)]
                for key, idx in [
                    ("CELL_NAME", 2),
                    ("DATE_ID", 0),
                    ("HOUR_ID", 1),
                ]
            ]
            date = self._parse_date(date_str)

            if cell in self.cell_data:
                if include_busy_hour or hour not in self.busyhour_data:
                    kpi_str = raw_data[self.rawhourly_col.get(self.mockpi, None)]
                    kpi_value = float(kpi_str) if kpi_str else 0

                    if date == pre_date:
                        pre_values[cell].append(kpi_value)
                    elif date == post_date:
                        post_values[cell].append(kpi_value)

        return pre_values, post_values

    def _sum_kpi_values_for_dates(self, values, start_date, end_date):
        sum_values = {cell: [] for cell in self.cell_data}
        for raw_data in self.rawdaily_data[1:]:
            cell, date_str, _ = [
                raw_data[self.rawdaily_col.get(key, idx)]
                for key, idx in [("CELL_NAME", 1), ("DATE_ID", 0), ("BSC", 2)]
            ]
            date = self._parse_date(date_str)

            if cell in self.cell_data and start_date <= date <= end_date:
                kpi_str = raw_data[self.rawdaily_col.get(self.mockpi, None)]
                kpi_value = float(kpi_str) if kpi_str else 0
                sum_values[cell].append(kpi_value)

        return {cell: sum(vals) for cell, vals in sum_values.items()}

    def process_kpi(self):
        pre_values, post_values = self._extract_kpi_values(False)
        kpi_result = []
        baseline_dict = dict(self.baseline_data)

        pre_date = self._parse_date(self.date_data[0][0])
        post_date = self._parse_date(self.date_data[0][1])
        # inc_kpis = Flag.flag5_inc()
        # dcr_kpis = Flag.flag5_dcr()
        #
        pre_sum_oneday = self._sum_kpi_values_for_dates(pre_values, pre_date, pre_date)

        post_sum_oneday = self._sum_kpi_values_for_dates(
            post_values, post_date, post_date
        )

        pre_sum_twodays = self._sum_kpi_values_for_dates(
            pre_values, pre_date, pre_date + timedelta(days=1)
        )
        post_sum_twodays = self._sum_kpi_values_for_dates(
            post_values, post_date - timedelta(days=1), post_date
        )

        pre_sum_oneweek = self._sum_kpi_values_for_dates(
            pre_values, pre_date, pre_date + timedelta(days=6)
        )
        post_sum_oneweek = self._sum_kpi_values_for_dates(
            post_values, post_date - timedelta(days=6), post_date
        )

        for cell in self.cell_data:
            pre_sum = sum(pre_values[cell]) if pre_values[cell] else 0
            post_sum = sum(post_values[cell]) if post_values[cell] else 0

            prepost_calc = Diff(pre_sum, post_sum)
            bsc = self._get_bsc(cell)

            one_day_calc = Diff(pre_sum_oneday[cell], post_sum_oneday[cell])
            twodays_calc = Diff(pre_sum_twodays[cell], post_sum_twodays[cell])
            oneweek_calc = Diff(pre_sum_oneweek[cell], post_sum_oneweek[cell])

            if baseline_dict.get(self.mockpi) == "SUFFIX":
                post_baseline = post_sum_oneweek[cell]
                pre_baseline = pre_sum_oneweek[cell]
                baseline_calc = Diff(pre_baseline, post_baseline)
                baseline_flag = baseline_calc.threshold_flag_dec
                baseline_delta = baseline_calc.delta_percent
            else:
                pre_baseline = post_sum_oneweek[cell]
                post_baseline = float(baseline_dict.get(self.mockpi, 0))
                baseline_calc = Diff(pre_baseline, post_baseline)
                baseline_flag = baseline_calc.threshold_flag_inc
                baseline_delta = baseline_calc.delta_percent

            kpi_data = [
                bsc,
                cell,
                self.mockpi,
                pre_sum,
                post_sum,
                prepost_calc.delta,
                prepost_calc.delta_percent,
                prepost_calc.flag5_inc,
                pre_sum_oneday[cell],
                post_sum_oneday[cell],
                one_day_calc.delta,
                one_day_calc.delta_percent,
                one_day_calc.flag5_inc,
                pre_sum_twodays[cell],
                post_sum_twodays[cell],
                twodays_calc.delta,
                twodays_calc.delta_percent,
                twodays_calc.flag5_inc,
                pre_sum_oneweek[cell],
                post_sum_oneweek[cell],
                oneweek_calc.delta,
                oneweek_calc.delta_percent,
                oneweek_calc.flag5_inc,
                pre_baseline,
                post_baseline,
                baseline_delta,
                baseline_flag,
            ]
            kpi_result.append(kpi_data)

        return kpi_result
