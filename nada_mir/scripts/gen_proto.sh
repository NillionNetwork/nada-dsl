#!/bin/bash
# Script to generate protocol buffer bindings for the Nada MIR. 
# This script needs to be run to update the protocol buffer definitions every time there's a change
# in `nada-mir-model`.
set -e

SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}" 2>/dev/null)" && pwd -P)"

# This is the path where nada-mir-model has been checked out in your workstation
NADA_MIR_MODEL_ROOT=${SCRIPT_PATH}/../../../nada-mir-model
GRPC_ROOT=${NADA_MIR_MODEL_ROOT}/proto

mir_files=(
  "nillion/nada/v1/mir.proto"
  "nillion/nada/v1/operations.proto"
  "nillion/nada/v1/types.proto"
)


OUTPUT_DIR=${SCRIPT_PATH}/../src/nada_mir_proto

mkdir -p ${OUTPUT_DIR}

cd ${SCRIPT_PATH}/../src

for file in "${mir_files[@]}"; do
  python -m grpc_tools.protoc -I${GRPC_ROOT} --python_betterproto_out=nada_mir_proto $file
done
