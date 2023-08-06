import os, sys, time
import threading as mt

def log(message):
    print "%d %s" % (os.getpid(), message)

def child(term):
    while not term.is_set():
        log('child %s' % os.getpid())
        time.sleep(1)

if __name__ == "__main__":
    term = mt.Event()
    log("is parent")
    t = mt.Thread(target=child, args=[term])
    t.start()
    # t.join() # OPTION 1
    
    time.sleep(2)

    childPID = os.fork()
    if childPID == 0:
        log("is child")

    log("threads: %s" % mt.enumerate())

    if childPID == 0:
        # child exits
        log('child exit')
        sys.exit(0)
        #os._exit(0) # OPTION 2
        pass

    else:
        term.set()
        t.join()
        #os.kill(childPID, 15) # OPTION 3
        log("parent done waiting for %s, now waiting for %d" %
             (t.getName(), childPID))
        os.waitpid(childPID, 0)
        log("parent exit")
        
