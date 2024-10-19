#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 19 14:15:52 2024

@author: krishnayadav
"""

import logging

class SuppressLogging:
    def __enter__(self):
        logging.disable(logging.CRITICAL)  # Disable all logging above CRITICAL level

    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.disable(logging.NOTSET)  # Re-enable logging