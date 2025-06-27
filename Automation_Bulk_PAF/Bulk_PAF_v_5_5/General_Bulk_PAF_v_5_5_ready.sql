/* ps_job and ps_position_data paired fields:
--added pairing -- (position_nbr, deptid, jobcode, shift, reg_temp, company, std_hours, reports_to, flsa_status)
-- Not added -- (business_unit, full_part_time, mail_drop, sal_admin_plan, grade, union_cd, reg_region, adds_to_fte_actual, supv_lvl_id, class_indc)

  Officer_CD  Description	        Manager	Rank
  1	          Director	          Yes	    2
  2	          CEO	                Yes	    0
  3	          Vice President	    Yes	    1
  6	          First Line Manager	Yes	    3
  7	          Coordinator	        No	    5
  9	          Staff	              No	    6
  A	          Executive Director	Yes	    1
  B	          IC Director	        Yes	    2
  C	          IC Manager	        Yes	    3
  D	          Supervisor	        No	    4
m.officer_cd in ('1','2','3','6','A','B','C')
decode(m.officer_cd, '1', 1, '2', 1, '3', 1, '6', 1, 'A', 1, 'B', 1, 'C', 1, 0) = 1

*/
with
    function char_only_strip(dirty_data varchar2) return varchar2 deterministic is clean_data varchar2(5000); begin
        clean_data := trim(replace(replace(replace(replace(replace(dirty_data, chr(9),''), chr(13), ''), chr(10)),';'),chr(34),''));
        return clean_data;
    end;
select
    a.audit_newer
  , a.audit_effdt_exists
  , a.emplid
  , a.empl_rcd
  , a.cur_job_effdt
  , a.effdt         new_effdt
  , a.action_reason acn_rsn
  , case 
      when a.total_pos_remaining_value_diffs = 0 then
        '-----Completed-----'
      when a.remaining_value_diff is not null and a.missing_head_count_fut_matching = 0 then
        '1.  POSITION_UPDATE Position_update_complete_exceltoci'
        
      when a.remaining_value_diff is not null and a.tfr_pos is null and ((a.missing_head_count > 0) or (a.missing_head_count = 0 and a.tfr_retain_one > 1)) then
        '2.  POSITION_CREATE Position_create_complete_exceltoci'
        
      when a.remaining_value_diff is not null and a.tfr_pos is not null then
        '3.  JOB_POS_TRANSFER Job_update_position_nbr_exceltoci'
      
      when a.remaining_value_diff is not null and (a.missing_head_count = 0 and a.tfr_retain_one = 1) and missing_head_count_fut_matching > 0 then 
        '3.1 !Pending pos update after transfers.!'
        
      when a.remaining_value_diff is null and a.cur_job_pos_override = 'Y' and a.override_diff_check = 0 then
        '4.  JOB_REVERSE_OVERRIDE Job_update_override_position_exceltoci'
    end status
  , case 
      when a.total_pos_remaining_value_diffs = 0 then
        null
      else
        decode(a.missing_head_count_fut_matching, 0, 'Yes', 'No')
    end full_incumbent_move
  , a.cur_pos
  , a.tfr_pos
  , a.position_update_complete_exceltoci
  , a.remaining_value_diff
  , a.position_create_complete_exceltoci
  , a.audit_tfr_move_plus_cur_over_max
  , a.job_update_position_nbr_exceltoci
  , a.cur_job_pos_override
  , a.job_update_override_position_exceltoci
  , a.override_remaining_values_diff
  
  , a.cur_job_effseq
  , a.deptid_proper_new
  , a.jobcode_proper_new
  , a.shift_proper_new
  , a.cur_reg_temp_proper
  , a.cur_union_cd_proper
  , a.bus_unit_proper_new
  , a.company_proper_new
  , a.cur_company_proper
  , a.std_hours_proper_new
  , a.reports_to_proper_new
  , a.location_proper_new
  , a.cur_flsa_status_proper
  , a.raw_generated_full_part_time_new
from
  (
    select
      a.*
      , ptransfer.tfr_pos                 tfr_pos
      , ptransfer.tfr_pos_head_count      tfr_pos_head_count
      , ptransfer.tfr_pos_max_head_count  tfr_pos_max_head_count
      , case when a.remaining_value_diff is not null and a.missing_head_count_fut_matching = 0 then
                        a.cur_pos
              || '|' || a.effdt
              || '|' || 'A'
              || '|' || a.action_reason
              || '|' || decode(a.bus_unit_proper_new,               a.cur_bus_unit_proper,          null, a.bus_unit_proper_new)
              || '|' || decode(a.deptid_proper_new,                 a.cur_pos_deptid,               null, a.deptid_proper_new)
              || '|' || decode(a.jobcode_proper_new,                a.cur_pos_jobcode,              null, a.jobcode_proper_new)
              || '|' || ' ' -- might phase out max head count field for updates a.cur_max_head_count_from_pos
              || '|' || decode(a.cur_pos_update_incumbents, 'Y',       null, 'Y')                      --Update Incumbents = 'Y'
              || '|' || decode(a.reports_to_proper_new,             a.cur_pos_reports_to,           null, a.reports_to_proper_new)
              || '|' || decode(a.location_proper_new,               a.cur_pos_location,             null, a.location_proper_new)
              || '|' || decode(a.company_proper_new,                a.cur_pos_company,              null, a.company_proper_new)
              || '|' || decode(a.std_hours_proper_new,              a.cur_pos_std_hours,            null, a.std_hours_proper_new)
              || '|' || decode(a.cur_union_cd_proper,               a.cur_pos_union_cd,             null, a.cur_union_cd_proper)
              || '|' || decode(a.shift_proper_new,                  a.cur_pos_shift,                null, a.shift_proper_new)
              || '|' || decode(a.cur_reg_temp_proper,               a.cur_pos_reg_temp,             null, a.cur_reg_temp_proper)
              || '|' || decode(a.raw_generated_full_part_time_new,  a.cur_pos_full_part_time,       null, a.raw_generated_full_part_time_new)
              || '|' || decode(a.cur_flsa_status_proper,            a.cur_pos_flsa_status,          null, a.cur_flsa_status_proper)
              || '|' || decode(a.cur_pos_include_title, 'Y', null, 'Y')
        end position_update_complete_exceltoci
      
      , case when a.remaining_value_diff is not null and ptransfer.tfr_pos is null and ((a.missing_head_count != 0) or (a.missing_head_count = 0 and a.tfr_retain_one != 1)) then
                      '00000000'      --Position Number. '00000000' is to create a new position_nbr
            || '|' || a.effdt
            || '|' || 'A'             --Status as of Effective Date
            || '|' || 'NEW'           --Action Reason
            || '|' || a.bus_unit_proper_new
            || '|' || a.deptid_proper_new
            || '|' || a.jobcode_proper_new
            || '|' || decode(a.cur_pos_mgr_bool, 1, '1','99')  --Max Head Count
            || '|' || 'Y'             --Update Incumbents
            || '|' || a.reports_to_proper_new
            || '|' || a.location_proper_new
            || '|' || a.company_proper_new
            || '|' || a.std_hours_proper_new
            || '|' || a.cur_union_cd_proper
            || '|' || a.shift_proper_new
            || '|' || a.cur_reg_temp_proper
            || '|' || a.raw_generated_full_part_time_new
            || '|' || a.cur_flsa_status_proper
            || '|' || 'Y'             --Force Update for Title Changes
        end
            position_create_complete_exceltoci
        
      , case when a.remaining_value_diff is not null and ptransfer.tfr_pos is not null and a.missing_head_count_fut_matching != 0 then
                      a.emplid
            || '|' || a.empl_rcd
            || '|' || a.effdt
            || '|' || decode(a.cur_job_effdt, a.effdt, (a.cur_job_effseq + 1), 0)
            || '|' || ptransfer.tfr_pos
            || '|' || 'POS'
            || '|' || a.action_reason
        end job_update_position_nbr_exceltoci
      , case 
          when a.cur_job_pos_override = 'N' and ((a.remaining_value_diff is null and a.override_diff_check = 0) or a.remaining_value_diff is not null) then
            null
          when a.cur_job_pos_override = 'N' and a.remaining_value_diff is null and a.override_diff_check = 1 then
            '!!Override reversal UNSAFE. Leave Unresolved. Position Override is N but there are remaining differences: ' || a.override_remaining_values_diff
          when a.cur_job_pos_override = 'Y' and a.remaining_value_diff is not null then
            'Override reversal pending. Must complete position moves.'
          when a.cur_job_pos_override = 'Y' and a.remaining_value_diff is null and a.override_diff_check = 1 then
            '!!Override reversal UNSAFE. Leave Unresolved. Remaining differences: ' || a.override_remaining_values_diff
          else
                      a.emplid 
            || '|' || a.empl_rcd
            || '|' || a.effdt
            || '|' || decode(a.cur_job_effdt, a.effdt, (a.cur_job_effseq + 1), 0) 
            || '|' || 'N'
            || '|' || 'POS'
            || '|' || 'UPD'  
        end
            job_update_override_position_exceltoci
      , case
          when a.remaining_value_diff is not null and (a.missing_head_count = 0 and a.tfr_retain_one = 1) and missing_head_count_fut_matching != 0 then
            'Pending pos update after transfers.'
          when ptransfer.tfr_pos is null then null
          when (count(1) over (partition by ptransfer.tfr_pos)) + ptransfer.tfr_pos_head_count > ptransfer.tfr_pos_max_head_count then
            '!! Increase (' || ptransfer.tfr_pos || ') capacity before proceeding ' || ((count(1) over (partition by ptransfer.tfr_pos)) + ptransfer.tfr_pos_head_count) || ' / ' || ptransfer.tfr_pos_max_head_count
          else
               'Ok ' 
            || (count(1) over (partition by ptransfer.tfr_pos)) 
            || ' record' 
            || case when (count(1) over (partition by ptransfer.tfr_pos)) > 1 then 's' else '' end 
            || ', new counts: ' 
            || ((count(1) over (partition by ptransfer.tfr_pos)) + ptransfer.tfr_pos_head_count) 
            || ' / ' 
            || ptransfer.tfr_pos_max_head_count
        end audit_tfr_move_plus_cur_over_max
    from
      (
        select
            a.*
          , dense_rank() over (partition by a.cur_pos order by a.cur_incumbent_fut_matching desc, a.incumbent_match_string_future_values) tfr_retain_one
        from
          (
            select
                a.*
              , a.cur_pos_head_count - count(1) over (partition by a.cur_pos, a.incumbent_match_string_future_values) missing_head_count_fut_matching -- at 0 means all are accounted for and position can be altered directly in the position_data table.
              , count(1) over (partition by a.cur_pos, a.incumbent_match_string_future_values) cur_incumbent_fut_matching
              , sum(decode(a.remaining_value_diff, null, 0, 1)) over (partition by a.cur_pos) total_pos_remaining_value_diffs
              , case when a.effdt = a.cur_job_effdt and a.remaining_value_diff is not null then
                  '!Warning! Record already exists on '|| a.cur_job_effdt
                end audit_effdt_exists
            from
              (
                select
                    a.*
                  , trim(nvl(
                        rpad(decode(a.bus_unit_proper_new,    a.cur_bus_unit_proper,   null,        'bu:'          || lpad(a.bus_unit_proper_new,5,' ')|| '(' || a.cur_bus_unit_proper    || ')'),15,' ')
                          || decode(a.deptid_proper_new,      a.cur_deptid_proper,     null, ' ' || 'dept:'        ||      a.deptid_proper_new         || '(' || a.cur_deptid_proper      || ')')
                          || decode(a.location_proper_new,    a.cur_location_proper,   null, ' ' || 'location:'    ||      a.location_proper_new       || '(' || a.cur_location_proper    || ')')
                          || decode(a.jobcode_proper_new,     a.cur_jobcode_proper,    null, ' ' || 'jobcode:'     ||      a.jobcode_proper_new        || '(' || a.cur_jobcode_proper     || ')')
                          || decode(a.company_proper_new,     a.cur_company_proper,    null, ' ' || 'company:'     ||      a.company_proper_new        || '(' || a.cur_company_proper     || ')')
                          || decode(a.std_hours_proper_new,   a.cur_std_hours_proper,  null, ' ' || 'std_hours:'   || rpad(a.std_hours_proper_new      || '(' || a.cur_std_hours_proper   || ')',8,' '))
                          || decode(a.reports_to_proper_new,  a.cur_reports_to_proper, null, ' ' || 'reports_to:'  ||      a.reports_to_proper_new     || '(' || a.cur_reports_to_proper  || ')')
                          || decode(a.shift_proper_new,       a.cur_shift_proper,      null, ' ' || 'shift:'       ||      a.shift_proper_new          || '(' || a.cur_shift_proper       || ')')
                      , '')
                    ) remaining_value_diff
                  ,
                              a.deptid_proper_new
                    || '|' || a.location_proper_new
                    || '|' || a.jobcode_proper_new
                    || '|' || a.shift_proper_new
                    || '|' || a.cur_reg_temp_proper
                    || '|' || a.cur_union_cd_proper
                    || '|' || a.bus_unit_proper_new
                    || '|' || a.company_proper_new
                    || '|' || a.std_hours_proper_new
                    || '|' || a.reports_to_proper_new
                    || '|' || a.cur_flsa_status_proper
                      incumbent_match_string_future_values
                  , a.cur_pos_head_count - a.cur_incumbent_count missing_head_count
                from
                  (
                    select
                        a.*
                      , b.position_nbr        cur_pos
                      , b.position_override   cur_job_pos_override
                      , b.effdt               cur_job_effdt
                      , b.effseq              cur_job_effseq
                      
                      , decode(b.position_override, 'Y',  b.business_unit,  p.business_unit)  cur_bus_unit_proper
                      , decode(b.position_override, 'Y',  b.deptid,         p.deptid)         cur_deptid_proper
                      , decode(b.position_override, 'Y',  b.location,       p.location)       cur_location_proper
                      , decode(b.position_override, 'Y',  b.jobcode,        p.jobcode)        cur_jobcode_proper
                      
                      -- must adjust company number if it is 001 and there is a shift from >20 std_hours to <20 std_hours
                      , case
                          when a.raw_std_hours_new is null or a.raw_std_hours_new >= 20 then
                            decode(b.position_override, 'Y',  b.company,        p.company)
                          else
                            decode(decode(b.position_override, 'Y',  b.company,        p.company), '001', '101', decode(b.position_override, 'Y',  b.company,        p.company))
                        end                                                                   company_proper_new
                      
                      , decode(b.position_override, 'Y',  b.company,        p.company)        cur_company_proper
                      
                      
                      , decode(b.position_override, 'Y',  b.std_hours,      p.std_hours)      cur_std_hours_proper
                      , decode(b.position_override, 'Y',  b.reports_to,     p.reports_to)     cur_reports_to_proper
                      , decode(b.position_override, 'Y',  b.union_cd,       p.union_cd)       cur_union_cd_proper
                      , decode(b.position_override, 'Y',  b.shift,          p.shift)          cur_shift_proper
                      , decode(b.position_override, 'Y',  b.reg_temp,       p.reg_temp)       cur_reg_temp_proper
                      , decode(b.position_override, 'Y',  b.flsa_status,    p.flsa_status)    cur_flsa_status_proper
                      
                      , nvl(a.raw_deptid_new,       decode(b.position_override, 'Y',  b.deptid,         p.deptid))      deptid_proper_new
                      , nvl(a.raw_location_new,     decode(b.position_override, 'Y',  b.location,       p.location))    location_proper_new
                      , nvl(a.raw_jobcode_new,      decode(b.position_override, 'Y',  b.jobcode,        p.jobcode))     jobcode_proper_new
                      , nvl(a.raw_shift_new,        decode(b.position_override, 'Y',  b.shift,          p.shift))       shift_proper_new
                      , nvl((select dj.business_unit 
                            from ps_nmh_dept_tbl dj 
                            where 
                                  a.raw_deptid_new is not null 
                              and dj.setid = 'SHARE' 
                              and dj.deptid = nvl(a.raw_deptid_new,       decode(b.position_override, 'Y',  b.deptid,         p.deptid))
                              and dj.effdt = (select max(dj_ed.effdt) from ps_nmh_dept_tbl dj_ed where dj.setid = dj_ed.setid and dj.deptid = dj_ed.deptid and dj_ed.effdt <= sysdate)),
                                                    decode(b.position_override, 'Y',  b.business_unit,  p.business_unit))bus_unit_proper_new
                      , nvl(a.raw_std_hours_new,    decode(b.position_override, 'Y',  b.std_hours,      p.std_hours))   std_hours_proper_new
                      , nvl(a.raw_mgr_position_new, decode(b.position_override, 'Y',  b.reports_to,     p.reports_to))  reports_to_proper_new
                      
                      , p.deptid            cur_pos_deptid
                      , p.location          cur_pos_location
                      , p.jobcode           cur_pos_jobcode
                      , p.shift             cur_pos_shift
                      , p.reg_temp          cur_pos_reg_temp
                      , p.union_cd          cur_pos_union_cd
                      , p.business_unit     cur_pos_bus_unit
                      , p.company           cur_pos_company
                      , p.std_hours         cur_pos_std_hours
                      , p.reports_to        cur_pos_reports_to
                      , p.flsa_status       cur_pos_flsa_status
                      , p.full_part_time    cur_pos_full_part_time
                      , p.include_title     cur_pos_include_title
                      , p.max_head_count    cur_pos_max_head_count
                      , p.update_incumbents cur_pos_update_incumbents
                      , case 
                          when nvl(a.raw_std_hours_new,    decode(b.position_override, 'Y',  b.std_hours,    p.std_hours)) < 20 then 'C' 
                          when nvl(a.raw_std_hours_new,    decode(b.position_override, 'Y',  b.std_hours,    p.std_hours)) < 36 then 'P' 
                          else 'F' 
                        end                 raw_generated_full_part_time_new
                      , decode(p.manager_level, '1', 1, '2', 1, '3', 1, '6', 1, 'A', 1, 'B', 1, 'C', 1, 0)  cur_pos_mgr_bool
                      , nvl(( select count(1)
                          from 
                            ps_job j
                          where 
                                j.position_nbr = b.position_nbr
                            and j.hr_status = 'A'
                            and j.effdt =   (select max(j_ed.effdt)  from ps_job j_ed where j.emplid = j_ed.emplid and j.empl_rcd = j_ed.empl_rcd and           j_ed.effdt <= a.effdt)
                            and j.effseq =  (select max(j_es.effseq) from ps_job j_es where j.emplid = j_es.emplid and j.empl_rcd = j_es.empl_rcd and j.effdt = j_es.effdt)),0)
                                                                                                            cur_pos_head_count
                      , count(1) over (partition by b.position_nbr)                                         cur_incumbent_count
                      , case
                          when  
                                b.deptid         = p.deptid
                            and b.location       = p.location
                            and b.jobcode        = p.jobcode
                            and b.shift          = p.shift
                            and b.reg_temp       = p.reg_temp
                            and b.union_cd       = p.union_cd
                            and b.business_unit  = p.business_unit 
                            and b.company        = p.company
                            and b.std_hours      = p.std_hours
                            and b.reports_to     = p.reports_to
                            and b.flsa_status    = p.flsa_status
                          then 0
                          else 1
                        end override_diff_check
                      , trim(nvl(
                            rpad(decode(b.business_unit, p.business_unit, null,        'bu:'         || lpad(b.business_unit,5,' ') || '(' || p.business_unit  || ')'),15,' ')
                              || decode(b.deptid,        p.deptid,        null, ' ' || 'dept:'       ||      b.deptid               || '(' || p.deptid         || ')')
                              || decode(b.location,      p.location,      null, ' ' || 'location:'   ||      b.location             || '(' || p.location       || ')')
                              || decode(b.jobcode,       p.jobcode,       null, ' ' || 'jobcode:'    ||      b.jobcode              || '(' || p.jobcode        || ')')
                              || decode(b.company,       p.company,       null, ' ' || 'co:'         ||      b.company              || '(' || p.company        || ')')
                              || decode(b.std_hours,     p.std_hours,     null, ' ' || 'std_hours:'  || rpad(b.std_hours            || '(' || p.std_hours      || ')',8,' '))
                              || decode(b.reports_to,    p.reports_to,    null, ' ' || 'reports_to:' ||      b.reports_to           || '(' || p.reports_to     || ')')
                              || decode(b.union_cd,      p.union_cd,      null, ' ' || 'union_cd:'   ||      b.union_cd             || '(' || p.union_cd       || ')')
                              || decode(b.shift,         p.shift,         null, ' ' || 'shift:'      ||      b.shift                || '(' || p.shift          || ')')
                              || decode(b.reg_temp,      p.reg_temp,      null, ' ' || 'reg_temp:'   ||      b.reg_temp             || '(' || p.reg_temp       || ')')
                              || decode(b.flsa_status,   p.flsa_status,   null, ' ' || 'flsa_status:'||      b.flsa_status          || '(' || p.flsa_status    || ')')
                            , '')
                        ) override_remaining_values_diff
                      , case when a.effdt < sysdate and b.effdt < (select max(bc_ed.effdt) from ps_job bc_ed where b.emplid = bc_ed.emplid and b.empl_rcd = bc_ed.empl_rcd and bc_ed.effdt <= sysdate) then
                          'WARNING: NEWER JOB RECORD FOUND: ' || (select max(bc_ed.effdt) from ps_job bc_ed where b.emplid = bc_ed.emplid and b.empl_rcd = bc_ed.empl_rcd and bc_ed.effdt <= sysdate)
                        end audit_newer
                    from
                      ( select
                                      char_only_strip(replace(regexp_substr(a.value, '^([^|]*)',  1, 1       ),''''))                                                               emplid
                          ,           char_only_strip(replace(regexp_substr(a.value, '\|([^|]*)', 1, 1, '', 1),''''))                                                               empl_rcd
                          
                          ------------Pulling Effective Date and Action Reason from the first :DATA row-------------------------
                          ,   to_date(char_only_strip(replace(regexp_substr (regexp_substr (char_only_strip(:DATA), '[^,]+', 1, 1), '^([^|]*)',  1, 1       ),'''')))               effdt
                          ,           char_only_strip(replace(regexp_substr (regexp_substr (char_only_strip(:DATA), '[^,]+', 1, 1), '\|([^|]*)', 1, 1, '', 1),''''))                action_reason
                          ------------------------------------------------------------------------------------------------------
                          
                          ,           char_only_strip(replace(regexp_substr(a.value, '\|([^|]*)', 1, 2, '', 1),''''))                                                               raw_deptid_new
                          ,           char_only_strip(replace(regexp_substr(a.value, '\|([^|]*)', 1, 3, '', 1),''''))                                                               raw_location_new
                          ,           char_only_strip(replace(regexp_substr(a.value, '\|([^|]*)', 1, 4, '', 1),''''))                                                               raw_jobcode_new
                          , to_number(char_only_strip(replace(regexp_substr(a.value, '\|([^|]*)', 1, 5, '', 1),'''')))                                                              raw_std_hours_new
                          ,           char_only_strip(replace(regexp_substr(a.value, '\|([^|]*)', 1, 6, '', 1),''''))                                                               raw_shift_new
                          ,           char_only_strip(replace(regexp_substr(a.value, '\|([^|]*)', 1, 7, '', 1),''''))                                                               raw_mgr_position_new
                        from
                          ( select 
                              regexp_substr (char_only_strip(:DATA), '[^,]+', 1, level) value
                            from dual where level > 1
                            connect by level <= length ( char_only_strip(:DATA) ) - length ( replace ( char_only_strip(:DATA), ',' ) ) + 1 ) a ) a -- delimiting the data into separate rows and fields.
                      join ps_job           b       on a.emplid = b.emplid  and a.empl_rcd = b.empl_rcd
                      join ps_position_data p       on b.position_nbr  = p.position_nbr
                    where
                      (
                            b.hr_status = 'A'
                        and b.effdt     = (select max(b_ed.effdt)   from ps_job           b_ed  where b.emplid = b_ed.emplid and b.empl_rcd = b_ed.empl_rcd and           b_ed.effdt <= a.effdt)
                        and b.effseq    = (select max(b_es.effseq)  from ps_job           b_es  where b.emplid = b_es.emplid and b.empl_rcd = b_es.empl_rcd and b.effdt = b_es.effdt)  
                        and p.effdt     = (select max(p_ed.effdt)   from ps_position_data p_ed  where p.position_nbr  = p_ed.position_nbr  and p_ed.effdt  <= a.effdt)
                      )
                  ) a
              ) a
          ) a
      ) a
      left join lateral (
        select /*+ FIRST_ROWS(1) */
            pc.position_nbr tfr_pos
          , nvl((
              select 
                count(j.emplid)
              from 
                ps_job j
              where 
                    j.position_nbr = pc.position_nbr
                and j.hr_status = 'A'
                and j.effdt =   (select max(j_ed.effdt)   from ps_job j_ed where j.emplid = j_ed.emplid and j.empl_rcd = j_ed.empl_rcd and            j_ed.effdt <= a.effdt)
                and j.effseq =  (select max(j_es.effseq)  from ps_job j_es where j.emplid = j_es.emplid and j.empl_rcd = j_es.empl_rcd and j.effdt =  j_es.effdt)
            ),0) tfr_pos_head_count
          , pc.max_head_count tfr_pos_max_head_count
        from
          ps_position_data pc
        where
              a.bus_unit_proper_new     = pc.business_unit
          and a.deptid_proper_new       = pc.deptid
          and a.location_proper_new     = pc.location
          and a.jobcode_proper_new      = pc.jobcode
          and a.company_proper_new      = pc.company
          and a.std_hours_proper_new    = pc.std_hours
          and a.reports_to_proper_new   = pc.reports_to
          and a.cur_union_cd_proper     = pc.union_cd
          and a.shift_proper_new        = pc.shift
          and a.cur_reg_temp_proper     = pc.reg_temp
          and a.cur_flsa_status_proper  = pc.flsa_status
          and pc.eff_status             = 'A'
          and pc.effdt                  = (select max(pc_ed.effdt) from ps_position_data pc_ed where pc.position_nbr = pc_ed.position_nbr and pc_ed.effdt <= a.effdt)
          and a.cur_pos                != pc.position_nbr
          and 
          (
                pc.manager_level not in ('1', '2', '3', '6', 'A', 'B', 'C')
            or  (
                      pc.manager_level in ('1', '2', '3', '6', 'A', 'B', 'C')
                  and nvl((
                        select 
                          count(h.emplid) 
                        from 
                          ps_job h
                        where
                              h.position_nbr = pc.position_nbr
                          and h.hr_status = 'A'
                          and h.effdt   = (select max(h_ed.effdt)   from ps_job h_ed where h.emplid = h_ed.emplid and h.empl_rcd = h_ed.empl_rcd and            h_ed.effdt <= a.effdt)
                          and h.effseq  = (select max(h_es.effseq)  from ps_job h_es where h.emplid = h_es.emplid and h.empl_rcd = h_es.empl_rcd and h.effdt =  h_es.effdt)
                      ),0) = 0
                )
          )
        order by
            tfr_pos_head_count desc
          , pc.max_head_count  desc
          , pc.position_nbr
        fetch first 1 row only
      ) ptransfer on a.remaining_value_diff is not null and ((a.missing_head_count > 0) or (a.missing_head_count = 0 and a.tfr_retain_one > 1))
  ) a
order by
    decode(a.total_pos_remaining_value_diffs, 0, 1, 0)
  , case 
      when a.total_pos_remaining_value_diffs = 0 and a.job_update_override_position_exceltoci is not null then
        0
      when a.total_pos_remaining_value_diffs = 0 and a.job_update_override_position_exceltoci is null then
        1
    end
  , case 
      when a.total_pos_remaining_value_diffs = 0 and a.job_update_override_position_exceltoci is not null then
        a.job_update_override_position_exceltoci
    end
  , status
  , a.cur_pos
  , a.emplid
  , a.empl_rcd 
;

