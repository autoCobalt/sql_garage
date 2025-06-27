with
    function char_only_strip(dirty_data varchar2) return varchar2 deterministic is clean_data varchar2(5000); begin
        clean_data := trim(replace(replace(replace(replace(dirty_data, chr(13), ''), chr(10)),';'),chr(34),''));
        return clean_data;
    end;
select
    'OT'                        paysheet_update_source
  , ''                          creation_date
  , active_emp.company          company
  , active_emp.paygroup         pay_group
  , 'N'                         off_cycle
  , a.emplid                    emplid
  , active_emp.empl_rcd         empl_rcd
  , ''                          sequence_nbr
  , 'D'                         paysheet_transaction_type
  , 'A'                         transaction_status
  , a.paysheet_one_time_code    paysheet_code_addition_or_refund
  , '00'                        plan_type
  , ''                          benefit_plan
  , a.ded_cd                    deduction_cd
  , a.ded_classification        before_after_tax
  , 'A'                         ded_calc_routine
  , a.amount                    amount
  , 'N'                         annual_check
  , 'B'                         sales_tax_type
from
  (
    select
                  trim(replace(regexp_substr (a.value, '[^|]+', 1, 1),''''))  emplid
      ,           trim(replace(regexp_substr (a.value, '[^|]+', 1, 2),''''))  co
      ,           trim(replace(regexp_substr (a.value, '[^|]+', 1, 3),''''))  ded_cd
      ,           trim(replace(regexp_substr (a.value, '[^|]+', 1, 4),''''))  ded_classification
      ,           trim(replace(regexp_substr (a.value, '[^|]+', 1, 5),''''))  paysheet_one_time_code
      , to_number(trim(replace(regexp_substr (a.value, '[^|]+', 1, 6),''''))) amount
    from
      (
        select 
          regexp_substr (c.value, '[^,]+', 1, level) value
        from 
          (select char_only_strip(:DATA) value from dual) c
        connect by level <= 
          length ( c.value ) - length ( replace ( c.value, ',' ) ) + 1
      ) a
  ) a
  join lateral (
    select /*+ FIRST_ROWS(1) */
        e.empl_rcd
      , e.company
      , e.paygroup
    from
      ps_employees e
    where
          e.emplid = a.emplid
      and (
              e.job_indicator = 'P'
          or not exists ( select /*+ FIRST_ROWS(1) */ 0 from ps_employees b where b.emplid = e.emplid and b.job_indicator = 'P' fetch first 1 row only)
      )
    order by
        e.reg_temp
      , e.std_hours desc
      , e.empl_rcd
    fetch first 1 row only
  ) active_emp on a.emplid is not null
where
  active_emp.empl_rcd is not null
order by
    a.emplid
  , active_emp.empl_rcd