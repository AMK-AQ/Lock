import logging
import os
from typing import Annotated, Optional
import qt
import vtk
import slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
#
# Lock
#

class Lock(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "Lock"  # TODO: make this more human readable by adding spaces
        self.parent.categories = ["Examples"]  # TODO: set categories (folders where the module shows up in the module selector)
        self.parent.dependencies = []  # TODO: add here list of module names that this module requires
        self.parent.contributors = ["John Doe (AnyWare Corp.)"]  # TODO: replace with "Firstname Lastname (Organization)"
        # TODO: update with short description of the module and a link to online module documentation
        self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
See more information in <a href="https://github.com/organization/projectname#Lock">module documentation</a>.
"""
        # TODO: replace with organization, grant and thanks
        self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc., Andras Lasso, PerkLab,
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
"""

        # Additional initialization step after application startup is complete
        slicer.app.connect("startupCompleted()", registerSampleData)


#
# Register sample data sets in Sample Data module
#

def registerSampleData():
    """
    Add data sets to Sample Data module.
    """
    # It is always recommended to provide sample data for users to make it easy to try the module,
    # but if no sample data is available then this method (and associated startupCompeted signal connection) can be removed.

    import SampleData
    iconsPath = os.path.join(os.path.dirname(__file__), 'Resources/Icons')

    # To ensure that the source code repository remains small (can be downloaded and installed quickly)
    # it is recommended to store data sets that are larger than a few MB in a Github release.

    # Lock1
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category='Lock',
        sampleName='Lock1',
        # Thumbnail should have size of approximately 260x280 pixels and stored in Resources/Icons folder.
        # It can be created by Screen Capture module, "Capture all views" option enabled, "Number of images" set to "Single".
        thumbnailFileName=os.path.join(iconsPath, 'Lock1.png'),
        # Download URL and target file name
        uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95",
        fileNames='Lock1.nrrd',
        # Checksum to ensure file integrity. Can be computed by this command:
        #  import hashlib; print(hashlib.sha256(open(filename, "rb").read()).hexdigest())
        checksums='SHA256:998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95',
        # This node name will be used when the data set is loaded
        nodeNames='Lock1'
    )

    # Lock2
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category='Lock',
        sampleName='Lock2',
        thumbnailFileName=os.path.join(iconsPath, 'Lock2.png'),
        # Download URL and target file name
        uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97",
        fileNames='Lock2.nrrd',
        checksums='SHA256:1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97',
        # This node name will be used when the data set is loaded
        nodeNames='Lock2'
    )
#
# LockWidget
#

class LockWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent=None) -> None:
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.__init__(self, parent)
       
    def setup(self) -> None:
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.setup(self)

        self.ASIS_R_layout, self.ASIS_R = self.create_layout(
            label_name="ASIS_R", tooltip_text="Anterior Superior Iliac Spine Right"
        )
        self.PT_L_layout, self.PT_L= self.create_layout(
            label_name="PT_L", tooltip_text="Pubic Tubercle Left"
        )
        self.PT_R_layout, self.PT_R = self.create_layout(
            label_name="PT_R", tooltip_text="Pubic Tubercle Right"
        )
        self.fiducialVisibleButton = Button(
            name="Visibility",
            callback=self.on_invisibility_fiducial_point_button,
            is_checkable=True
        )
        self.AlignBox = HBox(
            self.fiducialVisibleButton

        )

        alignment_point_layout = VBox(
            self.ASIS_R_layout,
            self.PT_L_layout,
            self.PT_R_layout,
            self.AlignBox,
        )
        self.alignment_point_group_box = GroupBox(
            title="Select points for volume alignment", layout=alignment_point_layout
        )
        
        self.layout.addWidget(self.alignment_point_group_box)

    def updateParameterNodeFromGUI(self, caller=None, event=None):
        """
        This method is called when the user makes any change in the GUI.
        The changes are saved into the parameter node (so that they are restored when the scene is saved and loaded).
        """

        if self._parameterNode is None or self._updatingGUIFromParameterNode:
            return

        wasModified = (
            self._parameterNode.StartModify()
        )  # Modify all properties in a single batch

        self._parameterNode.EndModify(wasModified)

    def create_label(self, label_name, tooltip_text):
        label = Label(label_name, None, tooltip_text)
        return label

    def create_node_selector(self, label_name, node_class="vtkMRMLMarkupsFiducialNode"):
        node_selector = NodeSelector.create_node_selector(
            self, label_name, node_class, call_back=self.updateParameterNodeFromGUI
        )
        return node_selector

    def create_place_markup_button(
        self, label_name, node_class="vtkMRMLMarkupsFiducialNode", transform=None
    ):
        place_markup_button = qt.QPushButton("Place Markup")
        place_markup_button.connect(
            "clicked()",
            lambda: self.add_markup_node_with_name_and_class(
                name=label_name, node_class=node_class, transform=transform
            ),
        )
        return place_markup_button

    def create_jump_button(self, label_name):
        jump_button = qt.QPushButton("Jump")
        jump_button.connect("clicked()", lambda: self.get_jump_callback(label_name))
        return jump_button

    def create_lock_button(self, label_name):
        lock_button = qt.QPushButton()
        lock_button.connect("clicked()", lambda: self.on_lock_button(label_name))
        lock_button.setCheckable(True)
       
        # Check if node exists before entering the lock status loop
        try:
            node = slicer.util.getNode(label_name)
            if node and node.GetLocked():
                lock_button.setIcon(Icons.locked_icon)
                lock_button.setChecked(True)
            else:
                lock_button.setIcon(Icons.unlocked_icon)
        except slicer.util.MRMLNodeNotFoundException:
            lock_button.setIcon(Icons.unlocked_icon)

        # Define a slot to change the icon when the button is clicked
        def change_icon(checked):
            node = slicer.util.getNode(label_name)
            if node and node.GetLocked():
                lock_button.setIcon(Icons.locked_icon)
                lock_button.setChecked(True)
            else:
                lock_button.setIcon(Icons.unlocked_icon)

        lock_button.clicked.connect(change_icon)
        
        return lock_button

    def on_lock_button(self, name: str) -> None:
        """
        This function toggles the locked status of a fiducial node with the given name. If the node is currently locked, it will
        be unlocked, and vice versa.

        Args:
            name(str): The name of the fiducial node to toggle the locked status for.

        Returns:
            None
        """
        fiducial_node = slicer.util.getFirstNodeByName(name)
        fiducial_node.SetLocked(not fiducial_node.GetLocked())
        
       
    def on_invisibility_fiducial_point_button(self):
        self.invisible_fiducial_points()
        self.fiducialVisibleButton.clicked.connect(LockWidget.update_button(self))
        """
          Calling the function update_button by clicking fiducialVisibleButton.
        """
        self.fiducialVisibleButton.setCheckable(True)
       
    def update_button(self):
         """
           This function will set the icon of lock buttons to locked_icon.

           Parameters:
                    ASIS_R
                    PT_L
                    PT_R
           Returns:
                 None         
         """
         count0=self.ASIS_R_layout.count()
         nodes = ["ASIS_R", "PT_L", "PT_R"] 
         layout=[self.ASIS_R_layout,self.PT_L_layout,self.PT_R_layout]   
         for i in range(count0):
            if i==3:
                j=0
                for node in nodes:
                 node=slicer.util.getNode(node)
                 node.SetLocked(True)
                 if node and not node.SetLocked(True):
                  widget=layout[j].itemAt(3).widget()
                  widget.setIcon(Icons.locked_icon)
                  widget.setChecked(True)
                 j=j+1           
    @staticmethod
    def invisible_fiducial_points():
        """Toggle visibility of specified fiducial points in the scene.

        The function gets a list of node names for fiducial points. It then checks if
        each of these nodes exists in the current MRML scene. For every node that exists,
        the visibility of the display node is toggled.

        Parameters:
            None

        Returns:
            None
        """
        # Define a list of fiducial point node names
        nodes = ["ASIS_R", "PT_L", "PT_R"]

        # Check if each node exists in the scene
        nodes_exist = [
            node
            for node in nodes
            if slicer.mrmlScene.GetFirstNodeByName(node) is not None
        ]

        # Toggle the visibility of each existing fiducial point node
        for node in nodes_exist:
            markups_node = slicer.util.getNode(node)
            markups_node.SetDisplayVisibility(not markups_node.GetDisplayVisibility())
            markups_node.SetLocked(markups_node.GetLocked())
    def create_layout(
        self,
        label_name,
        tooltip_text,
        transform=None,
        node_class="vtkMRMLMarkupsFiducialNode",
    ):
        label = Label(label_name, tooltip_text=tooltip_text)
        node_selector = self.create_node_selector(label_name, node_class)
        place_markup_button = self.create_place_markup_button(
            label_name, node_class, transform
        )
        jump_button = JumpButton(label_name)
        lock_button = LockButton(label_name)
   
        layout = HBox(
            label, place_markup_button, jump_button, lock_button, node_selector
        )
        slicer.app.connect(
            "mrmlSceneChanged(vtkMRMLScene*)",
            node_selector,
            "setMRMLScene(vtkMRMLScene*)",
        )
     
        return layout, node_selector

    def add_markup_node_with_name_and_class(
        self, name, node_class="vtkMRMLMarkupsFiducialNode", transform=None
    ):
        existing_node = slicer.mrmlScene.GetFirstNodeByName(name)
        if existing_node:
            slicer.mrmlScene.RemoveNode(existing_node)
        # Create a new markup node to store the point
        markup_node = slicer.mrmlScene.AddNewNodeByClass(node_class, name)

        # Create a markups place widget to allow the user to place a point
        MarkupPlace(markup_node=markup_node)

        if transform:
            self.transform_node(
                name,
                transform_name="World_to_PelvicCS",
                inverse_transform_name="World_to_PelvicCS_Inverse",
            )

class NodeSelector:
    """
    A class for creating various types of UI widgets.

    Attributes:
        None
    """
    def create_node_selector(self, viewName: str, node_type: str, call_back=None):
        """
        Creates a markup widget for selecting a fiducial node of a specified node type.

        Args:
            viewName (str): The name of the view.
            node_type (str): The type of the node to select.

        Returns:
            slicer.qSlicerSimpleMarkupsWidget: A markup widget that can be used to select a fiducial node.
        """
        node_selector = slicer.qSlicerSimpleMarkupsWidget()
        node_selector.setSizePolicy(qt.QSizePolicy.Preferred, qt.QSizePolicy.Fixed)
        node_selector.markupsSelectorComboBox().nodeTypes = [node_type]
        node_selector.objectName = viewName
        node_selector.toolTip = f"Select a fiducial to use as the {viewName} point."
        node_selector.setNodeBaseName(viewName)
        node_selector.defaultNodeColor = qt.QColor("#ff1472")
        node_selector.tableWidget().hide()
        node_selector.jumpToSliceEnabled = True
        node_selector.optionsVisible = False
        node_selector.markupsSelectorComboBox().noneEnabled = True
        node_selector.markupsPlaceWidget().setPlaceMultipleMarkups(slicer.qSlicerMarkupsPlaceWidget.ForcePlaceSingleMarkup)
        node_selector.markupsPlaceWidget().setButtonsVisible(False)
        node_selector.markupsPlaceWidget().placeButton().show()
        node_selector.setMRMLScene(slicer.mrmlScene)
        node_selector.setStyleSheet("""
            QFrame {
                border: 2px solid black;
                border-radius: 5px;
                color: #FFFFFF;
                font-family: Arial;
                padding: 4px;
                font-size: 16px;
                background-color: #493F5E;
            }

            # QFrame:hover {
            #     color: #323232;
            # }
            
        """)
        if call_back is not None:
            node_selector.connect("currentNodeChanged(vtkMRMLNode*)", call_back)
        return node_selector

class GroupBox(qt.QGroupBox):
    def __init__(self, title=None, layout=None) -> None:
        super().__init__()
        self.setTitle(title)
        self.setLayout(layout)
        self.setSizePolicy(qt.QSizePolicy.Preferred, qt.QSizePolicy.Fixed)
        self.setStyleSheet(self.set_style_sheet())

    @staticmethod
    def set_style_sheet():
        return """
            QGroupBox {
                border: 2px solid #4285f4;
                border-radius: 4px;
                margin-top: 12px;
                font-size: 16px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 6px;
                background-color:  #F7EDE2;
                color: #4285f4;
            }
        """

class Button(qt.QPushButton):
    def __init__(self, name:str = None, callback: Optional[callable] = None, is_checkable: bool = False, icon = None, enabled = True) -> qt.QPushButton:
        super().__init__()

        if name is not None:
            self.setText(name)

        self.setSizePolicy(qt.QSizePolicy.Preferred, qt.QSizePolicy.Fixed)

        if callback is not None:
            self.clicked.connect(callback)
            
            
        self.setCheckable(is_checkable)

        if icon is not None:
            self.setIcon(icon)
        
        if is_checkable:
            self.setStyleSheet(self.set_style_sheet())

        self.setEnabled(enabled)

    @staticmethod
    def set_style_sheet():
        return """
                QPushButton {
                    background-color: #3F51B5;
                    border: none;
                    color: white;
                    padding: 4px;
                    text-align: center;
                    text-decoration: none;
                    display: inline-block;
                    font-size: 12px;
                    cursor: pointer;
                    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
                    transition-duration: 0.3s;
                    border-style: outset;
                    border-width: 3px;
                    border-radius: 7px;
                    border-color: black;
                }
                QPushButton:hover {
                    background-color: #c83471;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
                }
             """

class VBox(qt.QVBoxLayout):
    """
        Creates a QHBoxLayout object and adds each widget to it.

        Args:
            *widgets: A variable-length argument list of QWidget objects.

        Returns:
            A QHBoxLayout object containing all the added widgets.

        Example:
            hbox = create_hbox(button1, button2, button3)
    """
    def __init__(self, *layouts: qt.QLayout) -> qt.QVBoxLayout:
        super().__init__()
        for layout in layouts:
            self.addLayout(layout)
          
class HBox(qt.QHBoxLayout):
    """
        Creates a QHBoxLayout object and adds each widget to it.

        Args:
            *widgets: A variable-length argument list of QWidget objects.

        Returns:
            A QHBoxLayout object containing all the added widgets.

        Example:
            hbox = create_hbox(button1, button2, button3)
    """
    def __init__(self, *widgets: qt.QWidget) -> qt.QHBoxLayout:
        s=[]
        super().__init__()
        for widget in widgets:
            self.addWidget(widget)
            

class LockButton(qt.QPushButton):
    def __init__(self, name) -> None:
        super().__init__()
        self.setIcon(Icons.unlocked_icon)
        self.connect("clicked()", lambda: self.on_lock_button(name))
        self.setCheckable(True) 

    def on_lock_button(self, name):
        try:
            self.toggle_state(name)
            self.change_icon(name)
           
        except slicer.util.MRMLNodeNotFoundException:
            self.setIcon(Icons.unlocked_icon)      

    def change_icon(self, name):
        node = slicer.util.getNode(name)
        if node and node.GetLocked():
            self.setIcon(Icons.locked_icon)
            self.setChecked(True)
        else:
             self.setIcon(Icons.unlocked_icon)
    
     
    @staticmethod
    def toggle_state(name: str) -> None:
        """
        This function toggles the locked status of a fiducial node with the given name. If the node is currently locked, it will
        be unlocked, and vice versa.

        Args:
            name(str): The name of the fiducial node to toggle the locked status for.
        
        Returns: 
            None
        """
        fiducial_node = slicer.util.getFirstNodeByName(name)
        fiducial_node.SetLocked( not fiducial_node.GetLocked())


class JumpLogic:
    @staticmethod
    def get_jump_callback(name):
        markup = slicer.util.getNode(name)
        slicer.modules.markups.logic().JumpSlicesToNthPointInMarkup(markup.GetID(), 0) 

        position = [0.0, 0.0, 0.0]
        markup.GetNthControlPointPositionWorld(0,position)

        # Center slice views and cameras on this position
        for sliceNode in slicer.util.getNodesByClass('vtkMRMLSliceNode'):
            sliceNode.JumpSliceByCentering(*position)
        for camera in slicer.util.getNodesByClass('vtkMRMLCameraNode'):
            camera.SetFocalPoint(position)    

class JumpButton(qt.QPushButton):
    def __init__(self, name) -> None:
        super().__init__()
        self.text = "Jump"
        self.connect("clicked()", lambda: JumpLogic.get_jump_callback(name))

class MarkupPlace:
    def __init__(self, markup_node) -> None:
        place_widget = slicer.qSlicerMarkupsPlaceWidget()
        place_widget.setMRMLScene(slicer.mrmlScene)
        place_widget.setCurrentNode(markup_node)
        place_widget.setPlaceModeEnabled(True)
        place_widget.setPlaceMultipleMarkups(slicer.qSlicerMarkupsPlaceWidget.ForcePlaceSingleMarkup)
        
        # Set up a signal to be triggered when the point is placed
        def on_point_placed():
            place_widget.disconnect("markupPlaced(vtkMRMLNode*)", on_point_placed)
            print("Markup point placed at:", markup_node.GetMarkupPointVector(0))
        
        place_widget.connect("markupPlaced(vtkMRMLNode*)", on_point_placed)

class Label(qt.QLabel):
    def __init__(self, text, size_policy=None, tooltip_text=None) -> None:
        super().__init__()
        self.setText(text)
        if tooltip_text is not None:
            self.setToolTip(tooltip_text)
        self.setStyleSheet(self.set_style_sheet())

        if size_policy is not None:
            self.setSizePolicy(size_policy)
        else:
            self.setFixedSize(90, 25)
        
        self.setAlignment(qt.Qt.AlignHCenter | qt.Qt.AlignVCenter)

    @staticmethod
    def set_style_sheet():
        return """
            QLabel { 
                background-color: #4285f4;
                color: #ffffff;
                border-radius: 4px;
                font-size: 12px;
                padding: 4px;
                text-align: center;
            }
        """

class Icons:
    unlocked_icon = qt.QIcon(
        os.path.join(os.path.dirname(__file__), "Widget", "Icons", "unlock.svg")
    )
    locked_icon = qt.QIcon(
        os.path.join(os.path.dirname(__file__), "Widget", "Icons", "lock.svg")
    )
    danger_icon = qt.QIcon(
        os.path.join(os.path.dirname(__file__), "Icons", "danger.svg")
    )
    eye_off_icon = qt.QIcon(
        os.path.join(os.path.dirname(__file__), "Widget", "Icons", "eye-off.svg")
    )
    eye_on_icon = qt.QIcon(
        os.path.join(os.path.dirname(__file__), "Widget", "Icons", "eye-open.svg")
    )