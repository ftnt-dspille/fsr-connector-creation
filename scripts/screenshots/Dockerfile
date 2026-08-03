# Screenshot host: code-server plus a real Python interpreter.
#
# Python matters: without an interpreter on PATH the connector tree renders a
# "Python not found -- click to fix" advisory row, which would appear in every
# captured frame. Baking it into an image keeps the apt install out of the
# per-run path (it is the slowest step by a wide margin).
FROM codercom/code-server:latest

USER root
RUN apt-get update -qq \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        python3 python3-venv \
    && rm -rf /var/lib/apt/lists/*
USER coder
