#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.


class Model:

    def __init__(self, filename=None):
        self.filename = filename


    def __bool__(self):
        return self.filename is not None
