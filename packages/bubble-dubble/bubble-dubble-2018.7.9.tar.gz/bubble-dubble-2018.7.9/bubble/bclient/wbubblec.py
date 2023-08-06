#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from PyQt5 import QtGui, QtCore, QtWidgets
import qtsnbl.widgets
import qtsnbl.version
from ..bcommon import default
from . import connector, wplot, wsaxsparams, wmask, wdark, wabout, wsopts
from .tools import clearButtonSlot
from .ui.wbubble import Ui_WBubble
try:
    from .. import frozen
except ImportError:
    frozen = None


class WBubble(QtWidgets.QDialog, Ui_WBubble, qtsnbl.widgets.FixedWidget):
    killServerSignal = QtCore.pyqtSignal()
    startServerSignal = QtCore.pyqtSignal(str, int)
    runSignal = QtCore.pyqtSignal(dict, str)
    beamlineToggledSignal = QtCore.pyqtSignal(str)
    applyWaxsDarkSignal = QtCore.pyqtSignal()
    applySaxsDarkSignal = QtCore.pyqtSignal()
    MaxLabelLen = 40

    def __init__(self):
        super().__init__()
        self.saveFolder = ''
        self.setUI()
        self.setValidators()
        self.setVisibleWidgets()
        self.createWindows()
        self.createConnector()
        self.connectSignals()
        self.fixWindow()

    def setUI(self):
        self.setupUi(self)
        self.bgBeamline = QtWidgets.QButtonGroup()
        self.bgBeamline.addButton(self.snblRadio, 0)
        self.bgBeamline.addButton(self.dubbleRadio, 1)
        self.bgUnits = QtWidgets.QButtonGroup()
        self.bgUnits.addButton(self.tthRadio, 0)
        self.bgUnits.addButton(self.qRadio, 1)
        self.bgUnits.addButton(self.aRadio, 2)
        self.tthRadio.tag = 't'
        self.qRadio.tag = 'q'
        self.aRadio.tag = 'a'
        self.snblRadio.tag = 'SNBL'
        self.dubbleRadio.tag = 'Dubble'

    def createConnector(self):
        self.connector = connector.Connector()

    def setValidators(self):
        self.multiplyLineEdit.setValidator(QtGui.QDoubleValidator())

    def createWindows(self):
        self.wSaxsMask = wmask.WMask('saxs', self)
        self.wWaxsMask = wmask.WMask('waxs', self)
        self.waxsPlot = wplot.WPlot('WAXS', self)
        self.saxsPlot = wplot.WPlot('SAXS', self)
        self.saxsPlot.plot1DView.setLogMode(x=True, y=True)
        self.wSaxsParams = wsaxsparams.WSaxsParams(self)
        self.wSaxsDark = wdark.WDark(self)
        self.wWaxsDark = wdark.WDark(self)
        self.wsopts = wsopts.WSOpts(self)
        version = qtsnbl.version.Version(frozen)
        self.wupdates = qtsnbl.widgets.WUpdates(self, version)
        self.wabout = wabout.WAboutBubble(self, version.hash, version.string)

    def start(self):
        self.loadSettings()
        self.wSaxsMask.loadSettings()
        self.wWaxsMask.loadSettings()
        self.waxsPlot.loadSettings()
        self.saxsPlot.loadSettings()
        self.wSaxsParams.loadSettings()
        self.wSaxsDark.loadSettings()
        self.wWaxsDark.loadSettings()
        self.wsopts.loadSettings()
        self.wupdates.loadSettings()
        self.startServerSignal.emit(self.hostLineEdit.text(), self.portSpinBox.value())
        self.show()
        self.wSaxsParams.showEvent(None)
        self.on_runSaxsButton_clicked(0)
        self.on_runWaxsButton_clicked(0)
        self.wupdates.checkNewVersion()

    def setVisibleWidgets(self):
        self.stopServerButton.hide()
        self.runServerButton.show()
        self.killServerButton.hide()
        self.stopWaxsButton.hide()
        self.stopSaxsButton.hide()
        self.sspeedCheckBox.setEnabled(False)
        self.multiEdit.setDisabled(True)

    # noinspection PyUnresolvedReferences
    def connectSignals(self):
        self.connector.serverStateSignal.connect(self.showServerState)
        self.connector.errorsSignal.connect(self.showServerErrors)
        self.connector.warningsSignal.connect(self.showServerWarnings)
        self.killServerSignal.connect(self.connector.killServer)
        self.connector.waxsStateSignal.connect(self.showWaxsState)
        self.connector.saxsStateSignal.connect(self.showSaxsState)
        self.connector.waxsPlotSignal.connect(self.waxsPlot.plot)
        self.connector.saxsPlotSignal.connect(self.saxsPlot.plot)
        self.runSignal.connect(self.connector.runSaxsWaxs)
        self.startServerSignal.connect(self.connector.tryServer)
        self.beamlineToggledSignal.connect(self.wWaxsMask.changeBeamline)
        self.beamlineToggledSignal.connect(self.wSaxsMask.changeBeamline)
        self.beamlineToggledSignal.connect(self.connector.setBeamline)
        self.applySaxsDarkSignal.connect(self.wSaxsDark.on_buttonBox_accepted)
        self.applyWaxsDarkSignal.connect(self.wWaxsDark.on_buttonBox_accepted)
        self.saxsPlot.sigClosed.connect(lambda: self.saxsPlotButton.setChecked(False))
        self.waxsPlot.sigClosed.connect(lambda: self.waxsPlotButton.setChecked(False))
        self.wSaxsMask.sigMask.connect(self.saxsMaskLineEdit.setText)
        self.wWaxsMask.sigMask.connect(self.waxsMaskLineEdit.setText)
        self.wabout.buttonUpdate.clicked.connect(self.wupdates.checkNewVersionByUser)

    def closeEvent(self, event):
        self.connector.disconnectFromServer()
        self.waxsPlot.close()
        self.saxsPlot.close()
        self.wSaxsMask.close()
        self.wWaxsMask.close()
        self.saveSettings()
        self.wsopts.saveSettings()
        self.wSaxsDark.saveSettings()
        self.wWaxsDark.saveSettings()
        self.waxsPlot.saveSettings()
        self.saxsPlot.saveSettings()
        self.wSaxsParams.saveSettings()
        self.wupdates.saveSettings()

    def saveSettings(self, s=None):
        _ = s.setValue if s else QtCore.QSettings().setValue
        _('WBubble/Geometry', self.saveGeometry())
        _('WBubble/host', self.hostLineEdit.text())
        _('WBubble/port', self.portSpinBox.value())
        _('WBubble/speed', self.speedCheckBox.isChecked())
        _('WBubble/sspeed', self.sspeedCheckBox.isChecked())
        _('WBubble/waxspath', self.waxsDirLineEdit.text())
        _('WBubble/waxsPoniPath', self.waxsPoniLineEdit.text())
        _('WBubble/waxsBkgPath', self.waxsBkgLineEdit.text())
        _('WBubble/waxsBkgCoef', self.waxsBkgCoefSpinBox.value())
        _('WBubble/saxspath', self.saxsDirLineEdit.text())
        _('WBubble/saxsPoniPath', self.saxsPoniLineEdit.text())
        _('WBubble/saxsMaskPath', self.saxsMaskLineEdit.text())
        _('WBubble/waxsMaskPath', self.waxsMaskLineEdit.text())
        _('WBubble/saxsBkgPath', self.saxsBkgLineEdit.text())
        _('WBubble/saxsBkgCoef', self.saxsBkgCoefSpinBox.value())
        _('WBubble/saxsAziStart', self.saxsAziStartSpinBox.value())
        _('WBubble/saxsAziStop', self.saxsAziStopSpinBox.value())
        _('WBubble/multiply', self.multiplyLineEdit.text())
        _('WBubble/beamline1', self.bgBeamline.checkedId())
        _('WBubble/outUnits1', self.bgUnits.checkedId())
        _('WBubble/waxsNormalization', self.comboNorm.currentText())
        _('WBubble/extCheckbox', self.extCheckBox.isChecked())
        _('WBubble/saxsDetector', self.saxsDetectorComboBox.currentText())
        _('WBubble/waxsDetector', self.waxsDetectorComboBox.currentText())
        _('WBubble/subdirCheckbox', self.subdirCheckBox.isChecked())
        _('WBubble/ext', self.extEdit.text())
        _('WBubble/subdir', self.subdirEdit.text())
        _('WBubble/saveFolder', self.saveFolder)
        _('WBubble/multicolumn', self.multiCheckBox.isChecked())
        _('WBubble/multicolumnName', self.multiEdit.text())
        _('WBubble/saveEdf', self.edfCheckBox.isChecked())
        _('WBubble/waxsAzimuth', self.waxsAzimuthCheckBox.isChecked())
        _('WBubble/waxsAzimuthStart', self.waxsAziStartSpinBox.value())
        _('WBubble/waxsAzimuthStop', self.waxsAziStopSpinBox.value())
        _('WBubble/waxsAzimuthSlices', self.waxsSlicesCheckBox.isChecked())
        _('WBubble/saxsAzimuth', self.saxsAzimuthCheckBox.isChecked())
        _('WBubble/saxsAzimuthSlices', self.saxsSlicesCheckBox.isChecked())
        _('WBubble/waxsRadial', self.waxsRadialCheckBox.isChecked())
        _('WBubble/waxsRadialStart', self.waxsRadStartSpinBox.value())
        _('WBubble/waxsRadialStop', self.waxsRadStopSpinBox.value())
        _('WBubble/saxsRadialStart', self.saxsRadStartSpinBox.value())
        _('WBubble/saxsRadialStop', self.saxsRadStopSpinBox.value())
        _('WBubble/saxsRadial', self.saxsRadialCheckBox.isChecked())
        _('WBubble/page', self.tabWidget.currentIndex())

    def loadSettings(self, s=None):
        _ = s.value if s else QtCore.QSettings().value
        self.restoreGeometry(_('WBubble/Geometry', b''))
        self.hostLineEdit.setText(_('WBubble/host', default.DEFAULT_HOST, str))
        self.portSpinBox.setValue(_('WBubble/port', default.DEFAULT_PORT, int))
        self.speedCheckBox.setChecked(_('WBubble/speed', False, bool))
        self.sspeedCheckBox.setChecked(_('WBubble/sspeed', False, bool))
        self.waxsDirLineEdit.setText(_('WBubble/waxspath', '', str))
        self.waxsPoniLineEdit.setText(_('WBubble/waxsPoniPath', '', str))
        self.waxsBkgLineEdit.setText(_('WBubble/waxsBkgPath', '', str))
        self.waxsBkgCoefSpinBox.setValue(_('WBubble/waxsBkgCoef', 0, float))
        self.saxsDirLineEdit.setText(_('WBubble/saxspath', '', str))
        self.saxsPoniLineEdit.setText(_('WBubble/saxsPoniPath', '', str))
        self.saxsMaskLineEdit.setText(_('WBubble/saxsMaskPath', '', str))
        self.waxsMaskLineEdit.setText(_('WBubble/waxsMaskPath', '', str))
        self.saxsBkgLineEdit.setText(_('WBubble/saxsBkgPath', '', str))
        self.saxsBkgCoefSpinBox.setValue(_('WBubble/saxsBkgCoef', 0, float))
        self.saxsAziStartSpinBox.setValue(_('WBubble/saxsAziStart', 0, float))
        self.saxsAziStopSpinBox.setValue(_('WBubble/saxsAziStop', 0, float))
        self.multiplyLineEdit.setText(_('WBubble/multiply', '1', str))
        self.bgBeamline.button(_('WBubble/beamline1', 0, int)).setChecked(True)
        norm = _('WBubble/waxsNormalization', 'Monitor', str)
        self.comboNorm.setCurrentIndex(self.comboNorm.findText(norm))
        self.saxsDetectorComboBox.setCurrentIndex(self.saxsDetectorComboBox.findText(
            _('WBubble/saxsDetector', 'Pilatus', str)))
        self.waxsDetectorComboBox.setCurrentIndex(
            self.waxsDetectorComboBox.findText(_('WBubble/waxsDetector', 'Pilatus', str)))
        self.bgUnits.button(_('WBubble/outUnits1', 0, int)).setChecked(True)
        self.extCheckBox.setChecked(_('WBubble/extCheckbox', False, bool))
        self.subdirCheckBox.setChecked(_('WBubble/subdirCheckbox', False, bool))
        self.extEdit.setText(_('WBubble/ext', '', str))
        self.subdirEdit.setText(_('WBubble/subdir', '', str))
        self.saveFolder = _('WBubble/saveFolder', '', str)
        self.multiCheckBox.setChecked(_('WBubble/multicolumn', False, bool))
        self.multiEdit.setText(_('WBubble/multicolumnName', default.MULTICOLUMN_NAME, str))
        self.edfCheckBox.setChecked(_('WBubble/saveEdf', False, bool))
        self.waxsAziStartSpinBox.setValue(_('WBubble/waxsAzimuthStart', 0, float))
        self.waxsAziStopSpinBox.setValue(_('WBubble/waxsAzimuthStop', 0, float))
        self.waxsSlicesCheckBox.setChecked(_('WBubble/waxsAzimuthSlices', False, bool))
        self.saxsSlicesCheckBox.setChecked(_('WBubble/saxsAzimuthSlices', False, bool))
        self.saxsAzimuthCheckBox.setChecked(_('WBubble/saxsAzimuth', False, bool))
        self.saxsRadialCheckBox.setChecked(_('WBubble/saxsRadial', False, bool))
        self.waxsRadialCheckBox.setChecked(_('WBubble/waxsRadial', False, bool))
        self.waxsRadStartSpinBox.setValue(_('WBubble/waxsRadialStart', 0, float))
        self.waxsRadStopSpinBox.setValue(_('WBubble/waxsRadialStop', 0, float))
        self.saxsRadStartSpinBox.setValue(_('WBubble/saxsRadialStart', 0, float))
        self.saxsRadStopSpinBox.setValue(_('WBubble/saxsRadialStop', 0, float))
        self.tabWidget.setCurrentIndex(_('WBubble/page', 0, int))

    @QtCore.pyqtSlot()
    def on_exitButton_clicked(self):
        self.close()

    def showServerState(self, status):
        if status['serverRunning']:
            self.serverLampLabel.setPixmap(QtGui.QPixmap(':/grnbtn'))
            self.serverStateLabel.setText(status['serverRunning'])
            self.tabWidget.setTabIcon(0, QtGui.QIcon(QtGui.QPixmap(':/grnbtn')))
            self.stopServerButton.show()
            self.runServerButton.hide()
            self.killServerButton.show()
        else:
            self.serverLampLabel.setPixmap(QtGui.QPixmap(':/redbtn'))
            self.serverStateLabel.setText(status['serverRunning'])
            self.tabWidget.setTabIcon(0, QtGui.QIcon(QtGui.QPixmap(':/redbtn')))
            self.stopServerButton.hide()
            self.runServerButton.show()
            self.serverStateLabel.setText('Server is stopped')
            self.killServerButton.hide()

    def showWaxsState(self, status):
        running = status.get('running', False)
        if running:
            self.waxsLampLabel.setPixmap(QtGui.QPixmap(':/grnbtn'))
            self.tabWidget.setTabIcon(2, QtGui.QIcon(QtGui.QPixmap(':/grnbtn')))
            self.formatLabelText(status.get('path', 'unknown'), self.waxsStateLabel)
            self.runWaxsButton.hide()
            self.stopWaxsButton.show()
        else:
            self.waxsLampLabel.setPixmap(QtGui.QPixmap(':/redbtn'))
            self.tabWidget.setTabIcon(2, QtGui.QIcon(QtGui.QPixmap(':/redbtn')))
            self.formatLabelText('stopped', self.waxsStateLabel)
            self.stopWaxsButton.hide()
            self.runWaxsButton.show()
        self.formatLabelText(os.path.basename(status.get('imageFile', '')), self.waxsLastfileLabel)
        self.formatLabelText(f'{status.get("total", 0)} of {status.get("all", 0)}', self.waxsTotalLabel)

    def formatLabelText(self, text: str, label: QtWidgets.QLabel):
        if len(text) >= self.MaxLabelLen:
            label.setText(f'...{text[-self.MaxLabelLen:]}')
        else:
            label.setText(text)
        label.setToolTip(text)

    def showSaxsState(self, status):
        running = status.get('running', False)
        if running:
            self.saxsLampLabel.setPixmap(QtGui.QPixmap(':/grnbtn'))
            self.tabWidget.setTabIcon(1, QtGui.QIcon(QtGui.QPixmap(':/grnbtn')))
            self.formatLabelText(status.get('path', 'unknown'), self.saxsStateLabel)
            self.runSaxsButton.hide()
            self.stopSaxsButton.show()
        else:
            self.saxsLampLabel.setPixmap(QtGui.QPixmap(':/redbtn'))
            self.tabWidget.setTabIcon(1, QtGui.QIcon(QtGui.QPixmap(':/redbtn')))
            self.formatLabelText('stopped', self.saxsStateLabel)
            self.stopSaxsButton.hide()
            self.runSaxsButton.show()
        self.formatLabelText(os.path.basename(status.get('imageFile', '')), self.saxsLastfileLabel)
        self.formatLabelText(f'{status.get("total", 0)} of {status.get("all", 0)}', self.saxsTotalLabel)

    def showServerErrors(self, errors):
        QtWidgets.QMessageBox.critical(self, 'Server errors', errors)

    def showServerWarnings(self, warnings):
        QtWidgets.QMessageBox.warning(self, 'Server warnings', warnings)

    @QtCore.pyqtSlot(bool)
    def on_localCheckBox_toggled(self, checked):
        if checked:
            self.hostLineEdit.setDisabled(True)
            self.portSpinBox.setDisabled(True)
            self.runServerButton.setText('Start server')
            self.stopServerButton.setText('Stop server')
        else:
            self.hostLineEdit.setEnabled(True)
            self.portSpinBox.setEnabled(True)
            self.runServerButton.setText('Connect')
            self.stopServerButton.setText('Disconnect')

    @QtCore.pyqtSlot()
    def on_stopServerButton_clicked(self):
        self.stopServerButton.hide()
        self.runServerButton.show()
        self.killServerButton.hide()
        self.serverLampLabel.setPixmap(QtGui.QPixmap(':/redbtn'))
        self.serverStateLabel.setText('Disconnected from the server')
        self.connector.disconnectFromServer()

    @QtCore.pyqtSlot()
    def on_runServerButton_clicked(self):
        self.runServerButton.hide()
        self.runServerButton.show()
        self.startServerSignal.emit(self.hostLineEdit.text(), self.portSpinBox.value())

    @QtCore.pyqtSlot()
    def on_killServerButton_clicked(self):
        self.killServerSignal.emit()

    def getSpeed(self):
        return {
            'speed': self.speedCheckBox.isChecked(),
            'sspeed': self.sspeedCheckBox.isEnabled() and self.sspeedCheckBox.isChecked(),
        }

    def getCommonParams(self):
        params = {
            'beamline': self.bgBeamline.checkedButton().tag,
            'units': self.bgUnits.checkedButton().tag,
        }
        params.update(self.getSpeed())
        params.update(self.wsopts.params)
        return params

    @QtCore.pyqtSlot()
    def on_runWaxsButton_clicked(self, run=1):
        path = self.waxsDirLineEdit.text()
        poniPath = self.waxsPoniLineEdit.text()
        ext = self.extEdit.text() if self.extCheckBox.isChecked() else ''
        subdir = self.subdirEdit.text() if self.subdirCheckBox.isChecked() else ''
        multi = ''
        if self.multiCheckBox.isChecked():
            name = self.multiEdit.text()
            multi = name if name else default.MULTICOLUMN_NAME
        if run and (not path or not poniPath):
            QtWidgets.QMessageBox.critical(self, 'WAXS Error', 'You have to set folder and poni file, at least.')
            return
        multiplier = self.multiplyLineEdit.text()
        norm = []
        for n in (self.spinWaxsBkgStart.value(), self.spinWaxsBkgStop.value()):
            try:
                norm.append(float(n))
            except ValueError:
                norm.append(0)

        params = {
            'path': path,
            'run': run,
            'poni': poniPath,
            'bkgCoef': self.waxsBkgCoefSpinBox.value(),
            'backgroundFiles': [s.strip() for s in self.waxsBkgLineEdit.text().split(';') if s],
            'maskFile': self.waxsMaskLineEdit.text(),
            'calibration': float(multiplier) if multiplier else 1,
            'ext': ext,
            'subdir': subdir,
            'multicolumnName': multi,
            'save': self.edfCheckBox.isChecked(),
            'detector': self.waxsDetectorComboBox.currentText(),
            'azimuth': (self.waxsAziStartSpinBox.value(), self.waxsAziStopSpinBox.value()),
            'azimuthSlices': self.waxsSlicesCheckBox.isChecked(),
            'azimuthChecked': self.waxsAzimuthCheckBox.isChecked(),
            'radial': (self.waxsRadStartSpinBox.value(), self.waxsRadStopSpinBox.value()),
            'useRadial': self.waxsRadialCheckBox.isChecked(),
            'normalization': self.comboNorm.currentText(),
            'normrange': norm,
        }
        params.update(self.getCommonParams())
        params.update(self.wWaxsDark.params)
        self.runSignal.emit(params, 'waxs')

    @QtCore.pyqtSlot()
    def on_runSaxsButton_clicked(self, run=1):
        path = self.saxsDirLineEdit.text()
        poniPath = self.saxsPoniLineEdit.text()
        ext = str(self.extEdit.text()) if self.extCheckBox.isChecked() else ''
        subdir = str(self.subdirEdit.text()) if self.subdirCheckBox.isChecked() else ''
        multi = ''
        if self.multiCheckBox.isChecked():
            name = str(self.multiEdit.text())
            multi = name if name else default.MULTICOLUMN_NAME
        if run and (not path or not poniPath):
            QtWidgets.QMessageBox.critical(self, 'SAXS Error', 'You have to set folder and poni file, at least.')
            return
        params = {
            'path': path,
            'run': run,
            'poni': poniPath,
            'bkgCoef': self.saxsBkgCoefSpinBox.value(),
            'azimuth': (self.saxsAziStartSpinBox.value(), self.saxsAziStopSpinBox.value()),
            'maskFile': str(self.saxsMaskLineEdit.text()),
            'backgroundFiles': [s.strip() for s in str(self.saxsBkgLineEdit.text()).split(';') if s],
            'ext': ext,
            'subdir': subdir,
            'multicolumnName': multi,
            'save': self.edfCheckBox.isChecked(),
            'detector': self.saxsDetectorComboBox.currentText(),
            'azimuthSlices': self.saxsSlicesCheckBox.isChecked(),
            'azimuthChecked': self.saxsAzimuthCheckBox.isChecked(),
            'radial': (self.saxsRadStartSpinBox.value(), self.saxsRadStopSpinBox.value()),
            'useRadial': self.saxsRadialCheckBox.isChecked(),
            'normalization': 'Monitor',
            'normrange': (None, None),
        }
        params.update(self.getCommonParams())
        params.update(self.wSaxsParams.params)
        params.update(self.wSaxsDark.params)
        self.runSignal.emit(params, 'saxs')

    @QtCore.pyqtSlot()
    def on_stopWaxsButton_clicked(self):
        self.runSignal.emit({'stop': 1}, 'waxs')

    @QtCore.pyqtSlot()
    def on_stopSaxsButton_clicked(self):
        self.runSignal.emit({'stop': 1}, 'saxs')

    @QtCore.pyqtSlot(bool)
    def on_waxsPlotButton_toggled(self, checked):
        self.waxsPlot.setVisible(checked)

    @QtCore.pyqtSlot(bool)
    def on_saxsPlotButton_toggled(self, checked):
        self.saxsPlot.setVisible(checked)

    @QtCore.pyqtSlot()
    def on_waxsFolderButton_clicked(self):
        self._folderButton_clicked(self.waxsDirLineEdit)

    @QtCore.pyqtSlot()
    def on_saxsFolderButton_clicked(self):
        self._folderButton_clicked(self.saxsDirLineEdit)

    def _folderButton_clicked(self, dirLineEdit):
        d = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select folder', dirLineEdit.text())
        if d:
            dirLineEdit.setText(d)

    @QtCore.pyqtSlot()
    def on_waxsPoniButton_clicked(self):
        self._poniButton_clicked(self.waxsPoniLineEdit)

    @QtCore.pyqtSlot()
    def on_saxsPoniButton_clicked(self):
        self._poniButton_clicked(self.saxsPoniLineEdit)

    def _poniButton_clicked(self, poniLineEdit):
        currentPoni = poniLineEdit.text()
        if currentPoni:
            currentPoni = os.path.dirname(currentPoni)
        poni = QtWidgets.QFileDialog.getOpenFileName(self, 'Select poni file', currentPoni, 'Poni (*.poni)')[0]
        if poni:
            poniLineEdit.setText(poni)

    @QtCore.pyqtSlot()
    def on_waxsBkgButton_clicked(self):
        self._bkgButton_clicked(self.waxsBkgLineEdit)

    @QtCore.pyqtSlot()
    def on_saxsBkgButton_clicked(self):
        self._bkgButton_clicked(self.saxsBkgLineEdit)

    def _bkgButton_clicked(self, bkgLineEdit):
        currentBkg = bkgLineEdit.text()
        if currentBkg:
            currentBkg = os.path.dirname(currentBkg.split(';')[0])
        bkg = QtWidgets.QFileDialog.getOpenFileNames(self, 'Select background files', currentBkg,
                                                     'Frames (*.edf *.cbf)')[0]
        if bkg:
            bkgLineEdit.setText(';'.join(bkg))

    @QtCore.pyqtSlot()
    def on_saxsMaskButton_clicked(self):
        self._maskButton_clicked(self.saxsMaskLineEdit)

    @QtCore.pyqtSlot()
    def on_waxsMaskButton_clicked(self):
        self._maskButton_clicked(self.waxsMaskLineEdit)

    def _maskButton_clicked(self, maskLineEdit):
        mask = maskLineEdit.text()
        mask = QtWidgets.QFileDialog.getOpenFileName(self, 'Select mask file', mask,
                                                     'Masks (*.msk *.npz);;Fit2D mask (*.msk);;Bubble mask (*.npz)')[0]
        if mask:
            maskLineEdit.setText(mask)

    @QtCore.pyqtSlot()
    def on_advancedButton_clicked(self):
        self.wSaxsParams.exec()

    @QtCore.pyqtSlot(bool)
    def on_snblRadio_toggled(self, checked):
        if checked:
            self.beamlineToggledSignal.emit('SNBL')
            self.tabWidget.setTabEnabled(1, False)

    @QtCore.pyqtSlot(bool)
    def on_dubbleRadio_toggled(self, checked):
        if checked:
            self.beamlineToggledSignal.emit('Dubble')
            self.tabWidget.setTabEnabled(1, True)

    @QtCore.pyqtSlot(bool)
    def on_extCheckBox_toggled(self, checked):
        self.extEdit.setEnabled(checked)

    @QtCore.pyqtSlot()
    def on_darkFilesButton_clicked(self):
        self.wSaxsDark.exec()

    @QtCore.pyqtSlot()
    def on_waxsDarkFilesButton_clicked(self):
        self.wWaxsDark.exec()

    @QtCore.pyqtSlot(bool)
    def on_subdirCheckBox_toggled(self, checked):
        self.subdirEdit.setEnabled(checked)

    @QtCore.pyqtSlot(bool)
    def on_multiCheckBox_toggled(self, checked):
        self.multiEdit.setEnabled(checked)

    @QtCore.pyqtSlot()
    def on_saveButton_clicked(self):
        fn = QtWidgets.QFileDialog.getSaveFileName(self, 'Save window settings...', self.saveFolder,
                                                   'Bubble settings (*.bub)')[0]
        if fn:
            self.saveFolder = os.path.dirname(fn)
            self.saveSettings(QtCore.QSettings(fn, QtCore.QSettings.IniFormat))

    @QtCore.pyqtSlot(str)
    def on_saxsDetectorComboBox_currentIndexChanged(self, detector):
        self.darkFilesButton.setEnabled(detector == 'Frelon')
        self.applySaxsDarkSignal.emit()

    @QtCore.pyqtSlot(str)
    def on_waxsDetectorComboBox_currentIndexChanged(self, detector):
        self.waxsDarkFilesButton.setEnabled(detector == 'Frelon')
        self.applyWaxsDarkSignal.emit()

    @QtCore.pyqtSlot(name='on_saxsDirClearButton_clicked')
    @QtCore.pyqtSlot(name='on_saxsPoniClearButton_clicked')
    @QtCore.pyqtSlot(name='on_saxsMaskClearButton_clicked')
    @QtCore.pyqtSlot(name='on_saxsBkgClearButton_clicked')
    @QtCore.pyqtSlot(name='on_waxsDirClearButton_clicked')
    @QtCore.pyqtSlot(name='on_waxsPoniClearButton_clicked')
    @QtCore.pyqtSlot(name='on_waxsMaskClearButton_clicked')
    @QtCore.pyqtSlot(name='on_waxsBkgClearButton_clicked')
    def _clearButton_clicked(self):
        clearButtonSlot(self)

    @QtCore.pyqtSlot()
    def on_loadButton_clicked(self):
        fn = QtWidgets.QFileDialog.getOpenFileName(self, 'Load window settings...', self.saveFolder,
                                                   'Bubble settings (*.bub)')[0]
        if fn:
            self.saveFolder = os.path.dirname(fn)
            self.loadSettings(QtCore.QSettings(fn, QtCore.QSettings.IniFormat))

    @QtCore.pyqtSlot()
    def on_waxsMakeMaskButton_clicked(self):
        self.wWaxsMask.show()

    @QtCore.pyqtSlot()
    def on_saxsMakeMaskButton_clicked(self):
        self.wSaxsMask.show()

    @QtCore.pyqtSlot(bool)
    def on_speedCheckBox_toggled(self, checked):
        self.sspeedCheckBox.setEnabled(checked)
        if not checked:
            self.sspeedCheckBox.setChecked(False)
        self.runSignal.emit(self.getSpeed(), 'saxs')
        self.runSignal.emit(self.getSpeed(), 'waxs')

    @QtCore.pyqtSlot(bool)
    def on_sspeedCheckBox_toggled(self, checked):
        self.multiCheckBox.setEnabled(not checked)
        if not self.multiCheckBox.isEnabled():
            self.multiCheckBox.setChecked(False)
        self.runSignal.emit(self.getSpeed(), 'saxs')
        self.runSignal.emit(self.getSpeed(), 'waxs')

    @QtCore.pyqtSlot()
    def on_aboutButton_clicked(self):
        self.wabout.exec()

    @QtCore.pyqtSlot()
    def on_buttonOptions_clicked(self):
        self.wsopts.exec()

    @QtCore.pyqtSlot(bool)
    def on_saxsSlicesCheckBox_toggled(self, checked):
        self.labelSaxsAzimuth.setText('and step' if checked else 'and stop')

    @QtCore.pyqtSlot(bool)
    def on_saxsRadialCheckBox_toggled(self, checked):
        self.saxsRadStartSpinBox.setEnabled(checked)
        self.saxsRadStopSpinBox.setEnabled(checked)

    @QtCore.pyqtSlot(bool)
    def on_saxsAzimuthCheckBox_toggled(self, checked):
        if not checked:
            self.saxsSlicesCheckBox.setChecked(False)
        self.saxsSlicesCheckBox.setEnabled(checked)
        self.saxsAziStartSpinBox.setEnabled(checked)
        self.saxsAziStopSpinBox.setEnabled(checked)

    @QtCore.pyqtSlot(bool)
    def on_waxsSlicesCheckBox_toggled(self, checked):
        self.labelWaxsAzimuth.setText('and step' if checked else 'and stop')

    @QtCore.pyqtSlot(bool)
    def on_waxsRadialCheckBox_toggled(self, checked):
        self.waxsRadStartSpinBox.setEnabled(checked)
        self.waxsRadStopSpinBox.setEnabled(checked)

    @QtCore.pyqtSlot(bool)
    def on_waxsAzimuthCheckBox_toggled(self, checked):
        if not checked:
            self.waxsSlicesCheckBox.setChecked(False)
        self.waxsSlicesCheckBox.setEnabled(checked)
        self.waxsAziStartSpinBox.setEnabled(checked)
        self.waxsAziStopSpinBox.setEnabled(checked)

    @QtCore.pyqtSlot(str)
    def on_comboNorm_currentTextChanged(self, text: str):
        bkg = text == 'Bkg'
        self.spinWaxsBkgStop.setEnabled(bkg)
        self.spinWaxsBkgStart.setEnabled(bkg)
