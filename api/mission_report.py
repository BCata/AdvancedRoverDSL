mission_name = "Exploration"


def task_finish_cause(timeout, elapsed_time):
    if elapsed_time >= timeout:
        return "TIMEOUT EXCEEDED"
    return "SUCCESS"


def report_header(timeout, elapsed_time):
    report = '''
    Mission {0} finished in {1} seconds with {2}
    '''.format(mission_name,
               elapsed_time,
               task_finish_cause(timeout, elapsed_time))

    return report


def lakes_mission_report(timeout, elapsed_time, measurements):
    measurements_report = ""
    for lake_color in measurements:
        measurements_report += '''
            {0}:
        '''.format(lake_color)

        if not measurements[lake_color]:
            # if there are no measurements for this lake
            measurements_report += '''
                No measurements performed
            '''

        for lake_measurements in measurements[lake_color]:
            measurements_report += '''
                {0}: {1}
            '''.format(lake_measurements, measurements[lake_color][lake_measurements])

    report = '''
        Lakes found finished in {0} seconds with {1}:
        '''.format(elapsed_time,
                   task_finish_cause(timeout, elapsed_time)) + '''
            {0}
        '''.format(measurements_report)

    return report


def bricks_mission_report(timeout, elapsed_time, bricks_pushed):
    report = '''
        Push bricks finished in {0} seconds with {1}:
    '''.format(elapsed_time,
               task_finish_cause(timeout, elapsed_time)) + '''
            Bricks pushed off Mars: {0}
        '''.format(bricks_pushed)

    return report


def celebration_report(celebration_type):
    report = '''
        Celebrated with {0}
    '''.format(celebration_type)
    return report


def generate_mission_report(timeouts, measurements):
    # timeouts = {
    #               global_timeout: 300,
    #               global_time_elapsed: 200,
    #               find_lakes_timeout: 100,
    #               find_lakes_elapsed_time: 50,
    #               push_bricks_timeout: 100,
    #               push_bricks_elapsed_time: 50
    #            }
    # measurements =    {
    #                       lakes: {
    #                                    blue: {
    #                                           temperature: "30 degrees celsius",
    #                                           depth: "5 m"
    #                                           salinity: "4 per mille"
    #                                           },
    #                                    red:...
    #                              },
    #                       bricks_pushed: 3 out of 5,
    #                       celebrate: "sing"

    f = open("mission_report.txt", "w")
    mission_report = \
        report_header(timeouts["global_timeout"],
                      timeouts["global_time_elapsed"]) + \
        lakes_mission_report(timeouts["find_lakes_timeout"],
                             timeouts["find_lakes_elapsed_time"],
                             measurements['lakes']) + \
        bricks_mission_report(timeouts["push_bricks_timeout"],
                              timeouts["push_bricks_elapsed_time"],
                              measurements['bricks_pushed']) + \
        celebration_report(measurements['celebrate'])

    f.write(mission_report)

