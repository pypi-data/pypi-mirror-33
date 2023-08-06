def init_yappi():
    OUT_FILE = '/tmp/mdatapipe'

    import atexit
    import yappi

    print('[YAPPI START]')
    yappi.set_clock_type('wall')
    yappi.start()

    @atexit.register
    def finish_yappi():  # pylint: disable=W0612
        print('[YAPPI STOP]')

        yappi.stop()

        print('[YAPPI WRITE]')

        stats = yappi.get_func_stats()

        for stat_type in ['pstat', 'callgrind', 'ystat']:
            print('writing {}.{}'.format(OUT_FILE, stat_type))
            stats.save('{}.{}'.format(OUT_FILE, stat_type), type=stat_type)

        print('\n[YAPPI FUNC_STATS]')

        print('writing {}.func_stats'.format(OUT_FILE))
        with open('{}.func_stats'.format(OUT_FILE), 'wb') as fh:
            stats.print_all(out=fh)

        print('\n[YAPPI THREAD_STATS]')

    print('writing {}.thread_stats'.format(OUT_FILE))
    tstats = yappi.get_thread_stats()
    with open('{}.thread_stats'.format(OUT_FILE), 'wb') as fh:
        tstats.print_all(out=fh)

    print('[YAPPI OUT]')
