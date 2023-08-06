import asyncio
import functools
import json
import time
from .environment import ITEM1, ITEM2, ITEM3, create_api_client
from model import Item

def duration_test(io_loop, client):
    _max_reads = 10
    _duration_list = []
    script = "return {inmation.getcorepath(), inmation.gettime(inmation.currenttime())}"
    context = Item('/System/Core')
                
    for i in range(1, _max_reads + 1):
        start_time = time.clock()
        io_loop.run_until_complete(client.run_script(context, script, None))

        duration = time.clock() - start_time
        _duration_list.append(duration)

    dur_list_len = len(_duration_list)
    avg_duration = functools.reduce(lambda x,y: x+y, _duration_list) / dur_list_len
    print("Average run script duration: {:.3f} ms for {} runs".format(avg_duration * 1000, dur_list_len))

def perf_test(io_loop, client):
    _max_reads = 1000
    _duration_list = []
    script = "return {inmation.getcorepath(), inmation.gettime(inmation.currenttime())}"
    context = Item('/System/Core')
                
    for i in range(1, _max_reads + 1):
        start_time = time.clock()
        io_loop.run_until_complete(client.run_script(context, script, None))

        duration = time.clock() - start_time
        _duration_list.append(duration)

    dur_list_len = len(_duration_list)
    avg_duration = functools.reduce(lambda x,y: x+y, _duration_list) / dur_list_len
    print("Average run script duration: {:.3f} ms for {} runs\n".format(avg_duration * 1000, dur_list_len))

def runscript_test():
    io_loop = asyncio.get_event_loop()
    client = create_api_client(io_loop)

    print('\n*** START runscript_test\n')
    print("\nDuration test ...")
    duration_test(io_loop, client)

    time.sleep(3)

    print("\nPeformance test ...")
    perf_test(io_loop, client)
    print('\n*** END runscript_test\n')