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

		self.status_bar = self.CreateStatusBar( 1, 0, wx.ID_ANY )
		self.menu_bar = wx.MenuBar( 0 )
		self.file_menu = wx.Menu()
		self.save_config_menu_item = wx.MenuItem( self.file_menu, wx.ID_ANY, u"Save Config"+ u"\t" + u"Ctrl-S", wx.EmptyString, wx.ITEM_NORMAL )
		self.file_menu.Append( self.save_config_menu_item )

		self.load_config_menu_item = wx.MenuItem( self.file_menu, wx.ID_ANY, u"Load Config"+ u"\t" + u"Ctrl-L", wx.EmptyString, wx.ITEM_NORMAL )
		self.file_menu.Append( self.load_config_menu_item )

		self.exit_menu_item = wx.MenuItem( self.file_menu, wx.ID_ANY, u"Exit", wx.EmptyString, wx.ITEM_NORMAL )
		self.file_menu.Append( self.exit_menu_item )

		self.menu_bar.Append( self.file_menu, u"File" )

		self.help_menu = wx.Menu()
		self.about_menu_item = wx.MenuItem( self.help_menu, wx.ID_ANY, u"About", wx.EmptyString, wx.ITEM_NORMAL )
		self.help_menu.Append( self.about_menu_item )

		self.menu_bar.Append( self.help_menu, u"Help" )

		self.SetMenuBar( self.menu_bar )

		base_sizer = wx.BoxSizer( wx.VERTICAL )

		b_sizer_13 = wx.BoxSizer( wx.HORIZONTAL )

		self.status_panel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.status_panel.SetBackgroundColour( wx.Colour( 163, 167, 184 ) )

		b_sizer_261 = wx.BoxSizer( wx.HORIZONTAL )

		b_sizer_39 = wx.BoxSizer( wx.HORIZONTAL )

		self.load_config_button = wx.Button( self.status_panel, wx.ID_ANY, u"Load Config", wx.DefaultPosition, wx.DefaultSize, 0 )
		b_sizer_39.Add( self.load_config_button, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.save_config_button = wx.Button( self.status_panel, wx.ID_ANY, u"Save Config", wx.DefaultPosition, wx.DefaultSize, 0 )
		b_sizer_39.Add( self.save_config_button, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.execute_config_button = wx.Button( self.status_panel, wx.ID_ANY, u"Execute", wx.DefaultPosition, wx.DefaultSize, 0 )
		b_sizer_39.Add( self.execute_config_button, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


		b_sizer_261.Add( b_sizer_39, 1, wx.EXPAND, 5 )


		b_sizer_261.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		b_sizer_14 = wx.BoxSizer( wx.VERTICAL )

		self.celsius_radio_button = wx.RadioButton( self.status_panel, wx.ID_ANY, u"Celsius", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.celsius_radio_button.SetValue( True )
		b_sizer_14.Add( self.celsius_radio_button, 0, wx.EXPAND|wx.LEFT|wx.TOP, 5 )

		self.fahrenheit_radio_button = wx.RadioButton( self.status_panel, wx.ID_ANY, u"Fahrenheit", wx.DefaultPosition, wx.DefaultSize, 0 )
		b_sizer_14.Add( self.fahrenheit_radio_button, 0, wx.BOTTOM|wx.EXPAND|wx.LEFT, 5 )


		b_sizer_261.Add( b_sizer_14, 0, wx.ALIGN_CENTER_VERTICAL, 5 )

		b_sizer_15 = wx.BoxSizer( wx.VERTICAL )

		self.status_grid = wx.grid.Grid( self.status_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )

		# Grid
		self.status_grid.CreateGrid( 1, 5 )
		self.status_grid.EnableEditing( False )
		self.status_grid.EnableGridLines( True )
		self.status_grid.EnableDragGridSize( False )
		self.status_grid.SetMargins( 0, 0 )

		# Columns
		self.status_grid.SetColSize( 0, 80 )
		self.status_grid.AutoSizeColumns()
		self.status_grid.EnableDragColMove( False )
		self.status_grid.EnableDragColSize( False )
		self.status_grid.SetColLabelValue( 0, u"Relay" )
		self.status_grid.SetColLabelValue( 1, u"Temp." )
		self.status_grid.SetColLabelValue( 2, u"Ref." )
		self.status_grid.SetColLabelValue( 3, u"Status" )
		self.status_grid.SetColLabelValue( 4, u"State" )
		self.status_grid.SetColLabelSize( 25 )
		self.status_grid.SetColLabelAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER )

		# Rows
		self.status_grid.SetRowSize( 0, 50 )
		self.status_grid.AutoSizeRows()
		self.status_grid.EnableDragRowSize( False )
		self.status_grid.SetRowLabelSize( 0 )
		self.status_grid.SetRowLabelAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER )

		# Label Appearance
		self.status_grid.SetLabelBackgroundColour( wx.Colour( 229, 229, 229 ) )

		# Cell Defaults
		self.status_grid.SetDefaultCellAlignment( wx.ALIGN_LEFT, wx.ALIGN_TOP )
		b_sizer_15.Add( self.status_grid, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )


		b_sizer_261.Add( b_sizer_15, 1, wx.EXPAND, 5 )


		self.status_panel.SetSizer( b_sizer_261 )
		self.status_panel.Layout()
		b_sizer_261.Fit( self.status_panel )
		b_sizer_13.Add( self.status_panel, 1, wx.EXPAND, 5 )


		base_sizer.Add( b_sizer_13, 0, wx.EXPAND, 5 )

		self.base_notebook = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.execution_panel = wx.Panel( self.base_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		execution_base_sizer = wx.BoxSizer( wx.VERTICAL )

		sb_sizer_3 = wx.StaticBoxSizer( wx.StaticBox( self.execution_panel, wx.ID_ANY, u"Control" ), wx.HORIZONTAL )

		self.save_data_button = wx.Button( sb_sizer_3.GetStaticBox(), wx.ID_ANY, u"Save Data To CSV", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.save_data_button.Enable( False )

		sb_sizer_3.Add( self.save_data_button, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


		sb_sizer_3.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.test_button = wx.Button( sb_sizer_3.GetStaticBox(), wx.ID_ANY, u"Test Relay", wx.DefaultPosition, wx.DefaultSize, 0 )
		sb_sizer_3.Add( self.test_button, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


		sb_sizer_3.Add( ( 0, 0), 1, wx.EXPAND, 0 )

		self.start_stop_reflow_button = wx.Button( sb_sizer_3.GetStaticBox(), wx.ID_ANY, u"Start Reflow", wx.DefaultPosition, wx.DefaultSize, 0 )
		sb_sizer_3.Add( self.start_stop_reflow_button, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		self.pause_reflow_button = wx.Button( sb_sizer_3.GetStaticBox(), wx.ID_ANY, u"Pause Reflow", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.pause_reflow_button.Enable( False )

		sb_sizer_3.Add( self.pause_reflow_button, 0, wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.BOTTOM|wx.RIGHT, 5 )


		execution_base_sizer.Add( sb_sizer_3, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 5 )

		execution_live_visualization_sizer = wx.BoxSizer( wx.VERTICAL )

		self.live_visualization_panel = wx.Panel( self.execution_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		live_visualization_sizer = wx.BoxSizer( wx.VERTICAL )


		self.live_visualization_panel.SetSizer( live_visualization_sizer )
		self.live_visualization_panel.Layout()
		live_visualization_sizer.Fit( self.live_visualization_panel )
		execution_live_visualization_sizer.Add( self.live_visualization_panel, 1, wx.EXPAND, 0 )


		execution_base_sizer.Add( execution_live_visualization_sizer, 1, wx.EXPAND, 0 )


		self.execution_panel.SetSizer( execution_base_sizer )
		self.execution_panel.Layout()
		execution_base_sizer.Fit( self.execution_panel )
		self.base_notebook.AddPage( self.execution_panel, u"Toasting!", False )

		base_sizer.Add( self.base_notebook, 1, wx.ALL|wx.EXPAND, 0 )

		progress_sizer = wx.BoxSizer( wx.VERTICAL )

		self.progress_gauge = wx.Gauge( self, wx.ID_ANY, 100, wx.DefaultPosition, wx.DefaultSize, wx.GA_HORIZONTAL )
		progress_sizer.Add( self.progress_gauge, 0, wx.ALL|wx.EXPAND, 0 )


		base_sizer.Add( progress_sizer, 0, wx.EXPAND, 0 )


		self.SetSizer( base_sizer )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.Bind( wx.EVT_MENU, self.save_config_menu_item_on_menu_selection, id = self.save_config_menu_item.GetId() )
		self.Bind( wx.EVT_MENU, self.load_config_menu_item_on_menu_selection, id = self.load_config_menu_item.GetId() )
		self.Bind( wx.EVT_MENU, self.on_close, id = self.exit_menu_item.GetId() )
		self.Bind( wx.EVT_MENU, self.about_menu_item_on_menu_selection, id = self.about_menu_item.GetId() )
		self.load_config_button.Bind( wx.EVT_BUTTON, self.load_config_button_on_button_click )
		self.save_config_button.Bind( wx.EVT_BUTTON, self.save_config_button_on_button_click )
		self.execute_config_button.Bind( wx.EVT_BUTTON, self.execute_config_button_on_button_click )
		self.celsius_radio_button.Bind( wx.EVT_RADIOBUTTON, self.temperature_on_radio_button )
		self.fahrenheit_radio_button.Bind( wx.EVT_RADIOBUTTON, self.temperature_on_radio_button )
		self.base_notebook.Bind( wx.EVT_NOTEBOOK_PAGE_CHANGED, self.base_notebook_on_notebook_page_changed )
		self.save_data_button.Bind( wx.EVT_BUTTON, self.save_data_button_on_button_click )
		self.test_button.Bind( wx.EVT_BUTTON, self.test_button_on_button_click )
		self.start_stop_reflow_button.Bind( wx.EVT_BUTTON, self.start_stop_reflow_button_on_button_click )
		self.pause_reflow_button.Bind( wx.EVT_BUTTON, self.pause_reflow_button_on_button_click )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def save_config_menu_item_on_menu_selection( self, event ):
		event.Skip()

	def load_config_menu_item_on_menu_selection( self, event ):
		event.Skip()

	def on_close( self, event ):
		event.Skip()

	def about_menu_item_on_menu_selection( self, event ):
		event.Skip()

	def load_config_button_on_button_click( self, event ):
		event.Skip()

	def save_config_button_on_button_click( self, event ):
		event.Skip()

	def execute_config_button_on_button_click( self, event ):
		event.Skip()

	def temperature_on_radio_button( self, event ):
		event.Skip()


	def base_notebook_on_notebook_page_changed( self, event ):
		event.Skip()

	def save_data_button_on_button_click( self, event ):
		event.Skip()

	def test_button_on_button_click( self, event ):
		event.Skip()

	def start_stop_reflow_button_on_button_click( self, event ):
		event.Skip()

	def pause_reflow_button_on_button_click( self, event ):
		event.Skip()


###########################################################################
## Class GraphTestFrame
###########################################################################

class GraphTestFrame ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Graph Test", pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		graph_test_base_sizer = wx.BoxSizer( wx.VERTICAL )

		self.graph_test_base_panel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		graph_test_inner_sizer = wx.BoxSizer( wx.VERTICAL )


		self.graph_test_base_panel.SetSizer( graph_test_inner_sizer )
		self.graph_test_base_panel.Layout()
		graph_test_inner_sizer.Fit( self.graph_test_base_panel )
		graph_test_base_sizer.Add( self.graph_test_base_panel, 1, wx.EXPAND |wx.ALL, 5 )


		self.SetSizer( graph_test_base_sizer )
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

		configuration_base_sizer = wx.BoxSizer( wx.VERTICAL )

		configuration_management_sizer = wx.BoxSizer( wx.HORIZONTAL )

		configuration_management_sizer.SetMinSize( wx.Size( -1,120 ) )
		configuration_grid_static_box_sizer = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Configuration Setup" ), wx.HORIZONTAL )

		b_sizer_41 = wx.BoxSizer( wx.VERTICAL )

		self.configuration_grid = wx.grid.Grid( configuration_grid_static_box_sizer.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL )

		# Grid
		self.configuration_grid.CreateGrid( 3, 0 )
		self.configuration_grid.EnableEditing( True )
		self.configuration_grid.EnableGridLines( True )
		self.configuration_grid.EnableDragGridSize( False )
		self.configuration_grid.SetMargins( 0, 10 )

		# Columns
		self.configuration_grid.EnableDragColMove( False )
		self.configuration_grid.EnableDragColSize( True )
		self.configuration_grid.SetColLabelSize( 1 )
		self.configuration_grid.SetColLabelAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER )

		# Rows
		self.configuration_grid.EnableDragRowSize( True )
		self.configuration_grid.SetRowLabelValue( 0, u"Step Name" )
		self.configuration_grid.SetRowLabelValue( 1, u"Target Temp" )
		self.configuration_grid.SetRowLabelValue( 2, u"Step Duration" )
		self.configuration_grid.SetRowLabelSize( 110 )
		self.configuration_grid.SetRowLabelAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER )

		# Label Appearance
		self.configuration_grid.SetLabelBackgroundColour( wx.Colour( 229, 229, 229 ) )

		# Cell Defaults
		self.configuration_grid.SetDefaultCellAlignment( wx.ALIGN_LEFT, wx.ALIGN_TOP )
		b_sizer_41.Add( self.configuration_grid, 0, wx.ALL|wx.EXPAND, 5 )


		configuration_grid_static_box_sizer.Add( b_sizer_41, 1, wx.EXPAND, 5 )

		b_sizer_40 = wx.BoxSizer( wx.VERTICAL )

		self.add_step_button = wx.Button( configuration_grid_static_box_sizer.GetStaticBox(), wx.ID_ANY, u"Add Step", wx.DefaultPosition, wx.DefaultSize, 0 )
		b_sizer_40.Add( self.add_step_button, 0, wx.ALL|wx.EXPAND, 5 )

		self.remove_step_button = wx.Button( configuration_grid_static_box_sizer.GetStaticBox(), wx.ID_ANY, u"Remove Step", wx.DefaultPosition, wx.DefaultSize, 0 )
		b_sizer_40.Add( self.remove_step_button, 0, wx.ALL|wx.EXPAND, 5 )


		configuration_grid_static_box_sizer.Add( b_sizer_40, 0, wx.EXPAND, 5 )


		configuration_management_sizer.Add( configuration_grid_static_box_sizer, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 5 )


		configuration_base_sizer.Add( configuration_management_sizer, 0, wx.EXPAND, 5 )

		configuration_visualizer_sizer = wx.BoxSizer( wx.VERTICAL )

		self.configuration_visualizer_panel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		configuration_visualizer_inner_sizer = wx.BoxSizer( wx.VERTICAL )


		self.configuration_visualizer_panel.SetSizer( configuration_visualizer_inner_sizer )
		self.configuration_visualizer_panel.Layout()
		configuration_visualizer_inner_sizer.Fit( self.configuration_visualizer_panel )
		configuration_visualizer_sizer.Add( self.configuration_visualizer_panel, 1, wx.EXPAND, 0 )


		configuration_base_sizer.Add( configuration_visualizer_sizer, 1, wx.EXPAND, 0 )


		self.SetSizer( configuration_base_sizer )
		self.Layout()

		# Connect Events
		self.add_step_button.Bind( wx.EVT_BUTTON, self.add_step_button_on_button_click )
		self.remove_step_button.Bind( wx.EVT_BUTTON, self.remove_step_button_on_button_click )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def add_step_button_on_button_click( self, event ):
		event.Skip()

	def remove_step_button_on_button_click( self, event ):
		event.Skip()


###########################################################################
## Class ControlTuningPanelBase
###########################################################################

class ControlTuningPanelBase ( wx.Panel ):

	def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 750,300 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
		wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

		tuning_base_sizer = wx.BoxSizer( wx.VERTICAL )

		b_sizer_26 = wx.BoxSizer( wx.HORIZONTAL )

		pid_tuning_static_box_sizer = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"PIDs" ), wx.VERTICAL )

		pid_flex_grid_sizer = wx.FlexGridSizer( 0, 2, 5, 0 )
		pid_flex_grid_sizer.AddGrowableCol( 1 )
		pid_flex_grid_sizer.SetFlexibleDirection( wx.HORIZONTAL )
		pid_flex_grid_sizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.pid_p_static_text = wx.StaticText( pid_tuning_static_box_sizer.GetStaticBox(), wx.ID_ANY, u"Proportional Gain (kP)", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		self.pid_p_static_text.Wrap( -1 )

		pid_flex_grid_sizer.Add( self.pid_p_static_text, 0, wx.ALIGN_RIGHT|wx.ALL|wx.EXPAND, 5 )

		self.pid_p_text_ctrl = wx.TextCtrl( pid_tuning_static_box_sizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		pid_flex_grid_sizer.Add( self.pid_p_text_ctrl, 0, wx.BOTTOM|wx.EXPAND|wx.LEFT|wx.RIGHT, 5 )

		self.pid_i_static_text = wx.StaticText( pid_tuning_static_box_sizer.GetStaticBox(), wx.ID_ANY, u"Integral Gain (kI)", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		self.pid_i_static_text.Wrap( -1 )

		pid_flex_grid_sizer.Add( self.pid_i_static_text, 0, wx.ALIGN_RIGHT|wx.ALL|wx.EXPAND, 5 )

		self.pid_i_text_ctrl = wx.TextCtrl( pid_tuning_static_box_sizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		pid_flex_grid_sizer.Add( self.pid_i_text_ctrl, 0, wx.BOTTOM|wx.EXPAND|wx.LEFT|wx.RIGHT, 5 )

		self.pid_d_static_text = wx.StaticText( pid_tuning_static_box_sizer.GetStaticBox(), wx.ID_ANY, u"Derivative Gain (kD)", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		self.pid_d_static_text.Wrap( -1 )

		pid_flex_grid_sizer.Add( self.pid_d_static_text, 0, wx.ALIGN_RIGHT|wx.ALL|wx.EXPAND, 5 )

		self.pid_d_text_ctrl = wx.TextCtrl( pid_tuning_static_box_sizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		pid_flex_grid_sizer.Add( self.pid_d_text_ctrl, 0, wx.BOTTOM|wx.EXPAND|wx.LEFT|wx.RIGHT, 5 )

		self.pid_min_out_static_text = wx.StaticText( pid_tuning_static_box_sizer.GetStaticBox(), wx.ID_ANY, u"PID Output Min Limit", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		self.pid_min_out_static_text.Wrap( -1 )

		pid_flex_grid_sizer.Add( self.pid_min_out_static_text, 0, wx.ALIGN_RIGHT|wx.ALL|wx.EXPAND, 5 )

		self.pid_min_out_limit_text_ctrl = wx.TextCtrl( pid_tuning_static_box_sizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		pid_flex_grid_sizer.Add( self.pid_min_out_limit_text_ctrl, 0, wx.BOTTOM|wx.EXPAND|wx.LEFT|wx.RIGHT, 5 )

		self.pid_max_out_static_text = wx.StaticText( pid_tuning_static_box_sizer.GetStaticBox(), wx.ID_ANY, u"PID Output Max Limit", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		self.pid_max_out_static_text.Wrap( -1 )

		pid_flex_grid_sizer.Add( self.pid_max_out_static_text, 0, wx.ALIGN_RIGHT|wx.ALL|wx.EXPAND, 5 )

		self.pid_max_out_limit_text_ctrl = wx.TextCtrl( pid_tuning_static_box_sizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		pid_flex_grid_sizer.Add( self.pid_max_out_limit_text_ctrl, 0, wx.BOTTOM|wx.EXPAND|wx.LEFT|wx.RIGHT, 5 )

		self.pid_windup_guard_static_text = wx.StaticText( pid_tuning_static_box_sizer.GetStaticBox(), wx.ID_ANY, u"PID Windup Guard", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		self.pid_windup_guard_static_text.Wrap( -1 )

		pid_flex_grid_sizer.Add( self.pid_windup_guard_static_text, 0, wx.ALIGN_RIGHT|wx.ALL|wx.EXPAND, 5 )

		self.pid_windup_guard_text_ctrl = wx.TextCtrl( pid_tuning_static_box_sizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		pid_flex_grid_sizer.Add( self.pid_windup_guard_text_ctrl, 0, wx.BOTTOM|wx.EXPAND|wx.LEFT|wx.RIGHT, 5 )


		pid_tuning_static_box_sizer.Add( pid_flex_grid_sizer, 1, wx.EXPAND, 5 )


		b_sizer_26.Add( pid_tuning_static_box_sizer, 1, wx.ALL|wx.EXPAND, 5 )

		other_tuning_static_box_sizer = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Other" ), wx.VERTICAL )

		other_flex_grid_sizer = wx.FlexGridSizer( 0, 2, 5, 0 )
		other_flex_grid_sizer.AddGrowableCol( 1 )
		other_flex_grid_sizer.SetFlexibleDirection( wx.HORIZONTAL )
		other_flex_grid_sizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.timer_period_static_text = wx.StaticText( other_tuning_static_box_sizer.GetStaticBox(), wx.ID_ANY, u"Timer Period (s)", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		self.timer_period_static_text.Wrap( -1 )

		other_flex_grid_sizer.Add( self.timer_period_static_text, 0, wx.ALIGN_RIGHT|wx.ALL|wx.EXPAND, 5 )

		self.timer_period_text_ctrl = wx.TextCtrl( other_tuning_static_box_sizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		other_flex_grid_sizer.Add( self.timer_period_text_ctrl, 0, wx.BOTTOM|wx.EXPAND|wx.LEFT|wx.RIGHT, 5 )

		self.relay_pin_static_text = wx.StaticText( other_tuning_static_box_sizer.GetStaticBox(), wx.ID_ANY, u"Relay Pin (BCM)", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		self.relay_pin_static_text.Wrap( -1 )

		other_flex_grid_sizer.Add( self.relay_pin_static_text, 0, wx.ALIGN_RIGHT|wx.ALL|wx.EXPAND, 5 )

		self.relay_pin_text_ctrl = wx.TextCtrl( other_tuning_static_box_sizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		other_flex_grid_sizer.Add( self.relay_pin_text_ctrl, 0, wx.BOTTOM|wx.EXPAND|wx.LEFT|wx.RIGHT, 5 )

		self.spi_cs_pin_static_text = wx.StaticText( other_tuning_static_box_sizer.GetStaticBox(), wx.ID_ANY, u"SPI CS Pin (0, 1)", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		self.spi_cs_pin_static_text.Wrap( -1 )

		other_flex_grid_sizer.Add( self.spi_cs_pin_static_text, 0, wx.ALIGN_RIGHT|wx.ALL|wx.EXPAND, 5 )

		self.spi_cs_pin_text_ctrl = wx.TextCtrl( other_tuning_static_box_sizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		other_flex_grid_sizer.Add( self.spi_cs_pin_text_ctrl, 0, wx.BOTTOM|wx.EXPAND|wx.LEFT|wx.RIGHT, 5 )


		other_tuning_static_box_sizer.Add( other_flex_grid_sizer, 1, wx.EXPAND, 5 )


		b_sizer_26.Add( other_tuning_static_box_sizer, 1, wx.BOTTOM|wx.EXPAND|wx.RIGHT|wx.TOP, 5 )


		tuning_base_sizer.Add( b_sizer_26, 0, wx.EXPAND, 5 )

		self.update_all_settings_button = wx.Button( self, wx.ID_ANY, u"Update All Settings", wx.DefaultPosition, wx.DefaultSize, 0 )
		tuning_base_sizer.Add( self.update_all_settings_button, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )


		self.SetSizer( tuning_base_sizer )
		self.Layout()

		# Connect Events
		self.pid_p_text_ctrl.Bind( wx.EVT_TEXT_ENTER, self.pid_on_text_enter )
		self.pid_i_text_ctrl.Bind( wx.EVT_TEXT_ENTER, self.pid_on_text_enter )
		self.pid_d_text_ctrl.Bind( wx.EVT_TEXT_ENTER, self.pid_on_text_enter )
		self.pid_min_out_limit_text_ctrl.Bind( wx.EVT_TEXT_ENTER, self.pid_on_text_enter )
		self.pid_max_out_limit_text_ctrl.Bind( wx.EVT_TEXT_ENTER, self.pid_on_text_enter )
		self.pid_windup_guard_text_ctrl.Bind( wx.EVT_TEXT_ENTER, self.pid_on_text_enter )
		self.timer_period_text_ctrl.Bind( wx.EVT_TEXT_ENTER, self.other_tuning_on_text_enter )
		self.relay_pin_text_ctrl.Bind( wx.EVT_TEXT_ENTER, self.other_tuning_on_text_enter )
		self.spi_cs_pin_text_ctrl.Bind( wx.EVT_TEXT_ENTER, self.other_tuning_on_text_enter )
		self.update_all_settings_button.Bind( wx.EVT_BUTTON, self.update_all_settings_button_on_button_click )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def pid_on_text_enter( self, event ):
		event.Skip()






	def other_tuning_on_text_enter( self, event ):
		event.Skip()



	def update_all_settings_button_on_button_click( self, event ):
		event.Skip()


###########################################################################
## Class ExecutionPanelBase
###########################################################################

class ExecutionPanelBase ( wx.Panel ):

	def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
		wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

		execution_base_sizer = wx.BoxSizer( wx.VERTICAL )

		sb_sizer_3 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Control" ), wx.HORIZONTAL )

		self.save_data_button = wx.Button( sb_sizer_3.GetStaticBox(), wx.ID_ANY, u"Save Data To CSV", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.save_data_button.Enable( False )

		sb_sizer_3.Add( self.save_data_button, 0, wx.ALL, 5 )


		sb_sizer_3.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.test_button = wx.Button( sb_sizer_3.GetStaticBox(), wx.ID_ANY, u"Test Relay", wx.DefaultPosition, wx.DefaultSize, 0 )
		sb_sizer_3.Add( self.test_button, 0, wx.ALL, 5 )


		sb_sizer_3.Add( ( 0, 0), 1, wx.EXPAND, 0 )

		self.start_stop_reflow_button = wx.Button( sb_sizer_3.GetStaticBox(), wx.ID_ANY, u"Start Reflow", wx.DefaultPosition, wx.DefaultSize, 0 )
		sb_sizer_3.Add( self.start_stop_reflow_button, 0, wx.ALL, 5 )

		self.pause_reflow_button = wx.Button( sb_sizer_3.GetStaticBox(), wx.ID_ANY, u"Pause Reflow", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.pause_reflow_button.Enable( False )

		sb_sizer_3.Add( self.pause_reflow_button, 0, wx.BOTTOM|wx.RIGHT|wx.TOP, 5 )


		execution_base_sizer.Add( sb_sizer_3, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 5 )

		execution_live_visualization_sizer = wx.BoxSizer( wx.VERTICAL )

		self.live_visualization_panel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		live_visualization_sizer = wx.BoxSizer( wx.VERTICAL )


		self.live_visualization_panel.SetSizer( live_visualization_sizer )
		self.live_visualization_panel.Layout()
		live_visualization_sizer.Fit( self.live_visualization_panel )
		execution_live_visualization_sizer.Add( self.live_visualization_panel, 1, wx.EXPAND, 0 )


		execution_base_sizer.Add( execution_live_visualization_sizer, 1, wx.EXPAND, 0 )


		self.SetSizer( execution_base_sizer )
		self.Layout()

		# Connect Events
		self.save_data_button.Bind( wx.EVT_BUTTON, self.save_data_button_on_button_click )
		self.test_button.Bind( wx.EVT_BUTTON, self.test_button_on_button_click )
		self.start_stop_reflow_button.Bind( wx.EVT_BUTTON, self.start_stop_reflow_button_on_button_click )
		self.pause_reflow_button.Bind( wx.EVT_BUTTON, self.pause_reflow_button_on_button_click )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def save_data_button_on_button_click( self, event ):
		event.Skip()

	def test_button_on_button_click( self, event ):
		event.Skip()

	def start_stop_reflow_button_on_button_click( self, event ):
		event.Skip()

	def pause_reflow_button_on_button_click( self, event ):
		event.Skip()


###########################################################################
## Class PanelTestFrame
###########################################################################

class PanelTestFrame ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 800,500 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		base_sizer = wx.BoxSizer( wx.VERTICAL )


		self.SetSizer( base_sizer )
		self.Layout()

		self.Centre( wx.BOTH )

	def __del__( self ):
		pass


