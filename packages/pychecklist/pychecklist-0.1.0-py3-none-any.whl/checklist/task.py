#    Copyright (C) 2018 Dylan Stephano-Shachter
#
#    This file is part of Checklist.
#
#    Checklist is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Checklist is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Checklist.  If not, see <https://www.gnu.org/licenses/>.

import uuid


class Task:

    def __init__(self, name, description=None, parent=None):
        self.name = name
        self.description = description
        self.parent = parent
        self.children = []
        self.completed = False

    def addChild(self, child):
        self.children.append(child)

    def complete(self):
        self.completed = True

    def uncomplete(self):
        self.completed = False
