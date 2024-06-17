from lib.utils import sort_testcase_script_name

def get_tc_list(tc_file):
        if not tc_file.exists():
            return []
        
        tc_list = []
        with open(tc_file, "r") as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if line != "":
                    tc_list.append(line)
        
        tc_list = sorted(tc_list, key=sort_testcase_script_name)
        return tc_list