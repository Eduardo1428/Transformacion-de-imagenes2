import sys
import os
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFileDialog, QGroupBox, QCheckBox, QSpinBox, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices

class ZonaImagenes(QLabel):
    def __init__(self, al_cambiar):
        super().__init__("Arrastra tus imágenes .BMP aquí\no haz clic para seleccionarlas\n(Máximo 10 archivos)")
        self.al_cambiar = al_cambiar
        self.setAlignment(Qt.AlignCenter)
        self.setFixedSize(305, 165)
        self.setAcceptDrops(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("QLabel { border: 2px dashed #38BDF8; border-radius: 14px; font-size: 13px; font-weight: 500; color: #BAE6FD; background-color: #1E293B; padding: 10px; } QLabel:hover { border-color: #34D399; background-color: #263549; color: #FFFFFF; }")

    def mousePressEvent(self, event):
        rutas, _ = QFileDialog.getOpenFileNames(self, "Seleccionar imágenes BMP", "", "Imágenes BMP (*.bmp)")
        if rutas:
            self.al_cambiar(rutas)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        rutas = [u.toLocalFile() for u in event.mimeData().urls()]
        self.al_cambiar(rutas)

class VentanaPrincipal(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interfaz LAE")
        self.resize(800, 520)
        self.imagenes = []

        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.carpeta_resultados = os.path.join(self.base_dir, "resultados")
        os.makedirs(self.carpeta_resultados, exist_ok=True)

        self.setStyleSheet(
            "QWidget { background-color: #0F172A; color: #F1F5F9; font-family: 'Helvetica Neue', 'Segoe UI', Arial, sans-serif; }"
            "QGroupBox { background-color: #1E293B; border: 1px solid #334155; border-radius: 14px; margin-top: 14px; padding: 15px 12px 12px 12px; font-size: 14px; font-weight: bold; color: #38BDF8; }"
            "QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; left: 16px; padding: 0 6px; background-color: #0F172A; border-radius: 4px; }"
            "QCheckBox { spacing: 8px; font-size: 13px; color: #E2E8F0; background-color: transparent; padding: 3px; }"
            "QCheckBox:hover { color: #38BDF8; }"
            "QCheckBox::indicator { width: 16px; height: 16px; border-radius: 4px; border: 2px solid #64748B; background-color: #0F172A; }"
            "QCheckBox::indicator:checked { background-color: #10B981; border-color: #10B981; }"
            "QSpinBox { background-color: #0F172A; color: #38BDF8; border: 1px solid #475569; border-radius: 6px; padding: 4px 8px; font-weight: bold; font-size: 13px; }"
        )

        layout = QVBoxLayout()
        layout.setContentsMargins(28, 22, 28, 16)

        titulo = QLabel("Transformador de Imágenes BMP")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 24px; font-weight: bold; color: #38BDF8; letter-spacing: 0.5px;")

        fila_central = QHBoxLayout()
        fila_central.setSpacing(22)

        col_izquierda = QVBoxLayout()
        col_izquierda.setSpacing(10)
        self.zona_drop = ZonaImagenes(self.agregar_imagenes)

        self.btn_limpiar = QPushButton("Limpiar imágenes")
        self.btn_limpiar.setCursor(Qt.PointingHandCursor)
        self.btn_limpiar.setStyleSheet("QPushButton { background-color: #334155; color: #FCA5A5; font-size: 12px; font-weight: bold; border: 1px solid #475569; border-radius: 8px; padding: 7px; } QPushButton:hover { background-color: #EF4444; color: white; border-color: #EF4444; }")
        self.btn_limpiar.clicked.connect(self.limpiar_imagenes)

        col_izquierda.addStretch()
        col_izquierda.addWidget(self.zona_drop)
        col_izquierda.addWidget(self.btn_limpiar)
        col_izquierda.addStretch()

        grupo_filtros = QGroupBox("Transformaciones")
        grid_filtros = QGridLayout()
        grid_filtros.setVerticalSpacing(8)

        instruccion = QLabel("Selecciona el tipo de transformación que deseas realizar:")
        instruccion.setStyleSheet("font-size: 12px; color: #94A3B8; background: transparent;")
        grid_filtros.addWidget(instruccion, 0, 0, 1, 2)

        self.chk_todas = QCheckBox("Seleccionar todas")
        self.chk_todas.setStyleSheet("font-weight: bold; color: #FBBF24; background: transparent;")
        self.chk_todas.stateChanged.connect(self.alternar_todas)
        grid_filtros.addWidget(self.chk_todas, 1, 0, 1, 2)

        nombres_filtros = [
            "Inversión horizontal a color",
            "Inversión horizontal blanco y negro",
            "Inversión vertical a color",
            "Inversión vertical blanco y negro",
            "Desenfoque a color",
            "Desenfoque blanco y negro",
            "Detección de bordes X",
            "Detección de bordes Y"
        ]
        self.checks = []
        for i, nombre in enumerate(nombres_filtros):
            chk = QCheckBox(nombre)
            self.checks.append(chk)
            grid_filtros.addWidget(chk, (i // 2) + 2, i % 2)

        fila_kernel = QHBoxLayout()
        lbl_kernel = QLabel("Tamaño de kernel (desenfoque):")
        lbl_kernel.setStyleSheet("font-size: 13px; color: #CBD5E1; background: transparent;")
        self.spin_kernel = QSpinBox()
        self.spin_kernel.setRange(3, 55)
        self.spin_kernel.setSingleStep(2)
        self.spin_kernel.setValue(3)
        self.spin_kernel.setFixedWidth(70)
        fila_kernel.addWidget(lbl_kernel)
        fila_kernel.addWidget(self.spin_kernel)
        fila_kernel.addStretch()
        grid_filtros.addLayout(fila_kernel, 6, 0, 1, 2)

        grupo_filtros.setLayout(grid_filtros)
        fila_central.addLayout(col_izquierda)
        fila_central.addWidget(grupo_filtros)

        fila_botones = QHBoxLayout()
        fila_botones.setSpacing(18)

        self.btn_procesar = QPushButton("Transformar")
        self.btn_procesar.setFixedSize(195, 42)
        self.btn_procesar.setCursor(Qt.PointingHandCursor)
        self.btn_procesar.setStyleSheet("QPushButton { background-color: #10B981; color: #064E3B; font-size: 15px; font-weight: bold; border-radius: 10px; } QPushButton:hover { background-color: #34D399; }")
        self.btn_procesar.clicked.connect(self.ejecutar)

        self.btn_resultados = QPushButton("Resultados")
        self.btn_resultados.setFixedSize(165, 42)
        self.btn_resultados.setCursor(Qt.PointingHandCursor)
        self.btn_resultados.setStyleSheet("QPushButton { background-color: #6366F1; color: white; font-size: 14px; font-weight: bold; border-radius: 10px; } QPushButton:hover { background-color: #818CF8; }")
        self.btn_resultados.clicked.connect(self.abrir_resultados)

        fila_botones.addStretch()
        fila_botones.addWidget(self.btn_procesar)
        fila_botones.addWidget(self.btn_resultados)
        fila_botones.addStretch()

        integrantes = QLabel("A01773799 | Luis De Los Santos Cadena   •   A01736561 | Andre Suárez Hernández   •   A01739517 | José Eduardo Muñoz Herrera")
        integrantes.setAlignment(Qt.AlignCenter)
        integrantes.setStyleSheet("font-size: 11px; color: #64748B;")

        layout.addWidget(titulo)
        layout.addSpacing(12)
        layout.addLayout(fila_central)
        layout.addSpacing(22)
        layout.addLayout(fila_botones)
        layout.addStretch()
        layout.addWidget(integrantes)

        self.setLayout(layout)

    def alternar_todas(self, estado):
        marcar = (estado == Qt.Checked)
        for chk in self.checks:
            chk.setChecked(marcar)

    def agregar_imagenes(self, nuevas_rutas):
        for ruta in nuevas_rutas:
            if len(self.imagenes) < 10 and ruta.lower().endswith(".bmp") and ruta not in self.imagenes:
                self.imagenes.append(ruta)
        if self.imagenes:
            nombres = ", ".join(os.path.basename(r) for r in self.imagenes)
            self.zona_drop.setText(f"{len(self.imagenes)}/10 imágenes cargadas\n({nombres})")

    def limpiar_imagenes(self):
        self.imagenes.clear()
        self.zona_drop.setText("Arrastra tus imágenes .BMP aquí\no haz clic para seleccionarlas\n(Máximo 10 archivos)")

    def abrir_resultados(self):
        os.makedirs(self.carpeta_resultados, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.carpeta_resultados))

    def ejecutar(self):
        if not self.imagenes:
            QMessageBox.warning(self, "Aviso", "Carga al menos una imagen .BMP primero.")
            return

        filtros_8bits = "".join("1" if chk.isChecked() else "0" for chk in self.checks)
        if filtros_8bits == "00000000":
            QMessageBox.warning(self, "Aviso", "Selecciona al menos una transformación.")
            return

        nombre_exe = "archivos_c.exe" if sys.platform == "win32" else "archivos_c"
        ruta_exe = os.path.join(self.base_dir, nombre_exe)

        if not os.path.exists(ruta_exe):
            QMessageBox.critical(self, "Ejecutable no encontrado", f"No se encontró '{nombre_exe}' en la carpeta:\n{self.base_dir}\n\nCompila tu código en C primero.")
            return

        kernel_size = str(self.spin_kernel.value())
        comando = [ruta_exe, kernel_size, filtros_8bits] + self.imagenes

        self.btn_procesar.setEnabled(False)
        self.btn_procesar.setText("Procesando...")
        QApplication.processEvents()

        try:
            resultado = subprocess.run(comando, cwd=self.base_dir, capture_output=True, text=True)

            if resultado.returncode == 0:
                tiempo = "Desconocido"
                for linea in resultado.stdout.splitlines():
                    if "Tiempo total de ejecucion:" in linea:
                        tiempo = linea.split(":", 1)[1].strip()
                        break

                QMessageBox.information(self, "Listo", f"<h2 style='color:#10B981;'>Proceso completado</h2><p style='font-size:14px;'>Tiempo de ejecución: <b>{tiempo}</b></p><p style='color:#94A3B8;'>Ver resultados con el botón <b>\"Resultados\"</b></p>")
            else:
                QMessageBox.critical(self, "Error en ejecución", f"El programa en C terminó con error:\n{resultado.stderr or resultado.stdout}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo ejecutar el programa:\n{str(e)}")
        finally:
            self.btn_procesar.setEnabled(True)
            self.btn_procesar.setText("Transformar")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec_())