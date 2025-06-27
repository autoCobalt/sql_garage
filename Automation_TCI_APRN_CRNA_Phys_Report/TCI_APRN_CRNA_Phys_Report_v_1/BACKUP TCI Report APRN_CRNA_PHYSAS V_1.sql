--Developed by Walter Alcazar. Version 1.0. Completed 2025-01-22
-- 1.0 Used TCI Staging report as a template. Added filter for jobfamily in ('B1','B2','B6')
--       as well as load_hire_dt between 100 days in past and 100 days in future

with
  function digits_only(phone varchar2) return varchar2 deterministic is clean_phone varchar2(25); begin
      clean_phone := regexp_replace(phone, '[^0-9]','');
      /*
      if length(clean_phone) = 10 then
        clean_phone := '1' || clean_phone;
      end if;
      */
      return clean_phone;
  end;
select
    null                                                                    notes
  , a.hire_dt                                                               hire_dt
  , TO_CHAR(sysdate, 'YYYY-MM-DD')                                          current_dt
  , to_date(a.hire_dt, 'YYYY-MM-DD') - TRUNC(sysdate)                       days_until_hire
  , a.req_num                                                               req_num
  , a.lm_emplid                                                             lm_emplid
  , a.hire_comments                                                         hire_type
  , a.last_name                                                             last_name
  , a.first_name                                                            first_name
  , a.middle_name                                                           middle_name
  , a.birthdate                                                             birthdate
  , a.national_id                                                           ssn
  , (
      select
        p.position_nbr || '|cur/in-' || LPAD(NVL(ac.head_count,0),3) || '|' || TO_CHAR(p.effdt,'YYYY-MM-DD') 
        || '|' || p.eff_status || '| | |UPD|' || LPAD(p.business_unit,6) || '|' 
        || p.deptid || '|' || p.jobcode || '|Y|HEAD?|' || LPAD(p.max_head_count,3)
        || '|Y|' || p.reports_to || '|' || LPAD(p.location,11) || '|Maildrop?|' 
        || p.company || '|' || LPAD(p.std_hours,4) || '|' || LPAD(p.union_cd,2) || '|' 
        || p.shift || '|' || p.reg_temp || '|' || p.full_part_time 
        || '| | |Y|' || p.avail_telework_pos || '--Available telework|Y'
      from
        ps_position_data p
          outer apply (
              select
                count(acc.emplid) head_count
              from 
                ps_job acc
              where
                    acc.position_nbr = p.position_nbr
                and acc.hr_status = 'A'
                and acc.effdt = (select MAX(acc_ed.effdt) from ps_job acc_ed where acc.emplid = acc_ed.emplid and acc.empl_rcd = acc_ed.empl_rcd and acc_ed.effdt <= SYSDATE)
                and acc.effseq = (select MAX(acc_es.effseq) from ps_job acc_es where acc.emplid = acc_es.emplid and acc.empl_rcd = acc_es.empl_rcd and acc.effdt = acc_es.effdt)
          ) ac
      where
            a.mgr_position_nbr <> 'XXXXXXXX'
        and p.eff_status = 'A'
        and p.deptid = a.deptid
        and p.jobcode = a.jobcode
        and p.reports_to = a.mgr_position_nbr
        and p.std_hours = a.std_hours
        and p.shift = DECODE(a.shift,'N','1',a.shift)
        and p.reg_temp = a.reg_temp
        and p.full_part_time = a.fpc
        and p.avail_telework_pos = DECODE(a.location,'RMOTE','Y','N')
        and p.effdt <= a.orig_hire_dt  -- ASK ABOUT +500 FROM ORIGINAL FILE. WHAT DOES THAT MEAN???????????
        and not exists (select 0 from ps_position_data p_ed where p.position_nbr = p_ed.position_nbr and p.effdt < p_ed.effdt and p_ed.effdt <= a.orig_hire_dt)
        and rownum = 1
    )                                                                       post_chg_pos_use
  
from
  (
    select
        a1.*
      , (
          select d.business_unit 
          from ps_nmh_dept_tbl d 
          where 
                d.deptid = a1.deptid 
            and d.setid  = 'SHARE'
            and d.effdt = (select MAX(d_ed.effdt) from ps_nmh_dept_tbl d_ed where d.setid = d_ed.setid and d.deptid = d_ed.deptid and d_ed.effdt <= SYSDATE)
          
        ) business_unit
      , (
          select jc.job_family
          from ps_jobcode_tbl jc 
          where 
                jc.jobcode = a1.jobcode 
            and jc.setid = 'SHARE'
            and jc.effdt = (select MAX(jc_ed.effdt) from ps_jobcode_tbl jc_ed where jc.setid =jc_ed.setid and jc.jobcode = jc_ed.jobcode and jc_ed.effdt <= SYSDATE)
        ) job_family
      , CASE WHEN a1.std_hours >= 36 THEN 'F' WHEN a1.std_hours < 20  THEN 'C' ELSE 'P' END     fpc
      , NVL(j.position_nbr,'XXXXXXXX')                    mgr_position_nbr
    from
      ( 
        select
            ap.nmh_load_status
          , ap.nmh_taleo_cand_id
          , ap.req_num
          , TO_CHAR(ap.hire_dt,'YYYY-MM-DD')        hire_dt
          , ap.hire_dt                              orig_hire_dt
          , ap.manager_id
          , ap.deptid
          , ap.jobcode
          , ap.std_hours
          , ap.last_name
          , ap.first_name
          , ap.middle_name
          , TO_CHAR(ap.birthdate,'YYYY-MM-DD')      birthdate
          , digits_only(ap.home_phone)              home_phone
          , digits_only(ap.work_phone)              work_phone
          , digits_only(ap.mobile_phone)            mobile_phone
          , ap.address1
          , ap.address2
          , ap.city
          , ap.state_number
          , ap.postal
          , ap.email_addr
          , ap.descr100
          , ap.flsa_status
          , ap.scheduled
          , ap.location
          , ap.union_cd
          , ap.national_id
          , ap.reg_temp
          , ap.full_part_time
          , ap.shift
          , ap.hourly_rt
          , ap.alter_emplid
          , ap.hire_comments
          , ap.datein_prefix
          , regexp_replace(ap.message_descr,'^Message: ','')                  message_descr
          , case
              when regexp_like(substr(ap.message_descr,-6), '^[[:digit:]]+$') then
                CAST(regexp_substr(substr(ap.message_descr,-6), '[0-9]{6}') as varchar2(6))  
            end lm_emplid
          , pnid.emplid                                                     ssn_matching_emplid
          , digits_only(pnid_phone.phone) ssn_emplid_cell_phone
          , pnid_address.email_addr ssn_emplid_home_email
          , DECODE(VALIDATE_CONVERSION(ap.req_num as NUMBER),1,TO_NUMBER(ap.req_num),0) num_order
          
        from
          ps_nmh_taleo ap
          join ps_jobcode_tbl jc on ap.jobcode = jc.jobcode and jc.setid = 'SHARE' and jc.job_family in ('B1','B6','B2')
          left join ps_pers_nid pnid on ap.national_id = pnid.national_id and pnid.country = 'USA' and pnid.national_id_type = 'PR' and case
                when regexp_like(pnid.national_id, '^[[:digit:]]+$') then
                  trim(CAST(regexp_substr(pnid.national_id, '[0-9]') as varchar2(20)))  
              end <> ' '
          left join ps_personal_phone pnid_phone on pnid.emplid = pnid_phone.emplid and pnid_phone.phone_type = 'CELL'
          left join ps_email_addresses pnid_address on pnid.emplid = pnid_address.emplid and pnid_address.e_addr_type = 'HOME'
        where
              ap.nmh_load_status = 'N'
          and ap.hire_dt between (sysdate - 100) and (sysdate + 100)
          and jc.effdt = (select max(jc_ed.effdt) from ps_jobcode_tbl jc_ed where jc.jobcode = jc_ed.jobcode and jc.setid = jc_ed.setid and jc_ed.effdt <= sysdate)
      ) a1
      left join ps_job j on
            j.emplid = a1.manager_id
        and j.hr_status = 'A'
        and j.officer_cd not in ('9', '7', 'D')
    where
      (
             j.effdt is null
          or (
                  j.effdt = (select  MAX(j_ed.effdt) from ps_job j_ed where j.emplid = j_ed.emplid and j.empl_rcd = j_ed.empl_rcd and j_ed.effdt <= SYSDATE)
              and j.effseq = (select MAX(j_es.effseq) from ps_job j_es where j.emplid = j_es.emplid and j.empl_rcd = j_es.empl_rcd and j.effdt = j_es.effdt)
          )
      )
  ) a
  outer apply (
    select
          LISTAGG(
              distinct case when a1.nmh_elig_rehire = 'N' then 'N' else '' end
            , ' | '
          ) within group (order by a1.per_org, a1.hr_status,  a1.termination_dt desc, a1.job_indicator, a1.emplid) rehire_eligibility
        , LISTAGG(
            case
              when p2.national_id is not null and p2.national_id <> a.national_id then 'SSN MISMATCH! ' || p2.national_id || ' <> ' || a.national_id
              else
                RPAD(
                          a1.hr_status || '/' || a1.per_org || '/' || a1.emplid || '/' 
                          || a1.empl_rcd || '/' || TO_CHAR(a1.effdt,'YYYY-MM-DD') 
                          || '/' || NVL(p2.national_id,'no_ssn_in_system') || '/' || TO_CHAR(p1.birthdate,'YYYY-MM-DD')
                          || '/' || a1.deptid || '/'|| a1.jobcode || '/' || n1.last_name
                          || '/' || n1.first_name
                    , 90
                  )
            end
          , '   '
          ) within group (order by a1.per_org, a1.hr_status,  a1.termination_dt desc, a1.job_indicator, a1.emplid) combined_records
      from
        ps_person p1
          join ps_job   a1 on p1.emplid = a1.emplid
          join ps_names n1 on a1.emplid = n1.emplid and n1.name_type = 'PRI'
          left join ps_pers_nid p2 on a1.emplid = p2.emplid 
              and p2.national_id_type = 'PR' 
              and p2.country = 'USA' 
              and p2.national_id is not null 
              and p2.national_id <> 'XXXXXXXXX'
      where
            p1.emplid = a.lm_emplid
        and (
             p2.national_id is null
          or p2.national_id = a.national_id
          or (
                  p2.national_id is not null
              and p2.national_id <> a.national_id
              and rownum = 1
          )
        )
        and a1.effdt =  (select MAX(a1_ed.effdt)  from ps_job a1_ed   where a1.emplid = a1_ed.emplid and a1.empl_rcd  = a1_ed.empl_rcd  and a1_ed.effdt <= SYSDATE)
        and a1.effseq = (select MAX(a1_es.effseq) from ps_job a1_es   where a1.emplid = a1_es.emplid and a1.empl_rcd  = a1_es.empl_rcd  and a1.effdt = a1_es.effdt)
        and n1.effdt =  (select MAX(n1_ed.effdt)  from ps_names n1_ed where n1.emplid = n1_ed.emplid and n1.name_type = n1_ed.name_type and n1_ed.effdt <= SYSDATE)
  ) lm_records
  outer apply (
    select
          LISTAGG(distinct
              case
                when a.ssn_matching_emplid is not null and a.ssn_matching_emplid = a.lm_emplid then ''
                else 
                  case when a1.nmh_elig_rehire = 'N' then 'N' else '' end
              end
            , ' | '
          ) within group (order by a1.per_org, a1.hr_status,  a1.termination_dt desc, a1.job_indicator, a1.emplid) rehire_eligibility
        , LISTAGG(
              case
                when a.ssn_matching_emplid is not null and a.ssn_matching_emplid = a.lm_emplid and rownum = 1 then '' --'ssn_matched_emplid is same as long_message_emplid'
                when a.ssn_matching_emplid is not null and a.ssn_matching_emplid = a.lm_emplid and rownum <> 1 then ''
                else
                  RPAD(
                            a1.hr_status || '/' || a1.per_org || '/' || a1.emplid || '/' 
                            || a1.empl_rcd || '/' || TO_CHAR(a1.effdt,'YYYY-MM-DD') 
                            || '/' || NVL(a.national_id,'no_ssn_in_system') || '/' || TO_CHAR(p1.birthdate,'YYYY-MM-DD')
                            || '/' || a1.deptid || '/'|| a1.jobcode || '/' || n1.last_name
                            || '/' || n1.first_name
                      , 90
                    )
              end
            , '   '
          ) within group (order by a1.per_org, a1.hr_status,  a1.termination_dt desc, a1.job_indicator, a1.emplid) combined_records
      from
        ps_person p1
          join ps_job   a1 on p1.emplid = a1.emplid
          join ps_names n1 on a1.emplid = n1.emplid and n1.name_type = 'PRI'
      where
            p1.emplid = a.ssn_matching_emplid
        and a1.effdt =  (select MAX(a1_ed.effdt)  from ps_job a1_ed   where a1.emplid = a1_ed.emplid and a1.empl_rcd  = a1_ed.empl_rcd  and a1_ed.effdt <= SYSDATE)
        and a1.effseq = (select MAX(a1_es.effseq) from ps_job a1_es   where a1.emplid = a1_es.emplid and a1.empl_rcd  = a1_es.empl_rcd  and a1.effdt = a1_es.effdt)
        and n1.effdt =  (select MAX(n1_ed.effdt)  from ps_names n1_ed where n1.emplid = n1_ed.emplid and n1.name_type = n1_ed.name_type and n1_ed.effdt <= SYSDATE)
  ) ssn_matching_records
order by
    a.hire_dt
  , a.num_order
  , a.req_num