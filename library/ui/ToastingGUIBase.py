# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Nov  6 2017)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.grid

###########################################################################
## Class ToastingBase
###########################################################################

class ToastingBase ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Toasting", pos = wx.DefaultPosition, size = wx.Size( 786,600 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHints( wx.Size( 786,600 ), wx.DefaultSize )
		
		self.statusBar = self.CreateStatusBar( 1, 0, wx.ID_ANY )
		self.menuBar = wx.MenuBar( 0 )
		self.fileMenu = wx.Menu()
		self.saveConfigMenuItem = wx.MenuItem( self.fileMenu, wx.ID_ANY, u"Save Config", wx.EmptyString, wx.ITEM_NORMAL )
		self.fileMenu.Append( self.saveConfigMenuItem )
		
		self.loadConfigMenuItem = wx.MenuItem( self.fileMenu, wx.ID_ANY, u"Load Config", wx.EmptyString, wx.ITEM_NORMAL )
		self.fileMenu.Append( self.loadConfigMenuItem )
		
		self.exitMenuItem = wx.MenuItem( self.fileMenu, wx.ID_ANY, u"Exit", wx.EmptyString, wx.ITEM_NORMAL )
		self.fileMenu.Append( self.exitMenuItem )
		
		self.menuBar.Append( self.fileMenu, u"File" ) 
		
		self.helpMenu = wx.Menu()
		self.aboutMenuItem = wx.MenuItem( self.helpMenu, wx.ID_ANY, u"About", wx.EmptyString, wx.ITEM_NORMAL )
		self.helpMenu.Append( self.aboutMenuItem )
		
		self.menuBar.Append( self.helpMenu, u"Help" ) 
		
		self.SetMenuBar( self.menuBar )
		
		baseSizer = wx.BoxSizer( wx.VERTICAL )
		
		bSizer13 = wx.BoxSizer( wx.HORIZONTAL )
		
		bSizer14 = wx.BoxSizer( wx.VERTICAL )
		
		self.celciusRadioButton = wx.RadioButton( self, wx.ID_ANY, u"Celcius", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer14.Add( self.celciusRadioButton, 0, wx.ALL, 5 )
		
		self.fahrenheitRadioButton = wx.RadioButton( self, wx.ID_ANY, u"Fahrenheit", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer14.Add( self.fahrenheitRadioButton, 0, wx.ALL, 5 )
		
		
		bSizer13.Add( bSizer14, 1, wx.EXPAND, 5 )
		
		
		bSizer13.Add( ( 0, 0), 1, wx.EXPAND, 5 )
		
		bSizer15 = wx.BoxSizer( wx.VERTICAL )
		
		bSizer16 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_staticText5 = wx.StaticText( self, wx.ID_ANY, u"Relay", wx.DefaultPosition, wx.Size( 50,-1 ), wx.ALIGN_CENTRE )
		self.m_staticText5.Wrap( -1 )
		bSizer16.Add( self.m_staticText5, 0, wx.TOP, 5 )
		
		self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, u"Temp", wx.DefaultPosition, wx.Size( 50,-1 ), wx.ALIGN_CENTRE )
		self.m_staticText1.Wrap( -1 )
		bSizer16.Add( self.m_staticText1, 0, wx.TOP, 5 )
		
		self.m_staticText2 = wx.StaticText( self, wx.ID_ANY, u"Ref.", wx.DefaultPosition, wx.Size( 50,-1 ), wx.ALIGN_CENTRE )
		self.m_staticText2.Wrap( -1 )
		bSizer16.Add( self.m_staticText2, 0, wx.TOP, 5 )
		
		self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, u"Status", wx.DefaultPosition, wx.Size( 70,-1 ), wx.ALIGN_CENTRE )
		self.m_staticText3.Wrap( -1 )
		bSizer16.Add( self.m_staticText3, 0, wx.TOP, 5 )
		
		self.m_staticText4 = wx.StaticText( self, wx.ID_ANY, u"State", wx.DefaultPosition, wx.Size( 80,-1 ), wx.ALIGN_CENTRE )
		self.m_staticText4.Wrap( -1 )
		bSizer16.Add( self.m_staticText4, 0, wx.TOP, 5 )
		
		
		bSizer15.Add( bSizer16, 1, wx.EXPAND, 5 )
		
		self.statusGrid = wx.grid.Grid( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
		
		# Grid
		self.statusGrid.CreateGrid( 1, 5 )
		self.statusGrid.EnableEditing( False )
		self.statusGrid.EnableGridLines( True )
		self.statusGrid.EnableDragGridSize( False )
		self.statusGrid.SetMargins( 0, 0 )
		
		# Columns
		self.statusGrid.SetColSize( 0, 50 )
		self.statusGrid.AutoSizeColumns()
		self.statusGrid.EnableDragColMove( False )
		self.statusGrid.EnableDragColSize( False )
		self.statusGrid.SetColLabelSize( 0 )
		self.statusGrid.SetColLabelAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
		
		# Rows
		self.statusGrid.SetRowSize( 0, 50 )
		self.statusGrid.AutoSizeRows()
		self.statusGrid.EnableDragRowSize( False )
		self.statusGrid.SetRowLabelSize( 0 )
		self.statusGrid.SetRowLabelAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
		
		# Label Appearance
		
		# Cell Defaults
		self.statusGrid.SetDefaultCellAlignment( wx.ALIGN_LEFT, wx.ALIGN_TOP )
		bSizer15.Add( self.statusGrid, 0, wx.ALL, 5 )
		
		
		bSizer13.Add( bSizer15, 0, wx.EXPAND, 5 )
		
		
		baseSizer.Add( bSizer13, 0, wx.EXPAND, 5 )
		
		self.baseNotebook = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.configurationPanel = wx.Panel( self.baseNotebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		configurationBaseSizer = wx.BoxSizer( wx.VERTICAL )
		
		configurationManagementSizer = wx.BoxSizer( wx.HORIZONTAL )
		
		configurationManagementSizer.SetMinSize( wx.Size( -1,90 ) ) 
		configurationGridStaticBoxSizer = wx.StaticBoxSizer( wx.StaticBox( self.configurationPanel, wx.ID_ANY, u"Configuration Setup" ), wx.HORIZONTAL )
		
		self.configurationGrid = wx.grid.Grid( configurationGridStaticBoxSizer.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
		
		# Grid
		self.configurationGrid.CreateGrid( 0, 0 )
		self.configurationGrid.EnableEditing( True )
		self.configurationGrid.EnableGridLines( True )
		self.configurationGrid.EnableDragGridSize( False )
		self.configurationGrid.SetMargins( 0, 0 )
		
		# Columns
		self.configurationGrid.EnableDragColMove( False )
		self.configurationGrid.EnableDragColSize( True )
		self.configurationGrid.SetColLabelSize( 30 )
		self.configurationGrid.SetColLabelAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
		
		# Rows
		self.configurationGrid.EnableDragRowSize( True )
		self.configurationGrid.SetRowLabelSize( 90 )
		self.configurationGrid.SetRowLabelAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
		
		# Label Appearance
		
		# Cell Defaults
		self.configurationGrid.SetDefaultCellAlignment( wx.ALIGN_LEFT, wx.ALIGN_TOP )
		configurationGridStaticBoxSizer.Add( self.configurationGrid, 1, wx.EXPAND, 5 )
		
		bSizer10 = wx.BoxSizer( wx.VERTICAL )
		
		self.saveConfigButton = wx.Button( configurationGridStaticBoxSizer.GetStaticBox(), wx.ID_ANY, u"Save", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer10.Add( self.saveConfigButton, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.loadConfigButton = wx.Button( configurationGridStaticBoxSizer.GetStaticBox(), wx.ID_ANY, u"Load", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer10.Add( self.loadConfigButton, 0, wx.ALL, 5 )
		
		self.executeConfigButton = wx.Button( configurationGridStaticBoxSizer.GetStaticBox(), wx.ID_ANY, u"Execute", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer10.Add( self.executeConfigButton, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		configurationGridStaticBoxSizer.Add( bSizer10, 0, wx.EXPAND, 5 )
		
		
		configurationManagementSizer.Add( configurationGridStaticBoxSizer, 1, wx.EXPAND, 5 )
		
		
		configurationBaseSizer.Add( configurationManagementSizer, 0, wx.EXPAND, 5 )
		
		configurationVisualizerSizer = wx.BoxSizer( wx.VERTICAL )
		
		self.configurationVisualizerPanel = wx.Panel( self.configurationPanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		configurationVisualizerInnerSizer = wx.BoxSizer( wx.VERTICAL )
		
		
		self.configurationVisualizerPanel.SetSizer( configurationVisualizerInnerSizer )
		self.configurationVisualizerPanel.Layout()
		configurationVisualizerInnerSizer.Fit( self.configurationVisualizerPanel )
		configurationVisualizerSizer.Add( self.configurationVisualizerPanel, 1, wx.EXPAND, 0 )
		
		
		configurationBaseSizer.Add( configurationVisualizerSizer, 1, wx.EXPAND, 0 )
		
		
		self.configurationPanel.SetSizer( configurationBaseSizer )
		self.configurationPanel.Layout()
		configurationBaseSizer.Fit( self.configurationPanel )
		self.baseNotebook.AddPage( self.configurationPanel, u"Configuration", True )
		self.tuningPanel = wx.Panel( self.baseNotebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		tuningBaseSizer = wx.BoxSizer( wx.VERTICAL )
		
		bSizer26 = wx.BoxSizer( wx.HORIZONTAL )
		
		pidTuningStaticBoxSizer = wx.StaticBoxSizer( wx.StaticBox( self.tuningPanel, wx.ID_ANY, u"PIDs" ), wx.HORIZONTAL )
		
		bSizer18 = wx.BoxSizer( wx.VERTICAL )
		
		self.pidPStaticText = wx.StaticText( pidTuningStaticBoxSizer.GetStaticBox(), wx.ID_ANY, u"Proportional Gain (kP)", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		self.pidPStaticText.Wrap( -1 )
		bSizer18.Add( self.pidPStaticText, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.pidIStaticText = wx.StaticText( pidTuningStaticBoxSizer.GetStaticBox(), wx.ID_ANY, u"Integral Gain (kI)", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		self.pidIStaticText.Wrap( -1 )
		bSizer18.Add( self.pidIStaticText, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.pidDStaticText = wx.StaticText( pidTuningStaticBoxSizer.GetStaticBox(), wx.ID_ANY, u"Derivative Gain (kD)", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		self.pidDStaticText.Wrap( -1 )
		bSizer18.Add( self.pidDStaticText, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.pidMinStaticText = wx.StaticText( pidTuningStaticBoxSizer.GetStaticBox(), wx.ID_ANY, u"PID Output Min Limit", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		self.pidMinStaticText.Wrap( -1 )
		bSizer18.Add( self.pidMinStaticText, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.pidMaxOutLimitStaticText = wx.StaticText( pidTuningStaticBoxSizer.GetStaticBox(), wx.ID_ANY, u"PID Output Max Limit", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		self.pidMaxOutLimitStaticText.Wrap( -1 )
		bSizer18.Add( self.pidMaxOutLimitStaticText, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.pidWindupGuardStaticText = wx.StaticText( pidTuningStaticBoxSizer.GetStaticBox(), wx.ID_ANY, u"PID Windup Guard", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		self.pidWindupGuardStaticText.Wrap( -1 )
		bSizer18.Add( self.pidWindupGuardStaticText, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		pidTuningStaticBoxSizer.Add( bSizer18, 0, wx.EXPAND, 5 )
		
		bSizer181 = wx.BoxSizer( wx.VERTICAL )
		
		self.pidPTextCtrl = wx.TextCtrl( pidTuningStaticBoxSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer181.Add( self.pidPTextCtrl, 1, wx.ALL, 5 )
		
		self.pidITextCtrl = wx.TextCtrl( pidTuningStaticBoxSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer181.Add( self.pidITextCtrl, 1, wx.ALL, 5 )
		
		self.pidDTextCtrl = wx.TextCtrl( pidTuningStaticBoxSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer181.Add( self.pidDTextCtrl, 1, wx.ALL, 5 )
		
		self.pidMinOutLimitTextCtrl = wx.TextCtrl( pidTuningStaticBoxSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer181.Add( self.pidMinOutLimitTextCtrl, 1, wx.ALL, 5 )
		
		self.pidMaxOutLimitTextCtrl = wx.TextCtrl( pidTuningStaticBoxSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer181.Add( self.pidMaxOutLimitTextCtrl, 1, wx.ALL, 5 )
		
		self.pidWindupGuardTextCtrl = wx.TextCtrl( pidTuningStaticBoxSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer181.Add( self.pidWindupGuardTextCtrl, 1, wx.ALL, 5 )
		
		
		pidTuningStaticBoxSizer.Add( bSizer181, 0, wx.EXPAND, 5 )
		
		bSizer182 = wx.BoxSizer( wx.VERTICAL )
		
		self.savePIDButton = wx.Button( pidTuningStaticBoxSizer.GetStaticBox(), wx.ID_ANY, u"Save PID Tuning", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer182.Add( self.savePIDButton, 0, wx.ALL, 5 )
		
		
		pidTuningStaticBoxSizer.Add( bSizer182, 0, wx.EXPAND, 5 )
		
		
		bSizer26.Add( pidTuningStaticBoxSizer, 0, wx.EXPAND, 0 )
		
		otherTuningStaticBoxSizer = wx.StaticBoxSizer( wx.StaticBox( self.tuningPanel, wx.ID_ANY, u"Other" ), wx.HORIZONTAL )
		
		bSizer27 = wx.BoxSizer( wx.VERTICAL )
		
		self.timerPeriodStaticText = wx.StaticText( otherTuningStaticBoxSizer.GetStaticBox(), wx.ID_ANY, u"Timer Period (s)", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		self.timerPeriodStaticText.Wrap( -1 )
		bSizer27.Add( self.timerPeriodStaticText, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		bSizer27.Add( ( 0, 0), 1, wx.ALL|wx.EXPAND, 5 )
		
		self.relayPinStaticText = wx.StaticText( otherTuningStaticBoxSizer.GetStaticBox(), wx.ID_ANY, u"Relay Pin (BCM)", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		self.relayPinStaticText.Wrap( -1 )
		bSizer27.Add( self.relayPinStaticText, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		bSizer27.Add( ( 0, 0), 1, wx.ALL|wx.EXPAND, 5 )
		
		self.spiCsPinStaticText = wx.StaticText( otherTuningStaticBoxSizer.GetStaticBox(), wx.ID_ANY, u"SPI CS Pin (BCM)", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		self.spiCsPinStaticText.Wrap( -1 )
		bSizer27.Add( self.spiCsPinStaticText, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		otherTuningStaticBoxSizer.Add( bSizer27, 0, wx.EXPAND, 5 )
		
		bSizer28 = wx.BoxSizer( wx.VERTICAL )
		
		self.timerPeriodTextCtrl = wx.TextCtrl( otherTuningStaticBoxSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer28.Add( self.timerPeriodTextCtrl, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		bSizer28.Add( ( 0, 0), 1, wx.ALL|wx.EXPAND, 5 )
		
		self.relayPinTextCtrl = wx.TextCtrl( otherTuningStaticBoxSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer28.Add( self.relayPinTextCtrl, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		bSizer28.Add( ( 0, 0), 1, wx.ALL|wx.EXPAND, 5 )
		
		self.spiCsPinTextCtrl = wx.TextCtrl( otherTuningStaticBoxSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer28.Add( self.spiCsPinTextCtrl, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		otherTuningStaticBoxSizer.Add( bSizer28, 0, wx.EXPAND, 5 )
		
		bSizer30 = wx.BoxSizer( wx.VERTICAL )
		
		self.saveOtherTuningButton = wx.Button( otherTuningStaticBoxSizer.GetStaticBox(), wx.ID_ANY, u"Save Other Tuning", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer30.Add( self.saveOtherTuningButton, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		otherTuningStaticBoxSizer.Add( bSizer30, 0, wx.EXPAND, 5 )
		
		
		bSizer26.Add( otherTuningStaticBoxSizer, 1, wx.EXPAND, 5 )
		
		
		tuningBaseSizer.Add( bSizer26, 0, wx.EXPAND, 5 )
		
		
		tuningBaseSizer.Add( ( 0, 0), 1, wx.EXPAND, 5 )
		
		
		self.tuningPanel.SetSizer( tuningBaseSizer )
		self.tuningPanel.Layout()
		tuningBaseSizer.Fit( self.tuningPanel )
		self.baseNotebook.AddPage( self.tuningPanel, u"Tuning", False )
		self.executionPanel = wx.Panel( self.baseNotebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		executionBaseSizer = wx.BoxSizer( wx.VERTICAL )
		
		sbSizer3 = wx.StaticBoxSizer( wx.StaticBox( self.executionPanel, wx.ID_ANY, u"Control" ), wx.HORIZONTAL )
		
		self.saveDataButton = wx.Button( sbSizer3.GetStaticBox(), wx.ID_ANY, u"Save Data To CSV", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.saveDataButton.Enable( False )
		
		sbSizer3.Add( self.saveDataButton, 0, wx.ALL, 5 )
		
		
		sbSizer3.Add( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.testButton = wx.Button( sbSizer3.GetStaticBox(), wx.ID_ANY, u"Test Relay", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer3.Add( self.testButton, 0, wx.ALL, 5 )
		
		
		sbSizer3.Add( ( 0, 0), 1, wx.EXPAND, 0 )
		
		self.startStopReflowButton = wx.Button( sbSizer3.GetStaticBox(), wx.ID_ANY, u"Start Reflow", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer3.Add( self.startStopReflowButton, 0, wx.ALL, 5 )
		
		self.pauseReflowButton = wx.Button( sbSizer3.GetStaticBox(), wx.ID_ANY, u"Pause Reflow", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.pauseReflowButton.Enable( False )
		
		sbSizer3.Add( self.pauseReflowButton, 0, wx.BOTTOM|wx.RIGHT|wx.TOP, 5 )
		
		
		executionBaseSizer.Add( sbSizer3, 0, wx.EXPAND, 5 )
		
		executionLiveVisualizationSizer = wx.BoxSizer( wx.VERTICAL )
		
		self.liveVisualizationPanel = wx.Panel( self.executionPanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		liveVisualizationSizer = wx.BoxSizer( wx.VERTICAL )
		
		
		self.liveVisualizationPanel.SetSizer( liveVisualizationSizer )
		self.liveVisualizationPanel.Layout()
		liveVisualizationSizer.Fit( self.liveVisualizationPanel )
		executionLiveVisualizationSizer.Add( self.liveVisualizationPanel, 1, wx.EXPAND, 0 )
		
		
		executionBaseSizer.Add( executionLiveVisualizationSizer, 1, wx.EXPAND, 0 )
		
		
		self.executionPanel.SetSizer( executionBaseSizer )
		self.executionPanel.Layout()
		executionBaseSizer.Fit( self.executionPanel )
		self.baseNotebook.AddPage( self.executionPanel, u"Toasting!", False )
		
		baseSizer.Add( self.baseNotebook, 1, wx.EXPAND, 0 )
		
		progressSizer = wx.BoxSizer( wx.VERTICAL )
		
		self.progressGauge = wx.Gauge( self, wx.ID_ANY, 100, wx.DefaultPosition, wx.DefaultSize, wx.GA_HORIZONTAL )
		progressSizer.Add( self.progressGauge, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 0 )
		
		
		baseSizer.Add( progressSizer, 0, wx.EXPAND, 0 )
		
		
		self.SetSizer( baseSizer )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.Bind( wx.EVT_MENU, self.saveConfigMenuItemOnMenuSelection, id = self.saveConfigMenuItem.GetId() )
		self.Bind( wx.EVT_MENU, self.loadConfigMenuItemOnMenuSelection, id = self.loadConfigMenuItem.GetId() )
		self.Bind( wx.EVT_MENU, self.onClose, id = self.exitMenuItem.GetId() )
		self.Bind( wx.EVT_MENU, self.onAbout, id = self.aboutMenuItem.GetId() )
		self.celciusRadioButton.Bind( wx.EVT_RADIOBUTTON, self.temperatureOnRadioButton )
		self.fahrenheitRadioButton.Bind( wx.EVT_RADIOBUTTON, self.temperatureOnRadioButton )
		self.baseNotebook.Bind( wx.EVT_NOTEBOOK_PAGE_CHANGED, self.baseNotebookOnNotebookPageChanged )
		self.saveConfigButton.Bind( wx.EVT_BUTTON, self.saveConfigButtonOnButtonClick )
		self.loadConfigButton.Bind( wx.EVT_BUTTON, self.loadConfigButtonOnButtonClick )
		self.executeConfigButton.Bind( wx.EVT_BUTTON, self.executeConfigButtonOnButtonClick )
		self.savePIDButton.Bind( wx.EVT_BUTTON, self.savePIDButtonOnButtonClick )
		self.saveOtherTuningButton.Bind( wx.EVT_BUTTON, self.saveOtherTuningButtonOnButtonClick )
		self.saveDataButton.Bind( wx.EVT_BUTTON, self.saveDataButtonOnButtonClick )
		self.testButton.Bind( wx.EVT_BUTTON, self.testButtonOnButtonClick )
		self.startStopReflowButton.Bind( wx.EVT_BUTTON, self.startStopReflowButtonOnButtonClick )
		self.pauseReflowButton.Bind( wx.EVT_BUTTON, self.pauseReflowButtonOnButtonClick )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def saveConfigMenuItemOnMenuSelection( self, event ):
		event.Skip()
	
	def loadConfigMenuItemOnMenuSelection( self, event ):
		event.Skip()
	
	def onClose( self, event ):
		event.Skip()
	
	def onAbout( self, event ):
		event.Skip()
	
	def temperatureOnRadioButton( self, event ):
		event.Skip()
	
	
	def baseNotebookOnNotebookPageChanged( self, event ):
		event.Skip()
	
	def saveConfigButtonOnButtonClick( self, event ):
		event.Skip()
	
	def loadConfigButtonOnButtonClick( self, event ):
		event.Skip()
	
	def executeConfigButtonOnButtonClick( self, event ):
		event.Skip()
	
	def savePIDButtonOnButtonClick( self, event ):
		event.Skip()
	
	def saveOtherTuningButtonOnButtonClick( self, event ):
		event.Skip()
	
	def saveDataButtonOnButtonClick( self, event ):
		event.Skip()
	
	def testButtonOnButtonClick( self, event ):
		event.Skip()
	
	def startStopReflowButtonOnButtonClick( self, event ):
		event.Skip()
	
	def pauseReflowButtonOnButtonClick( self, event ):
		event.Skip()
	

###########################################################################
## Class GraphTestFrame
###########################################################################

class GraphTestFrame ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Graph Test", pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
		
		graphTestBaseSizer = wx.BoxSizer( wx.VERTICAL )
		
		self.graphTestBasePanel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		graphTestInnerSizer = wx.BoxSizer( wx.VERTICAL )
		
		
		self.graphTestBasePanel.SetSizer( graphTestInnerSizer )
		self.graphTestBasePanel.Layout()
		graphTestInnerSizer.Fit( self.graphTestBasePanel )
		graphTestBaseSizer.Add( self.graphTestBasePanel, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		self.SetSizer( graphTestBaseSizer )
		self.Layout()
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass
	

