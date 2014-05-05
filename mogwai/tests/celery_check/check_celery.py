if __name__ == '__main__':
    import tasks
    from mogwai._compat import print_
    print_("Queuing up tasks...")

    NUM_OBJECTS = 10

    results = tasks.test_retrieval(NUM_OBJECTS)
    print_("Got Results:")
    print_(results)

else:
    print_("This must be executed manually")