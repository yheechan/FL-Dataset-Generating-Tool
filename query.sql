# show version, tc_result, count of tc_name
    SELECT version, experiment_name, tc_result, COUNT(tc_name) AS count
    FROM tc_info
    WHERE tc_result IN ('pass', 'fail', 'crash')
    GROUP BY version, experiment_name, tc_result
    ORDER BY version, experiment_name, tc_result;

# show versions
    SELECT experiment_name, version FROM tc_info GROUP BY experiment_name, version;