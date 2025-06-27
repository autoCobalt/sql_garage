/*
Author: Walter Alcazar
Version: 1.0 - Cleaned Version

This uses the Levenshtein Distance formula to find the nearest match individuals to a given full name. 
Query was needed to find individuals from a list of names where the names may have typo's/nicknames.
Outdated table joins in the query. Saved only for backup. Query must be rebuilt if needed again.

*/

WITH 
  names_list AS
(
  SELECT
    count(*) over (PARTITION BY f.name_searched) as prox_range_hits,
    f.*
  FROM
    (
-----------------------------------------------------------------------------------------
      --ALL HEAVY LIFTING OF SEARCHING FOR MATCHES IS IN HERE
      SELECT
        b_list.name_searched,
        b_list.original_search_count,
        pmax.emplid,
        pmax.name_type,
        pmax.effdt,
        pmax.name as max_historical_name_match,
        a.name_psformat,
        a.name_display,
        a.first_name,
        a.last_name,
        a.middle_name,
        row_number() over (PARTITION BY pmax.emplid ORDER BY UTL_MATCH.jaro_winkler_similarity(lower(b_list.name_searched),lower(pmax.name)) desc, p.order_by_seq) row_priority,
        UTL_MATCH.jaro_winkler_similarity(lower(b_list.name_searched),lower(pmax.name)) max_historical_proximity,
        max(UTL_MATCH.jaro_winkler_similarity(lower(b_list.name_searched),lower(pmax.name))) over (PARTITION BY pmax.emplid) as max_historical_by_id,
        UTL_MATCH.jaro_winkler_similarity(lower(b_list.name_searched),lower(a.name_psformat)) current_proximity
      FROM
        (
          SELECT
              b_counter.COLUMN_VALUE name_searched,
              count(*) over () as original_search_count
            FROM
              sys.odcivarchar2list(
              
              
              
              --batch 1: 1-500 (500)
              --REDACTED

              --batch 2: 501-1000 (500)
              --REDACTED

              --batch 3: 1001-1536 (536)
              --REDACTED

          
              ) b_counter
        ) b_list,
        PS_NAMES pmax
         JOIN PS_PERSON_NAME a ON pmax.emplid = a.emplid
         JOIN PS_HCR_NM_TYP_I p ON pmax.name_type = p.name_type
      WHERE
        UTL_MATCH.jaro_winkler_similarity(lower(b_list.name_searched),lower(pmax.name)) > 90
-------------------------------------------------------------------------------------------------------------        
    ) f
  WHERE
    f.row_priority = 1
),
  nc AS 
(
  SELECT
    nc.emplid,
    nc.empl_rcd,
    nc.effdt,
    nc.effseq,
    nc.per_org,
    nc.company,
    nc.business_unit,
    nc.deptid,
    nc.dept_descr,
    nc.jobcode,
    nc.job_descr,
    nc.nm_job_descr50,
    nc.position_nbr,
    nc.empl_status,
    nc.hire_dt,
    nc.termination_dt,
    j.location,
    mj.emplid manager_id,
    mj_name.name manager_name,
    mj_name.first_name manager_first_name,
    mj_name.last_name manager_last_name,
    mj_name.name_psformat manager_name_psformat
  FROM
    PS_NMH_RT_COMPLETE nc
      JOIN PS_JOB j ON
        j.emplid   = nc.emplid AND
        j.empl_rcd = nc.empl_rcd AND
        j.effdt    = nc.effdt AND
        j.effseq   = nc.effseq
      LEFT OUTER JOIN PS_JOB mj ON nc.reports_to = mj.position_nbr AND
        mj.effdt = ( 
            SELECT MAX(mj_ed.effdt) FROM PS_JOB mj_ed 
            WHERE 
              mj.position_nbr = mj_ed.position_nbr AND
              mj_ed.effdt <= nc.effdt
        ) AND
        mj.effseq = (
            SELECT MAX(mj_es.effseq) FROM PS_JOB mj_es
            WHERE 
              mj.emplid = mj_es.emplid AND 
              mj.empl_rcd = mj_es.empl_rcd AND
              mj.effdt = mj_es.effdt
        )
        LEFT OUTER JOIN PS_PERSON_NAME mj_name ON mj.emplid = mj_name.emplid
),
lt AS
(
  SELECT
    l.location,
    l.descr,
    l.descr_ac,
    l.building,
    l.geo_code
  FROM
    PS_LOCATION_TBL l
  WHERE
    l.setid = 'SHARE' AND
    l.effdt =
      (
        SELECT MAX(lt_ed.effdt) FROM PS_LOCATION_TBL lt_ed 
        WHERE 
          l.location = lt_ed.location AND 
          l.setid = lt_ed.setid
      )
) 
------------------------BEGIN MAIN SELECT QUERY BELOW------------------------
SELECT
  a.prox_range_hits,
  a.original_search_count,
  a.name_searched,
  a.max_historical_name_match,
  a.name_psformat,
  a.max_historical_proximity,
  a.current_proximity, 
  user_id.oprid,
  a.emplid,
  nc.empl_rcd,
  nc.effdt,
  nc.effseq,
  nid.national_id,
  a.name_display,
  a.first_name,
  a.last_name,
  a.middle_name,
  b.address_type,
  b.address1,
  b.address2,
  b.city,
  b.county,
  b.state,
  b.postal,
  coalesce(ph.phone, pc.phone) first_phone_found,
  ph.phone phone_home,
  pc.phone phone_cell,
  coalesce(eh.email_addr, eb.email_addr) first_email_found,
  eb.email_addr email_busn,
  eh.email_addr email_home,
  nc.per_org,
  nc.company,
  nc.business_unit,
  nc.deptid,
  nc.dept_descr,
  nc.manager_id,
  nc.manager_name,
  nc.manager_first_name,
  nc.manager_last_name,
  nc.manager_name_psformat,
  nc.location,
  lt.descr location_descr,
  lt.descr_ac location_descr_ac,
  lt.building,
  lt.geo_code,
  nc.jobcode,
  nc.job_descr,
  nc.nm_job_descr50,
  nc.position_nbr,
  nc.empl_status,
  nc.hire_dt,
  nc.termination_dt
FROM
  names_list a
    LEFT OUTER JOIN nc ON a.emplid = nc.emplid
      LEFT OUTER JOIN lt ON nc.location = lt.location
    LEFT OUTER JOIN PS_PERSON_ADDRESS   b ON a.emplid =  b.emplid and b.address_type = 'HOME'
    LEFT OUTER JOIN PS_PERSONAL_PHONE  ph ON a.emplid = ph.emplid and ph.PHONE_TYPE  = 'HOME'
    LEFT OUTER JOIN PS_PERSONAL_PHONE  pc ON a.emplid = pc.emplid and pc.PHONE_TYPE  = 'CELL'
    LEFT OUTER JOIN PS_EMAIL_ADDRESSES eb ON a.emplid = eb.emplid and eb.e_addr_type = 'BUSN'
    LEFT OUTER JOIN PS_EMAIL_ADDRESSES eh ON a.emplid = eh.emplid and eh.e_addr_type = 'HOME'
    LEFT OUTER JOIN PS_PERS_NID nid       ON a.emplid = nid.emplid
    LEFT OUTER JOIN PSOPRDEFN user_id     ON a.emplid = user_id.emplid
ORDER BY
  a.name_searched, a.max_historical_proximity desc, a.current_proximity desc

