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
## Digest sha256:52b32769... resolved from the 'latest' tag via
## the registry manifest API (verification step, not trust source):
##   https://gcr.io/v2/oss-fuzz-base/base-builder-python/manifests/latest
##   (docker-content-digest header)
##
## :latest stays matched to clusterfuzzlite-run-fuzzers:v1's ABI
## (Ubuntu 20.04 / glibc 2.31) - OSS-Fuzz keeps this guarantee so
## binaries built in the base-builder land cleanly in the run
## container. Do not pin to the ubuntu-24-04 tag without also
## forking CFLite to override its hardcoded run image.
##
## Upstream tracking:
##   https://github.com/google/clusterfuzzlite/issues/145 - asks
##     for Ubuntu 20.04 -> 24.04 migration (open, June 2025; cites
##     Python 3.8 being too old for modern projects).
##   https://github.com/google/clusterfuzzlite/pull/146 - proposes
##     flipping the build + run actions to :ubuntu-24-04-v1 tags
##     (not merged; reviewer blocked on missing opt-in / backward-
##     compat path for existing users).
##
## When that work lands and OSS-Fuzz republishes :latest pointing
## at the new ABI, this pin can be refreshed in a single digest
## swap.
FROM gcr.io/oss-fuzz-base/base-builder-python@sha256:04d1a93ee11e221f464dde307b3003c6a5f4a9ac148f00ceff3006e777467107

COPY . $SRC/helper-scripts
COPY .clusterfuzzlite/build.sh $SRC/build.sh
WORKDIR $SRC/helper-scripts
