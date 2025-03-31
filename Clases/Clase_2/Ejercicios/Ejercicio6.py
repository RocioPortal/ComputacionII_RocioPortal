import os, time

pid = os.fork()
if pid > 0:
    print("[PADRE] Terminando")
    os._exit(0)
else:
    print("[HIJO] Ahora soy huérfano. Mi nuevo padre será init/systemd")
    time.sleep(10)
