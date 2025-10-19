import win32com.client as wc32
import os
import pathlib
import shutil
import json

ROOT = pathlib.Path(__file__).parent

def get_filepath() -> tuple:
    with open(os.path.join(ROOT, 'resources', 'variable.json'), 'r', encoding='utf-8') as var:
        dct: dict = json.load(var)
        return dct['name_tmp_assembly'], dct['path_tmp_copy_to'], dct['path_from_copy'], dct['search']


def copy_tmp_assembly_file(path_from_copy: str, path_tmp_copy_to: str, search: str, replace_: str) -> tuple:
    new_name_assembly = ""
    dct_filepath = {}

    lst_path_tmp_copy_to = path_tmp_copy_to.split('\\')
    for i in range(1, len(lst_path_tmp_copy_to) + 1):
        path = "\\".join(lst_path_tmp_copy_to[: i])
        if not os.path.exists(path):
            os.mkdir(path)

    for filename in os.listdir(path_from_copy):
        if '.iam' in filename or '.ipt' in filename:
            filepath = os.path.join(path_tmp_copy_to, filename)
            dct_filepath[filepath] = ""
            if not os.path.exists(filepath):
                shutil.copy(os.path.join(path_from_copy, filename), os.path.join(path_tmp_copy_to, filename))

        if '.iam' in filename:
            new_name_assembly = filename.replace(search, replace_)

    return new_name_assembly, dct_filepath


def set_dct_filepath(dct_filepath: dict, copy_to: str, search: str, replace_: str) -> dict:
    for filepath in dct_filepath.keys():
        new_filepath = '\\'.join(filepath.split('\\')[-2:len(filepath)]).replace(search, replace_)
        dct_filepath[filepath] = os.path.join(copy_to, new_filepath)

    return dct_filepath


def copy_assembly_inventor(path_tmp_assembly: str, new_name_assembly: str, copy_to: str, dct_filepath: dict, search: str, replace_: str) -> str:
    new_path_assembly = os.path.join(copy_to, new_name_assembly.replace('.iam', ''), new_name_assembly)

    app = wc32.GetActiveObject('Inventor.Application')
    doc = app.Documents.Open(path_tmp_assembly)
    try:
        set_unique = set()
        for component in doc.ComponentDefinition.Occurrences:
            filepath = str(component.Definition.Document.FullFileName)
            component.Name = str(component.Name).replace(search, replace_)

            if filepath not in set_unique:
                new_filepath = dct_filepath.get(filepath)
                component.Definition.Document.SaveAs(new_filepath, True)
                component.Replace(new_filepath, True)
                if component.Adaptive:
                    component.Adaptive = True

                set_unique.add(filepath)
                set_unique.add(new_filepath)
    except Exception as error:
        print(error, '\n')

    doc.DisplayName = new_name_assembly
    doc.SaveAs(new_path_assembly, True)
    doc.Close(True)

    if os.path.exists(path_tmp_assembly):
        shutil.rmtree('\\'.join(path_tmp_assembly.split('\\')[:-1]))

    return new_path_assembly


def copy_assembly_inventor_end(new_path_assembly: str, search: str, replace_: str, copy_to, new_name_assembly: str, need_open=True) -> None:
    app = wc32.GetActiveObject('Inventor.Application')
    doc = app.Documents.Open(new_path_assembly)

    doc.ComponentDefinition.RepresentationsManager.LevelOfDetailRepresentations("Рабочий").Activate(True)

    for component in doc.ComponentDefinition.Occurrences:
        if 'основа' in str(component.Name).lower():
            component.Adaptive = True
            break

    iLogic = app.ApplicationAddIns.ItemById("{3bdd8d79-2179-4b11-8a5a-257b1c0263ac}").Automation

    for rule in iLogic.Rules(doc):
        rule.Text = str(rule.Text).replace(search, replace_)

    doc.Save()

    if need_open:
        os.startfile(os.path.join(copy_to, new_name_assembly.replace('.iam', '')))



if __name__ == "__main__":
    app = wc32.GetActiveObject('Inventor.Application')
    doc = app.ActiveDocuments
    iLogicAddIn = app.ApplicationAddIns.ItemById("{3bdd8d79-2179-4b11-8a5a-257b1c0263ac}")
    iLogic = iLogicAddIn.Automation