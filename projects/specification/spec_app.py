from __future__ import annotations
import sys
from PyQt5 import QtWidgets

if __name__ == '__main__':
    # Для запуска через IDE
    from pathlib import Path
    test_path = str(Path(__file__).parent.parent.parent)
    sys.path.append(test_path)

from projects.specification.ui.main_window import WindowSpecification

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = WindowSpecification()
    
    window.show()
    sys.exit(app.exec_())
    