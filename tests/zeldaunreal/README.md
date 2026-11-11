# ZeldaUnreal TCP transport smoke (ROM-free)

A compact test for the **real** `runner/cyc/cyc_tcp.c` server. The C harness
registers a mock `zelda_bridge_probe` command and runs the TCP poll loop.
The Python test connects to loopback and verifies JSON request IDs,
room arguments, explicit errors, unknown commands and `help`.

This test **does not build Zelda**, use any ROM, or prove that the Zelda-fork
extension exports authentic world geometry. That end-to-end step requires
a locally supplied original game ROM and a Windows installation capable of
building NESRecomp. The game-specific extension is developed separately in
`danielsfroste-a11y/LegendOfZeldaNESRecomp`.

Test locally (Linux):

```sh
cc -std=c11 -O2 -Wall -Wextra -I runner/cyc \
  tests/zeldaunreal/cyc_tcp_bridge_probe.c runner/cyc/cyc_tcp.c \
  -o /tmp/zeldaunreal_tcp_probe
python3 tests/zeldaunreal/check_tcp_transport.py /tmp/zeldaunreal_tcp_probe
```
