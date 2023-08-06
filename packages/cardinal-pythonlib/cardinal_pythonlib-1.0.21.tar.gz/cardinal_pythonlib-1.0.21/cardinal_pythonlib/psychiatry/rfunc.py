#!/usr/bin/env python
# cardinal_pythonlib/psychiatry/rfunc.py

"""
===============================================================================

    Copyright (C) 2009-2018 Rudolf Cardinal (rudolf@pobox.com).

    This file is part of cardinal_pythonlib.

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

===============================================================================

WORK IN PROGRESS. Doesn't do much that's useful at present.

Functions to be used from R via reticulate
(https://cran.r-project.org/web/packages/reticulate/index.html).

See drugs.py for notes on how to get reticulate talking to this library.

Briefly:

.. code-block:: r

    # -------------------------------------------------------------------------
    # Load libraries
    # -------------------------------------------------------------------------

    library(data.table)
    library(reticulate)

    # -------------------------------------------------------------------------
    # Import module via reticulate
    # -------------------------------------------------------------------------

    VENV <- "~/dev/venvs/cardinal_pythonlib"
    PYTHON_VERSION <- "python3.5"
    CARDINAL_PYTHONLIB_BASEDIR <- ifelse(
        .Platform$OS.type == "windows",
        file.path(VENV, "lib", "site-packages/cardinal_pythonlib"),
        file.path(VENV, "lib", PYTHON_VERSION, "site-packages/cardinal_pythonlib")
    )
    reticulate::use_virtualenv(VENV, required=TRUE)

    # cpl_rfunc <- reticulate::import_from_path("rfunc", file.path(CARDINAL_PYTHONLIB_BASEDIR, "psychiatry"))

    # Or, for development:
    cpl_rfunc <- reticulate::import_from_path("rfunc", "~/Documents/code/cardinal_pythonlib/cardinal_pythonlib/psychiatry")

"""  # noqa

from typing import Any, Dict, Tuple

from pandas import DataFrame


# =============================================================================
# Simple information for R
# =============================================================================

def get_python_repr(x: Any) -> str:
    """
    A few notes:
    
    **data.table()**
    
    Data tables are converted to a Python dictionary:
    
    .. code-block:: r

        dt <- data.table(
            subject = c("Alice", "Bob", "Charles", "Dawn", "Egbert", "Flora"),
            drug = c("citalopram", "Cipramil", "Prozac", "fluoxetine",
                     "Priadel", "Haldol")
        )
        dt_repr <- cpl_rfunc$get_python_repr(dt)

    gives

    .. code-block:: none

        [1] "{'drug': ['citalopram', 'Cipramil', 'Prozac', 'fluoxetine',
        'Priadel', 'Haldol'], 'subject': ['Alice', 'Bob', 'Charles', 'Dawn',
        'Egbert', 'Flora']}"
    """
    return repr(x)


def get_python_repr_of_type(x: Any) -> str:
    """
    See get_python_repr.

    .. code-block:: r

        dt_type_repr <- cpl_rfunc$get_python_repr_of_type(dt)

    gives

    .. code-block:: none

        [1] "<class 'dict'>"
    """
    return repr(type(x))


def test_get_dict() -> Dict[str, Any]:
    """
    Test with:

    .. code-block:: r

        testdict <- cpl_rfunc$test_get_dict()

    This gives a list:

    .. code-block:: none

        > testdict
        $strings
        [1] "one"   "two"   "three" "four"  "five"

        $integers
        [1] 1 2 3 4 5

        $floats
        [1] 1.1 2.1 3.1 4.1 5.1

    """
    return {
        'integers': [1, 2, 3, 4, 5],
        'floats': [1.1, 2.1, 3.1, 4.1, 5.1],
        'strings': ["one", "two", "three", "four", "five"],
    }


def test_get_repr_of_data_frame(df: DataFrame) -> Tuple[str, str, str]:
    """
    Following on:

    .. code-block:: r

        dataframe <- as.data.frame(dt)
        cpl_rfunc$test_get_repr_of_data_frame(dataframe)
    """
    df2 = DataFrame(df)
    return repr(df2), repr(type(df2)), repr(type(df))
