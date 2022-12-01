def read_satisfiability(json_obj,min_solving_option):
    try:
        satisfiability = int(json_obj[min_solving_option.replace("solvingTime", "satisfiability")][0])
    except:
        try:
            satisfiability = int(json_obj["satisfiability"][0])
        except:
            satisfiability=-1
    return satisfiability