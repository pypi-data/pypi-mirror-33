""" Todoist adapter """

import re
from datetime import datetime
import logging as log
import csv
import six

import todoist
from app.util import same_date


TO_UPDATE = {}


class Task():
    """A single task that has name and time stamps associated with it"""

    def __init__(self):
        self.id = 0
        self.name = ""
        self.pid = 0
        self.done = False
        self.ts_done = -1
        self.ts_added = -1
        self.meta_data = None

    def __repr__(self):
        name = self.name
        name = (name[:50] + '...') if len(name) > 50 else name
        if six.PY2:
            name = name.encode('utf-8')
        return "Task({})".format(name)


class Project():
    """A single project that has a name and prioroty associated with it"""

    def __init__(self):
        self.id = 0
        self.name = ""
        self.tasks = []
        self.priority = 0

    def __repr__(self):
        name = self.name
        name = (name[:50] + '...') if len(name) > 50 else name
        return "Project(\"" + name + "\")"


class Todoist():
    """
    An class wrapping around Todoist client. Provides multiple functionality
    to read/write/update Todoist
    """

    def __init__(self, email, password):
        """
        Initialize Todoist object. This function needs to be called once before
        use.
        :param email: login email
        :param password: login password

        """
        self.user = None
        self.completed_tasks = None
        self.planned_label = None
        self.planned_label_id = None
        self.already_planned = []

        self.api = todoist.TodoistAPI()
        self.user = self.api.user.login(email, password)
        err = self.user.get("error")
        if err:
            raise Exception(err)

        self.api.sync()
        self.planned_label = self.get_label("planned")
        if not self.planned_label:
            log.debug("Create new planned label")
            self.planned_label = self.api.labels.add("planned")
        self.planned_label_id = int(self.planned_label['id'])
        log.debug("planned_label_id: %d", self.planned_label_id)

    def get_token(self):
        """Get Todoist access token"""
        return self.user['token']

    def get_label(self, name):
        """
        Get an label object by name
        :param name: label name

        """
        self.labels = self.api.labels.all()
        for l in self.labels:
            if not isinstance(l['id'], int):
                # skip non-regular label object
                continue
            if l['name'] == name:
                return l
        return None

    def PyTaskAdapter(self, pytodoist_task):
        """

        :param pytodoist_task: 

        """
        t = Task()
        tt = pytodoist_task

        if isinstance(tt, todoist.models.Item):
            completed_date = tt.data.get("completed_date")
            checked = tt['checked']
        else:
            completed_date = tt.get("completed_date")
            checked = tt.get('checked')

        t.id = tt['id']
        t.name = tt['content']
        t.done = checked
        t.pid = tt['project_id']
        t._data = tt

        if completed_date is not None:
            t.ts_done = datetime.strptime(
                tt['completed_date'], "%a %d %b %Y %H:%M:%S +0000")
            t.done = True
        else:
            t.ts_added = datetime.strptime(
                tt['date_added'], "%a %d %b %Y %H:%M:%S +0000")

        return t

    def _get_ttasks(self):
        """ """
        self.ttasks = self.api.items.all()
        return self.ttasks

    def get_tasks(self):
        """ """
        ttasks = self._get_ttasks()
        tasks = []
        for tt in ttasks:
            tasks.append(self.PyTaskAdapter(tt))
        return tasks

    def get_projects(self):
        """Get all projects"""
        ttasks = self._get_ttasks()
        ttasks = sorted(ttasks, key=lambda x: x['item_order'])

        pmap = {}
        for tt in ttasks:
            already_planned = False
            if self.planned_label_id in tt['labels']:
                already_planned = True
            elif tt['date_string']:
                continue
            t = self.PyTaskAdapter(tt)
            # print(t)
            if already_planned:
                log.debug("Already planned: %-20s", t)
                self.already_planned.append(t)

            if pmap.get(tt['project_id']) is None:
                tp = self.api.projects.get_by_id(tt['project_id'])
                p = Project()
                p.id = tp['id']
                p.name = tp['name']
                p._data = tp

                m = re.match(r"(\d+)\-(.*)", p.name)
                if m:
                    p.name = m.group(2)
                    p.priority = int(m.group(1))
                p.tasks.append(t)
                pmap[tt['project_id']] = p
            else:
                p = pmap[tt['project_id']]
                p.tasks.append(t)

        projects = []
        for _, v in pmap.items():
            projects.append(v)

        log.debug("Number of projects: %d", len(projects))
        log.debug("Number of tasks: %d", len(ttasks))
        log.debug("Number of already planned tasks: %d",
                  len(self.already_planned))

        return projects

    def clean_up(self):
        """ """
        log.debug("Number of tasks to clear: %d", len(self.already_planned))
        for t in self.already_planned:
            tt = t._data
            tt.update(date_string="")
            log.debug("Clear date_string: %-20s", t)
            if self.planned_label_id in tt['labels']:
                labels = tt['labels'][:]
                labels.remove(self.planned_label_id)
                tt.update(labels=labels)
                log.debug("Clear label: %-20s", t)

    def update(self):
        """Commit updates to Todoist."""
        self.api.commit()

    def update_task(self, t, **kargs):
        """

        :param t: 
        :param **kargs: 

        """
        tt = t._data
        tt.update(**kargs)

    def update_project(self, project):
        """

        :param project: 

        """
        p = project
        i = 0
        if len(p.tasks) < 1:
            return
        for t in p.tasks:
            # Get pytodoist task
            tt = t._data
            tt.update(item_order=i)
            i += 1

    def update_projects(self, projects):
        """

        :param projects: 

        """
        for p in projects:
            self.update_project(p)

    def get_completed_tasks(self, since=None, until=None, max=100):
        """

        :param since:  (Default value = None)
        :param until:  (Default value = None)

        """
        # This is a premium only feature
        res = self.completed_tasks
        if not res:
            res = []
            if not self.user.get('is_premium'):
                self.completed_tasks = res
                return res

            offset = 0
            limit = 50
            while True:
                completed = self.api.completed.get_all(limit=limit, offset=offset)
                tasks = completed['items']
                log.debug("Get completed tasks: %d" % len(tasks))

                for t in tasks:
                    res.append(self.PyTaskAdapter(t))

                if len(tasks) < limit:
                    break
                if max is not None and len(res) >= max:
                    break
                offset += limit

            res = sorted(res, key=lambda x: x.ts_done, reverse=True)
            self.completed_tasks = res

        if since:
            res = [x for x in res if x.ts_done > since]
        if until:
            res = [x for x in res if x.ts_done < until]

        return res

    def num_tasks_completed_today(self, timezone):
        """

        :param timezone: 

        """
        now = datetime.utcnow()
        n = 0

        if not self.completed_tasks:
            self.get_completed_tasks()

        for item in self.completed_tasks:
            if same_date(now, item.ts_done, timezone):
                n = n + 1

        return n

    def mark_as_planned(self, task):
        """

        :param task: 

        """
        tt = task._data
        if len(tt['labels']) == 0:
            tt.update(labels=[self.planned_label_id])
        else:
            if self.planned_label_id not in tt['labels']:
                labels = tt['labels'][:]
                labels.append(self.planned_label_id)
                tt.update(labels=labels)

        if task in self.already_planned:
            self.already_planned.remove(task)

    def get_stats(self):
        """ """
        ttasks = self._get_ttasks()
        return "Total number of tasks: %d" % len(ttasks)

    def to_csv(self, fname="todoist.csv", include_completed=True):
        """
        Dump all tasks into a csvfile
        :param fname: name of the csv file to be written
        """
        with open(fname, "w") as csvfile:

            writer = csv.writer(csvfile)
            writer.writerow(["id", "name", "project id", "done",
                             "timestamp_done", "timestamp_added"])

            tasks = self.get_tasks()
            log.debug("Number of not completed tasks: %d" % len(tasks))
            for task in tasks:
                writer.writerow([task.id, task.name, task.pid, task.done,
                                 task.ts_done, task.ts_added])
            if include_completed:
                ctasks = self.get_completed_tasks(max=None)
                log.debug("Number of completed tasks: %d" % len(ctasks))
                for task in ctasks:
                    writer.writerow([task.id, task.name, task.pid, task.done,
                                     task.ts_done, task.ts_added])
