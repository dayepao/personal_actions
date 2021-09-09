import subprocess
import chardet


ps = "write-output 'test1'; Start-Sleep -s 5; write-output 'test2'"

with subprocess.Popen(['powershell', ps], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW) as proc:
    # for line in proc.stdout.readlines():
    while (line := proc.stdout.readline()) != b'':
        print(line.decode(chardet.detect(line)["encoding"], "ignore").replace("\r\n", ""))
