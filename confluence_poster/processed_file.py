"""Processed File

ProcessedFile is a wrapper containing the title and the content of each file as it has been processed by the system.
"""
import collections

ProcessedFile = collections.namedtuple('ProcessedFile', 'title content')
