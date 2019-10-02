#include <signal.h>
#include "core/SimpleLogger.h"
#include "forwarder/miniforwarder.h"

void signal_handler(int signum) { 
    LOG_CRT << "Received CTRL-C";
    exit(-1);
}

int main() { 
    signal(SIGINT, signal_handler);
    miniforwarder fwd("ForwarderCfg.yaml", "Forwarder");
    fwd.run();
    return 0;
}
