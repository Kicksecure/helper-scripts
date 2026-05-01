## Copyright (C) 2026 - 2026 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## AI-Assisted

## ClusterFuzzLite Python Dockerfile.
## https://google.github.io/clusterfuzzlite/build-integration/python-lang/

## Image: gcr.io/oss-fuzz-base/base-builder-python.
##
## Trust root - this image path is the canonical Python base for
## OSS-Fuzz / ClusterFuzzLite, published by Google's OSS-Fuzz
## project. The Dockerfile that produces this image lives in the
## OSS-Fuzz repo; the language-specific guide tells integrators to
## use this exact path:
##   https://github.com/google/oss-fuzz/tree/master/infra/base-images/base-builder-python
##   https://google.github.io/oss-fuzz/getting-started/new-project-guide/python-lang/
##
## Digest sha256:92b94004... resolved from the 'latest' tag via
## the registry manifest API (verification step, not trust source):
##   https://gcr.io/v2/oss-fuzz-base/base-builder-python/manifests/latest
##   (docker-content-digest header)
FROM gcr.io/oss-fuzz-base/base-builder-python@sha256:92b940040eaa039d39de69ea44254cb7943c5d729a7f8094a87bedb318f5cec3

COPY . $SRC/helper-scripts
COPY .clusterfuzzlite/build.sh $SRC/build.sh
WORKDIR $SRC/helper-scripts
