/* ROM-free check of the real cycle TCP transport.
 * Links directly with runner/cyc/cyc_tcp.c. Uses only loopback.
 */
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "cyc_tcp.h"

static void zelda_mock(int id, const char *request)
{
    long room = -1;
    if (!cyc_tcp_long(request, "room", &room) || room < 0 || room > 127) {
        cyc_tcp_err(id, "room must be between 0 and 127");
        return;
    }
    char fields[96];
    snprintf(fields, sizeof(fields), "\"room\":%ld,\"bridge\":\"ok\"", room);
    cyc_tcp_ok(id, fields);
}

int main(int argc, char **argv)
{
    if (argc != 2) return 2;
    const int port = atoi(argv[1]);
    if (port < 1024 || port > 65535) return 2;
    cyc_tcp_register("zelda_bridge_probe", "ROM-free room protocol test", zelda_mock);
    if (!cyc_tcp_start(port)) return 3;
    puts("READY");
    fflush(stdout);

    struct timespec delay = {0, 1000000}; /* 1 ms */
    for (int i = 0; i < 7000; ++i) {
        cyc_tcp_poll();
        nanosleep(&delay, NULL);
    }
    cyc_tcp_stop();
    return 0;
}
