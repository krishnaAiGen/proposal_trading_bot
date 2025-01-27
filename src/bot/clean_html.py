#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 15:10:07 2025

@author: krishnayadav
"""

import re

def remove_html_tags(text):
    """
    Remove all HTML tags from the text and return clean paragraphs.
    """
    # Remove HTML tags using regex
    clean_text = re.sub(r'<[^>]+>', '', text)
    
    # Split the text into paragraphs based on double newlines
    paragraphs = [p.strip() for p in clean_text.split('\n\n') if p.strip()]
    
    return paragraphs

