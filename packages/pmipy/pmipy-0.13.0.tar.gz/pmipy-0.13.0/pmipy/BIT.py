# BIT.py


def main(sheet, filepath1, filepath2, filepath3, filepath4, period_num):
    if sheet == 'sheet2':
        from pmipy.BITauto import BIT_sheet2
        BIT_sheet2.BIT_automation(filepath1, filepath2, filepath3, filepath4, period_num)
    elif sheet == 'sheet3':
        from pmipy.BITauto import BIT_sheet3
        BIT_sheet3.BIT_automation(filepath1, filepath2, filepath3, filepath4, period_num)
    elif sheet == 'sheet4':
        from pmipy.BITauto import BIT_sheet4
        BIT_sheet4.BIT_automation(filepath1, filepath2, filepath3, filepath4, period_num)
    elif sheet == 'sheet5':
        from pmipy.BITauto import BIT_sheet5
        BIT_sheet5.BIT_automation(filepath1, filepath2, filepath3, filepath4, period_num)
    elif sheet == 'sheet6':
        from pmipy.BITauto import BIT_sheet6
        BIT_sheet6.BIT_automation(filepath1, filepath2, filepath3, filepath4, period_num)
    elif sheet == 'sheet7':
        from pmipy.BITauto import BIT_sheet7
        BIT_sheet7.BIT_automation(filepath1, filepath2, filepath3, filepath4, period_num)
    elif sheet == 'all':
        from pmipy.BITauto import BIT_sheet2
        from pmipy.BITauto import BIT_sheet3
        from pmipy.BITauto import BIT_sheet4
        from pmipy.BITauto import BIT_sheet5
        from pmipy.BITauto import BIT_sheet6
        from pmipy.BITauto import BIT_sheet7
        BIT_sheet2.BIT_automation(filepath1, filepath2, filepath3, filepath4, period_num)
        BIT_sheet3.BIT_automation(filepath1, filepath2, filepath3, filepath4, period_num)
        BIT_sheet4.BIT_automation(filepath1, filepath2, filepath3, filepath4, period_num)
        BIT_sheet5.BIT_automation(filepath1, filepath2, filepath3, filepath4, period_num)
        BIT_sheet6.BIT_automation(filepath1, filepath2, filepath3, filepath4, period_num)
        BIT_sheet7.BIT_automation(filepath1, filepath2, filepath3, filepath4, period_num)
    else:
        print("请输入正确的sheet！")