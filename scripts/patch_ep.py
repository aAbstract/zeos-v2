main_fd=open('main.py', 'w');switch_fd=open('switch.py', 'r');main_fd.write(switch_fd.read());main_fd.close()
