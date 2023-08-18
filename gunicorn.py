bind = "0.0.0.0:8000"

workers = 2
threads = 4
worker_class = "gthread"
timeout = 90

reload = True
reload_engine = "poll"

accesslog = "-"
errorlog = "-"

worker_tmp_dir = "/dev/shm"
