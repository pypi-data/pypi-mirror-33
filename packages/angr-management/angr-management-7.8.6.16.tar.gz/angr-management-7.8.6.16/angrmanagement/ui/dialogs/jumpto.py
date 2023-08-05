
from PySide.QtGui import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit
from PySide.QtCore import Qt

from ..widgets import QAddressInput


class JumpTo(QDialog):
    def __init__(self, disasm_view, parent=None):
        super(JumpTo, self).__init__(parent)

        # initialization
        self._disasm_view = disasm_view

        self._address_box = None
        self._status_label = None
        self._ok_button = None

        self.setWindowTitle('Jump to address')

        self.main_layout = QVBoxLayout()

        self._init_widgets()

        self.setLayout(self.main_layout)

        self.show()

    #
    # Private methods
    #

    def _init_widgets(self):

        # address label

        address_label = QLabel(self)
        address_label.setText('Address')

        address = QAddressInput(self._on_address_changed, parent=self)
        self._address_box = address

        address_layout = QHBoxLayout()
        address_layout.addWidget(address_label)
        address_layout.addWidget(address)
        self.main_layout.addLayout(address_layout)

        # status label
        status_label = QLabel(self)
        self.main_layout.addWidget(status_label)
        self._status_label = status_label

        # buttons

        ok_button = QPushButton(self)
        ok_button.setText('OK')
        ok_button.setEnabled(False)
        ok_button.clicked.connect(self._on_ok_clicked)
        self._ok_button = ok_button

        cancel_button = QPushButton(self)
        cancel_button.setText('Cancel')
        cancel_button.clicked.connect(self._on_cancel_clicked)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(ok_button)
        buttons_layout.addWidget(cancel_button)

        self.main_layout.addLayout(buttons_layout)

    #
    # Event handlers
    #

    def _on_address_changed(self, new_text):
        if self._address_box.target is None:
            # the address is invalid

            self._status_label.setText('Invalid')
            self._status_label.setProperty('class', 'status_invalid')
            self._ok_button.setEnabled(False)
        else:
            self._status_label.setText('Valid')
            self._status_label.setProperty('class', 'status_valid')
            self._ok_button.setEnabled(True)

        self._status_label.style().unpolish(self._status_label)
        self._status_label.style().polish(self._status_label)

    def _on_ok_clicked(self):
        addr = self._address_box.target
        if addr is not None:
            r = self._disasm_view.jump_to(addr)
            if r:
                self.close()

    def _on_cancel_clicked(self):
        self.cfg_args = None
        self.close()
