import sys
import composer
from io import StringIO
import os

print(str(sys.argv))
for path in sys.argv[1:]:
    print(path)
    with open(path, 'r') as file:
        network = []
        log = StringIO()
        print("Processing case "+path)
        composer.create(file, log, network)
        with open(path+".log",'w') as out:
            a = log.getvalue()
            a = a.replace("</br>","\n\r")
            a = a.splitlines()
            for line in a:
                if line.startswith("Perf:"):
                    out.write(line+"\n")

    print("Cleaning up...")
    os.system("for a in `docker ps -aq`; do docker kill $a; docker rm $a; done; docker network prune -f")