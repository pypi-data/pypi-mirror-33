#!/bin/bash

################################################################################
# Instance Preparation
# For Google cloud, Stackdriver/logging should have Write, 
#                   Google Storage should have Full
#                   All other APIs None,
#
#
# Copyright (C) 2018 The Board of Trustees of the Leland Stanford Junior
# University.
# Copyright (C) 2018 Vanessa Sochat.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
# License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
################################################################################

echo "Step 1: Installing Git Dependency"
sudo yum update && yum install -y git curl

## NOTE: TOOD: This will be updated when apt version is tested and finished.

################################################################################
# Google Metadata
#
# Maintain build routine in builders repository, so minimal changes needed to
# sregistry client.

echo "Step 2: Preparing Metadata"

# Installation of Singularity, and custom build routines maintained separately
# to maximize community involvement & minimize needing change sregistry client

METADATA="http://metadata/computeMetadata/v1/instance/attributes"
BUILDER_KILLHOURS=$(curl ${METADATA}/BUILDER_KILLHOURS -H "Metadata-Flavor: Google")

REPO=$(curl ${METADATA}/repo -H "Metadata-Flavor: Google")
BRANCH=$(curl ${METADATA}/branch -H "Metadata-Flavor: Google")
RUNSCRIPT=$(curl ${METADATA}/runscript -H "Metadata-Flavor: Google")
COMMIT=$(curl ${METADATA}/commit -H "Metadata-Flavor: Google")
FOLDER=$(basename $REPO)

# Commit

echo "Step 3: Cloning Repository"
git clone -b "${BRANCH}" "${REPO}" && cd "${FOLDER}"


if [ -x "${COMMIT}" ]; then
    git checkout $COMMIT .
else
    COMMIT=$(git log -n 1 --pretty=format:"%H")
fi

echo "Using commit ${COMMIT}"

# Run build

if [ -f "${RUNSCRIPT}" ]; then
    echo "Building ${RUNSCRIPT}... here we go!"
    exec "${RUNSCRIPT}"
else
    echo "Cannot find ${RUNSCRIPT}"
    ls
fi
