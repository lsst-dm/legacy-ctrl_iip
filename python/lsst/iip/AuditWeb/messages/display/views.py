# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from .models import Machines
from django.http import HttpResponseRedirect

from influxdb import DataFrameClient
from .forms import table_query
import datetime
import calendar
# Create your views here.



def morning(request):
    context = {
    }
    return render(request, 'try_jquery.html', context)

def view_forwarders(request, forwarder_id):
    #m = get_object_or_404(Machines,forwarder_id = forwarder_id)
    pic_dict = {
        'IDLE': '"images/rvn.jpg"',
        'WORKING': '"images/glazed.jpg"',
        'BAD': '"images/felix.jpg"',
    }
    all_machines = Machines.objects.all()
    machine_chosen = []
    for machine in all_machines:
        if machine.forwarder_id == forwarder_id:
            machine_chosen.append(machine)
    machine_chosen.reverse()

    # forms
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = table_query(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            form.save()
            # redirect to a new URL:
            return HttpResponseRedirect('/display/time_query/')
    # if a GET (or any other method) we'll create a blank form
    else:
        form = table_query()

    context = {
        'forwarder_id': forwarder_id,
        'machine_chosen': machine_chosen,
        'form': form,
    }
    return render(request, 'forwarders.html', context)

def view_scoreboard(request):
    #m = get_object_or_404(Machines,forwarder_id = forwarder_id)
    influx_db = "estherdb"
    dict_job_state, column_name_job_state = get_query_result(
        query_message="select * from JOB_STATE", measurement_name="JOB_STATE", influx_db=influx_db)
    dict_ack, column_name_ack = get_query_result(
        query_message="select * from acks", measurement_name="acks", influx_db=influx_db)
    # forms
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = table_query(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            form.save()
            # redirect to a new URL:
            return HttpResponseRedirect('/display/time_query/')
    # if a GET (or any other method) we'll create a blank form
    else:
        form = table_query()

    context = {
        'column_name_job_state': column_name_job_state,
        'column_name_ack': column_name_ack,
        'dict_ack': dict_ack,
        'dict_job_state': dict_job_state,
        'form': form,
    }
    return render(request, 'tables_sidebar.html', context)


# helper function for the main tables
def get_query_result(query_message, measurement_name, influx_db):
    try:
        # get result as a dataframe
        client = DataFrameClient(host='141.142.211.122', port=8086, database=influx_db)

        # extract the result from dataframe
        query_result = client.query(query_message)[measurement_name]
    except KeyError:
        return False,False

    # make in to correct form
    column_name = list(query_result)
    second_list = []
    for index, row in query_result.iterrows():
        first_list = []
        first_list.append(str(index))
        for c in column_name:
            first_list.append(row[c])
        second_list.append(first_list)

    column_name = list(query_result)

    out_dicts = []
    for first_list in second_list:
        first_dict = {}
        count = 0
        for i in first_list:
            if count == 0:
                first_dict['time'] = i
                count += 1
            else:
                col_name = column_name[count - 1]
                first_dict[col_name] = i
                count += 1
        out_dicts.append(first_dict)

    return out_dicts, column_name


def get_table_time_query(request):
    # get data from forms
    form = table_query(request.POST)
    start_time = form['start_time'].value()
    end_time = form['end_time'].value()
    interval = form['interval'].value()
    scbds = request.POST.getlist('choose_scoreboard')

    # process chosen scoreboards
    ack_scbd = False
    job_state_scbd = False
    for s in scbds:
        if s == "job_state_scbd":
            job_state_scbd = True
        if s == "ack_scbd":
            ack_scbd = True

    # convert to epoch time and make query messages
    start_epoch = epoch_time(start_time)
    end_epoch = epoch_time(end_time)

    no_pick = False
    if (not ack_scbd) and (not job_state_scbd):
        no_pick = True
    influx_db = "estherdb"

    # set up default info
    content = {
        'form': form,
        'no_pick': no_pick,
        'choose_ack': ack_scbd,
        'choose_job_state': job_state_scbd,
        'interval': interval,
    }

    # add in content for each scoreboard
    if ack_scbd:
        dict_ack = 'select * from acks where "time">{0} and "time"<{1};'.format(start_epoch, end_epoch)
        second_list_ack, column_name_ack = get_query_result(
            query_message=query_message_ack, measurement_name="acks", influx_db=influx_db)
        content['dict_ack'] = dict_ack
        content['column_name_ack'] = column_name_ack

    if job_state_scbd:
        query_message_job_state = 'select * from JOB_STATE where "time">{0} and "time"<{1};'.format(start_epoch,
                                                                                                    end_epoch)
        dict_job_state, column_name_job_state = get_query_result(
            query_message=query_message_job_state, measurement_name="JOB_STATE", influx_db=influx_db)
        content['dict_job_state'] = dict_job_state
        content['column_name_job_state'] = column_name_job_state

    return render(request, 'time_query.html', content)

# helper function for changing YYYY,MM,DD,HH,MM,SS to epoch time
def epoch_time(in_time):
    # split the string and convert to list of integers
    time_split = in_time.split(',')
    int_time_split = [int(x) for x in time_split]

    # change into epoch time
    time_datetime = datetime.datetime(int_time_split[0], int_time_split[1],int_time_split[2],int_time_split[3],int_time_split[4],int_time_split[5], 00)
    out_time = calendar.timegm(time_datetime.timetuple())

    # deal with precisions
    out_time_work = str(out_time) + "000000000"

    return out_time_work


def get_img_query(request):
    # get data from forms
    form = table_query(request.POST)
    img_chosen = form['img_chosen'].value()
    scbds = request.POST.getlist('choose_scoreboard')

    # process chosen scoreboards
    ack_scbd = False
    job_state_scbd = False
    for s in scbds:
        if s == "job_state_scbd":
            job_state_scbd = True
        if s == "ack_scbd":
            ack_scbd = True

    no_pick = False
    if (not ack_scbd) and (not job_state_scbd):
        no_pick = True
    influx_db = "estherdb"

    # set up default info
    content = {
        'form': form,
        'no_pick': no_pick,
        'img_chosen': img_chosen,
        'choose_ack': ack_scbd,
        'choose_job_state': job_state_scbd,
    }

    # add in content for each scoreboard
    if ack_scbd:
        query_message_ack = 'select * from acks where "image_id"='
        query_message_ack += "'{0}';".format(img_chosen)
        dict_ack, column_name_ack = get_query_result(
            query_message=query_message_ack, measurement_name="acks", influx_db=influx_db)
        content['dict_ack'] = dict_ack
        content['column_name_ack'] = column_name_ack

    if job_state_scbd:
        query_message_job_state = 'select * from JOB_STATE where "image_id"='
        query_message_job_state += "'{0}';".format(img_chosen)
        dict_job_state, column_name_job_state = get_query_result(
            query_message=query_message_job_state, measurement_name="JOB_STATE", influx_db=influx_db)
        content['dict_job_state'] = dict_job_state
        content['column_name_job_state'] = column_name_job_state

    return render(request, 'img_query.html', content)

def get_index(request):
    # get data from forms
    form = table_query(request.POST)
    start_time = form['start_time'].value()
    # set up default info
    content = {
        'form': form,
        'start_time': start_time,
    }

    return render(request, 'index.html', content)