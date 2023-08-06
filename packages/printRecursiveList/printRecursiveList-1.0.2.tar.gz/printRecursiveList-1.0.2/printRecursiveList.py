""" _loop_solver funciton to print the recursive lists. """
def _loop_solver(obj):
    """ Logic of _looop_solver funciton which takes a parameter as a complex list and print each element """
    if isinstance(obj,list):
        for loop_list_item in obj:
            _loop_solver(loop_list_item)
    else:
        print(obj)