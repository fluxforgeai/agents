#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from flux_forge_prototype_coder.crew import Coder

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

assignment = "Write a Python function that calculates the first 10 000 terms of this \
    series, multiplying the total by 4: 1 - 1/3 + 1/5 -1/7 + ... "

def run():
    """ Run the Coder Crew """
    inputs = {'assignment': assignment}
    coder = Coder()
    result = coder.crew().kickoff(inputs=inputs)
    print(result.raw)