# MATLAB R2026a + JupyterLab (jupyter-matlab-proxy) + Dynare 7.1 (MATLAB MEX)
# Target: registry.cn-hangzhou.aliyuncs.com/dslab/matlab-jupyter-dynare:7.1-r2026a
#
# Runtime contract:
#   - JupyterLab on 8888; auth is provided at run time (JUPYTER_TOKEN env or
#     --IdentityProvider.token=... appended as container args) — nothing baked in
#   - MATLAB license at run time only:  -e MLM_LICENSE_FILE=27000@<license-server>
#   - Notebooks/mod files: mount at /home/matlab/work ; recommend --shm-size=1g
#
# Adapted from the official Dynare Dockerfile (git.dynare.org scripts/docker,
# 6.x meson path -> 7.1) and mathworks-ref-arch/matlab-integration-for-jupyter.
# Octave + TeXLive dropped.

ARG MATLAB_RELEASE=R2026a

FROM mathworks/matlab:${MATLAB_RELEASE}

ARG MATLAB_RELEASE
ARG DYNARE_VERSION=7.1
ARG MATLAB_INSTALL_LOCATION=/opt/matlab/${MATLAB_RELEASE}
# Same toolbox list the official dynare/dynare images install via mpm
ARG MATLAB_PRODUCT_LIST="Symbolic_Math_Toolbox Statistics_and_Machine_Learning_Toolbox Optimization_Toolbox Econometrics_Toolbox Parallel_Computing_Toolbox Control_System_Toolbox Global_Optimization_Toolbox"

USER root
ENV DEBIAN_FRONTEND=noninteractive

# ---- 1. mpm: add the toolboxes Dynare needs on top of base MATLAB ----
RUN apt-get update \
    && apt-get install --no-install-recommends --yes wget unzip ca-certificates \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN wget -q https://www.mathworks.com/mpm/glnxa64/mpm \
    && chmod +x mpm \
    && ./mpm install \
         --release=${MATLAB_RELEASE} \
         --destination=${MATLAB_INSTALL_LOCATION} \
         --products ${MATLAB_PRODUCT_LIST} \
    || (echo "MPM install failed:" && cat /tmp/mathworks_root.log && false) \
    && rm -f mpm /tmp/mathworks_root.log

# ---- 2. Build + runtime deps for Dynare (Ubuntu 24.04: meson 1.3.2 >= required 1.3.0) ----
RUN apt-get update \
    && apt-get install --no-install-recommends --yes \
       gcc g++ gfortran meson pkgconf \
       libboost-graph-dev libgsl-dev libmatio-dev \
       libslicot-dev libslicot-pic libsuitesparse-dev \
       flex libfl-dev bison \
       git git-lfs \
       python3 python3-venv python3-pip \
       xvfb \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# x13as (X-13ARIMA-SEATS) — optional feature, tolerate absence
RUN apt-get update \
    && (apt-get install --no-install-recommends --yes x13as \
        || echo "WARN: x13as not packaged here; Dynare X-13 features disabled") \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ---- 3. Hide MATLAB's bundled GCC runtime libs (matlab-support trick, per official Dynare Dockerfile) ----
RUN for f in sys/os/glnxa64/libgcc_s.so.1 \
             sys/os/glnxa64/libstdc++.so.6 \
             sys/os/glnxa64/libgfortran.so.5 \
             sys/os/glnxa64/libquadmath.so.0 \
             bin/glnxa64/libfreetype.so.6 \
             bin/glnxa64/libtiff.so.5; do \
        if [ -f "${MATLAB_INSTALL_LOCATION}/$f" ]; then \
            mv "${MATLAB_INSTALL_LOCATION}/$f" "${MATLAB_INSTALL_LOCATION}/$f.bak"; \
        fi; \
    done

# ---- 4. Clone + compile Dynare against MATLAB (no license needed at build time) ----
USER matlab
WORKDIR /home/matlab
RUN git lfs install \
    && git clone --depth 1 --branch ${DYNARE_VERSION} --recurse-submodules \
         https://git.dynare.org/dynare/dynare.git

# Build dir MUST be exactly <srctree>/build-matlab: Dynare auto-locates the
# preprocessor + MEX files there (7.1 README); do NOT delete it afterwards.
RUN cd dynare \
    && meson setup -Dmatlab_path=${MATLAB_INSTALL_LOCATION} -Dbuildtype=debugoptimized build-matlab \
    && meson compile -C build-matlab

# ---- 5. Put dynare on the MATLAB path for every session (incl. the Jupyter kernel) ----
# startup.m in newer mathworks/matlab images is a function ending in "end":
# insert addpath before the last line (verbatim logic from the official Dockerfile).
USER root
RUN filename="/home/matlab/Documents/MATLAB/startup.m" \
    && mkdir -p /home/matlab/Documents/MATLAB \
    && if [ -f "$filename" ]; then \
         tempfile=$(mktemp) && \
         total_lines=$(wc -l < "$filename") && \
         line_number=$((total_lines - 1)) && \
         head -n "$line_number" "$filename" > "$tempfile" && \
         echo "addpath('/home/matlab/dynare/matlab');" >> "$tempfile" && \
         tail -n 1 "$filename" >> "$tempfile" && \
         mv "$tempfile" "$filename"; \
       else \
         echo "addpath('/home/matlab/dynare/matlab');" >> "$filename"; \
       fi \
    && chown -R matlab:matlab /home/matlab/Documents

# ---- 6. JupyterLab + MATLAB kernel in a dedicated venv (Ubuntu 24.04 is PEP-668 managed) ----
RUN python3 -m venv /opt/jupyter \
    && /opt/jupyter/bin/pip install --no-cache-dir --upgrade pip \
    && /opt/jupyter/bin/pip install --no-cache-dir jupyterlab jupyter-matlab-proxy \
    && ln -sf /opt/jupyter/bin/jupyter /usr/local/bin/jupyter \
    && test -x /usr/local/bin/matlab

RUN mkdir -p /home/matlab/work && chown matlab:matlab /home/matlab/work

USER matlab
WORKDIR /home/matlab/work
ENV MW_CONTEXT_TAGS=MATLAB_PROXY:JUPYTER:V1
# MLM_LICENSE_FILE deliberately NOT set here — pass at docker run.

EXPOSE 8888
# Override the mathworks/matlab entrypoint (/bin/run.sh) with JupyterLab.
ENTRYPOINT ["/opt/jupyter/bin/jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser"]
