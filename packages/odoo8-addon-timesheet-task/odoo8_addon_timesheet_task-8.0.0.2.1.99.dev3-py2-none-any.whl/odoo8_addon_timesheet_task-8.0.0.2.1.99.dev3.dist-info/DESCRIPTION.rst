Replace task work items (project.task.work) linked to task with
timesheet lines (hr.analytic.timesheet).

Unless the module project_timesheet, it allows to have only one single
object that handles and records time spent by employees, making more
coherence for the end user. This way, time entered through timesheet
lines or tasks is the same. As long as a timesheet lines has an
associated task, it will compute the related indicators.

Used with the module hr_timesheet_task, it also allows users to complete
task information through the timesheet sheet (hr.timesheet.sheet).


