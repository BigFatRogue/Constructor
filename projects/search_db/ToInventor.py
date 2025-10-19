import win32com.client as wc


def paste_detail_in_inventor(path_detail: str):
    inventor = wc.GetActiveObject('Inventor.Application')

    kFileNameEvent = 6657
    kPlaceComponentCommand = 2057

    inventor.CommandManager.PostPrivateEvent(kFileNameEvent, path_detail)
    # inventor.CommandManager.StartCommand(kPlaceComponentCommand)

    oCtrlDef = inventor.CommandManager.ControlDefinitions.Item("AssemblyPlaceComponentCmd")
    oCtrlDef.Execute()


if __name__ == '__main__':
    directory = r'\\192.168.1.11\PKODocs\Inventor Project\Библиотека оборудования ALS'
    detail = fr"{directory}\Конденсатоотводчики\Вентар\FT43-4.5 DN40 (2NGT)\ft43-10.ipt"
    detail = r'\\192.168.1.11\PKODocs\Inventor Project\Библиотека оборудования ALS\КИПиА\Манометры и термометры\Manotherm\TBiSChg100 dF8 L60 G1-2 осевой по центру.ipt'
    paste_detail_in_inventor(detail)
