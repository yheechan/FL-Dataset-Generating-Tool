# show version, tc_result, count of tc_name
    SELECT version, experiment_name, tc_result, COUNT(tc_name) AS count
    FROM tc_info
    WHERE tc_result IN ('pass', 'fail', 'crash')
    GROUP BY version, experiment_name, tc_result
    ORDER BY version, experiment_name, tc_result;

# show versions
    SELECT experiment_name, version FROM tc_info GROUP BY experiment_name, version;


# Average number of mutations per line of a subject
WITH avg_mutants_per_line AS (
    SELECT 
        m.bug_idx, 
        AVG(m.mutant_count_per_line) AS avg_mutants_per_bug
    FROM (
        SELECT 
            bug_idx, 
            line_idx, 
            COUNT(*) AS mutant_count_per_line
        FROM mutation_info
        WHERE build_result IS TRUE
        GROUP BY bug_idx, line_idx
    ) m
    JOIN bug_info b ON m.bug_idx = b.bug_idx
    WHERE b.subject = 'zlib_ng_TF_top30' 
      AND b.mbfl IS TRUE
    GROUP BY m.bug_idx
)
SELECT AVG(avg_mutants_per_bug) AS overall_avg_mutants_per_line
FROM avg_mutants_per_line;