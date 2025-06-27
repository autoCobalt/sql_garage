/*
Author: Walter Alcazar
Version: 3.5

Include Only:
- hire_comment in ('Transfer', 'FTE/Shift Changes')
- any emplid's with exactly one currently active 'EMP' employee record in job table.
- if a record is missing emplid, try to find a match with name in system that follows above rules.
- if a record is missing hrs_hiring_mgr_id, try to find a match in system with matching hrs_hiring_mgr = full_name in system
    but officer_cd must be matching a mgr type from list cheryl provided, and only if one match was found. Otherwise exclude.
- Only include if exactly one manager emplid was found otherwise exclude.
- EXCLUDE casual std_hours range where person is being moved into a jobcode_tbl.union_cd ('73','399') but has std_hours < 20. This is an error.

!!!!!!!!!!!!!!!!!!!!!!Notes!!!!!!!!!!!!!!!!!!!!!!
- comp_effseq is always 0
- compensation is the hourly_rt

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
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
('1','2','3','6','A','B','C')
decode(m.officer_cd, '1', 1, '2', 1, '3', 1, '6', 1, 'A', 1, 'B', 1, 'C', 1, 0) = 1
decode(c.manager_level, '1', 2, '2', 0, '3', 1, '6', 3, '7', 5, '9', 6, 'A', 1, 'B', 2, 'C', 3, 'D', 4, 9)

ACTION REASON DETERMINATION:

Promotion (PRO):
  ONLY COMPARE FIELDS DIRECTLY FROM THE JOBCODE TABLE!!! Do this by joining the jobcode table to the jobcode in the
  job record, then joining another jobcode table to the jobcode found in the ps_nmh_edw_hires record.
  
  1)
    - CURRENT_jobcode_tbl.salary_admin_plan = EDW_jobcode_tbl.salary_admin_plan
    - CURRENT_jobcode_tbl.grade             < EDW_jobcode_tbl.grade
  2)
    - CURRENT_jobcode_tbl.salary_admin_plan = EDW_jobcode_tbl.salary_admin_plan
    - CURRENT_jobcode_tbl.grade             > EDW_jobcode_tbl.grade

Lateral Move (LTM):
  - CURRENT_job.dept != EDW.dept OR CURRENT_job.jobcode != EDW.jobcode
  
Shift Change (SFT):
  !!!!TAKES PRIORITY BETWEEN (HRS) AND (SFT) CODES IF BOTH QUALIFY!!!!

  - CURRENT_job.dept    = EDW.dept
  - CURRENT_job.jobcode = EDW.jobcode
  - CURRENT_JOB.shift  != EDW.shift

Hours Change (HRS):
  - CURRENT_job.dept        = EDW.dept
  - CURRENT_job.jobcode     = EDW.jobcode
  - CURRENT_JOB.std_hours  != EDW.std_hours

SECOND RECORD ENTRY ( ps_job.effseq = 1 ) MUST BE MADE WHEN STD_HOURS CHANGES BETWEEN FULL TIME, PART TIME, AND CASUAL RANGES:
FT_PT_Status	STD_HOURS
C	            <20
P	            >=20 <36
P	            >=36	 
 	 	 	 
Old FT-PT	New FT-PT	Action	Reason
C	        P	        POS	    CPT
C	        F	        POS	    CFT
F	        P	        POS	    FTP
F	        C	        POS	    FTC
P	        F	        POS	    PTF
P	        C	        POS	    PTC

*/
select
    a.acn_rsn
  , a.hire_comments
  , a.req_num
  , a.orig_emp
  , a.name
  , a.emplid
  , a.empl_rcd
  , a.effseq
  , a.cur_job_effdt
  , a.start_date
  , a.complex_check
  , a.complex_def
  , a.status
  , a.audit_newer
  , a.cur_pos
  , a.cur_job_officer_cd
  , a.tfr_pos
  , a.tfr_pos_mgr_level
  , case 
      when a.tfr_pos is null and a.row_val = 1 then
        null
      else
                  decode(a.complex_check, 'Complex', '!!!', '') || a.emplid
        || '|' || a.empl_rcd
        || '|' || a.start_date
        || '|' || decode(a.cur_job_effdt, a.start_date, a.effseq + a.row_rn, a.row_rn - 1)
        || '|' || a.tfr_pos
        || '|' || 'POS'
        || '|' || a.acn_rsn
        || '|' || 'Y'
        || '|' || 'Y'
        || '|' || '0'
        || '|' || 'NAHRLY'
        || '|' || a.corrected_hourly_rt
        || '|' || 'H'
        || '|' || 'USD'
    end transfers_exceltoci 
  , a.prof_dt_exceltoci
  , nvl(a.remaining_value_diff, '-------Completed-------') remaining_value_diff
  , a.edw_mgr_id
  , a.edw_mgr_name
  , a.dual_emp_exceltoci
  , a.position_create_complete_exceltoci
  , a.edw_prof_exp_dt
  , a.edw_deptid
  , a.edw_jobcode
  , a.edw_std_hours
  , a.edw_shift
  , a.cur_job_indicator
  , a.row_val
  , a.row_def  
  
from
  (
    select
        a.*
      , decode(a.edw_prof_exp_dt, a.cur_prof_exp_dt, 'Match', a.emplid || '|' || a.empl_rcd || '|' || a.edw_prof_exp_dt) prof_dt_exceltoci
      , case 
          when 
                a.id_req_count > 1 
            or decode(a.hire_comments, 'Transfer', 1, 'FTE/Shift Changes', 1, 0) = 0 
            or a.fpc_union_mismatch = 1 
            or a.id_empl_rcd_count > 1
            or a.edw_reports_to is null
          then 
            'Complex' 
          else 
            'Simple' 
        end complex_check
      , case 
          when a.edw_reports_to is null then
            'Reports_to issue'
          when a.id_req_count > 1 then 
            'Multiple Different Emplids'
          when a.id_empl_rcd_count > 1 then 
            'Multiple active empl_rcds'
          when a.fpc_union_mismatch = 1 then 
            'Casual Union Mismatch'
          when  decode(a.hire_comments, 'Transfer', 1, 'FTE/Shift Changes', 1, 0) = 0 then 
            'Non Tfr/FTE/Shift Change'
        end complex_def
      , ptransfer.*
      , count(1) over (partition by ptransfer.tfr_pos) tfr_planned_moves
      , case
          when a.row_val = 2 then
            a.generated_fpc_analysis
          when a.row_val = 3 then
            'TRE'
          when a.row_val > 3 then
            'N/A NOT PROGRAMMED FOR ADDITIONAL ROWS BEYOND row_val = 3'
          when (a.cur_job_deptid = a.edw_deptid) and (a.cur_job_jobcode = a.edw_jobcode) and (a.cur_job_shift != a.edw_shift) then
            'SFT'
          when (a.cur_job_deptid = a.edw_deptid) and (a.cur_job_jobcode = a.edw_jobcode) and (a.cur_job_std_hours != a.edw_std_hours) then
            'HRS'
          when (a.cur_job_jc_mgr_rank > a.edw_jc_mgr_rank) then
            'PRO'
          when (a.cur_job_jc_mgr_rank < a.edw_jc_mgr_rank) then
            'DEM'
          when (a.cur_job_jc_sal_admin_plan = a.edw_jc_sal_admin_plan) and (a.cur_job_jc_grade < a.edw_jc_grade) then
            'PRO'
          when (a.cur_job_jc_sal_admin_plan = a.edw_jc_sal_admin_plan) and (a.cur_job_jc_grade > a.edw_jc_grade) then
            'DEM'
          when (a.cur_job_jobcode != a.edw_jobcode) and (a.cur_job_hourly_rt < a.corrected_hourly_rt) then
            'PRO'
          when (a.cur_job_deptid != a.edw_deptid) or (a.cur_job_jobcode != a.edw_jobcode) then
            'LTM'
          else
            '???'
        end acn_rsn
      , 
        case
          when a.row_val != 1 then
            null
          when a.remaining_value_diff is null then
            null
          when ptransfer.tfr_pos is not null then
            null
          when a.edw_anyvalue_reports_to is not null and a.edw_reports_to is null then
            'Reports_to is not a manager.'
          when a.edw_anyvalue_reports_to is null and a.edw_reports_to is null then
            'Hiring manager no longer active.'
          else
                      '00000000'      --Position Number. '00000000' is to create a new position_nbr
            || '|' || a.start_date
            || '|' || 'A'             --Status as of Effective Date
            || '|' || 'NEW'           --Action Reason
            || '|' || a.edw_bus_unit_jr
            || '|' || a.edw_deptid
            || '|' || a.edw_jobcode
            || '|' || decode(a.edw_jc_is_mgr, 1, '1','99') --Max Head Count
            || '|' || 'Y'             --Update Incumbents
            || '|' || a.edw_reports_to
            || '|' || a.edw_jc_company
            || '|' || a.edw_std_hours
            || '|' || a.edw_jc_union_cd
            || '|' || a.edw_shift
            || '|' || a.edw_reg_temp
            || '|' || a.edw_generated_fpc
            || '|' || a.edw_flsa_status
            || '|' || 'Y'             --Force Update for Title Changes
        end position_create_complete_exceltoci
      , case
          when a.remaining_value_diff is null then
            '-----Completed-----'
          when a.edw_anyvalue_reports_to is not null and a.edw_reports_to is null then
            'Reports_to is not a manager.'
          when a.edw_anyvalue_reports_to is null and a.edw_reports_to is null then
            'Hiring manager no longer active.'
          when a.cur_job_on_leave = 1 then
            '--!! On Leave !!---'
          when a.fpc_union_mismatch = 1 then 
            '!Union and Casual!!'
          when a.cur_job_company != a.edw_jc_company then
            '!!Company  Number!!'
          when a.cur_job_effdt = a.start_date then 
            'Existing ' || a.start_date
        end status
      , sum(case when a.remaining_value_diff is null then 1 else 0 end) over (partition by a.req_num, a.emplid)         min_one_completed_row
      , dual_emp.dual_emp_exceltoci
    from
      (
        select  /*+ PARALLEL(2) */
            a.*
          , (select a_prof.prof_experience_dt from ps_per_org_asgn a_prof where a.emplid = a_prof.emplid and a.empl_rcd = a_prof.empl_rcd) cur_prof_exp_dt
          , count(distinct a.emplid) over (partition by a.req_num, a.name)                                              id_req_count
          , count(distinct a.empl_rcd) over (partition by a.req_num, a.name, a.emplid)                                  id_empl_rcd_count
          , decode(c.manager_level, '1', 1, '2', 1, '3', 1, '6', 1, 'A', 1, 'B', 1, 'C', 1, 0)                          cur_job_jc_is_mgr
          , decode(e.manager_level, '1', 1, '2', 1, '3', 1, '6', 1, 'A', 1, 'B', 1, 'C', 1, 0)                          edw_jc_is_mgr
          , decode(c.manager_level, '1', 2, '2', 0, '3', 1, '6', 3, '7', 5, '9', 6, 'A', 1, 'B', 2, 'C', 3, 'D', 4, 9)  cur_job_jc_mgr_rank
          , decode(e.manager_level, '1', 2, '2', 0, '3', 1, '6', 3, '7', 5, '9', 6, 'A', 1, 'B', 2, 'C', 3, 'D', 4, 9)  edw_jc_mgr_rank
          , decode(a.edw_generated_fpc, 'F', 0, 'P', 0, decode(e.union_cd, '73', 1, '399', 1, 0))                       fpc_union_mismatch
          , e.union_cd                                            edw_jc_union_cd
          , decode(e.union_cd, '73', '001', '399', '001', '101')  edw_jc_company
          , c.sal_admin_plan                                      cur_job_jc_sal_admin_plan
          , e.sal_admin_plan                                      edw_jc_sal_admin_plan
          , c.grade                                               cur_job_jc_grade
          , e.grade                                               edw_jc_grade
          , e.manager_level                                       edw_jc_officer_cd
          , trim(nvl(
                  rpad(decode(a.edw_bus_unit_jr,                                    a.cur_job_bus_unit,     null,        'bu:'          || lpad(a.edw_bus_unit_jr,5,' ')                            || '(' || a.cur_job_bus_unit || ')'),15,' ')
                    || decode(a.edw_deptid,                                         a.cur_job_deptid,       null, ' ' || 'dept:'        || a.edw_deptid                                             || '(' || a.cur_job_deptid        || ')')
                    || decode(a.edw_jobcode,                                        a.cur_job_jobcode,      null, ' ' || 'jobcode:'     || a.edw_jobcode                                            || '(' || a.cur_job_jobcode       || ')')
                    || decode(decode(e.union_cd, '73', '001', '399', '001', '101'), a.cur_job_company,      null, ' ' || 'co:'          ||decode(e.union_cd, '73', '001', '399', '001', '101')      || '(' || a.cur_job_company       || ')')
                    || decode(a.edw_std_hours,                                      a.cur_job_std_hours,    null, ' ' || 'std_hours:'   || rpad(a.edw_std_hours                                     || '(' || a.cur_job_std_hours     || ')',8,' '))
                    || decode(a.edw_reports_to,                                     a.cur_job_reports_to,   null, ' ' || 'reports_to:'  || a.edw_reports_to                                         || '(' || a.cur_job_reports_to    || ')')
                    || decode(e.union_cd,                                           a.cur_job_union_cd,     null, ' ' || 'union_cd:'    || e.union_cd                                               || '(' || a.cur_job_union_cd      || ')')
                    || decode(a.edw_shift,                                          a.cur_job_shift,        null, ' ' || 'shift:'       || a.edw_shift                                              || '(' || a.cur_job_shift         || ')')
                    || decode(a.edw_reg_temp,                                       a.cur_job_reg_temp,     null, ' ' || 'reg_temp:'    || a.edw_reg_temp                                           || '(' || a.cur_job_reg_temp      || ')')
                    || decode(a.edw_flsa_status,                                    a.cur_job_flsa_status,  null, ' ' || 'flsa_status:' || a.edw_flsa_status                                        || '(' || a.cur_job_flsa_status   || ')')
              , '')
            )                                                     remaining_value_diff
          , case when a.future_job_effdt is not null then
              '!!NEWER EFFDT FOUND: ' || a.future_job_effdt
            end                                                   audit_newer
          , duplicate_fpc_change.*
        from
          (
        
              select
                  a.*
                , 1                                                     matching_name_id
                , j.emplid                                              emplid
                , j.empl_rcd                                            empl_rcd
                , j.effdt                                               cur_job_effdt
                , (
                    select min(j_ed.effdt) 
                    from 
                      ps_job j_ed 
                    where 
                          j.emplid    = j_ed.emplid 
                      and j.empl_rcd  = j_ed.empl_rcd 
                      and j_ed.effdt  > a.start_date
                  )                                                     future_job_effdt
                , j.effseq                                              effseq
                , j.hourly_rt                                           cur_job_hourly_rt
                , j.business_unit                                       cur_job_bus_unit
                , case 
                    when abs(a.edw_hourly_rt - j.hourly_rt) < 0.01 then 
                      j.hourly_rt
                    else
                      a.edw_hourly_rt
                  end                                                   corrected_hourly_rt
                , j.job_indicator                                       cur_job_indicator
                , j.officer_cd                                          cur_job_officer_cd
                , j.deptid                                              cur_job_deptid
                , j.jobcode                                             cur_job_jobcode
                , j.std_hours                                           cur_job_std_hours
                , j.full_part_time                                      cur_job_full_part_time
                , j.shift                                               cur_job_shift
                , j.position_nbr                                        cur_pos
                , j.reports_to                                          cur_job_reports_to
                , j.company                                             cur_job_company
                , j.union_cd                                            cur_job_union_cd
                , j.flsa_status                                         cur_job_flsa_status
                , j.reg_temp                                            cur_job_reg_temp
                , decode(j.empl_status, 'L', 1, 'P', 1, 0)              cur_job_on_leave
                , case
                    when 
                          (a.edw_std_hours <  20 and j.full_part_time = 'C')
                      or  (a.edw_std_hours <  36 and j.full_part_time = 'P')
                      or  (a.edw_std_hours >= 36 and j.full_part_time = 'F')
                    then
                      null
                    when a.edw_std_hours < 20 then
                      decode(j.full_part_time, 'F', 'FTC', 'PTC')
                    when a.edw_std_hours < 36 then
                      decode(j.full_part_time, 'F', 'FTP', 'CPT')
                    else
                      decode(j.full_part_time, 'P', 'PTF', 'CFT')
                  end                                                   generated_fpc_analysis
              from
                (
                  -- Primary, inner-most subquery
                  select
                      trim(a.hire_comments)                             hire_comments
                    , trim(a.emplid)                                    orig_emp
                    , a.name                                            name
                    , a.union_code_descr                                edw_union_code_descr
                    , a.hourly_rt                                       edw_hourly_rt
                    , a.prof_experience_dt                              edw_prof_exp_dt
                    , a.hrs_hiring_mgr_id                               edw_mgr_id
                    , a.hrs_hiring_mgr                                  edw_mgr_name
                    , a.deptid                                          edw_deptid
                    , a.jobcode                                         edw_jobcode
                    , a.std_hours                                       edw_std_hours
                    , case 
                        when a.std_hours < 20 then 'C' 
                        when a.std_hours < 36 then 'P' 
                        else 'F' 
                      end                                               edw_generated_fpc
                    , a.shift                                           edw_shift
                    , a.flsa_status                                     edw_flsa_status
                    , a.reg_temp                                        edw_reg_temp
                    , a.start_date                                      start_date
                    , a.req_num                                         req_num
                    , a.completed_dt                                    edw_completed_dt
                    , (
                        select d.business_unit 
                        from ps_nmh_dept_tbl d 
                        where 
                              a.deptid = d.deptid 
                          and d.effdt = (
                            select max(d_ed.effdt) 
                            from ps_nmh_dept_tbl d_ed 
                            where 
                                  d.setid = d_ed.setid 
                              and d.deptid = d_ed.deptid 
                              and d_ed.effdt <= sysdate
                          )
                      )                                                 edw_bus_unit_jr
                      
                    , (
                        select
                          n.position_nbr
                        from
                          (
                            select
                                count(*) over () mgr_records_count
                              , m.position_nbr
                            from 
                              ps_job m 
                            where 
                                  a.hrs_hiring_mgr_id != ' '
                              and length(a.hrs_hiring_mgr_id) = 6
                              and regexp_like(a.hrs_hiring_mgr_id, '^[[:digit:]]+$')
                              and a.hrs_hiring_mgr_id = m.emplid
                              and m.hr_status = 'A'
                              and decode(m.officer_cd, '1', 1, '2', 1, '3', 1, '6', 1, 'A', 1, 'B', 1, 'C', 1, 0) = 1
                              and m.effdt =   (select max(m_ed.effdt)   from ps_job m_ed where m.emplid = m_ed.emplid and m.empl_rcd = m_ed.empl_rcd and           m_ed.effdt <= a.start_date)
                              and m.effseq =  (select max(m_es.effseq)  from ps_job m_es where m.emplid = m_es.emplid and m.empl_rcd = m_es.empl_rcd and m.effdt = m_es.effdt)
                          ) n
                        where
                          n.mgr_records_count = 1
                      )                                                 edw_reports_to
                    , (
                        select
                          n.position_nbr
                        from
                          (
                            select
                                count(*) over () mgr_records_count
                              , m.position_nbr
                            from 
                              ps_job m 
                            where 
                                  a.hrs_hiring_mgr_id != ' '
                              and length(a.hrs_hiring_mgr_id) = 6
                              and regexp_like(a.hrs_hiring_mgr_id, '^[[:digit:]]+$')
                              and a.hrs_hiring_mgr_id = m.emplid
                              and m.hr_status = 'A'
                              and m.effdt =   (select max(m_ed.effdt)   from ps_job m_ed where m.emplid = m_ed.emplid and m.empl_rcd = m_ed.empl_rcd and           m_ed.effdt <= a.start_date)
                              and m.effseq =  (select max(m_es.effseq)  from ps_job m_es where m.emplid = m_es.emplid and m.empl_rcd = m_es.empl_rcd and m.effdt = m_es.effdt)
                          ) n
                        where
                          n.mgr_records_count = 1
                      )                                                 edw_anyvalue_reports_to
                      
                  from
                    ps_nmh_edw_hires a
                  where
                        a.hire_comments != ' '
                    and a.emplid != ' '
                    and a.start_date = :STARTING_DATE
                ) a
                join ps_job j on a.orig_emp = j.emplid and j.per_org = 'EMP' and j.hr_status = 'A'
              where
                    j.effdt  = (select max(j_ed.effdt)  from ps_job j_ed where j.emplid = j_ed.emplid and j.empl_rcd = j_ed.empl_rcd and            j_ed.effdt <= a.start_date)
                and j.effseq = (select max(j_es.effseq) from ps_job j_es where j.emplid = j_es.emplid and j.empl_rcd = j_es.empl_rcd and j.effdt =  j_es.effdt)
            
            
            UNION ALL        
              
              select
                a.*
              from
                (
                  select
                      a.*
                    , count(distinct n.emplid) over (partition by a.req_num, a.name)  matching_name_emplid_found
                    , j.emplid                                                        emplid
                    , j.empl_rcd                                                      empl_rcd
                    , j.effdt                                                         cur_job_effdt
                    , (
                        select min(j_ed.effdt) 
                        from 
                          ps_job j_ed 
                        where 
                              j.emplid    = j_ed.emplid 
                          and j.empl_rcd  = j_ed.empl_rcd 
                          and j_ed.effdt  > a.start_date
                      )                                                               future_job_effdt
                    , j.effseq                                                        effseq
                    , j.hourly_rt                                                     cur_job_hourly_rt
                    , j.business_unit                                                 cur_job_bus_unit
                    , case 
                        when abs(a.edw_hourly_rt - j.hourly_rt) < 0.01 then 
                          j.hourly_rt
                        else
                          a.edw_hourly_rt
                      end                                                             corrected_hourly_rt
                    , j.job_indicator                                                 cur_job_indicator
                    , j.officer_cd                                                    cur_job_officer_cd
                    , j.deptid                                                        cur_job_deptid
                    , j.jobcode                                                       cur_job_jobcode
                    , j.std_hours                                                     cur_job_std_hours
                    , j.full_part_time                                                cur_job_full_part_time
                    , j.shift                                                         cur_job_shift
                    , j.position_nbr                                                  cur_pos
                    , j.reports_to                                                    cur_job_reports_to
                    , j.company                                                       cur_job_company
                    , j.union_cd                                                      cur_job_union_cd
                    , j.flsa_status                                                   cur_job_flsa_status
                    , j.reg_temp                                                      cur_job_reg_temp
                    , decode(j.empl_status, 'L', 1, 'P', 1, 0)                        cur_job_on_leave
                    , case
                        when 
                              (a.edw_std_hours <  20 and j.full_part_time = 'C')
                          or  (a.edw_std_hours <  36 and j.full_part_time = 'P')
                          or  (a.edw_std_hours >= 36 and j.full_part_time = 'F')
                        then
                          null
                        when a.edw_std_hours < 20 then
                          decode(j.full_part_time, 'F', 'FTC', 'PTC')
                        when a.edw_std_hours < 36 then
                          decode(j.full_part_time, 'F', 'FTP', 'CPT')
                        else
                          decode(j.full_part_time, 'P', 'PTF', 'CFT')
                      end                                                   generated_fpc_analysis
                  from
                    (
                      -- Primary, inner-most subquery - SPECIAL HANDLE LIST FOR MISSING EMPLID'S. Try to find a full name match in the system.
                      select
                          trim(a.hire_comments)                             hire_comments
                        , trim(a.emplid)                                    orig_emp
                        , a.name                                            name
                        , a.union_code_descr                                edw_union_code_descr
                        , a.hourly_rt                                       edw_hourly_rt
                        , a.prof_experience_dt                              edw_prof_exp_dt
                        , a.hrs_hiring_mgr_id                               edw_mgr_id
                        , a.hrs_hiring_mgr                                  edw_mgr_name
                        , a.deptid                                          edw_deptid
                        , a.jobcode                                         edw_jobcode
                        , a.std_hours                                       edw_std_hours
                        , case 
                            when a.std_hours < 20 then 'C' 
                            when a.std_hours < 36 then 'P' 
                            else 'F' 
                          end                                               edw_generated_fpc
                        , a.shift                                           edw_shift
                        , a.flsa_status                                     edw_flsa_status
                        , a.reg_temp                                        edw_reg_temp
                        , a.start_date                                      start_date
                        , a.req_num                                         req_num
                        , a.completed_dt                                    edw_completed_dt
                        
                        , (
                            select d.business_unit 
                            from ps_nmh_dept_tbl d 
                            where 
                                  a.deptid = d.deptid 
                              and d.effdt = (
                                select max(d_ed.effdt) 
                                from ps_nmh_dept_tbl d_ed 
                                where 
                                      d.setid = d_ed.setid 
                                  and d.deptid = d_ed.deptid 
                                  and d_ed.effdt <= sysdate
                              )
                          )                                                 edw_bus_unit_jr
                          
                        , (
                            select
                              n.position_nbr
                            from
                              (
                                select
                                    count(*) over () mgr_records_count
                                  , m.position_nbr
                                from 
                                  ps_job m 
                                where 
                                      a.hrs_hiring_mgr_id != ' '
                                  and length(a.hrs_hiring_mgr_id) = 6
                                  and regexp_like(a.hrs_hiring_mgr_id, '^[[:digit:]]+$')
                                  and a.hrs_hiring_mgr_id = m.emplid
                                  and m.hr_status = 'A'
                                  and decode(m.officer_cd, '1', 1, '2', 1, '3', 1, '6', 1, 'A', 1, 'B', 1, 'C', 1, 0) = 1
                                  and m.effdt =   (select max(m_ed.effdt)   from ps_job m_ed where m.emplid = m_ed.emplid and m.empl_rcd = m_ed.empl_rcd and           m_ed.effdt <= a.start_date)
                                  and m.effseq =  (select max(m_es.effseq)  from ps_job m_es where m.emplid = m_es.emplid and m.empl_rcd = m_es.empl_rcd and m.effdt = m_es.effdt)
                              ) n
                            where
                              n.mgr_records_count = 1
                          )                                                 edw_reports_to
                        , (
                            select
                              n.position_nbr
                            from
                              (
                                select
                                    count(*) over () mgr_records_count
                                  , m.position_nbr
                                from 
                                  ps_job m 
                                where 
                                      a.hrs_hiring_mgr_id != ' '
                                  and length(a.hrs_hiring_mgr_id) = 6
                                  and regexp_like(a.hrs_hiring_mgr_id, '^[[:digit:]]+$')
                                  and a.hrs_hiring_mgr_id = m.emplid
                                  and m.hr_status = 'A'
                                  and m.effdt =   (select max(m_ed.effdt)   from ps_job m_ed where m.emplid = m_ed.emplid and m.empl_rcd = m_ed.empl_rcd and           m_ed.effdt <= a.start_date)
                                  and m.effseq =  (select max(m_es.effseq)  from ps_job m_es where m.emplid = m_es.emplid and m.empl_rcd = m_es.empl_rcd and m.effdt = m_es.effdt)
                              ) n
                            where
                              n.mgr_records_count = 1
                          )                                                 edw_anyvalue_reports_to
                          
                      from
                        ps_nmh_edw_hires a
                      where
                            a.hire_comments != ' '
                        and a.emplid = ' '
                        and a.start_date = :STARTING_DATE
                    ) a
                    join ps_names n on a.name = n.name_display and n.name_type = 'PRI'
                    join ps_job j on n.emplid = j.emplid and j.per_org = 'EMP' and j.hr_status = 'A'
                  where
                        n.effdt  = (select max(n_ed.effdt)  from ps_names n_ed  where n.emplid = n_ed.emplid and n.name_type = n_ed.name_type and n_ed.effdt <= sysdate)
                    and j.effdt  = (select max(j_ed.effdt)  from ps_job j_ed    where j.emplid = j_ed.emplid and j.empl_rcd = j_ed.empl_rcd and            j_ed.effdt <= a.start_date)
                    and j.effseq = (select max(j_es.effseq) from ps_job j_es    where j.emplid = j_es.emplid and j.empl_rcd = j_es.empl_rcd and j.effdt =  j_es.effdt)
                ) a
              where
                a.matching_name_emplid_found = 1
            
          ) a
          join ps_jobcode_tbl c on a.cur_job_jobcode = c.jobcode and c.setid = 'SHARE'
          join ps_jobcode_tbl e on a.edw_jobcode     = e.jobcode and e.setid = 'SHARE'
          left join lateral (
            select
                d.*
              , row_number() over (order by d.row_val) row_rn
              , 1 + decode(a.generated_fpc_analysis, null, 0, 1) + decode(a.edw_reg_temp, a.cur_job_reg_temp, 0, 1) row_total
            from
              (
                  select 
                      1               row_val
                    , 'Primary Row'   row_def
                  from 
                    dual
                union all
                  select 
                      2
                    , 'FPC cat change'
                  from 
                    dual
                  where
                    a.generated_fpc_analysis is not null
                union all
                  select 
                      3
                    , 'reg_temp change'
                  from 
                    dual
                  where
                    a.edw_reg_temp != a.cur_job_reg_temp
              ) d
          ) duplicate_fpc_change on 1=1
          
        where
              c.effdt = (select max(c_ed.effdt) from ps_jobcode_tbl c_ed where c.setid = c_ed.setid and c.jobcode = c_ed.jobcode and c_ed.effdt <= sysdate)
          and e.effdt = (select max(e_ed.effdt) from ps_jobcode_tbl e_ed where e.setid = e_ed.setid and e.jobcode = e_ed.jobcode and e_ed.effdt <= sysdate)
      ) a
      left join lateral (
        select /*+ FIRST_ROWS(1) */
            pc.position_nbr tfr_pos
          , pc.manager_level tfr_pos_mgr_level
          , nvl((
              select 
                count(j.emplid)
              from 
                ps_job j
              where 
                    j.position_nbr = pc.position_nbr
                and j.hr_status = 'A'
                and j.effdt =   (select max(j_ed.effdt)   from ps_job j_ed where j.emplid = j_ed.emplid and j.empl_rcd = j_ed.empl_rcd and            j_ed.effdt <= a.start_date)
                and j.effseq =  (select max(j_es.effseq)  from ps_job j_es where j.emplid = j_es.emplid and j.empl_rcd = j_es.empl_rcd and j.effdt =  j_es.effdt)
            ),0) tfr_pos_head_count
          , pc.max_head_count tfr_pos_max_head_count
        from
          ps_position_data pc
        where
              a.edw_bus_unit_jr   = pc.business_unit
          and a.edw_deptid        = pc.deptid
          and a.edw_jobcode       = pc.jobcode
          and a.edw_jc_company    = pc.company
          and a.edw_std_hours     = pc.std_hours
          and a.edw_reports_to    = pc.reports_to
          and a.edw_jc_union_cd   = pc.union_cd
          and a.edw_shift         = pc.shift
          and a.edw_reg_temp      = pc.reg_temp
          and a.edw_flsa_status   = pc.flsa_status
          and pc.eff_status       = 'A'
          and pc.effdt            = (select max(pc_ed.effdt) from ps_position_data pc_ed where pc.position_nbr = pc_ed.position_nbr and pc_ed.effdt <= a.start_date)
          
          and 
          (
                decode(pc.manager_level, '1', 1, '2', 1, '3', 1, '6', 1, 'A', 1, 'B', 1, 'C', 1, 0) = 0
            or  a.cur_pos = pc.position_nbr
            or  (
                      decode(pc.manager_level, '1', 1, '2', 1, '3', 1, '6', 1, 'A', 1, 'B', 1, 'C', 1, 0) = 1
                  and nvl((
                        select 
                          count(h.emplid) 
                        from 
                          ps_job h
                        where
                              h.position_nbr = pc.position_nbr
                          and h.hr_status = 'A'
                          and h.effdt   = (select max(h_ed.effdt)   from ps_job h_ed where h.emplid = h_ed.emplid and h.empl_rcd = h_ed.empl_rcd and            h_ed.effdt <= a.start_date)
                          and h.effseq  = (select max(h_es.effseq)  from ps_job h_es where h.emplid = h_es.emplid and h.empl_rcd = h_es.empl_rcd and h.effdt =  h_es.effdt)
                      ),0) = 0
                )
          )
        order by
            case when a.cur_pos = pc.position_nbr then 0 else 1 end
          , tfr_pos_head_count desc
          , pc.max_head_count desc
          , pc.position_nbr
        fetch first 1 row only
      ) ptransfer on a.remaining_value_diff is not null and a.row_val = 1
      left join lateral (
        select
          case
            when b.id_count is null then
              'No Active Primary EMP'
            when b.id_count > 1 then
              'Multiple Primary EMP records'
            else
                        a.emplid
              || '|' || ((select max(h_er.empl_rcd) from ps_per_org_asgn h_er where h.emplid = h_er.emplid) + 1)
              || '|' || h.per_org
              || '|' || h.org_instance_ern
              || '|' || h.benefit_rcd_nbr
              || '|' || 'Y'                   -- cmpny_dt_ovr
              || '|' || h.cmpny_seniority_dt
              || '|' || 'Y'                   -- service_dt_ovr
              || '|' || h.service_dt
              || '|' || 'Y'                   -- sen_pay_dt_ovr
              || '|' || h.seniority_pay_dt
              || '|' || a.edw_prof_exp_dt
              || '|' || a.start_date
              || '|' || '0'                   -- effseq
              || '|' || ptransfer.tfr_pos
              || '|' || 'ADL'                 -- action
              || '|' || 'ADL'                 -- action_reason
              || '|' || a.edw_jc_officer_cd
              || '|' || 'S'                   -- job_indicator
              || '|' || 'BA'                  -- benefit_system
              || '|' || 'Y'                   -- default_pay
              || '|' || 'Y'                   -- calc_comp
              || '|' || '0'                   -- comp_effseq
              || '|' || 'NAHRLY'              -- comp_rate_code
              || '|' || a.edw_hourly_rt
              || '|' || 'H'                   -- frequency
              || '|' || 'USD'                 -- curr_code
          end dual_emp_exceltoci
        from
          dual d
          left join lateral
            (
              select /*+ FIRST_ROWS(1) */
                  b.id_count
                , b.empl_rcd
              from
                (
                  select
                      count(*) over () id_count
                    , b.empl_rcd
                  from
                    ps_job b
                  where
                        a.emplid = b.emplid
                    and b.hr_status = 'A'
                    and b.job_indicator = 'P'
                    and b.per_org = 'EMP'
                    and b.effdt  = (select max(b_ed.effdt)  from ps_job b_ed where b.emplid = b_ed.emplid and b.empl_rcd = b_ed.empl_rcd and b_ed.effdt <= a.start_date)
                    and b.effseq = (select max(b_es.effseq) from ps_job b_es where b.emplid = b_es.emplid and b.empl_rcd = b_es.empl_rcd and b.effdt = b_es.effdt)
                ) b
              fetch first 1 row only
            ) b on 1=1
          left join ps_per_org_asgn h on b.id_count is not null and b.id_count = 1 and a.emplid = h.emplid and b.empl_rcd = h.empl_rcd
      ) dual_emp on ptransfer.tfr_pos is not null and a.hire_comments = 'Dual Employment'
    where
          a.remaining_value_diff is not null
      or  (
              a.remaining_value_diff is null
          and a.row_val = 1
      )
  ) a
where
  (
        a.min_one_completed_row = 0
    or  (
            a.min_one_completed_row >= 1
        and a.remaining_value_diff is null
    )
  )
order by
    decode(a.remaining_value_diff, null, 1, 0)
  , a.complex_check desc
  , sum(case when a.acn_rsn = '???' then 1 else 0 end) over (partition by a.emplid)
  , a.emplid
  , a.req_num
  , a.empl_rcd
  , a.effseq
  , a.row_rn
  , a.remaining_value_diff
  , transfers_exceltoci
;
