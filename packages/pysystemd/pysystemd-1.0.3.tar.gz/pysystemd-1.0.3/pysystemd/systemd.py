import subprocess
import os

class status():
  """ check the status of a service on your system."""
  def __init__(self, service):
    self.service=service
  def is_run(self):
    """ if the service running return 0. """
    run=subprocess.check_output("systemctl | grep running", shell=True)
    str_run=str(run)
    test=str_run.find(self.service)
    if(test==-1):
      return 1
    else:
      return 0
  def is_enable(self):
    """ if the service enabled return 0. """

    run=subprocess.check_output("systemctl | grep enabled", shell=True)
    str_run=str(run)
    test=str_run.find(self.service)
    if(test==-1):
      return 1
    else:
      return 0
class services():
  """manage the services like running and stop and reboot."""
  def __init__(self, service):
    self.service=service
  def start(self):
    """ start a service, return 0 if Succeed."""
    start="systemctl start "+self.service
    run=subprocess.check_output(start, shell=True)
    test_run=status(self.service)
    return test_run.is_run()
  def stop(self):
    """ sstop a service, return 0 if Succeed."""
    stop="systemctl stop "+self.service
    run=subprocess.check_output(stop, shell=True)
    test_run = status(self.service)
    test_run.is_run()
    if(test_run==0):
      return 1
    else:
      return 0

  def restart(self):
    """ restart a service, return 0."""
    restart="systemctl restart "+self.service
    run=subprocess.check_output(restart, shell=True)
    return 0

  def reload(self):
    """ relode a service, return 0"""
    reload="systemctl reload "+self.service
    run=subprocess.check_output(reload, shell=True)
    return 0

  def enable(self):
    """ enable service, return 0 if Succeed."""

    enable="systemctl enable "+self.service
    run=subprocess.check_output(enable, shell=True)
    test_run=status(self.service)
    return test_run.is_enable()
  def disable(self):
    """ disable service, return 0 if Succeed."""

    disable="systemctl disable "+self.service
    run=subprocess.check_output(disable, shell=True)
    test_run = status(self.service)
    test_run.is_enable()
    if(test_run==0):
      return 1
    else:
      return 0

class list_services():
  """ list the services. """
  def list_all(self):
    """ list all services. """
    tru_list=[]
    x_list=os.listdir("/etc/systemd/system")
    y_list=os.listdir("/lib/systemd/system")
    all=x_list+y_list
    for i in all:
      if(".service" in i):
        tru_list.append(i)
    return tru_list
  def list_running(self):
    """ list all running services. """
    list=[]
    run_list=self.list_all()
    for x in run_list:
      run=status(x)
      test=run.is_run()

      if(test==0):
        list.append(x)
    return list
  def list_dont_running(self):
    """ list all not running services. """
    list=[]
    run_list=self.list_all()
    for x in run_list:
      run=status(x)
      test=run.is_run()

      if(test==1):
        list.append(x)
    return list
  def list_enable(self):
    """ list all enabled services. """
    list=[]
    run_list=self.list_all()
    for x in run_list:
      run=status(x)
      test=run.is_enable()

      if(test==0):
        list.append(x)
    return list
  def list_disable(self):
    """list all disabled services. """
    list=[]
    run_list=self.list_all()
    run=status()
    for x in run_list:
      run=status(x)
      test=run.is_enable()

      if(test==1):
        list.append(x)
    return list
class power:
  """server power manager."""
  def poweroff(self):
    """poweroff the system."""

    run=subprocess.check_output("systemctl poweroff", shell=True)
  def reboot(self):
    "reboot the system."""
    run=subprocess.check_output("systemctl reboot", shell=True)
  def rescue(self):
    """boot to rescue mode."""
    run=subprocess.check_output("systemctl rescue", shell=True)
  def suspend(self):
    """suspend the system."""
    run=subprocess.check_output("systemctl suspend", shell=True)
