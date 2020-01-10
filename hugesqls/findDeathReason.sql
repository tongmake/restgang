select col_1,
sum(aged) + sum(baby) + sum(nonage) + sum(young) + sum(unknown) as count,
sum(swcount) as swcount, sum(szcount) as szcount, sum(aged) as aged,
       sum(baby) + sum(nonage) as nonage, sum(young) as young, sum(unknown) as unknown,
       sum(baby) + sum(nonage) + sum(aged) as ansum,
       Case when (sum(aged) + sum(baby) + sum(nonage) + sum(young) +
              sum(unknown)) != 0 then
          round((sum(baby) + sum(nonage) + sum(aged)) /
                (sum(aged) + sum(baby) + sum(nonage) + sum(young) +
                sum(unknown)) * 100,
                2)
       end as agedProportion,
       sum(ns) ns,
       sum(df) as df,
       sum(ym) as ym,
       sum(sh) as sh,
       sum(qt) as qt,
       sum(shsw) as shsw,
       case
         when (sum(aged) + sum(baby) + sum(nonage) + sum(young) +
              sum(unknown)) != 0 then
          round(sum(shsw) / (sum(aged) + sum(baby) + sum(nonage) +
                             sum(young) + sum(unknown)) * 100,
                2)
       end as shswProportion,
       sum(shsz) as shsz,
       case
         when (sum(aged) + sum(baby) + sum(nonage) + sum(young) +
              sum(unknown)) != 0 then
          round(sum(shsz) / (sum(aged) + sum(baby) + sum(nonage) +
                             sum(young) + sum(unknown)) * 100,
                2)
       end as shszProportion,
       sum(shsw) + sum(shsz) as shsw_sz,
       case
         when (sum(aged) + sum(baby) + sum(nonage) + sum(young) +
              sum(unknown)) != 0 then
          round((sum(shsw) + sum(shsz)) /
                (sum(aged) + sum(baby) + sum(nonage) + sum(young) +
                sum(unknown)) * 100,
                2)
       end as swszProportion
  from (select '合计' as col_1,
               (case
                 when col_6 is null or col_6 = 'null' or col_6 = '不详' then
                  1
                 else
                  0
               end) as unknown,
               (case
                 when col_6 like '%个月%' then
                  1
                 else
                  0
               end) as baby,
               (case
                 when nvl2(translate(col_6, '/1234567890.', '/'),
                           'CHAR',
                           'NUMBER') = 'NUMBER' and to_number(col_6) > 0 and
                      to_number(col_6) < 18 then
                  1
                 else
                  0
               end) as nonage,
               (case
                 when nvl2(translate(col_6, '/1234567890.', '/'),
                           'CHAR',
                           'NUMBER') = 'NUMBER' and to_number(col_6) >= 18 and
                      to_number(col_6) < 60 then
                  1
                 else
                  0
               end) as young,
               (case
                 when nvl2(translate(col_6, '/1234567890.', '/'),
                           'CHAR',
                           'NUMBER') = 'NUMBER' and to_number(col_6) >= 60 then
                  1
                 else
                  0
               end) as aged,
               (case
                 when col_10 like '%降雨-大江大河洪水-溺水%' then
                  1
                 else
                  0
               end) as ns,
               (case
                 when col_10 like '%倒房%' then
                  1
                 else
                  0
               end) as df,
               (case
                 when col_10 like '%掩埋%' then
                  1
                 else
                  0
               end) as ym,
               (case
                 when col_10 like '%降雨-山洪灾害-山洪冲淹-溺水%' then
                  1
                 else
                  0
               end) as sh,
               (case
                 when col_10 like '%其它%' then
                  1
                 else
                  0
               end) as qt,
               (case
                 when col_3 like '%死亡%' then
                  1
                 else
                  0
               end) as sw,
               (case
                 when col_3 like '%失踪%' then
                  1
                 else
                  0
               end) as sz,
               (case
                 when col_10 like '%山洪灾害%' and col_3 = '死亡' then
                  1
                 else
                  0
               end) as shsw,
               (case
                 when col_10 like '%山洪灾害%' and col_3 = '失踪' then
                  1
                 else
                  0
               end) as shsz,
               (case
                 when col_3 = '死亡' then
                  1
                 else
                  0
               end) as swcount,
               (case
                 when col_3 = '失踪' then
                  1
                 else
                  0
               end) as szcount
          from shzh_business_report_05
         where proid = :proid ) t
union all
select col_1,
       sum(aged) + sum(baby) + sum(nonage) + sum(young) + sum(unknown),
       sum(swcount) as swcount,
       sum(szcount) as szcount,
       sum(aged) as aged,
       sum(baby) + sum(nonage) as nonage,
       sum(young) as young,
       sum(unknown) as unknown,
       sum(baby) + sum(nonage) + sum(aged) as ansum,
       case
         when (sum(aged) + sum(baby) + sum(nonage) + sum(young) +
              sum(unknown)) != 0 then
          round((sum(baby) + sum(nonage) + sum(aged)) /
                (sum(aged) + sum(baby) + sum(nonage) + sum(young) +
                sum(unknown)) * 100,
                2)
       end as agedProportion,
       sum(ns) ns,
       sum(df) as df,
       sum(ym) as ym,
       sum(sh) as sh,
       sum(qt) as qt,
       sum(shsw) as shsw,
       case
         when (sum(aged) + sum(baby) + sum(nonage) + sum(young) +
              sum(unknown)) != 0 then
          round(sum(shsw) / (sum(aged) + sum(baby) + sum(nonage) +
                             sum(young) + sum(unknown)) * 100,
                2)
       end as shswProportion,
       sum(shsz) as shsz,
       case
         when (sum(aged) + sum(baby) + sum(nonage) + sum(young) +
              sum(unknown)) != 0 then
          round(sum(shsz) / (sum(aged) + sum(baby) + sum(nonage) +
                             sum(young) + sum(unknown)) * 100,
                2)
       end as shszProportion,
       sum(shsw) + sum(shsz),
       case
         when (sum(aged) + sum(baby) + sum(nonage) + sum(young) +
              sum(unknown)) != 0 then
          round((sum(shsw) + sum(shsz)) /
                (sum(aged) + sum(baby) + sum(nonage) + sum(young) +
                sum(unknown)) * 100,
                2)
       end as swszProportion
  from (select col_1,
               (case
                 when col_6 is null or col_6 = 'null' or col_6 = '不详' then
                  1
                 else
                  0
               end) as unknown,
               (case
                 when col_6 like '%个月%' then
                  1
                 else
                  0
               end) as baby,
               (case
                 when nvl2(translate(col_6, '/1234567890.', '/'),
                           'CHAR',
                           'NUMBER') = 'NUMBER' and to_number(col_6) > 0 and
                      to_number(col_6) < 18 then
                  1
                 else
                  0
               end) as nonage,
               (case
                 when nvl2(translate(col_6, '/1234567890.', '/'),
                           'CHAR',
                           'NUMBER') = 'NUMBER' and to_number(col_6) >= 18 and
                      to_number(col_6) < 60 then
                  1
                 else
                  0
               end) as young,
               (case
                 when nvl2(translate(col_6, '/1234567890.', '/'),
                           'CHAR',
                           'NUMBER') = 'NUMBER' and to_number(col_6) >= 60 then
                  1
                 else
                  0
               end) as aged,
               (case
                 when col_10 like '%降雨-大江大河洪水-溺水%' then
                  1
                 else
                  0
               end) as ns,
               (case
                 when col_10 like '%倒房%' then
                  1
                 else
                  0
               end) as df,
               (case
                 when col_10 like '%掩埋%' then
                  1
                 else
                  0
               end) as ym,
               (case
                 when col_10 like '%降雨-山洪灾害-山洪冲淹-溺水%' then
                  1
                 else
                  0
               end) as sh,
               (case
                 when col_10 like '%其它%' then
                  1
                 else
                  0
               end) as qt,
               (case
                 when col_3 like '%死亡%' then
                  1
                 else
                  0
               end) as sw,
               (case
                 when col_3 like '%失踪%' then
                  1
                 else
                  0
               end) as sz,
               (case
                 when col_10 like '%山洪灾害%' and col_3 = '死亡' then
                  1
                 else
                  0
               end) as shsw,
               (case
                 when col_10 like '%山洪灾害%' and col_3 = '失踪' then
                  1
                 else
                  0
               end) as shsz,
               (case
                 when col_3 = '死亡' then
                  1
                 else
                  0
               end) as swcount,
               (case
                 when col_3 = '失踪' then
                  1
                 else
                  0
               end) as szcount
          from shzh_business_report_05
         where proid = :proid ) t
 group by col_1