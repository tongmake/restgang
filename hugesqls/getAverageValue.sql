with tab as (select to_date( :stime ,'yyyy-MM-dd') as strattime,to_date( :etime ,'yyyy-MM-dd') as endtime from dual)
,table1 as
 (select '1990年以来同期均值',
         a.shmjxj +
         ((b.shmjxj - a.shmjxj) / (to_char(last_day((select endtime from tab)), 'dd')) * (select to_char(endtime,'DD')  from tab)) as shmjxj,
         a.czmjxj +
         ((b.czmjxj - a.czmjxj) / (to_char(last_day((select endtime from tab)), 'dd')) * (select to_char(endtime,'DD')  from tab)) as czmjxj,
         a.szrk +
         ((b.szrk - a.szrk) / (to_char(last_day((select endtime from tab)), 'dd')) * (select to_char(endtime,'DD')  from tab)) as szrk,
         a.swrk +
         ((b.swrk - a.swrk) / (to_char(last_day((select endtime from tab)), 'dd')) * (select to_char(endtime,'DD')  from tab)) as swrk,
         a.szrkr + ((b.szrkr - a.szrkr) /
         (to_char(last_day((select endtime from tab)), 'dd')) * (select to_char(endtime,'DD')  from tab))  as szrkr,
         a.dtfw +
         ((b.dtfw - a.dtfw) / (to_char(last_day((select endtime from tab)), 'dd')) * (select to_char(endtime,'DD')  from tab)) as dtfw,
         a.zjjjzss +
          ((b.zjjjzss - a.zjjjzss) /(to_char(last_day((select endtime from tab)), 'dd')) * (select to_char(endtime,'DD')  from tab)) as zjjjzss,
         a.slsszjjjss + ((b.slsszjjjss - a.slsszjjjss) /(to_char(last_day((select endtime from tab)),'dd')) * (select to_char(endtime,'DD')  from tab)) as slsszjjjss
    from (select avg(shmjxj) shmjxj,
                 avg(czmjxj) czmjxj,
                 avg(szrk) szrk,
                 avg(swrk) swrk,
                 avg(szrkr) szrkr,
                 avg(dtfw) dtfw,
                 avg(zjjjzss) zjjjzss,
                 avg(slsszjjjss) slsszjjjss
            from (select t.lsyear,
                         t.lsmonth,
                         avg(t.shmjxj) as shmjxj,
                         avg(t.czmjxj) as czmjxj,
                         avg(t.szrk) as szrk,
                         avg(t.swrk) as swrk,
                         avg(t.szrkr) as szrkr,
                         avg(t.dtfw) as dtfw,
                         avg(t.zjjjzss) as zjjjzss,
                         avg(t.slsszjjjss) as slsszjjjss
                    from lstqlj t
                   where t.lsmonth = (select to_char(add_months(endtime,-1),'MM') from tab)
                     and t.lsyear >= 1990
                     and t.lsyear < (select to_char(endtime,'YYYY') from tab)
                   group by t.lsyear, t.lsmonth)) a,
         (select avg(shmjxj) shmjxj,
                 avg(czmjxj) czmjxj,
                 avg(szrk) szrk,
                 avg(swrk) swrk,
                 avg(szrkr) szrkr,
                 avg(dtfw) dtfw,
                 avg(zjjjzss) zjjjzss,
                 avg(slsszjjjss) slsszjjjss
            from (select t.lsyear,
                         t.lsmonth,
                         avg(t.shmjxj) as shmjxj,
                         avg(t.czmjxj) as czmjxj,
                         avg(t.szrk) as szrk,
                         avg(t.swrk) as swrk,
                         avg(t.szrkr) as szrkr,
                         avg(t.dtfw) as dtfw,
                         avg(t.zjjjzss) as zjjjzss,
                         avg(t.slsszjjjss) as slsszjjjss
                    from lstqlj t
                   where t.lsmonth = (select to_char(endtime,'MM') from tab)
                     and t.lsyear >= 1990
                     and t.lsyear <  (select to_char(endtime,'YYYY') from tab)
                   group by t.lsyear, t.lsmonth)) b),
table2 as
 (select '2000年以来同期均值',
         a.shmjxj +
         ((b.shmjxj - a.shmjxj) / (to_char(last_day((select endtime from tab)), 'dd')) * (select to_char(endtime,'DD')  from tab)) as shmjxj,
         a.czmjxj +
         ((b.czmjxj - a.czmjxj) / (to_char(last_day((select endtime from tab)), 'dd')) * (select to_char(endtime,'DD')  from tab)) as czmjxj,
         a.szrk +
         ((b.szrk - a.szrk) / (to_char(last_day((select endtime from tab)), 'dd')） * (select to_char(endtime,'DD')  from tab)) as szrk,
         a.swrk +
         ((b.swrk - a.swrk) / (to_char(last_day((select endtime from tab)), 'dd')） * (select to_char(endtime,'DD')  from tab)) as swrk,
         a.szrkr + ((b.szrkr - a.szrkr) / (to_char(last_day((select endtime from tab)), 'dd')) * (select to_char(endtime,'DD')  from tab))  as szrkr,
         a.dtfw +
         ((b.dtfw - a.dtfw) / (to_char(last_day((select endtime from tab)), 'dd')) * (select to_char(endtime,'DD')  from tab)) as dtfw,
         a.zjjjzss + ((b.zjjjzss - a.zjjjzss) /(to_char(last_day((select endtime from tab)), 'dd')) * (select to_char(endtime,'DD')  from tab)) as zjjjzss,
         a.slsszjjjss + ((b.slsszjjjss - a.slsszjjjss) /(to_char(last_day((select endtime from tab)),'dd')) * (select to_char(endtime,'DD')  from tab)) as slsszjjjss
    from (select avg(shmjxj) shmjxj,
                 avg(czmjxj) czmjxj,
                 avg(szrk) szrk,
                 avg(swrk)swrk,
                 avg(szrkr) szrkr,
                 avg(dtfw) dtfw,
                 avg(zjjjzss) zjjjzss,
                 avg(slsszjjjss) slsszjjjss
            from (select t.lsyear,
                         t.lsmonth,
                         avg(t.shmjxj) as shmjxj,
                         avg(t.czmjxj) as czmjxj,
                         avg(t.szrk) as szrk,
                         avg(t.swrk) as swrk,
                         avg(t.szrkr) as szrkr,
                         avg(t.dtfw) as dtfw,
                         avg(t.zjjjzss) as zjjjzss,
                         avg(t.slsszjjjss) as slsszjjjss
                    from lstqlj t
                   where t.lsmonth = (select to_char(add_months(endtime,-1),'MM') from tab)
                     and t.lsyear >= 2000
                     and t.lsyear < (select to_char(endtime,'YYYY') from tab)
                   group by t.lsyear, t.lsmonth)) a,
         (select avg(shmjxj) shmjxj,
                 avg(czmjxj) czmjxj,
                 avg(szrk) szrk,
                 avg(swrk) swrk,
                 avg(szrkr) szrkr,
                 avg(dtfw) dtfw,
                 avg(zjjjzss) zjjjzss,
                 avg(slsszjjjss) slsszjjjss
            from (select t.lsyear,
                         t.lsmonth,
                         avg(t.shmjxj) as shmjxj,
                         avg(t.czmjxj) as czmjxj,
                         avg(t.szrk) as szrk,
                         avg(t.swrk) as swrk,
                         avg(t.szrkr) as szrkr,
                         avg(t.dtfw) as dtfw,
                         avg(t.zjjjzss) as zjjjzss,
                         avg(t.slsszjjjss) as slsszjjjss
                    from lstqlj t
                   where t.lsmonth = (select to_char(endtime,'MM') from tab)
                     and t.lsyear >= 2000
                     and t.lsyear < (select to_char(endtime,'YYYY') from tab)
                   group by t.lsyear, t.lsmonth)) b),
table3 as
 (select '近五年同期均值',
         a.shmjxj +
         ((b.shmjxj - a.shmjxj) / (to_char(last_day((select endtime from tab)),'dd')) * (select to_char(endtime,'DD')  from tab)) as shmjxj,
         a.czmjxj +
         ((b.czmjxj - a.czmjxj) / (to_char(last_day((select endtime from tab)), 'dd')) * (select to_char(endtime,'DD')  from tab)) as czmjxj,
         a.szrk +
         ((b.szrk - a.szrk) / (to_char(last_day((select endtime from tab)), 'dd')) * (select to_char(endtime,'DD')  from tab)) as szrk,
         a.swrk +
         ((b.swrk - a.swrk) / (to_char(last_day((select endtime from tab)), 'dd')) * (select to_char(endtime,'DD')  from tab)) as swrk,
         a.szrkr +
         ((b.szrkr - a.szrkr) /(to_char(last_day((select endtime from tab)), 'dd')) * (select to_char(endtime,'DD')  from tab)) as szrkr,
         a.dtfw +
         ((b.dtfw - a.dtfw) / (to_char(last_day((select endtime from tab)), 'dd')) * (select to_char(endtime,'DD')  from tab)) as dtfw,
         a.zjjjzss +
          ((b.zjjjzss - a.zjjjzss) /(to_char(last_day((select endtime from tab)),'dd')) * (select to_char(endtime,'DD')  from tab)) as zjjjzss,
         a.slsszjjjss +
         ((b.slsszjjjss - a.slsszjjjss) /(to_char(last_day((select endtime from tab)),'dd')) * (select to_char(endtime,'DD')  from tab)) as slsszjjjss
    from (select avg(shmjxj) shmjxj,
                 avg(czmjxj) czmjxj,
                 avg(szrk) szrk,
                 avg(swrk)

                 swrk,
                 avg(szrkr) szrkr,
                 avg(dtfw) dtfw,
                 avg(zjjjzss) zjjjzss,
                 avg(slsszjjjss)

                 slsszjjjss
            from (select t.lsyear,
                         t.lsmonth,
                         avg(t.shmjxj) as shmjxj,
                         avg(t.czmjxj) as czmjxj,
                         avg(t.szrk) as szrk,
                         avg(t.swrk) as swrk,
                         avg(t.szrkr) as szrkr,
                         avg(t.dtfw) as dtfw,
                         avg(t.zjjjzss) as zjjjzss,
                         avg(t.slsszjjjss) as slsszjjjss
                    from lstqlj t
                   where t.lsmonth = (select to_char(add_months(endtime,-1),'MM') from tab)
                     and t.lsyear >= (select to_char(add_months(endtime,-60),'YYYY') from tab)
                     and t.lsyear < (select to_char(endtime,'YYYY') from tab)
                   group by t.lsyear, t.lsmonth)) a,
         (select avg(shmjxj) shmjxj,
                 avg(czmjxj) czmjxj,
                 avg(szrk) szrk,
                 avg(swrk) swrk,
                 avg(szrkr) szrkr,
                 avg(dtfw) dtfw,
                 avg(zjjjzss) zjjjzss,
                 avg(slsszjjjss) slsszjjjss
            from (select t.lsyear,
                         t.lsmonth,
                         avg(t.shmjxj) as shmjxj,
                         avg(t.czmjxj) as czmjxj,
                         avg(t.szrk) as szrk,
                         avg(t.swrk) as swrk,
                         avg(t.szrkr) as szrkr,
                         avg(t.dtfw) as dtfw,
                         avg(t.zjjjzss) as zjjjzss,
                         avg(t.slsszjjjss) as slsszjjjss
                    from lstqlj t
                   where t.lsmonth = (select to_char(endtime,'MM') from tab)
                     and t.lsyear >= (select to_char(add_months(endtime,-60),'YYYY') from tab)
                     and t.lsyear < (select to_char(endtime,'YYYY') from tab)
                   group by t.lsyear, t.lsmonth)) b),
  table10 as
 (select   to_char((select add_months(endtime,-12) from tab),'YYYY')|| '年同期值',
         to_number(b.col_2) as shmjxj,
         to_number(b.col_4) as czmjxj,
         to_number(e.col_4) as szrk,
         to_number(e.col_7) as swrk,
         to_number(e.col_8) as szrkr,
         to_number(e.col_6) as dtfw,
         to_number(e.col_10) as zjjjzss,
         to_number(c.col_19) as slsszjjjss
    from (select a.*
            from (select t.*,
                         abs(t.endtime - (select add_months(endtime,-12) from tab)) as etm,
                         abs(t.starttime - (select add_months(starttime,-12) from tab)) as stm
                    from comm_summ_detail t
                   Inner join (select *
                                from comm_summrep_detail
                               where reportpdtype = 'CR') t1
                      on t.id = t1.summerreportdetailid
                   Inner join (select proid
                                from shzh_business_report_01
                               group by proid) t2
                      on t.id = t2.proid
where t.bjdeletestate=0 and t.bussysmark=2
                   order by etm,stm, t.createtime desc

                  ) a
           where rownum = 1) a
    left join shzh_business_report_01 e
      on a.id = e.proid and e.col_1='国家防总'
    left join shzh_business_report_02 b
      on a.id = b.proid and e.col_1=b.col_1
    left join shzh_business_report_04 c
      on a.id = c.proid and c.col_1=e.col_1
  )

select *
  from table1 t1
union all
select *
  from table2
union all
select *
  from table3
union all
select * from table10
sify