class Flag:
    @staticmethod
    def flag5_inc():
        return [
            "Availability",
            "Call_Setup_Success_Rate",
            "HO_Success_Rate",
            "HO_UTRAN_Success_Rate",
            "DL_EGRPS_Throughput",
            "UL_EGRPS_Throughput",
            "Random_Access_Success_Rate",
            "HO_attempts",
            "HO_Utran_Attempts",
            "Voice_Traffic",
            "Traffic_Mb",
        ]

    @staticmethod
    def flag5_dcr():
        return [
            "Interference_UL_ICM_Band4_Band5",
            "SDCCH_Drop_Rate",
            "Call_Drop_Rate",
            "TbfDrop_Rate",
        ]
