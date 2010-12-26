import sys
import os
import logging

import PyQt4.QtGui as QtGui
import PyQt4.QtCore as QtCore
import PyQt4.uic as uic

import drQtLib as drQtLib
import drqueue.base.libdrqueue as drqueue


logging.basicConfig()
log = logging.getLogger("drQt")
log.setLevel(logging.DEBUG)

current_path = os.path.dirname(__file__)
icons_path = os.path.join(current_path,"ui","icons")

ui_path=os.path.join(current_path,"ui","drQt.ui")
widget_class, base_class = uic.loadUiType(ui_path)


class drQt(widget_class, base_class):
    
    node_properties=["Id","Enabled","Running","Name","Os","CPUs","Load Avg","Pools"]
    job_properties=["Id","Name","Owner","Status","Process","Left","Done","Priority","Pool"]
    
    def __init__(self,*args,**kwargs):
        super(drQt,self).__init__(*args,**kwargs)
        
        try:
            drqueue.request_job_list(drqueue.CLIENT)
        except:
            raise "NO MASTER FOUND"
        
        self.setupUi(self)
        self._timer_=drQtLib.Timer(parent=self)
        self.timer_interrupt=0
        self.jobs_tab_list=[]
        self.nodes_tab_list=[]
        self._selected_job_row= None
        
        self.setup_main()
        self.PB_refresh.clicked.connect(self.refresh)
        self.CB_auto_refresh.stateChanged.connect(self.set_autorefresh)
        self.connect(self._timer_,QtCore.SIGNAL("time_elapsed"),self.refresh)
        
        self.SB_refresh_time.setMinimum(1)
        self.SB_refresh_time.setValue(2)

        self.setWindowFlags(QtCore.Qt.Window |
                            QtCore.Qt.WindowMinimizeButtonHint | 
                            QtCore.Qt.WindowCloseButtonHint | 
                            QtCore.Qt.WindowMaximizeButtonHint)        
        
        self.connect(self.TW_job,QtCore.SIGNAL("cellClicked(int,int)"),self._store_selected_job)
        
        
    def _store_selected_job(self,row,column):
        self._selected_job_row = row
        
    def setup_main(self):
        self.setWindowTitle("DrQueue Manager")
        self.set_main_icons()
        self.setup_about()
        self.setup_jobs()
        self.init_jobs_tabs()
        
        self.setup_nodes()
        self.init_nodes_tabs()
        
    def setup_nodes(self):
        self.TW_node.clear()
        
        self.TW_node.setColumnCount(len(self.node_properties))
        self.TW_node.setHorizontalHeaderLabels(self.node_properties) 
        
        self.TW_node.verticalHeader().hide()
        self.TW_node.setAlternatingRowColors(True)
        self.TW_node.setSelectionBehavior(QtGui.QTableView.SelectRows)
        self.TW_node.setSelectionMode(QtGui.QTableView.SingleSelection) 
                               
    def setup_jobs(self):
        #add a couple of jobs
        self.TW_job.clear()

        self.TW_job.setColumnCount(len(self.job_properties))
        self.TW_job.setHorizontalHeaderLabels(self.job_properties) 

        self.TW_job.verticalHeader().hide()
        self.TW_job.setAlternatingRowColors(True)
        self.TW_job.setSelectionBehavior(QtGui.QTableView.SelectRows)
        self.TW_job.setSelectionMode(QtGui.QTableView.SingleSelection)

        
    def refresh(self):
        self.setCursor(QtCore.Qt.WaitCursor);
        self.init_jobs_tabs()
        self.init_nodes_tabs()
        self.TW_job.repaint()
        self.TW_node.repaint()
        self.TW_job.setCurrentCell(self._selected_job_row,0)
        self.setCursor(QtCore.Qt.ArrowCursor);
        
    def set_autorefresh(self,status):
        if status:
            log.debug("autorefresh:ON")
            refresh_time=self.SB_refresh_time.value()
            self._timer_.set_run_time(refresh_time)
            self._timer_.start()
        else:
            log.debug("autorefresh:OFF")
            self._timer_.terminate()

    def init_jobs_tabs(self):
        self.jobs_tab_list=[]
        log.debug("building job tabs...")
        self.TW_job.clearContents()
        jobs=self._get_all_jobs()
        num_jobs = len(jobs)
        self.TW_job.setRowCount(num_jobs)        

        for i in range(num_jobs):
            job_tab = drQtLib.JobTab(jobs[i],parent=self.TW_job)
            job_tab.add_to_table(self.TW_job, i)
            self.jobs_tab_list.append(job_tab)
        
    def init_nodes_tabs(self):
        self.nodes_tab_list=[]
        log.debug("building nodes tabs...")
        nodes=self._get_all_nodes()
        num_nodes = len(nodes)
        self.TW_node.setRowCount(num_nodes)
        for i in range(num_nodes):
            node_tab = drQtLib.NodeTab(nodes[i],parent=self.TW_node)
            node_tab.add_to_table(self.TW_node, i)
            self.nodes_tab_list.append(node_tab)
                      
    def setup_about(self):
        url=QtCore.QUrl("ui/about.html")
        self.WV_about.load(url)
        
    def set_main_icons(self):
        self.setWindowIcon(QtGui.QIcon(os.path.join(icons_path,"main.svg")))
        self.TW_main.setTabIcon(0,QtGui.QIcon(os.path.join(icons_path,"job.svg")))
        self.TW_main.setTabIcon(1,QtGui.QIcon(os.path.join(icons_path,"nodes.svg")))        
        self.TW_main.setTabIcon(2,QtGui.QIcon(os.path.join(icons_path,"about.svg")))        
    
        
    def _get_all_jobs(self):
        job_list = drqueue.request_job_list(drqueue.CLIENT)
        return job_list
    
    def _get_all_nodes(self):
        computer_list = drqueue.request_computer_list (drqueue.CLIENT)
        return computer_list
        
def main():
    app = QtGui.QApplication(sys.argv)
    dialog = drQt()    
    dialog.show()
    return app.exec_()

if __name__ == "__main__":
    main()
