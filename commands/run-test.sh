#!/bin/sh
set -e

coverage run -m pytest

coverage html