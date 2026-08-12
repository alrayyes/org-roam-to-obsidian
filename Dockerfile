# convert.py imports nothing outside the standard library, so there is nothing
# to compile and nothing to copy between stages. A single alpine stage is the
# whole image; a builder stage would only add a layer that produces no artefact.
FROM python:3.13-alpine@sha256:42825e7ec3437b3bce923c237484eb23d32128476e18307d2f48951bf86f1db2

# Read by the label below rather than hardcoded, so the release workflow stamps
# the tag it is building without this file changing every release.
ARG VERSION=dev

LABEL org.opencontainers.image.title="org-roam-to-obsidian" \
      org.opencontainers.image.description="Convert org-roam notes to Obsidian Markdown" \
      org.opencontainers.image.source="https://github.com/alrayyes/org-roam-to-obsidian" \
      org.opencontainers.image.licenses="GPL-3.0-or-later" \
      org.opencontainers.image.version="${VERSION}"

# The notes being converted are the user's own, and a container that writes them
# back as root leaves a directory they need sudo to delete.
RUN adduser -D -u 1000 convert
# Numeric, so the id resolves the same way whatever the host thinks of the name.
USER 1000

WORKDIR /work
COPY --chown=convert:convert convert.py /app/convert.py

# The mount points live in the ENTRYPOINT, not in CMD. Anything the user passes
# to `docker run` replaces CMD outright, so with the defaults there a single
# `-p filetags` would silently drop --input and --output and convert nothing.
# In the ENTRYPOINT they are always present and user arguments append; argparse
# takes the last occurrence, so -i and -o still override them.
ENTRYPOINT ["python", "/app/convert.py", "--input", "/input", "--output", "/output"]
