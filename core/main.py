import sys
from inquisitor_obj import *
from ainsi import *

def safe_exit(inquisitor):
	threading_end_event.set()
	print(f"\n{erase_lines(2)}", end="\n")
	for thread in threading.enumerate():
		print(thread.name)
		if thread is not threading.main_thread():
			thread.join(timeout=2)
		log_warning(f"Thread {colored(thread.name, RED)} terminate.")
	log_exit("ARP monitor stopped.\n")
	sys.exit(0)

def main():
	if len(sys.argv) != 5:
		sys.exit(1)

	try:
		
		inquisitor = Inquisitor(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
		while not threading_end_event.is_set():
			threading_end_event.wait(1)
			
	except KeyboardInterrupt:
		safe_exit(inquisitor)
	except Exception as e:
		log_error(f"Fail in main loop :\t{e}")
	log_exit("Stoping ARP monitor...")
	return 0

if __name__ == "__main__":
    log_info("Starting ARP monitor...\n\n\n\n\n\n")	
    main()
