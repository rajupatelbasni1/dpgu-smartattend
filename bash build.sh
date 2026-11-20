#!/usr/bin/env bash
# Exit on error
set -o errexit

# Upgrade pip
python3 -m pip install --upgrade pip

# 🔥 YEH SABSE ZAROORI LINE HAI 🔥
# Yeh dlib ko sirf 1 core use karne ko bolegi, jisse RAM 8GB cross nahi hogi
export CMAKE_BUILD_PARALLEL_LEVEL=1

# Install heavy dependencies separately without caching to save memory
pip3 install --no-cache-dir cmake wheel setuptools
pip3 install --no-cache-dir dlib

# Install rest of the requirements
pip3 install --no-cache-dir -r requirements.txt

# Run migrations (Optional but good practice)
python3 manage.py migrate