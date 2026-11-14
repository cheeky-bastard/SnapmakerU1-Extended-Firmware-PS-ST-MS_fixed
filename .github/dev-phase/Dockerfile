FROM snapmaker-u1-dev:latest
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-cffi python3-numpy ca-certificates && rm -rf /var/lib/apt/lists/*
# Prepared with the checksum-verified official GNU Arm 10.3-2021.10 toolchain.
COPY --from=u1-stock-mcu:10.3-2021.10 /opt/gcc-arm /opt/gcc-arm
ENV MCU_CROSS_PREFIX=/opt/gcc-arm/bin/arm-none-eabi-
