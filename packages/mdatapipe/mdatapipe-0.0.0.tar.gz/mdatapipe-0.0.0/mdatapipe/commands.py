from __future__ import print_function
import click
from mdatapipe.pipeline import Pipeline
from time import sleep


@click.command()    # NOQA
@click.argument('file', type=click.Path(exists=True), nargs=-1, required=True)
@click.option('--fail', '-f', is_flag=True)
@click.option('--stats-interval', '-s', type=int)
@click.option('--parallel', '-p', multiple=True)
def run(file, fail, stats_interval, parallel):

    pipeline_list = []

    # Load all pipelines
    for filename in file:
        print("Starting pipeline %s" % filename)
        if len(parallel) > 0:
            print("Parallel", ','.join(parallel))
        pipeline = Pipeline(file=filename, parallel=parallel)
        pipeline_list.append(pipeline)

    # Start all pipelines
    for pipeline in pipeline_list:
        pipeline.start(fail)

    time_to_status = stats_interval

    # Loop checking the stats of all pipelines
    total_processes = 1  # Dummy value to start the collect stats loop

    try:
        while total_processes > 0:
            if time_to_status:
                time_to_status -= 1
            total_processes = 0
            for pipeline in pipeline_list:
                reques_status = (time_to_status == 0)
                if reques_status:
                    pipeline.check_status(reques_status)
                    time_to_status = stats_interval
                total_processes += pipeline.get_stats()
                pipeline.check_status(reques_status)
            sleep(1)

    except KeyboardInterrupt:
        print("\nInterrupted by user")
        for pipeline in pipeline_list:
            pipeline.kill()
