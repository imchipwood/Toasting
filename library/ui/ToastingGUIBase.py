# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.10.1-0-g8feb16b3)
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
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Toasting", pos = wx.DefaultPosition, size = wx.Size( 800,800 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.Size( 786,800 ), wx.DefaultSize )

		self.statusBar = self.CreateStatusBar( 1, 0, wx.ID_ANY )
		self.menuBar = wx.MenuBar( 0 )
		self.fileMenu = wx.Menu()
		self.saveConfigMenuItem = wx.MenuItem( self.fileMenu, wx.ID_ANY, u"Save Config"+ u"\t" + u"Ctrl-S", wx.EmptyString, wx.ITEM_NORMAL )
		self.fileMenu.Append( self.saveConfigMenuItem )

		self.loadConfigMenuItem = wx.MenuItem( self.fileMenu, wx.ID_ANY, u"Load Config"+ u"\t" + u"Ctrl-L", wx.EmptyString, wx.ITEM_NORMAL )
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

		self.statusPanel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.statusPanel.SetBackgroundColour( wx.Colour( 163, 167, 184 ) )

		bSizer261 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer39 = wx.BoxSizer( wx.HORIZONTAL )

		self.loadConfigButton = wx.Button( self.statusPanel, wx.ID_ANY, u"Load Config", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer39.Add( self.loadConfigButton, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.saveConfigButton = wx.Button( self.statusPanel, wx.ID_ANY, u"Save Config", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer39.Add( self.saveConfigButton, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.executeConfigButton = wx.Button( self.statusPanel, wx.ID_ANY, u"Execute", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer39.Add( self.executeConfigButton, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


		bSizer261.Add( bSizer39, 1, wx.EXPAND, 5 )


		bSizer261.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		bSizer14 = wx.BoxSizer( wx.VERTICAL )

		self.celsiusRadioButton = wx.RadioButton( self.statusPanel, wx.ID_ANY, u"Celsius", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.celsiusRadioButton.SetValue( True )
		bSizer14.Add( self.celsiusRadioButton, 0, wx.EXPAND|wx.LEFT|wx.TOP, 5 )

		self.fahrenheitRadioButton = wx.RadioButton( self.statusPanel, wx.ID_ANY, u"Fahrenheit", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer14.Add( self.fahrenheitRadioButton, 0, wx.BOTTOM|wx.EXPAND|wx.LEFT, 5 )


		bSizer261.Add( bSizer14, 0, wx.EXPAND, 5 )

		bSizer15 = wx.BoxSizer( wx.VERTICAL )

		self.statusGrid = wx.grid.Grid( self.statusPanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )

		# Grid
		self.statusGrid.CreateGrid( 1, 5 )
		self.statusGrid.EnableEditing( False )
		self.statusGrid.EnableGridLines( True )
		self.statusGrid.EnableDragGridSize( False )
		self.statusGrid.SetMargins( 0, 0 )

		# Columns
		self.statusGrid.SetColSize( 0, 80 )
		self.statusGrid.AutoSizeColumns()
		self.statusGrid.EnableDragColMove( False )
		self.statusGrid.EnableDragColSize( False )
		self.statusGrid.SetColLabelValue( 0, u"Relay" )
		self.statusGrid.SetColLabelValue( 1, u"Temp." )
		self.statusGrid.SetColLabelValue( 2, u"Ref." )
		self.statusGrid.SetColLabelValue( 3, u"Status" )
		self.statusGrid.SetColLabelValue( 4, u"State" )
		self.statusGrid.SetColLabelSize( 25 )
		self.statusGrid.SetColLabelAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER )

		# Rows
		self.statusGrid.SetRowSize( 0, 50 )
		self.statusGrid.AutoSizeRows()
		self.statusGrid.EnableDragRowSize( False )
		self.statusGrid.SetRowLabelSize( 0 )
		self.statusGrid.SetRowLabelAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER )

		# Label Appearance
		self.statusGrid.SetLabelBackgroundColour( wx.Colour( 229, 229, 229 ) )

		# Cell Defaults
		self.statusGrid.SetDefaultCellAlignment( wx.ALIGN_LEFT, wx.ALIGN_TOP )
		bSizer15.Add( self.statusGrid, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )


		bSizer261.Add( bSizer15, 1, wx.EXPAND, 5 )


		self.statusPanel.SetSizer( bSizer261 )
		self.statusPanel.Layout()
		bSizer261.Fit( self.statusPanel )
		bSizer13.Add( self.statusPanel, 1, wx.EXPAND, 5 )


		baseSizer.Add( bSizer13, 0, wx.EXPAND, 5 )

		self.baseNotebook = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.executionPanel = wx.Panel( self.baseNotebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		executionBaseSizer = wx.BoxSizer( wx.VERTICAL )

		sbSizer3 = wx.StaticBoxSizer( wx.StaticBox( self.executionPanel, wx.ID_ANY, u"Control" ), wx.HORIZONTAL )

		self.saveDataButton = wx.Button( sbSizer3.GetStaticBox(), wx.ID_ANY, u"Save Data To CSV", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.saveDataButton.Enable( False )

		sbSizer3.Add( self.saveDataButton, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


		sbSizer3.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.testButton = wx.Button( sbSizer3.GetStaticBox(), wx.ID_ANY, u"Test Relay", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer3.Add( self.testButton, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


		sbSizer3.Add( ( 0, 0), 1, wx.EXPAND, 0 )

		self.startStopReflowButton = wx.Button( sbSizer3.GetStaticBox(), wx.ID_ANY, u"Start Reflow", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer3.Add( self.startStopReflowButton, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		self.pauseReflowButton = wx.Button( sbSizer3.GetStaticBox(), wx.ID_ANY, u"Pause Reflow", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.pauseReflowButton.Enable( False )

		sbSizer3.Add( self.pauseReflowButton, 0, wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.BOTTOM|wx.RIGHT, 5 )


		executionBaseSizer.Add( sbSizer3, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 5 )

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

		baseSizer.Add( self.baseNotebook, 1, wx.ALL|wx.EXPAND, 0 )

		progressSizer = wx.BoxSizer( wx.VERTICAL )

		self.progressGauge = wx.Gauge( self, wx.ID_ANY, 100, wx.DefaultPosition, wx.DefaultSize, wx.GA_HORIZONTAL )
		progressSizer.Add( self.progressGauge, 0, wx.ALL|wx.EXPAND, 0 )


		baseSizer.Add( progressSizer, 0, wx.EXPAND, 0 )


		self.SetSizer( baseSizer )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.Bind( wx.EVT_MENU, self.saveConfigMenuItemOnMenuSelection, id = self.saveConfigMenuItem.GetId() )
		self.Bind( wx.EVT_MENU, self.loadConfigMenuItemOnMenuSelection, id = self.loadConfigMenuItem.GetId() )
		self.Bind( wx.EVT_MENU, self.onClose, id = self.exitMenuItem.GetId() )
		self.Bind( wx.EVT_MENU, self.aboutMenuItemOnMenuSelection, id = self.aboutMenuItem.GetId() )
		self.loadConfigButton.Bind( wx.EVT_BUTTON, self.loadConfigButtonOnButtonClick )
		self.saveConfigButton.Bind( wx.EVT_BUTTON, self.saveConfigButtonOnButtonClick )
		self.executeConfigButton.Bind( wx.EVT_BUTTON, self.executeConfigButtonOnButtonClick )
		self.celsiusRadioButton.Bind( wx.EVT_RADIOBUTTON, self.temperatureOnRadioButton )
		self.fahrenheitRadioButton.Bind( wx.EVT_RADIOBUTTON, self.temperatureOnRadioButton )
		self.baseNotebook.Bind( wx.EVT_NOTEBOOK_PAGE_CHANGED, self.baseNotebookOnNotebookPageChanged )
		self.saveDataButton.Bind( wx.EVT_BUTTON, self.saveDataButtonOnButtonClick )
		self.testButton.Bind( wx.EVT_BUTTON, self.testButtonOnButtonClick )
		self.startStopReflowButton.Bind( wx.EVT_BUTTON, self.startStopReflowButtonOnButtonClick )
		self.pauseReflowButton.Bind( wx.EVT_BUTTON, self.pauseReflowButtonOnButtonClick )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def saveConfigMenuItemOnMenuSelection( self, event ):
		event.Skip()

	def loadConfigMenuItemOnMenuSelection( self, event ):
		event.Skip()

	def onClose( self, event ):
		event.Skip()

	def aboutMenuItemOnMenuSelection( self, event ):
		event.Skip()

	def loadConfigButtonOnButtonClick( self, event ):
		event.Skip()

	def saveConfigButtonOnButtonClick( self, event ):
		event.Skip()

	def executeConfigButtonOnButtonClick( self, event ):
		event.Skip()

	def temperatureOnRadioButton( self, event ):
		event.Skip()


	def baseNotebookOnNotebookPageChanged( self, event ):
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


###########################################################################
## Class StateConfigurationPanelBase
###########################################################################

class StateConfigurationPanelBase ( wx.Panel ):

	def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
		wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

		configurationBaseSizer = wx.BoxSizer( wx.VERTICAL )

		configurationManagementSizer = wx.BoxSizer( wx.HORIZONTAL )

		configurationManagementSizer.SetMinSize( wx.Size( -1,120 ) )
		configurationGridStaticBoxSizer = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Configuration Setup" ), wx.HORIZONTAL )

		bSizer41 = wx.BoxSizer( wx.VERTICAL )

		self.configurationGrid = wx.grid.Grid( configurationGridStaticBoxSizer.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL )

		# Grid
		self.configurationGrid.CreateGrid( 3, 0 )
		self.configurationGrid.EnableEditing( True )
		self.configurationGrid.EnableGridLines( True )
		self.configurationGrid.EnableDragGridSize( False )
		self.configurationGrid.SetMargins( 0, 10 )

		# Columns
		self.configurationGrid.EnableDragColMove( False )
		self.configurationGrid.EnableDragColSize( True )
		self.configurationGrid.SetColLabelSize( 1 )
		self.configurationGrid.SetColLabelAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER )

		# Rows
		self.configurationGrid.EnableDragRowSize( True )
		self.configurationGrid.SetRowLabelValue( 0, u"Step Name" )
		self.configurationGrid.SetRowLabelValue( 1, u"Target Temp" )
		self.configurationGrid.SetRowLabelValue( 2, u"Step Duration" )
		self.configurationGrid.SetRowLabelSize( 110 )
		self.configurationGrid.SetRowLabelAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER )

		# Label Appearance
		self.configurationGrid.SetLabelBackgroundColour( wx.Colour( 229, 229, 229 ) )

		# Cell Defaults
		self.configurationGrid.SetDefaultCellAlignment( wx.ALIGN_LEFT, wx.ALIGN_TOP )
		bSizer41.Add( self.configurationGrid, 0, wx.ALL|wx.EXPAND, 5 )


		configurationGridStaticBoxSizer.Add( bSizer41, 1, wx.EXPAND, 5 )

		bSizer40 = wx.BoxSizer( wx.VERTICAL )

		self.addStepButton = wx.Button( configurationGridStaticBoxSizer.GetStaticBox(), wx.ID_ANY, u"Add Step", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer40.Add( self.addStepButton, 0, wx.ALL|wx.EXPAND, 5 )

		self.removeStepButton = wx.Button( configurationGridStaticBoxSizer.GetStaticBox(), wx.ID_ANY, u"Remove Step", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer40.Add( self.removeStepButton, 0, wx.ALL|wx.EXPAND, 5 )


		configurationGridStaticBoxSizer.Add( bSizer40, 0, wx.EXPAND, 5 )


		configurationManagementSizer.Add( configurationGridStaticBoxSizer, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 5 )


		configurationBaseSizer.Add( configurationManagementSizer, 0, wx.EXPAND, 5 )

		configurationVisualizerSizer = wx.BoxSizer( wx.VERTICAL )

		self.configurationVisualizerPanel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		configurationVisualizerInnerSizer = wx.BoxSizer( wx.VERTICAL )


		self.configurationVisualizerPanel.SetSizer( configurationVisualizerInnerSizer )
		self.configurationVisualizerPanel.Layout()
		configurationVisualizerInnerSizer.Fit( self.configurationVisualizerPanel )
		configurationVisualizerSizer.Add( self.configurationVisualizerPanel, 1, wx.EXPAND, 0 )


		configurationBaseSizer.Add( configurationVisualizerSizer, 1, wx.EXPAND, 0 )


		self.SetSizer( configurationBaseSizer )
		self.Layout()

		# Connect Events
		self.addStepButton.Bind( wx.EVT_BUTTON, self.addStepButtonOnButtonClick )
		self.removeStepButton.Bind( wx.EVT_BUTTON, self.removeStepButtonOnButtonClick )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def addStepButtonOnButtonClick( self, event ):
		event.Skip()

	def removeStepButtonOnButtonClick( self, event ):
		event.Skip()


###########################################################################
## Class ControlTuningPanelBase
###########################################################################

class ControlTuningPanelBase ( wx.Panel ):

	def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 750,300 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
		wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

		tuningBaseSizer1 = wx.BoxSizer( wx.VERTICAL )

		bSizer26 = wx.BoxSizer( wx.HORIZONTAL )

		pidTuningStaticBoxSizer = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"PIDs" ), wx.VERTICAL )

		pidFlexGridSizer = wx.FlexGridSizer( 0, 2, 5, 0 )
		pidFlexGridSizer.AddGrowableCol( 1 )
		pidFlexGridSizer.SetFlexibleDirection( wx.HORIZONTAL )
		pidFlexGridSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.pidPStaticText = wx.StaticText( pidTuningStaticBoxSizer.GetStaticBox(), wx.ID_ANY, u"Proportional Gain (kP)", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		self.pidPStaticText.Wrap( -1 )

		pidFlexGridSizer.Add( self.pidPStaticText, 0, wx.ALIGN_RIGHT|wx.ALL|wx.EXPAND, 5 )

		self.pidPTextCtrl = wx.TextCtrl( pidTuningStaticBoxSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		pidFlexGridSizer.Add( self.pidPTextCtrl, 0, wx.BOTTOM|wx.EXPAND|wx.LEFT|wx.RIGHT, 5 )

		self.pidIStaticText = wx.StaticText( pidTuningStaticBoxSizer.GetStaticBox(), wx.ID_ANY, u"Integral Gain (kI)", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		self.pidIStaticText.Wrap( -1 )

		pidFlexGridSizer.Add( self.pidIStaticText, 0, wx.ALIGN_RIGHT|wx.ALL|wx.EXPAND, 5 )

		self.pidITextCtrl = wx.TextCtrl( pidTuningStaticBoxSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		pidFlexGridSizer.Add( self.pidITextCtrl, 0, wx.BOTTOM|wx.EXPAND|wx.LEFT|wx.RIGHT, 5 )

		self.pidDStaticText = wx.StaticText( pidTuningStaticBoxSizer.GetStaticBox(), wx.ID_ANY, u"Derivative Gain (kD)", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		self.pidDStaticText.Wrap( -1 )

		pidFlexGridSizer.Add( self.pidDStaticText, 0, wx.ALIGN_RIGHT|wx.ALL|wx.EXPAND, 5 )

		self.pidDTextCtrl = wx.TextCtrl( pidTuningStaticBoxSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		pidFlexGridSizer.Add( self.pidDTextCtrl, 0, wx.BOTTOM|wx.EXPAND|wx.LEFT|wx.RIGHT, 5 )

		self.pidMinStaticText = wx.StaticText( pidTuningStaticBoxSizer.GetStaticBox(), wx.ID_ANY, u"PID Output Min Limit", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		self.pidMinStaticText.Wrap( -1 )

		pidFlexGridSizer.Add( self.pidMinStaticText, 0, wx.ALIGN_RIGHT|wx.ALL|wx.EXPAND, 5 )

		self.pidMinOutLimitTextCtrl = wx.TextCtrl( pidTuningStaticBoxSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		pidFlexGridSizer.Add( self.pidMinOutLimitTextCtrl, 0, wx.BOTTOM|wx.EXPAND|wx.LEFT|wx.RIGHT, 5 )

		self.pidMaxOutLimitStaticText = wx.StaticText( pidTuningStaticBoxSizer.GetStaticBox(), wx.ID_ANY, u"PID Output Max Limit", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		self.pidMaxOutLimitStaticText.Wrap( -1 )

		pidFlexGridSizer.Add( self.pidMaxOutLimitStaticText, 0, wx.ALIGN_RIGHT|wx.ALL|wx.EXPAND, 5 )

		self.pidMaxOutLimitTextCtrl = wx.TextCtrl( pidTuningStaticBoxSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		pidFlexGridSizer.Add( self.pidMaxOutLimitTextCtrl, 0, wx.BOTTOM|wx.EXPAND|wx.LEFT|wx.RIGHT, 5 )

		self.pidWindupGuardStaticText = wx.StaticText( pidTuningStaticBoxSizer.GetStaticBox(), wx.ID_ANY, u"PID Windup Guard", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		self.pidWindupGuardStaticText.Wrap( -1 )

		pidFlexGridSizer.Add( self.pidWindupGuardStaticText, 0, wx.ALIGN_RIGHT|wx.ALL|wx.EXPAND, 5 )

		self.pidWindupGuardTextCtrl = wx.TextCtrl( pidTuningStaticBoxSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		pidFlexGridSizer.Add( self.pidWindupGuardTextCtrl, 0, wx.BOTTOM|wx.EXPAND|wx.LEFT|wx.RIGHT, 5 )


		pidTuningStaticBoxSizer.Add( pidFlexGridSizer, 1, wx.EXPAND, 5 )


		bSizer26.Add( pidTuningStaticBoxSizer, 1, wx.ALL|wx.EXPAND, 5 )

		otherTuningStaticBoxSizer = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Other" ), wx.VERTICAL )

		otherFlexGridSizer = wx.FlexGridSizer( 0, 2, 5, 0 )
		otherFlexGridSizer.AddGrowableCol( 1 )
		otherFlexGridSizer.SetFlexibleDirection( wx.HORIZONTAL )
		otherFlexGridSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.timerPeriodStaticText = wx.StaticText( otherTuningStaticBoxSizer.GetStaticBox(), wx.ID_ANY, u"Timer Period (s)", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		self.timerPeriodStaticText.Wrap( -1 )

		otherFlexGridSizer.Add( self.timerPeriodStaticText, 0, wx.ALIGN_RIGHT|wx.ALL|wx.EXPAND, 5 )

		self.timerPeriodTextCtrl = wx.TextCtrl( otherTuningStaticBoxSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		otherFlexGridSizer.Add( self.timerPeriodTextCtrl, 0, wx.BOTTOM|wx.EXPAND|wx.LEFT|wx.RIGHT, 5 )

		self.relayPinStaticText = wx.StaticText( otherTuningStaticBoxSizer.GetStaticBox(), wx.ID_ANY, u"Relay Pin (BCM)", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		self.relayPinStaticText.Wrap( -1 )

		otherFlexGridSizer.Add( self.relayPinStaticText, 0, wx.ALIGN_RIGHT|wx.ALL|wx.EXPAND, 5 )

		self.relayPinTextCtrl = wx.TextCtrl( otherTuningStaticBoxSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		otherFlexGridSizer.Add( self.relayPinTextCtrl, 0, wx.BOTTOM|wx.EXPAND|wx.LEFT|wx.RIGHT, 5 )

		self.spiCsPinStaticText = wx.StaticText( otherTuningStaticBoxSizer.GetStaticBox(), wx.ID_ANY, u"SPI CS Pin (0, 1)", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		self.spiCsPinStaticText.Wrap( -1 )

		otherFlexGridSizer.Add( self.spiCsPinStaticText, 0, wx.ALIGN_RIGHT|wx.ALL|wx.EXPAND, 5 )

		self.spiCsPinTextCtrl = wx.TextCtrl( otherTuningStaticBoxSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		otherFlexGridSizer.Add( self.spiCsPinTextCtrl, 0, wx.BOTTOM|wx.EXPAND|wx.LEFT|wx.RIGHT, 5 )


		otherTuningStaticBoxSizer.Add( otherFlexGridSizer, 1, wx.EXPAND, 5 )


		bSizer26.Add( otherTuningStaticBoxSizer, 1, wx.BOTTOM|wx.EXPAND|wx.RIGHT|wx.TOP, 5 )


		tuningBaseSizer1.Add( bSizer26, 0, wx.EXPAND, 5 )

		self.updateAllSettingsButton = wx.Button( self, wx.ID_ANY, u"Update All Settings", wx.DefaultPosition, wx.DefaultSize, 0 )
		tuningBaseSizer1.Add( self.updateAllSettingsButton, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )


		self.SetSizer( tuningBaseSizer1 )
		self.Layout()

		# Connect Events
		self.pidPTextCtrl.Bind( wx.EVT_TEXT_ENTER, self.pidOnTextEnter )
		self.pidITextCtrl.Bind( wx.EVT_TEXT_ENTER, self.pidOnTextEnter )
		self.pidDTextCtrl.Bind( wx.EVT_TEXT_ENTER, self.pidOnTextEnter )
		self.pidMinOutLimitTextCtrl.Bind( wx.EVT_TEXT_ENTER, self.pidOnTextEnter )
		self.pidMaxOutLimitTextCtrl.Bind( wx.EVT_TEXT_ENTER, self.pidOnTextEnter )
		self.pidWindupGuardTextCtrl.Bind( wx.EVT_TEXT_ENTER, self.pidOnTextEnter )
		self.timerPeriodTextCtrl.Bind( wx.EVT_TEXT_ENTER, self.otherTuningOnTextEnter )
		self.relayPinTextCtrl.Bind( wx.EVT_TEXT_ENTER, self.otherTuningOnTextEnter )
		self.spiCsPinTextCtrl.Bind( wx.EVT_TEXT_ENTER, self.otherTuningOnTextEnter )
		self.updateAllSettingsButton.Bind( wx.EVT_BUTTON, self.updateAllSettingsButtonOnButtonClick )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def pidOnTextEnter( self, event ):
		event.Skip()






	def otherTuningOnTextEnter( self, event ):
		event.Skip()



	def updateAllSettingsButtonOnButtonClick( self, event ):
		event.Skip()


###########################################################################
## Class ExecutionPanelBase
###########################################################################

class ExecutionPanelBase ( wx.Panel ):

	def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
		wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

		executionBaseSizer = wx.BoxSizer( wx.VERTICAL )

		sbSizer3 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Control" ), wx.HORIZONTAL )

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


		executionBaseSizer.Add( sbSizer3, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 5 )

		executionLiveVisualizationSizer = wx.BoxSizer( wx.VERTICAL )

		self.liveVisualizationPanel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		liveVisualizationSizer = wx.BoxSizer( wx.VERTICAL )


		self.liveVisualizationPanel.SetSizer( liveVisualizationSizer )
		self.liveVisualizationPanel.Layout()
		liveVisualizationSizer.Fit( self.liveVisualizationPanel )
		executionLiveVisualizationSizer.Add( self.liveVisualizationPanel, 1, wx.EXPAND, 0 )


		executionBaseSizer.Add( executionLiveVisualizationSizer, 1, wx.EXPAND, 0 )


		self.SetSizer( executionBaseSizer )
		self.Layout()

		# Connect Events
		self.saveDataButton.Bind( wx.EVT_BUTTON, self.saveDataButtonOnButtonClick )
		self.testButton.Bind( wx.EVT_BUTTON, self.testButtonOnButtonClick )
		self.startStopReflowButton.Bind( wx.EVT_BUTTON, self.startStopReflowButtonOnButtonClick )
		self.pauseReflowButton.Bind( wx.EVT_BUTTON, self.pauseReflowButtonOnButtonClick )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def saveDataButtonOnButtonClick( self, event ):
		event.Skip()

	def testButtonOnButtonClick( self, event ):
		event.Skip()

	def startStopReflowButtonOnButtonClick( self, event ):
		event.Skip()

	def pauseReflowButtonOnButtonClick( self, event ):
		event.Skip()


###########################################################################
## Class PanelTestFrame
###########################################################################

class PanelTestFrame ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 800,500 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		baseSizer = wx.BoxSizer( wx.VERTICAL )


		self.SetSizer( baseSizer )
		self.Layout()

		self.Centre( wx.BOTH )

	def __del__( self ):
		pass


