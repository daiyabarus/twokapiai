from utils.diff import Diff
from datetime import datetime, timedelta
# from eenum.enumflag import Flag


class SUMNodePrePost:
    def __init__(
        self,
        rawhourly_data,
        rawhourly_col,
        rawdaily_data,
        rawdaily_col,
        date_data,
        busyhour_data,
        baseline_data,
        mockpi,
    ):
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

    def _extract_kpi_values(self, include_busy_hour=True):
        pre_date = self._parse_date(self.date_data[0][0])
        post_date = self._parse_date(self.date_data[0][1])
        pre_values = {}
        post_values = {}

        for raw_data in self.rawhourly_data[1:]:
            bsc, date_str, hour = [
                raw_data[self.rawhourly_col[key]]
                for key in ["BSC", "DATE_ID", "HOUR_ID"]
            ]
            date = self._parse_date(date_str)
            if not include_busy_hour or int(hour) in self.busyhour_data:
                kpi_str = raw_data[self.rawhourly_col.get(self.mockpi, None)]
                kpi_value = float(kpi_str) if kpi_str else 0
                if date == pre_date:
                    pre_values.setdefault(bsc, []).append(kpi_value)
                elif date == post_date:
                    post_values.setdefault(bsc, []).append(kpi_value)

        return pre_values, post_values

    def _sum_kpi_values_for_dates(self, values, start_date, end_date):
        sum_values = {}
        for raw_data in self.rawdaily_data[1:]:
            bsc, date_str = [
                raw_data[self.rawdaily_col[key]] for key in ["BSC", "DATE_ID"]
            ]
            date = self._parse_date(date_str)

            if start_date <= date <= end_date:
                kpi_str = raw_data[self.rawdaily_col.get(self.mockpi, None)]
                kpi_value = float(kpi_str) if kpi_str else 0
                sum_values.setdefault(bsc, []).append(kpi_value)

        return {bsc: sum(vals) for bsc, vals in sum_values.items()}

    def process_kpi(self):
        pre_date = self._parse_date(self.date_data[0][0])
        post_date = self._parse_date(self.date_data[0][1])
        baseline_dict = dict(self.baseline_data)
        # inc_kpis = Flag.flag5_inc()
        # dcr_kpis = Flag.flag5_dcr()
        pre_values, post_values = self._extract_kpi_values(False)
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

        kpi_result = []

        for bsc in set(list(pre_sum_oneday.keys()) + list(post_sum_oneday.keys())):
            pre_sum = sum(pre_values.get(bsc, []))
            post_sum = sum(post_values.get(bsc, []))

            # if self.mockpi in inc_kpis:
            #     flag_type = "inc"
            # elif self.mockpi in dcr_kpis:
            #     flag_type = "dcr"
            # else:
            #     flag_type = "unknown"

            prepost_calc = Diff(pre_sum, post_sum)
            # flag_result_prepost = (
            #     prepost_calc.flag5_inc if flag_type == "inc" else prepost_calc.flag5_dcr
            # )

            one_day_calc = Diff(pre_sum_oneday.get(bsc, 0), post_sum_oneday.get(bsc, 0))
            # flag_result_one_day = (
            #     one_day_calc.flag5_inc if flag_type == "inc" else one_day_calc.flag5_dcr
            # )
            #
            twodays_calc = Diff(
                pre_sum_twodays.get(bsc, 0), post_sum_twodays.get(bsc, 0)
            )
            # flag_result_two_days = (
            #     twodays_calc.flag5_inc if flag_type == "inc" else twodays_calc.flag5_dcr
            # )

            oneweek_calc = Diff(
                pre_sum_oneweek.get(bsc, 0), post_sum_oneweek.get(bsc, 0)
            )
            # flag_result_one_week = (
            #     oneweek_calc.flag5_inc if flag_type == "inc" else oneweek_calc.flag5_dcr
            # )

            if baseline_dict.get(self.mockpi) == "SUFFIX":
                post_baseline = post_sum_oneweek.get(bsc, 0)
                pre_baseline = pre_sum_oneweek.get(bsc, 0)
                baseline_calc = Diff(pre_baseline, post_baseline)
                baseline_flag = baseline_calc.threshold_flag_dec
                baseline_delta = baseline_calc.delta_percent
            else:
                pre_baseline = post_sum_oneweek.get(bsc, 0)
                post_baseline = float(baseline_dict.get(self.mockpi, 0))
                baseline_calc = Diff(pre_baseline, post_baseline)
                baseline_flag = baseline_calc.threshold_flag_inc
                baseline_delta = baseline_calc.delta_percent

            kpi_data = [
                bsc,
                self.mockpi,
                # pre_sum,
                # post_sum,
                # prepost_calc.delta,
                # prepost_calc.delta_percent,
                # flag_result_prepost,
                pre_sum_oneday.get(bsc, 0),
                post_sum_oneday.get(bsc, 0),
                one_day_calc.delta,
                one_day_calc.delta_percent,
                one_day_calc.flag5_inc,
                pre_sum_twodays.get(bsc, 0),
                post_sum_twodays.get(bsc, 0),
                twodays_calc.delta,
                twodays_calc.delta_percent,
                twodays_calc.flag5_inc,
                pre_sum_oneweek.get(bsc, 0),
                post_sum_oneweek.get(bsc, 0),
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
