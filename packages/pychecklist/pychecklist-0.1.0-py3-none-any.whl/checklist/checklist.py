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

import pickle

from checklist.task import Task

PICKLE_VERS = 4


class ChecklistException(Exception):
     def __init__(self, *args, **kwargs):
         Exception.__init__(self, *args, **kwargs)


class TaskExistsException(ChecklistException):
     def __init__(self, *args, **kwargs):
         ChecklistException.__init__(self, *args, **kwargs)


class ParentNotExistsException(ChecklistException):
     def __init__(self, *args, **kwargs):
         ChecklistException.__init__(self, *args, **kwargs)


class Checklist:

    def __init__(self, pickle_path=None):
        if pickle_path:
            self.idmap = {}
            self.load(pickle_path)
        else:
            self.tasks = []
            self.completed_tasks = []
            self.idmap = {}

    def load(self, pickle_path):
        with open(pickle_path, 'rb') as pkl_file:
            self.tasks, self.completed_tasks = pickle.load(pkl_file)
        for task in self.tasks:
            self.idmap[task.name] = task
        for task in self.completed_tasks:
            self.idmap[task.name] = task


    def save(self, pickle_path):
        with open(pickle_path, 'wb') as pkl_file:
            pickle.dump((self.tasks, self.completed_tasks), pkl_file, protocol=PICKLE_VERS)

    def newTask(self, name, description=None, parent=None):
        if name in self.idmap:
            raise TaskExistsException('Task "{}" already exists'.format(name))
        if parent and (parent not in self.idmap):
            raise ParentNotExistsException('Parent "{}" does not exist'.format(parent))
        new_task = Task(name=name, description=description, parent=parent)
        if parent:
            self.idmap[parent].addChild(new_task.name)
        self.tasks.append(new_task)
        self.idmap[new_task.name] = new_task

    def completeTask(self, name):
        task = self.idmap[name]
        task.complete()
        if self._childrenCompleted(task.name) and task.parent == None:
            self.tasks.remove(task)
            self.completed_tasks.append(task)

    def uncompleteTask(self, name):
        task = self.idmap[name]
        task.uncomplete()

    def getTask(self, name):
        return self.idmap[name]

    def _childrenCompleted(self, name):
        for child in self.idmap[name].children:
            if not self.idmap[child].completed:
                return False
            if not self._childrenCompleted(child):
                return False
        return True
