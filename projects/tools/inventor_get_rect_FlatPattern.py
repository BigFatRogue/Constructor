import win32com.client as wc32
from pythoncom import VT_ARRAY, VT_R8, VT_DISPATCH
from math import pi as PI, floor, ceil


class AutoCad:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls, *args, **kwargs)
        return cls.__instance

    def __init__(self):
        self.app = wc32.GetActiveObject('Autocad.Application')
        self.doc = self.app.ActiveDocument
        self.mp = self.doc.ModelSpace
    
    @staticmethod
    def point(coords: tuple):
        return wc32.VARIANT(VT_ARRAY | VT_R8, coords)

    def add_line(self, pos0, pos1):
        self.mp.AddLine(self.point(pos0), self.point(pos1))

    def add_arc(self, center, radius, start_angle, end_angle):
        self.mp.AddArc(self.point(center), radius, start_angle, end_angle)

    def add_rect(self, botom_left_point: tuple, top_right_point: tuple) -> None:
        x0, y0 = botom_left_point
        x1, y1 = top_right_point

        p1 = (x0, y0, 0)
        p2 = (x0, y1, 0)
        p3 = (x1, y1, 0)
        p4 = (x1, y0, 0)
        pline = self.mp.AddPolyline(self.point([*p1, *p2, *p3, *p4]))
        pline.Closed = True
    
    def add_text(self, text: str, point: tuple, height: float) -> None:
        self.mp.AddText(text, self.point(point), height)


def recursive_tree_assembly() -> None:
    app = wc32.GetActiveObject('Inventor.Application')
    doc = app.ActiveDocument
    __recursive_tree_assembly(document=doc)


def __recursive_tree_assembly(document, cindex=0, offsetY=0, is_recursion=False):

    if not is_recursion:
        # Начало рекурсии. Когда мы работаем с базовым файлом
        list_component = document.ComponentDefinition.Occurrences
    else:
        # Рекурсия, когда уже начали перебор подсборок
        list_component = document.SubOccurrences

    for component in list_component:
        try:
            count = int(component.SubOccurrences.Count)
            
            if count != 0:
                # Если компонентов в подсборке более 0, то тогда мы заходим в неё и перебираем в рекурсии
                offsetY = __recursive_tree_assembly(document=component, cindex=cindex, offsetY=offsetY, is_recursion=True)
            else:
                sub_doc = component.Definition.Document
                # 150995200 - Листовой
                if sub_doc.ComponentDefinition.Type == 150995200:
                    w, h = draw_flatten_body(document=sub_doc, offsetY=offsetY)
                    offsetY += h + 50
        except Exception:
            pass
    return offsetY



def draw_flatten_body(document, offsetY):
    ac = AutoCad()

    flat_pattern = document.ComponentDefinition.FlatPattern
    box = flat_pattern.RangeBox
    w, h = ceil(box.maxPoint.X - box.minPoint.X), ceil(box.maxPoint.Y - box.minPoint.Y)

    w, h = w * 10, h * 10
    ac.add_rect((0,  offsetY), (w, h + offsetY))
    ac.add_text(f'{w}x{h} {document.DisplayName}', (0, h + offsetY - 15, 0), 15)

    # flat_body = flat_pattern.SurfaceBodies
    # dict_geometry_type = {
    #     5128: 'spline',
    #     5124: 'curcle',
    #     5125: 'arc',
    #     5126: 'ellipse',
    #     5127: 'ellipseArc',
    #     5122: 'line',
    #     5123: 'line_segment',
    #     5129: 'polyline',
    #     5121: 'unknown'}
    
    # for body in flat_body:
    #     for edge in body.Edges:
    #         tp = dict_geometry_type.get(edge.GeometryType)

    #         if tp == 'line_segment':
    #             x_start, y_start = edge.StartVertex.Point.X, edge.StartVertex.Point.Y
    #             x_end, y_end = edge.StopVertex.Point.X, edge.StopVertex.Point.Y
    #             ac.add_line((x_start, y_start + offsetY, 0), (x_end, y_end + offsetY, 0))
    #         elif tp == 'arc':
    #             arc_geom = edge.Geometry
    #             center = arc_geom.Center.X, arc_geom.Center.Y + offsetY, 0
    #             radius = arc_geom.Radius
    #             start_angle = arc_geom.StartAngle
    #             len_arc = arc_geom.SweepAngle
    #             ac.add_arc(center, radius, start_angle, len_arc - start_angle)
    #         elif tp == 'spline':
    #             x_start, y_start = edge.StartVertex.Point.X, edge.StartVertex.Point.Y
    #             items = edge.TangentiallyConnectedEdges
    #             for item in items:
    #                 x_start_item, y_start_item = item.StartVertex.Point.X, item.StartVertex.Point.Y
    #                 # print(x_start_item, y_start_item)

  
    return w, h


if __name__ == '__main__':
    recursive_tree_assembly()
    print('done')
