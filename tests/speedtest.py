import time

def speedtest(function_string, times_run = int):
    test_times = []
    for i in range(times_run +1):
        start_time = time.perf_counter()
        test = function_string
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        test_times.append(execution_time)

    print(f'The average runtime of {function_string} is :{sum(test_times) / len(test_times)}')



test_list = ['phrase 1', 'test phrase 2', 'test phrase 3', 'test phrase 4', 'test phrase 5', 'test phrase 6', 'test phrase 7', 'test phrase 8', 'test phrase 9', 'test phrase 10']
speedtest(' '.join(test_list), 100000)
speedtest(f'{test_list[0]} {test_list[1]} {test_list[2]} {test_list[3]} {test_list[4]} {test_list[5]} {test_list[6]} {test_list[7]} {test_list[8]} {test_list[9]}', 100000)