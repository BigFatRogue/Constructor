# 
# Основной список получаемый после прочтения сборки 
# dict_data_assembly = 
#   {
#       'root_assembly': '',
#       'name_assembly': '',
#       'new_root_assembly': '',
#       'new_name_assembly': '',
#       'item': {
#           'full_filename': {
#               'component_name': , 
#               'display_name': , 
#               'short_filename': , 
#               'image': '', 
#               'item': sub_item
#            }
#        }
#   }
#

import os
import shutil
from typing import Any
from pathlib import Path
from datetime import datetime

from sitting import *
from my_logging import loging_try


def mkdir_tree(path: str):
    path: Path = Path(path)
    tpl = path.parts

    lost_part = tpl[-1].split('.')
    if len(lost_part) > 1:
        tpl = tpl[:-1]

    for i in range(len(tpl)):
        p = Path(os.path.join(*tpl[:i + 1]))
        if not p.exists():
            try:
                p.mkdir()
            except Exception:
                loging_try()

def move_file_inventor_project() -> None:
    """
    Копирование из ресурсов проекта Inventor для копирования сборок
    """
    mkdir_tree(path=PATH_TMP)
    project_inventor_full_filename = os.path.join(PATH_TMP, PROJECT_INVENTOR_FILENAME)
    if not os.path.exists(project_inventor_full_filename):
        shutil.copy(os.path.join(PROJECT_ROOT, 'resources', PROJECT_INVENTOR_FILENAME), project_inventor_full_filename)

def copy_file_assembly(full_filename: str) -> str:
    """
    :param - full_filename - полный путь к сборке
    :return - путь к копированной сборки во временную папку  
    """
    full_filename = full_filename
    path_full_filename = Path(full_filename) 
    path_parent = path_full_filename.parent
    dir_name = path_parent.name
    now_time = f'{datetime.today():%d-%m-%Y$%H-%M-%S}'
    to_ = os.path.join(PATH_TMP, f'{dir_name} (copy at {now_time})')

    if not os.path.exists(to_):
        shutil.copytree(path_parent, to_)

    return os.path.join(to_, path_full_filename.name)

def get_tree_assembly(application, options_open_document, full_filename_assembly: str) -> tuple:
    document = application.Documents.OpenWithOptions(full_filename_assembly, options_open_document, False)

    path_assemlby_full_filename = Path(full_filename_assembly)
    root_assembly = str(path_assemlby_full_filename.parent)
    main_dct = {
        'root_assembly': root_assembly,
        'name_assembly': path_assemlby_full_filename.name,
        'new_root_assembly': '',
        'new_name_assembly': '',
        'item': {}
    }

    main_dct['item'] = _get_tree_assembly_recursive(document=document, root_assembly=root_assembly)
    
    return main_dct, document

def _get_tree_assembly_recursive(document, root_assembly: str, dct=None, is_recursion=False) -> dict:
    if dct is None:
        dct = {}
    
    try:
        if not is_recursion:
            # Начало рекурсии. Когда мы работаем с базовым файлом
            list_component = document.ComponentDefinition.Occurrences
        else:
            # Рекурсия, когда уже начали перебор подсборок
            list_component = document.SubOccurrences
    except Exception as error:
        loging_try()
        list_component = tuple()
    
    for component in list_component:
        try:
            referenced_document_descriptor = component.ReferencedDocumentDescriptor
            full_filename: str = referenced_document_descriptor.FullDocumentName.replace(root_assembly, '')
            short_filename = full_filename.replace(root_assembly, '')
            display_name: str = referenced_document_descriptor.DisplayName
            component_name: str = component.Name

            if all([i.lower() not in full_filename.lower() for i in FILTERS]):
                if ':' in component_name:
                    component_name = ':'.join(component_name.split(':')[:-1])

                if '.iam' in full_filename:
                    sub_dct = _get_tree_assembly_recursive(document=component, root_assembly=root_assembly, is_recursion=True)
                    value = {'component_name': component_name, 'display_name': display_name, 'short_filename': short_filename, 'image': 'iam_image.png', 'item': sub_dct}
                else:
                    value = {'component_name': component_name, 'display_name': display_name, 'short_filename': short_filename, 'image': 'ipt_image.png', 'item': {}}
                
                if full_filename not in dct:
                    dct[full_filename] = value
        except Exception as error:
            loging_try()
    return dct

def create_folder_rename_assembly(assembly_name: str) -> str:
    now_time = f'{datetime.today():%d-%m-%Y$%H-%M-%S}'
    name = f'({now_time}) {assembly_name.replace(".iam", "")}'
    path = os.path.join(PATH_TMP, name)
    os.mkdir(path)
    
    return  path

def copy_and_rename_file_assembly(dct: dict) -> None:
    """
    Копирование файлов входящих в сборку Inventor и их переименование 
    """
    for old_short_filename, new_short_filename in dct['short_filename'].items():
        old_full_filename = dct['root_assembly'] + old_short_filename
        new_full_filename = dct['new_root_assembly'] + new_short_filename
    
        mkdir_tree(new_full_filename)
        if not os.path.exists(new_full_filename) and os.path.exists(old_full_filename):
            shutil.copy(old_full_filename, new_full_filename)
            
    old_full_filename_assembly = os.path.join(dct['root_assembly'], dct['name_assembly'])
    new_full_filename_assembly = os.path.join(dct['new_root_assembly'], dct['new_name_assembly'])
    if not os.path.exists(new_full_filename_assembly) and os.path.exists(old_full_filename_assembly):
        shutil.copy(old_full_filename_assembly, new_full_filename_assembly)
    
def replace_reference_file(application: Any, document: Any, options_open_document: Any, dict_data_assembly: dict) -> None: 
    """
    Замена сылок на входящие детали и подсборки на файлы в сборке
    """
    for ref_file in document.File.ReferencedFileDescriptors:
        full_filename: str = ref_file.FullFileName
        
        for old_shortpath, new_shortpath in dict_data_assembly['short_filename'].items():
            new_full_filename = dict_data_assembly['new_root_assembly'] + new_shortpath
            if old_shortpath in full_filename:
                if os.path.exists(new_full_filename):
                    if '.ipt' in full_filename:
                        ref_file.ReplaceReference(new_full_filename)
                
                    elif '.iam' in full_filename:
                        wrapper_doc = application.Documents.OpenWithOptions(new_full_filename, options_open_document, False)
                        replace_reference_file(application=application, document=wrapper_doc, options_open_document=options_open_document, dict_data_assembly=dict_data_assembly)
                        ref_file.ReplaceReference(new_full_filename)
                        wrapper_doc.Close(True)

def rename_display_name_file(application: Any, options_open_document: Any, dict_data_assembly: dict):
    """ Открытие каждого файла входящего в сборку и переименования его имени в браузере (DisplayName) """
    for old_short_filename, new_short_filename in dict_data_assembly['short_filename'].items():
        new_full_filename = dict_data_assembly['new_root_assembly'] + new_short_filename
        if os.path.exists(new_full_filename):
            sub_doc = application.Documents.OpenWithOptions(new_full_filename, options_open_document, False)
            new_display_name = dict_data_assembly['display_name'].get(sub_doc.DisplayName)
            try:
                if new_display_name:
                    sub_doc.DisplayName = new_display_name.replace('.ipt', '').replace('.iam', '')
                    sub_doc.Save()
            except Exception as error:
                loging_try()
            sub_doc.Close()

def rename_component_name_in_assembly(document: Any, dict_data_assembly: dict, is_recursion=False) -> None:
    """ Переименовывание имён в браузере Inventor в основной сборки"""
    try:
        if not is_recursion:
            # Начало рекурсии. Когда мы работаем с базовым файлом
            document.DisplayName = dict_data_assembly['new_name_assembly']
            list_component = document.ComponentDefinition.Occurrences
        else:
            # Рекурсия, когда уже начали перебор подсборок
            list_component = document.SubOccurrences
    except Exception as error:
        loging_try()
        list_component = tuple()

    for component in list_component:
        try:
            component_fullname: str = component.Name
            referenced_document_descriptor = component.ReferencedDocumentDescriptor
            full_filename = referenced_document_descriptor.FullDocumentName
            
            if all([i.lower() not in full_filename.lower() for i in FILTERS]):
                key = ''.join(component_fullname.split(':')[:-1]) if ':' in component_fullname else component_fullname
                new_component_name = dict_data_assembly['component_name'].get(key)
                
                if new_component_name:
                    value = new_component_name if ':' not in component_fullname else f'{new_component_name}:{component_fullname.split(":")[-1]}'
                    component.Name = value
            
            if '.iam' in full_filename:
                # Если компонентов в подсборке более 0, то тогда мы заходим в неё и перебираем в рекурсии
                rename_component_name_in_assembly(document=component, dict_data_assembly=dict_data_assembly, is_recursion=True)
        except Exception as error:
            loging_try()        
            pass

def get_rules_assembly(application: Any, document: Any) -> dict:
    """ Получение правил из сборки """
    rules_dict = {}
    try:
        iLogic = application.ApplicationAddIns.ItemById("{3bdd8d79-2179-4b11-8a5a-257b1c0263ac}").Automation
        rules = iLogic.Rules(document)

        if rules is not None:
            for rule in rules:
                rules_dict[rule.Name] = rule.Text
    except Exception as error:
        loging_try()
    return rules_dict

def set_rulse(aplication: Any, document: Any, dict_rules: dict) -> None:
    """ Замена текста в правилах """
    if dict_rules:
        iLogic = aplication.ApplicationAddIns.ItemById("{3bdd8d79-2179-4b11-8a5a-257b1c0263ac}").Automation
        for rule in iLogic.Rules(document):
            rule.Text = dict_rules[rule.Name]

    
if __name__ == '__main__':
    assembly_path = r'C:\Users\p.golubev\Desktop\Пробники Inventor\Дренажный лоток\v1.5\ALS.PROJECT.ZONE.XX.00.00.000.iam'
    # tmp_assembly_path = copy_file_assembly(assembly_path)
    
    # app = wc32.GetActiveObject('Inventor.Application')
    # app.SilentOperation = True
    # oNVM = app.TransientObjects.CreateNameValueMap()
    # oNVM.Add("SkipAllUnresolvedFiles", True)


