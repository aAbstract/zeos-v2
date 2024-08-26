def zeos_breakpoint(stack_frame: dict = {}):
    print('Starting Debugger...')
    print('Stack Frame:')
    for sf_vk in stack_frame.keys():
        print(sf_vk)
    print('Global Scope:')
    for gs_vk in globals().keys():
        print(gs_vk)
    print('Starting Debugger...OK')
    cmd = ''
    while cmd != 'q':
        try:
            cmd = input('dbg> ')
            if cmd == 'exit':
                break
            else:
                eval(cmd, globals(), stack_frame)
        except Exception as e:
            print('Debug Shell Error: ' + str(e))
