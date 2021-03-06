select t.*,
       (djdh1 + djdh2 + djdh3 + djdh4) as djdhcount,
       (shzh1 + shzh2 + shzh3 + shzh4) as shzhcount,
       (tfzh1 + tfzh2 + tfzh3 + tfzh4) as tfzhcount,
       (jyzh1 + jyzh2 + jyzh3 + jyzh4) as jyzhcount,
       (djdh1 + shzh1 + tfzh1 + jyzh1) as nscount,
       (djdh2 + shzh2 + tfzh2 + jyzh2) as ymcount,
       (djdh3 + shzh3 + tfzh3 + jyzh3) as dfcount,
       (djdh4 + shzh4 + tfzh4 + jyzh4) as qtcount
  from (select count(case when t.col_10 like '降雨-大江大河洪水-溺水' then t.col_10 end) djdh1,
     count(case when t.col_10 like '降雨-大江大河%' and  t.col_10 like '%掩埋%' then t.col_10 end) djdh2,
     count(case when t.col_10 like '降雨-大江大河%' and t.col_10 like '%倒房%' then  t.col_10 end) djdh3,
     count(case when t.col_10 like '降雨-大江大河%' and t.col_10 like '%其它%' then t.col_10 end) djdh4,
     count(case when t.col_10 = '降雨-山洪灾害-山洪冲淹-溺水' then  t.col_10 end) shzh1,
     count(case when t.col_10 like '降雨-山洪灾害%' and t.col_10 like '%掩埋%' then t.col_10 end) shzh2,
     count(case when t.col_10 like '降雨-山洪灾害%' and t.col_10 like '%倒房%' then t.col_10 end) shzh3,
     count(case when t.col_10 like '降雨-山洪灾害%' and t.col_10 like '%其它%' then t.col_10 end) shzh4,
    count(case when t.col_10 like '台风-降雨%' and t.col_10 like '%溺水%' then  t.col_10 end) tfzh1,
    count(case when t.col_10 like  '台风-降雨%' and t.col_10 like '%掩埋%' then t.col_10  end) tfzh2,
    count(case when t.col_10 like '台风-降雨%' and t.col_10 like '%倒房%' then t.col_10 end) tfzh3,
    count(case when t.col_10 like '台风-降雨%' and t.col_10 like '%其它%' then t.col_10 end) tfzh4,
      count(case when t.col_10 = '降雨-溺水' then t.col_10 end) jyzh1,
      count(case when t.col_10 = '降雨-滑坡' or t.col_10 = '降雨-泥石流' then t.col_10 end) jyzh2,
      count(case when t.col_10 = '降雨-倒房' then t.col_10 end) jyzh3,
     count(case when t.col_10 = '降雨-其它' then t.col_10 end) jyzh4
 from shzh_business_report_05 t where t.proid = :proid ) t